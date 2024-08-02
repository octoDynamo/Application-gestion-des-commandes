from django import forms
from .models import Commande
from .models import Option

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client_name', 'company_reference_number', 'adresse', 'email', 'fax', 'ice', 'infographiste']
