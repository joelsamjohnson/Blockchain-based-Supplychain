from django.db import migrations

def migrate_user_types(apps, schema_editor):
    User = apps.get_model('supplychain', 'User')
    # Mapping from old values to new values
    type_mapping = {
        'RMS': 'S',
        'Manufacturer': 'M',
        'Retailer': 'R',
        'Distributor': 'D',
    }
    for user in User.objects.all():
        if user.user_type in type_mapping:
            user.user_type = type_mapping[user.user_type]
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('supplychain', '0002_product'),
    ]

    operations = [
        migrations.RunPython(migrate_user_types),
    ]
