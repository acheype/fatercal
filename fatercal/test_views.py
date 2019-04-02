from django.test import TestCase
from .views import *
from django.contrib.auth.models import User


# Test view that are related to the model Taxon
class TaxonTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
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
        Taxon.objects.create(id=9, id_ref=self.species, lb_nom="species_synonymous", lb_auteur="auteur9",
                             rang=self.species.rang)
        self.sub_species.id_ref = self.sub_species
        self.species.id_ref = self.species
        self.species.save()
        self.genus.id_ref = self.genus
        self.genus.save()
        self.family.id_ref = self.family
        self.family.save()

    def test_change_taxon_ref(self):
        pass

    def test_change_taxon_sup(self):
        pass

    def test_change_validity_to_valid(self):
        pass

    def test_advanced_search(self):
        pass

    def test_extract_taxon_taxref(self):
        pass

    def test_extract_search_taxon_taxref(self):
        pass

    def test_choose_search_data(self):
        pass

    def test_extract_search_sample(self):
        pass

    def test_export_for_import_sample(self):
        pass

    def test_add_sample_by_csv(self):
        pass

    def test_export_adv_search(self):
        pass


# Test view that are related to the model Prelevement
class SampleTestClass(TestCase):
    def setUp(self):
        species = Taxon.objects.create(id=1, lb_nom="species", lb_auteur="auteur1",
                                       rang=TaxrefRang.objects.create(rang='ES', lb_rang='Espece'))
        sample = Prelevement.objects.create(id_taxref=species)
        Recolteur.objects.create(id_prelevement=sample, lb_auteur="auteur")
        species.id_ref = species
        species.save()


class TestMapCase(TestCase):
    def test_update_map(self):
        pass

    def test_map_sample(self):
        pass
