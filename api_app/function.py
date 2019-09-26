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

from sql import GET_LAST_SEND_DATE, GET_TAXON_FROM_ID, GET_TAXON_WITH_CD_NOM
from sql import GET_UPDATE_FROM_FATERCAL, INSERT_LAST_SEND_DATE, GET_TAXREF_TAXON
from sql import GET_VERSION_TAXREF_TAXON, INSERT_INTO_TAXREF_UPDATE, UPDATE_SET_NOT_REFERENCED
from sql import UPDATE_SET_REFERENCED, GET_FATERCAL_TAXON, GET_VERSION_TAXREF_UPDATE


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

def create_csv_format_taxref(conn, list_id):
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
        writer = csv.writer(csv_file, delimiter=";", lineterminator='\n', encoding="utf-8")
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
        Boolean, String or None -- True if it find a new version (with the number)
    """
    curr = conn.cursor()
    curr.execute(GET_VERSION_TAXREF_UPDATE)
    version_taxref_fatercal = curr.fetchone()[0]
    if version_taxref_fatercal is None:
        curr.execute(GET_VERSION_TAXREF_TAXON)
        version_taxref_fatercal = curr.fetchone()[0]
    if version_taxref_fatercal is None:
        raise p2.DatabaseError()
    response = requests.get(
        "https://taxref.mnhn.fr/api/taxrefVersions/" + str(int(version_taxref_fatercal) + 1)
    )
    curr.close()
    if response.status_code == 404:
        return False, None
    taxref_version = response.json()['id']
    return True, taxref_version

def get_list_taxon_taxref_nc(taxref_version):
    """ Get a list of taxon of New-Caledonia from taxref with their API
    and have Animalia as a parent
    
    Arguments:
        taxref_version {String} -- The taxref version we import update from
    
    Returns:
        List -- Return a list of dict containing all taxon of nc referenced in taxref
    """
    size = 1
    count = 1
    list_taxon = []
    list_taxon_not_filter = []
    # We get all taxon by browsing throught 'page' (See Taxref API doc)
    while size != 0:
        response = requests.get(
            "https://taxref.mnhn.fr/api/taxa/search?territories=nc&page={}".format(count)
        )
        if response.status_code == 404:
            list_taxon_temp = None
            if list_taxon_not_filter == []:
                list_taxon_not_filter = None
            size = 0
        else:
            list_taxon_temp = response.json().get('_embedded', None)
            if list_taxon_temp is None:
                size = 0
            else:
                size = len(list_taxon_temp['taxa'])
                if size != 0:
                    list_taxon_not_filter = list_taxon_not_filter + list_taxon_temp['taxa']
        count = count + 1
    if list_taxon_not_filter:
        for taxon in list_taxon_not_filter:
            if taxon['kingdomName'] == 'Animalia':
                list_taxon.append(taxon)
    else:
        list_taxon = list_taxon_not_filter
    return list_taxon



def create_tuple_taxref_update(taxon_fatercal, taxon_taxref, taxref_version):
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
    is_different = False
    if taxon_taxref['habitat'] is not None:
        taxon_taxref['habitat'] = int(taxon_taxref['habitat'])
    if taxon_fatercal['cd_sup'] != taxon_taxref['parentId'] or \
    taxon_fatercal['cd_ref'] != taxon_taxref['referenceId'] or \
    taxon_fatercal['rang'] != taxon_taxref['rankId'] or \
    taxon_fatercal['lb_nom'] != taxon_taxref['scientificName'] or \
    taxon_fatercal['lb_auteur'] != taxon_taxref['authority'] or \
    taxon_fatercal['nom_complet'] != taxon_taxref['fullName'] or \
    (taxon_fatercal['habitat'] != taxon_taxref['habitat'] and taxon_taxref['habitat'] is not None) or \
    (taxon_fatercal['nc'] != taxon_taxref['nc'] and taxon_taxref['nc'] is not None):
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
    """ Insert taxon in the table taxref_update
    
    Arguments:
        conn {connection} -- a connector to the database
        list_taxon_diff {List} -- a list of tuple
    """
    curr = conn.cursor()
    extras.execute_values(curr,
        INSERT_INTO_TAXREF_UPDATE,
        list_taxon_diff)
    curr.close()
    conn.commit()

def filter_list_taxon(conn, list_taxon, taxref_version):
    """ Filter the list of taxon for update or insert
    
    Arguments:
        conn {connection} -- a connector to the database
        list_taxon {List} -- List of dict
        taxref_version {Integer} -- current version of taxref
    
    Returns:
        List -- a list of tuple
    """
    dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
    list_taxon_update = []
    for taxon_taxref in list_taxon:
        # We check if the taxon exist in Fatercal
        dict_curr.execute(GET_TAXON_WITH_CD_NOM, [taxon_taxref['id']])
        taxon_fatercal = dict_curr.fetchone()
        # Taxon with no id will be inserted as new taxon
        if taxon_fatercal is None:
            insert = filter_insert_taxon(taxon_taxref)
            if insert:
                list_taxon_update.append((
                    None, taxon_taxref['id'], taxon_taxref['parentId'],
                    taxon_taxref['referenceId'], taxon_taxref['rankId'],
                    taxon_taxref['scientificName'], taxon_taxref['authority'],
                    taxon_taxref['fullName'], taxon_taxref['habitat'],
                    taxon_taxref['nc'], datetime.now(), taxref_version)
                )
        # Taxon with an existant id will be updated if there's a diff
        else:
            taxon_diff = create_tuple_taxref_update(
                taxon_fatercal, taxon_taxref, taxref_version)
            if taxon_diff is not None:
                list_taxon_update.append(taxon_diff)
    dict_curr.close()
    return list_taxon_update

def filter_insert_taxon(taxon_taxref):
    """Detect the taxon which are not meant to be in Fatercal
    
    Arguments:
        taxon_taxref {Dict} -- A dict containing info on a taxon
    
    Returns:
        [Boolean] -- return if the taxon can be insert in Fatercal or not
    """
    insert = True
    if taxon_taxref['phylumName'] == 'Echinodermata':
        insert = False
    if taxon_taxref['phylumName'] == 'Cnidaria':
        insert = False
    if taxon_taxref['phylumName'] == 'Annelida':
        if taxon_taxref['className'] != 'Clitellata':
            insert = False
    if taxon_taxref['phylumName'] == 'Mollusca':
        if taxon_taxref['className'] == 'Gastropoda':
            if taxon_taxref['orderName'] != 'Stylommatophora' and taxon_taxref['familyName'] != 'Assimineidae' \
                and taxon_taxref['familyName'] != 'Hydrobiidae' and taxon_taxref['familyName'] != 'Tateidae':
                insert = False
        else:
            insert = False
    if taxon_taxref['className'] == 'Malacostraca':
        if taxon_taxref['orderName'] == 'Amphipoda':
            if taxon_taxref['familyName'] != 'Talitridae':
                insert = False
        elif taxon_taxref['orderName'] == 'Isopoda':
            if taxon_taxref['familyName'] != 'Armadillidae' and taxon_taxref['familyName'] != 'Philosciidae' \
                and taxon_taxref['familyName'] != 'Oniscidae' and taxon_taxref['familyName'] != 'Ligiidae' \
                and taxon_taxref['familyName'] != 'Trachelipodidae' and taxon_taxref['familyName'] != 'Porcellionidae':
                insert = False
        elif taxon_taxref['orderName'] == 'Decapoda':
            if taxon_taxref['familyName'] != 'Goneplacidae' and taxon_taxref['familyName'] != 'Hymenosomatidae' \
                and taxon_taxref['familyName'] != 'Grapsidae'and taxon_taxref['familyName'] != 'Alpheidae' \
                and taxon_taxref['familyName'] != 'Atyidae' and taxon_taxref['familyName'] != 'Palaemonidae':
                insert = False
        else:
            insert = False
    if taxon_taxref['className'] == 'Mammalia':
        insert = False
    return insert

def seek_deleted_taxon_in_taxref(conn, list_taxon_taxref):
    """ Delete cd_nom reference in Fatercal taxon when Taxref delete these taxon
    
    Arguments:
        conn {connection} -- a connector to the database
        list_taxon_taxref {List} -- a list of dict
    """
    dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
    dict_curr.execute(GET_TAXREF_TAXON)
    list_taxon_fatercal = dict_curr.fetchall()
    dict_curr.close()
    curr = conn.cursor()
    for fatercal_taxon in list_taxon_fatercal:
        taxref_taxon = next(
            (taxref_taxon for taxref_taxon in list_taxon_taxref
                if taxref_taxon['id'] == fatercal_taxon['cd_nom']), None)
        if taxref_taxon is None:
            curr.execute(UPDATE_SET_NOT_REFERENCED, [fatercal_taxon['id']])
    curr.close()

def seek_referenced_taxon_in_taxref(conn, list_taxon_taxref):
    """ Update cd_nom reference in Fatercal taxon's when Taxref add these taxon
    
    Arguments:
        conn {connection} -- a connector to the database
        list_taxon_taxref {List} -- a list of dict
    """
    dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
    dict_curr.execute(GET_FATERCAL_TAXON)
    list_taxon_fatercal = dict_curr.fetchall()
    dict_curr.close()
    curr = conn.cursor()
    for fatercal_taxon in list_taxon_fatercal:
        taxref_taxon = next(
            (taxref_taxon for taxref_taxon in list_taxon_taxref 
                if taxref_taxon['scientificName'] == fatercal_taxon['lb_nom']), None)
        if taxref_taxon is not None:
            curr.execute(GET_TAXON_WITH_CD_NOM, [taxref_taxon['id']])
            temp_taxon = curr.fetchone()
            if temp_taxon is None:
                curr.execute(UPDATE_SET_REFERENCED,
                    [taxref_taxon['id'], taxref_taxon['parentId'],
                    taxref_taxon['referenceId'], fatercal_taxon['id']])
    curr.close()
