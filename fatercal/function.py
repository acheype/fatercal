from django.http import HttpResponse
from django.template import loader
from django.db.models import F, Q
import re

""" Variable for the application"""
regex_date = r"(^\d{4}$)|" \
        r"(^\d{4}-(0[1-9]|1[0-2])$)|" \
        r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)|" \
        r"(^$)|" \
        r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])\/\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)"
params_search_taxon = ['q', 'nc__status__exact', 'rang__rang__exact', 'valide']
params_search_sample = ['q', 'toponyme']


def get_recolteur(recolteur, prelev):
    """
    Get the Harvesteur's for a specific sample
    :param recolteur:
    :param prelev: the object
    :return: a string
    """
    list_recolt = recolteur.objects.filter(id_prelevement=prelev.id_prelevement)
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


def get_msg(tup):
    """
    This function aim to get a message for taxref if it's != or not
    :param tup: the object from the Taxon model
    :return a tupple:
    """
    if tup.cd_nom is None:
        return 'x', None, None, None
    elif (tup.id_ref != tup and tup.cd_ref == tup.id_ref.cd_nom) or \
            (tup.id_ref == tup and tup.cd_ref != tup.id_ref.cd_nom):
        return None, None, None, 'x'
    elif tup.cd_ref != tup.id_ref.cd_nom:
        return None, 'x', None, None
    elif tup.cd_sup is not None:
        if tup.cd_sup != tup.id_sup.cd_nom:
            return None, None, 'x', None
    return None, None, None, None


def get_taxon(taxons, param):
    """
    This function get all Information needed from all taxon
    :param taxons: The model which is connected to the table Taxon in the database
    :param param: the parameter's if the user want to export his research
    :return: a list of tuple
    """
    if param is None:
        list_not_proper = taxons.objects.all()
    else:
        list_param = inspect_url_variable(param, params_search_taxon)
        list_not_proper = get_specific_search_taxon(taxons, list_param)
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
                  dict_parent.get('CL'), dict_parent.get('FM'), None, None, taxon.id, taxon.id_ref_id, id_sup,
                  taxon.cd_nom, None, taxon.cd_sup, taxon.cd_ref, taxon.rang.rang, taxon.lb_nom, taxon.lb_auteur,
                  taxon.nom_complet, None, taxon.lb_nom, None, None, habitat, statut) + msg
    else:
        dict_parent = get_superior(taxon.id_ref)
        tupple = (dict_parent.get('KD'), dict_parent.get('PH'), dict_parent.get('CL'), dict_parent.get('OR'),
                  dict_parent.get('CL'), dict_parent.get('FM'), None, None, taxon.id, taxon.id_ref_id, None,
                  taxon.cd_nom, None, taxon.cd_sup, taxon.cd_ref, taxon.rang.rang, taxon.lb_nom, taxon.lb_auteur,
                  taxon.nom_complet, None, taxon.id_ref.lb_nom, None, None, habitat, statut) + msg
    return tupple


def get_taxon_personal(taxons, form):
    """
    Get the list of taxon the user get from its search
    :param taxons: The model which is connected to the table Taxon in the database
    :param form: an form object (See Django doc)
    :return: a list
    """
    list_not_proper = get_specific_search_taxon(taxons, form.cleaned_data)
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
    if tuple == ():
        return list_taxon
    else:
        for taxon in list_not_proper.iterator():
            cleaned_taxon = construct_cleaned_taxon_search(taxon, cleaned_data)
            list_taxon.append(cleaned_taxon)
    return list_taxon


def construct_cleaned_taxon_search(taxon, cleaned_data):
    """
    Construct a tuple with field requested by the user
    :param taxon: The model which is connected to the table Taxon in the database
    :param cleaned_data: a dict from the form object (see Django doc)
    :return: a tuple
    """
    cleaned_taxon = ()
    if cleaned_data['id']: cleaned_taxon += (taxon.id,)
    if taxon.id == taxon.id_ref_id:
        if taxon.id_sup is None: cleaned_taxon += (None,)
        else:
            if cleaned_data['id_sup']: cleaned_taxon += (taxon.id_sup_id,)
    else: cleaned_taxon += (None,)
    if cleaned_data['id_ref']: cleaned_taxon += (taxon.id_ref_id,)
    if cleaned_data['name']: cleaned_taxon += (taxon.lb_nom,)
    if cleaned_data['author']: cleaned_taxon += (taxon.lb_auteur,)
    if cleaned_data['rank']: cleaned_taxon += (taxon.rang.lb_rang,)
    if taxon.id == taxon.id_ref_id:
        if cleaned_data['rank_sup']: cleaned_taxon += (taxon.id_sup,)
    else: cleaned_taxon += (None,)
    if taxon.nc is None:
        cleaned_taxon += (None,)
    else:
        if cleaned_data['status']: cleaned_taxon += (taxon.nc.lb_status,)
    if taxon.habitat is None: cleaned_taxon += (None,)
    else:
        if cleaned_data['habitat']: cleaned_taxon += (taxon.habitat.lb_habitat,)
    if cleaned_data['grande_terre']: cleaned_taxon += (taxon.grande_terre,)
    if cleaned_data['loyalty_island']: cleaned_taxon += (taxon.iles_loyautee,)
    if cleaned_data['other']: cleaned_taxon += (taxon.autre,)
    if taxon.remarque is None: cleaned_taxon += (None,)
    else:
        if cleaned_data['remark']: cleaned_taxon += (taxon.remarque.replace('\n', ''),)
    if taxon.sources is None: cleaned_taxon += (None,)
    else:
        if cleaned_data['source']: cleaned_taxon += (taxon.sources.replace('\n', ''),)
    if taxon.reference_description is None: cleaned_taxon += (None,)
    else:
        if cleaned_data['description_reference']: cleaned_taxon += (taxon.reference_description.replace('\n', ''),)
    return cleaned_taxon


def get_sample(samples, param):
    """
    This function get all Information needed from all or specific sample
    :param samples: The model which is connected to the table Prelevement in the database
    :param param: the parameter's if the user want to export his research
    :return: a list of tuple
    """
    if param is None:
        list_not_proper = samples.objects.all()
    else:
        list_not_proper = get_specific_search_sample(samples, param)
    list_sample = [
        ('NOM', 'AUTEUR', 'LOCALISATION', 'TOPONYME', 'ALTITUDE MIN', 'ALTITUDE MAX', 'COORDONNEE X', 'COORDONNEE Y',
         'DATE', 'TYPE SPECIMEN')
    ]
    for sample in list_not_proper.iterator():
        tupple = (sample.id_taxref.lb_nom, sample.id_taxref.lb_auteur, sample.id_loc, sample.toponyme,
                  sample.altitude_min, sample.altitude_max, sample.toponymie_x, sample.toponymie_y, sample.date,
                  sample.type_specimen)
        list_sample.append(tupple)
    return list_sample


def inspect_url_variable(param, params_search):
    """
    Get the get parameter's from the past url
    :param param: the user's parameter if the user want to export his research
    :param params_search: a dict which contain's the default parameter's name
    :return: a dict
    """
    list_param = {}
    if param is None:
        return None
    else:
        for params in params_search:
            if params in param:
                first = param.find(params)
                part_param = param[first:]
                if part_param.find('&') == -1:
                    list_param[params] = part_param[part_param.find('=') + 1:]
                else:
                    list_param[params] = part_param[part_param.find('=') + 1:part_param.find('&')]
        return list_param


def get_specific_search_taxon(taxons, list_param):
    """
    Filter from the user's parameter
    :param taxons: The model which is connected to the table Taxon in the database
    :param list_param:
    :return: a list of taxon
    """
    list_not_proper = taxons.objects.all()
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


def get_specific_search_sample(taxons, param):
    """
    Filter from the user's parameter's
    :param taxons: The model which is connected to the table Taxon in the database
    :param param: the user's parameter if the user want to export his research
    :return: a list filtered
    """
    list_not_proper = taxons.objects.all()
    list_param_sample = inspect_url_variable(param, params_search_sample)
    if 'q' in list_param_sample:
        if list_param_sample['q'] != '':
            list_not_proper = list_not_proper.filter(
                id_taxref__lb_nom__icontains=list_param_sample['q'].replace("+", " "))
    return list_not_proper


def get_taxon_child(taxon, queryset, child, count_es):
    """
    This function will give us all the child of the child of a taxon and returning it into a list
    For that we have to do a recursive function
    :param taxon: The model which is connected to the table Taxon in the database
    :param queryset: its a queryset we use to know if the child we want to append isn't already added
    :param child: the current taxon from who we want the child
    :param count_es:
    :return: the new list of taxon we want
    """
    lchild = taxon.objects.filter(id_sup=child.id)
    if lchild:
        list_child = []
        for child2 in lchild:
            list_child_temp, count_es = get_taxon_child(taxon, queryset, child2, count_es)
            list_child.append([child2, list_child_temp])
        if child.rang.rang == 'ES' or child.rang.rang == 'SSES':
            count_es = count_es + 1
        return list_child, count_es
    else:
        if child.rang.rang == 'ES' or child.rang.rang == 'SSES':
            count_es = count_es + 1
        return None, count_es


def get_search_results(taxons, search_term):
    """
    The goal of this function is to retun in a list of list all the children of a specific taxon
    :param taxons: The model which is connected to the table Taxon in the database
    :param search_term: the term the user entered
    :return: the list of children
    """
    queryset = taxons.objects.filter(Q(lb_nom__icontains=search_term))
    list_taxon = []
    count_es = 0
    if len(queryset) == 1:
        taxon = queryset.first()
        if taxon.id_ref_id == taxon.id:
            list_child = taxons.objects.filter(id_sup=taxon.id)
            list_temp_taxon = []
            for child in list_child:
                list_temp_child, count_es = get_taxon_child(taxons, queryset, child, count_es)
                list_temp_taxon.append([child, list_temp_child])
            list_taxon.append(taxon)
            list_taxon.append(list_temp_taxon)
        return list_taxon, count_es
    else:
        if len(queryset) == 0:
            error = 'Aucun résultat trouvé.'
            return error, 0
        else:
            error = 'Trop de résultats. Vous voulez dire ?'
            for taxon in queryset:
                error += '</br>' + taxon.__str__()
            return error, 0


def get_search_results_auteur(taxons, search_term):
    """
    The goal of this function is to retun a list of genus related by a author
    :param taxons: The model which is connected to the table Taxon in the database
    :param search_term: the term the user entered
    :return: the list of children
    """
    queryset = taxons.objects.filter(Q(lb_auteur__icontains=search_term) & Q(rang='GN'))
    list_taxon = []
    count_es = 0
    if len(queryset) > 0:
        for taxon in queryset:
            if taxon.id_ref_id == taxon.id:
                list_child = taxons.objects.filter(id_sup=taxon.id)
                list_temp_taxon = []
                for child in list_child:
                    list_temp_child, count_es = get_taxon_child(taxons, queryset, child, count_es)
                    list_temp_taxon.append([child, list_temp_child])
                list_taxon.append([taxon, list_temp_taxon])
        return list_taxon, count_es
    else:
        error = 'Aucun résultat trouvé.'
        return error, 0


def constr_hierarchy_tree_adv_search(taxons, search_term, auteur):
    """
    From a search term, we get the taxonomic rank, then we search for its children. Finally we construct the
    hierarchy tree from these data. Also we return the number of species and of sub-species inherited from the taxon
    entered by the user
    :param taxons: The model which is connected to the table Taxon in the database
    :param search_term: the term the user entered
    :param auteur: a boolean if the user want to search by author or not
    :return: a string with html tag
    """
    if search_term == '':
        return 'Veuillez remplir le champ de recherche !', 0
    else:
        if auteur:
            list_taxon, count_es = get_search_results_auteur(taxons, search_term)
            if type(list_taxon) is str:
                return list_taxon, 0
            html_hierarchy = ''
            for l_taxon in list_taxon:
                html_hierarchy += '<div>'
                list_hierarchy, count = l_taxon[0].get_hierarchy()
                html_hierarchy_begin, html_hierarchy_end = constr_hierarchy_tree_branch_parents(list_hierarchy)
                html_hierarchy_child = ''
                html_hierarchy_child = contr_hierarchy_tree_branch_adv_search_child(l_taxon[1],
                                                                                    count + 1, html_hierarchy_child)
                html_taxon = '<li class="folder"><label><strong>{} :</strong> {} {}</label></li>' \
                    .format(l_taxon[0].rang, l_taxon[0].lb_nom, l_taxon[0].lb_auteur)
                html_hierarchy_end = html_hierarchy_child + '</ul></ul></li>'
                html_hierarchy += html_hierarchy_begin + html_taxon + html_hierarchy_end + '</div>'
        else:
            list_taxon, count_es = get_search_results(taxons, search_term)
            if type(list_taxon) is str:
                return list_taxon, 0
            list_hierarchy, count = list_taxon[0].get_hierarchy()
            html_hierarchy_begin, html_hierarchy_end = constr_hierarchy_tree_branch_parents(list_hierarchy)
            html_hierarchy_child = ''
            html_hierarchy_child = contr_hierarchy_tree_branch_adv_search_child(list_taxon[1],
                                                                                count + 1, html_hierarchy_child)
            html_taxon = '<li class="folder"><label><strong>{} :</strong> {} {}</label></li>' \
                .format(list_taxon[0].rang, list_taxon[0].lb_nom, list_taxon[0].lb_auteur)
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
    html_hierarchy_begin = '<ul class="tree"><br/>'
    html_hierarchy_end = '</ul>'
    if list_hierarchy is not None:
        for parent in reversed(list_hierarchy):
            html_hierarchy_begin = html_hierarchy_begin + '''<li><label class="tree_label" for="c{}">
            <strong>{} : </strong></al><a href="/fatercal/taxon/{}/">{}</a>
            </label><ul>'''.format(count_parent, parent.rang, parent.id, parent)
            html_hierarchy_end = '</ul></li>' + html_hierarchy_end
            count_parent = count_parent + 1
    return html_hierarchy_begin, html_hierarchy_end


def contr_hierarchy_tree_branch_adv_search_child(list_taxon, count, hierarchy_child):
    """
    Construct the end of the hierarchy tree
    :param list_taxon: a list which contains different taxon
    :param count: an int
    :param hierarchy_child: a string with html tag
    :return: a string with html tag
    """
    for l_taxon in list_taxon:
        hierarchy_child = hierarchy_child + \
                          '<ul><li><label class="tree_label" for="c{}"/><strong>{} : </strong></al>' \
                          '<a href="/fatercal/taxon/{}/">{}</a></label>   ''' \
                              .format(count, l_taxon[0].rang, l_taxon[0].id, l_taxon[0])
        if l_taxon[1] is not None:
            hierarchy_child = contr_hierarchy_tree_branch_adv_search_child(l_taxon[1], count + 1, hierarchy_child)
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
        str_child = '<ul><li><label class="tree_label" for="c{}"/><strong>{} : </strong></label><ul>' \
            .format(str(nb + 1), rang)
        for child in list_child:
            if rang != child.rang:
                str_child = str_child + '''</ul></li><li class="folder"><label for="c{}">
                <strong>{} : </strong></label><li><ul>
                <a href="/fatercal/taxon/{}/">{}</a>'''.format(str(nb + 1), child.rang, child.id, child)
                rang = child.rang
            else:
                str_child = str_child + '<li><a href="/fatercal/taxon/{}/">{} {}</a></li>' \
                    .format(child.id, child.lb_nom, child.lb_auteur)
    else:
        str_child = ''
    return str_child


def get_form_advanced_search(search_advanced, request):
    """
    Construct the default form for advanced search
    :param search_advanced: a form (Django doc)
    :param request: a request (Django doc)
    :return: an HttpResponse (Django doc)
    """
    template = loader.get_template('fatercal/advanced_search/change_form.html')
    form = search_advanced()
    context = {
        'form': form,
        'count_es': -1
    }
    return HttpResponse(template.render(context, request))


def get_taxons_for_sample(param, taxons):
    """
    Construct a csv file with research result for importing sample for these taxon
    :return: a list of tuple
    """
    if param is None:
        list_not_proper = taxons.objects.all()
    else:
        list_param = inspect_url_variable(param, params_search_taxon)
        list_not_proper = get_specific_search_taxon(taxons, list_param)
    list_taxon = [
        ('id', 'rang', 'nom', 'auteur', 'collection museum', 'code specimen', 'nb taxon present',
         'type specimen', 'type enregistrement', 'mode de collecte', 'date', 'information complementaire',
         'localisation', 'latitude', 'longitude', 'GPS', 'altitude min', 'altitude max', 'recolteurs')
    ]
    for taxon in list_not_proper:
        list_taxon.append((taxon.id, taxon.rang.lb_rang, taxon.lb_auteur))
    return list_taxon


def verify_sample(line, taxons, type_enregistrement, count):
    """
    This function verify if all the parameter's with condition are good
    :param line: The line in the csv file
    :param taxon: The model which is connected to the table Taxon in the database
    :param type_enregistrement: The model which is connected to the table TypeEnregistrement in the database
    :param count: the line number we check
    :return: a boolean
    """
    result = {
        'good': False,
        'message': 'Une erreur à été perçue à la ligne {}.'.format(count)
    }
    if taxons.objects.filter(id=line['id']).count() > 0:
        if type_enregistrement.objects.filter(lb_type=line['type enregistrement']).count() > 0:
            line['latitude'] = line['latitude'].replace(',', '.')
            line['longitude'] = line['longitude'].replace(',', '.')
            if is_variable_good(line):
                if line['date'] is None or line['date'] == '':
                    result['good'] = True
                elif re.match(regex_date, line['date']):
                    result['good'] = True
                else:
                    result['message'] += " La date entrée n'est pas au bon format."
            else:
                result['message'] += " L'un des nombres sur cette ligne contient des lettres ou GPS n'est pas au bon " \
                                     "format."
        else:
            result['message'] += " Le type d'enregistrement entré n'existe pas."
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
        print(line)
        if line['latitude'] != '': float(line['latitude'])
        if line['longitude'] != '': float(line['longitude'])
        if line['altitude max'] != '': int(line['altitude max'])
        if line['altitude min'] != '': int(line['altitude min'])
        if line['nb taxon present'] != '': int(line['nb taxon present'])
        if line['GPS'] == '' or line['GPS'] == 'true' or line['GPS'] == 'false':
            return True
        else:
            return False
    except ValueError:
        return False


def construct_sample(line, taxons, prelevements, localisations, recolteurs, type_loc, type_enregistrement):
    """
    Construct the sample to import into the database from a line in the csv file
    :param line: The line in the csv file
    :param taxons: The model which is connected to the table Taxon in the database
    :param prelevements: The model which is connected to the table Prelevement in the database
    :param localisations: The model which is connected to the table Localisation in the database
    :param recolteurs: The model which is connected to the table Recolteur in the database
    :param type_loc: The model which is connected to the table TypeLoc in the database
    :param type_enregistrement: The model which is connected to the table TypeEnregistrement in the database
    :return: a dictionnary
    """
    result = {
        'sample': None,
        'loc': None,
        'list_harvester': []
    }
    variable = get_variable_in_good_format(line)
    if len(localisations.objects.filter(nom=line['localisation'])) > 0:
        loc = localisations.objects.filter(nom=line['localisation'])[0]
    else:
        loc = localisations(loc_type=type_loc.objects.filter(id_type=4).first(), nom=line['localisation'],
                            latitude=variable['latitude'], longitude=variable['longitude'])
    result['loc'] = loc
    sample = prelevements(id_taxref=taxons.objects.filter(id=line['id']).first(),
                          collection_museum=line['collection museum'],
                          code_specimen=line['code specimen'], nb_taxon_present=variable['nb_taxon'],
                          type_specimen=line['type specimen'],
                          type_enregistrement=type_enregistrement.objects.filter(
                              lb_type=line['type enregistrement']).first(),
                          mode_de_collecte=line['mode de collecte'], date=line['date'],
                          information_complementaire=line['information complementaire'],
                          toponymie_x=variable['latitude'], toponymie_y=variable['longitude'], gps=variable['GPS'],
                          altitude_min=variable['altitude_min'], altitude_max=variable['altitude_max'])
    result['sample'] = sample
    if line['recolteurs'] != '':
        recolteur = line['recolteurs']
        list_harvester = []
        print(type(recolteur))
        if recolteur.find(',') == -1:
            list_harvester.append(recolteurs(lb_auteur=recolteur.strip()))
        else:
            while recolteur is not None:
                print(recolteur)
                if recolteur.find(',') == -1:
                    harvester = recolteur
                    recolteur = None
                else:
                    harvester = recolteur[:recolteur.find(',')]
                    recolteur = recolteur[recolteur.find(',')+1:]
                list_harvester.append(recolteurs(lb_auteur=harvester.strip()))
        result['list_harvester'] = list_harvester
    return result


def get_variable_in_good_format(line):
    """
    Transform the variable in a usable state
    :param line: The line in the csv file
    :return: a dictionnary
    """
    if line['latitude'] == '' or line['latitude'] is None: latitude = None
    else: latitude = float(line['latitude'])
    if line['longitude'] == '' or line['longitude'] is None: longitude = None
    else: longitude = float(line['longitude'])
    if line['altitude max'] == '' or line['altitude max'] is None: altitude_max = None
    else: altitude_max = int(line['altitude max'])
    if line['altitude min'] == '' or line['altitude min'] is None: altitude_min = None
    else: altitude_min = int(line['altitude max'])
    if line['nb taxon present'] == '' or line['nb taxon present'] is None: nb_taxon = None
    else: nb_taxon = int(line['nb taxon present'])
    if line['GPS'] == '' or line['GPS'] is None: gps = None
    else:
        if line['GPS'] == 'true':
            gps = True
        else:
            gps = False
    return {
        'latitude': latitude,
        'longitude': longitude,
        'altitude_max': altitude_max,
        'altitude_min': altitude_min,
        'nb_taxon': nb_taxon,
        'GPS': gps
    }


def save_all_sample(list_dict_sample):
    """
    This function simply save all the object from the csv file
    :param list_dict_sample: a dictionnary which contains all the object to save
    :return: void
    """
    for sample in list_dict_sample:
        sample['loc'].save()
        sample['sample'].id_loc = sample['loc']
        sample['sample'].save()
        print(sample)
        for harvest in sample['list_harvester']:
            harvest.id_prelevement = sample['sample']
            harvest.save()


class NotGoodSample(Exception):
    def __init__(self, message):
        self.message = message
