from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse
from rest_framework.test import APIClient, APITestCase

from .models import Category, Ticket


class TicketAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="owner", password="test-password")
        cls.other_user = get_user_model().objects.create_user(username="other", password="test-password")
        cls.category = Category.objects.create(name="Учебные вопросы")

    def setUp(self):
        self.client.force_authenticate(self.user)
        self.ticket = Ticket.objects.create(
            title="Исходная заявка", category=self.category, owner=self.user,
        )
        self.url = reverse("tickets-detail", args=[self.ticket.pk])
        self.list_url = reverse("tickets-list")

    def test_create_is_actually_saved_and_owner_cannot_be_spoofed(self):
        response = self.client.post(self.list_url, {
            "title": "  Новая заявка  ", "description": "Подробности",
            "category": self.category.pk, "owner": self.other_user.pk,
        }, format="json")
        self.assertEqual(response.status_code, 201)
        saved = Ticket.objects.get(pk=response.data["id"])
        self.assertEqual(saved.title, "Новая заявка")
        self.assertEqual(saved.description, "Подробности")
        self.assertEqual(saved.category_id, self.category.pk)
        self.assertEqual(saved.owner_id, self.user.pk)
        self.assertEqual(saved.status, Ticket.Status.NEW)

    def test_categories_are_related_entities_and_read_only(self):
        response = self.client.get(reverse("categories-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], self.category.pk)
        self.assertEqual(self.client.post(reverse("categories-list"), {"name": "Другая"}).status_code, 405)

    def test_new_ticket_cannot_start_in_another_status(self):
        for status in ["progress", "done", "invalid"]:
            with self.subTest(status=status):
                response = self.client.post(self.list_url, {
                    "title": "Новая заявка", "category": self.category.pk, "status": status,
                }, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("status", response.data)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_invalid_data_is_rejected_without_creating_objects(self):
        for payload, field in [
            ({"title": "abc", "category": self.category.pk}, "title"),
            ({"title": "     ", "category": self.category.pk}, "title"),
            ({"title": "a" * 201, "category": self.category.pk}, "title"),
            ({"title": "Корректное название", "category": 999999}, "category"),
            ({"title": "Корректное название"}, "category"),
        ]:
            with self.subTest(payload=payload):
                response = self.client.post(self.list_url, payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_status_lifecycle_persists_and_returns_available_transitions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["allowed_statuses"], [{"value": "progress", "label": "В работе"}])
        for status, next_statuses in [("progress", [{"value": "done", "label": "Выполнена"}]), ("done", [])]:
            response = self.client.patch(self.url, {"status": status}, format="json")
            self.assertEqual(response.status_code, 200)
            self.ticket.refresh_from_db()
            self.assertEqual(self.ticket.status, status)
            self.assertEqual(response.data["allowed_statuses"], next_statuses)
            self.assertEqual(response.data["status_label"], self.ticket.get_status_display())
            self.assertEqual(self.client.get(self.url).data["status"], status)

    def test_all_forbidden_transitions_are_rejected_and_db_is_unchanged(self):
        for old_status, new_status in [
            ("new", "done"), ("progress", "new"),
            ("done", "new"), ("done", "progress"), ("new", "unknown"),
        ]:
            for method in ["patch", "put"]:
                with self.subTest(old=old_status, new=new_status, method=method):
                    self.ticket.status = old_status
                    self.ticket.save(update_fields=["status"])
                    response = getattr(self.client, method)(self.url, {
                        "status": new_status, "title": "Изменённое название", "category": self.category.pk,
                    }, format="json")
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("status", response.data)
                    self.ticket.refresh_from_db()
                    self.assertEqual(self.ticket.status, old_status)
                    self.assertEqual(self.ticket.title, "Исходная заявка")

    def test_other_fields_can_be_edited_without_changing_status(self):
        response = self.client.patch(self.url, {"title": "Изменённое название", "description": "Новое описание"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.title, "Изменённое название")
        self.assertEqual(self.ticket.description, "Новое описание")
        self.assertEqual(self.ticket.status, "new")

    def test_delete_removes_record_from_database(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_owner_sees_only_own_tickets_and_can_filter_by_status(self):
        Ticket.objects.create(title="Чужая заявка", category=self.category, owner=self.other_user)
        done = Ticket.objects.create(title="Готовая заявка", category=self.category, owner=self.user, status="done")
        response = self.client.get(self.list_url)
        self.assertEqual({item["id"] for item in response.data}, {self.ticket.pk, done.pk})
        response = self.client.get(self.list_url, {"status": "done"})
        self.assertEqual([item["id"] for item in response.data], [done.pk])

    def test_other_user_cannot_read_update_or_delete_ticket(self):
        self.client.force_authenticate(self.other_user)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.patch(self.url, {"status": "progress"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(self.url).status_code, 404)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "new")

    def test_anonymous_requests_are_denied(self):
        self.client.force_authenticate(user=None)
        for method, url, payload in [
            ("get", self.list_url, None), ("get", reverse("categories-list"), None),
            ("post", self.list_url, {"title": "Новая заявка", "category": self.category.pk}),
            ("patch", self.url, {"status": "progress"}), ("delete", self.url, None),
        ]:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, 403)
        self.assertEqual(Ticket.objects.count(), 1)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "new")


class SessionAndCSRFTests(TestCase):
    def test_session_requires_csrf_for_all_writes(self):
        user = get_user_model().objects.create_user(username="session-user", password="test-password")
        category = Category.objects.create(name="Общие")
        ticket = Ticket.objects.create(title="Проверка CSRF", category=category, owner=user)
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)
        page = client.get(reverse("tickets-dashboard"))
        self.assertEqual(page.status_code, 200)
        token = client.cookies["csrftoken"].value
        url = reverse("tickets-detail", args=[ticket.pk])
        for method, target, payload in [
            ("post", reverse("tickets-list"), {"title": "Новая заявка", "category": category.pk}),
            ("patch", url, {"status": "progress"}), ("delete", url, None),
        ]:
            with self.subTest(method=method):
                self.assertEqual(getattr(client, method)(target, payload, format="json").status_code, 403)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "new")
        response = client.patch(url, {"status": "progress"}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "progress")
        self.assertEqual(client.delete(url, HTTP_X_CSRFTOKEN=token).status_code, 204)
        self.assertFalse(Ticket.objects.filter(pk=ticket.pk).exists())

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("tickets-dashboard"))
        self.assertRedirects(response, "/login/?next=/", fetch_redirect_response=False)

    def test_regular_user_can_log_in_and_work_without_admin_permissions(self):
        user = get_user_model().objects.create_user(username="regular", password="test-password")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        response = self.client.post(reverse("login"), {"username": "regular", "password": "test-password"})
        self.assertRedirects(response, reverse("tickets-dashboard"))
        self.assertContains(self.client.get(reverse("tickets-dashboard")), "regular")
        category = Category.objects.create(name="Вопросы пользователя")
        response = self.client.post(reverse("tickets-list"), {
            "title": "Заявка обычного пользователя", "category": category.pk,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Ticket.objects.get(pk=response.json()["id"]).owner_id, user.pk)
        self.assertEqual(self.client.get("/admin/").status_code, 302)

    def test_invalid_login_shows_error_and_does_not_authenticate(self):
        response = self.client.post(reverse("login"), {"username": "unknown", "password": "wrong"})
        self.assertContains(response, "Неверное имя пользователя или пароль")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_rejects_external_redirect(self):
        get_user_model().objects.create_user(username="regular", password="test-password")
        response = self.client.post(reverse("login"), {
            "username": "regular", "password": "test-password", "next": "https://example.com/",
        })
        self.assertRedirects(response, reverse("tickets-dashboard"))

    def test_logout_requires_post_and_csrf(self):
        user = get_user_model().objects.create_user(username="regular", password="test-password")
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(user)
        client.get(reverse("tickets-dashboard"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.get(reverse("logout")).status_code, 405)
        self.assertEqual(client.post(reverse("logout")).status_code, 403)
        self.assertRedirects(client.post(reverse("logout"), HTTP_X_CSRFTOKEN=token), reverse("login"))
        self.assertEqual(client.get(reverse("tickets-list")).status_code, 403)


class ExistingPortalRoutesTests(TestCase):
    def test_original_portal_routes_and_ticket_home_are_both_available(self):
        self.assertEqual(reverse("dashboard"), "/dashboard/")
        self.assertEqual(reverse("tickets-dashboard"), "/")
        self.assertEqual(reverse("profile"), "/profile/")
        self.assertEqual(resolve("/dashboard/").view_name, "dashboard")
        self.assertEqual(resolve("/dashboard/api/").view_name, "dashboard_api")
        response = self.client.get("/dashboard")
        self.assertRedirects(response, "/dashboard/", fetch_redirect_response=False, status_code=301)
        self.assertRedirects(self.client.get("/dashboard/"), "/accounts/login/?next=/dashboard/", fetch_redirect_response=False)

    def test_methodist_can_open_original_dashboard(self):
        from django.contrib.auth.models import Group

        user = get_user_model().objects.create_user(username="methodist", password="test-password")
        user.groups.add(Group.objects.create(name="Методист"))
        self.client.force_login(user)
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Аналитическая панель")
        self.assertEqual(self.client.get("/dashboard/api/").status_code, 200)
