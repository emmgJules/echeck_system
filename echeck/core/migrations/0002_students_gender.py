# Generated by Django 5.0.2 on 2024-02-20 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='gender',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
