# Generated by Django 5.0.7 on 2024-08-04 14:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0041_remove_commande_bl_date_remove_commande_bl_numero_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonlivraison',
            name='bl_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='devis',
            name='devis_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='facture',
            name='facture_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='bonlivraison',
            name='commande',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bon_livraison', to='Application.commande'),
        ),
        migrations.AlterField(
            model_name='commande',
            name='order_status',
            field=models.CharField(choices=[('draft', 'Draft'), ('completed', 'Completed'), ('devis', 'Devis'), ('facture', 'Facture'), ('bon_livraison', 'Bon de Livraison'), ('situation_client', 'Situation Client')], max_length=50),
        ),
        migrations.AlterField(
            model_name='designation',
            name='commande',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='designations', to='Application.commande'),
        ),
        migrations.AlterField(
            model_name='devis',
            name='commande',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='devis', to='Application.commande'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='commande',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='facture', to='Application.commande'),
        ),
        migrations.AlterField(
            model_name='option',
            name='designation',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='options', to='Application.designation'),
            preserve_default=False,
        ),
    ]
