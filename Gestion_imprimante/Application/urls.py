from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('commandes/', views.liste_commandes, name='liste_commandes'),
    path('ajouter/', views.ajouter_commande, name='ajouter_commande'),
    path('modifier/<int:pk>/', views.modifier_commande, name='modifier_commande'),
    path('supprimer/<int:pk>/', views.supprimer_commande, name='supprimer_commande'),
    path('generer_devis/<int:pk>/', views.generer_devis, name='generer_devis'),
    path('designation/<int:pk>/', views.designation_commande, name='designation_commande'),
    path('log/', views.log_view, name='log_view'),
    path('clear_log/', views.clear_log, name='clear_log'),
]
