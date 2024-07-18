from django.db import models

class Commande(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    date_time = models.DateTimeField(auto_now_add=True)
    company_reference_number = models.CharField(max_length=100)
    order_status = models.CharField(max_length=50)

    def __str__(self):
        return self.order_id
