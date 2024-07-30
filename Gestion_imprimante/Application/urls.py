from django.urls import path
from .views import (
    login_view, dashboard, liste_commandes, ajouter_commande,
    supprimer_commande, modifier_commande, generer_devis, logout_view,
    designation_commande, log_view, clear_log, liste_devis, liste_factures,
    liste_bon_livraison, situation_client, generer_facture, generer_bon_livraison
)


urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('commandes/', liste_commandes, name='liste_commandes'),
    path('ajouter/', ajouter_commande, name='ajouter_commande'),
    path('supprimer/<int:pk>/', supprimer_commande, name='supprimer_commande'),
    path('modifier/<int:pk>/', modifier_commande, name='modifier_commande'),
    path('logout/', logout_view, name='logout'),
    path('designation/<int:pk>/', designation_commande, name='designation_commande'),
     path('generer_devis/<int:pk>/', generer_devis, name='generer_devis'),
    path('generer_facture/<int:pk>/', generer_facture, name='generer_facture'),
    path('generer_bon_livraison/<int:pk>/', generer_bon_livraison, name='generer_bon_livraison'),
    path('log_view/', log_view, name='log_view'),
    path('clear_log/', clear_log, name='clear_log'),
    path('devis/', liste_devis, name='liste_devis'),
    path('factures/', liste_factures, name='liste_factures'),
    path('bon_livraison/', liste_bon_livraison, name='liste_bon_livraison'),
    path('situation_client/', situation_client, name='situation_client'),
]