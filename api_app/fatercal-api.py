import os
from distutils.util import strtobool
import psycopg2 as p2
from flask import Flask, jsonify
from variable import fatercal_subject, taxref_subject, taxref_body
from function import start_connection, find_manual_update, is_version_different, get_update_taxref
from function import stop_connection, create_csv, send_mail, update_last_send_date, insert_update_taxref
from function import create_body_mail_update_taxref


app = Flask(__name__)

@app.route("/api/update_to_taxref")
def send_to_taxref_update():
    """
    Send a mail with a csv containing all change to taxon from a date
    :return: a json file
    """
    try:
        conn = start_connection()
        if conn is not None:
            list_id = find_manual_update(conn)
            if list_id:
                filee = create_csv(conn, list_id)
                send_mail(taxref_subject, os.environ['RECEIVER_TAXREF'], [filee], taxref_body)
                update_last_send_date(conn)
            else:
                filee = None
            stop_connection(conn)
            if filee is not None:
                os.remove(filee['location'])
            return jsonify("Succes")
        else:
            return jsonify('Error 500')
    except p2.DatabaseError as exception:
        print(exception)
        return jsonify("Error 500")

@app.route("/api/update_from_taxref")
def get_update_from_taxref():
    """
    Search all the update and send mail to the admin site if there are
    update or if any taxon has been erased in taxref
    :return: a json file
    """
    try:
        conn = start_connection()
        if conn is not None:
            new_version = is_version_different(conn)
            if new_version:
                list_taxon_diff, list_taxon_erased = get_update_taxref(conn)
                if list_taxon_diff:
                    insert_update_taxref(conn, list_taxon_diff)
                    fatercal_body = create_body_mail_update_taxref(list_taxon_diff, list_taxon_erased)
                    if fatercal_body is not None:
                        send_mail(fatercal_subject, os.environ['RECEIVER_FATERCAL'], [],fatercal_body)
                return jsonify('Succes')
            return('Error 404: Not Found')
        else:
            return jsonify('Error 500')
    except p2.DatabaseError as exception:
        print(exception)
        return jsonify("Error 500")


if __name__ == '__main__':
    app.run(debug=strtobool(os.environ['DEBUG']))
