from django.db import models
import json

class Commande(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    date_time = models.DateTimeField(auto_now_add=True)
    company_reference_number = models.CharField(max_length=100)
    order_status = models.CharField(max_length=50)
    designation = models.CharField(max_length=100, blank=True, null=True)
    options = models.JSONField(default=dict)  # Provide a default empty dict

    def __str__(self):
        return self.order_id
