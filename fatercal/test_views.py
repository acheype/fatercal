from django.test import TestCase
from .views import *
from django.contrib.auth.models import User, Group
from django.utils.encoding import force_text
import json


# Test view that are related to the model Taxon
class TaxonTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.my_group = Group.objects.create(name='Admin')
        self.kingdom = Taxon.objects.create(id=1, lb_nom="kingdom", lb_auteur="auteur1",
                                            rang=TaxrefRang.objects.create(rang='KD', lb_rang='Regne'))
        self.phylum = Taxon.objects.create(id=2, lb_nom="phylum", lb_auteur="auteur2",
                                           rang=TaxrefRang.objects.create(rang='PH', lb_rang='Phylum'),
                                           id_sup=self.kingdom)
        self.classe = Taxon.objects.create(id=3, lb_nom="classe", lb_auteur="auteur3",
                                           rang=TaxrefRang.objects.create(rang='CL', lb_rang='Classe'),
                                           id_sup=self.phylum)
        self.order = Taxon.objects.create(id=4, lb_nom="order", lb_auteur="auteur4",
                                          rang=TaxrefRang.objects.create(rang='OR', lb_rang='Ordre'),
                                          id_sup=self.classe)
        self.family = Taxon.objects.create(id=5, lb_nom="family", lb_auteur="auteur5",
                                           rang=TaxrefRang.objects.create(rang='FM', lb_rang='Famille'),
                                           id_sup=self.order)
        self.genus = Taxon.objects.create(id=6, lb_nom="genus", lb_auteur="auteur6",
                                          rang=TaxrefRang.objects.create(rang='GN', lb_rang='Genre'),
                                          id_sup=self.family)
        self.species = Taxon.objects.create(id=7, lb_nom="species", lb_auteur="auteur7",
                                            rang=TaxrefRang.objects.create(rang='ES', lb_rang='Espèce'),
                                            id_sup=self.genus)
        self.sub_species = Taxon.objects.create(id=8, lb_nom="sub_species", lb_auteur="auteur8",
                                                rang=TaxrefRang.objects.create(rang='SSES', lb_rang='Sous-Espèce'),
                                                id_sup=self.species)
        self.species_syn = Taxon.objects.create(id=9, id_ref=self.species, lb_nom="species_synonymous",
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

    def test_change_taxon_ref(self):
        second_species = Taxon.objects.create(id=10, lb_nom="second_species", lb_auteur="auteur10",
                                              rang=self.species.rang, id_sup=self.genus)
        second_species.id_ref = second_species
        second_species.save()
        response = self.client.get('/fatercal/change_ref/7/')
        self.assertRedirects(response, '/login/?next=/fatercal/change_ref/7/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/change_ref/7/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/change_ref/7/', {'taxon': ''})
        self.assertEqual(response.status_code, 200)
        self.species = Taxon.objects.get(id=7)
        self.assertEqual(self.species.id_ref, self.species)

        response = self.client.post('/fatercal/change_ref/7/', {'taxon': self.species.id})
        self.assertEqual(response.status_code, 200)
        self.species = Taxon.objects.get(id=7)
        self.assertEqual(self.species.id_ref, self.species)

        response = self.client.post('/fatercal/change_ref/7/', {'taxon': second_species.id})
        self.assertEqual(response.status_code, 200)
        self.species = Taxon.objects.get(id=7)
        self.sub_species = Taxon.objects.get(id=8)
        synonymous = Taxon.objects.get(id=9)
        self.assertEqual(synonymous.id_ref, second_species)
        self.assertEqual(self.sub_species.id_sup, second_species)
        self.assertEqual(self.species.id_ref, second_species)

    def test_change_taxon_sup(self):
        second_genus = Taxon.objects.create(
            id=10, lb_nom="second_genus", lb_auteur="auteur10", rang=self.genus.rang, id_sup=self.genus)
        second_genus.id_ref = second_genus
        second_genus.save()
        response = self.client.get('/fatercal/change_sup/7/')
        self.assertRedirects(response, '/login/?next=/fatercal/change_sup/7/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/change_sup/7/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/fatercal/change_sup/9/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/change_sup/7/', {'taxon_superieur': ''})
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/change_sup/7/', {'taxon_superieur': self.sub_species.id})
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/change_sup/7/', {'taxon_superieur': self.species.id})
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/change_sup/7/', {'taxon_superieur': second_genus.id})
        self.assertEqual(response.status_code, 200)
        self.species = Taxon.objects.get(id=7)
        self.assertEqual(self.species.id_sup, second_genus)

    def test_change_validity_to_valid(self):
        response = self.client.get('/fatercal/taxon_to_valid/1/')
        self.assertRedirects(response, '/login/?next=/fatercal/taxon_to_valid/1/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/taxon_to_valid/1/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/fatercal/taxon_to_valid/9/')
        self.assertEqual(response.status_code, 200)
        self.species_syn = Taxon.objects.get(id=9)
        self.assertEqual(self.species_syn.id_ref, self.species_syn)

    def test_advanced_search(self):
        response = self.client.get('/fatercal/advanced_search/')
        self.assertRedirects(response, '/login/?next=/fatercal/advanced_search/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/advanced_search/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/change_sup/7/', {'taxon': self.species.id})
        self.assertEqual(response.status_code, 200)

    def test_extract_taxon_taxref(self):
        response = self.client.get('/fatercal/export_taxref/')
        self.assertRedirects(response, '/login/?next=/fatercal/export_taxref/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 404)

        self.my_group.user_set.add(self.user)
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 200)

    def test_extract_search_taxon_taxref(self):
        response = self.client.get('/fatercal/export_search_taxref/?q=q')
        self.assertRedirects(response, '/login/?next=/fatercal/export_search_taxref/?q=q')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/export_search_taxref/?q=q')
        self.assertEqual(response.status_code, 404)

        self.my_group.user_set.add(self.user)
        response = self.client.get('/fatercal/export_search_taxref/?q=q')
        self.assertEqual(response.status_code, 200)

    def test_choose_search_data(self):
        response = self.client.get('/fatercal/choose_search_data_taxon/')
        self.assertRedirects(response, '/login/?next=/fatercal/choose_search_data_taxon/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/choose_search_data_taxon/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/change_sup/7/', {'q': ''})
        self.assertEqual(response.status_code, 200)

    def test_extract_search_sample(self):
        response = self.client.get('/fatercal/export_taxref/')
        self.assertRedirects(response, '/login/?next=/fatercal/export_taxref/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 404)

        self.my_group.user_set.add(self.user)
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 200)

    def test_export_for_import_sample(self):
        response = self.client.get('/fatercal/export_taxref/')
        self.assertRedirects(response, '/login/?next=/fatercal/export_taxref/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 404)

        self.my_group.user_set.add(self.user)
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 200)

    def test_add_sample_by_csv(self):
        response = self.client.get('/fatercal/export_taxref/')
        self.assertRedirects(response, '/login/?next=/fatercal/export_taxref/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 404)

        self.my_group.user_set.add(self.user)
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/fatercal/export_taxref/', {'not_good': ''})
        self.assertEqual(response.status_code, 200)

    def test_export_adv_search(self):
        response = self.client.get('/fatercal/export_taxref/')
        self.assertRedirects(response, '/login/?next=/fatercal/export_taxref/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 404)

        self.my_group.user_set.add(self.user)
        response = self.client.get('/fatercal/export_taxref/')
        self.assertEqual(response.status_code, 200)


# Test view that are related to the model Prelevement
class SampleTestClass(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.species = Taxon.objects.create(id=1, lb_nom="species", lb_auteur="auteur1",
                                       rang=TaxrefRang.objects.create(rang='ES', lb_rang='Espece'))
        self.sample = Prelevement.objects.create(id_prelevement=1, id_taxref=self.species)
        Recolteur.objects.create(id_prelevement=self.sample, lb_auteur="auteur")
        self.species.id_ref = self.species
        self.species.save()

    def test_update_map(self):
        response = self.client.get('/fatercal/update_map/')
        self.assertRedirects(response, '/login/?next=/fatercal/update_map/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/update_map/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(force_text(response.content), [])

        response = self.client.get('/fatercal/update_map/?taxon=1')
        self.assertEqual(response.status_code, 200)
        json_output = force_text(response.content)
        json_expected = json.dumps([])
        self.assertJSONEqual(json_expected, json_output)

        self.sample.toponymie_x = 1
        self.sample.toponymie_y = 1
        self.sample.save()
        response = self.client.get('/fatercal/update_map/?taxon=1')
        self.assertEqual(response.status_code, 200)
        json_output = force_text(response.content)
        json_expected = json.dumps([{'collection_museum': None, 'date': None, 'default_loc': False, 'id': 1,
                                     'latitude': 1.0, 'loc': None, 'longitude': 1.0, 't_enre': None}])
        self.assertJSONEqual(json_expected, json_output)

    def test_map_sample(self):
        response = self.client.get('/fatercal/map_sample/')
        self.assertRedirects(response, '/login/?next=/fatercal/map_sample/')

        self.client.login(username='temporary', password='temporary')
        response = self.client.get('/fatercal/map_sample/')
        self.assertEqual(response.status_code, 200)

