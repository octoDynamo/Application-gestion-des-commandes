# Generated by Django 5.0.7 on 2024-08-07 20:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0055_alter_logentry_bon_livraison_alter_logentry_commande_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='bon_livraison',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_entries', to='Application.bonlivraison'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='commande',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_entries', to='Application.commande'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='devis',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_entries', to='Application.devis'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='facture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_entries', to='Application.facture'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_log_entries', to=settings.AUTH_USER_MODEL),
        ),
    ]
