import os
from distutils.util import strtobool
import psycopg2 as p2
from flask import Flask, jsonify
from function import start_connection, find_manual_update
from function import stop_connection, create_csv, send_mail, update_last_send_date


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
                file_name = create_csv(conn, list_id)
                send_mail()
                update_last_send_date(conn)
            else:
                file_name = None
            stop_connection(conn)
            if file_name is not None:
                os.remove(file_name)
            return jsonify("it works")
        else:
            return jsonify('Error 500')
    except p2.DatabaseError as exception:
        print(exception)
        return jsonify("Error 500")


if __name__ == '__main__':
    app.run(debug=strtobool(os.environ['DEBUG']))
