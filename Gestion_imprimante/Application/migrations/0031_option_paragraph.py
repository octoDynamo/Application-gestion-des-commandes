# Generated by Django 5.0.7 on 2024-08-02 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0030_alter_option_format_alter_option_paper_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='paragraph',
            field=models.TextField(blank=True, null=True),
        ),
    ]
