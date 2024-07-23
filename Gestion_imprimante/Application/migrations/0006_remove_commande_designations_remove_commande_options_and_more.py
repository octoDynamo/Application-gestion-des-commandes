# Generated by Django 5.0.7 on 2024-07-23 16:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0005_alter_commandelog_commande'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commande',
            name='designations',
        ),
        migrations.RemoveField(
            model_name='commande',
            name='options',
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='designations', to='Application.commande')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_name', models.CharField(max_length=100)),
                ('format', models.CharField(max_length=100)),
                ('quantity', models.PositiveIntegerField()),
                ('paper_type', models.CharField(max_length=100)),
                ('designation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='Application.designation')),
            ],
        ),
    ]
