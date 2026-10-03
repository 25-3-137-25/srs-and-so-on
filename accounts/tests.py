from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from .models import AcademicGroup, Course, Department


class PortalTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user('reader', password='test-password')
        self.editor = User.objects.create_user('methodist', password='test-password')
        self.editor.groups.add(Group.objects.create(name='Методист'))
        self.department = Department.objects.create(name='Факультет')
        self.course = Course.objects.create(title='Курс', department=self.department)
        self.group = AcademicGroup.objects.create(name='Группа', department=self.department)

    def test_login_next_and_logout(self):
        response = self.client.get(reverse('course_list'))
        self.assertRedirects(response, '/accounts/login/?next=/courses/')
        response = self.client.post(reverse('login') + '?next=/courses/', {'username': 'reader', 'password': 'test-password', 'next': '/courses/'})
        self.assertRedirects(response, reverse('course_list'))
        self.assertRedirects(self.client.post(reverse('logout')), reverse('login'))

    def test_reader_pages_and_access(self):
        self.client.force_login(self.reader)
        for kind, obj in [('course', self.course), ('department', self.department), ('academic_group', self.group)]:
            response = self.client.get(reverse(kind + '_list'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, str(obj))
            self.assertNotContains(response, reverse(kind + '_create'))
            for action, args in [('create', []), ('update', [obj.pk]), ('delete', [obj.pk])]:
                self.assertEqual(self.client.post(reverse(kind + '_' + action, args=args), {}).status_code, 302)
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())
        self.assertTrue(Department.objects.filter(pk=self.department.pk).exists())
        self.assertTrue(AcademicGroup.objects.filter(pk=self.group.pk).exists())

    def test_methodist_crud_and_templates(self):
        self.client.force_login(self.editor)
        self.assertContains(self.client.get(reverse('profile')), 'Методист')
        for kind, model, data in [
            ('course', Course, {'title': 'Новый курс', 'description': 'Описание', 'department': self.department.pk}),
            ('academic_group', AcademicGroup, {'name': 'Новая группа', 'department': self.department.pk}),
            ('department', Department, {'name': 'Новый факультет'}),
        ]:
            self.assertContains(self.client.get(reverse(kind + '_list')), reverse(kind + '_create'))
            self.assertEqual(self.client.get(reverse(kind + '_create')).status_code, 200)
            self.assertContains(self.client.post(reverse(kind + '_create'), {}), 'errorlist')
            response = self.client.post(reverse(kind + '_create'), data)
            self.assertRedirects(response, reverse(kind + '_list'))
            obj = model.objects.latest('pk')
            self.assertContains(self.client.get(reverse(kind + '_list')), reverse(kind + '_update', args=[obj.pk]))
            self.assertEqual(self.client.get(reverse(kind + '_update', args=[obj.pk])).status_code, 200)
            data['title' if kind == 'course' else 'name'] = 'Изменено'
            self.assertRedirects(self.client.post(reverse(kind + '_update', args=[obj.pk]), data), reverse(kind + '_list'))
            obj.refresh_from_db()
            self.assertEqual(str(obj), 'Изменено')
            self.assertContains(self.client.get(reverse(kind + '_delete', args=[obj.pk])), reverse(kind + '_list'))
            self.assertTrue(model.objects.filter(pk=obj.pk).exists())
            self.assertRedirects(self.client.post(reverse(kind + '_delete', args=[obj.pk])), reverse(kind + '_list'))
            self.assertFalse(model.objects.filter(pk=obj.pk).exists())

    def test_empty_states_and_escaping(self):
        self.client.force_login(self.editor)
        self.course.title = '<script>alert(1)</script>'
        self.course.save()
        response = self.client.get(reverse('course_list'))
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
        Department.objects.all().delete()
        for route in ['course_list', 'department_list', 'academic_group_list']:
            self.assertContains(self.client.get(reverse(route)), 'Здесь пока нет записей')
