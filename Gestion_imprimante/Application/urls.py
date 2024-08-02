from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('commandes/', views.liste_commandes, name='liste_commandes'),
    path('devis/', views.liste_devis, name='liste_devis'),
    path('factures/', views.liste_factures, name='liste_factures'),
    path('bon_livraison/', views.liste_bon_livraison, name='liste_bon_livraison'),
    path('situation_client/', views.situation_client, name='situation_client'),
    path('ajouter/', views.ajouter_commande, name='ajouter_commande'),
    path('supprimer/<int:pk>/', views.supprimer_commande, name='supprimer_commande'),
    path('modifier/<int:pk>/', views.modifier_commande, name='modifier_commande'),
    path('designation/<int:pk>/', views.designation_commande, name='designation_commande'),
    path('generer_devis/<int:pk>/', views.generer_devis, name='generer_devis'),
    path('generer_facture/<int:pk>/', views.generer_facture, name='generer_facture'),
    path('generer_bon_livraison/<int:pk>/', views.generer_bon_livraison, name='generer_bon_livraison'),
    path('logs/', views.log_view, name='log_view'),
    path('logs/clear/', views.clear_log, name='clear_log'),
    path('welcome_director/', views.welcome_director, name='welcome_director'),
    path('update_facture_status/<int:pk>/', views.update_facture_status, name='update_facture_status'),
    path('supprimer_facture/<int:pk>/', views.supprimer_facture, name='supprimer_facture'),
    path('update_devis_status/<int:pk>/', views.update_devis_status, name='update_devis_status'),
    path('supprimer_devis/<int:pk>/', views.supprimer_devis, name='supprimer_devis'),
    path('update_bl_status/<int:pk>/', views.update_bl_status, name='update_bl_status'),
    path('supprimer_bl/<int:pk>/', views.supprimer_bl, name='supprimer_bl'),
]



