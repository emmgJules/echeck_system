import os
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
import shutil
from django.core import serializers

class Command(BaseCommand):
    help = 'Backs up the SQLite database and stores a JSON dump of the data'

    def handle(self, *args, **kwargs):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        
        db_path = settings.DATABASES['default']['NAME']
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.sqlite3')
        shutil.copy2(db_path, backup_file)
        self.stdout.write(self.style.SUCCESS(f'Database backup created at {backup_file}'))
        
        json_backup_file = os.path.join(backup_dir, f'db_dump_{timestamp}.json')
        with open(json_backup_file, 'w') as json_file:
            data = serializers.serialize('json', self.get_all_objects())
            json_file.write(data)
        self.stdout.write(self.style.SUCCESS(f'Database JSON dump created at {json_backup_file}'))

    def get_all_objects(self):
        from django.apps import apps
        all_objects = []
        for model in apps.get_models():
            all_objects.extend(model.objects.all())
        return all_objects
