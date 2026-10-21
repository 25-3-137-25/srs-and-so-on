from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from groups.models import Faculty, StudyGroup

User = get_user_model()

class Command(BaseCommand):
    help = 'Заполнение базы данных начальными данными (факультеты и группы)'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение базы данных...')

        # Создаём факультеты
        faculties_data = [
            {'code': 'И1', 'name': 'Институт №1 «Авиационные системы»'},
            {'code': 'И3', 'name': 'Институт №3 «Системы управления, информатика и электроэнергетика»'},
            {'code': 'И6', 'name': 'Институт №6 «Аэрокосмический»'},
            {'code': 'И8', 'name': 'Институт №8 «Компьютерные науки и прикладная математика»'},
        ]

        faculties = {}
        for fac_data in faculties_data:
            faculty, created = Faculty.objects.get_or_create(
                code=fac_data['code'],
                defaults={'name': fac_data['name']}
            )
            faculties[fac_data['code']] = faculty
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан факультет: {faculty}'))
            else:
                self.stdout.write(self.style.WARNING(f'Факультет уже существует: {faculty}'))

        # Создаём учебного пользователя (куратора), если нет
        curator, created = User.objects.get_or_create(
            username='curator',
            defaults={
                'email': 'curator@example.com',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'is_staff': True
            }
        )
        if created:
            curator.set_password('Curator123!')
            curator.save()
            self.stdout.write(self.style.SUCCESS('Создан пользователь-куратор: curator / Curator123!'))

        # Создаём учебные группы
        groups_data = [
            {'name': 'М3О-234БВ-25', 'faculty_code': 'И3', 'status': 'studying', 'students': 21},
            {'name': 'М8О-102БВ-25', 'faculty_code': 'И8', 'status': 'recruiting', 'students': 25},
            {'name': 'М1О-305А-25', 'faculty_code': 'И1', 'status': 'graduated', 'students': 18},
        ]

        for group_data in groups_data:
            faculty = faculties[group_data['faculty_code']]
            group, created = StudyGroup.objects.get_or_create(
                name=group_data['name'],
                defaults={
                    'faculty': faculty,
                    'curator': curator,
                    'status': group_data['status'],
                    'students_count': group_data['students']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана группа: {group}'))
            else:
                self.stdout.write(self.style.WARNING(f'Группа уже существует: {group}'))

        self.stdout.write(self.style.SUCCESS('\nЗаполнение базы данных завершено!'))