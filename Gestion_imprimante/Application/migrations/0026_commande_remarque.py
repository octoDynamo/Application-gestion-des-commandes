# Generated by Django 5.0.7 on 2024-08-01 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0025_remove_commande_remarque'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='remarque',
            field=models.CharField(choices=[('paye', 'Payé'), ('non_paye', 'Non Payé')], default='non payé', max_length=50),
        ),
    ]
