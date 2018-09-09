from django.http import HttpResponse
from django.template import loader
from django.db.models import F, Q

""" Variable for the application"""
regex = r"(^\d{4}$)|"
r"(^\d{4}-(0[1-9]|1[0-2])$)|"
r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)|"
r"(^$)|"
r"(^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])\/\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[0-1])$)"
params_search_taxon = ['q', 'nc__status__exact', 'rang__rang__exact', 'valide']
params_search_sample = ['q', 'toponyme']


def get_recolteur(recolteur, prelev):
    """
    Get the Harvesteur's for a specific sample
    :param recolteur:
    :param prelev: the object
    :return: In each case we retuen a string
    """
    list_recolt = recolteur.objects.filter(id_prelevement=prelev.id_prelevement)
    if len(list_recolt) > 0:
        str_recolt = ''
        first = True
        for recolt in list_recolt:
            if first:
                first = False
            else:
                str_recolt += ', '
            str_recolt += '{}'.format(recolt.lb_auteur)
        return str_recolt
    else:
        return 'Récolteur inconnu'


def get_info(taxon):
    """
    This function get all information of superior and miscellaneous info
    :param taxon: The object Taxon from which we want the information we need
    :return: a list containing a summary of the different info on the taxon
    """
    sup = taxon.id_sup
    if sup is None:
        sup = taxon
    list_sup = [sup]
    while sup.id_sup is not None:
        list_sup.append(sup.id_sup)
        sup = sup.id_sup
    if taxon.rang.lb_rang != 'Règne':
        regne = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == 'Règne'), None)
    else:
        regne = taxon.lb_nom
    if taxon.rang.lb_rang != "Phylum/Embranchement":
        phylum = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Phylum/Embranchement"), None)
    else:
        phylum = taxon.lb_nom
    if taxon.rang.lb_rang != "Classe":
        classe = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Classe"), None)
    else:
        classe = taxon.lb_nom
    if taxon.rang.lb_rang != "Ordre":
        ordre = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Ordre"), None)
    else:
        ordre = taxon.lb_nom
    if taxon.rang.lb_rang != "Famille":
        famille = next((tupp.lb_nom for tupp in list_sup if tupp.rang.lb_rang == "Famille"), None)
    else:
        famille = taxon.lb_nom
    if taxon.habitat is None:
        habitat = None
    else:
        habitat = taxon.habitat.habitat
    if taxon.nc is None:
        nc = None
    else:
        nc = taxon.nc.status
    return {
        'regne': regne,
        'phylum': phylum,
        'class': classe,
        'order': ordre,
        'famille': famille,
        'habitat': habitat,
        'nc': nc,
    }


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
    return (None, None, None, None)


def get_taxon(taxons, param):
    """
    This function get all Information needed from all taxon
    :param taxons: The model which is connected to the table Taxon in the database
    :param param: the parameter's if the user want to export his research
    :return: all the taxon with the information we want
    """
    if param is None:
        list_not_proper = taxons.objects.all()
    else:
        list_not_proper = get_specific_search_taxon(taxons, param)
    list_taxon = [
        ('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN', 'ID', 'ID_REF', 'ID_SUP',
         'CD_NOM', 'CD_TAXSUP', 'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM', 'LB_AUTEUR', 'NOM_COMPLET', 'NOM_COMPLET_HTML',
         'NOM_VALIDE', 'NOM_VERN', 'NOM_VERN_ENG', 'HABITAT', 'NC', 'NON PRESENT DANS TAXREF',
         'CD_REF DIFFERENT', 'CD_SUP DIFFERENT', 'VALIDITY DIFFERENT')
    ]
    for taxon in list_not_proper:
        msg = get_msg(taxon)
        if 'sp.' not in taxon.lb_nom:
            if taxon == taxon.id_ref:
                if taxon.id_sup is None:
                    id_sup = None
                else:
                    id_sup = taxon.id_sup_id
                dict_taxon = get_info(taxon)
                tupple = (dict_taxon['regne'], dict_taxon['phylum'], dict_taxon['class'],
                          dict_taxon['order'], dict_taxon['famille'], None, None, taxon.id, taxon.id_ref.id,
                          id_sup, taxon.cd_nom, None, taxon.cd_sup, taxon.cd_ref, taxon.rang.rang,
                          taxon.lb_nom, taxon.lb_auteur, taxon.nom_complet, None, taxon.lb_nom, None, None,
                          dict_taxon['habitat'], dict_taxon['nc']) + msg
                list_taxon.append(tupple)
            else:
                dict_taxon = get_info(taxon.id_ref)
                tupple = (dict_taxon['regne'], dict_taxon['phylum'], dict_taxon['class'],
                          dict_taxon['order'], dict_taxon['famille'], None, None, taxon.id, taxon.id_ref.id,
                          None, taxon.cd_nom, None, taxon.cd_sup, taxon.cd_ref, taxon.rang.rang,
                          taxon.lb_nom, taxon.lb_auteur, taxon.nom_complet, None, taxon.id_ref.lb_nom, None, None, None,
                          None) + msg
                list_taxon.append(tupple)
    return list_taxon


def get_sample(samples, param):
    """
    This function get all Information needed from all or specific sample
    :param samples: The model which is connected to the table Prelevement in the database
    :param param: the parameter's if the user want to export his research
    :return: all the taxon with the information we want
    """
    if param is None:
        list_not_proper = samples.objects.all()
    else:
        list_not_proper = get_specific_search_sample(samples, param)
    list_sample = [
        ('NOM', 'AUTEUR', 'LOCALITE', 'TOPONYME', 'ALTITUDE', 'COORDONNEE X', 'COORDONNEE Y', 'DATE', 'TYPE SPECIMEN')
    ]
    for sample in list_not_proper:
        tupple = (sample.id_taxref.lb_nom, sample.id_taxref.lb_auteur, sample.id_localitee, sample.toponyme,
                  sample.altitude, sample.toponymie_x, sample.toponymie_y, sample.date, sample.type_specimen)
        list_sample.append(tupple)
    return list_sample


def get_specific_search_taxon(taxon, param):
    list_not_proper = taxon.objects.all()
    list_param = {}
    for params in params_search_taxon:
        if params in param:
            first = param.find(params)
            part_param = param[first:]
            if part_param.find('&') == -1:
                list_param[params] = part_param[part_param.find('=')+1:]
            else:
                list_param[params] = part_param[part_param.find('=')+1:part_param.find('&')]
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


def get_specific_search_sample(taxon, param):
    list_not_proper = taxon.objects.all()
    list_param_sample = {}
    for params in params_search_sample:
        if params in param:
            first = param.find(params)
            part_param = param[first:]
            if part_param.find('&') == -1:
                list_param_sample[params] = part_param[part_param.find('=')+1:]
            else:
                list_param_sample[params] = part_param[part_param.find('=')+1:part_param.find('&')]
    if 'q' in list_param_sample:
        if list_param_sample['q'] != '':
            list_not_proper = list_not_proper.filter(id_taxref__lb_nom__icontains=list_param_sample['q'])
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
        if taxon.id_ref.id == taxon.id:
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
            if taxon.id_ref.id == taxon.id:
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
    :return: a tree in a string with html tag
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
            '<a href="/fatercal/taxon/{}/">{}</a></label>   '''\
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
    :return:
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
