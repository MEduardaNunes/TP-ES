from datetime import timedelta
from freezegun import freeze_time
from django.urls import reverse

from schedules import views
from schedules.models import Activity, ActivityCheck

from django.core.files.uploadedfile import SimpleUploadedFile

from .base import BaseScheduleTestCase

@freeze_time("2026-06-21")
class ActivityTests(BaseScheduleTestCase):

    def test_create_activity_allows_admin_user(self):
        self._login_admin()

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "Estudar Python",
                "kind": "task",
                "activity_type": "study",
                "date": self.REFERENCE_DATE.isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=tarefas",
        )

        self.assertTrue(
            Activity.objects.filter(
                schedule=self.schedule,
                title="Estudar Python",
                kind="task",
            ).exists()
        )

    def test_create_activity_rejects_missing_fields(self):
        self._login_admin()

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "",
                "kind": "",
                "activity_type": "",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "Preencha todos os campos obrigatórios.")

    def test_create_activity_rejects_event_without_date(self):
        self._login_admin()

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "Evento sem data",
                "kind": "event",
                "activity_type": "class",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=eventos",
        )

        self._assert_message(response, "Eventos precisam de uma data.")

    def test_create_activity_get_redirects_to_calendario(self):
        self._login_admin()

        response = self.client.get(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

    def test_create_activity_creates_event_activity(self):
        self._login_admin()

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "Aula de amanhã",
                "kind": "event",
                "activity_type": "class",
                "date": self.REFERENCE_DATE.isoformat(),
                "start_time": "09:00",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=eventos",
        )

        self.assertTrue(
            Activity.objects.filter(
                schedule=self.schedule,
                title="Aula de amanhã",
                kind="event",
            ).exists()
        )

    def test_create_activity_rejects_member_user(self):
        self._login_member()

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "Tarefa proibida",
                "kind": "task",
                "activity_type": "study",
                "date": self.REFERENCE_DATE.isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )
        self._assert_message(response, "Você não tem permissão para isso.")

    def test_edit_activity_updates_activity(self):
        self._login_admin()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa antiga",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.post(
            reverse(
                "schedules:edit_activity",
                args=[self.schedule.id, activity.id],
            ),
            {
                "title": "Tarefa atualizada",
                "activity_type": "exam",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=tarefas",
        )

        activity.refresh_from_db()
        self.assertEqual(activity.title, "Tarefa atualizada")
        self.assertEqual(activity.activity_type, "exam")

    def test_edit_activity_rejects_member_user(self):
        self._login_member()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa antiga",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.post(
            reverse(
                "schedules:edit_activity",
                args=[self.schedule.id, activity.id],
            ),
            {
                "title": "Tentativa de edição",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )
        self._assert_message(response, "Você não tem permissão para isso.")

    def test_delete_activity_deletes_activity(self):
        self._login_admin()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa para remover",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.post(
            reverse(
                "schedules:delete_activity",
                args=[self.schedule.id, activity.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=tarefas",
        )

        self.assertFalse(
            Activity.objects.filter(id=activity.id).exists()
        )

    def test_delete_activity_for_missing_activity(self):
        self._login_admin()

        response = self.client.post(
            reverse(
                "schedules:delete_activity",
                args=[self.schedule.id, 9999],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "Atividade não encontrada.")

    def test_quick_create_activity_get_redirects_to_calendario(self):
        self._login_admin()

        response = self.client.get(reverse("schedules:quick_create_activity"))

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

    def test_edit_activity_rejects_missing_activity(self):
        self._login_admin()

        response = self.client.post(
            reverse(
                "schedules:edit_activity",
                args=[self.schedule.id, 9999],
            ),
            {
                "title": "Atividade inexistente",
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_activity_rejects_member_user(self):
        self._login_member()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa para não deletar",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.post(
            reverse(
                "schedules:delete_activity",
                args=[self.schedule.id, activity.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "Você não tem permissão para isso.")

        self.assertTrue(
            Activity.objects.filter(id=activity.id).exists()
        )

    def test_delete_activity_rejects_get_request(self):
        self._login_admin()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa para não deletar",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.get(
            reverse(
                "schedules:delete_activity",
                args=[self.schedule.id, activity.id],
            )
        )

        self.assertEqual(response.status_code, 405)

    def test_quick_create_activity_creates_activity(self):
        self._login_admin()

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "activity_type": "class",
                "date": self.REFERENCE_DATE.isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=eventos",
        )

        self.assertTrue(
            Activity.objects.filter(
                schedule=self.schedule,
                title="Evento rápido",
                kind="event",
            ).exists()
        )
        
    def test_quick_create_activity_rejects_missing_kind(self):
        self._login_admin()

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "activity_type": "class",
                "date": self.REFERENCE_DATE.isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "O tipo da atividade é obrigatório.")

    def test_quick_create_activity_rejects_missing_category(self):
        self._login_admin()

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "date": self.REFERENCE_DATE.isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "A categoria da atividade é obrigatória.")

    def test_quick_create_activity_rejects_non_participant(self):
        self._login_external()

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "activity_type": "class",
                "date": self.REFERENCE_DATE.isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "Você não tem acesso a essa agenda.")

    def test_quick_create_activity_rejects_member_user(self):
        self._login_member()

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "activity_type": "class",
                "date": self.REFERENCE_DATE.isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "Você não tem permissão para criar atividades nessa agenda.")

    def test_toggle_check_marks_activity(self):
        self._login_member()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa a ser marcada",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.post(
            reverse("schedules:toggle_check", args=[self.schedule.id, activity.id])
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=tarefas",
        )

        self.assertTrue(
            ActivityCheck.objects.filter(activity=activity, user=self.member_user).exists()
        )

    def test_toggle_check_unmarks_activity(self):
        self._login_member()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa a ser desmarcada",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        ActivityCheck.objects.create(activity=activity, user=self.member_user)

        response = self.client.post(
            reverse("schedules:toggle_check", args=[self.schedule.id, activity.id])
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=tarefas",
        )

        self.assertFalse(
            ActivityCheck.objects.filter(activity=activity, user=self.member_user).exists()
        )

    def test_toggle_check_rejects_non_participant(self):
        self._login_external()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa protegida",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.post(
            reverse(
                "schedules:toggle_check",
                args=[self.schedule.id, activity.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        self._assert_message(response, "Você não tem acesso a essa agenda.")

    def test_toggle_check_rejects_get_request(self):
        self._login_member()

        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa para verificação",
            kind="task",
            activity_type="study",
            date=self.REFERENCE_DATE,
        )

        response = self.client.get(
            reverse(
                "schedules:toggle_check",
                args=[self.schedule.id, activity.id],
            )
        )

        self.assertEqual(response.status_code, 405)

    def test_toggle_check_rejects_missing_activity(self):
        self._login_member()

        response = self.client.post(
            reverse(
                "schedules:toggle_check",
                args=[self.schedule.id, 9999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_sync_event_checks_creates_past_event_check(self):
        self._login_admin()
        today = self.REFERENCE_DATE
        past_event = self._create_activity(
            schedule=self.schedule,
            title="Evento passado",
            kind="event",
            activity_type="class",
            date=today - timedelta(days=1),
            end_time="10:00",
        )

        views.sync_event_checks(self.admin_user, [self.schedule.id])

        self.assertTrue(
            ActivityCheck.objects.filter(activity=past_event, user=self.admin_user).exists()
        )
        
    def test_sync_event_checks_removes_future_check(self):
        self._login_admin()
        today = self.REFERENCE_DATE
        future_event = self._create_activity(
            schedule=self.schedule,
            title="Evento futuro",
            kind="event",
            activity_type="class",
            date=today + timedelta(days=1),
            end_time="10:00",
        )
        ActivityCheck.objects.create(activity=future_event, user=self.admin_user)

        views.sync_event_checks(self.admin_user, [self.schedule.id])

        self.assertFalse(
            ActivityCheck.objects.filter(activity=future_event, user=self.admin_user).exists()
        )

    def test_activity_check_unique_together_constraint(self):
        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa Duplicada",
            kind="task",
        )
        ActivityCheck.objects.create(activity=activity, user=self.member_user)

        # Tentar criar um segundo check para o mesmo usuário 
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ActivityCheck.objects.create(activity=activity, user=self.member_user)
    
    def test_activity_check_string_representation(self):
        activity = self._create_activity(
            schedule=self.schedule,
            title="Tarefa String",
            kind="task",
        )
        check = ActivityCheck.objects.create(activity=activity, user=self.member_user)
        expected_str = f"{self.member_user} ✔ {activity}"
        
        self.assertEqual(str(check), expected_str)  