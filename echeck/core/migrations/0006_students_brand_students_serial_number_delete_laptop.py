# Generated by Django 5.0.2 on 2024-02-27 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_entry_laptop'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='brand',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='students',
            name='serial_number',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Laptop',
        ),
    ]
