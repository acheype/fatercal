CREATE OR REPLACE FUNCTION get_all_taxon_to_taxref()
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
  LANGUAGE plpgsql VOLATILE;
