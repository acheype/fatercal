import psycopg2 as p2
import psycopg2.extras as p2_extra
import numpy as np
import time
import sys
import csv

import settings as st
import taxonChange as tc
import function as fc

# Get data from file
print('Script d\'importation d\'une nouvelle version du référentiel de Taxref...\nInfo : le fichier doit être nommé \'taxref_animalia.csv\' et enregistré avec l\'encodage UTF-8.')
sorted_columns = sorted(st.COLUMNS.items(), key=lambda t : t[1]['index'])
csv_index = [value['csv_index'] for key,value in sorted_columns]
taxref = []

try:
    # Connect to database
    conn = p2.connect(
        dbname ='fatercal',
        host ='postgres',
        user ='postgres',
        password ='123'
    )
    curr = conn.cursor()
    with open('taxref_animalia.csv','r') as f:
        reader = csv.reader(f,delimiter='\t')
        for row in reader:
            tupple = [row[tup] for tup in csv_index]
            taxref.append(tupple)
    del taxref[0]
    i = 0
    tupple = fc.get_difference_between_bdd(taxref, curr)
    if len(tupple) != 0:
        t = 'Info : Il y a {} lignes qui réfèrent à des taxons déjà existants dans Fatercal et qui comportent des modifications dans Taxref.\nVoulez-vous poursuivre ?'.format(len(tupple))
        if fc.query_yes_no(t):
            fc.classify_change_type(taxref, tupple, curr)
            fc.vef_of_ref(taxref, tupple, curr)
            list_ref_by_taxref, list_syn_to_valid, list_valid_to_syn, list_valid_taxon_change, list_higher_taxon_change, list_no_id_change, list_new_tax_and_syn = fc.make_list_of_update(tupple, curr)
            for tup in list_ref_by_taxref:
                i = i + 1
            if i !=0:
                t = "\nIl y a {} taxon(s) qui a/ont recu un identifiant de taxref.\n!! Attention la validité d'un ou de plusieurs taxons a peut-être été mise à jour par Taxref. Veuillez consultez le fichier 'taxon_to_verify.csv' pour prendre connaisssance des mises à jour sur ces taxons et les répercuter si besoin via l'interface graphique !!\nVoulez-vous mettre à jour les identifiants (cd_nom) ? Dans le cas contraire le programme s'arrêtera !!".format(i)
            else:
                t = "\nIl n'y a aucun taxon qui a recu un identifiant de taxref. Voulez-vous continuer ? Dans le cas contraîre le programme s'arrètera !!"
            update_ref = fc.query_yes_no(t)
            if update_ref:
                with open('taxon_to_verify.csv','w') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=';')
                    spamwriter.writerow(['CD_NOM', 'CD_REF', 'CD_SUP', 'HABITAT', 'LB_AUTEUR', 'LB_NOM', 'NC', 'NOM_COMPLET', 'RANG', 'NOM_VERN', 'NOM_VERN_ENG'])
                    for tup in list_ref_by_taxref:
                        spamwriter.writerow(tup.tupple)
                fc.update_ref_by_taxref(taxref, tupple, list_ref_by_taxref, curr)
                for tup in reversed(tupple):
                    if tup.change_type != tc.ChangeType.REFERENCED_BY_TAXREF:
                        msg = fc.get_msg_for_user(taxref, tup, curr, tupple, tc.ChangeType.SYNONYMOUS_TO_VALID)
                        print('\n' + str(tup.tupple[st.COLUMNS['lb_nom']['index']]) + ' ' + str(tup.tupple[st.COLUMNS['lb_auteur']['index']]) + ', cd_nom = ' + str(tup.tupple[st.COLUMNS['cd_nom']['index']]))
                        print(msg)
                        if tup.is_updatable:
                            tup.is_accepted_by_user = fc.query_yes_no("Voulez-vous le mettre à jour/ l'insérer ?")
                            if  not tup.is_accepted_by_user and tup.change_type == tc.ChangeType.NEW_VALID_TAXON:
                                for dep_tax in tupple:
                                    if str(dep_tax.tupple[st.COLUMNS['cd_ref']['index']]) == str(tup.tupple[st.COLUMNS['cd_nom']['index']]) or str(dep_tax.tupple[st.COLUMNS['cd_sup']['index']]) == str(tup.tupple[st.COLUMNS['cd_nom']['index']]):
                                        dep_tax.is_updatable = False
                                        if dep_tax.change_type == tc.ChangeType.HIGHER_TAXON_CHANGE:
                                            dep_tax.user_message += 'Ce taxon ne peut être inséré ou mis à jour car son supérieur est le taxon {}, cd_nom = {} que vous avez précédemment refusé d\'insérer'.format(tup.tupple[st.COLUMNS['nom_complet']['index']], tup.tupple[st.COLUMNS['cd_nom']['index']])
                                        else:
                                            dep_tax.user_message += 'Ce taxon ne peut être inséré ou mis à jour car son référent est le taxon {}, cd_nom = {} que vous avez précédemment refusé d\'insérer'.format(tup.tupple[st.COLUMNS['nom_complet']['index']], tup.tupple[st.COLUMNS['cd_nom']['index']])
                list_ref_by_taxref, list_syn_to_valid, list_valid_to_syn, list_valid_taxon_change, list_higher_taxon_change, list_no_id_change, list_new_tax_and_syn = fc.make_list_of_update(tupple, curr)
                fc.update_data(list_ref_by_taxref, list_syn_to_valid, list_valid_to_syn, list_valid_taxon_change, list_higher_taxon_change, list_no_id_change, list_new_tax_and_syn, update_ref, curr)
    else:
        print('Il n\'y a aucune différence.')
    curr.execute('''
        UPDATE taxon
        set id_ref=id
        WHERE id_ref IS Null
        ''',)
    conn.commit()
    curr.close()
    conn.close()
    print('''
Merci d'avoir utilisé le script d'import fatercal
Made by Laurent Schaeffer, managed by Adrien Cheype
    '''
    )
except p2.DatabaseError as exception:
    print(exception)
    sys.exit(1)
except FileNotFoundError:
    print('Le fichier \'taxref_anima.csv\' n\'a pas été trouvé.' )
finally:
    if conn:
        conn.close()
