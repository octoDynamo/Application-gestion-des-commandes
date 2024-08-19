from django import forms
from .models import Commande
from .models import Option

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['client_name', 'company_reference_number', 'adresse', 'email', 'fax', 'ice', 'infographiste']

class SituationClientForm(forms.Form):
    client_ref = forms.CharField(max_length=255, label='Référence Client')

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_name', 'format', 'paper_type', 'paragraph', 'grammage', 'recto_verso', 
                  'pelliculage_mat', 'pelliculage_brillant', 'spiral', 'piquage', 'collage', 'cousu', 'quantity', 'unit_price']
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price < 0:
            raise forms.ValidationError("Unit price cannot be negative.")
        return unit_price