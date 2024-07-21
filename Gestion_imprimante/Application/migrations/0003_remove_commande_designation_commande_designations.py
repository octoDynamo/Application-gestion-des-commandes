# Generated by Django 5.0.7 on 2024-07-21 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0002_commande_designation_commande_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commande',
            name='designation',
        ),
        migrations.AddField(
            model_name='commande',
            name='designations',
            field=models.JSONField(default=list),
        ),
    ]
