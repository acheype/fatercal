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
  LANGUAGE plpgsql VOLATILE
  COST 100;
