# Generated by Django 5.0.7 on 2024-08-20 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0057_alter_option_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='recto_verso',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
