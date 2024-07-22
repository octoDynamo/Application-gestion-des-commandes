from django.db import models
from django.contrib.auth.models import User
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
    
class CommandeLog(models.Model):
    ACTION_CHOICES = (
        ('add', 'Add'),
        ('modify', 'Modify'),
        ('delete', 'Delete'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    commande = models.ForeignKey(Commande, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.commande} at {self.timestamp}"