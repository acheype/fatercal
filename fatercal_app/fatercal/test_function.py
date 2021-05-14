from django.test import TestCase
from django.contrib.auth.models import User, Group
from .function import *
from .models import TaxrefStatus, TaxrefHabitat, TaxrefRang
from .models import TypeEnregistrement, TaxrefUpdate
from .forms import ChooseData, ChooseTaxonToInsert

import os
import csv
import datetime


# Test function that are related to the model Taxon
class TaxonTestCase(TestCase):
    def setUp(self):
        self.status = TaxrefStatus.objects.create(status="A", lb_status="Absent")
        self.habitat = TaxrefHabitat.objects.create(habitat=1, lb_habitat="Marin")
        self.kingdom = Taxon.objects.create(lb_nom="kingdom", lb_auteur="auteur1",
                                            rang=TaxrefRang.objects.create(rang='KD', lb_rang='Regne'))
        self.phylum = Taxon.objects.create(lb_nom="phylum", lb_auteur="auteur2",
                                           rang=TaxrefRang.objects.create(rang='PH', lb_rang='Phylum'),
                                           id_sup=self.kingdom)
        self.classe = Taxon.objects.create(lb_nom="classe", lb_auteur="auteur3",
                                           rang=TaxrefRang.objects.create(rang='CL', lb_rang='Classe'),
                                           id_sup=self.phylum)
        self.order = Taxon.objects.create(lb_nom="order", lb_auteur="auteur4",
                                          rang=TaxrefRang.objects.create(rang='OR', lb_rang='Ordre'),
                                          id_sup=self.classe)
        self.family = Taxon.objects.create(lb_nom="family", lb_auteur="auteur5",
                                           rang=TaxrefRang.objects.create(rang='FM', lb_rang='Famille'),
                                           id_sup=self.order)
        self.genus = Taxon.objects.create(lb_nom="genus", lb_auteur="auteur6",
                                          rang=TaxrefRang.objects.create(rang='GN', lb_rang='Genre'),
                                          id_sup=self.family)
        self.species = Taxon.objects.create(lb_nom="species", lb_auteur="auteur7",
                                            rang=TaxrefRang.objects.create(rang='ES', lb_rang='Espèce'),
                                            id_sup=self.genus)
        self.sub_species = Taxon.objects.create(lb_nom="sub_species", lb_auteur="auteur8",
                                                rang=TaxrefRang.objects.create(rang='SSES', lb_rang='Sous-Espèce'),
                                                id_sup=self.species)
        self.species_syn = Taxon.objects.create(id_ref=self.species, lb_nom="species_synonymous",
                                                lb_auteur="auteur9", rang=self.species.rang)
        self.sub_species.id_ref = self.sub_species
        self.sub_species.save()
        self.species.id_ref = self.species
        self.species.save()
        self.genus.id_ref = self.genus
        self.genus.save()
        self.family.id_ref = self.family
        self.family.save()
        self.order.id_ref = self.order
        self.order.save()
        self.classe.id_ref = self.classe
        self.classe.save()
        self.phylum.id_ref = self.phylum
        self.phylum.save()
        self.kingdom.id_ref = self.kingdom
        self.kingdom.save()
        create_db_view_test()

    def test_change_ref_taxon(self):
        second_species = Taxon.objects.create(id=10, lb_nom="second_species", lb_auteur="auteur10",
                                              rang=self.species.rang, id_sup=self.genus)
        second_species.id_ref = second_species
        second_species.save()
        cleaned_data = {'taxon': second_species}
        change_ref_taxon(self.species, cleaned_data)
        self.species = Taxon.objects.get(id=7)
        self.sub_species = Taxon.objects.get(id=8)
        self.species_syn = Taxon.objects.get(id=9)
        self.assertEqual(self.species_syn.id_ref, second_species)
        self.assertEqual(self.sub_species.id_sup, second_species)
        self.assertEqual(self.species.id_ref, second_species)

    def test_change_sup_taxon(self):
        second_genus = Taxon.objects.create(lb_nom="second_genus", lb_auteur="auteur10",
                                            rang=self.genus.rang, id_sup=self.genus)
        second_genus.id_ref = second_genus
        second_genus.save()
        cleaned_data = {'taxon_superieur': second_genus}
        template_expected = loader.get_template('fatercal/return_change_taxon.html')
        error_expected = ''
        template_output, error_output = change_sup_taxon(self.species, cleaned_data)
        self.assertEqual(template_expected.render(), template_output.render())
        self.assertEqual(error_expected, error_output)
        self.species = Taxon.objects.get(id=self.species.id)
        self.assertEqual(self.species.id_sup, second_genus)

        cleaned_data = {'taxon_superieur': self.sub_species}
        template_expected = loader.get_template('fatercal/change_taxon.html')
        error_expected = 'Le taxon supérieur a un rang inférieur a votre taxon .'
        template_output, error_output = change_sup_taxon(self.species, cleaned_data)
        self.assertEqual(template_expected.render(), template_output.render())
        self.assertEqual(error_expected, error_output)
        self.species = Taxon.objects.get(id=self.species.id)
        self.assertEqual(self.species.id_sup, second_genus)

    def test_get_superior(self):
        dict_parent = get_superior(self.species)
        self.assertEqual(dict_parent['GN'], self.genus.lb_nom)
        self.assertEqual(dict_parent['FM'], self.family.lb_nom)

        dict_parent = get_superior(self.kingdom)
        self.assertEqual(dict_parent, {})

    def test_get_message(self):
        species_syn = Taxon.objects.get(lb_nom="species_synonymous")
        self.assertEqual(get_msg(self.species), ('x', None, None, None))
        self.species.cd_nom = 1
        self.species.cd_ref = 2
        self.species.save()
        species_syn.cd_nom = 2
        species_syn.cd_ref = 1
        species_syn.save()
        self.assertEqual(get_msg(self.species), (None, None, None, 'x'))
        self.assertEqual(get_msg(species_syn), (None, None, None, 'x'))

        species_syn.cd_ref = 2
        species_syn.save()
        self.assertEqual(get_msg(species_syn), (None, 'x', None, None))
        self.species.cd_ref = 1
        self.species.cd_sup = 3
        self.species.id_ref.cd_nom = 1
        self.species.id_ref.save()
        self.species.save()
        self.genus.cd_nom = 4
        self.genus.save()
        self.assertEqual(get_msg(self.species), (None, None, 'x', None))
        self.species.id_sup.cd_nom = 3
        self.species.id_sup.save()
        self.assertEqual(get_msg(self.species), (None, None, None, None))

    def test_construct_clean_taxon(self):
        self.assertEqual(construct_cleaned_taxon(self.species), ('kingdom', 'phylum', 'classe', 'order', 'family', None,
                                                                 None, self.species.id, self.species.id, self.genus.id, None, None, None, None, 'ES',
                                                                 'genus species', 'auteur7', 'genus species auteur7',
                                                                 None, 'genus species', None, None, None, None, 'x',
                                                                 None, None, None))
        self.species.habitat = self.habitat
        self.species.nc = self.status
        self.species.id_sup = None
        self.species.save()
        self.assertEqual(construct_cleaned_taxon(self.species), (None, None, None, None, None, None, None, self.species.id, self.species.id, None,
                                                                 None, None, None, None, 'ES', 'genus species',
                                                                 'auteur7', 'genus species auteur7', None,
                                                                 'genus species', None, None, 1, 'A', 'x', None, None,
                                                                 None))

        self.assertEqual(construct_cleaned_taxon(self.species_syn), (None, None, None, None, None, None, None, self.species_syn.id, self.species.id,
                                                                     None, None, None, None, None, 'ES',
                                                                     'species_synonymous', 'auteur9',
                                                                     'species_synonymous auteur9', None,
                                                                     'genus species', None, None, None, None, 'x', None,
                                                                     None, None))

    def test_get_specific_taxon_search(self):
        dict_param = {}
        list_not_proper = get_specific_search_taxon(dict_param)
        self.assertEqual(list_not_proper.count(), 9)

        dict_param = {'q': 'genus species'}
        list_not_proper = get_specific_search_taxon(dict_param)
        self.assertEqual(list_not_proper.first(), self.species)

        self.species.nc = self.status
        self.species.save()
        dict_param = {'nc__status__exact': 'A'}
        list_not_proper = get_specific_search_taxon(dict_param)
        self.assertEqual(list_not_proper.first(), self.species)

        dict_param = {'rang__rang__exact': 'KD'}
        kingdom = Taxon.objects.get(lb_nom="kingdom")
        list_not_proper = get_specific_search_taxon(dict_param)
        self.assertEqual(list_not_proper.first(), kingdom)

    def test_get_specific_taxon_search_taxref(self):
        dict_param = {}
        list_not_proper = get_specific_search_taxon_taxref(dict_param)
        self.assertEqual(list_not_proper.count(), 9)

        dict_param = {'q': 'genus species'}
        list_not_proper = get_specific_search_taxon_taxref(dict_param)
        taxref_export_expected = TaxrefExport.objects.get(lb_nom='genus species')
        self.assertEqual(list_not_proper.first(), taxref_export_expected)

        self.species.save()
        dict_param = {'nc__status__exact': 'A'}
        taxref_export_expected = None
        list_not_proper = get_specific_search_taxon_taxref(dict_param)
        self.assertEqual(list_not_proper.first(), taxref_export_expected)

        dict_param = {'rang__rang__exact': 'KD'}
        taxref_export_expected = TaxrefExport.objects.get(lb_nom="kingdom")
        list_not_proper = get_specific_search_taxon_taxref(dict_param)
        self.assertEqual(list_not_proper.first(), taxref_export_expected)

    def test_get_taxon_child(self):
        self.sub_species = Taxon.objects.get(lb_nom="genus species sub_species")
        list_child, nb = get_taxon_child(self.genus, 0)
        self.assertEqual(list_child, [[self.species, [[self.sub_species, None]]]])

        species_2 = Taxon.objects.create(id=10, lb_nom="species_2", lb_auteur="auteur10", rang=self.species.rang,
                                         id_sup=self.genus)
        list_child, nb = get_taxon_child(self.genus, 0)
        self.assertEqual(list_child, [[self.species, [[self.sub_species, None]]], [species_2, None]])

    def test_get_child_of_child(self):
        list_child, nb = get_child_of_child(self.genus)
        self.assertEqual(list_child, [self.genus, [[self.species, [[self.sub_species, None]]]]])

    def test_get_hierarchy_to_dicy(self):
        dict_hierarchy_output = get_hierarchy_to_dict(self.sub_species)
        dict_hierarchy_expected = {
            'Ordre': 'order',
            'Famille': 'family',
            'Sous-Famille': '',
            'Genre': 'genus',
            'Sous-Genre': '',
            'Espèce': 'genus species',
            'Sous-Espèce': 'genus species sub_species'
        }
        self.assertEqual(dict_hierarchy_expected, dict_hierarchy_output)

    def test_get_taxon_from_search(self):
        param = None
        list_taxon_output = get_taxon_from_search(param)
        list_taxon_expected = [('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN', 'ID',
                                'ID_REF', 'ID_SUP', 'CD_NOM', 'CD_TAXSUP', 'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM',
                                'LB_AUTEUR', 'NOM_COMPLET', 'NOM_COMPLET_HTML', 'NOM_VALIDE', 'NOM_VERN',
                                'NOM_VERN_ENG', 'HABITAT', 'NC', 'NON PRESENT DANS TAXREF', 'CD_REF DIFFERENT',
                                'CD_SUP DIFFERENT', 'VALIDITY DIFFERENT'),
                               ('kingdom', 'phylum', None, None, None, None, None, self.classe.id, self.classe.id, self.phylum.id, None, None, None, None,
                                'CL', 'classe', 'auteur3', 'classe auteur3', None, 'classe', None, None, None, None,
                                'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', None, None, None, self.family.id, self.family.id, self.order.id, None, None, None,
                                None, 'FM', 'family', 'auteur5', 'family auteur5', None, 'family', None, None, None,
                                None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.genus.id, self.genus.id, self.family.id, None, None,
                                None, None, 'GN', 'genus', 'auteur6', 'genus auteur6', None, 'genus', None, None, None,
                                None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species.id, self.species.id, self.genus.id, None, None, None,
                                None, 'ES', 'genus species', 'auteur7', 'genus species auteur7', None, 'genus species',
                                None, None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.sub_species.id, self.sub_species.id, self.species.id, None, None, None,
                                None, 'SSES', 'genus species sub_species', 'auteur8',
                                'genus species sub_species auteur8', None, 'genus species sub_species', None, None,
                                None, None, 'x', None, None, None),
                               (None, None, None, None, None, None, None, self.kingdom.id, self.kingdom.id, None, None, None, None, None, 'KD',
                                'kingdom', 'auteur1', 'kingdom auteur1', None, 'kingdom', None, None, None, None, 'x',
                                None, None, None),
                               ('kingdom', 'phylum', 'classe', None, None, None, None, self.order.id, self.order.id, self.classe.id, None, None, None, None,
                                'OR', 'order', 'auteur4', 'order auteur4', None, 'order', None, None, None, None, 'x',
                                None, None, None),
                               ('kingdom', None, None, None, None, None, None, self.phylum.id, self.phylum.id, self.kingdom.id, None, None, None, None, 'PH',
                                'phylum', 'auteur2', 'phylum auteur2', None, 'phylum', None, None, None, None, 'x',
                                None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species_syn.id, self.species.id, None, None, None,
                                None, None, 'ES', 'species_synonymous', 'auteur9', None, None, 'genus species', None,
                                None, None, None, 'x', None, None, None)]
        self.assertEqual(list_taxon_expected, list_taxon_output)

        param = {'q': 'species'}
        list_taxon_output = get_taxon_from_search(param)
        list_taxon_expected = [('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN', 'ID',
                                'ID_REF', 'ID_SUP', 'CD_NOM', 'CD_TAXSUP', 'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM',
                                'LB_AUTEUR', 'NOM_COMPLET', 'NOM_COMPLET_HTML', 'NOM_VALIDE', 'NOM_VERN',
                                'NOM_VERN_ENG', 'HABITAT', 'NC', 'NON PRESENT DANS TAXREF', 'CD_REF DIFFERENT',
                                'CD_SUP DIFFERENT', 'VALIDITY DIFFERENT'),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species.id, self.species.id, self.genus.id, None, None, None,
                                None, 'ES', 'genus species', 'auteur7', 'genus species auteur7', None, 'genus species',
                                None, None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.sub_species.id, self.sub_species.id, self.species.id, None, None, None,
                                None, 'SSES', 'genus species sub_species', 'auteur8',
                                'genus species sub_species auteur8', None, 'genus species sub_species', None, None,
                                None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species_syn.id, self.species.id, None, None, None,
                                None, None, 'ES', 'species_synonymous', 'auteur9', None, None, 'genus species', None,
                                None, None, None, 'x', None, None, None)]
        self.assertEqual(list_taxon_expected, list_taxon_output)

    def test_get_taxon_from_search_taxref(self):
        param = {}
        list_taxon_output = get_taxon_from_search_taxref(param)
        list_taxon_expected = [('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN', 'ID',
                                'ID_REF', 'ID_SUP', 'CD_NOM', 'CD_TAXSUP', 'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM',
                                'LB_AUTEUR', 'NOM_COMPLET', 'NOM_COMPLET_HTML', 'NOM_VALIDE', 'NOM_VERN',
                                'NOM_VERN_ENG', 'HABITAT', 'NC', 'GRANDE_TERRE', 'ILES_LOYAUTE', 'AUTRE',
                                'NON PRESENT DANS TAXREF', 'CD_REF DIFFERENT', 'CD_SUP DIFFERENT',
                                'VALIDITY DIFFERENT'),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species_syn.id, self.species.id, None, None, None,
                                None, None, 'ES', 'species_synonymous', 'auteur9', None, None, None, None, None, None,
                                None, None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.sub_species.id, self.sub_species.id, self.species.id, None, None, None,
                                None, 'SSES', 'genus species sub_species', 'auteur8',
                                'genus species sub_species auteur8', None, None, None, None, None, None, None, None,
                                None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species.id, self.species.id, self.genus.id, None, None, None,
                                None, 'ES', 'genus species', 'auteur7', 'genus species auteur7', None, None, None, None,
                                None, None, None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.genus.id, self.genus.id, self.family.id, None, None, None,
                                None, 'GN', 'genus', 'auteur6', 'genus auteur6', None, None, None, None, None, None,
                                None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', None, None, None, self.family.id, self.family.id, self.order.id, None, None, None,
                                None, 'FM', 'family', 'auteur5', 'family auteur5', None, None, None, None, None, None,
                                None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', None, None, None, None, self.order.id, self.order.id, self.classe.id, None, None, None, None,
                                'OR', 'order', 'auteur4', 'order auteur4', None, None, None, None, None, None, None,
                                None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', None, None, None, None, None, self.classe.id, self.classe.id, self.phylum.id, None, None, None, None,
                                'CL', 'classe', 'auteur3', 'classe auteur3', None, None, None, None, None, None, None,
                                None, None, 'x', None, None, None),
                               ('kingdom', None, None, None, None, None, None, self.phylum.id, self.phylum.id, self.kingdom.id, None, None, None, None, 'PH',
                                'phylum', 'auteur2', 'phylum auteur2', None, None, None, None, None, None, None, None,
                                None, 'x', None, None, None),
                               (None, None, None, None, None, None, None, self.kingdom.id, self.kingdom.id, None, None, None, None, None, 'KD',
                                'kingdom', 'auteur1', 'kingdom auteur1', None, None, None, None, None, None, None, None,
                                None, 'x', None, None, None)]
        self.assertEqual(list_taxon_expected, list_taxon_output)

        param = {'q': 'species'}
        list_taxon_output = get_taxon_from_search_taxref(param)
        list_taxon_expected = [('REGNE', 'PHYLUM', 'CLASSE', 'ORDRE', 'FAMILLE', 'GROUP1_INPN', 'GROUP2_INPN', 'ID',
                                'ID_REF', 'ID_SUP', 'CD_NOM', 'CD_TAXSUP', 'CD_SUP', 'CD_REF', 'RANG', 'LB_NOM',
                                'LB_AUTEUR', 'NOM_COMPLET', 'NOM_COMPLET_HTML', 'NOM_VALIDE', 'NOM_VERN',
                                'NOM_VERN_ENG', 'HABITAT', 'NC', 'GRANDE_TERRE', 'ILES_LOYAUTE', 'AUTRE',
                                'NON PRESENT DANS TAXREF', 'CD_REF DIFFERENT', 'CD_SUP DIFFERENT',
                                'VALIDITY DIFFERENT'),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species_syn.id,
                               self.species.id, None, None, None, None, None, 'ES', 'species_synonymous', 'auteur9',
                               None, None, None, None, None, None, None, None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.sub_species.id,
                               self.sub_species.id, self.species.id, None, None, None, None, 'SSES',
                               'genus species sub_species', 'auteur8', 'genus species sub_species auteur8', None,
                               None, None, None, None, None, None, None, None, 'x', None, None, None),
                               ('kingdom', 'phylum', 'classe', 'order', 'family', None, None, self.species.id,
                               self.species.id, self.genus.id, None, None, None, None, 'ES', 'genus species',
                               'auteur7', 'genus species auteur7', None, None, None, None, None, None, None,
                               None, None, 'x', None, None, None)]
        self.assertEqual(list_taxon_expected, list_taxon_output)

    def test_get_taxon_personal(self):
        self.species.habitat = self.habitat
        self.species.nc = self.status
        self.species.save()
        form = ChooseData()
        form.cleaned_data = {
            'q': 'species', 'nc__status__exact': 'A', 'rang__rang__exact': '', 'valide': '',
            'id': True, 'id_sup': True, 'id_ref': True, 'name': True, 'author': True, 'rank': True,
            'rank_sup': True, 'status': True, 'habitat': True, 'grande_terre': True, 'loyalty_island': True,
            'other': True, 'remark': True, 'source': True, 'description_reference': True
        }
        taxon_personal_output = get_taxon_personal(form)
        taxon_personal_expected = [('id', 'id_sup', 'id_ref', 'name', 'author', 'rank', 'rank_sup', 'status', 'habitat',
                                    'grande_terre', 'loyalty_island', 'other', 'remark', 'source',
                                    'description_reference'),
                                   (self.species.id, self.genus.id, self.species.id, 'genus species', 'auteur7', 'Espèce', self.genus, 'Absent',
                                   'Marin', None, None, None, None, None, None)]
        self.assertEqual(taxon_personal_expected, taxon_personal_output)

    def test_construct_list_taxon(self):
        param = {'q': 'species',}
        list_not_proper = get_specific_search_taxon(param)
        cleaned_data = {
            'id': False, 'id_sup': False, 'id_ref': False, 'name': False, 'author': False, 'rank': False,
            'rank_sup': False, 'status': False, 'habitat': False, 'grande_terre': False, 'loyalty_island': False,
            'other': False, 'remark': False, 'source': False, 'description_reference': False
        }
        list_taxon_expected = [()]
        list_taxon_output = construct_list_taxon(list_not_proper, cleaned_data)
        self.assertEqual(list_taxon_expected, list_taxon_output)

        cleaned_data = {
            'id': True, 'id_sup': True, 'id_ref': True, 'name': True, 'author': True, 'rank': True, 'rank_sup': True,
            'status': True, 'habitat': True, 'grande_terre': True, 'loyalty_island': True, 'other': True,
            'remark': True, 'source': True, 'description_reference': True
        }
        list_taxon_expected = [('id', 'id_sup', 'id_ref', 'name', 'author', 'rank', 'rank_sup', 'status', 'habitat',
                                'grande_terre', 'loyalty_island', 'other', 'remark', 'source', 'description_reference'),
                               (self.species.id, self.genus.id, self.species.id, 'genus species', 'auteur7', 'Espèce', self.genus, None, None, None, None, None,
                                None, None, None),
                               (self.sub_species.id, self.species.id, self.sub_species.id, 'genus species sub_species', 'auteur8', 'Sous-Espèce', self.species, None,
                                None, None, None, None, None, None, None),
                               (self.species_syn.id, None, self.species.id, 'species_synonymous', 'auteur9', 'Espèce', None, None, None, None, None,
                                None, None, None, None)]

        list_taxon_output = construct_list_taxon(list_not_proper, cleaned_data)
        self.assertEqual(list_taxon_expected, list_taxon_output)

    def test_construct_cleaned_taxon_search(self):
        cleaned_data = {
            'id': True, 'id_sup': True, 'id_ref': True, 'name': True, 'author': True, 'rank': True, 'rank_sup': True,
            'status': True, 'habitat': True, 'grande_terre': True, 'loyalty_island': True, 'other': True,
            'remark': True, 'source': True, 'description_reference': True
        }
        cleaned_taxon_search_output = construct_cleaned_taxon_search(self.species, cleaned_data)
        cleaned_taxon_search_expected = (self.species.id, self.genus.id, self.species.id, 'genus species', 'auteur7', 'Espèce',
                                         self.genus, None, None, None, None, None, None, None, None)
        self.assertEqual(cleaned_taxon_search_expected, cleaned_taxon_search_output)

        self.species.id_sup = None
        self.species.habitat = self.habitat
        self.species.nc = self.status
        self.species.remarque = "Une remarque"
        self.species.sources = "Une source"
        self.species.reference_description = "Une description de reference"
        self.species.save()
        cleaned_taxon_search_output = construct_cleaned_taxon_search(self.species, cleaned_data)
        cleaned_taxon_search_expected = (self.species.id, None, self.species.id, 'genus species', 'auteur7', 'Espèce', None, 'Absent', 'Marin',
                                         None, None, None, 'Une remarque', 'Une source', 'Une description de reference')
        self.assertEqual(cleaned_taxon_search_expected, cleaned_taxon_search_output)
        cleaned_taxon_search_output = construct_cleaned_taxon_search(self.species_syn, cleaned_data)
        cleaned_taxon_search_expected = (self.species_syn.id, None, self.species.id, 'species_synonymous', 'auteur9', 'Espèce', None, None, None, None,
                                         None, None, None, None, None)
        self.assertEqual(cleaned_taxon_search_expected, cleaned_taxon_search_output)

    def test_get_search_results_auteur_by_species(self):
        result_output = get_search_results_auteur_by_species('auteur7')
        result_expected = ([[self.species, [[self.sub_species, None]]]], 1)
        self.assertEqual(result_expected, result_output)

        self.genus.delete()
        self.species.id_sup = None
        self.species.save()
        result_output = get_search_results_auteur_by_species('auteur6')
        result_expected = ('Aucun résultat trouvé.', 0)
        self.assertEqual(result_expected, result_output)

    def test_get_taxons_for_sample(self):
        list_param = None
        list_taxon_output = get_taxons_for_sample(list_param)
        list_taxon_expected = [('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece',
                                'sous-espece', 'auteur(s)/date', 'date', 'collecteurs', 'identificateur',
                                "date d'identification", 'altitude(m)', 'pays', 'region', 'commune', 'lieu dit',
                                'type de milieu', 'nombre', 'sexe', 'capture/relacher', 'informations complementaires',
                                'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc'),
                               (self.classe.id, '', '', '', '', '', '', '', 'auteur3'),
                               (self.family.id, 'order', 'family', '', '', '', '', '', 'auteur5'),
                               (self.genus.id, 'order', 'family', '', 'genus', '', '', '', 'auteur6'),
                               (self.species.id, 'order', 'family', '', 'genus', '', 'genus species', '', 'auteur7'),
                               (self.sub_species.id, 'order', 'family', '', 'genus', '', 'genus species', 'genus species sub_species',
                                'auteur8'),
                               (self.kingdom.id, None, None, None, None, None, None, None, 'auteur1'),
                               (self.order.id, 'order', '', '', '', '', '', '', 'auteur4'),
                               (self.phylum.id, '', '', '', '', '', '', '', 'auteur2'),
                               (self.species_syn.id, None, None, None, None, None, None, None, 'auteur9')]
        self.assertEqual(list_taxon_expected, list_taxon_output)

        list_param = {'q': 'genus species'}
        list_taxon_output = get_taxons_for_sample(list_param)
        list_taxon_expected = [('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece',
                                'sous-espece', 'auteur(s)/date', 'date', 'collecteurs', 'identificateur',
                                "date d'identification", 'altitude(m)', 'pays', 'region', 'commune', 'lieu dit',
                                'type de milieu', 'nombre', 'sexe', 'capture/relacher', 'informations complementaires',
                                'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc'),
                               (self.species.id, 'order', 'family', '', 'genus', '', 'genus species', '', 'auteur7'),
                               (self.sub_species.id, 'order', 'family', '', 'genus', '', 'genus species', 'genus species sub_species',
                                'auteur8')]
        self.assertEqual(list_taxon_expected, list_taxon_output)

    def test_constr_hierarchy_tree_adv_search(self):
        html_hierarchy_output, nb_output = constr_hierarchy_tree_adv_search(self.species, None)
        html_hierarchy_expected = """<ul class="tree"><br/><al><al><al><al><al><al><al>
    <li><label class="tree_label" for="c1">
            <strong>Regne : </strong></al><a href="/fatercal/taxon/"""+ str(self.kingdom.id) +"""/">kingdom auteur1</a>
            <ul><li><label class="tree_label" for="c2">
            <strong>Phylum : </strong></al><a href="/fatercal/taxon/"""+ str(self.phylum.id) +"""/">phylum auteur2</a>
            <ul><li><label class="tree_label" for="c3">
            <strong>Classe : </strong></al><a href="/fatercal/taxon/"""+ str(self.classe.id) +"""/">classe auteur3</a>
            <ul><li><label class="tree_label" for="c4">
            <strong>Ordre : </strong></al><a href="/fatercal/taxon/"""+ str(self.order.id) +"""/">order auteur4</a>
            <ul><li><label class="tree_label" for="c5">
            <strong>Famille : </strong></al><a href="/fatercal/taxon/"""+ str(self.family.id) +"""/">family auteur5</a>
            <ul><li><label class="tree_label" for="c6">
            <strong>Genre : </strong></al><a href="/fatercal/taxon/"""+ str(self.genus.id) +"""/">genus auteur6</a>
            <ul><li class="folder"><label><strong>Espèce :</strong> genus species auteur7</li>
        <ul><li><al><label class="tree_label" for="c7"/><strong>Sous-Espèce : </strong></al>
        <a href="/fatercal/taxon/"""+ str(self.sub_species.id) +"""/">genus species sub_species auteur8</a></li></ul></ul></ul></li>"""
        self.maxDiff = None
        self.assertEqual(html_hierarchy_expected, html_hierarchy_output)
        self.assertEqual(nb_output, 1)

        html_hierarchy_output, nb_output = constr_hierarchy_tree_adv_search(None, 'auteur7')
        html_hierarchy_expected = """<div><ul class="tree"><br/><al><al><al><al><al><al><al>
    <li><label class="tree_label" for="c1">
            <strong>Regne : </strong></al><a href="/fatercal/taxon/"""+ str(self.kingdom.id) +"""/">kingdom auteur1</a>
            <ul><li><label class="tree_label" for="c2">
            <strong>Phylum : </strong></al><a href="/fatercal/taxon/"""+ str(self.phylum.id) +"""/">phylum auteur2</a>
            <ul><li><label class="tree_label" for="c3">
            <strong>Classe : </strong></al><a href="/fatercal/taxon/"""+ str(self.classe.id) +"""/">classe auteur3</a>
            <ul><li><label class="tree_label" for="c4">
            <strong>Ordre : </strong></al><a href="/fatercal/taxon/"""+ str(self.order.id) +"""/">order auteur4</a>
            <ul><li><label class="tree_label" for="c5">
            <strong>Famille : </strong></al><a href="/fatercal/taxon/"""+ str(self.family.id) +"""/">family auteur5</a>
            <ul><li><label class="tree_label" for="c6">
            <strong>Genre : </strong></al><a href="/fatercal/taxon/"""+ str(self.genus.id) +"""/">genus auteur6</a>
            <ul><li class="folder"><label><strong>Espèce :</strong> genus species auteur7</li>
        <ul><li><al><label class="tree_label" for="c7"/><strong>Sous-Espèce : </strong></al>
        <a href="/fatercal/taxon/"""+ str(self.sub_species.id) +"""/">genus species sub_species auteur8</a></li></ul></ul></ul></li></div>"""
        self.assertEqual(html_hierarchy_expected, html_hierarchy_output)
        self.assertEqual(nb_output, 2)

    def test_constr_hierarchy_tree_branch_parents(self):
        list_hierarchy, nb = self.species.get_hierarchy()
        html_hierarchy_start_output, html_hierarchy_end_output = constr_hierarchy_tree_branch_parents(list_hierarchy)
        html_hierarchy_start_expected = """<ul class="tree"><br/><al><al><al><al><al><al><al>
            <li><label class="tree_label" for="c1">
            <strong>Regne : </strong></al><a href="/fatercal/taxon/"""+ str(self.kingdom.id) +"""/">kingdom auteur1</a>
            <ul><li><label class="tree_label" for="c2">
            <strong>Phylum : </strong></al><a href="/fatercal/taxon/"""+ str(self.phylum.id) +"""/">phylum auteur2</a>
            <ul><li><label class="tree_label" for="c3">
            <strong>Classe : </strong></al><a href="/fatercal/taxon/"""+ str(self.classe.id) +"""/">classe auteur3</a>
            <ul><li><label class="tree_label" for="c4">
            <strong>Ordre : </strong></al><a href="/fatercal/taxon/"""+ str(self.order.id) +"""/">order auteur4</a>
            <ul><li><label class="tree_label" for="c5">
            <strong>Famille : </strong></al><a href="/fatercal/taxon/"""+ str(self.family.id) +"""/">family auteur5</a>
            <ul><li><label class="tree_label" for="c6">
            <strong>Genre : </strong></al><a href="/fatercal/taxon/"""+ str(self.genus.id) +"""/">genus auteur6</a>
            <ul>"""
        self.assertHTMLEqual(html_hierarchy_start_expected, html_hierarchy_start_output)
        html_hierarchy_end_expected = "</ul></li></ul></li></ul></li></ul></li></ul></li></ul></li></ul>"
        self.assertEqual(html_hierarchy_end_expected, html_hierarchy_end_output)

    def test_contr_hierarchy_tree_branch_adv_search_child(self):
        list_taxon, nb = get_child_of_child(self.species)
        hierarchy_child_output = constr_hierarchy_tree_branch_adv_search_child(list_taxon[1], nb, '')
        hierarchy_child_expected = """<ul><li><al><label class="tree_label" for="c1"/><strong>Sous-Espèce : </strong>
        </al><a href="/fatercal/taxon/"""+ str(self.sub_species.id) +"""/">genus species sub_species auteur8</a></li></ul>"""
        self.assertHTMLEqual(hierarchy_child_expected, hierarchy_child_output)

    def test_constr_hierarchy_tree_branch_child(self):
        list_hierarchy, nb = self.species.get_hierarchy()
        list_child = Taxon.objects.filter(id_sup=self.species.id).order_by('rang')
        str_child_output = constr_hierarchy_tree_branch_child(list_child, nb)
        str_child_expected = """<ul><li><label class="tree_label" for="c7"/><strong>Sous-Espèce : </strong><ul>
        <li><a href="/fatercal/taxon/"""+ str(self.sub_species.id) +"""/">genus species sub_species auteur8</a></li>"""
        self.assertHTMLEqual(str_child_expected, str_child_output)

    def test_get_taxon_adv_search(self):
        list_taxon_output = get_taxon_adv_search(self.species.id, None)
        list_taxon_expected = [
            ('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece', 'sous-espece',
             'auteur(s)/date', 'date', 'collecteurs', 'identificateur', "date d'identification", 'altitude(m)',
             'pays', 'region', 'commune', 'lieu dit', 'type de milieu', 'nombre', 'sexe', 'capture/relacher',
             'informations complementaires', 'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc'),
            (self.species.id, 'order', 'family', '', 'genus', '', 'genus species', '', 'auteur7'),
            (self.sub_species.id, None, 'order', 'family', '', 'genus', '', 'genus species', 'genus species sub_species', 'auteur8')]
        self.assertEqual(list_taxon_expected, list_taxon_output)

        auteur = 'not found'
        list_taxon_output = get_taxon_adv_search(None, auteur)
        list_taxon_expected = [
            ('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece', 'sous-espece',
             'auteur(s)/date', 'date', 'collecteurs', 'identificateur', "date d'identification", 'altitude(m)', 'pays',
             'region', 'commune', 'lieu dit', 'type de milieu', 'nombre', 'sexe', 'capture/relacher',
             'informations complementaires', 'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc')]
        self.assertEqual(list_taxon_expected, list_taxon_output)

        auteur = 'auteur7'
        list_taxon_output = get_taxon_adv_search(None, auteur)
        list_taxon_expected = [
            ('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece', 'sous-espece',
             'auteur(s)/date', 'date', 'collecteurs', 'identificateur', "date d'identification", 'altitude(m)', 'pays',
             'region', 'commune', 'lieu dit', 'type de milieu', 'nombre', 'sexe', 'capture/relacher',
             'informations complementaires', 'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc'),
            (self.species.id, None, 'order', 'family', '', 'genus', '', 'genus species', '', 'auteur7'),
            (self.sub_species.id, None, 'order', 'family', '', 'genus', '', 'genus species', 'genus species sub_species', 'auteur8')]
        self.assertEqual(list_taxon_expected, list_taxon_output)

    def test_format_adv_search_child_for_export_sample(self):
        list_taxon = [
            ('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece',
             'sous-espece', 'auteur(s)/date', 'date', 'collecteurs', 'identificateur', "date d'identification",
             'altitude(m)', 'pays', 'region', 'commune', 'lieu dit', 'type de milieu', 'nombre', 'sexe',
             'capture/relacher', 'informations complementaires', 'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc')
        ]
        list_child_taxon, count_es = get_child_of_child(self.species)
        list_taxon_ouput = format_adv_search_child_for_export_sample(list_child_taxon[1], list_taxon)
        list_taxon_expected = [
            ('id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece', 'sous-espece',
             'auteur(s)/date', 'date', 'collecteurs', 'identificateur', "date d'identification", 'altitude(m)', 'pays',
             'region', 'commune', 'lieu dit', 'type de milieu', 'nombre', 'sexe', 'capture/relacher',
             'informations complementaires', 'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc'),
            (self.sub_species.id, None, 'order', 'family', '', 'genus', '', 'genus species', 'genus species sub_species', 'auteur8')]
        self.assertEqual(list_taxon_expected, list_taxon_ouput)
    
    def test_get_taxref_update(self):
        self.maxDiff = 800
        status = TaxrefStatus.objects.create(status="P", lb_status="Présent")
        habitat = TaxrefHabitat.objects.create(habitat=2, lb_habitat="Terrestre")
        self.species.cd_nom=1
        self.species.cd_ref=1
        self.species.cd_sup=2
        self.genus.cd_nom= 2
        self.genus.save()
        self.species.save()
        taxon_taxref = TaxrefUpdate.objects.create(
            taxon_id=self.species, cd_nom=1,
            cd_ref=1, cd_sup=2, rang='ES',
            lb_nom='different_name', lb_auteur='different author',
            nom_complet='different_name different author',
            date=datetime.datetime.now(),
            taxref_version='11'
        )
        empty, taxref_version, count = get_taxref_update()
        taxref_version_expected = "11"
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species)
        nom_complet_expected = "different_name different author: Le nom du taxon est différent. "\
            "Nom Chez Fatercal: genus species, Chez taxref: different_name. Le nom de l'auteur de "\
            "ce taxon est différent. Auteur Chez Fatercal: auteur7, Chez taxref: different author. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        self.genus.cd_nom = None
        self.genus.save()
        taxon_taxref.habitat = None
        taxon_taxref.nc = None
        taxon_taxref.lb_nom = 'genus species'
        taxon_taxref.lb_auteur = 'auteur7'
        taxon_taxref.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species)
        nom_complet_expected = "genus species auteur7: Le supérieur de ce taxon "\
            "est différent et celui de Fatercal n'existe pas chez Taxref. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        self.genus.cd_nom = 2
        self.genus.save()
        self.species.id_sup=None
        self.species.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species)
        nom_complet_expected = "genus species auteur7: Ce taxon n'a pas de supérieur "\
            "dans fatercal et Taxref lui en a assigné un Supérieur chez Taxref: genus auteur6"
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        self.genus.cd_nom = None
        self.genus.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species)
        nom_complet_expected = "genus species auteur7: Ce taxon n'a pas de supérieur dans fatercal "\
            "et Taxref lui en a assigné un mais il n'exist pas chez fatercal. Cd_nom supérieur chez Taxref: 2"
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        self.species.id_sup = self.genus
        taxon_taxref.cd_sup = None
        taxon_taxref.cd_ref = 3
        self.species_syn.cd_nom = 3
        self.species.save()
        self.species_syn.save()
        taxon_taxref.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species)
        nom_complet_expected = "genus species auteur7: Le taxon est valide "\
            "chez fatercal mais synonyme chez Taxref. Taxon référent chez Taxref: species_synonymous auteur9 (Non Valide)"
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        self.species_syn.cd_nom = None
        self.species_syn.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species)
        nom_complet_expected = "genus species auteur7: Le taxon est valide chez fatercal "\
            "mais synonyme chez Taxrefet n'éxiste pas chez Fatercal. Cd_nom taxon référent chez Taxref: 3."
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        self.species.cd_nom = None
        self.species.save()
        self.species_syn.cd_nom = 1
        self.species_syn.save()
        taxon_taxref.taxon_id = self.species_syn
        taxon_taxref.cd_ref = 3
        taxon_taxref.lb_nom = "species_synonymous"
        taxon_taxref.lb_auteur = "auteur9"
        taxon_taxref.save()
        self.genus.cd_nom = 2
        self.genus.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Le référent de ce taxon est différent "\
            "et celui de Fatercal n'existe pas chez Taxref. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        self.species.cd_nom = 3
        self.species.save()
        taxon_taxref.cd_sup = 2
        taxon_taxref.cd_ref = 1
        taxon_taxref.save()
        self.genus.cd_nom = None
        self.genus.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Le taxon est synonyme chez fatercal "\
            "mais valide chez Taxref mais le taxon supérieur n'existe pas chez Fatercal Cd_nom taxon "\
                "supérieur chez Taxref: 2. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        self.genus.cd_nom = 2
        self.genus.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Le taxon est synonyme "\
            "chez fatercal mais valide chez Taxref. Supérieur chez Taxref: genus auteur6. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        taxon_taxref.cd_ref = 4
        taxon_taxref.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Le référent de ce taxon "\
            "est différent et n'existe pas dans Fatercal. CD_NOM = 4. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        self.sub_species.cd_nom = 4
        self.sub_species.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Le référent de ce taxon est différent. "\
            "Référent chez fatercal: genus species auteur7, chez Taxref genus species sub_species auteur8. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        taxon_taxref.cd_ref = 3
        taxon_taxref.rang = "NEIF"
        taxon_taxref.habitat = 154
        taxon_taxref.nc = "NEIF"
        taxon_taxref.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Le rang est différent et n'existe pas "\
            "chez Fatercal. Nouveau rang: NEIF. Un habitat a été spécifié pour ce taxon mais il n'existe pas chez fatercal. Nouvelle habitat: 154. Un status a été spécifié pour ce taxon mais il n'existe pas chez fatercal. Nouveau Status: NEIF. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        taxon_taxref.rang = "ES"
        taxon_taxref.save()
        self.species_syn.nc = TaxrefStatus.objects.get(status="A")
        self.species_syn.habitat = TaxrefHabitat.objects.get(habitat=1)
        self.species_syn.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: L'habitat est différent "\
            "et n'existe pas chez Fatercal. Nouvelle Habitat: 154. Le status est différent "\
            "et n'existe pas chez Fatercal. Nouveau Status: NEIF"
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])
        
        taxon_taxref.nc = "P"
        taxon_taxref.habitat = 2
        taxon_taxref.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: L'habitat est différent. "\
            "Nouvelle Habitat: Terrestre. Le status est différent. Nouveau Status: Présent"
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        self.species_syn.nc = None
        self.species_syn.habitat = None
        self.species_syn.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Un habitat a été spécifié pour ce taxon. "\
            "Nouvelle Habitat: Terrestre. Un status a été spécifié pour ce taxon. Nouveau Status: Présent. "
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        taxon_taxref.nc = None
        taxon_taxref.habitat = None
        self.species_syn.save()
        taxon_taxref.save()
        empty, taxref_version, count = get_taxref_update()
        taxon_taxref = TaxrefUpdate.objects.get(taxon_id=self.species_syn)
        nom_complet_expected = "species_synonymous auteur9: Aucune différence mais des "\
            "identifiant venant de Taxref était manquant."
        self.assertEqual(nom_complet_expected, taxon_taxref.nom_complet)
        self.assertEqual(empty, False)
        self.assertEqual(count, 1)
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

    def test_get_taxref_insert(self):
        status = TaxrefStatus.objects.create(status="P", lb_status="Présent")
        habitat = TaxrefHabitat.objects.create(habitat=2, lb_habitat="Terrestre")
        taxon_taxref = TaxrefUpdate.objects.create(
            cd_nom=1, cd_ref=1, cd_sup=2, rang='UN',
            lb_nom='new taxon', lb_auteur='author',
            nom_complet='new taxon author',
            date=datetime.datetime.now(),
            taxref_version='11', nc='unkn', habitat=6
        )
        exist, exist_rang, nb_taxon, taxref_version = get_taxref_insert('ES')
        taxref_version_expected = "11"
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

        taxon_taxref.lb_auteur = None
        taxon_taxref.cd_sup = None
        taxon_taxref.cd_ref = 2
        taxon_taxref.nc = None
        taxon_taxref.habitat = None
        taxon_taxref.rang = 'ES'
        taxon_taxref.save()
        exist, exist_rang, nb_taxon, taxref_version = get_taxref_insert('ES')
        self.assertEqual(taxref_version_expected, taxref_version['taxref_version__max'])

    def test_insert_taxon_from_taxref(self):
        status = TaxrefStatus.objects.create(status="P", lb_status="Présent")
        habitat = TaxrefHabitat.objects.create(habitat=2, lb_habitat="Terrestre")
        taxon_taxref = TaxrefUpdate.objects.create(
            cd_nom=1, cd_ref=1, cd_sup=2, rang='UN',
            lb_nom='new taxon', lb_auteur='author',
            nom_complet='new taxon author',
            date=datetime.datetime.now(),
            taxref_version='11', nc='unkn', habitat=6
        )
        data = {
            'choices': [taxon_taxref],
            'time': datetime.datetime.now(),
            'count': 7
        }
        taxref_version = {'taxref_version__max': 11}
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        list_not_insert = insert_taxon_from_taxref(data, taxref_version, user)
        list_not_insert_expected = [{'name': 'new taxon:', 'info': 'Rang taxon: UN'}]
        self.assertEqual(list_not_insert_expected, list_not_insert)
        self.assertEqual(False, Taxon.objects.filter(lb_nom='new taxon').exists())
        self.assertEqual(False, TaxrefUpdate.objects.filter(cd_nom=1).exists())

        taxon_taxref.rang = 'ES'
        taxon_taxref.save()
        self.genus.cd_nom = 2
        self.genus.save()
        list_not_insert = insert_taxon_from_taxref(data, taxref_version, user)
        list_not_insert_expected = []
        self.assertEqual(list_not_insert_expected, list_not_insert)
        self.assertEqual(True, Taxon.objects.filter(cd_nom=1).exists())
        self.assertEqual(False, TaxrefUpdate.objects.filter(cd_nom=1).exists())

    def test_update_taxon_from_taxref(self):
        status = TaxrefStatus.objects.create(status="P", lb_status="Présent")
        habitat = TaxrefHabitat.objects.create(habitat=2, lb_habitat="Terrestre")
        time = datetime.datetime.now()
        self.species.cd_nom=1
        self.species.cd_ref=1
        self.species.cd_sup=2
        self.species_syn.cd_nom = 4
        self.genus.cd_nom= 2
        self.genus.save()
        self.species.save()
        self.species_syn.save()
        taxon_taxref = TaxrefUpdate.objects.create(
            taxon_id=self.species, cd_nom=1,
            cd_ref=1, cd_sup=2, rang='ES',
            lb_nom='different name', lb_auteur='different author',
            nom_complet='different_name different author',
            nc="P",
            habitat=2,
            date=datetime.datetime.now(),
            taxref_version='11'
        )
        taxon_taxref_syn = TaxrefUpdate.objects.create(
            taxon_id=self.species_syn, cd_nom=4,
            cd_ref=4, cd_sup=2, rang='ES',
            lb_nom='syn_name', lb_auteur='syn_author',
            nom_complet='syn_name syn_author',
            date=datetime.datetime.now(),
            taxref_version='11'
        )
        id_taxon = taxon_taxref.id
        id_taxon_syn = taxon_taxref_syn.id
        data = {
            'choices': TaxrefUpdate.objects.filter(id=id_taxon),
            'time': time
        }
        taxref_version = {'taxref_version__max': 11}
        update_taxon_from_taxref(data, taxref_version, "dummy_user")
        TaxrefUpdate.objects.filter(id=id_taxon)
        self.species = Taxon.objects.get(id=self.species.id)
        self.species_syn = Taxon.objects.get(id=self.species_syn.id)
        self.assertEqual(self.species.lb_nom, 'different name')
        self.assertEqual(self.species.lb_auteur, 'different author')
        self.assertEqual(self.species.taxref_version, 11)
        self.assertEqual(habitat, self.species.habitat)
        self.assertEqual(status, self.species.nc)
        self.assertEqual(TaxrefUpdate.objects.filter(id=id_taxon).exists(), False)
        self.assertEqual(TaxrefUpdate.objects.filter(id=id_taxon_syn).exists(), False)
        self.assertEqual(self.species_syn.source, 'Fatercal')
        self.assertEqual(self.species_syn.utilisateur, 'dummy_user')
        self.assertEqual(self.species_syn.taxref_version, 11)
        self.assertEqual(self.species.source, 'Taxref')
        self.assertEqual(self.species.utilisateur, 'dummy_user')
        self.assertEqual(self.species.taxref_version, 11)

        taxon_taxref.cd_ref = 4
        taxon_taxref.cd_sup = None
        taxon_taxref.save()
        taxon_taxref_syn.save()
        self.species_syn.cd_nom = 4
        self.species_syn.save()
        data = {
            'choices': TaxrefUpdate.objects.all(),
            'time': datetime.datetime.now()
        }
        update_taxon_from_taxref(data, taxref_version, "dummy_user")
        self.species = Taxon.objects.get(id=self.species.id)
        self.species_syn = Taxon.objects.get(id=self.species_syn.id)
        self.sub_species = Taxon.objects.get(id=self.sub_species.id)
        self.assertEqual(self.sub_species.id_sup, self.species_syn)
        self.assertEqual(self.species.id_ref, self.species_syn)
        self.assertEqual(self.species_syn.id_ref, self.species_syn)
        self.assertEqual(self.species_syn.id_sup, self.genus)

    def test_next_taxref_insert_page(self):
        taxon_taxref = TaxrefUpdate.objects.create(
            cd_nom=1, cd_ref=1, cd_sup=2, rang='UN',
            lb_nom='new taxon', lb_auteur='author',
            nom_complet='new taxon author',
            date=datetime.datetime.now(),
            taxref_version='11', nc='unkn', habitat=6
        )
        template, context = next_taxref_insert_page(None, True)
        context_expected = {'error': True, 'goal': 'insert'}
        self.assertEqual(context_expected, context)
        
        form = ChooseTaxonToInsert(
            initial = {
                'count': 1,
                'time': datetime.datetime.now(),
            }
        )
        form.cleaned_data = {'count': 0, 'time': datetime.datetime.now()}
        template, context = next_taxref_insert_page(form, False)
        context_expected = {'nb_taxon': 0, 'exist': True,'exist_rang': False,
            'rang': TaxrefRang.objects.get(rang=list_hierarchy[1]).lb_rang}
        self.assertEqual(context_expected['exist'], context['exist'])
        self.assertEqual(context_expected['exist_rang'], context['exist_rang'])
        self.assertEqual(context_expected['rang'], context['rang'])
        self.assertEqual(context_expected['nb_taxon'], context['nb_taxon'])

        form.cleaned_data['count'] = 10
        template, context = next_taxref_insert_page(form, False)
        context_expected['rang'] = 'other'
        context_expected['nb_taxon'] = 1
        self.assertEqual(context_expected['exist'], context['exist'])
        self.assertEqual(context_expected['exist_rang'], context['exist_rang'])
        self.assertEqual(context_expected['rang'], context['rang'])
        self.assertEqual(context_expected['nb_taxon'], context['nb_taxon'])

        form.cleaned_data['count'] = -1
        template, context = next_taxref_insert_page(form, False)
        context_expected = {'error': False, 'goal': 'insert'}
        self.assertEqual(context_expected, context)
        

# Test function that are related to the model Prelevement
class SampleTestClass(TestCase):
    def setUp(self):
        self.species = Taxon.objects.create(id=1, lb_nom="species", lb_auteur="auteur1",
                                            rang=TaxrefRang.objects.create(rang='ES', lb_rang='Espece'))
        self.sample = Prelevement.objects.create(id_prelevement=10, id_taxon=self.species)
        Recolteur.objects.create(id_prelevement=self.sample, lb_auteur="auteur")
        self.species.id_ref = self.species
        self.species.save()

    def test_get_haverster(self):
        harvester_real = Recolteur.objects.get(lb_auteur="auteur")
        harvester_found = get_recolteur(self.sample)
        self.assertEqual(harvester_real.lb_auteur, harvester_found)

        harvester_real.delete()
        harvester_found = get_recolteur(self.sample)
        self.assertEqual(harvester_found, "Récolteur inconnu")

    def test_get_loc_from_sample(self):
        pays = Localisation.objects.create(nom='country', loc_type=TypeLoc.objects.create(type='pays'))
        region = Localisation.objects.create(nom='regions', loc_type=TypeLoc.objects.create(type='region'), id_sup=pays)
        ville = Localisation.objects.create(nom='town', loc_type=TypeLoc.objects.create(type='ville'), id_sup=region)
        self.assertEqual(get_loc_from_sample(self.sample), {})

        self.sample.id_loc = ville
        dict_loc_output = get_loc_from_sample(self.sample)
        dict_loc_expected = {
            'region': 'regions',
            'ville': 'town',
            'pays': 'country'
        }
        self.assertEqual(dict_loc_output, dict_loc_expected)

    def test_format_altitude_sample(self):
        self.sample.altitude_max = 2
        self.sample.save()
        self.assertEqual(format_altitude_sample(self.sample), 2)

        self.sample.altitude_max = None
        self.sample.altitude_min = 1
        self.sample.save()
        self.assertEqual(format_altitude_sample(self.sample), 1)

        self.sample.altitude_max = 2
        self.sample.save()
        self.assertEqual(format_altitude_sample(self.sample), '1-2')

    def test_verify_sample(self):
        TypeEnregistrement.objects.create(lb_type='pays')
        line = {
            'id_taxon': '56',
            'altitude(m)': '1',
            'nombre': '2'
        }
        result_output = verify_sample(line, 1)
        result_expected = {
            'good': False,
            'message': 'Une erreur à été perçue à la ligne 1. L\'ID du taxon entrée n\'existe pas.'
        }
        self.assertEqual(result_expected, result_output)

        line['id_taxon'] = '1'
        line['capture/relacher'] = None
        result_expected['message'] = 'Une erreur à été perçue à la ligne 1. Le type d\'enregistrement ' \
                                     'dans le champ capture/relacher n\'existe pas ou n\'est pas renseigné.'
        result_output = verify_sample(line, 1)
        self.assertEqual(result_expected, result_output)

        line['capture/relacher'] = 'pays'
        line['x wgs 84'] = None
        line['y wgs 84'] = None
        result_expected['message'] = 'Une erreur à été perçue à la ligne 1. Les coordonnées pour ce prélèvements ' \
                                     'ne sont pas présentes.'
        result_output = verify_sample(line, 1)
        self.assertEqual(result_expected, result_output)

        line['x wgs 84'] = 'sduifsefh'
        line['y wgs 84'] = '12'
        result_expected['message'] = 'Une erreur à été perçue à la ligne 1. ' \
                                     'L\'un des nombres sur cette ligne contient des lettres'
        result_output = verify_sample(line, 1)

        self.assertEqual(result_expected, result_output)

        line['x wgs 84'] = '11'
        line['date'] = '2019-120'
        result_expected['message'] = 'Une erreur à été perçue à la ligne 1. ' \
                                     'La date entrée n\'est pas au bon format.'
        result_output = verify_sample(line, 1)
        self.assertEqual(result_expected, result_output)

        line['date'] = None
        result_expected['good'] = True
        result_expected['message'] = 'Une erreur à été perçue à la ligne 1.'
        result_output = verify_sample(line, 1)
        self.assertEqual(result_expected, result_output)

        line['date'] = '2019-03-19'
        result_output = verify_sample(line, 1)
        self.assertEqual(result_expected, result_output)

    def test_save_all_sample(self):
        species = Taxon.objects.create(id=2, lb_nom="species_test", lb_auteur="auteur1",
                                       rang=TaxrefRang.objects.get(rang='ES'))
        sample = Prelevement(id_taxon=species)
        pays = Localisation(nom='country', loc_type=TypeLoc.objects.create(type='pays'))
        region = Localisation(nom='regions', loc_type=TypeLoc.objects.create(type='region'))
        secteur = Localisation(nom='secteur', loc_type=TypeLoc.objects.create(type='secteur'))
        nom = Localisation(nom='nom', loc_type=TypeLoc.objects.create(type='nom'))
        line = {
            'sample': sample,
            'loc': {
                'pays': pays,
                'region': region,
                'secteur': secteur,
                'nom': nom
            },
            'habitat': None,
            'list_harvester': ()
        }
        list_sample = [line]
        save_all_sample(list_sample)
        self.assertTrue(Prelevement.objects.filter(id_taxon=species).exists())
        self.assertEqual(Localisation.objects.get(nom='country'), pays)
        self.assertEqual(Localisation.objects.get(nom='regions'), region)
        self.assertEqual(Localisation.objects.get(nom='secteur'), secteur)
        self.assertEqual(Localisation.objects.get(nom='nom'), nom)
        self.assertEqual(sample.id_loc, nom)

        region.delete()
        region.id_sup = pays
        secteur.delete()
        nom.delete()
        line['loc']['pays'] = None
        line['loc']['region'] = region
        line['habitat'] = HabitatDetail.objects.create(nom='habitat')
        line['list_harvester'] = (Recolteur(lb_auteur='harvester'),)
        save_all_sample(list_sample)
        self.assertEqual(Localisation.objects.get(nom='regions'), region)
        self.assertEqual(Localisation.objects.get(nom='secteur'), secteur)
        self.assertEqual(Localisation.objects.get(nom='nom'), nom)

        secteur.delete()
        nom.delete()
        secteur.id_sup = region
        line['loc']['region'] = None
        line['loc']['secteur'] = secteur
        save_all_sample(list_sample)
        self.assertEqual(Localisation.objects.get(nom='secteur'), secteur)
        self.assertEqual(Localisation.objects.get(nom='nom'), nom)

        nom.delete()
        nom.id_sup = secteur
        line['loc']['secteur'] = None
        line['loc']['nom'] = nom
        save_all_sample(list_sample)
        self.assertEqual(Localisation.objects.get(nom='nom'), nom)

    def test_get_sample(self):
        list_sample_output = get_sample(None)
        list_sample_expected = [('Code identification', 'Ordre', 'Famille', 'Sous-Famille', 'Genre', 'Sous-Genre',
                                 'Espece', 'Sous-Espece', 'Auteur(s)/date', 'Date', 'Collecteurs', 'Identificateur',
                                 "Date d'identification", 'Altitude(m)', 'Pays', 'Region', 'Commune', 'Lieu dit',
                                 'Type de milieu', 'Nombre', 'Sexe', 'Capture/relacher',
                                 'Informations complémentaires', 'Photo', 'X WGS 84', 'Y WGS 84', 'X RGNC', 'Y RGNC'),
                                (10, None, None, None, None, None, None, None, 'auteur1', None, 'auteur', None, None,
                                 None, None, None, None, None, None, None, None, None, None, None, None, None)]
        self.assertEqual(list_sample_expected, list_sample_output)

        list_param = {'q': 'None Found'}
        list_sample_output = get_sample(list_param)
        list_sample_expected = [('Code identification', 'Ordre', 'Famille', 'Sous-Famille', 'Genre', 'Sous-Genre',
                                 'Espece', 'Sous-Espece', 'Auteur(s)/date', 'Date', 'Collecteurs', 'Identificateur',
                                 "Date d'identification", 'Altitude(m)', 'Pays', 'Region', 'Commune', 'Lieu dit',
                                 'Type de milieu', 'Nombre', 'Sexe', 'Capture/relacher',
                                 'Informations complémentaires', 'Photo', 'X WGS 84', 'Y WGS 84', 'X RGNC', 'Y RGNC')]
        self.assertEqual(list_sample_expected, list_sample_output)

    def test_get_specific_sample_search(self):
        list_param = None
        list_not_proper = get_specific_search_sample(list_param)
        self.assertEqual(list_not_proper.count(), 1)

        list_param = {'q': 'species'}
        list_not_proper = get_specific_search_sample(list_param)
        self.assertEqual(list_not_proper.first(), self.sample)

    def test_construct_sample(self):
        pays = Localisation.objects.create(nom='country', loc_type=TypeLoc.objects.create(type='pays'))
        region = Localisation.objects.create(nom='regions', loc_type=TypeLoc.objects.create(type='region'), id_sup=pays)
        ville = Localisation.objects.create(nom='town', loc_type=TypeLoc.objects.create(type='ville'), id_sup=region)
        nom = Localisation.objects.create(nom='nom', loc_type=TypeLoc.objects.create(type='nom'), id_sup=ville)
        typeEn = TypeEnregistrement.objects.create(lb_type='type')
        HabitatDetail.objects.create(nom="habitat")
        line = {
            'id_taxon': 1,
            'pays': 'country',
            'region': 'regions',
            'commune': 'town',
            'lieu dit': 'nom',
            'x wgs 84': '1',
            'y wgs 84': '2',
            'altitude(m)': '10',
            'nombre': '0',
            'sexe': 'male',
            'date': '2018',
            'informations complementaires': '',
            'collecteurs': '',
            'capture/relacher': 'type',
            'type de milieu': 'habitat',
        }
        habitat = HabitatDetail.objects.get(nom="habitat")
        result_expected = {
            'loc': {
                'pays': None,
                'region': None,
                'secteur': None,
                'nom': nom
            },
            'list_harvester': [],
            'habitat': habitat
        }
        sample = Prelevement(id_taxon=self.species, nb_taxon_present=0, type_specimen=line['sexe'],
                             type_enregistrement=typeEn, date='2018', information_complementaire='', toponymie_x=1,
                             toponymie_y=2, gps=True, altitude_min=10, altitude_max=None)
        try:
            result_output = construct_sample(line, 1)
            self.assertEqual(result_expected['loc'], result_output['loc'])
            self.assertEqual(result_expected['habitat'], result_output['habitat'])
            self.assertEqual(result_expected['list_harvester'], result_output['list_harvester'])
            self.assertEqual(sample.id_taxon, result_output['sample'].id_taxon)
            self.assertEqual(sample.nb_taxon_present, result_output['sample'].nb_taxon_present)
            self.assertEqual(sample.type_specimen, result_output['sample'].type_specimen)
            self.assertEqual(sample.type_enregistrement, result_output['sample'].type_enregistrement)
            self.assertEqual(sample.date, result_output['sample'].date)
            self.assertEqual(sample.information_complementaire, result_output['sample'].information_complementaire)
            self.assertEqual(sample.toponymie_x, result_output['sample'].toponymie_x)
            self.assertEqual(sample.toponymie_y, result_output['sample'].toponymie_y)
            self.assertEqual(sample.gps, result_output['sample'].gps)
            self.assertEqual(sample.altitude_min, result_output['sample'].altitude_min)
            self.assertEqual(sample.altitude_max, result_output['sample'].altitude_max)
        except NotGoodSample:
            self.fail("La localisation n'est pas renseignée.")
        line['type de milieu'] = None
        result_expected['habitat'] = None
        result_output = construct_sample(line, 1)
        self.assertEqual(result_expected['habitat'], result_output['habitat'])

        line['pays'] = None
        line['region'] = None
        line['commune'] = None
        line['lieu dit'] = None
        try:
            construct_sample(line, 1)
            self.fail("La localisation est pas renseignée.")
        except NotGoodSample:
            pass

    def test_verify_and_save_sample(self):
        pays = Localisation.objects.create(nom='country', loc_type=TypeLoc.objects.create(type='pays'))
        region = Localisation.objects.create(nom='regions', loc_type=TypeLoc.objects.create(type='region'), id_sup=pays)
        ville = Localisation.objects.create(nom='town', loc_type=TypeLoc.objects.create(type='ville'), id_sup=region)
        Localisation.objects.create(nom='nom', loc_type=TypeLoc.objects.create(type='nom'), id_sup=ville)
        TypeEnregistrement.objects.create(lb_type='type')
        HabitatDetail.objects.create(nom="habitat")
        extension = '.rb'
        message_output = verify_and_save_sample(None, extension)
        message_expected = "Le fichier n'est pas dans le bon format."
        self.assertEqual(message_expected, message_output)

        with open('test.csv', 'w', newline='') as csvfile:
            fieldnames = ['not good']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'not good': 'yes'})
        with open('test.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            extension = '.csv'
            message_output = verify_and_save_sample(reader, extension)
            message_expected = "Le fichier n'a pas les bons noms de colonne ou une colonne est manquante."
        self.assertEqual(message_expected, message_output)

        with open('test.csv', 'w', newline='') as csvfile:
            fieldnames = ['id_taxon', 'ordre', 'famille', 'sous-famille', 'genre', 'sous-genre', 'espece',
                          'sous-espece', 'auteur(s)/date', 'date', 'collecteurs', 'identificateur',
                          'date d\'identification', 'altitude(m)', 'pays', 'region', 'commune', 'lieu dit',
                          'type de milieu', 'nombre', 'sexe', 'capture/relacher', 'informations complementaires',
                          'photo', 'x wgs 84', 'y wgs 84', 'x rgnc', 'y rgnc']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'id_taxon': 1, 'pays': 'country', 'region': 'regions', 'commune': 'town',
                             'lieu dit': 'nom', 'x wgs 84': '1', 'y wgs 84': '2', 'altitude(m)': '10', 'nombre': '0',
                             'sexe': 'male', 'date': '2018', 'informations complementaires': '', 'collecteurs': '',
                             'capture/relacher': 'type', 'type de milieu': 'habitat',})
        with open('test.csv', 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            extension = '.csv'
            message_output = verify_and_save_sample(reader, extension)
            message_expected = "Tous les prélèvements ont tous été importé."
        self.assertEqual(message_expected, message_output)
        self.addCleanup(os.remove, 'test.csv')

    def test_list_sample_for_map(self):
        list_sample_output = list_sample_for_map(self.species)
        list_sample_expected = []
        self.assertEqual(list_sample_expected, list_sample_output)
        self.sample.toponymie_x = 1
        self.sample.toponymie_y = 2
        self.sample.save()
        list_sample_output = list_sample_for_map(self.species)
        list_sample_expected = [{'id': 10, 'loc': None, 'default_loc': False, 'latitude': 2.0, 'longitude': 1.0,
                                 't_enre': None, 'date': None, 'collection_museum': None}]
        self.assertEqual(list_sample_expected, list_sample_output)
        species_syn = Taxon.objects.create(id=2, id_ref=self.species, lb_nom="species_synonymous",
                                           lb_auteur="auteur1", rang=self.species.rang)
        country = Localisation.objects.create(nom='country', loc_type=TypeLoc.objects.create(type='pays'),
                                              longitude=4, latitude=1)
        Prelevement.objects.create(id_prelevement=2, id_taxon=species_syn, toponymie_x=1, toponymie_y=4,
                                   type_enregistrement=TypeEnregistrement.objects.create(lb_type='pays'),
                                   id_loc=country)
        list_sample_output = list_sample_for_map(self.species)
        list_sample_expected = [{'id': 10, 'loc': None, 'default_loc': False, 'latitude': 2.0, 'longitude': 1.0,
                                 't_enre': None, 'date': None, 'collection_museum': None},
                                {'id': 2, 'loc': 'country', 'default_loc': True, 'latitude': 4.0, 'longitude': 1.0,
                                 't_enre': 'pays', 'date': None, 'collection_museum': None}]
        self.assertEqual(list_sample_expected, list_sample_output)


# Test function that are related to the model Localisation
class LocationTestCase(TestCase):
    def setUp(self):
        self.pays = Localisation.objects.create(nom='New-Caledonia', loc_type=TypeLoc.objects.create(type='Pays'))
        self.region = Localisation.objects.create(nom='Province Sud',
                                                  loc_type=TypeLoc.objects.create(type='Region'), id_sup=self.pays)
        self.commune = Localisation.objects.create(nom='Koumac',
                                                   loc_type=TypeLoc.objects.create(type='Secteur'), id_sup=self.region)
        self.nom = Localisation.objects.create(nom='1er Rue',
                                               loc_type=TypeLoc.objects.create(type='nom'), id_sup=self.commune)

    def test_get_loc_from_line(self):
        line = {
            'pays': 'patate',
            'region': None,
            'commune': None,
            'lieu dit': None,
            'x wgs 84': '1',
            'y wgs 84': '2',
        }
        self.assertEqual(None, get_loc_from_line(line))

        line['pays'] = 'New-Caledonia'
        line['region'] = 'Province Sud'
        line['commune'] = 'Koumac'
        line['lieu dit'] = '1er Rue'
        dict_loc_expected = {
            'pays': None,
            'region': None,
            'secteur': None,
            'nom': self.nom
        }
        dict_loc_output = get_loc_from_line(line)
        self.assertEqual(dict_loc_expected, dict_loc_output)

        line['pays'] = 'Pays'
        line['region'] = 'Region'
        line['commune'] = 'Commune'
        line['lieu dit'] = 'Lieu Dit'
        dict_loc_output = get_loc_from_line(line)
        dict_loc_output['pays'].save()
        dict_loc_output['region'].save()
        dict_loc_output['secteur'].save()
        dict_loc_output['nom'].save()
        dict_loc_expected['pays'] = Localisation.objects.get(nom='Pays')
        dict_loc_expected['region'] = Localisation.objects.get(nom='Region')
        dict_loc_expected['secteur'] = Localisation.objects.get(nom='Commune')
        dict_loc_expected['nom'] = Localisation.objects.get(nom='Lieu Dit')
        self.assertEqual(dict_loc_expected, dict_loc_output)


# Test function that are not related to any existing model
class OtherTestCase(TestCase):
    def test_is_variable_good(self):
        line = {
            'x wgs 84': 'dfsdf',
            'y wgs 84': '2',
            'altitude(m)': '2-2',
            'nombre': '4'
        }
        boolean = is_variable_good(line)
        self.assertEqual(False, boolean)

        line['x wgs 84'] = '1'
        line['altitude(m)'] = '2'
        boolean = is_variable_good(line)
        self.assertEqual(boolean, True)

    def test_get_variable_in_good_format(self):
        line = {
            'x wgs 84': None,
            'y wgs 84': None,
            'altitude(m)': '10',
            'nombre': None
        }
        dict_expected = {
            'x wgs 84': None,
            'y wgs 84': None,
            'altitude_min': 10,
            'altitude_max': None,
            'nombre': None

        }
        dict_output = get_variable_in_good_format(line)
        self.assertEqual(dict_expected, dict_output)

        line['x wgs 84'] = 10
        line['y wgs 84'] = 12
        line['altitude(m)'] = '15-16'
        line['nombre'] = 1
        dict_expected['x wgs 84'] = 10.0
        dict_expected['y wgs 84'] = 12.0
        dict_expected['altitude_min'] = '15'
        dict_expected['altitude_max'] = '16'
        dict_expected['nombre'] = 1
        dict_output = get_variable_in_good_format(line)
        self.assertEqual(dict_expected, dict_output)

    def test_is_admin(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        my_group = Group.objects.create(name='Admin')
        self.assertFalse(is_admin(user))

        my_group.user_set.add(user)
        self.assertTrue(is_admin(user))
