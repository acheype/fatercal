import csv
import os
import requests
import psycopg2 as p2
import psycopg2.extras as extras

import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sql import GET_LAST_SEND_DATE, GET_TAXON_FROM_ID, GET_TAXREF_TAXON
from sql import GET_UPDATE_FROM_FATERCAL, INSERT_LAST_SEND_DATE
from sql import GET_VERSION_TAXREF, INSERT_INTO_TAXREF_UPDATE


def start_connection():
    """ Create a new database session and return a new connection object
    
    Returns:
        connection -- a connector to the database
    """
    # Connect to database
    conn = p2.connect(
        dbname='fatercal',
        host=os.environ['POSTGRES_HOST'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    return conn

def stop_connection(conn):
    """ Stop the connection to the database
    
    Arguments:
        conn {connection} -- a connector to the database
    """
    conn.close()

def find_manual_update(conn):
    """ Find all update of taxon since the last time we data to taxref
    
    Arguments:
        conn {connection} -- a connector to the database
    
    Returns:
        List -- a list of dict containing id of taxon
    """
    dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
    dict_curr.execute(GET_LAST_SEND_DATE)
    dict_last_update = dict_curr.fetchone()

    dict_curr.execute(GET_UPDATE_FROM_FATERCAL, [dict_last_update['date']])
    list_id = dict_curr.fetchall()
    dict_curr.close()
    return list_id

def create_csv(conn, list_id):
    """ Create a csv with the info of taxon fatercal updated
    
    Arguments:
        conn {connection} -- a connector to the database
        list_id {List} -- list of dict containing id of taxon
    
    Returns:
        [Dict] -- Dict with the location and name of the csv
    """
    curr = conn.cursor()
    filee = {
        'location' : os.getcwd() + "/taxref_update_fatercal.csv",
        'name' : "taxref_update_fatercal.csv"
        }
    with open(filee['location'], 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=";", lineterminator='\n')
        writer.writerow(
            ('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN',
             'GROUP2_INPN', 'ID', 'ID_REF', 'ID_SUP', 'CD_NOM', 'CD_TAXSUP',
             'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM', 'LB_AUTEUR', 'NOM_COMPLET',
             'NOM_COMPLET_HTML', 'NOM_VALIDE', 'NOM_VERN', 'NOM_VERN_ENG', 'HABITAT', 'NC'))
        for taxref_id in list_id:
            curr.execute(GET_TAXON_FROM_ID, taxref_id)
            taxon = curr.fetchone()
            writer.writerow(taxon)
    curr.close()
    return filee

def send_mail(subject, receiver, list_file, body):
    """ Send a mail
    
    Arguments:
        subject {String} -- The subject of the mail
        receiver {String} -- The personn who will receive the mail
        list_file {List} -- A list of dict with the location and name of the files we want to send with the mail
        body {String} -- The body of the mail
    """
    smtp_server = os.environ['SMTP_SERVER']

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = os.environ['SENDER_MAIL']
    msg['To'] = receiver

    msg.attach(MIMEText(body, 'plain'))

    for filee in list_file:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(filee['location'], "rb").read())
        encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment', filename=filee['name'])

        msg.attach(part)

    with smtplib.SMTP(smtp_server) as server:
        server.sendmail(msg['From'], msg['To'], msg.as_string())

def update_last_send_date(conn):
    """ Update the database with the current date in the table last_update
    
    Arguments:
        conn {connection} -- a connector to the database
    """
    curr = conn.cursor()
    curr.execute(INSERT_LAST_SEND_DATE)
    curr.close()
    conn.commit()

def is_version_different(conn):
    """ Compare the version we have of taxref with the latest version
    
    Arguments:
        conn {connection} -- a connector to the database
    
    Returns:
        Boolean, String or None if not found -- True if it find a new version (with the number)
    """
    curr = conn.cursor()
    curr.execute(GET_VERSION_TAXREF)
    version_taxref_fatercal = curr.fetchone()[0]

    response = requests.get(
        "https://taxref.mnhn.fr/api/taxrefVersions/" + str(int(version_taxref_fatercal) + 1)
    )
    if response.status_code == 404:
        return False, None
    taxref_version = response.json()['id']
    return True, taxref_version

def get_update_taxref(conn, taxref_version):
    """ Get the update from taxref with their API
    
    Arguments:
        conn {connection} -- a connector to the database
        taxref_version {String} -- The taxref version we import update from
    
    Returns:
        List, List -- Return two list with updated and erased taxon
    """
    dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
    dict_curr.execute(GET_TAXREF_TAXON)
    list_dict_taxon_fater = dict_curr.fetchall()
    dict_curr.close()
    list_taxon_diff = []
    list_taxon_erased = []
    for taxon_fatercal in list_dict_taxon_fater:
        response = requests.get(
            "https://taxref.mnhn.fr/api/taxa/" + str(taxon_fatercal['cd_nom'])
        )
        if response.status_code == 404:
            list_taxon_erased.append(
                "Nom complet:" + taxon_fatercal['nom_complet'] + " CD_NOM:" + str(taxon_fatercal['cd_nom'])
            )
        else:
            taxon_taxref = response.json()
            taxon_diff = create_dict_taxref_update(taxon_fatercal, taxon_taxref, taxref_version)
            if taxon_diff is not None:
                list_taxon_diff.append(taxon_diff)
    return list_taxon_diff, list_taxon_erased



def create_dict_taxref_update(taxon_fatercal, taxon_taxref, taxref_version):
    """ Create a tuple which contains all the info we need 
    for update
    
    Arguments:
        taxon_fatercal {Dict} -- a dict about a taxon from fatercal
        taxon_taxref {Dict} -- a dict about a taxon from taxref
        taxref_version {String} -- The taxref version we import update from
    
    Returns:
        Tuple -- A tuple which contains info on an updated taxon
    """
    taxon_diff = None
    if taxon_taxref['habitat'] is not None:
        taxon_taxref['habitat'] = int(taxon_taxref['habitat'])
    is_different = False
    if taxon_fatercal['cd_sup'] != taxon_taxref['parentId'] or \
    taxon_fatercal['cd_ref'] != taxon_taxref['referenceId'] or \
    taxon_fatercal['rang'] != taxon_taxref['rankId'] or \
    taxon_fatercal['lb_nom'] != taxon_taxref['scientificName'] or \
    taxon_fatercal['lb_auteur'] != taxon_taxref['authority'] or \
    taxon_fatercal['nom_complet'] != taxon_taxref['fullName'] or \
    taxon_fatercal['habitat'] != taxon_taxref['habitat'] or \
    taxon_fatercal['nc'] != taxon_taxref['nc']:
        is_different = True

    if is_different:
        taxon_diff = (taxon_fatercal['id'], taxon_taxref['id'],
            taxon_taxref['parentId'], taxon_taxref['referenceId'],
            taxon_taxref['rankId'], taxon_taxref['scientificName'],
            taxon_taxref['authority'], taxon_taxref['fullName'],
            taxon_taxref['habitat'], taxon_taxref['nc'], datetime.now(),
            taxref_version)
    return taxon_diff

def insert_update_taxref(conn, list_taxon_diff):
    curr = conn.cursor()
    extras.execute_values(curr,
        INSERT_INTO_TAXREF_UPDATE,
        list_taxon_diff)
    curr.close()
    conn.commit()

def create_body_mail_update_taxref(list_taxon_diff, list_taxon_erased):
    """ Create the body of a mail to send
    
    Arguments:
        list_taxon_diff {List} -- Contains all taxon which is different in taxref
        list_taxon_erased {List} -- Contains all taxon erased from taxref

    Returns:
        String -- The body of the mail
    """

    fatercal_body = None
    if list_taxon_diff and list_taxon_erased:
        fatercal_body = """Une mise a jour depuis taxref attend la validation de plusieurs taxon
        Un ou plusieurs taxon ont été suprimé de taxref.
        Voici le nom complet et le cd_nom des taxon supprimé
        """
        for taxon in list_taxon_erased:
            fatercal_body = fatercal_body + taxon
    elif list_taxon_diff and not list_taxon_erased:
        fatercal_body = """Une mise a jour depuis taxref attend la validation de plusieurs taxon"""
    elif not list_taxon_diff and list_taxon_erased:
        fatercal_body = """Un ou plusieurs taxon ont été suprimé de taxref.
        Voici le nom complet et le cd_nom des taxon supprimé
        """
        for taxon in list_taxon_erased:
            fatercal_body = fatercal_body + taxon
    return fatercal_body
