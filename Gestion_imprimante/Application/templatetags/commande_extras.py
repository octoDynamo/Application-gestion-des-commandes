# application/templatetags/commande_extras.py

from django import template

register = template.Library()

@register.filter
def translate_status(status):
    translations = {
        'draft': 'Incomplète',
        'completed': 'Complète',
        'devis': 'Devis',
        'facture': 'Facture',
        'bon_livraison': 'Bon de Livraison',
        'situation_client': 'Situation Client'
    }
    return translations.get(status, status)
