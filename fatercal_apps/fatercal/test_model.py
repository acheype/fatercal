from django.test import TestCase
from fatercal.models import ValidationError, Taxon, TaxrefRang


# Test function that are related to the model Taxon
class TaxonTestCase(TestCase):
    def setUp(self):
        kingdom = Taxon.objects.create(id=1, lb_nom="kingdom", lb_auteur="auteur1",
                                       rang=TaxrefRang.objects.create(rang='KD', lb_rang='Regne'))
        phylum = Taxon.objects.create(id=2, lb_nom="phylum", lb_auteur="auteur2",
                                      rang=TaxrefRang.objects.create(rang='PH', lb_rang='Phylum'), id_sup=kingdom)
        classe = Taxon.objects.create(id=3, lb_nom="classe", lb_auteur="auteur3",
                                      rang=TaxrefRang.objects.create(rang='CL', lb_rang='Classe'), id_sup=phylum)
        order = Taxon.objects.create(id=4, lb_nom="order", lb_auteur="auteur4",
                                     rang=TaxrefRang.objects.create(rang='OR', lb_rang='Ordre'), id_sup=classe)
        family = Taxon.objects.create(id=5, lb_nom="family", lb_auteur="auteur5",
                                      rang=TaxrefRang.objects.create(rang='FM', lb_rang='Famille'), id_sup=order)
        genus = Taxon.objects.create(id=6, lb_nom="genus", lb_auteur="auteur6",
                                     rang=TaxrefRang.objects.create(rang='GN', lb_rang='Genre'), id_sup=family)
        species = Taxon.objects.create(id=7, lb_nom="species", lb_auteur="auteur7",
                                       rang=TaxrefRang.objects.create(rang='ES', lb_rang='Espèce'), id_sup=genus)
        sub_species = Taxon.objects.create(id=8, lb_nom="sub_species", lb_auteur="auteur8",
                                       rang=TaxrefRang.objects.create(rang='SSES', lb_rang='Sous-Espèce'), id_sup=species)
        Taxon.objects.create(id=9, id_ref=species, lb_nom="species_synonymous", lb_auteur="auteur9", rang=species.rang)
        sub_species.id_ref = sub_species
        species.id_ref = species
        species.save()
        genus.id_ref = genus
        genus.save()
        family.id_ref = family
        family.save()

    def test_get_hierarchy(self):
        kingdom = Taxon.objects.get(lb_nom="kingdom")
        phylum = Taxon.objects.get(lb_nom='phylum')
        classe = Taxon.objects.get(lb_nom='classe')
        order = Taxon.objects.get(lb_nom='order')
        family = Taxon.objects.get(lb_nom='family')
        genus = Taxon.objects.get(lb_nom="genus")
        species = Taxon.objects.get(lb_nom="genus species")
        sub_species = Taxon.objects.get(lb_nom='sub_species')
        list_hierarchy_expected = [
            species,
            genus,
            family,
            order,
            classe,
            phylum,
            kingdom
        ]
        nb = 7
        self.assertEqual((list_hierarchy_expected, nb), sub_species.get_hierarchy())

    def test_valide(self):
        species = Taxon.objects.get(lb_nom="genus species")
        species_syn = Taxon.objects.get(lb_nom="species_synonymous")
        self.assertTrue(species.valide())
        self.assertFalse(species_syn.valide())

    def test_clean(self):
        genus = Taxon.objects.get(lb_nom="genus")
        species = Taxon.objects.get(lb_nom="genus species")
        sub_species = Taxon.objects.get(lb_nom='sub_species')
        species.id_sup = sub_species
        try:
            species.clean()
            self.fail()
        except ValidationError:
            pass
        species.id_sup = genus
        try:
            species.clean()
        except ValidationError:
            self.fail()
