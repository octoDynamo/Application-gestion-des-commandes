# Generated by Django 5.0.7 on 2024-07-29 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0010_commande_client_name_commande_designations_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='adresse',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='fax',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='ice',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='commande',
            name='infographiste',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='commande',
            name='order_status',
            field=models.CharField(default='draft', max_length=50),
        ),
    ]
