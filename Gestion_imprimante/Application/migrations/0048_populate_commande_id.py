from django.db import migrations, models

def populate_commande_id(apps, schema_editor):
    Designation = apps.get_model('Application', 'Designation')
    Commande = apps.get_model('Application', 'Commande')

    # Create a default Commande if it doesn't exist
    default_commande, created = Commande.objects.get_or_create(
        company_reference_number="default",
        defaults={'client_name': "default", 'order_status': "draft"}
    )

    # Update all Designation objects with a null commande_id to use the default Commande
    Designation.objects.filter(commande__isnull=True).update(commande=default_commande)

class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0047_alter_designation_commande'),
    ]

    operations = [
        migrations.RunPython(populate_commande_id),
    ]
