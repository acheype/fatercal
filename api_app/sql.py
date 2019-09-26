"""
Sql query to have the latest date when we send mail to taxref
"""
GET_LAST_SEND_DATE = """
SELECT MAX(date) as date 
FROM last_update
WHERE type = 'IN'
"""

"""
Sql query to insert the current date when we send mail to taxref
"""
INSERT_LAST_SEND_DATE = """
INSERT INTO last_update
VALUES(NOW(), 'IN', 'Fatercal');
"""

"""
Sql query to insert the current date when we receive update from taxref
"""
INSERT_LAST_RECEIVE_DATE = """
INSERT INTO last_update
VALUES(NOW(), 'OUT', 'Taxref');
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
AND ht.last_update > %s
AND source = 'Fatercal';
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
GET_TAXON_WITH_CD_NOM = """
SELECT * 
FROM taxon 
WHERE cd_nom = %s;
"""

"""
Sql query to have all taxon referenced by Taxref
"""
GET_TAXREF_TAXON = """
SELECT * 
FROM taxon 
WHERE cd_nom is not Null;
"""

"""
Sql query to have all taxon not referenced by Taxref
"""
GET_FATERCAL_TAXON = """
SELECT * 
FROM taxon 
WHERE cd_nom is Null;
"""

"""
Sql query to have the latest version of taxref we register in the db
"""
GET_VERSION_TAXREF_UPDATE = """
SELECT MAX(taxrefversion)
FROM taxref_update;
"""

"""
Sql query to have the latest version of taxref in the table taxon
we register in the db
"""
GET_VERSION_TAXREF_TAXON = """
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

"""
Sql query to update taxon which are deleted in Taxref 
"""
UPDATE_SET_NOT_REFERENCED = """
UPDATE taxon
SET cd_nom = Null, cd_ref = Null, cd_sup = Null,
source = 'Taxref', last_update = NOW()
WHERE id = %s
"""

"""
Sql query to update taxon which are referenced in Taxref 
"""
UPDATE_SET_REFERENCED = """
UPDATE taxon
SET cd_nom = %s, cd_sup = %s, cd_ref = %s,
source = 'Taxref', last_update = NOW()
WHERE id = %s
"""

### Sql query for test ###

CREATE_LAST_UPDATE_TABLE = """
CREATE TABLE last_update(
    date timestamp without time zone,
    type character varying(100),
    source character varying(100)
)
"""

CREATE_TABLE_HISTORIQUE_TAXON = """
CREATE TABLE historique_taxon(
    id integer, cd_nom integer, cd_ref integer, cd_sup integer,
    lb_nom character varying(250) NOT NULL, lb_auteur character varying(250),
    nom_complet character varying(250), grande_terre boolean,
    iles_loyautee boolean, autre boolean, territoire_fr boolean,
    remarque text, sources text, id_espece integer, reference_description text,
    habitat smallint, id_ref integer, id_sup integer, nc character varying(4),
    rang character varying(4), last_update timestamp without time zone,
    type_modification character varying(250), champ_modifie character varying(250),
    last_user_update character varying(250), source character varying(50)
)
"""

CREATE_TABLE_TAXON = """
CREATE TABLE taxon(
    id serial NOT NULL PRIMARY KEY,
    cd_nom integer, cd_ref integer, cd_sup integer,
    lb_nom character varying(250) NOT NULL, lb_auteur character varying(250),
    nom_complet character varying(250), grande_terre boolean,
    iles_loyautee boolean, autre boolean, territoire_fr boolean,
    remarque text, sources text, id_espece integer, reference_description text,
    habitat smallint, id_ref integer, id_sup integer, nc character varying(4),
    rang character varying(4) NOT NULL, utilisateur character varying(250),
    last_update timestamp without time zone, source character varying(250),
    taxrefversion integer
)
"""

CREATE_TABLE_TAXREF_UPDATE = """
CREATE TABLE public.taxref_update(
    id serial NOT NULL,
    taxon_id integer,
    cd_nom integer,
    cd_sup integer,
    cd_ref integer,
    rang character varying(4) NOT NULL,
    lb_nom character varying(250) NOT NULL,
    lb_auteur character varying(250),
    nom_complet character varying(250),
    habitat smallint,
    nc character varying(4),
    date timestamp without time zone,
    taxrefversion integer,
    CONSTRAINT taxref_update_pkey PRIMARY KEY (id),
    CONSTRAINT update_taxref_taxon_id__taxon_id FOREIGN KEY (taxon_id)
      REFERENCES public.taxon (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
)
"""

CREATE_TYPE_TAXREF_DATA = """
CREATE TYPE public.taxref_data AS (
    regne character varying(250), phylum character varying(250),
    classe character varying(250), ordre character varying(250),
    famille character varying(250), group1_inpn character varying(50),
    group2_inpn character varying(50), id integer, id_ref integer,
    id_sup integer, cd_nom integer, cd_taxsup integer,
    cd_sup integer, cd_ref integer, rang character varying(4),
    lb_nom character varying(250), lb_auteur character varying(250),
    nom_complet character varying(250), nom_complet_html character varying(250),
    nom_valide character varying(100), nom_vern character varying(100),
    nom_vern_eng character varying(100), habitat character varying(100),
    nc character varying(4), grande_terre character varying(50),
    iles_loyautee character varying(50), autre character varying(50),
    non_present character varying(4), cd_ref_diff character varying(4),
    cd_sup_diff character varying(4), validity_diff character varying(4)
);
"""

CREATE_FUNCTION_GET_ALL_TAXON= """
CREATE OR REPLACE FUNCTION public.get_all_taxon_to_taxref()
  RETURNS SETOF taxref_data AS
$BODY$
DECLARE taxon taxon%ROWTYPE;
	
BEGIN
    FOR taxon IN SELECT * FROM taxon
    LOOP
	RETURN NEXT get_taxon_to_taxref(taxon.id);
    END LOOP;
END;
$BODY$
  LANGUAGE plpgsql
"""

CREATE_FUNCTION_GET_TAXON =  """
CREATE OR REPLACE FUNCTION public.get_taxon_to_taxref(taxon_id integer)
  RETURNS taxref_data AS
$BODY$
DECLARE taxon_t taxon%ROWTYPE;
	taxon_superior taxon%ROWTYPE;
	taxon_ref taxon%ROWTYPE;
	taxon_superior_id integer;
	result taxref_data;

BEGIN

SELECT * INTO taxon_t FROM taxon WHERE id=taxon_id;
SELECT * INTO taxon_ref FROM taxon WHERE id=taxon_t.id_ref;
IF taxon_t.id != taxon_t.id_ref THEN
    SELECT id_sup INTO taxon_superior_id FROM taxon WHERE id=taxon_t.id_ref;
ELSE
    SELECT id_sup INTO taxon_superior_id FROM taxon WHERE id=taxon_t.id;
END IF;
WHILE taxon_superior_id is not Null
LOOP
    SELECT * INTO taxon_superior FROM taxon WHERE id=taxon_superior_id;
    IF taxon_superior.rang = 'KD' THEN
        result.regne = taxon_superior.lb_nom;
    END IF;
    IF taxon_superior.rang = 'PH' THEN
        result.phylum = taxon_superior.lb_nom;
    END IF;
    IF taxon_superior.rang = 'CL' THEN
        result.classe = taxon_superior.lb_nom;
    END IF;
    IF taxon_superior.rang = 'OR' THEN
        result.ordre = taxon_superior.lb_nom;
    END IF;
    IF taxon_superior.rang = 'FM' THEN
        result.famille = taxon_superior.lb_nom;
    END IF;
    SELECT id_sup INTO taxon_superior_id FROM taxon WHERE id=taxon_superior_id;
END LOOP;
SELECT * INTO taxon_superior FROM taxon WHERE id=taxon_t.id_sup;
IF taxon_t.cd_nom is Null THEN
    result.non_present = 'x';
ELSE IF (taxon_t.id != taxon_t.id_ref and taxon_t.cd_ref = taxon_ref.cd_nom) OR
(taxon_t.id = taxon_t.id_ref and taxon_t.cd_ref != taxon_ref.cd_nom) THEN
    result.validity_diff = 'x';
ELSE IF taxon_t.cd_ref != taxon_ref.cd_nom THEN
    result.cd_ref_diff = 'x';
ELSE IF taxon_t.cd_sup != taxon_superior.cd_nom THEN
    result.cd_sup_diff = 'x';
END IF;
END IF;
END IF;
END IF;

IF taxon_t.grande_terre is TRUE THEN
    result.grande_terre = 'Présent';
ELSE IF taxon_t.grande_terre is FALSE THEN
    result.grande_terre = 'Non Présent';
END IF;
END IF;

IF taxon_t.iles_loyautee is TRUE THEN
    result.iles_loyautee = 'Présent';
ELSE IF taxon_t.iles_loyautee is FALSE THEN
    result.iles_loyautee= 'Non Présent';
END IF;
END IF;

IF taxon_t.autre is TRUE THEN
    result.autre = 'Présent';
ELSE IF taxon_t.autre is FALSE THEN
    result.autre= 'Non Présent';
END IF;
END IF;

IF taxon_t.rang = 'KD' THEN
    result.regne = taxon_t.lb_nom;
END IF;
result.id = taxon_t.id;
result.id_ref = taxon_t.id_ref;
result.id_sup = taxon_t.id_sup;
result.cd_nom = taxon_t.cd_nom;
result.cd_ref = taxon_t.cd_ref;
result.cd_sup = taxon_t.cd_sup;
result.rang = taxon_t.rang;
result.lb_nom = taxon_t.lb_nom;
result.lb_auteur = taxon_t.lb_auteur;
result.nom_complet = taxon_t.nom_complet;
result.habitat = taxon_t.habitat;
result.nc = taxon_t.nc;
RETURN result;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE;
"""

INSERT_INTO_LAST_UPDATE = """
INSERT INTO last_update(date, type, source)
VALUES (%s, %s, %s)
"""

INSERT_TAXON = """
INSERT INTO taxon(lb_nom, rang, cd_nom, taxrefversion)
VALUES (%s, %s, %s, %s)
RETURNING id
"""

INSERT_HISTO_TAXON = """
INSERT INTO historique_taxon(id, lb_nom, rang, cd_nom, last_update)
VALUES (%s, %s, %s, %s, %s)
"""