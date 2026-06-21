from freezegun import freeze_time
from django.urls import reverse
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile

from schedules.models import Participant, Schedule

from .base import BaseScheduleTestCase

@freeze_time("2026-06-21")
class ScheduleTests(BaseScheduleTestCase):
    
    # --- main_calendar_view (Validação de Parâmetros) ---

    def test_main_calendar_view_handles_invalid_month_fallback(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:main_calendar_view"), {"mes": "13", "ano": "2026"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["month"], self.REFERENCE_DATE.month)

    def test_main_calendar_view_handles_invalid_year_fallback(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:main_calendar_view"), {"mes": "6", "ano": "abcd"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["year"], self.REFERENCE_DATE.year)

    def test_main_calendar_view_renders_for_authenticated_user(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:main_calendar_view"))
        self.assertEqual(response.status_code, 200)

    def test_main_calendar_view_redirects_non_authenticated_user(self):
        response = self.client.get(reverse("schedules:main_calendar_view"))
        login_url = reverse("accounts:login_page")
        self.assertRedirects(response, login_url + "?next=" + reverse("schedules:main_calendar_view"))

    # --- main_calendar_view (Filtragem e Estrutura) ---

    def test_main_calendar_view_filters_activities_by_kind_and_category_metrics(self):
        self._login_admin()
        today = self.REFERENCE_DATE
        event_day = date(2026, 6, 23)
        
        self._create_activity(schedule=self.schedule, title="Evento", kind="event", activity_type="class", date=event_day)
        self._create_activity(schedule=self.schedule, title="Tarefa", kind="task", activity_type="study", date=today)

        response = self.client.get(
            reverse("schedules:main_calendar_view"),
            {"kind": ["event"], "category": ["class"], "mes": event_day.month, "ano": event_day.year},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_activities"], 1)
        self.assertIn(event_day.day, response.context["activities_by_day"])
        self.assertEqual(len(response.context["activities_by_day"][event_day.day]), 1)

    def test_main_calendar_view_filters_activities_by_kind_and_category_object_integrity(self):
        self._login_admin()
        event_day = date(2026, 6, 23)
        self._create_activity(schedule=self.schedule, title="Evento de teste", kind="event", activity_type="class", date=event_day)

        response = self.client.get(
            reverse("schedules:main_calendar_view"),
            {"kind": ["event"], "category": ["class"], "mes": event_day.month, "ano": event_day.year},
        )
        activity = response.context["activities_by_day"][event_day.day][0]
        self.assertEqual(activity.title, "Evento de teste")
        self.assertEqual(activity.kind, "event")
        self.assertEqual(activity.activity_type, "class")

    # --- create_schedule ---

    def test_create_schedule_redirects_and_persists(self):
        self._login_admin()
        response = self.client.post(
            reverse("schedules:create_schedule"),
            {"name": "Nova Agenda", "description": "Descrição", "color": "#123456"},
        )
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=agendas")
        self.assertTrue(Schedule.objects.filter(name="Nova Agenda").exists())

    def test_create_schedule_authorizes_creator_as_admin(self):
        self._login_admin()
        self.client.post(
            reverse("schedules:create_schedule"),
            {"name": "Nova Agenda", "description": "Descrição", "color": "#123456"},
        )
        schedule = Schedule.objects.get(name="Nova Agenda")
        self.assertTrue(Participant.objects.filter(schedule=schedule, user=self.admin_user, role=Participant.Role.ADMIN).exists())

    def test_create_schedule_partial_participants_warning_flow(self):
        self._login_admin()
        response = self.client.post(
            reverse("schedules:create_schedule"),
            {"name": "Agenda com participantes", "participant_usernames": ["external", "inexistente"]},
        )
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=agendas")
        self._assert_message(response, "Alguns usuários não foram adicionados")
        self.assertTrue(Participant.objects.filter(schedule__name="Agenda com participantes", user=self.external_user).exists())

    def test_create_schedule_rejects_empty_name(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:create_schedule"), {"name": ""})
        self._assert_message(response, "Preencha o nome da agenda.")
        self.assertEqual(Schedule.objects.count(), 1)

    def test_create_schedule_get_request_redirects(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:create_schedule"))
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=agendas")
        
    # --- edit_schedule ---

    def test_edit_schedule_redirects_and_updates(self):
        self._login_admin()
        response = self.client.post(
            reverse("schedules:edit_schedule", args=[self.schedule.id]),
            {"name": "Agenda Atualizada", "description": "Nova descrição", "color": "#000000"},
        )
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=agendas")
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.name, "Agenda Atualizada")

    def test_edit_schedule_rejects_member_user(self):
        self._login_member()
        response = self.client.post(reverse("schedules:edit_schedule", args=[self.schedule.id]), {"name": "Tentativa"})
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=calendario")
        self._assert_message(response, "Você não tem permissão para isso.")
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.name, "Agenda de Teste")

    def test_edit_schedule_rejects_missing_schedule(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:edit_schedule", args=[9999]), {"name": "Inexistente"})
        self.assertEqual(response.status_code, 404)

    # --- delete_schedule ---

    def test_delete_schedule_removes_record_and_redirects(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:delete_schedule", args=[self.schedule.id]))
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=agendas")
        self.assertFalse(Schedule.objects.filter(id=self.schedule.id).exists())
        
    def test_delete_schedule_rejects_member_user(self):
        self._login_member()
        response = self.client.post(reverse("schedules:delete_schedule", args=[self.schedule.id]))
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=calendario")
        self._assert_message(response, "Você não tem permissão para isso.")
        self.assertTrue(Schedule.objects.filter(id=self.schedule.id).exists())

    def test_delete_schedule_rejects_get_request(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:delete_schedule", args=[self.schedule.id]))
        self.assertEqual(response.status_code, 405)

    # --- leave_schedule ---

    def test_leave_schedule_removes_participant_and_redirects(self):
        self._login_member()
        response = self.client.post(reverse("schedules:leave_schedule", args=[self.schedule.id]))
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=agendas")
        self.assertFalse(Participant.objects.filter(schedule=self.schedule, user=self.member_user).exists())

    def test_leave_schedule_rejects_admin(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:leave_schedule", args=[self.schedule.id]))
        self._assert_message(response, "Administradores não podem sair da agenda")
        self.assertTrue(Participant.objects.filter(schedule=self.schedule, user=self.admin_user).exists())
        
    # --- view_schedule ---

    def test_view_schedule_redirects_for_participant(self):
        self._login_member()
        response = self.client.get(reverse("schedules:view_schedule", args=[self.schedule.id]))
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=agendas")

    def test_view_schedule_rejects_non_participant_user(self):
        self._login_external()
        response = self.client.get(reverse("schedules:view_schedule", args=[self.schedule.id]))
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=calendario")
        self._assert_message(response, "Você não tem acesso a essa agenda.")

    def test_view_schedule_rejects_missing_schedule(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:view_schedule", args=[9999]))
        self.assertEqual(response.status_code, 404)

    # --- add_participant ---

    def test_add_participant_persists_and_redirects(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:add_participant", args=[self.schedule.id]), {"username": "external"})
        self.assertRedirects(response, reverse("schedules:view_schedule", args=[self.schedule.id]), fetch_redirect_response=False)
        self.assertTrue(Participant.objects.filter(schedule=self.schedule, user=self.external_user).exists())

    def test_add_participant_rejects_nonexistent_user(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:add_participant", args=[self.schedule.id]), {"username": "inexistente"})
        self._assert_message(response, "Usuário não encontrado.")

    def test_add_participant_rejects_duplicate_user(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:add_participant", args=[self.schedule.id]), {"username": "member"})
        self._assert_message(response, "Usuário já é participante.")

    # --- remove_participant ---

    def test_remove_participant_removes_record_and_redirects(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:remove_participant", args=[self.schedule.id]), {"user_id": self.member_user.id})
        self.assertRedirects(response, reverse("schedules:view_schedule", args=[self.schedule.id]), fetch_redirect_response=False)
        self.assertFalse(Participant.objects.filter(schedule=self.schedule, user=self.member_user).exists())

    def test_remove_participant_rejects_get_request(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:remove_participant", args=[self.schedule.id]))
        self.assertEqual(response.status_code, 405)

    def test_remove_participant_rejects_admin(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:remove_participant", args=[self.schedule.id]), {"user_id": self.admin_user.id})
        self._assert_message(response, "Não é possível remover um administrador.")
        self.assertTrue(Participant.objects.filter(schedule=self.schedule, user=self.admin_user).exists())

    def test_remove_participant_rejects_non_admin_user(self):
        self._login_member()
        response = self.client.post(reverse("schedules:remove_participant", args=[self.schedule.id]), {"user_id": self.admin_user.id})
        self.assertRedirects(response, reverse("schedules:main_calendar_view") + "?tab=calendario")
        self._assert_message(response, "Você não tem permissão para isso.")
    
    def test_remove_participant_rejects_missing_user(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:remove_participant", args=[self.schedule.id]), {"user_id": 9999})
        self.assertEqual(response.status_code, 404)

    # --- validate_participant_username (JSON View) ---

    def test_validate_participant_username_redirects_anonymous(self):
        response = self.client.get(reverse("schedules:validate_participant_username"))
        login_url = reverse("accounts:login_page")
        self.assertRedirects(response, login_url + "?next=" + reverse("schedules:validate_participant_username"))

    def test_validate_participant_username_rejects_empty_payload(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:validate_participant_username"), {"username": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["valid"], False)
        self.assertEqual(response.json()["message"], "Digite o nome do usuário para adicionar.")

    def test_validate_participant_username_rejects_unknown_user_payload(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:validate_participant_username"), {"username": "inexistente"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["valid"], False)
        self.assertEqual(response.json()["message"], "Usuário não encontrado. Verifique o nome e tente novamente.")

    def test_validate_participant_username_accepts_known_user_payload(self):
        self._login_admin()
        response = self.client.get(reverse("schedules:validate_participant_username"), {"username": "member"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["valid"], True)
        self.assertEqual(response.json()["username"], "member")
        self.assertIn('"level": "success"', response.content.decode())

    # --- logout ---
        
    def test_logout_view_clears_session_and_redirects(self):
        self._login_admin()
        response = self.client.post(reverse("schedules:logout"))
        self.assertRedirects(response, reverse("accounts:login_page"))
        self.assertNotIn("_auth_user_id", self.client.session)
        
    def test_schedule_invalid_color_hex_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        invalid_schedule = Schedule(name="Agenda Errada", color="#INVALID")
        
        with self.assertRaises(ValidationError):
            invalid_schedule.full_clean()

    def test_schedule_default_activity_type_colors_are_copied(self):
        from schedules.models import DEFAULT_ACTIVITY_TYPE_COLORS
        new_schedule = Schedule.objects.create(name="Agenda Cores")
        
        self.assertEqual(new_schedule.activity_type_colors, DEFAULT_ACTIVITY_TYPE_COLORS)

    def test_schedule_string_representation(self):
        self.assertEqual(str(self.schedule), "Agenda de Teste")

    def test_participant_unique_together_constraint(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Participant.objects.create(
                schedule=self.schedule,
                user=self.admin_user,
                role=Participant.Role.MEMBER
            )

    def test_participant_is_admin_property_true_for_admin_role(self):
        participant = Participant.objects.get(schedule=self.schedule, user=self.admin_user)
        self.assertTrue(participant.is_admin)

    def test_participant_is_admin_property_false_for_member_role(self):
        participant = Participant.objects.get(schedule=self.schedule, user=self.member_user)
        self.assertFalse(participant.is_admin)

    def test_participant_string_representation(self):
        participant = Participant.objects.get(schedule=self.schedule, user=self.member_user)
        expected_str = f"{self.member_user} — {self.schedule} ({participant.get_role_display()})"
        
        self.assertEqual(str(participant), expected_str)

    def test_edit_schedule_handles_icon_image_upload(self):
        self._login_admin()
        dummy_image = SimpleUploadedFile(
            name='test_icon.jpg', 
            content=b'dummy_image_data', 
            content_type='image/jpeg'
        )
        
        self.client.post(
            reverse("schedules:edit_schedule", args=[self.schedule.id]),
            {"name": "Agenda com Icone", "icon_image": dummy_image},
        )
        self.schedule.refresh_from_db()
        self.assertTrue(bool(self.schedule.icon_image))

    def test_edit_schedule_handles_clear_icon_image(self):
        self._login_admin()
        self.schedule.icon_image = 'schedule_icons/test.jpg'
        self.schedule.save()
        
        self.client.post(
            reverse("schedules:edit_schedule", args=[self.schedule.id]),
            {"name": "Agenda Limpa", "clear_icon_image": "1"},
        )
        self.schedule.refresh_from_db()
        self.assertFalse(bool(self.schedule.icon_image))