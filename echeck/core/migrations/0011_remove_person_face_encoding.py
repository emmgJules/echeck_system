# Generated by Django 5.0.6 on 2024-06-26 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_entry_student_delete_students'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='face_encoding',
        ),
    ]