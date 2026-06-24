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

    def test_theme_preference_color_validation(self):
        from django.core.exceptions import ValidationError
        pref = UserThemePreference(user=self.user, base_clr="invalid")
        with self.assertRaises(ValidationError):
            pref.full_clean()

        # Valid color should not raise
        pref.base_clr = "#FF0000"
        pref.full_clean()

    def test_settings_page_requires_login(self):
        response = self.client.get(reverse("accounts:settings_page"))
        self.assertEqual(response.status_code, 302)

    def test_settings_page_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:settings_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/settings.html")
        self.assertIn("preference", response.context)

    def test_update_preferences_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("schedules:preferences:update_preferences"))
        self.assertRedirects(response, reverse("accounts:settings_page"))

    def test_update_preferences_requires_login(self):
        response = self.client.post(reverse("schedules:preferences:update_preferences"))
        self.assertEqual(response.status_code, 302)

    def test_update_preferences_success(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("schedules:preferences:update_preferences"),
            {
                "base_clr": "#111111",
                "line_clr": "#222222",
                "hover_clr": "#333333",
                "text_clr": "#444444",
                "accent_clr": "#555555",
                "secondary_text_clr": "#666666",
                "container_background_base": "#777777",
                "secondary_base_clr": "#888888",
                "sidebar_gradient_start": "#999999",
                "sidebar_gradient_end": "#aaaaaa",
                "profile_icon_emoji": "😎",
                "agenda_icon_emoji": "📅",
                "default_activity_icon_emoji": "📝",
            },
        )
        self.assertRedirects(response, reverse("accounts:settings_page"))
        
        pref = UserThemePreference.objects.get(user=self.user)
        self.assertEqual(pref.base_clr, "#111111")
        self.assertEqual(pref.line_clr, "#222222")
        self.assertEqual(pref.hover_clr, "#333333")
        self.assertEqual(pref.text_clr, "#444444")
        self.assertEqual(pref.accent_clr, "#555555")
        self.assertEqual(pref.secondary_text_clr, "#666666")
        self.assertEqual(pref.container_background_base, "#777777")
        self.assertEqual(pref.secondary_base_clr, "#888888")
        self.assertEqual(pref.sidebar_gradient_start, "#999999")
        self.assertEqual(pref.sidebar_gradient_end, "#aaaaaa")
        self.assertEqual(pref.profile_icon_emoji, "😎")
        self.assertEqual(pref.agenda_icon_emoji, "📅")
        self.assertEqual(pref.default_activity_icon_emoji, "📝")

    def test_update_preferences_uploads_and_clears_images(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_login(self.user)

        gif_data = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
        )
        profile_file = SimpleUploadedFile("profile.gif", gif_data, content_type="image/gif")
        agenda_file = SimpleUploadedFile("agenda.gif", gif_data, content_type="image/gif")
        activity_file = SimpleUploadedFile("activity.gif", gif_data, content_type="image/gif")

        # Test upload
        response = self.client.post(
            reverse("schedules:preferences:update_preferences"),
            {
                "profile_icon_image": profile_file,
                "agenda_icon_image": agenda_file,
                "default_activity_icon_image": activity_file,
            },
        )
        self.assertRedirects(response, reverse("accounts:settings_page"))
        
        pref = UserThemePreference.objects.get(user=self.user)
        self.assertTrue(pref.profile_icon_image.name.startswith("ui_icons/profile/profile"))
        self.assertTrue(pref.agenda_icon_image.name.startswith("ui_icons/agenda/agenda"))
        self.assertTrue(pref.default_activity_icon_image.name.startswith("ui_icons/activity_default/activity"))

        # Test clear
        response2 = self.client.post(
            reverse("schedules:preferences:update_preferences"),
            {
                "clear_profile_icon_image": "1",
                "clear_agenda_icon_image": "1",
                "clear_default_activity_icon_image": "1",
            },
        )
        self.assertRedirects(response2, reverse("accounts:settings_page"))
        
        pref.refresh_from_db()
        self.assertFalse(pref.profile_icon_image)
        self.assertFalse(pref.agenda_icon_image)
        self.assertFalse(pref.default_activity_icon_image)

    def test_reset_preferences_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("schedules:preferences:reset_preferences"))
        self.assertRedirects(response, reverse("accounts:settings_page"))

    def test_reset_preferences_requires_login(self):
        response = self.client.post(reverse("schedules:preferences:reset_preferences"))
        self.assertEqual(response.status_code, 302)

    def test_reset_preferences_success(self):
        self.client.force_login(self.user)
        # First ensure it exists
        UserThemePreference.objects.get_or_create(user=self.user)
        self.assertTrue(UserThemePreference.objects.filter(user=self.user).exists())

        response = self.client.post(reverse("schedules:preferences:reset_preferences"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:settings_page")))
        self.assertFalse(UserThemePreference.objects.filter(user=self.user).exists())

    def test_reset_preferences_success_if_not_exists(self):
        self.client.force_login(self.user)
        # Delete it first
        UserThemePreference.objects.filter(user=self.user).delete()
        self.assertFalse(UserThemePreference.objects.filter(user=self.user).exists())

        response = self.client.post(reverse("schedules:preferences:reset_preferences"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:settings_page")))
        self.assertFalse(UserThemePreference.objects.filter(user=self.user).exists())

    def test_edit_user_updates_password_successfully(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:edit_user"),
            {
                "username": "tester",
                "password": "novasenha123",
                "password_confirm": "novasenha123",
            },
        )
        self.assertRedirects(response, reverse("accounts:user_space"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("novasenha123"))

    def test_login_user_get_redirects_to_login_page(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertRedirects(response, reverse("accounts:login_page"))

    def test_logout_user_get_redirects_to_login_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:login_page")))

    def test_edit_user_get_redirects_to_user_space(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:edit_user"))
        self.assertRedirects(response, reverse("accounts:user_space"))

    def test_delete_user_get_redirects_to_user_space(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:delete_user"))
        self.assertRedirects(response, reverse("accounts:user_space"))



