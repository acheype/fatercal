import csv
import os
import psycopg2 as p2
import psycopg2.extras as extras

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sql import GET_LAST_SEND_DATE, GET_TAXON_FROM_ID
from sql import GET_UPDATE_FROM_FATERCAL


def start_connection():
    """
    Start the connection to the database
    :return: return a connector to the database
    """
    # Connect to database
    conn = p2.connect(
        dbname='fatercal',
        host=os.environ['POSTGRES_HOST'],
        user='fatercal',
        password=os.environ['POSTGRES_PASSWORD']
    )
    return conn

def stop_connection(conn):
    """
    Stop the connection to the database
    :param conn: a connector to the database
    :return: N/A
    """
    conn.close()

def find_manual_update(conn):
    """
    Find all update of taxon since the last time
    we send a mail to taxref
    :param conn: a connector to the database
    :return: a list of dict containing id of taxon
    """
    dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
    dict_curr.execute(GET_LAST_SEND_DATE)
    dict_last_update = dict_curr.fetchone()

    dict_curr.execute(GET_UPDATE_FROM_FATERCAL, [dict_last_update['date']])
    list_id = dict_curr.fetchall()
    dict_curr.close()
    return list_id

def create_csv(conn, list_id):
    """
    Create a csv file
    :param conn: a connector to the database
    :param list_id: a list of dict containing id of taxon
    :return: the file name (String)
    """
    curr = conn.cursor()
    file_name = "taxref_update_fatercal.csv"
    with open(file_name, 'w') as csv_file:
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
    return file_name

def send_mail():
    """
    Send mail
    """
    smtp_server = os.environ['SMTP_SERVER']

    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = 'Mis à jour Fatercal'
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = "laurent.schaeffer@ird.fr"
    msg['To'] = os.environ['RECEIVER_MAIL']

    body = "Voici les mises à jour de Fatercal depuis le mois dernier"

    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("taxref_update_fatercal.csv", "rb").read())
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment', filename='taxref_update_fatercal.csv')

    msg.attach(part)

    with smtplib.SMTP(smtp_server) as server:
        server.sendmail(msg['From'], msg['To'], msg.as_string())
