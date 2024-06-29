# Generated by Django 5.0.6 on 2024-06-27 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_person_img'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='student',
            new_name='person',
        ),
        migrations.AddField(
            model_name='entry',
            name='card_id',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='media/profile_pics/'),
        ),
    ]
