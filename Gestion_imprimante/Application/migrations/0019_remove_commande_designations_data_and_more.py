# Generated by Django 5.0.7 on 2024-07-31 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0018_commande_bc_number_commande_date_bc_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commande',
            name='designations_data',
        ),
        migrations.RemoveField(
            model_name='commande',
            name='options_data',
        ),
    ]
