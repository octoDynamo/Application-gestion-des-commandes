from django.db import models
import json

class Commande(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    date_time = models.DateTimeField(auto_now_add=True)
    company_reference_number = models.CharField(max_length=100)
    order_status = models.CharField(max_length=50)
    designations = models.JSONField(default=list)  # Store multiple designations
    options = models.JSONField(default=dict)  # Store options per designation

    def __str__(self):
        return self.order_id