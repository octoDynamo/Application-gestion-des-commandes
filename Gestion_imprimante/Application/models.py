# Application/models.py

from django.db import models
from django.contrib.auth.models import User

class Commande(models.Model):
    order_id = models.AutoField(primary_key=True)
    date_time = models.DateTimeField(auto_now_add=True)
    company_reference_number = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100, default="")
    adresse = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    ice = models.CharField(max_length=50, blank=True, null=True)
    infographiste = models.CharField(max_length=100, blank=True, null=True)
    order_status = models.CharField(max_length=50, choices=[
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ])
    bc_number = models.CharField(max_length=50, blank=True, null=True)
    date_bc = models.DateField(blank=True, null=True)
    devis_status = models.CharField(max_length=50, default='pas de devis')
    devis_date = models.DateTimeField(blank=True, null=True)
    devis_numero = models.IntegerField(null=True, blank=True)
    facture_status = models.CharField(max_length=50, default='pas de facture')
    facture_date = models.DateTimeField(blank=True, null=True)
    facture_numero = models.IntegerField(null=True, blank=True)
    bl_status = models.CharField(max_length=50, default='pas de bon_livraison')
    bl_date = models.DateTimeField(blank=True, null=True)
    bl_numero = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Commande {self.order_id}: {self.client_name}"

class Devis(models.Model):
    commande = models.ForeignKey(Commande, related_name='devis', on_delete=models.CASCADE)
    devis_numero = models.PositiveIntegerField(unique=True, null=True, blank=True)
    devis_status = models.CharField(max_length=50, choices=[
        ('no_devis', 'Pas de Devis'),
        ('devis_termine', 'Devis Terminé')
    ], default='pas de devis')
    devis_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Devis {self.devis_numero}"

class Facture(models.Model):
    commande = models.ForeignKey(Commande, related_name='factures', on_delete=models.CASCADE)
    facture_numero = models.PositiveIntegerField(unique=True, null=True, blank=True)
    facture_status = models.CharField(max_length=50, choices=[
        ('no_facture', 'Pas de Facture'),
        ('facture_termine', 'Facture Terminée')
    ], default='pas de facture')
    remarque = models.CharField(max_length=50, choices=[
        ('paye', 'Payé'),
        ('non_paye', 'Non Payé')
    ], default='non payé')
    facture_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Facture {self.facture_numero}"

class BonLivraison(models.Model):
    commande = models.ForeignKey(Commande, related_name='bon_livraison', on_delete=models.CASCADE)
    bl_numero = models.PositiveIntegerField(unique=True, null=True, blank=True)
    bl_status = models.CharField(max_length=50, choices=[
        ('no_bl', 'Pas de bon_livraison'),
        ('bl_termine', 'bon_livraison Terminé')
    ], default='pas de bon_livraison')
    bl_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Bon de Livraison {self.bl_numero}"

class Designation(models.Model):
    name = models.CharField(max_length=255)
    commande = models.ForeignKey(Commande, related_name='designations', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Option(models.Model):
    designation = models.ForeignKey(Designation, related_name='options', on_delete=models.CASCADE)
    option_name = models.CharField(max_length=255)
    format = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    paper_type = models.CharField(max_length=255, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tva_20 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grammage = models.CharField(max_length=255, blank=True, null=True)
    paragraph = models.TextField(blank=True, null=True)
    recto_verso = models.CharField(max_length=2, choices=[('R', 'R'), ('RV', 'R/V')], blank=True, null=True)
    pelliculage_mat = models.BooleanField(default=False)
    pelliculage_brillant = models.BooleanField(default=False)
    spiral = models.BooleanField(default=False)
    piquage = models.BooleanField(default=False)
    collage = models.BooleanField(default=False)
    cousu = models.BooleanField(default=False)

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
