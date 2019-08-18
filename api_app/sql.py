"""
Sql query to have the latest date when we send mail to taxref
"""
GET_LAST_SEND_DATE = """
SELECT *
FROM last_update
WHERE date = (SELECT MAX(date) FROM last_update)
AND type LIKE 'IN';
"""

"""
Sql query to insert the current date when we send mail to taxref
"""
INSERT_LAST_SEND_DATE = """
INSERT INTO last_update
VALUES(NOW(), 'IN', 'Fatercal');
"""

"""
Sql query to get a list of id of updated taxon from fatercal
since a given time
"""
GET_UPDATE_FROM_FATERCAL = """
SELECT t.id
FROM taxon as t, historique_taxon as ht
WHERE t.cd_nom is not NULL
AND t.id = ht.id
AND ht.last_update > %s;
"""


"""
Sql query to have a taxon from an id
"""
GET_TAXON_FROM_ID = """
SELECT regne, phylum, classe, ordre, famille, group1_inpn, group2_inpn,
    id, id_ref, id_sup, cd_nom, cd_taxsup, cd_sup, cd_ref, rang,
    lb_nom, lb_auteur, nom_complet, nom_complet_html, nom_valide,
    nom_vern, nom_vern_eng, habitat, nc
FROM get_taxon_to_taxref(%s);
"""

"""
Sql query to have a taxon from an id
"""
GET_TAXREF_TAXON = """
SELECT * 
FROM taxon 
WHERE cd_nom is not Null
"""

"""
Sql query to have the latest version of taxref we register in the db
"""
GET_VERSION_TAXREF = """
SELECT MAX(taxrefversion)
FROM taxon;
"""

"""
Sql query to insert the taxon from taxref with their new data
"""
INSERT_INTO_TAXREF_UPDATE = """
INSERT INTO taxref_update (taxon_id, cd_nom, cd_sup,
cd_ref, rang, lb_nom, lb_auteur, nom_complet, habitat,
nc, date, taxrefversion)
VALUES %s;
"""
