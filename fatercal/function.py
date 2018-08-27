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


def get_taxon(taxon):
    """
    This function get all Information needed from all taxon
    :param taxon: The model which is connected to the table Taxon in the database
    :return: all the taxon with the information we want
    """

    list_not_proper = taxon.objects.all()
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


def get_new_taxon(taxon, list_new_taxon, queryset, child):
    """
    This function will give us all the child of the child of a taxon and returning it into a list
    For that we have to do a recursive function
    :param taxon: The model which is connected to the table Taxon in the database
    :param list_new_taxon:
    :param queryset: its a queryset we use to know if the child we want to append isn't already added
    :param child: the current taxon from who we want the child
    :return: the new list of taxon we want
    """
    list_child = taxon.objects.filter(id_sup=child.id)
    if list_child:
        for child2 in list_child:
            get_new_taxon(list_new_taxon, queryset, child2)
            if len(queryset.filter(id=child2.id)) == 0 and child2 not in list_new_taxon:
                list_new_taxon.append(child2)
        return list_new_taxon
    else:
        return list_new_taxon

