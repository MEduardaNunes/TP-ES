from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from ..models import UserThemePreference


class AccountsViewsTests(TestCase):
    # Contexto geral: usuário de teste
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="senha123",
        )

    def test_login_page_redirects_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:login_page"))

        self.assertRedirects(response, reverse("schedules:main_calendar_view"))

    def test_login_page_renders_for_non_authenticated_user(self):
        response = self.client.get(reverse("accounts:login_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entrar")
        self.assertContains(response, "Nome")

    def test_user_space_renders_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:user_space"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tester")

    def test_user_space_renders_for_non_authenticated_user(self):
        response = self.client.get(reverse("accounts:user_space"))

        self.assertEqual(response.status_code, 302)

    def test_sign_up(self):
        response = self.client.get(reverse("accounts:sign_up"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cadastrar")

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "novo_usuario",
                "password": "senha123",
                "password_confirm": "senha123",
            },
        )

        self.assertRedirects(response, reverse("accounts:login_page"))
        self.assertTrue(get_user_model().objects.filter(username="novo_usuario").exists())

    def test_register_rejects_existing_username(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "tester",
                "password": "senha123",
                "password_confirm": "senha123",
            },
        )

        self.assertRedirects(response, reverse("accounts:sign_up"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("já existe" in str(message) for message in messages))

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "outro_usuario",
                "password": "senha123",
                "password_confirm": "outra_senha",
            },
        )

        self.assertRedirects(response, reverse("accounts:sign_up"))
        self.assertFalse(get_user_model().objects.filter(username="outro_usuario").exists())

    def test_register_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:register")) 

        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse("schedules:main_calendar_view"))

    def test_login_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:login"))

        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse("schedules:main_calendar_view"))

    def test_login_user_authenticates_valid_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "tester", "password": "senha123"},
        )

        self.assertRedirects(response, reverse("schedules:main_calendar_view"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_user_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "tester", "password": "senha_errada"},
        )

        self.assertRedirects(response, reverse("accounts:login_page"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("incorretos" in str(message) for message in messages))

    def test_logout_user_logs_out_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login_page"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_user_logs_out_non_authenticated_user(self):
        response = self.client.post(reverse("accounts:logout"))

        self.assertTrue(response.status_code, 302)

    def test_edit_user_non_authenticated_user(self):
        response = self.client.post(reverse("accounts:edit_user"))

        self.assertTrue(response.status_code, 302)

    def test_edit_user_updates_username(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_user"),
            {
                "username": "tester_atualizado",
                "password": "",
                "password_confirm": "",
            },
        )

        self.assertRedirects(response, reverse("accounts:user_space"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "tester_atualizado")

    def test_edit_user_updates_username_used(self):
        get_user_model().objects.create_user(username="outro_usuario", password="password")
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_user"),
            {
                "username": "outro_usuario",
                "password": "",
                "password_confirm": "",
            },
        )

        self.assertRedirects(response, reverse("accounts:user_space"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("já existe" in str(message) for message in messages))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "tester")

    def test_edit_user_updates_no_password(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_user"),
            {
                "username": "tester_atualizado",
                "password": "",
                "password_confirm": "123",
            },
        )

        self.assertRedirects(response, reverse("accounts:user_space"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("preencha a nova senha" in str(message) for message in messages))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "tester")

    def test_edit_user_updates_no_confirm_password(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_user"),
            {
                "username": "tester_atualizado",
                "password": "123",
                "password_confirm": "",
            },
        )

        self.assertRedirects(response, reverse("accounts:user_space"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("confirme a nova senha" in str(message) for message in messages))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "tester")

    def test_edit_user_updates_dont_match_passwords(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_user"),
            {
                "username": "tester_atualizado",
                "password": "123",
                "password_confirm": "1234",
            },
        )

        self.assertRedirects(response, reverse("accounts:user_space"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("não coincidem" in str(message) for message in messages))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("senha123"))

    def test_delete_user_removes_account(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:delete_user"))

        self.assertRedirects(response, reverse("accounts:login_page"))
        self.assertFalse(get_user_model().objects.filter(pk=self.user.pk).exists())

    def test_delete_user_non_authenticated(self):
        response = self.client.post(reverse("accounts:delete_user"))

        self.assertEqual(response.status_code, 302)
