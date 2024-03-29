import re

from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import F, Q, Max
from django.template import loader
from django.urls import reverse

from .forms import ChooseTaxonToInsert

from .models import Taxon, Prelevement, Localisation, TypeEnregistrement, Recolteur, TypeLoc, HabitatDetail, \
    TaxrefExport, TaxrefUpdate, TaxrefRang, TaxrefHabitat, TaxrefStatus
from .variable import regex_date, list_hierarchy
import os


def update_taxon_ref(taxon_to_change, cleaned_data):
    """
    Change the ref of the taxon
    :param taxon_to_change:
    :param cleaned_data:
    :return:
    """
    list_syn = Taxon.objects.filter(id_ref=taxon_to_change)
    list_child = Taxon.objects.filter(id_sup=taxon_to_change)
    for child in list_child:
        child.id_sup = cleaned_data['taxon']
        child.save()
    for syn in list_syn:
        syn.id_ref = cleaned_data['taxon']
        syn.save()
    if cleaned_data['taxon'] != cleaned_data['taxon'].id_ref:
        cleaned_data['taxon'].id_ref = cleaned_data['taxon']
        cleaned_data['taxon'].id_sup = taxon_to_change.id_sup
        cleaned_data['taxon'].save()
    taxon_to_change.id_ref = cleaned_data['taxon']
    taxon_to_change.id_sup = None
    taxon_to_change.save()


def update_taxon_sup(taxon_to_change, cleaned_data):
    """
    Change the superior of the taxon
    :param taxon_to_change:
    :param cleaned_data:
    :return: the template and an error (if its got one)
    """
    taxon_to_change.id_sup = cleaned_data['taxon_superieur']
    try:
        taxon_to_change.clean()
        error = ''
        taxon_to_change.save()
        template = loader.get_template('fatercal/return_change_taxon.html')
        return template, error
    except ValidationError as e:
        template = loader.get_template('fatercal/change_taxon.html')
        error = e.message
        return template, error


def get_recolteur(prelev):
    """
    Get the Harvesteur's for a specific sample
    :param recolteur:
    :param prelev: the object
    :return: a string
    """
    list_recolt = Recolteur.objects.filter(prelevement=prelev.id)
    if len(list_recolt) > 0:
        str_recolt = ''
        first = True
        for recolt in list_recolt.iterator():
            if first:
                first = False
            else:
                str_recolt += ', '
            str_recolt += '{}'.format(recolt.lb_auteur)
        return str_recolt
    else:
        return 'Récolteur inconnu'


def get_superior(taxon):
    """
    This function get name of superior
    :param taxon: The object Taxon from which we want the information we need
    :return: a list containing a summary of the different info on the taxon
    """
    parent_taxon, nb = taxon.get_hierarchy()
    dict_parent = {}
    if parent_taxon is not None:
        for parent in parent_taxon:
            dict_parent[parent.rang.rang] = parent.lb_nom
    return dict_parent


def get_msg(taxon):
    """
    This function aim to get a message if it's != or not between Fatercal and Taxref in the csv file
    :param taxon: the object from the Taxon model
    :return a tupple:
    """
    if taxon.cd_nom is None:
        return 'x', None, None, None
    elif (taxon.id_ref != taxon and taxon.cd_ref == taxon.id_ref.cd_nom) or \
            (taxon.id_ref == taxon and taxon.cd_ref != taxon.cd_nom):
        return None, None, None, 'x'
    elif taxon.cd_ref != taxon.id_ref.cd_nom:
        return None, 'x', None, None
    elif taxon.cd_sup is not None:
        if taxon.cd_sup != taxon.id_sup.cd_nom:
            return None, None, 'x', None
    return None, None, None, None


def get_taxon_from_search(list_param):
    """
    This function get all Information needed from all taxon from the user's search parameter
    :param list_param: a dict which contains the parameters
    :return: a list of tuple
    """
    if list_param is None:
        list_not_proper = Taxon.objects.all()
    else:
        list_not_proper = get_specific_search_taxon(list_param)
    list_taxon = [
        ('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN', 'ID', 'ID_REF', 'ID_SUP',
         'CD_NOM', 'CD_TAXSUP', 'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM', 'LB_AUTEUR', 'NOM_COMPLET', 'NOM_COMPLET_HTML',
         'NOM_VALIDE', 'NOM_VERN', 'NOM_VERN_ENG', 'HABITAT', 'NC', 'NON PRESENT DANS TAXREF',
         'CD_REF DIFFERENT', 'CD_SUP DIFFERENT', 'VALIDITY DIFFERENT')
    ]
    for taxon in list_not_proper.iterator():
        # Taxref don't want unamed Taxon so we don't append it to the list
        if 'sp.' not in taxon.lb_nom:
            tupple = construct_cleaned_taxon(taxon)
            list_taxon.append(tupple)
    return list_taxon


def get_taxon_from_search_taxref(list_param):
    """
    This function get all Information needed from all taxon from the user's search parameter
    :param list_param: a dict which contains the parameters
    :return: a list of tuple
    """
    if list_param is None:
        list_not_proper = TaxrefExport.objects.all()
    else:
        list_not_proper = get_specific_search_taxon_taxref(list_param)
    list_taxon = [
        ('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN', 'ID', 'ID_REF', 'ID_SUP',
         'CD_NOM', 'CD_TAXSUP', 'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM', 'LB_AUTEUR', 'NOM_COMPLET', 'NOM_COMPLET_HTML',
         'NOM_VALIDE', 'NOM_VERN', 'NOM_VERN_ENG', 'HABITAT', 'NC', 'GRANDE_TERRE', 'ILES_LOYAUTE', 'AUTRE',
         'NON PRESENT DANS TAXREF', 'CD_REF DIFFERENT', 'CD_SUP DIFFERENT', 'VALIDITY DIFFERENT')
    ]
    for taxon in list_not_proper:
        taxref_format = (taxon.regne, taxon.phylum, taxon.classe, taxon.ordre, taxon.famille, taxon.group1_inpn,
                         taxon.group2_inpn, taxon.id, taxon.id_ref, taxon.id_sup, taxon.cd_nom, taxon.cd_taxsup,
                         taxon.cd_sup, taxon.cd_ref, taxon.rang, taxon.lb_nom, taxon.lb_auteur, taxon.nom_complet,
                         taxon.nom_complet_html, taxon.nom_valide, taxon.nom_vern, taxon.nom_vern_eng, taxon.habitat,
                         taxon.nc, taxon.grande_terre, taxon.iles_loyaute, taxon.autre, taxon.non_present,
                         taxon.cd_ref_diff, taxon.cd_sup_diff, taxon.validity_diff)
        list_taxon.append(taxref_format)
    return list_taxon


def construct_cleaned_taxon(taxon):
    """
    Construct a tuple in the form we want for the csv
    :param taxon: a taxon object
    :return: a tuple
    """
    msg = get_msg(taxon)
    if taxon.habitat is None:
        habitat = None
    else:
        habitat = taxon.habitat.habitat
    if taxon.nc is None:
        statut = None
    else:
        statut = taxon.nc.status
    if taxon.id == taxon.id_ref_id:
        if taxon.id_sup is None:
            id_sup = None
        else:
            id_sup = taxon.id_sup_id
        dict_parent = get_superior(taxon)
        tupple = (dict_parent.get('KD'), dict_parent.get('PH'), dict_parent.get('CL'), dict_parent.get('OR'),
                  dict_parent.get('FM'), None, None, taxon.id, taxon.id_ref_id, id_sup,
                  taxon.cd_nom, None, taxon.cd_sup, taxon.cd_ref, taxon.rang.rang, taxon.lb_nom, taxon.lb_auteur,
                  taxon.nom_complet, None, taxon.lb_nom, None, None, habitat, statut) + msg
    else:
        dict_parent = get_superior(taxon.id_ref)
        tupple = (dict_parent.get('KD'), dict_parent.get('PH'), dict_parent.get('CL'), dict_parent.get('OR'),
                  dict_parent.get('FM'), None, None, taxon.id, taxon.id_ref_id, None,
                  taxon.cd_nom, None, taxon.cd_sup, taxon.cd_ref, taxon.rang.rang, taxon.lb_nom, taxon.lb_auteur,
                  taxon.nom_complet, None, taxon.id_ref.lb_nom, None, None, habitat, statut) + msg
    return tupple


def get_taxon_personal(form):
    """
    Get the list of taxon the user get from its search
    :param form: an form object (See Django doc)
    :return: a list
    """
    list_not_proper = get_specific_search_taxon(form.cleaned_data)
    if 'q' in form.cleaned_data:
        del form.cleaned_data['q']
    if 'nc__status__exact' in form.cleaned_data:
        del form.cleaned_data['nc__status__exact']
    if 'rang__rang__exact' in form.cleaned_data:
        del form.cleaned_data['rang__rang__exact']
    if 'valide' in form.cleaned_data:
        del form.cleaned_data['valide']
    return construct_list_taxon(list_not_proper, form.cleaned_data)


def construct_list_taxon(list_not_proper, cleaned_data):
    """
    Construct the list of taxon for the csv
    :param list_not_proper: a queryset object (see Django doc)
    :param cleaned_data: a dict from the form object (see Django doc)
    :return: a list
    """
    cleaned_list = ()
    for (key, value) in cleaned_data.items():
        if cleaned_data[key]:
            cleaned_list += (key,)
    list_taxon = [cleaned_list, ]
    if cleaned_list == ():
        return list_taxon
    else:
        for taxon in list_not_proper.iterator():
            cleaned_taxon = construct_cleaned_taxon_search(taxon, cleaned_data)
            list_taxon.append(cleaned_taxon)
    return list_taxon


def construct_cleaned_taxon_search(taxon, cleaned_data):
    """
    Construct a tuple with field requested by the user
    :param taxon: An taxon object from the model Taxon
    :param cleaned_data: a dict from the form object (see Django doc)
    :return: a tuple
    """
    cleaned_taxon = ()
    if cleaned_data['id']:
        cleaned_taxon += (taxon.id,)
    if taxon.id == taxon.id_ref_id:
        if taxon.id_sup is None:
            cleaned_taxon += (None,)
        else:
            if cleaned_data['id_sup']:
                cleaned_taxon += (taxon.id_sup_id,)
    else:
        cleaned_taxon += (None,)
    if cleaned_data['id_ref']:
        cleaned_taxon += (taxon.id_ref_id,)
    if cleaned_data['name']:
        cleaned_taxon += (taxon.lb_nom,)
    if cleaned_data['author']:
        cleaned_taxon += (taxon.lb_auteur,)
    if cleaned_data['rank']:
        cleaned_taxon += (taxon.rang.lb_rang,)
    if taxon.id == taxon.id_ref_id:
        if cleaned_data['rank_sup']:
            cleaned_taxon += (taxon.id_sup,)
    else:
        cleaned_taxon += (None,)
    if taxon.nc is None:
        cleaned_taxon += (None,)
    else:
        if cleaned_data['status']:
            cleaned_taxon += (taxon.nc.lb_status,)
    if taxon.habitat is None:
        cleaned_taxon += (None,)
    else:
        if cleaned_data['habitat']:
            cleaned_taxon += (taxon.habitat.lb_habitat,)
    if cleaned_data['grande_terre']:
        cleaned_taxon += (taxon.grande_terre,)
    if cleaned_data['loyalty_island']:
        cleaned_taxon += (taxon.iles_loyaute,)
    if cleaned_data['other']:
        cleaned_taxon += (taxon.autre,)
    if taxon.remarques is None:
        cleaned_taxon += (None,)
    else:
        if cleaned_data['remark']:
            cleaned_taxon += (taxon.remarques.replace('\n', ''),)
    if taxon.sources is None:
        cleaned_taxon += (None,)
    else:
        if cleaned_data['source']:
            cleaned_taxon += (taxon.sources.replace('\n', ''),)
    if taxon.reference_description is None:
        cleaned_taxon += (None,)
    else:
        if cleaned_data['description_reference']:
            cleaned_taxon += (taxon.reference_description.replace('\n', ''),)
    return cleaned_taxon


def get_sample(param):
    """
    This function get all Information needed from all or specific sample
    :param param: the parameter's if the user want to export his research
    :return: a list of tuple
    """
    if not param:
        list_not_proper = Prelevement.objects.all()
    else:
        list_not_proper = get_specific_search_sample(param)
    list_sample = [
        ('Code identification', 'Ordre', 'Famille', 'Sous-Famille', 'Genre', 'Sous-Genre', 'Espece',
         'Sous-Espece', 'Auteur(s)/date', 'Date', 'Collecteurs', 'Identificateur', "Date d'identification",
         'Altitude(m)', 'Pays', 'Region', 'Commune', 'Lieu dit', 'Type de milieu', 'Nombre', 'Sexe', 'Capture/relacher',
         'Informations complémentaires', 'Photo', 'X WGS 84', 'Y WGS 84', 'X RGNC', 'Y RGNC')
    ]
    for sample in list_not_proper.iterator():
        harvesters = get_recolteur(sample)
        dict_loc = get_loc_from_sample(sample)
        taxon = Taxon.objects.get(id=sample.id_taxon)
        if taxon.id != taxon.id_ref_id:
            dict_hierarchy = get_hierarchy_to_dict(taxon.id_ref)
        else:
            dict_hierarchy = get_hierarchy_to_dict(taxon)
        altitude = format_altitude_sample(sample)
        tupple = (sample.id, dict_hierarchy.get('Ordre'), dict_hierarchy.get('Famille'),
                  dict_hierarchy.get('Sous-Famille'), dict_hierarchy.get('Genre'), dict_hierarchy.get('Sous-Genre'),
                  dict_hierarchy.get('Espèce'), dict_hierarchy.get('Sous-Espèce'), sample.id_taxon.lb_auteur,
                  sample.date, harvesters, None, None, altitude, dict_loc.get('Pays'), dict_loc.get('Region'),
                  dict_loc.get('Secteur'), dict_loc.get('nom'), sample.habitat, sample.nb_individus,
                  sample.type_specimen, sample.mode_de_collecte, sample.infos_compl, None,
                  sample.toponymie_x, sample.toponymie_y)
        list_sample.append(tupple)
    return list_sample


def get_loc_from_sample(sample):
    """
    Get the localisation hierarchy in a dict to use it in the database
    :param sample: an object sample
    :return: a dictionnary
    """
    if sample.id is None:
        return {}
    else:
        loc = sample.localisation
        dict_loc = {}
        while loc is not None:
            dict_loc[loc.loc_type.type] = loc.nom
            loc = loc.id_sup
        return dict_loc


def format_altitude_sample(sample):
    """
    Return the altitude in a string
    :param sample: an object sample
    :return: a string
    """
    if sample.altitude_min is None:
        return sample.altitude_max
    elif sample.altitude_max is None:
        return sample.altitude_min
    else:
        return "{}-{}".format(sample.altitude_min, sample.altitude_max)


def get_specific_search_taxon(list_param):
    """
    Filter from the user's parameter
    :param list_param:
    :return: a list of taxon
    """
    list_not_proper = Taxon.objects.all()
    if 'q' in list_param:
        if list_param['q'] != '':
            list_not_proper = list_not_proper.filter(Q(lb_auteur__icontains=list_param['q']) |
                                                     Q(lb_nom__icontains=list_param['q']))
    if 'nc__status__exact' in list_param:
        if list_param['nc__status__exact'] != '':
            list_not_proper = list_not_proper.filter(nc__status=list_param['nc__status__exact'])
    if 'rang__rang__exact' in list_param:
        if list_param['rang__rang__exact'] != '':
            list_not_proper = list_not_proper.filter(rang__rang=list_param['rang__rang__exact'])
    if 'valide' in list_param:
        if list_param['valide'] != '':
            if list_param['valide'] == 'valide':
                list_not_proper = list_not_proper.filter(id=F('id_ref'))
            else:
                list_not_proper = list_not_proper.filter(~Q(id=F('id_ref')))
    return list_not_proper


def get_specific_search_taxon_taxref(list_param):
    """
    Filter from the user's parameter
    :param list_param:
    :return: a list of taxon
    """
    list_not_proper = TaxrefExport.objects.all()
    if 'q' in list_param:
        if list_param['q'] != '':
            list_not_proper = list_not_proper.filter(Q(lb_auteur__icontains=list_param['q']) |
                                                     Q(lb_nom__icontains=list_param['q']))
    if 'nc__status__exact' in list_param:
        if list_param['nc__status__exact'] != '':
            list_not_proper = list_not_proper.filter(nc=list_param['nc__status__exact'])
    if 'rang__rang__exact' in list_param:
        if list_param['rang__rang__exact'] != '':
            list_not_proper = list_not_proper.filter(rang=list_param['rang__rang__exact'])
    if 'valide' in list_param:
        if list_param['valide'] != '':
            if list_param['valide'] == 'valide':
                list_not_proper = list_not_proper.filter(id=F('id_ref'))
            else:
                list_not_proper = list_not_proper.filter(~Q(id=F('id_ref')))
    return list_not_proper


def get_specific_search_sample(list_param):
    """
    Filter from the user's parameter's
    :param list_param: a list of parameter if the user want to export his research
    :return: a list filtered
    """
    list_not_proper = Prelevement.objects.all()
    if list_param is not None:
        if 'q' in list_param:
            if list_param['q'] != '':
                list_not_proper = list_not_proper.filter(
                    Q(id_taxon__lb_nom__icontains=list_param['q'].replace("+", " ")) |
                    Q(toponyme__icontains=list_param['q'].replace("+", " ")))
    return list_not_proper


def get_taxon_child(child, count_es):
    """
    This function will give us all the child of the child of a taxon and returning it into a list
    For that we have to do a recursive function
    :param child: the current taxon from who we want the child
    :param count_es:
    :return: the new list of taxon we want
    """
    lchild = Taxon.objects.filter(id_sup=child.id)
    if lchild:
        list_child = []
        for child2 in lchild:
            list_child_temp, count_es = get_taxon_child(child2, count_es)
            list_child.append([child2, list_child_temp])
        if child.rang.rang == 'ES' or child.rang.rang == 'SSES':
            count_es = count_es + 1
        return list_child, count_es
    else:
        if child.rang.rang == 'ES' or child.rang.rang == 'SSES':
            count_es = count_es + 1
        return None, count_es


def get_search_results_auteur_by_species(search_term):
    """
    The goal of this function is to retun a list of genus related by a author
    :param search_term: the term the user entered
    :return: the list of children
    """
    queryset = Taxon.objects.filter(Q(lb_auteur__icontains=search_term) & Q(rang='ES'))
    list_taxon = []
    count_es = 0
    if len(queryset) > 0:
        for taxon in queryset:
            if taxon.id_ref_id == taxon.id:
                list_child = Taxon.objects.filter(id_sup=taxon.id)
                list_temp_taxon = []
                for child in list_child:
                    list_temp_child, count_es = get_taxon_child(child, count_es)
                    list_temp_taxon.append([child, list_temp_child])
                list_taxon.append([taxon, list_temp_taxon])
        return list_taxon, count_es
    else:
        error = 'Aucun résultat trouvé.'
        return error, 0


def get_child_of_child(taxon):
    """
    The goal of this function is to retun in a list of list all the children of a specific taxon
    :param taxon: the taxon the user choose
    :return: the list of children
    """
    list_taxon = []
    count_es = 0
    list_child = Taxon.objects.filter(id_sup=taxon.id)
    list_temp_taxon = []
    for child in list_child:
        list_temp_child, count_es = get_taxon_child(child, count_es)
        list_temp_taxon.append([child, list_temp_child])
    list_taxon.append(taxon)
    list_taxon.append(list_temp_taxon)
    return list_taxon, count_es


def constr_hierarchy_tree_adv_search(taxon, auteur):
    """
    From a search term, we get the taxonomic rank, then we search for its children. Finally we construct the
    hierarchy tree from these data. Also we return the number of species and of sub-species inherited from the taxon
    entered by the user
    :param taxon: the taxon the user choose
    :param auteur: a string if the user want to search by author or not
    :return: a string
    """
    if taxon is None:
        if auteur == '':
            html_hierarchy = 'Veuillez remplir le champ de recherche !'
            count_es = 0
        else:
            list_taxon, count_es = get_search_results_auteur_by_species(auteur)
            if type(list_taxon) is str:
                return list_taxon, 0
            else:
                count_es = count_es + 1
            html_hierarchy = ''
            for l_taxon in list_taxon:
                html_hierarchy += '<div>'
                list_hierarchy, count = l_taxon[0].get_hierarchy()
                html_hierarchy_begin, html_hierarchy_end = constr_hierarchy_tree_branch_parents(list_hierarchy)
                html_hierarchy_child = ''
                html_hierarchy_child = constr_hierarchy_tree_branch_adv_search_child(l_taxon[1],
                                                                                     count + 1,
                                                                                     html_hierarchy_child)
                html_taxon = f'<li class="folder"><label>{l_taxon[0].rang} :</label> ' \
                             f'{l_taxon[0].lb_nom} {l_taxon[0].lb_auteur}</li>'
                html_hierarchy_end = html_hierarchy_child + '</ul></ul></li>'
                html_hierarchy += html_hierarchy_begin + html_taxon + html_hierarchy_end + '</div>'
    else:
        list_taxon, count_es = get_child_of_child(taxon)
        list_hierarchy, count = taxon.get_hierarchy()
        html_hierarchy_begin, html_hierarchy_end = constr_hierarchy_tree_branch_parents(list_hierarchy)
        html_hierarchy_child = ''
        html_hierarchy_child = constr_hierarchy_tree_branch_adv_search_child(list_taxon[1],
                                                                             count + 1,
                                                                             html_hierarchy_child)
        html_taxon = f'<li class="folder"><label>{taxon.rang} :</label> {taxon.lb_nom} {taxon.lb_auteur}</li>'
        html_hierarchy_end = html_hierarchy_child + '</ul></ul></li>'
        html_hierarchy = html_hierarchy_begin + html_taxon + html_hierarchy_end

    return html_hierarchy, count_es


def constr_hierarchy_tree_branch_parents(list_hierarchy):
    """
    Construct the beginning of the tree
    :param list_hierarchy:
    :return: a string with html tag
    """
    count_parent = 1
    html_hierarchy_begin_start = '<ul class="tree"><br/>'
    html_hierarchy_begin = ''
    html_hierarchy_end = '</ul>'
    if list_hierarchy is not None:
        for parent in reversed(list_hierarchy):
            html_hierarchy_begin = html_hierarchy_begin + \
                                   f'<li><label class="tree_label" for="c{count_parent}">{parent.rang} :</label> ' \
                                   f'''<a href="{reverse('admin:fatercal_taxon_change', args=[parent.id])}">''' \
                                   f'''{parent}</a><ul class="tree">'''
            html_hierarchy_end = '</ul></li>' + html_hierarchy_end
            count_parent = count_parent + 1
    html_hierarchy_begin = html_hierarchy_begin_start + html_hierarchy_begin
    return html_hierarchy_begin, html_hierarchy_end


def constr_hierarchy_tree_branch_adv_search_child(list_taxon, count, hierarchy_child):
    """
    Construct the end of the hierarchy tree
    :param list_taxon: a list which contains different taxon
    :param count: an int
    :param hierarchy_child: a string with html tag
    :return: a string with html tag
    """
    for l_taxon in list_taxon:
        hierarchy_child = hierarchy_child + \
                          f'<ul class="tree"><li><label class="tree_label" for="c{count}">{l_taxon[0].rang} :</label> ' \
                          f'''<a href="{reverse('admin:fatercal_taxon_change', args=[l_taxon[0].id])}'">''' \
                          f'{l_taxon[0]}</a>'
        if l_taxon[1] is not None:
            hierarchy_child = constr_hierarchy_tree_branch_adv_search_child(l_taxon[1], count + 1, hierarchy_child)
        hierarchy_child = hierarchy_child + '</li></ul>'
    return hierarchy_child


def constr_hierarchy_tree_branch_child(list_child, nb):
    """
    Construct the child branch of the hierarchy tree
    :param list_child: the list of child from which we construct the child branch of the tree
    :param nb: an indicator for html use
    :return: a string with html tag
    """
    if len(list_child) > 0:
        rang = list_child[0].rang
        str_child = f'<ul class="tree"><li><label class="tree_label" for="c{str(nb + 1)}">{rang} :</label>' \
                    '<ul class="tree">'
        for child in list_child:
            if rang != child.rang:
                str_child = str_child + \
                            f'''</ul></li><li class="tree_label"><label for="c{str(nb + 1)}">{child.rang} :</label> ''' \
                            f'<li><ul class="tree">' \
                            f'''<a href="{reverse('admin:fatercal_taxon_change', args=[child.id])}">{child}</a>'''
                rang = child.rang
            else:
                str_child = str_child + \
                            f'''<li><a href="{reverse('admin:fatercal_taxon_change', args=[child.id])}">''' \
                            f'''{child.lb_nom} {child.lb_auteur}</a></li>'''
    else:
        str_child = ''
    return str_child


def get_taxons_for_sample(list_param):
    """
    Construct a csv file with research result for importing sample for these taxon
    :return: a list of tuple
    """
    if list_param is None:
        list_not_proper = Taxon.objects.all()
    else:
        list_not_proper = get_specific_search_taxon(list_param)
    list_taxon = [
        ('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece',
         'sous-espece', 'auteur(s)/date', 'date', 'collecteurs', 'identificateur', "date d'identification",
         'altitude(m)', 'pays', 'region', 'commune', 'lieu dit', 'type de milieu', 'nombre', 'sexe', 'capture/relacher',
         'informations complementaires', 'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc')
    ]
    for taxon in list_not_proper.iterator():
        dict_hierarchy = get_hierarchy_to_dict(taxon)
        list_taxon.append((taxon.id, dict_hierarchy.get('Ordre'), dict_hierarchy.get('Famille'),
                           dict_hierarchy.get('Sous-Famille'), dict_hierarchy.get('Genre'),
                           dict_hierarchy.get('Sous-Genre'), dict_hierarchy.get('Espèce'),
                           dict_hierarchy.get('Sous-Espèce'), taxon.lb_auteur))
    return list_taxon


def get_hierarchy_to_dict(taxon):
    """
    Transform the list hierarchy in a usable dict for export
    :param taxon: an object taxon
    :return: a dictionnary
    """
    hierarchy, nb = taxon.get_hierarchy()
    dict_hierarchy = {}
    if hierarchy is not None:
        dict_hierarchy['Ordre'] = \
            next((taxon_p.lb_nom for taxon_p in hierarchy if taxon_p.rang.lb_rang == 'Ordre'), '')
        dict_hierarchy['Famille'] = \
            next((taxon_p.lb_nom for taxon_p in hierarchy if taxon_p.rang.lb_rang == 'Famille'), '')
        dict_hierarchy['Sous-Famille'] = \
            next((taxon_p.lb_nom for taxon_p in hierarchy if taxon_p.rang.lb_rang == 'Sous-Famille'), '')
        dict_hierarchy['Genre'] = \
            next((taxon_p.lb_nom for taxon_p in hierarchy if taxon_p.rang.lb_rang == 'Genre'), '')
        dict_hierarchy['Sous-Genre'] = \
            next((taxon_p.lb_nom for taxon_p in hierarchy if taxon_p.rang.lb_rang == 'Sous-Genre'), '')
        dict_hierarchy['Espèce'] = \
            next((taxon_p.lb_nom for taxon_p in hierarchy if taxon_p.rang.lb_rang == 'Espèce'), '')
        dict_hierarchy['Sous-Espèce'] = \
            next((taxon_p.lb_nom for taxon_p in hierarchy if taxon_p.rang.lb_rang == 'Sous-Espèce'), '')
        dict_hierarchy[taxon.rang.lb_rang] = taxon.lb_nom
    return dict_hierarchy


def verify_sample(line, count):
    """
    This function verify if all the parameter's with condition are good
    :param line: The line in the csv file
    :param count: the line number we check
    :return: a boolean
    """
    result = {
        'good': False,
        'message': 'Une erreur à été perçue à la ligne {}.'.format(count)
    }
    if Taxon.objects.filter(id=line['id_taxon']).count() > 0:
        if TypeEnregistrement.objects.filter(lb_type=line['capture/relacher']).count() > 0:
            if line['x wgs 84'] is not None and line['y wgs 84'] is not None:
                if is_variable_good(line):
                    if line['date'] is None or line['date'] == '':
                        result['good'] = True
                    elif re.match(regex_date, line['date']):
                        result['good'] = True
                    else:
                        result['message'] += " La date entrée n'est pas au bon format."
                else:
                    result['message'] += " L'un des nombres sur cette ligne contient des lettres"
            else:
                result['message'] += " Les coordonnées pour ce prélèvements ne sont pas présentes."
        else:
            result['message'] += " Le type d'enregistrement dans le champ capture/relacher n'existe pas" \
                                 " ou n'est pas renseigné."
    else:
        result['message'] += " L'ID du taxon entrée n'existe pas."
    return result


def is_variable_good(line):
    """
    Here we verify if the variables have digit in it or for GPS is a good format
    :param line: The line in the csv file
    :return: a boolean
    """
    try:
        if line['x wgs 84'] != '' and line['x wgs 84'] is not None:
            float(line['x wgs 84'])
        if line['y wgs 84'] != '' and line['y wgs 84'] is not None:
            float(line['y wgs 84'])
        if "-" in line['altitude(m)']:
            int(line['altitude(m)'][:line['altitude(m)'].find('-')])
            int(line['altitude(m)'][line['altitude(m)'].find('-') + 1:])
        else:
            int(line['altitude(m)'])
        if line['nombre'] != '':
            int(line['nombre'])
        return True
    except ValueError:
        return False


def construct_sample(line, count):
    """
    Construct the sample to import into the database from a line in the csv file
    :param line: The line in the csv file
    :param count: an int which indicate the csv line where at
    :return: a dictionnary
    """
    result = {
        'sample': None,
        'loc': None,
        'list_harvester': []
    }
    variable = get_variable_in_good_format(line)
    result['loc'] = get_loc_from_line(line)
    type_enregistrement = TypeEnregistrement.objects.get(lb_type=line['capture/relacher'])
    if line['type de milieu'] is not None and line['type de milieu'].strip() != '':
        habitat = HabitatDetail.objects.filter(nom=line['type de milieu']).first()
        if habitat is None:
            habitat = HabitatDetail(nom=line['type de milieu'])
    else:
        habitat = None
    result['habitat'] = habitat
    if result['loc'] is None:
        raise NotGoodSample("Une erreur à la ligne {}. ".format(count) + "La localisation n'est pas indiqué dans "
                                                                         "l'un des 4 champs.")
    sample = Prelevement(id_taxon=Taxon.objects.filter(id=line['id_taxon']).first(),
                         nb_individus=variable['nombre'],
                         type_specimen=line['sexe'],
                         type_enregistrement=type_enregistrement, date=line['date'],
                         infos_compl=line['informations complementaires'],
                         toponymie_x=variable['x wgs 84'], toponymie_y=variable['y wgs 84'], gps=True,
                         altitude_min=variable['altitude_min'], altitude_max=variable['altitude_max'])
    result['sample'] = sample
    if line['collecteurs'] != '':
        recolteur = line['collecteurs']
        list_harvester = []
        if recolteur.find(',') == -1:
            list_harvester.append(Recolteur(lb_auteur=recolteur.strip()))
        else:
            while recolteur is not None:
                if recolteur.find(',') == -1:
                    harvester = recolteur
                    recolteur = None
                else:
                    harvester = recolteur[:recolteur.find(',')]
                    recolteur = recolteur[recolteur.find(',') + 1:]
                list_harvester.append(Recolteur(lb_auteur=harvester.strip()))
        result['list_harvester'] = list_harvester
    return result


def get_loc_from_line(line):
    """
    Return a dictionnary of localisation from the line
    :param line: The line in the csv file
    :return: a dictionnary or None
    """
    if (line['lieu dit'] is None or line['lieu dit'] == '') or (line['commune'] is None or line['commune'] == '') or \
            ((line['region'] is None or line['region']) == '') or ((line['pays'] is None or line['pays']) == ''):
        return None
    else:
        pays = Localisation.objects.filter(
            nom=line['pays']
        ).first()
        if pays is None:
            pays = Localisation(nom=line['pays'], latitude=line['x wgs 84'], longitude=line['y wgs 84'],
                                loc_type=TypeLoc.objects.get(type='Pays'))
        region = Localisation.objects.filter(
            nom=line['region']
        ).first()
        if region is None:
            region = Localisation(nom=line['region'], latitude=line['x wgs 84'], longitude=line['y wgs 84'],
                                  loc_type=TypeLoc.objects.get(type='Region'))
        else:
            pays = None
        secteur = Localisation.objects.filter(
            nom=line['commune']
        ).first()
        if secteur is None:
            secteur = Localisation(nom=line['commune'], latitude=line['x wgs 84'], longitude=line['y wgs 84'],
                                   loc_type=TypeLoc.objects.get(type='Secteur'))
        else:
            region = None
            pays = None
        nom = Localisation.objects.filter(
            nom=line['lieu dit']
        ).first()
        if nom is None:
            nom = Localisation(nom=line['lieu dit'], latitude=line['x wgs 84'], longitude=line['y wgs 84'],
                               loc_type=TypeLoc.objects.get(type='nom'))
        else:
            secteur = None
            region = None
            pays = None
    return {
        "pays": pays,
        "region": region,
        "secteur": secteur,
        "nom": nom
    }


def get_variable_in_good_format(line):
    """
    Transform the variable in a usable state
    :param line: The line in the csv file
    :return: a dictionnary
    """
    if line['x wgs 84'] == '' or line['x wgs 84'] is None:
        latitude = None
    else:
        latitude = float(line['x wgs 84'])
    if line['y wgs 84'] == '' or line['y wgs 84'] is None:
        longitude = None
    else:
        longitude = float(line['y wgs 84'])
    if "-" in line['altitude(m)']:
        altitude_min = line['altitude(m)'][:line['altitude(m)'].find('-')]
        altitude_max = line['altitude(m)'][line['altitude(m)'].find('-')+1:]
    else:
        altitude_min = int(line['altitude(m)'])
        altitude_max = None
    if line['nombre'] == '' or line['nombre'] is None:
        nb_taxon = None
    else:
        nb_taxon = int(line['nombre'])
    return {
        'x wgs 84': latitude,
        'y wgs 84': longitude,
        'altitude_min': altitude_min,
        'altitude_max': altitude_max,
        'nombre': nb_taxon,
    }


def save_all_sample(list_dict_sample):
    """
    This function simply save all the object from the csv file
    :param list_dict_sample: a dictionnary which contains all the object to save
    :return: void
    """
    for sample in list_dict_sample:
        if sample['loc']['pays'] is not None:
            sample['loc']['pays'].save()
            sample['loc']['region'].id_sup = sample['loc']['pays']
            sample['loc']['region'].save()
            sample['loc']['secteur'].id_sup = sample['loc']['region']
            sample['loc']['secteur'].save()
            sample['loc']['nom'].id_sup = sample['loc']['secteur']
            sample['loc']['nom'].save()
        elif sample['loc']['region'] is not None:
            sample['loc']['region'].save()
            sample['loc']['secteur'].id_sup = sample['loc']['region']
            sample['loc']['secteur'].save()
            sample['loc']['nom'].id_sup = sample['loc']['secteur']
            sample['loc']['nom'].save()
        elif sample['loc']['secteur'] is not None:
            sample['loc']['secteur'].save()
            sample['loc']['nom'].id_sup = sample['loc']['secteur']
            sample['loc']['nom'].save()
        else:
            sample['loc']['nom'].save()
        sample['sample'].localisation = sample['loc']['nom']
        if sample['habitat'] is not None:
            sample['sample'].habitat = sample['habitat']
        sample['sample'].save()
        for harvest in sample['list_harvester']:
            harvest.prelevement = sample['sample']
            harvest.save()


def get_taxon_adv_search(taxon_id, auteur):
    """
    This function will get the child taxon of a taxon or an taxon's author choose by the user
    :param taxon_id: a taxon's ID
    :param auteur: a string
    :return: a list of tuple
    """
    list_taxon = [
        ('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece',
         'sous-espece', 'auteur(s)/date', 'date', 'collecteurs', 'identificateur', "date d'identification",
         'altitude(m)', 'pays', 'region', 'commune', 'lieu dit', 'type de milieu', 'nombre', 'sexe',
         'capture/relacher', 'informations complementaires', 'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc')
    ]
    if taxon_id is not None:
        taxon = Taxon.objects.get(id=id_taxon)
        list_child_taxon, count_es = get_child_of_child(taxon)
        dict_hierarchy = get_hierarchy_to_dict(taxon)
        list_taxon.append((taxon.id, dict_hierarchy.get('Ordre'), dict_hierarchy.get('Famille'),
                           dict_hierarchy.get('Sous-Famille'), dict_hierarchy.get('Genre'),
                           dict_hierarchy.get('Sous-Genre'), dict_hierarchy.get('Espèce'),
                           dict_hierarchy.get('Sous-Espèce'), taxon.lb_auteur))
        list_taxon = format_adv_search_child_for_export_sample(list_child_taxon[1], list_taxon)
    elif auteur is not None:
        list_child_taxon, count_es = get_search_results_auteur_by_species(auteur)
        if type(list_child_taxon) is str:
            return list_taxon
        for l_taxon in list_child_taxon:
            dict_hierarchy = get_hierarchy_to_dict(l_taxon[0])
            list_taxon.append((l_taxon[0].id, None, dict_hierarchy.get('Ordre'), dict_hierarchy.get('Famille'),
                               dict_hierarchy.get('Sous-Famille'), dict_hierarchy.get('Genre'),
                               dict_hierarchy.get('Sous-Genre'), dict_hierarchy.get('Espèce'),
                               dict_hierarchy.get('Sous-Espèce'), l_taxon[0].lb_auteur))
            list_taxon = format_adv_search_child_for_export_sample(l_taxon[1], list_taxon)
    return list_taxon


def format_adv_search_child_for_export_sample(list_child_taxon, list_taxon):
    """
    Get the child taxon in a good format for the csv file in a recursive way
    :param list_child_taxon: a list of taxon
    :param list_taxon: a list of tuple
    :return: a list of tuple
    """
    for l_taxon in list_child_taxon:
        dict_hierarchy = get_hierarchy_to_dict(l_taxon[0])
        list_taxon.append((l_taxon[0].id, None, dict_hierarchy.get('Ordre'), dict_hierarchy.get('Famille'),
                           dict_hierarchy.get('Sous-Famille'), dict_hierarchy.get('Genre'),
                           dict_hierarchy.get('Sous-Genre'), dict_hierarchy.get('Espèce'),
                           dict_hierarchy.get('Sous-Espèce'), l_taxon[0].lb_auteur))
        if l_taxon[1] is not None:
            list_taxon = format_adv_search_child_for_export_sample(l_taxon[1], list_taxon)
    return list_taxon


def verify_and_save_sample(csv_file, extension):
    """
    This function verify all sample contain in the file return a message if the sample have been saved or not
    :param csv_file: a DictReader object which read the file
    :param extension: a string which indicate the extension of the file we inspect
    :return: a string
    """
    try:
        valid_extensions = ['.csv', '.txt']
        list_error_message = []
        message = ''
        if extension in valid_extensions:
            list_dict_sample = []
            count = 1
            for row in csv_file:
                result = verify_sample(row, count)
                if result['good']:
                    result = construct_sample(row, count)
                    list_dict_sample.append(result)
                else:
                    list_error_message.append(result['message'])
                count += 1
            if len(list_error_message) == 0:
                save_all_sample(list_dict_sample)
                message = 'Tous les prélèvements ont tous été importé.'
            else:
                message = 'Les prélèvements du fichiers n\'ont pas été intégré. <br>'
                for message_error in list_error_message:
                    message = message + message_error + '<br>'
        else:
            raise ValidationError(u'Unsupported file extension.')
    except ValidationError:
        message = "Le fichier n'est pas dans le bon format."
    except KeyError:
        message = "Le fichier n'a pas les bons noms de colonne ou une colonne est manquante."
    return message


def list_sample_for_map(taxon):
    """
    Get info on sample when it is located (longitude and latitude is given)
    :param taxon: a taxon object from the model Taxon
    :return: a list of dict
    """
    list_sample = []
    queryset = Prelevement.objects.filter(id_taxon=taxon.id)
    if taxon.id == taxon.id_ref_id:
        queryset_taxon_synonymous = Taxon.objects.filter(id_ref=taxon.id).filter(~Q(id=taxon.id))
        for taxon in queryset_taxon_synonymous:
            queryset_sample_of_synonymous = Prelevement.objects.filter(id_taxon=taxon.id)
            queryset = queryset | queryset_sample_of_synonymous
    for sample in queryset:
        if sample.toponymie_x is not None and sample.toponymie_y is not None:
            default_loc = False
            if sample.type_enregistrement is None:
                t_enre = None
            else:
                t_enre = sample.type_enregistrement.lb_type
            if sample.localisation is None:
                loc = None
            else:
                loc = sample.localisation.nom
                if sample.toponymie_x == sample.localisation.latitude and sample.localisation.longitude == sample.toponymie_y:
                    default_loc = True
            list_sample.append({
                'id': sample.id,
                'loc': loc,
                'default_loc': default_loc,
                'latitude': sample.toponymie_y,
                'longitude': sample.toponymie_x,
                't_enre': t_enre,
                'date': sample.date,
                'collection_museum': sample.collection_museum,
            })
    return list_sample

def get_taxref_update():
    """Get the update from the table taxref_update
    Returns:
        [Boolean, Integer, Integer] -- Return a boolean, the last taxref version
        and the number of taxon to update
    """
    # Here we get the latest version of taxref
    taxref_version = TaxrefUpdate.objects.aggregate(Max('taxref_version'))
    if not TaxrefUpdate.objects.filter(Q(taxref_version=taxref_version['taxref_version__max'])
        & ~Q(id_taxon=None)).exists():
        empty = True
        count = 0
    else:
        empty = False
        list_taxon_to_update = TaxrefUpdate.objects.filter(
            Q(taxref_version=taxref_version['taxref_version__max']) &
            ~Q(id_taxon=None))
        count = len(list_taxon_to_update)
        # For every taxon we check all possible update
        for taxref_taxon in list_taxon_to_update.iterator():
            diff = ""
            fatercal_taxon = Taxon.objects.get(id=taxref_taxon.id_taxon)
            is_taxon_sup = Taxon.objects.filter(Q(cd_nom=taxref_taxon.cd_sup) & ~Q(cd_nom=None)).exists()
            is_taxon_ref = Taxon.objects.filter(Q(cd_nom=taxref_taxon.cd_ref) & ~Q(cd_nom=None)).exists()
            rang = TaxrefRang.objects.filter(rang=taxref_taxon.rang).exists()
            habitat = TaxrefHabitat.objects.filter(habitat=taxref_taxon.habitat).exists()
            nc = TaxrefStatus.objects.filter(status=taxref_taxon.nc).exists()

            # We verify the validity of the taxon
            if fatercal_taxon.valide():
                if fatercal_taxon.id_sup is None:
                    if is_taxon_sup:
                        taxon_sup = Taxon.objects.get(cd_nom=taxref_taxon.cd_sup)
                        diff = diff + "Ce taxon n'a pas de supérieur dans fatercal et Taxref lui en a assigné un " \
                        "Supérieur chez Taxref: {}".format(taxon_sup)
                    else:
                        diff = diff + "Ce taxon n'a pas de supérieur dans fatercal et Taxref lui en a assigné un" \
                        " mais il n'exist pas chez fatercal. Cd_nom supérieur chez Taxref: {}".format(taxref_taxon.cd_sup)
                elif taxref_taxon.cd_nom != taxref_taxon.cd_ref:
                    if is_taxon_ref:
                        taxon_ref = Taxon.objects.get(cd_nom=taxref_taxon.cd_ref)
                        diff = diff + "Le taxon est valide chez fatercal mais synonyme chez Taxref. " \
                            "Taxon référent chez Taxref: {}".format(taxon_ref)
                    else:
                        diff = diff + "Le taxon est valide chez fatercal mais synonyme chez Taxref" \
                            "et n'éxiste pas chez Fatercal. Cd_nom taxon référent chez Taxref: {}.".format(taxref_taxon.cd_ref)
                elif fatercal_taxon.id_sup.cd_nom is not None:
                    if fatercal_taxon.id_sup.cd_nom != taxref_taxon.cd_sup:
                        if is_taxon_sup:
                            taxon_sup = Taxon.objects.get(cd_nom=taxref_taxon.cd_sup)
                            diff = diff + "Le supérieur de ce taxon est différent. "\
                                "Supérieur chez fatercal: {}, chez Taxref {}. ".format(
                                    fatercal_taxon.id_sup, taxon_sup)
                        else:
                            diff = diff + "Le supérieur de ce taxon est différent "\
                            "et n'existe pas dans Fatercal. CD_NOM = {}. ".format(taxref_taxon.cd_sup)
                else:
                    diff = diff + "Le supérieur de ce taxon est différent et celui de Fatercal " \
                        "n'existe pas chez Taxref. "
            else:
                if taxref_taxon.cd_nom == taxref_taxon.cd_ref:
                    if is_taxon_sup:
                        taxon_sup = Taxon.objects.get(cd_nom=taxref_taxon.cd_sup)
                        diff = diff + "Le taxon est synonyme chez fatercal mais valide chez Taxref. " \
                            "Supérieur chez Taxref: {}. ".format(taxon_sup)
                    else:
                        diff = diff + "Le taxon est synonyme chez fatercal mais valide chez Taxref " \
                            "mais le taxon supérieur n'existe pas chez Fatercal " \
                            "Cd_nom taxon supérieur chez Taxref: {}. ".format(taxref_taxon.cd_sup)
                elif fatercal_taxon.id_ref.cd_nom is not None:
                    if fatercal_taxon.id_ref.cd_nom != taxref_taxon.cd_ref:
                        if is_taxon_ref:
                            taxon_ref = Taxon.objects.get(cd_nom=taxref_taxon.cd_ref)
                            diff = diff + "Le référent de ce taxon est différent. " \
                                "Référent chez fatercal: {}, chez Taxref {}. ".format(
                                    fatercal_taxon.id_ref, taxon_ref)
                        else:
                            diff = diff + "Le référent de ce taxon est différent "\
                            "et n'existe pas dans Fatercal. CD_NOM = {}. ".format(taxref_taxon.cd_ref)
                else:
                    diff = diff + "Le référent de ce taxon est différent et celui de Fatercal " \
                        "n'existe pas chez Taxref. "
        
            # We verify the rank
            if taxref_taxon.rang != fatercal_taxon.rang.rang:
                if rang:
                    rang = TaxrefRang.objects.get(rang=taxref_taxon.rang)
                    diff = diff + "Le rang est différent. Nouveau rang: {}. ".format(rang)
                else:
                    diff = diff + "Le rang est différent et n'existe pas chez Fatercal. " \
                        "Nouveau rang: {}. ".format(taxref_taxon.rang)
            
            # We verify the lb_nom
            if taxref_taxon.lb_nom != fatercal_taxon.lb_nom:
                diff = diff + "Le nom du taxon est différent. Nom Chez Fatercal: {}, " \
                    "Chez taxref: {}. ".format(fatercal_taxon.lb_nom, taxref_taxon.lb_nom)
            
            # We verify the lb_auteur
            if taxref_taxon.lb_auteur != fatercal_taxon.lb_auteur:
                diff = diff + "Le nom de l'auteur de ce taxon est différent. Auteur " \
                    "Chez Fatercal: {}, Chez taxref: {}. ".format(
                        fatercal_taxon.lb_auteur, taxref_taxon.lb_auteur)
            
            # We verify the habitat
            if taxref_taxon.habitat is not None:
                if fatercal_taxon.habitat is not None:
                    if taxref_taxon.habitat != fatercal_taxon.habitat.habitat:
                        if habitat:
                            habitat = TaxrefHabitat.objects.get(habitat=taxref_taxon.habitat)
                            diff = diff + "L'habitat est différent. Nouvelle Habitat: {}. ".format(habitat.lb_habitat)
                        else:
                            diff = diff + "L'habitat est différent et n'existe pas chez Fatercal. " \
                                "Nouvelle Habitat: {}. ".format(taxref_taxon.habitat)
                else:
                    if habitat:
                        habitat = TaxrefHabitat.objects.get(habitat=taxref_taxon.habitat)
                        diff = diff + "Un habitat a été spécifié pour ce taxon. Nouvelle Habitat: {}. ".format(habitat.lb_habitat)
                    else:
                        diff = diff + "Un habitat a été spécifié pour ce taxon mais il n'existe pas chez fatercal. " \
                            "Nouvelle habitat: {}. ".format(taxref_taxon.habitat)
            
            # We verify the status
            if taxref_taxon.nc is not None:
                if fatercal_taxon.nc is not None:
                    if taxref_taxon.nc != fatercal_taxon.nc.status:
                        if nc:
                            nc = TaxrefStatus.objects.get(status=taxref_taxon.nc)
                            diff = diff + "Le status est différent. Nouveau Status: {}".format(nc.lb_status)
                        else:
                            diff = diff + "Le status est différent et n'existe pas chez Fatercal. " \
                                "Nouveau Status: {}".format(taxref_taxon.nc)
                else:
                    if nc:
                        nc = TaxrefStatus.objects.get(status=taxref_taxon.nc)
                        diff = diff + "Un status a été spécifié pour ce taxon. Nouveau Status: {}. ".format(nc.lb_status)
                    else:
                        diff = diff + "Un status a été spécifié pour ce taxon mais il n'existe pas chez fatercal. " \
                            "Nouveau Status: {}. ".format(taxref_taxon.nc)
            # All info in a dict if there's a diff
            if taxref_taxon.lb_auteur is None:
                nom_complet = taxref_taxon.lb_nom
            else:
                nom_complet = taxref_taxon.lb_nom + " " + taxref_taxon.lb_auteur
            if diff != "":
                taxref_taxon.nom_complet = nom_complet + ": " + diff
            else:
                taxref_taxon.nom_complet = nom_complet + ": Aucune différence " \
                    "mais des identifiant venant de Taxref était manquant."
            taxref_taxon.save()
    return empty, taxref_version, count

def update_taxon_from_taxref(data, taxref_version, user):
    """Update taxon based on ther user's choice
    
    Arguments:
        data {dict} -- Dict Containing time and taxon to update
        taxref_version {integer} -- the actual version of version from which we get the data
        user {user} -- Type User (See Django Doc)
    """
    if data['choices']:
        for taxon in data['choices']:
            fatercal_taxon = taxon.id_taxon
            # Check if the lb_nom is different
            if fatercal_taxon.lb_nom != taxon.lb_nom:
                fatercal_taxon.lb_nom = taxon.lb_nom
            # Check if the lb_auteur is different
            if fatercal_taxon.lb_auteur != taxon.lb_auteur:
                fatercal_taxon.lb_auteur = taxon.lb_auteur
            # Check if the rank is different
            if fatercal_taxon.rang.rang != taxon.rang:
                if TaxrefRang.objects.filter(rang=taxon.rang).exists():
                    fatercal_taxon.rang = TaxrefRang.objects.get(rang=taxon.rang)
            # Check if the habitat is different
            if fatercal_taxon.habitat is not None:
                if fatercal_taxon.habitat.habitat != taxon.habitat and taxon.habitat is not None:
                    if TaxrefHabitat.objects.filter(habitat=taxon.habitat).exists():
                        fatercal_taxon.habitat = TaxrefHabitat.objects.get(habitat=taxon.habitat)
            else:
                if taxon.habitat is not None:
                    if TaxrefHabitat.objects.filter(habitat=taxon.habitat).exists():
                        fatercal_taxon.habitat = TaxrefHabitat.objects.get(habitat=taxon.habitat)
            # Check if the status is different
            if fatercal_taxon.nc is not None:
                if fatercal_taxon.nc.status != taxon.nc:
                    if TaxrefStatus.objects.filter(status=taxon.nc).exists():
                        fatercal_taxon.nc = TaxrefStatus.objects.get(status=taxon.nc)
            else:
                if taxon.nc is not None:
                    if TaxrefStatus.objects.filter(status=taxon.nc).exists():
                        fatercal_taxon.nc = TaxrefStatus.objects.get(status=taxon.nc)
            # Check if the superior or referent is different
            if taxon.cd_ref is not None:
                if fatercal_taxon.cd_ref != taxon.cd_ref:
                    fatercal_taxon.cd_ref = taxon.cd_ref
                    if Taxon.objects.filter(Q(cd_nom=taxon.cd_ref) & ~Q(cd_nom=None)).exists():
                        taxon_ref = Taxon.objects.get(cd_nom=taxon.cd_ref)
                        fatercal_taxon.id_ref = taxon_ref
                        # If a valid taxon become a synonymous
                        if taxon.cd_ref != taxon.cd_nom and Taxon.objects.filter(id_ref=fatercal_taxon.id).exists():
                            taxon_ref_and_sup = Taxon.objects.get(cd_nom=taxon.cd_ref)
                            for taxon_syn in Taxon.objects.filter(id_ref=fatercal_taxon.id):
                                taxon_syn.id_ref = taxon_ref_and_sup
                                taxon_syn.save()
                            for taxon_child in Taxon.objects.filter(id_sup=fatercal_taxon.id):
                                taxon_child.id_sup = taxon_ref_and_sup
                                taxon_child.save()
            if taxon.cd_sup is not None:
                if fatercal_taxon.cd_sup != taxon.cd_sup:
                    fatercal_taxon.cd_sup = taxon.cd_sup
                    if Taxon.objects.filter(Q(cd_nom=taxon.cd_sup) & ~Q(cd_nom=None)).exists():
                        taxon_sup = Taxon.objects.get(cd_nom=taxon.cd_sup)
                        fatercal_taxon.id_sup = taxon_sup
            fatercal_taxon.taxref_version = taxref_version['taxref_version__max']
            fatercal_taxon.source = "Taxref"
            fatercal_taxon.utilisateur = user.__str__()
            fatercal_taxon.last_update = data['time']
            fatercal_taxon.save()
            taxon.delete()
    # We delete all TaxrefUpdate object and set the last version 
    # on taxon not updated with Taxref Data 
    list_taxon = TaxrefUpdate.objects.filter(
            Q(taxref_version=taxref_version['taxref_version__max'])
            & ~Q(id_taxon=None)
        )
    for taxon in list_taxon.iterator():
        fatercal_taxon = taxon.id_taxon
        fatercal_taxon.taxref_version = taxref_version['taxref_version__max']
        fatercal_taxon.source = "Fatercal"
        fatercal_taxon.utilisateur = user.__str__()
        fatercal_taxon.last_update = data['time']
        fatercal_taxon.save()
    list_taxon.delete()

def get_taxref_insert(rang):
    """ Get the new taxon from the table taxref_update
    
    Arguments:
        rang {string} -- A string which contains the rank to validate
    
    Returns:
        [List, List, Integer] -- Return two list of dict and the lastest version of taxref 
    """
    nb_taxon = 0
    taxref_version = TaxrefUpdate.objects.aggregate(Max('taxref_version'))
    exist = TaxrefUpdate.objects.filter(
        Q(taxref_version=taxref_version['taxref_version__max']) &
        Q(id_taxon=None)).exists()
    if exist:
        exist_rang = TaxrefUpdate.objects.filter(
            Q(taxref_version=taxref_version['taxref_version__max']) &
            Q(id_taxon=None) & Q(rang=rang)).exists()
        if exist_rang or rang == 'other':
            if rang == 'other':
                list_taxon_to_insert = TaxrefUpdate.objects.filter(
                    Q(taxref_version=taxref_version['taxref_version__max']) &
                    Q(id_taxon=None) & ~Q(rang__in=list_hierarchy))
            else:
                list_taxon_to_insert = TaxrefUpdate.objects.filter(
                    Q(taxref_version=taxref_version['taxref_version__max']) &
                    Q(id_taxon=None) & Q(rang=rang))
            nb_taxon = list_taxon_to_insert.count()
            for taxon in list_taxon_to_insert.iterator():
                is_taxon_sup = Taxon.objects.filter(cd_nom=taxon.cd_sup).exists()
                is_taxon_ref = Taxon.objects.filter(cd_nom=taxon.cd_ref).exists()
                rang = TaxrefRang.objects.filter(rang=taxon.rang).exists()
                habitat = TaxrefHabitat.objects.filter(habitat=taxon.habitat).exists()
                nc = TaxrefStatus.objects.filter(status=taxon.nc).exists()
                taxon_existent = ""
                if not is_taxon_sup and taxon.cd_sup is not None and taxon.cd_nom == taxon.cd_ref:
                    taxon_existent = taxon_existent + " Le supérieur n'existe pas chez Fatercal. "\
                        "Cd_nom Taxon supérieur: {}.".format(taxon.cd_sup)
                if not is_taxon_ref and taxon.cd_ref is not None and taxon.cd_nom != taxon.cd_ref:
                    taxon_existent = taxon_existent + " Le référent n'existe pas chez Fatercal. "\
                        "Cd_nom Taxon référent: {}.".format(taxon.cd_ref)
                if not rang and taxon.rang is not None:
                    taxon_existent = taxon_existent + " Le rang n'existe pas chez Fatercal "\
                        "Référence rang: {}.".format(taxon.rang)
                if not habitat and taxon.habitat is not None:
                    taxon_existent = taxon_existent + " L'habitat n'existe pas chez Fatercal. "\
                        "Référence habitat: {}.".format(taxon.habitat)
                if not nc and taxon.nc is not None:
                    taxon_existent = taxon_existent + " Le statut n'existe pas chez Fatercal "\
                    "Référence statut: {}.".format(taxon.nc)
                # All info in a dict if the have an attribute that doesn't exist in fatercal
                if taxon.lb_auteur is None:
                    nom_complet = taxon.lb_nom
                else:
                    nom_complet = taxon.lb_nom + " " + taxon.lb_auteur
                if taxon_existent != "":
                    taxon.nom_complet = nom_complet + ": " + taxon_existent
                else:
                    taxon.nom_complet = nom_complet
                taxon.save()
    else:
        exist_rang = False
    return exist, exist_rang, nb_taxon, taxref_version

def insert_taxon_from_taxref(data, taxref_version, user):
    """Insert taxon based on ther user's choice
    
    Arguments:
        data {dict} -- Dict Containing time and taxon to insert
        taxref_version {integer} -- the actual version of version from which we get the data
        user {user} -- Type User (See Django Doc)
    
    Returns:
        [List or None] -- Return a list of taxon not insert or None
    """
    list_not_insert = []
    if data['choices']:
        for taxon in data['choices']:
            if TaxrefRang.objects.filter(rang=taxon.rang).exists() and taxon.rang is not None:
                rang = TaxrefRang.objects.get(rang=taxon.rang)
                if Taxon.objects.filter(cd_nom=taxon.cd_sup).exists() and taxon.cd_sup is not None:
                    id_sup = Taxon.objects.get(cd_nom=taxon.cd_sup)
                else:
                    id_sup = None
                if TaxrefHabitat.objects.filter(habitat=taxon.habitat).exists() and taxon.habitat is not None:
                    habitat = TaxrefHabitat.objects.get(habitat=taxon.habitat)
                else:
                    habitat = None
                if TaxrefStatus.objects.filter(status=taxon.nc).exists() and taxon.nc is not None:
                    nc = TaxrefStatus.objects.get(status=taxon.nc)
                else:
                    nc = None
                if taxon.lb_auteur is None:
                    lb_auteur = None
                    nom_complet = taxon.lb_nom
                else:
                    lb_auteur = taxon.lb_auteur
                    nom_complet = taxon.lb_nom + lb_auteur
                if Taxon.objects.filter(cd_nom=taxon.cd_ref).exists() and taxon.cd_ref is not None:
                    id_ref = Taxon.objects.get(cd_nom=taxon.cd_ref)
                else:
                    id_ref = None
                fatercal_taxon = Taxon(lb_nom=taxon.lb_nom, lb_auteur=lb_auteur,
                    nom_complet=nom_complet, id_ref=id_ref, id_sup=id_sup,
                    cd_nom=taxon.cd_nom, cd_ref=taxon.cd_ref, cd_sup=taxon.cd_sup,
                    rang=rang, habitat=habitat, nc=nc)
                fatercal_taxon.taxref_version = taxref_version['taxref_version__max']
                fatercal_taxon.source = "Taxref"
                fatercal_taxon.utilisateur = user.__str__()
                fatercal_taxon.last_update = data['time']
                fatercal_taxon.save()
                fatercal_taxon.id_ref = fatercal_taxon
                fatercal_taxon.save()
            else:
                list_not_insert.append(
                    {'name': taxon.lb_nom + ":", 'info': "Rang taxon: {}".format(taxon.rang)})
            taxon.delete()
    list_taxon = TaxrefUpdate.objects.filter(rang=list_hierarchy[data['count']])
    list_taxon.delete()
    return list_not_insert

def delete_not_choose_taxref_insert():
    """[summary]
    """
    taxref_version = get_last_taxref_version()
    # We delete all TaxrefUpdate object new taxon not selected by user
    list_taxon = TaxrefUpdate.objects.filter(
            Q(taxref_version=taxref_version['taxref_version__max'])
            & Q(id_taxon=None)
        )
    list_taxon.delete()

def get_last_taxref_version():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    taxref_version = TaxrefUpdate.objects.aggregate(Max('taxref_version'))
    return taxref_version

def next_taxref_insert_page(form, error):
    """[summary]
    
    Arguments:
        form {[type]} -- [description]
        error {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    if error:
        template = loader.get_template('fatercal/taxon/update_taxon.html')
        context = {
                'error': error,
                'goal': 'insert'
        }
    else:
        data = form.cleaned_data
        if data['count'] > -1:
            if data['count'] + 1 < len(list_hierarchy):
                rang = list_hierarchy[data['count'] + 1]
                exist, exist_rang, nb_taxon, taxref_version = get_taxref_insert(rang)
                rang = TaxrefRang.objects.get(rang=rang).lb_rang
                initial = {
                    'taxref_version': int(taxref_version['taxref_version__max']),
                    'time': data['time'],
                    'count':  data['count'] + 1,
                    'rang': list_hierarchy[data['count'] + 1]
                }
            else:
                rang = 'other'
                exist, exist_rang, nb_taxon, taxref_version = get_taxref_insert(rang)
                data['count'] = -2
                initial = {
                    'taxref_version': int(taxref_version['taxref_version__max']),
                    'time': data['time'],
                    'count':  data['count'],
                    'rang': rang
                }
            form = ChooseTaxonToInsert(initial = initial)
            context = {'form': form, 'exist': exist,'exist_rang': exist_rang,
                'rang': rang, 'nb_taxon': nb_taxon}
            template = loader.get_template('fatercal/taxon/choose_taxon_insert.html')
        else:
            template = loader.get_template('fatercal/taxon/update_taxon.html')
            context = {'error': error, 'goal': 'insert'}
    return template, context

def is_admin(user):
    """
    Verify if the user is in the group Admin
    :param user: An user object (See Django Doc)
    :return: a boolean
    """
    for group in user.groups.all():
        if group.name == "Admin":
            return True
    return False


def create_db_view_test():
    """For testing purpose
    """
    with connection.cursor() as cursor:
        cursor.execute(open(os.getcwd() + "/sql_script/create_type_taxref_data.sql", "r").read())
        cursor.execute(open(os.getcwd() + "/sql_script/function_get_taxon_to_taxref.sql", "r").read())
        cursor.execute(open(os.getcwd() + "/sql_script/function_get_all_taxon_to_taxref.sql", "r").read())
        cursor.execute(open(os.getcwd() + "/sql_script/create_materialized_view_taxref_export.sql", "r").read())


class NotGoodSample(Exception):
    def __init__(self, message):
        self.message = message
