import settings as st
import taxonChange as tc
import os
import sys
import csv

#  ----------------------------Start : Insert data-----------------------------


def get_tupple_from_csv_for_extraction(line):

    if line[st.COLUMNS['habitat']['index']]==-1:
        habitat = None
        # No information about habitat
    else:
        habitat = int(line[st.COLUMNS['habitat']['index']])
    if line[st.COLUMNS['nc']['index']]=='' :
        # No information about nc
        nc = None
    else:
        nc = line[st.COLUMNS['nc']['index']]
    if int(line[st.COLUMNS['cd_sup']['index']])==-1:
        cd_sup = None
    else:
        cd_sup = int(line[st.COLUMNS['cd_sup']['index']])
    if int(line[st.COLUMNS['cd_nom']['index']])==-1:
        cd_nom = None
    else:
        cd_nom = int(line[st.COLUMNS['cd_nom']['index']])
    if int(line[st.COLUMNS['cd_ref']['index']])==-1:
        cd_ref = None
    else:
        cd_ref = int(line[st.COLUMNS['cd_ref']['index']])
    tupple = (
        cd_nom,
        cd_ref,
        cd_sup,
        habitat,
        line[st.COLUMNS['lb_auteur']['index']],
        line[st.COLUMNS['lb_nom']['index']],
        nc,
        line[st.COLUMNS['nom_complet']['index']],
        line[st.COLUMNS['rang']['index']],
        line[st.COLUMNS['nom_vern']['index']],
        line[st.COLUMNS['nom_vern_eng']['index']],
        True
    )
    return tupple


def get_tupple_from_csv(line):

    if line[st.COLUMNS['habitat']['index']]==-1:
        habitat = None
        # No information about habitat
    else:
        habitat = int(line[st.COLUMNS['habitat']['index']])
    if line[st.COLUMNS['nc']['index']]=='' :
        # No information about nc
        nc = None
    else:
        nc = line[st.COLUMNS['nc']['index']]
    if int(line[st.COLUMNS['cd_sup']['index']])==-1:
        cd_sup = None
    else:
        cd_sup = int(line[st.COLUMNS['cd_sup']['index']])
    if int(line[st.COLUMNS['cd_nom']['index']])==-1:
        cd_nom = None
    else:
        cd_nom = int(line[st.COLUMNS['cd_nom']['index']])
    if int(line[st.COLUMNS['cd_ref']['index']])==-1:
        cd_ref = None
    else:
        cd_ref = int(line[st.COLUMNS['cd_ref']['index']])
    tupple = (
        None,
        None,
        cd_nom,
        cd_ref,
        cd_sup,
        line[st.COLUMNS['lb_nom']['index']],
        line[st.COLUMNS['lb_auteur']['index']],
        line[st.COLUMNS['nom_complet']['index']],
        line[st.COLUMNS['rang']['index']],
        habitat,
        nc,
        True
    )
    # tupple = {
    # 	'id_ref' : None,
    # 	'id_sup' : None,
    # 	'cd_nom' : int(line[st.COLUMNS['cd_nom']['index']]),
    # 	'cd_ref' : int(line[st.COLUMNS['cd_ref']['index']]),
    # 	'cd_sup' : cd_sup,
    # 	'lb_nom' : line[st.COLUMNS['lb_nom']['index']],
    # 	'lb_auteur' : line[st.COLUMNS['lb_auteur']['index']],
    # 	'nom_complet' : line[st.COLUMNS['nom_complet']['index']],
    # 	'rang' : line[st.COLUMNS['rang']['index']],
    # 	'habitat' : habitat,
    # 	'nc' : nc,
    # 	'territoire' : True
    # }
    return tupple


def insert_in_fatercal(fatercal):
    """
        Fonction qui va permettre l'insertion des donnee dans Fatercal,
        et plus precisement dans la table taxref
    """
    try:
        # Connect to database
        conn = p2.connect(
            dbname ='fatercal',
            host ='127.0.0.1',
            user ='postgres',
            password ='123'
        )
        curr = conn.cursor()
        tupple = []
        for line in fatercal:
            tupple.append(get_tupple_from_csv(line))
        curr.execute('''DELETE FROM taxon''')
        curr.execute('''ALTER SEQUENCE "taxref_id_seq" RESTART WITH 1''')
        conn.commit()
        insert_query = '''INSERT INTO taxon(id_ref, id_sup, cd_nom,
            cd_ref, cd_sup, lb_nom, lb_auteur, nom_complet,
            rang, habitat, nc, territoire_fr) VALUES %s'''
        p2_extra.execute_values(curr, insert_query, tupple, page_size=100)
        conn.commit()
        tupple2 = []
        for line in fatercal:
            tupple2.append(making_link_between_line(fatercal, line))

        insert_query2 = '''UPDATE taxon SET id_ref = (
            SELECT id FROM taxon WHERE cd_nom = %s),id_sup = 
            (SELECT id FROM taxon WHERE cd_nom = %s) WHERE cd_nom = %s'''
        p2_extra.execute_batch(curr, insert_query2, tupple2, page_size=100)
        conn.commit()
        curr.close()
        conn.close()
    except p2.DatabaseError as exception:
        print(exception)
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def making_link_between_line(fatercal, line):
    cd_nom = int(line[st.COLUMNS['cd_nom']['index']])
    cd_nom_sup = int(line[st.COLUMNS['cd_sup']['index']])
    cd_nom_ref = int(line[st.COLUMNS['cd_ref']['index']])
    return (cd_nom_ref, cd_nom_sup, cd_nom)

#  ----------------------------End : Insert data-------------------------------


#  ----------------------------Start : Update data-----------------------------

def query_yes_no(question, default=None):
    """
        Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
    """
    valid = {
        "yes": True,
        "y": True,
        "ye": True,
        "no": False,
        "n": False
    }
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Repondez par 'yes' ou 'no' "
                            "(ou bien par 'y' ou 'n').\n")

def create_tupple_from_list_taxref(line):
	"""
		The aim of this function is create a new tuple from line's file

		"line" a line from the file whitch is also a tuple
	"""
	if line[st.COLUMNS['habitat']['index']] == '':
		habitat = None
        # No information about habitat
	else:
		habitat = int(line[st.COLUMNS['habitat']['index']])
	if line[st.COLUMNS['nc']['index']] == '' :
        # No information about nc
		nc = None
	else:
		nc = line[st.COLUMNS['nc']['index']]
	if line[st.COLUMNS['cd_sup']['index']] == '':
		cd_sup = None
	else:
		cd_sup = int(line[st.COLUMNS['cd_sup']['index']])
	return (
		int(line[st.COLUMNS['cd_nom']['index']]),
		int(line[st.COLUMNS['cd_ref']['index']]),
		cd_sup,
		habitat,
		nc,
		line[st.COLUMNS['rang']['index']]
	)



def create_tupple_from_list_taxref2(line):
    """
        The aim of this function is create a new tuple from line's file

        "line" a line from the file whitch is also a tuple
    """
    if line[st.COLUMNS['habitat']['index']] == '':
        habitat = None
        # No information about habitat
    else:
        habitat = int(line[st.COLUMNS['habitat']['index']])
    if line[st.COLUMNS['nc']['index']] == '' :
        # No information about nc
        nc = None
    else:
        nc = line[st.COLUMNS['nc']['index']]
    if line[st.COLUMNS['cd_sup']['index']] == '':
        cd_sup = None
    else:
        cd_sup = int(line[st.COLUMNS['cd_sup']['index']])
    return (
        int(line[st.COLUMNS['cd_nom']['index']]),
        int(line[st.COLUMNS['cd_ref']['index']]),
        cd_sup,
        habitat,
        line[st.COLUMNS['lb_auteur']['index']],
        line[st.COLUMNS['lb_nom']['index']],
        nc,
        line[st.COLUMNS['nom_complet']['index']],
        line[st.COLUMNS['rang']['index']],
        line[st.COLUMNS['nom_vern']['index']],
        line[st.COLUMNS['nom_vern_eng']['index']],
    )


def make_list_of_update(tupple, curr):
    list_ref_by_taxref = [tup for tup in tupple if tup.change_type == tc.ChangeType.REFERENCED_BY_TAXREF]
    list_syn_to_valid = [tup for tup in tupple if tup.change_type == tc.ChangeType.SYNONYMOUS_TO_VALID]
    list_valid_to_syn = [tup for tup in tupple if tup.change_type == tc.ChangeType.VALID_TO_SYNONYMOUS]
    list_valid_taxon_change = [tup for tup in tupple if tup.change_type == tc.ChangeType.VALID_TAXON_CHANGE]
    list_higher_taxon_change = [tup for tup in tupple if tup.change_type == tc.ChangeType.HIGHER_TAXON_CHANGE]
    list_no_id_change = [tup for tup in tupple if tup.change_type == tc.ChangeType.NO_ID_CHANGE or (tup.change_type == tc.ChangeType.REFERENCED_BY_TAXREF and tup.is_additionnal_change)]
    list_new_tax_and_syn = [tup for tup in tupple if tup.change_type == tc.ChangeType.NEW_VALID_TAXON or tup.change_type == tc.ChangeType.NEW_SYNONYMOUS]
    return list_ref_by_taxref, list_syn_to_valid, list_valid_to_syn, list_valid_taxon_change, list_higher_taxon_change, list_no_id_change, list_new_tax_and_syn


def get_msg_for_user(taxref, tup, curr, tupple, change_type):
    """
        The aim of this function is to create a message
        for the user to display if it is updatable

        "tup" the tup who has the type of change for defining a message

        "curr" the cursor used to send request to the db

        "tupple" a TaxonChanges Object which contain all the possible update to the db
    """
    msg = ''
    curr.execute('''
        SELECT cd_nom, cd_ref, cd_sup, habitat, lb_auteur, lb_nom, nc, nom_complet, rang
        FROM taxon
        WHERE cd_nom = %s
        ''',
        [tup.tupple[st.COLUMNS['cd_nom']['index']]]
    )
    tup_fat = curr.fetchone()
    if tup_fat[st.COLUMNS['habitat']['index']] is None:
            habitat = ''
    else:
        habitat = str(tup_fat[st.COLUMNS['habitat']['index']])
    if tup_fat[st.COLUMNS['nc']['index']] is None:
        nc = ''
    else:
        nc = str(tup_fat[st.COLUMNS['nc']['nc']])
    if tup.is_updatable:
        if tup.change_type == tc.ChangeType.SYNONYMOUS_TO_VALID:
            tup_in_taxref = next((tupp for tupp in taxref if str(tup_fat[st.COLUMNS['cd_ref']['index']]) == str(tupp[st.COLUMNS['cd_nom']['index']])), None)
            msg = "Ce synonyme est devenu un taxon valide:\nDifférence cd_ref:\nFATERCAL: {}, cd_nom = {}\nTAXREF: {}, cd_nom = {}".format(tup_in_taxref[st.COLUMNS['nom_complet']['index']], tup_in_taxref[st.COLUMNS['cd_nom']['index']], tup_fat[st.COLUMNS['nom_complet']['index']], tup.tupple[st.COLUMNS['cd_nom']['index']])
        elif tup.change_type == tc.ChangeType.VALID_TO_SYNONYMOUS:
            tup_in_taxref = next((tupp for tupp in taxref if tup.tupple[st.COLUMNS['cd_ref']['index']]==tupp[st.COLUMNS['cd_nom']['index']]), None)
            msg = "Ce taxon est devenu un synonyme:\nDifference cd_ref:\nFATERCAL: {}, cd_nom = {}\nTAXREF: {}, cd_nom = {}".format(tup_fat[st.COLUMNS['nom_complet']['index']], tup_fat[st.COLUMNS['cd_ref']['index']], tup_in_taxref[st.COLUMNS['nom_complet']['index']], tup.tupple[st.COLUMNS['cd_ref']['index']])
        elif tup.change_type == tc.ChangeType.VALID_TAXON_CHANGE:
            msg = "Ce synonyme a changé de taxon valide:\nDifférence cd_ref:\nFATERCAL: {}\nTAXREF: {}".format(tup_fat[st.COLUMNS['cd_ref']['index']], tup.tupple[st.COLUMNS['cd_ref']['index']])
        elif tup.change_type == tc.ChangeType.HIGHER_TAXON_CHANGE:
            tup_in_taxref2 = next((tupp for tupp in taxref if str(tup_fat[st.COLUMNS['cd_sup']['index']]) == str(tupp[st.COLUMNS['cd_nom']['index']])), None)
            tup_in_taxref = next((tupp for tupp in taxref if tup.tupple[st.COLUMNS['cd_sup']['index']] == tupp[st.COLUMNS['cd_nom']['index']]), None)
            msg = "Ce taxon a changé de taxon superieur:\nDifférence cd_sup:\nFATERCAL: {}, cd_nom = {}\nTAXREF: {}, cd_nom = {}".format(tup_in_taxref2[st.COLUMNS['nom_complet']['index']], tup_in_taxref[st.COLUMNS['cd_sup']['index']], tup_in_taxref[st.COLUMNS['nom_complet']['index']], tup.tupple[st.COLUMNS['cd_sup']['index']])
        elif tup.change_type == tc.ChangeType.NO_ID_CHANGE:
            msg = "Ce taxon a eu des modifications sur d'autres champs\nAutre(s) différence(s) (habitat, nc, rang):\nFATERCAL: {}\nTAXREF: {}".format((habitat, nc, tup_fat[st.COLUMNS['rang']['index']]), (tup.tupple[st.COLUMNS['habitat']['index']], tup.tupple[st.COLUMNS['nc']['index']], tup.tupple[st.COLUMNS['rang']['index']]))
        elif tup.change_type == tc.ChangeType.NEW_VALID_TAXON:
            number = get_nb_taxon_dependant(tup, tupple)
            msg = "C'est un nouveau taxon à insérer.\nChamps : ('CD_NOM', 'CD_REF', 'CD_SUP', 'HABITAT', 'LB_AUTEUR', 'LB_NOM', 'NC', 'NOM_COMPLET', 'RANG', 'NOM_VERN', 'NOM_VERN_ENG',)\nDonnées : {}\nIl y a {} mise(s) à jour de taxon qui dépendent de ce taxon".format(tup.tupple, number)
        elif tup.change_type == tc.ChangeType.NEW_SYNONYMOUS:
            msg = "C'est un nouveau synonyme à insérer.\nChamps : ('CD_NOM', 'CD_REF', 'CD_SUP', 'HABITAT', 'LB_AUTEUR', 'LB_NOM', 'NC', 'NOM_COMPLET', 'RANG', 'NOM_VERN', 'NOM_VERN_ENG',)\nDonnées : {}".format(tup.tupple)
        if tup.is_additionnal_change != None:
            msg += "\n Autres différences (habitat, nc, rang):\nFATERCAL: {}\nTAXREF: {}".format((habitat, nc, tup_fat[st.COLUMNS['rang']['index']]), (tup.tupple[st.COLUMNS['habitat']['index']], tup.tupple[st.COLUMNS['nc']['index']], tup.tupple[st.COLUMNS['rang']['index']]))
        msg += "\n{}".format(tup.user_message)
        return msg
    else:
        return tup.user_message


def get_nb_taxon_dependant(tup, tupple):
    number = 0
    for tupp in tupple:
        if str(tupp.tupple[st.COLUMNS['cd_ref']['index']]) == str(tup.tupple[st.COLUMNS['cd_nom']['index']]) and int(tupp.tupple[st.COLUMNS['cd_nom']['index']]) != int(tup.tupple[st.COLUMNS['cd_nom']['index']]) or str(tupp.tupple[st.COLUMNS['cd_sup']['index']]) == str(tup.tupple[st.COLUMNS['cd_nom']['index']]):
            number += 1
    return number

# ----------------------------Start : Define data update-----------------------------


def get_difference_between_bdd(taxref, curr):
    """
        This function will search all difference between Fatercal and the file from taxref
    	
    	"taxref" a list created from a csv file which contains tuple
    	
    	"curr" the cursor used to send request to the db
    """
    curr.execute("prepare myplan as "
    			'''SELECT EXISTS(SELECT 1
    			FROM taxon WHERE cd_nom = $1 AND 
    			( cd_ref != $2 OR cd_sup != $3 
    			OR habitat != $4 OR nc != $5 
                OR rang !=$6 ))'''
    			)
    tupple = tc.TaxonChanges()
    i = 0
    for line in taxref:
        data = create_tupple_from_list_taxref(line)
        if is_different_from_db(data, curr):
            tupple.append(tc.TaxonChange(line))
        else:
            if is_cas_nb_1(line, curr) :
                tupple.append(tc.TaxonChange(line))
        i = i + 1
        os.system('clear')
        print((i*100)/len(taxref), '% Terminé')
    os.system('clear')
    return tupple


def is_different_from_db(data, curr):
    """
        The aim of this function is to return a boolean whitch will
        determinate if the tuple is different from the db

        "data" a tuple to test whitch is in the form like settings

        "curr" the cursor used to send request to the db
    """
    curr.execute('''          
                execute myplan (%s,%s,%s,%s,%s,%s)
                ''',data)
    return curr.fetchone()[0]


def is_cas_nb_1(data, curr):
    curr.execute('''
            SELECT EXISTS(
                SELECT 1
                FROM taxon 
                WHERE lb_nom = %s AND lb_auteur = %s 
                AND rang = %s AND cd_nom IS NULL
            )''',
            [data[st.COLUMNS['lb_nom']['index']],
            data[st.COLUMNS['lb_auteur']['index']],
            data[st.COLUMNS['rang']['index']]]
            )
    return curr.fetchone()[0]


def classify_change_type(taxref, tupple, curr):
    """
        This function will dispatch all type of change in different case

    	"taxref" a list created from a csv file which contains tuple

    	"tupple" a TaxonChanges object which is also a list containing TaxonChange object

        "curr" the cursor used to send request to the db
    """
    liste_cas_insert = tc.TaxonChanges()
    liste_synonymous = tc.TaxonChanges()
    for tup in tupple:
        if is_referenced(tup.tupple,curr):
            tup.change_type = tc.ChangeType.REFERENCED_BY_TAXREF
            if is_changed_by_taxref(tup.tupple,curr):
                tup.is_additionnal_change = True
            else:
                tup.is_additionnal_change = False
        else:
            # tupp = get_tupple_taxref_from_db(tup.tupple[st.COLUMNS['cd_nom']['index']],curr)
            if is_synonymous_to_valid(tup.tupple, curr):
                tup.change_type = tc.ChangeType.SYNONYMOUS_TO_VALID
                if is_changed_by_taxref_other(tup.tupple, curr):
                    tup.is_additionnal_change = True
            elif is_valid_to_synonymous(tup.tupple, curr):
                tup.change_type = tc.ChangeType.VALID_TO_SYNONYMOUS
                if is_changed_by_taxref_other(tup.tupple, curr):
                    tup.is_additionnal_change = True
                get_taxon_from_taxref_to_insert_in_fatercal(tup, liste_cas_insert, liste_synonymous, taxref, curr, "VALID_TO_SYNONYMOUS")
            elif is_valid_taxon_change(tup.tupple,curr):
                tup.change_type = tc.ChangeType.VALID_TAXON_CHANGE
                if is_changed_by_taxref_other(tup.tupple, curr):
                    tup.is_additionnal_change = True
            elif is_higher_taxon_change(tup.tupple,curr):
                if is_changed_by_taxref_other(tup.tupple, curr):
                    tup.is_additionnal_change = True
                tup.change_type = tc.ChangeType.HIGHER_TAXON_CHANGE
                get_taxon_from_taxref_to_insert_in_fatercal(tup, liste_cas_insert, liste_synonymous, taxref, curr, "HIGHER_TAXON_CHANGE")
            else:
                tup.change_type = tc.ChangeType.NO_ID_CHANGE
    for tup in liste_synonymous:
        tup.change_type = tc.ChangeType.NEW_SYNONYMOUS
        tupple.append(tup)
    for tup in liste_cas_insert:
    	tupple.append(tup)


def get_taxon_from_taxref_to_insert_in_fatercal(tup, liste_cas_insert, liste_synonymous, taxref, curr, to_do):
    """
    The aim of this function is to detect any new taxon the tup need for updating    
    """
    if to_do == "VALID_TO_SYNONYMOUS":
        if not is_taxon_exist(tup.tupple[st.COLUMNS['cd_ref']['index']], curr) and is_in_file_with_cd_nom(taxref, tup.tupple[st.COLUMNS['cd_ref']['index']]):
            if not any(tupp for tupp in liste_cas_insert if tupp.tupple[st.COLUMNS['cd_nom']['index']] == tup.tupple[st.COLUMNS['cd_ref']['index']]):
                tupp = tc.TaxonChange(create_tupple_from_list_taxref2(get_tuple_from_file(taxref, tup.tupple, to_do)))
                tupp.change_type = tc.ChangeType.NEW_VALID_TAXON
                get_higner_taxon(tupp, taxref, liste_cas_insert, curr)
                liste_cas_insert.append(tupp)
                liste_synonymous1 = get_synonymous_from_file(taxref, tupp, curr)
                if liste_synonymous1 is not None:
                    for syn in liste_synonymous1:
                        liste_synonymous.append(syn)
        elif not is_taxon_exist(tup.tupple[st.COLUMNS['cd_ref']['index']], curr) and not is_in_file_with_cd_nom(taxref, tup.tupple[st.COLUMNS['cd_ref']['index']]):
            tup.is_updatable = False
            tup.user_message = 'Le nouveau taxon referent n\'existe pas dans le fichier importe ni dans la base de donnee:\nline: {}'.format(tup.tupple)
    elif to_do == "HIGHER_TAXON_CHANGE":
        if not is_taxon_exist(tup.tupple[st.COLUMNS['cd_sup']['index']], curr) and is_in_file_with_cd_nom(taxref, tup.tupple[st.COLUMNS['cd_sup']['index']]):
            if not any(tupp for tupp in liste_cas_insert if tupp.tupple[st.COLUMNS['cd_nom']['index']] == tup.tupple[st.COLUMNS['cd_sup']['index']]):
                tupp = tc.TaxonChange(create_tupple_from_list_taxref2(get_tuple_from_file(taxref, tup.tupple, to_do)))
                tupp.change_type = tc.ChangeType.NEW_VALID_TAXON
                get_higner_taxon(tupp, taxref, liste_cas_insert, curr)
                liste_cas_insert.append(tupp)
                liste_synonymous1 = get_synonymous_from_file(taxref, tupp, curr)
                if liste_synonymous1 is not None:
                    for syn in liste_synonymous1:
                        liste_synonymous.append(syn)
        elif not is_taxon_exist(tup.tupple[st.COLUMNS['cd_sup']['index']], curr) and not is_in_file_with_cd_nom(taxref, tup.tupple[st.COLUMNS['cd_sup']['index']]):
            tup.is_updatable = False
            tup.user_message = 'Le nouveau taxon superieur n\'existe pas dans le fichier importe ni dans la base de donnee:\nline: {}'.format(tup.tupple)


def get_higner_taxon(tup, taxref, liste_cas_insert, curr):
    """
        Get higher taxon if it doesn't exist in the db
    """
    tupp = tup.tupple
    to_continue = True
    while not is_taxon_exist(tupp[st.COLUMNS['cd_sup']['index']], curr) and to_continue:
        tupple = next((tupp2 for tupp2 in taxref if str(tupp2[st.COLUMNS['cd_nom']['index']]) == str(tupp[st.COLUMNS['cd_sup']['index']])), None)
        if tupple is None:
            to_continue = False
        else:
            tupp = tupple
            new_higher = tc.TaxonChange(create_tupple_from_list_taxref2(tupp))            
            new_higher.change_type = tc.ChangeType.NEW_VALID_TAXON
            liste_cas_insert.append(new_higher)


def get_synonymous_from_file(taxref, tup, curr):
    """
        The aim of this function is to get all the synonymous of valid taxon that are not not existant in the db 
    """
    list_syn = [tupp for tupp in taxref if str(tupp[st.COLUMNS['cd_ref']['index']]) == str(tup.tupple[st.COLUMNS['cd_nom']['index']])  and int(tupp[st.COLUMNS['cd_nom']['index']]) != int(tup.tupple[st.COLUMNS['cd_nom']['index']])]
    liste_synonymous = []
    for tupp in list_syn:
        if not is_taxon_exist(int(tupp[st.COLUMNS['cd_nom']['index']]), curr):
            syn = tc.TaxonChange(create_tupple_from_list_taxref2(tupp))
            liste_synonymous.append(syn)
    return liste_synonymous


def get_tupple_taxref_from_db(cd_nom, curr):
    """
		"cd_nom" an integer which is identifier and used to get information from the db

		"curr" the cursor used to send request to the db
    """
    curr.execute('''
        SELECT cd_nom, cd_ref, cd_sup, habitat, lb_auteur, lb_nom, nc, nom_complet, rang
        FROM taxon 
        WHERE cd_nom = %s
        ''',
        [cd_nom])
    return curr.fetchone()


def is_referenced(tup, curr):
    """
        This function will search all the data from Fatercal that have been referenced
        by taxref
		
		"tup" is a tupple which contains the information for a comparaison with the db

        "curr" the cursor used to send request to the db
    """
    curr.execute('''
        SELECT EXISTS(
            SELECT 1	
            FROM taxon
            WHERE lb_nom = %s AND lb_auteur = %s AND rang = %s
            AND cd_nom IS NULL AND cd_ref IS NULL)''',
        (tup[st.COLUMNS['lb_nom']['index']],
        tup[st.COLUMNS['lb_auteur']['index']],
        tup[st.COLUMNS['rang']['index']]))
    if not curr.fetchone()[0]:
        return False
    else:
        return True


def is_changed_by_taxref(tup, curr):
    """
        This function will search if the data from FATERCAL referenced by
        TAXREF has been modified

    	"tup" is a tuple which contains the information for a comparaison with the db

        "curr" the cursor used to send request to the db
    """
    curr.execute('''
        SELECT EXISTS (	
            SELECT 1	
            FROM taxon
            WHERE lb_nom = %s AND lb_auteur = %s AND (rang != %s
            or habitat != %s or nc != %s)
        )''',
        (tup[st.COLUMNS['lb_nom']['index']],
        tup[st.COLUMNS['lb_auteur']['index']],
        tup[st.COLUMNS['rang']['index']],
        tup[st.COLUMNS['habitat']['index']],
        tup[st.COLUMNS['nc']['index']],)
    )
    if not curr.fetchone()[0]:
        return True
    else:
        return False


def is_changed_by_taxref_other(tup, curr):
    """
        This function will search if the data from FATERCAL referenced by
        TAXREF has been modified

        "tup" is a tuple which contains the information for a comparaison with the db

        "curr" the cursor used to send request to the db
    """
    if tup[st.COLUMNS['nc']['index']] == '':
            nc = None
    else:
        nc = tup[st.COLUMNS['nc']['index']]
    if tup[st.COLUMNS['habitat']['index']] == '':
        habitat = None
    else:
        habitat = tup[st.COLUMNS['habitat']['index']]
    curr.execute('''
        SELECT EXISTS ( 
            SELECT 1
            FROM taxon
            WHERE cd_nom = %s AND (rang != %s or habitat != %s or nc != %s)
        )''',
        (tup[st.COLUMNS['cd_nom']['index']],
        tup[st.COLUMNS['rang']['index']],
        habitat,
        nc)
    )
    return curr.fetchone()[0]


def get_tuple_from_file(taxref, tupple, to_do):
    """
        The purpose of this function is to get a tuple from the file

        "taxref" a list created from a csv file which contains tuple

        "tupple" a tuple which contains the data we need to get the tuple from the file 
    """
    if to_do == "VALID_TO_SYNONYMOUS":
        return next((tup for tup in taxref if tup[st.COLUMNS['cd_nom']['index']] == tupple[st.COLUMNS['cd_ref']['index']]), None)
    elif to_do == "HIGHER_TAXON_CHANGE":
        return next((tup for tup in taxref if tup[st.COLUMNS['cd_nom']['index']] == tupple[st.COLUMNS['cd_sup']['index']]), None)


def is_taxon_exist(cd_nom, curr):
    """
		this function ask the database if the information exist in the db

		"tup" is a tuple which contains the information for a comparaison with the db

		"curr" the cursor used to send request to the db
	"""
    if cd_nom == '':
        cd_nom = None
    curr.execute('''
        SELECT EXISTS(
            SELECT 1
            FROM taxon
            WHERE cd_nom = %s
        )''',
        [cd_nom])
    return curr.fetchone()[0]


def is_new_synonymous(tup, curr):
    """
        The purpose of this function is see if the tup is a synonym or a new valid taxon
    
    	"tup" is a tuple which contains the information for a comparaison with the db

        "curr" the cursor used to send request to the db
    """
    if tup[st.COLUMNS['cd_nom']['index']] == tup[st.COLUMNS['cd_ref']['index']]:
        return False
    else:
        return True


def is_synonymous_to_valid(tup, curr):
    """
    	The purpose of this function is see if the synonymous from the db has became valid

    	"tup" is a tuple which contains the information for a comparaison with the db
    """
    tupp = get_tupple_taxref_from_db(tup[st.COLUMNS['cd_nom']['index']], curr)
    if tupp[st.COLUMNS['cd_nom']['index']] != tupp[st.COLUMNS['cd_ref']['index']] and tup[st.COLUMNS['cd_nom']['index']] == tup[st.COLUMNS['cd_ref']['index']] :
        return True
    else:
        return False


def is_valid_to_synonymous(tup, curr):
    """
        The purpose of this function is see if the valid taxon from the db has became a synonymous

        "tup" is a tuple which contains the information for a comparaison with the db
    """
    tupp = get_tupple_taxref_from_db(tup[st.COLUMNS['cd_nom']['index']], curr)
    if tupp[st.COLUMNS['cd_nom']['index']] == tupp[st.COLUMNS['cd_ref']['index']] and tup[st.COLUMNS['cd_nom']['index']] != tup[st.COLUMNS['cd_ref']['index']] :
        return True
    else:
        return False


def is_valid_taxon_change(tup, curr):
    """
        The purpose of this function is see if the synonymous from the db has changed of valid taxon

    	"tup" is a tuple which contains the information for a comparaison with the db
    """
    tupp = get_tupple_taxref_from_db(tup[st.COLUMNS['cd_nom']['index']], curr)
    if str(tupp[st.COLUMNS['cd_ref']['index']]) != str(tup[st.COLUMNS['cd_ref']['index']]):
        return True
    else:
        return False


def is_higher_taxon_change(tup, curr):
    """
        The purpose of this function is see if the valid taxon from the db has changed of higher taxon

        "tup" is a tuple which contains the information for a comparaison with the db

        "curr" the cursor used to send request to the db
    """
    tupp = get_tupple_taxref_from_db(tup[st.COLUMNS['cd_nom']['index']], curr)
    if tup[st.COLUMNS['cd_sup']['index']] != '':
        if str(tupp[st.COLUMNS['cd_sup']['index']]) != str(tup[st.COLUMNS['cd_sup']['index']]):
            return True
        else:
            return False
    else:
        return False


def is_in_file_with_cd_nom(taxref, cd):
	"""
		The aim of this function is to see if the taxon exist in the file (with comparison of the cd_nom)
		
		"taxref" a list created from a csv file which contains tuple

		"tup" a tuple which contain the data to compare
	"""
	return (any(tupp for tupp in taxref if (tupp[st.COLUMNS['cd_nom']['index']] == cd)))


def is_in_file(taxref, tup):
    """
        The aim of this function is to see if the taxon exist in the file (with comparison of the cd_nom)

        "taxref" a list created from a csv file which contains tuple

        "tup" a tuple which contain the data to compare
    """
    cd_ref = str(tup[st.COLUMNS['cd_ref']['index']])
    cd_sup = str(tup[st.COLUMNS['cd_sup']['index']])
    return (any(tupp for tupp in taxref if (tupp[st.COLUMNS['cd_nom']['index']] == cd_sup) or (tupp[st.COLUMNS['cd_nom']['index']] == cd_ref)))


def is_ref_in_db_or_file(taxref, tup, curr):
    """
         The aim of this function is to see if the taxon exist in the file or in db
		
        "taxref" a list created from a csv file which contains tuple

        "tup" a tuple which contain the data to compare

        "curr" the cursor used to send request to the db
    """
    if tup.tupple[st.COLUMNS['cd_sup']['index']] != '':
        curr.execute('''
            SELECT EXISTS(
                SELECT 1
    			FROM taxon
    			WHERE (cd_nom = %s) and (cd_nom = %s) and cd_nom is not Null
    		)''',
    		(tup.tupple[st.COLUMNS['cd_ref']['index']],
            tup.tupple[st.COLUMNS['cd_sup']['index']])
        )
    else:
        curr.execute('''
            SELECT EXISTS(
                SELECT 1
                FROM taxon
                WHERE (cd_nom = %s)
            )''',
            (tup.tupple[st.COLUMNS['cd_ref']['index']],)
        )
    result = curr.fetchone()
    if not result[0] and not is_in_file(taxref, tup.tupple):
        tup.user_message = tup.user_message + '\nUne erreur est apparu :\ncd_nom : '
        tup.user_message = tup.user_message +str(tup.tupple[st.COLUMNS['cd_nom']['index']])
        tup.user_message = tup.user_message +'\nLe taxon valide de ce synonyme n\'existe pas :\n cd_ref : '
        tup.user_message = tup.user_message +str(tup.tupple[st.COLUMNS['cd_ref']['index']])
        return False
    elif not is_in_file(taxref, tup.tupple) and tup.tupple[st.COLUMNS['cd_sup']['index']] != '':
        curr.execute('''
            SELECT EXISTS(
                SELECT 1
                FROM taxon
                WHERE (cd_nom = %s)
            )''',
    		[tup.tupple[st.COLUMNS['cd_sup']['index']]]
        )
        if curr.fetchone()[0] and not is_in_file(taxref, tup.tupple) :
            tup.user_message = tup.user_message +'\nUne erreur est apparu : cd_nom : '
            tup.user_message = tup.user_message +str(tup.tupple[st.COLUMNS['cd_nom']['index']])
            tup.user_message = tup.user_message +'\nLe taxon superieur de ce taxon n\'existe pas. \ncd_sup : '
            tup.user_message = tup.user_message +str(tup.tupple[st.COLUMNS['cd_sup']['index']])
            return False
        else:
            return True
    else:
        return True


def vef_of_ref(taxref, tupple, curr):
    """
        The aim of this function is to see if the taxon is referenced by a taxon from FATERCAL
		
        "taxref" a list created from a csv file which contains tuple

        "tup" a tuple which contain the data to compare
		
        "curr" the cursor used to send request to the db
    """
    for tup in tupple:
        tup.is_updatable = is_ref_in_db_or_file(taxref, tup, curr)


def is_ref_by_fatercal_taxon(tup, curr):
	"""
		The aim of this function is to see if the taxon is referenced by a taxon from FATERCAL
		
		"taxref" a list created from a csv file which contains tuple

		"tup" a tuple which contain the data to compare
		
		"curr" the cursor used to send request to the db
	"""
	curr.execute('''
        SELECT EXISTS(
            SELECT 1
            FROM taxon
            WHERE id_ref = (SELECT id FROM taxon WHERE cd_nom =%s)
            AND cd_nom IS NULL AND cd_ref IS NULL AND cd_sup IS NULL
        )''',
        [tup.tupple[st.COLUMNS['cd_nom']['index']]])
	if curr.fetchone()[0]:
		return {'old_cd_nom': tup.tupple[st.COLUMNS['cd_nom']['index']],
        'new_cd_nom' : tup.tupple[st.COLUMNS['cd_ref']['index']],
        'is_cd_ref' : True}
	else:
		curr.execute('''
            SELECT EXISTS(
                SELECT 1
                FROM taxon
                WHERE id_sup = (SELECT id FROM taxon WHERE cd_nom =%s)
                AND cd_nom IS NULL AND cd_ref IS NULL AND cd_sup IS NULL
			)''',
			[tup.tupple[st.COLUMNS['cd_nom']['index']]])
		if curr.fetchone()[0]:
			return {'old_cd_nom': tup.tupple[st.COLUMNS['cd_nom']['index']],
            'new_cd_nom' : tup.tupple[st.COLUMNS['cd_nom']['index']],
            'is_cd_ref' : False}
		else:
			return False

#  ----------------------------End : Define data update-----------------------------

#  ----------------------------Start : Inser data-----------------------------


def insert_new_taxon_and_synonymous(list_new_tax_and_syn, curr):
    for tup in list_new_tax_and_syn:
        if tup.is_updatable and tup.is_accepted_by_user and tup.change_type == tc.ChangeType.NEW_VALID_TAXON:
            if tup.tupple[st.COLUMNS['cd_sup']['index']] is not None:
                curr.execute('''
                    SELECT id 
                    FROM taxon
                    WHERE cd_nom = %s''',
                    [tup.tupple[st.COLUMNS['cd_sup']['index']]]
                )
                id_sup = curr.fetchone()[0]
            else:
                id_sup = None
            curr.execute('''
                INSERT INTO taxon(id_sup, cd_nom, cd_ref, cd_sup, habitat, lb_auteur, lb_nom, nom_complet, rang)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, cd_nom''',
                (id_sup,
                tup.tupple[st.COLUMNS['cd_nom']['index']],
                tup.tupple[st.COLUMNS['cd_ref']['index']],
                tup.tupple[st.COLUMNS['cd_sup']['index']],
                tup.tupple[st.COLUMNS['habitat']['index']],
                tup.tupple[st.COLUMNS['lb_auteur']['index']],
                tup.tupple[st.COLUMNS['lb_nom']['index']],
                tup.tupple[st.COLUMNS['nom_complet']['index']],
                tup.tupple[st.COLUMNS['rang']['index']]
                )
            )
            id_sup, cd_nom = curr.fetchone()
            list_syn = [tup for tup in list_new_tax_and_syn if cd_nom == tup.tupple[st.COLUMNS['cd_ref']['index']] and tup.is_updatable and tup.is_accepted_by_user and tup.change_type == tc.ChangeType.NEW_SYNONYMOUS]
            if list_syn != None:
                for tupp in list_syn:
                    curr.execute('''
                        INSERT INTO taxon(id_ref, cd_nom, cd_ref, habitat, lb_auteur, lb_nom, nom_complet, rang)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                        ''',
                        (id_sup,
                        tupp.tupple[st.COLUMNS['cd_nom']['index']],
                        tupp.tupple[st.COLUMNS['cd_ref']['index']],
                        tupp.tupple[st.COLUMNS['habitat']['index']],
                        tupp.tupple[st.COLUMNS['lb_auteur']['index']],
                        tupp.tupple[st.COLUMNS['lb_nom']['index']],
                        tupp.tupple[st.COLUMNS['nom_complet']['index']],
                        tupp.tupple[st.COLUMNS['rang']['index']])
                    )


def update_ref_by_taxref(taxref, tupple, list_ref_by_taxref, curr):
    with open('taxon_problem.csv','w') as csvfile :
        spamwriter = csv.writer(csvfile, delimiter=';')
        for tup in list_ref_by_taxref:
            if tup.is_updatable:
                if not is_in_db(tup.tupple[st.COLUMNS['cd_nom']['index']], curr):
                    if tup.tupple[st.COLUMNS['cd_ref']['index']] != tup.tupple[st.COLUMNS['cd_nom']['index']]:
                        curr.execute('''
                            UPDATE taxon
                            SET cd_nom = %s, cd_ref = %s
                            WHERE lb_nom = %s and lb_auteur = %s and rang = %s
                            ''',
                            (tup.tupple[st.COLUMNS['cd_nom']['index']],
                            tup.tupple[st.COLUMNS['cd_ref']['index']],
                            tup.tupple[st.COLUMNS['lb_nom']['index']],
                            tup.tupple[st.COLUMNS['lb_auteur']['index']],
                            tup.tupple[st.COLUMNS['rang']['index']]
                            )
                        )
                    else:
                        curr.execute('''
                            UPDATE taxon
                            SET cd_nom = %s, cd_ref = %s, cd_sup = %s
                            WHERE lb_nom = %s and lb_auteur = %s and rang = %s
                            ''',
                            (tup.tupple[st.COLUMNS['cd_nom']['index']],
                            tup.tupple[st.COLUMNS['cd_ref']['index']],
                            tup.tupple[st.COLUMNS['cd_sup']['index']],
                            tup.tupple[st.COLUMNS['lb_nom']['index']],
                            tup.tupple[st.COLUMNS['lb_auteur']['index']],
                            tup.tupple[st.COLUMNS['rang']['index']]
                            )
                        )
                else:
                    spamwriter.writerow(tup.tupple)


def is_in_db(cd_nom, curr):
    curr.execute('''
        SELECT EXISTS(
            SELECT 1
            FROM taxon
            WHERE cd_nom = %s
        )
        ''',
        [cd_nom]
    )
    return curr.fetchone()[0]


def get_tupple_fatercal_from_db(cd_nom, curr):
    """
        "cd_nom" an integer which is identifier and used to get information from the db

        "curr" the cursor used to send request to the db
    """
    curr.execute('''
        SELECT id, id_ref, id_sup
        FROM taxon
        WHERE cd_nom = %s
        ''',
        [cd_nom])
    return curr.fetchone()


def update_syn_to_valid(list_syn_to_valid, curr):
    for tup in list_syn_to_valid:
        if tup.is_updatable and tup.is_accepted_by_user:
            curr.execute('''
                UPDATE taxon
                SET id_ref = id, cd_ref = cd_nom, cd_sup = %s,
                id_sup = (SELECT id
                                FROM TAXON
                                WHERE cd_nom = %s)
                WHERE cd_nom = %s''',
                (tup.tupple[st.COLUMNS['cd_sup']['index']],
                tup.tupple[st.COLUMNS['cd_sup']['index']],
                tup.tupple[st.COLUMNS['cd_nom']['index']]
                )
            )
            update_additionnal_change(tup, curr)


def update_valid_to_syn(list_valid_to_syn, curr):
    for tup in list_valid_to_syn:
        if tup.is_updatable and tup.is_accepted_by_user:
            curr.execute('''
                UPDATE taxon
                SET id_ref = (SELECT id
                                FROM TAXON
                                WHERE cd_nom = %s),
                id_sup = Null,
                cd_ref = %s, cd_sup = NULL
                WHERE cd_nom = %s''',
                (tup.tupple[st.COLUMNS['cd_ref']['index']],
                tup.tupple[st.COLUMNS['cd_ref']['index']],
                tup.tupple[st.COLUMNS['cd_nom']['index']]
                )
            )
            update_additionnal_change(tup, curr)


def update_valid_taxon_change(list_valid_taxon_change, curr):
    for tup in list_valid_taxon_change:
        if tup.is_updatable and tup.is_accepted_by_user:
            curr.execute('''
                UPDATE taxon
                SET id_ref = (SELECT id
                                FROM TAXON
                                WHERE cd_nom = %s),
                cd_ref = %s
                WHERE cd_nom = %s''',
                (tup.tupple[st.COLUMNS['cd_ref']['index']],
                tup.tupple[st.COLUMNS['cd_ref']['index']],
                tup.tupple[st.COLUMNS['cd_nom']['index']]
                )
            )
            update_additionnal_change(tup, curr)


def update_higher_taxon_change(list_higher_taxon_change, curr):
    for tup in list_higher_taxon_change:
        if tup.is_updatable and tup.is_accepted_by_user:
            curr.execute('''
                UPDATE taxon
                SET id_sup = (SELECT id
                                FROM TAXON
                                WHERE cd_nom = %s),
                cd_sup = %s
                WHERE cd_nom = %s''',
                (tup.tupple[st.COLUMNS['cd_sup']['index']],
                tup.tupple[st.COLUMNS['cd_sup']['index']],
                tup.tupple[st.COLUMNS['cd_nom']['index']]
                )
            )
            update_additionnal_change(tup, curr)


def update_no_id_change(list_no_id_change, curr):
    for tup in list_no_id_change:
        if tup.tupple[st.COLUMNS['nc']['index']] == '':
            nc = None
        else:
            nc = tup.tupple[st.COLUMNS['nc']['index']]
        if tup.tupple[st.COLUMNS['habitat']['index']] == '':
            habitat = None
        else:
            habitat = tup.tupple[st.COLUMNS['habitat']['index']]
        if tup.is_updatable and tup.is_accepted_by_user:
            curr.execute('''
                UPDATE taxon
                SET rang = %s, habitat = %s, nc = %s
                WHERE cd_nom = %s''',
                (tup.tupple[st.COLUMNS['rang']['index']],
                habitat,
                nc,
                tup.tupple[st.COLUMNS['cd_nom']['index']]
                )
            )


def update_additionnal_change(tup, curr):
    if tup.is_additionnal_change:
        if tup.tupple[st.COLUMNS['nc']['index']] == '':
            nc = None
        else:
            nc = tup.tupple[st.COLUMNS['nc']['index']]
        if tup.tupple[st.COLUMNS['habitat']['index']] == '':
            habitat = None
        else:
            habitat = tup.tupple[st.COLUMNS['habitat']['index']]
        curr.execute('''
            UPDATE taxon
            SET rang = %s, habitat = %s, nc = %s
            WHERE cd_nom = %s''',
            (tup.tupple[st.COLUMNS['rang']['index']],
            habitat,
            nc,
            tup.tupple[st.COLUMNS['cd_nom']['index']]
            )
        )


def update_data(list_ref_by_taxref, list_syn_to_valid, list_valid_to_syn, list_valid_taxon_change, list_higher_taxon_change, list_no_id_change, list_new_tax_and_syn, update_ref, curr):
    insert_new_taxon_and_synonymous(list_new_tax_and_syn, curr)    
    update_syn_to_valid(list_syn_to_valid, curr)
    update_valid_to_syn(list_valid_to_syn, curr)
    update_valid_taxon_change(list_valid_taxon_change, curr)
    update_higher_taxon_change(list_higher_taxon_change, curr)
    update_no_id_change(list_no_id_change, curr)


#  ----------------------------End : Inser data-----------------------------

#  ----------------------------End : Update data-----------------------------

"""

"""