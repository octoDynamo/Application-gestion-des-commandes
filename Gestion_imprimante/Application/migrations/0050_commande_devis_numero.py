# Generated by Django 5.0.7 on 2024-08-04 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0049_commande_devis_date_commande_devis_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='devis_numero',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
