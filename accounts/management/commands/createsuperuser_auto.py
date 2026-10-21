from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

User = get_user_model()

class Command(BaseCommand):
    help = 'Create superuser for deployment'

    def handle(self, *args, **options):
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='Admin123456!'
                )
                self.stdout.write(self.style.SUCCESS('✅ Superuser created successfully!'))
                self.stdout.write(self.style.WARNING('Username: admin'))
                self.stdout.write(self.style.WARNING('Password: Admin123456!'))
            else:
                self.stdout.write(self.style.INFO('Superuser already exists'))
        except OperationalError:
            self.stdout.write(self.style.ERROR('Database not ready yet'))