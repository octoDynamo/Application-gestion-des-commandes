# Generated by Django 5.0.7 on 2024-08-04 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0036_alter_designation_commande_alter_option_designation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commande',
            name='order_status',
            field=models.CharField(choices=[('draft', 'Incomplète'), ('completed', 'Complète'), ('devis', 'Devis'), ('facture', 'Facture'), ('bon_livraison', 'Bon de Livraison'), ('situation_client', 'Situation Client')], max_length=50),
        ),
    ]
