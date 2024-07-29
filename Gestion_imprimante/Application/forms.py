from django import forms
from .models import Commande

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client_name', 'company_reference_number', 'adresse', 'email', 'fax', 'ice', 'infographiste']
