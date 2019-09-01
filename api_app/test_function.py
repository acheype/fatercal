import os
import time
import psycopg2
import unittest
from datetime import datetime
from function import *
import testing.postgresql
from sql import CREATE_LAST_UPDATE_TABLE, CREATE_TABLE_HISTORIQUE_TAXON
from sql import CREATE_TABLE_TAXON, CREATE_TYPE_TAXREF_DATA, CREATE_TABLE_TAXREF_UPDATE
from sql import CREATE_FUNCTION_GET_ALL_TAXON, CREATE_FUNCTION_GET_TAXON
from sql import INSERT_INTO_LAST_UPDATE, INSERT_TAXON, INSERT_HISTO_TAXON

def handler(postgresql):
    conn = psycopg2.connect(**postgresql.dsn())
    curr = conn.cursor()
    curr.execute(CREATE_LAST_UPDATE_TABLE)
    curr.execute(CREATE_TABLE_HISTORIQUE_TAXON)
    curr.execute(CREATE_TABLE_TAXON)
    curr.execute(CREATE_TABLE_TAXREF_UPDATE)
    curr.execute(CREATE_TYPE_TAXREF_DATA)
    curr.execute(CREATE_FUNCTION_GET_TAXON)
    curr.execute(CREATE_FUNCTION_GET_ALL_TAXON)
    curr.close()
    conn.commit()
    conn.close()

Postgresql = testing.postgresql.PostgresqlFactory(
    cache_initialized_db=True,
    on_initialized=handler
)

class TestFunction(unittest.TestCase):

    def setUp(self):
        self.postgresql = Postgresql()

    def tearDown(self):
        self.postgresql.stop()
    
    def tearDownModule(self):
        # clear cached database at end of tests
        Postgresql.clear_cache()
    
    def test_find_manual_update(self):
        conn = psycopg2.connect(**self.postgresql.dsn())
        dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
        dict_curr.execute(
            INSERT_INTO_LAST_UPDATE,
            [datetime.now(), 'IN', 'Fatercal']
        )
        # If the cd_nom is None we get nothing
        dict_curr.execute(INSERT_TAXON, ['taxon', 'GN', None, None])
        taxon_id = dict_curr.fetchone()
        time.sleep(1.0)
        dict_curr.execute(
            INSERT_HISTO_TAXON,
            [taxon_id[0], 'taxon', 'GN', None, datetime.now()]
        )
        list_id_expected = []
        list_id_result = find_manual_update(conn)
        self.assertEqual(list_id_result, list_id_expected)
        # If the cd_nom is not None we get something
        dict_curr.execute(INSERT_TAXON, ['taxon', 'GN', 126, None])
        taxon_id = dict_curr.fetchone()
        time.sleep(1.0)
        dict_curr.execute(
            INSERT_HISTO_TAXON,
            [taxon_id[0], 'taxon', 'GN', 126, datetime.now()]
        )
        list_id_result = find_manual_update(conn)
        list_id_expected = [[taxon_id[0]]]
        self.assertEqual(list_id_result, list_id_expected)
        dict_curr.close()
        conn.close()
        
    def test_create_csv(self):
        conn = psycopg2.connect(**self.postgresql.dsn())
        dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
        list_id_empty = []
        filee = create_csv_format_taxref(conn, list_id_empty)
        file_name_expected = "taxref_update_fatercal.csv"
        self.assertEqual(file_name_expected, filee['name'])
        self.assertTrue(os.path.exists(filee['location']))
        os.remove(filee['location'])
        dict_curr.execute(INSERT_TAXON, ['taxon', 'GN', 126, None])
        taxon_id = dict_curr.fetchone()
        list_id_not_empty = [[taxon_id[0]]]
        filee = create_csv_format_taxref(conn, list_id_not_empty)
        self.assertEqual(file_name_expected, filee['name'])
        self.assertTrue(os.path.exists(filee['location']))
        with open(filee['location']) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';', lineterminator='\n')
            line_count = 0
            for row_result in csv_reader:
                if line_count == 0:
                    row_expected = ['REGNE', 'PHYLUM', 'CLASSE',
                        'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN',
                        'ID', 'ID_REF', 'ID_SUP', 'CD_NOM', 'CD_TAXSUP',
                        'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM', 'LB_AUTEUR',
                        'NOM_COMPLET', 'NOM_COMPLET_HTML', 'NOM_VALIDE',
                        'NOM_VERN', 'NOM_VERN_ENG', 'HABITAT', 'NC']
                    self.assertEqual(row_expected, row_result)
                    line_count += 1
                else:
                    row_expected = ['', '', '', '', '', '',
                        '', str(taxon_id[0]), '', '', '126',
                        '', '', '', 'GN', 'taxon', '', '',
                        '', '', '', '', '', '']
                    self.assertEqual(row_expected, row_result)
                    line_count += 1
        os.remove(filee['location'])
        dict_curr.close()
        conn.close()

    def test_update_last_send_date(self):
        conn = psycopg2.connect(**self.postgresql.dsn())
        time = datetime.now()
        update_last_send_date(conn)
        dict_curr = conn.cursor(cursor_factory=extras.DictCursor)
        dict_curr.execute(GET_LAST_SEND_DATE)
        last_send = dict_curr.fetchone()
        self.assertGreater(last_send['date'], time)

    def test_is_version_different(self):
        conn = psycopg2.connect(**self.postgresql.dsn())
        curr = conn.cursor()
        # If we can't get a version from both table we raise a DatabaseError
        try:
            is_diff, taxref_version = is_version_different(conn)
        except psycopg2.DatabaseError as e:
            print('Catch error on purpose')
        # We set an old version so it the API return the next version after this one
        curr.execute(INSERT_TAXON, ['taxon', 'GN', 126, 1])
        taxon_id = curr.fetchone()[0]
        try:
            is_diff, taxref_version = is_version_different(conn)
        except psycopg2.DatabaseError as e:
            self.fail("An error ocurred no date is in both table taxon and taxref_update")
        taxref_version_expected = 2
        self.assertTrue(is_diff)
        self.assertEqual(taxref_version_expected, taxref_version)
        # We set an version nonexistant so it the API return an error 404
        curr.execute(INSERT_TAXON, ['taxon', 'GN', 126, 10000000])
        try:
            is_diff, taxref_version = is_version_different(conn)
        except psycopg2.DatabaseError as e:
            self.fail("An error ocurred no date is in both table taxon and taxref_update")
        self.assertFalse(is_diff)
        self.assertIsNone(taxref_version)
        # We set insert a new row in taxref_update the function will check first if there a version
        # in this table before checking in the table taxon
        curr.execute(
            INSERT_INTO_TAXREF_UPDATE, 
            [(taxon_id, 125, None, None, 'GN', 'taxon', 'auteur',
            None, None, None, datetime.now(), 1)]
        )
        try:
            is_diff, taxref_version = is_version_different(conn)
        except psycopg2.DatabaseError as e:
            self.fail("An error ocurred no date is in both table taxon and taxref_update")
        self.assertTrue(is_diff)
        self.assertEqual(taxref_version_expected, taxref_version)

    def test_create_tuple_taxref_update(self):
        dict_taxref = {
            'id': 1, 'parentId': 2, 'referenceId': 3,
            'rankId': 'GN', 'scientificName': 'taxon',
            'authority': 'auteur', 'fullName': '',
            'habitat': '5', 'nc': None
        }
        dict_fatercal = {
            'id': 1, 'cd_sup': 2, 'cd_ref': 3, 'rang': 'GN',
            'lb_nom': 'taxon', 'lb_auteur': 'auteur', 'nom_complet': '',
            'habitat': 5, 'nc': None
        }
        taxon_tuple = create_tuple_taxref_update(dict_fatercal, dict_taxref, None)
        self.assertIsNone(taxon_tuple)
        dict_fatercal['habitat'] = 4
        taxon_tuple = create_tuple_taxref_update(dict_fatercal, dict_taxref, None)
        self.assertIsNotNone(taxon_tuple)

    def test_filter_list_taxon(self):
        conn = psycopg2.connect(**self.postgresql.dsn())
        list_taxon = [
            {'id': 1, 'parentId': 2, 'referenceId': 3,
            'rankId': 'GN', 'scientificName': 'taxon',
            'authority': 'auteur', 'fullName': '',
            'habitat': '5', 'nc': None},
            {'id': 4, 'parentId': 5, 'referenceId': 6,
            'rankId': 'GN', 'scientificName': 'taxon',
            'authority': 'auteur', 'fullName': '',
            'habitat': '5', 'nc': None}
        ]
        curr = conn.cursor()
        curr.execute(INSERT_TAXON, ['taxon', 'GN', 1, 1])
        list_taxon_update = filter_list_taxon(conn, list_taxon, None)
        list_taxon_update[0] = list(list_taxon_update[0])
        list_taxon_update[1] = list(list_taxon_update[1])
        list_taxon_update[0][10] = None
        list_taxon_update[1][10] = None
        list_taxon_update_expected = [
            [1, 1, 2, 3, 'GN', 'taxon', 'auteur', '', 5, None, None, None],
            [None, 4, 5, 6, 'GN', 'taxon', 'auteur', '', '5', None, None, None]
        ]
        self.assertEqual(list_taxon_update_expected, list_taxon_update)

    def test_seek_deleted_taxon_in_taxref(self):
        conn = psycopg2.connect(**self.postgresql.dsn())
        curr = conn.cursor()
        curr.execute(INSERT_TAXON, ['taxon', 'GN', 1, 1])
        seek_deleted_taxon_in_taxref(conn, [])
        curr.execute(GET_TAXON_WITH_CD_NOM, [1])
        taxon = curr.fetchone()
        self.assertIsNone(taxon)
        curr.execute(INSERT_TAXON, ['taxon', 'GN', 2, 1])
        list_taxon_taxref = [
            {'id': 2, 'parentId': 3, 'referenceId': 4,
            'rankId': 'GN', 'scientificName': 'taxon',
            'authority': 'auteur', 'fullName': '',
            'habitat': '5', 'nc': None}
        ]
        seek_deleted_taxon_in_taxref(conn, list_taxon_taxref)
        curr.execute(GET_TAXON_WITH_CD_NOM, [2])
        taxon = curr.fetchone()
        self.assertIsNotNone(taxon)



    def test_seek_referenced_taxon_in_taxref(self):
        conn = psycopg2.connect(**self.postgresql.dsn())
        curr = conn.cursor()
        curr.execute(INSERT_TAXON, ['taxon', 'GN', None, 1])
        seek_referenced_taxon_in_taxref(conn, [])
        curr.execute(GET_TAXON_WITH_CD_NOM, [1])
        taxon = curr.fetchone()
        self.assertIsNone(taxon)
        curr.execute(INSERT_TAXON, ['taxon', 'GN', None, 1])
        list_taxon_taxref = [
            {'id': 2, 'parentId': 3, 'referenceId': 4,
            'rankId': 'GN', 'scientificName': 'taxon',
            'authority': 'auteur', 'fullName': '',
            'habitat': '5', 'nc': None}
        ]
        seek_referenced_taxon_in_taxref(conn, list_taxon_taxref)
        curr.execute(GET_TAXON_WITH_CD_NOM, [2])
        taxon = curr.fetchone()
        self.assertIsNotNone(taxon)
