# Generated by Django 5.1 on 2024-09-01 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_person_phone_alter_person_serial_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='qr_code_pdf',
            field=models.FileField(blank=True, null=True, upload_to='qrcodes/'),
        ),
    ]
