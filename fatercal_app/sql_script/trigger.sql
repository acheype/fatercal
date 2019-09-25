CREATE OR REPLACE FUNCTION public.function_trigger_delete_prelevement()
  RETURNS trigger AS
$BODY$
    BEGIN
        INSERT INTO historique_prelevement VALUES 
        (OLD.id_prelevement, OLD.date, OLD.nb_taxon_present, OLD.collection_museum, OLD.type_specimen, OLD.code_specimen,
            OLD.altitude_min, OLD.mode_de_collecte, OLD.toponyme, OLD.toponymie_x, OLD.toponymie_y,
            OLD.information_complementaire, OLD.id_loc, OLD.id_taxref, OLD.type_enregistrement, OLD.gps,
            OLD.altitude_max, OLD.id_habitat, OLD.id_plante_hote,
            NOW() at time zone 'Pacific/Noumea', 'Delete', '', OLD.utilisateur, OLD.source);

        RETURN OLD;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE OR REPLACE FUNCTION public.function_trigger_delete_taxon()
  RETURNS trigger AS
$BODY$
    BEGIN
        INSERT INTO historique_taxon VALUES
        (OLD.id, OLD.cd_nom, OLD.cd_ref, OLD.cd_sup, OLD.lb_nom, OLD.lb_auteur,
            OLD.nom_complet, OLD.grande_terre, OLD.iles_loyautee, OLD.autre, OLD.territoire_fr,
            OLD.remarque, OLD.sources, OLD.id_espece, OLD.reference_description, OLD.habitat,
            OLD.id_ref, OLD.id_sup, OLD.nc, OLD.rang, NOW() at time zone 'Pacific/Noumea',
            'Delete', '', OLD.utilisateur, OLD.source);

        RETURN OLD;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE OR REPLACE FUNCTION public.function_trigger_insert_prelevement()
  RETURNS trigger AS
$BODY$
    BEGIN
        INSERT INTO historique_prelevement VALUES 
        (NEW.id_prelevement, NEW.date, NEW.nb_taxon_present, NEW.collection_museum, NEW.type_specimen, NEW.code_specimen,
            NEW.altitude_min, NEW.mode_de_collecte, NEW.toponyme, NEW.toponymie_x, NEW.toponymie_y,
            NEW.information_complementaire, NEW.id_loc, NEW.id_taxref, NEW.type_enregistrement, NEW.gps,
            NEW.altitude_max, NEW.id_habitat, NEW.id_plante_hote, NOW() at time zone 'Pacific/Noumea',
            'Insert', '', NEW.utilisateur, NEW.source);

        RETURN NEW;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE OR REPLACE FUNCTION public.function_trigger_insert_taxon()
  RETURNS trigger AS
$BODY$
    BEGIN
        INSERT INTO historique_taxon VALUES
        (NEW.id, NEW.cd_nom, NEW.cd_ref, NEW.cd_sup, NEW.lb_nom, NEW.lb_auteur,
            NEW.nom_complet, NEW.grande_terre, NEW.iles_loyautee, NEW.autre, NEW.territoire_fr,
            NEW.remarque, NEW.sources, NEW.id_espece, NEW.reference_description, NEW.habitat,
            NEW.id_ref, NEW.id_sup, NEW.nc, NEW.rang, NOW() at time zone 'Pacific/Noumea',
            'Insert', '', NEW.utilisateur, NEW.source);

        RETURN NEW;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE OR REPLACE FUNCTION public.function_trigger_update_prelevement()
  RETURNS trigger AS
$BODY$
DECLARE changed_column_prelevement varchar(250);
    BEGIN
        changed_column_prelevement = '';
        -- Check that empname and salary are given
        IF NEW.id_prelevement != OLD.id_prelevement  THEN
            SELECT CONCAT(changed_column_prelevement,'id_prelevement, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.date != OLD.date  THEN
            SELECT CONCAT(changed_column_prelevement,'date, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.nb_taxon_present != OLD.nb_taxon_present  THEN
            SELECT CONCAT(changed_column_prelevement,'nb_taxon_present, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.collection_museum != OLD.collection_museum  THEN
            SELECT CONCAT(changed_column_prelevement,'collection_museum, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.type_specimen != OLD.type_specimen  THEN
            SELECT CONCAT(changed_column_prelevement,'type_specimen, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.code_specimen != OLD.code_specimen  THEN
            SELECT CONCAT(changed_column_prelevement,'code_specimen, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.altitude_min != OLD.altitude_min  THEN
            SELECT CONCAT(changed_column_prelevement,'altitude_min, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.mode_de_collecte != OLD.mode_de_collecte  THEN
            SELECT CONCAT(changed_column_prelevement,'mode_de_collecte, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.toponyme != OLD.toponyme  THEN
            SELECT CONCAT(changed_column_prelevement,'toponyme, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.toponymie_x != OLD.toponymie_x  THEN
            SELECT CONCAT(changed_column_prelevement,'toponymie_x, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.toponymie_y != OLD.toponymie_y  THEN
            SELECT CONCAT(changed_column_prelevement,'toponymie_y, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.information_complementaire != OLD.information_complementaire  THEN
            SELECT CONCAT(changed_column_prelevement,'information_complementaire, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.id_loc != OLD.id_loc  THEN
            SELECT CONCAT(changed_column_prelevement,'id_loc, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.id_taxref != OLD.id_taxref  THEN
            SELECT CONCAT(changed_column_prelevement,'id_taxref, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.type_enregistrement != OLD.type_enregistrement  THEN
            SELECT CONCAT(changed_column_prelevement,'type_enregistrement, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.gps != OLD.gps  THEN
            SELECT CONCAT(changed_column_prelevement,'gps, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.altitude_max != OLD.altitude_max  THEN
            SELECT CONCAT(changed_column_prelevement,'altitude_max, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.id_habitat != OLD.id_habitat  THEN
            SELECT CONCAT(changed_column_prelevement,'id_habitat, ') INTO changed_column_prelevement;
        END IF;
        IF NEW.id_plante_hote != OLD.id_plante_hote  THEN
            SELECT CONCAT(changed_column_prelevement,'id_plante_hote , ') INTO changed_column_prelevement;
        END IF;
        INSERT INTO historique_prelevement VALUES 
        (OLD.id_prelevement, OLD.date, OLD.nb_taxon_present, OLD.collection_museum, OLD.type_specimen, OLD.code_specimen,
            OLD.altitude_min, OLD.mode_de_collecte, OLD.toponyme, OLD.toponymie_x, OLD.toponymie_y,
            OLD.information_complementaire, OLD.id_loc, OLD.id_taxref, OLD.type_enregistrement, OLD.gps,
            OLD.altitude_max, OLD.id_habitat, OLD.id_plante_hote, NOW() at time zone 'Pacific/Noumea', 
            'Update', changed_column_prelevement, NEW.utilisateur, OLD.source);

        RETURN NEW;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE OR REPLACE FUNCTION public.function_trigger_update_taxon()
  RETURNS trigger AS
$BODY$
DECLARE changed_column_taxon varchar(250);
    BEGIN
        changed_column_taxon = '';
        IF NEW.id != OLD.id  THEN
            SELECT CONCAT(changed_column_taxon,'id, ') INTO changed_column_taxon;
        END IF;
        IF NEW.cd_nom != OLD.cd_nom  THEN
            SELECT CONCAT(changed_column_taxon,'cd_nom, ') INTO changed_column_taxon;
        END IF;
        IF NEW.cd_ref != OLD.cd_ref  THEN
            SELECT CONCAT(changed_column_taxon,'cd_ref, ') INTO changed_column_taxon;
        END IF;
        IF NEW.cd_sup != OLD.cd_sup  THEN
            SELECT CONCAT(changed_column_taxon,'cd_sup, ') INTO changed_column_taxon;
        END IF;
        IF NEW.lb_nom != OLD.lb_nom  THEN
            SELECT CONCAT(changed_column_taxon,'lb_nom, ') INTO changed_column_taxon;
        END IF;
        IF NEW.lb_auteur != OLD.lb_auteur  THEN
            SELECT CONCAT(changed_column_taxon,'lb_auteur, ') INTO changed_column_taxon;
        END IF;
        IF NEW.nom_complet != OLD.nom_complet  THEN
            SELECT CONCAT(changed_column_taxon,'nom_complet, ') INTO changed_column_taxon;
        END IF;
        IF NEW.grande_terre != OLD.grande_terre  THEN
            SELECT CONCAT(changed_column_taxon,'grande_terre, ') INTO changed_column_taxon;
        END IF;
        IF NEW.iles_loyautee != OLD.iles_loyautee  THEN
            SELECT CONCAT(changed_column_taxon,'iles_loyautee, ') INTO changed_column_taxon;
        END IF;
        IF NEW.autre != OLD.autre  THEN
            SELECT CONCAT(changed_column_taxon,'autre, ') INTO changed_column_taxon;
        END IF;
        IF NEW.territoire_fr != OLD.territoire_fr  THEN
            SELECT CONCAT(changed_column_taxon,'territoire_fr, ') INTO changed_column_taxon;
        END IF;
        IF NEW.remarque != OLD.remarque  THEN
            SELECT CONCAT(changed_column_taxon,'remarque, ') INTO changed_column_taxon;
        END IF;
        IF NEW.sources != OLD.sources  THEN
            SELECT CONCAT(changed_column_taxon,'sources, ') INTO changed_column_taxon;
        END IF;
        IF NEW.id_espece != OLD.id_espece  THEN
            SELECT CONCAT(changed_column_taxon,'id_espece, ') INTO changed_column_taxon;
        END IF;
        IF NEW.reference_description != OLD.reference_description  THEN
            SELECT CONCAT(changed_column_taxon,'reference_description, ') INTO changed_column_taxon;
        END IF;
        IF NEW.habitat != OLD.habitat  THEN
            SELECT CONCAT(changed_column_taxon,'habitat, ') INTO changed_column_taxon;
        END IF;
        IF NEW.id_ref != OLD.id_ref  THEN
            SELECT CONCAT(changed_column_taxon,'id_ref, ') INTO changed_column_taxon;
        END IF;
        IF NEW.id_sup != OLD.id_sup  THEN
            SELECT CONCAT(changed_column_taxon,'id_sup, ') INTO changed_column_taxon;
        END IF;
        IF NEW.nc != OLD.nc  THEN
            SELECT CONCAT(changed_column_taxon,'nc, ') INTO changed_column_taxon;
        END IF;
        IF NEW.rang != OLD.rang  THEN
            SELECT CONCAT(changed_column_taxon,'rang, ') INTO changed_column_taxon;
        END IF;
        IF NEW.source != OLD.source  THEN
            SELECT CONCAT(changed_column_taxon,'source, ') INTO changed_column_taxon;
        END IF;
        IF NEW.taxrefversion != OLD.taxrefversion  THEN
            SELECT CONCAT(changed_column_taxon,'taxrefVersion, ') INTO changed_column_taxon;
        END IF;
        INSERT INTO historique_taxon VALUES 
        (OLD.id, OLD.cd_nom, OLD.cd_ref, OLD.cd_sup, OLD.lb_nom, OLD.lb_auteur,
            OLD.nom_complet, OLD.grande_terre, OLD.iles_loyautee, OLD.autre, OLD.territoire_fr,
            OLD.remarque, OLD.sources, OLD.id_espece, OLD.reference_description, OLD.habitat,
            OLD.id_ref, OLD.id_sup, OLD.nc, OLD.rang, NOW() at time zone 'Pacific/Noumea',
            'Update',changed_column_taxon, NEW.utilisateur, NEW.source);

        RETURN NEW;
    END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;