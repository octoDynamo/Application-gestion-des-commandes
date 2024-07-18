from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_commandes, name='liste_commandes'),
    path('ajouter/', views.ajouter_commande, name='ajouter_commande'),
]
