from .models import Recolteur


# Get the Harvesteur's for a specific sample
def get_Recolteur(prelev):
    list_recolt = Recolteur.objects.filter(id_prelevement=prelev.id_prelevement)
    if len(list_recolt) > 0:
        str_recolt = ''
        for recolt in list_recolt:
            str_recolt += ', '
            str_recolt += '{}'.format(recolt.lb_auteur)
        return str_recolt
    else:
        return 'Récolteur inconnu'
