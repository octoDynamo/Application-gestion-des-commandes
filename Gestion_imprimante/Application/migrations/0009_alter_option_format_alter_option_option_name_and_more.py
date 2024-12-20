# Generated by Django 5.0.7 on 2024-07-25 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0008_alter_option_format_alter_option_option_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='format',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='option',
            name='option_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='option',
            name='paper_type',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='option',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
