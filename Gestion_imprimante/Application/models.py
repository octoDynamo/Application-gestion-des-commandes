from django.db import models
from django.contrib.auth.models import User


class Commande(models.Model):
    order_id = models.AutoField(primary_key=True)  # Auto-incremented primary key
    date_time = models.DateTimeField(auto_now_add=True)
    company_reference_number = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100, default="")  # New field
    adresse = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    ice = models.CharField(max_length=50, blank=True, null=True)
    infographiste = models.CharField(max_length=100, blank=True, null=True)
    order_status = models.CharField(max_length=50, choices=[ ('draft', 'Draft'), 
        ('completed', 'Completed'), 
        ('devis', 'Devis'), 
        ('facture', 'Facture'), 
        ('bon_livraison', 'Bon de Livraison'), 
        ('situation_client', 'Situation Client')
    ])
    bc_number = models.CharField(max_length=50, blank=True, null=True)  # New field for BC number
    date_bc = models.DateField(blank=True, null=True) 
    devis_numero = models.PositiveIntegerField(unique=True, null=True, blank=True)
    facture_numero = models.PositiveIntegerField(unique=True, null=True, blank=True)
    facture_status = models.CharField(max_length=50, choices=[
        ('no_facture', 'Pas de Facture'),
        ('facture_termine', 'Facture Terminée')
    ], default='pas de facture')
    remarque = models.CharField(max_length=50, choices=[
        ('paye', 'Payé'),
        ('non_paye', 'Non Payé')
    ], default='non payé')
    devis_status = models.CharField(max_length=50, choices=[
        ('no_devis', 'Pas de Devis'),
        ('devis_termine', 'Devis Terminé')
    ], default='pas de devis')
    designations_data = models.JSONField(default=list)  # Renamed field
    options_data = models.JSONField(default=dict)

    def __str__(self):
        return f"Commande {self.order_id}: {self.client_name}"

class Designation(models.Model):
    name = models.CharField(max_length=255)
    commande = models.ForeignKey(Commande, related_name='designations', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Option(models.Model):
    designation = models.ForeignKey(Designation, related_name='options', on_delete=models.CASCADE)
    option_name = models.CharField(max_length=255)
    format = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    paper_type = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tva_20 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grammage = models.CharField(max_length=255, blank=True, null=True)  # Ajouter ce champ
    recto_verso = models.CharField(max_length=2, choices=[('R', 'R'), ('RV', 'R/V')], blank=True, null=True)  # Ajouter ce champ

    def __str__(self):
        return self.option_name

class Prix(models.Model):
    option = models.ForeignKey(Option, related_name='prices', on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Prix for {self.option.option_name} - {self.unit_price}"

class CommandeLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('modify', 'Modify'),
        ('delete', 'Delete'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    commande = models.ForeignKey(Commande, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.commande} at {self.timestamp}"
