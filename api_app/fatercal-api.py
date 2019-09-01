import os
from distutils.util import strtobool
import json
import psycopg2 as p2
from flask import Flask, abort
from variable import fatercal_subject, fatercal_body, taxref_subject, taxref_body
from function import start_connection, find_manual_update, is_version_different, get_list_taxon_taxref_nc
from function import stop_connection, create_csv_format_taxref, send_mail, update_last_send_date, insert_update_taxref
from function import filter_list_taxon, seek_deleted_taxon_in_taxref, seek_referenced_taxon_in_taxref

app = Flask(__name__)

@app.route("/api/update_to_taxref")
def send_to_taxref_update():
    """ Send a mail with a csv containing all change to taxon from a date
    
    Returns:
        json -- a json file
        abort -- end the process if error
    """
    try:
        conn = start_connection()
        list_id = find_manual_update(conn)
        if list_id:
            filee = create_csv_format_taxref(conn, list_id)
            send_mail(taxref_subject, os.environ['RECEIVER_TAXREF'], [filee], taxref_body)
            update_last_send_date(conn)
        else:
            filee = None
        stop_connection(conn)
        if filee is not None:
            os.remove(filee['location'])
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except p2.DatabaseError as exception:
        print(exception)
        rabort(500)

@app.route("/api/update_from_taxref")
def get_update_from_taxref():
    """ Search all the update and send mail to the admin site if there are
    update or if any taxon has been erased in taxref
    
    Returns:
        json -- a json file
        abort -- end the process if error
    """
    try:
        conn = start_connection()
        is_diff, taxref_version = is_version_different(conn)
        if is_diff:
            list_taxon = get_list_taxon_taxref_nc(taxref_version)
            if list_taxon is not None:
                seek_deleted_taxon_in_taxref(conn, list_taxon)
                seek_referenced_taxon_in_taxref(conn, list_taxon)
                list_taxon_update = filter_list_taxon(conn, list_taxon, taxref_version)
                insert_update_taxref(conn, list_taxon_update)
            send_mail(fatercal_subject, os.environ['RECEIVER_FATERCAL'], [],fatercal_body)
            return json.dumps({'New_version':True}), 200, {'ContentType':'application/json'} 
        else:
            return json.dumps({'New_version':False}), 200, {'ContentType':'application/json'}
    except p2.DatabaseError as exception:
        print(exception)
        abort(500)


if __name__ == '__main__':
    app.run(debug=strtobool(os.environ['DEBUG']))
