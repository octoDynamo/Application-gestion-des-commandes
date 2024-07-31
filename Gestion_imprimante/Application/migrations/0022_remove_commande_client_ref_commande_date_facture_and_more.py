# Generated by Django 5.0.7 on 2024-07-31 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0021_alter_commande_remarque'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commande',
            name='client_ref',
        ),
        migrations.AddField(
            model_name='commande',
            name='date_facture',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='commande',
            name='facture_status',
            field=models.CharField(choices=[('no_facture', 'Pas de Facture'), ('facture_termine', 'Facture Terminée')], default='pas de facture', max_length=50),
        ),
        migrations.AlterField(
            model_name='commande',
            name='remarque',
            field=models.CharField(choices=[('paye', 'Payé'), ('non_paye', 'Non Payé')], default='non payé', max_length=50),
        ),
    ]
