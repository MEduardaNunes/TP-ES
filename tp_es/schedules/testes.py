from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from schedules import views
from schedules.models import Activity, ActivityCheck, Participant, Schedule


class ScheduleViewsTests(TestCase):
    # Contexto geral: usuários e agenda de teste

    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username="admin",
            password="senha123",
        )

        self.member_user = get_user_model().objects.create_user(
            username="member",
            password="senha123",
        )

        self.external_user = get_user_model().objects.create_user(
            username="external",
            password="senha123",
        )

        self.schedule = Schedule.objects.create(
            name="Agenda de Teste",
            description="Descrição da agenda",
            color="#59e7ec",
        )

        Participant.objects.create(
            schedule=self.schedule,
            user=self.admin_user,
            role=Participant.Role.ADMIN,
        )

        Participant.objects.create(
            schedule=self.schedule,
            user=self.member_user,
            role=Participant.Role.MEMBER,
        )

    # main_calendar_view

    def test_main_calendar_view_renders_for_authenticated_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("schedules:main_calendar_view")
        )

        self.assertEqual(response.status_code, 200)

    def test_main_calendar_view_redirects_non_authenticated_user(self):
        response = self.client.get(
            reverse("schedules:main_calendar_view")
        )

        self.assertEqual(response.status_code, 302)

    # create_schedule

    def test_create_schedule(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("schedules:create_schedule"),
            {
                "name": "Nova Agenda",
                "description": "Descrição",
                "color": "#123456",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=agendas",
        )

        self.assertTrue(
            Schedule.objects.filter(name="Nova Agenda").exists()
        )

        schedule = Schedule.objects.get(name="Nova Agenda")

        self.assertTrue(
            Participant.objects.filter(
                schedule=schedule,
                user=self.admin_user,
                role=Participant.Role.ADMIN,
            ).exists()
        )

    def test_create_schedule_rejects_empty_name(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("schedules:create_schedule"),
            {
                "name": "",
            },
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any(
                "Preencha o nome da agenda." in str(message)
                for message in messages
            )
        )

        self.assertEqual(Schedule.objects.count(), 1)

    # edit_schedule

    def test_edit_schedule(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:edit_schedule",
                args=[self.schedule.id],
            ),
            {
                "name": "Agenda Atualizada",
                "description": "Nova descrição",
                "color": "#000000",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=agendas",
        )

        self.schedule.refresh_from_db()

        self.assertEqual(
            self.schedule.name,
            "Agenda Atualizada",
        )

    def test_edit_schedule_rejects_member_user(self):
        self.client.force_login(self.member_user)

        response = self.client.post(
            reverse(
                "schedules:edit_schedule",
                args=[self.schedule.id],
            ),
            {
                "name": "Tentativa de alteração",
            },
        )

        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any(
                "Você não tem permissão para isso." in str(message)
                for message in messages
            )
        )

        self.schedule.refresh_from_db()

        self.assertEqual(
            self.schedule.name,
            "Agenda de Teste",
        )

    # delete_schedule

    def test_delete_schedule(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:delete_schedule",
                args=[self.schedule.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=agendas",
        )

        self.assertFalse(
            Schedule.objects.filter(
                id=self.schedule.id
            ).exists()
        )

    def test_delete_schedule_rejects_member_user(self):
        self.client.force_login(self.member_user)

        response = self.client.post(
            reverse(
                "schedules:delete_schedule",
                args=[self.schedule.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any(
                "Você não tem permissão para isso." in str(message)
                for message in messages
            )
        )

        self.assertTrue(
            Schedule.objects.filter(
                id=self.schedule.id
            ).exists()
        )

    # add_participant

    def test_add_participant(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:add_participant",
                args=[self.schedule.id],
            ),
            {
                "username": "external",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            reverse(
                "schedules:view_schedule",
                args=[self.schedule.id],
            ),
        )

        self.assertTrue(
            Participant.objects.filter(
                schedule=self.schedule,
                user=self.external_user,
            ).exists()
        )

    def test_add_participant_rejects_nonexistent_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:add_participant",
                args=[self.schedule.id],
            ),
            {
                "username": "inexistente",
            },
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any(
                "Usuário não encontrado." in str(message)
                for message in messages
            )
        )

    def test_add_participant_rejects_duplicate_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:add_participant",
                args=[self.schedule.id],
            ),
            {
                "username": "member",
            },
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any(
                "Usuário já é participante." in str(message)
                for message in messages
            )
        )

    # remove_participant

    def test_remove_participant(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:remove_participant",
                args=[self.schedule.id],
            ),
            {
                "user_id": self.member_user.id,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            reverse(
                "schedules:view_schedule",
                args=[self.schedule.id],
            ),
        )

        self.assertFalse(
            Participant.objects.filter(
                schedule=self.schedule,
                user=self.member_user,
            ).exists()
        )

    def test_remove_participant_rejects_admin(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:remove_participant",
                args=[self.schedule.id],
            ),
            {
                "user_id": self.admin_user.id,
            },
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any(
                "Não é possível remover um administrador." in str(message)
                for message in messages
            )
        )

        self.assertTrue(
            Participant.objects.filter(
                schedule=self.schedule,
                user=self.admin_user,
            ).exists()
        )

    # leave_schedule

    def test_leave_schedule(self):
        self.client.force_login(self.member_user)

        response = self.client.post(
            reverse(
                "schedules:leave_schedule",
                args=[self.schedule.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=agendas",
        )

        self.assertFalse(
            Participant.objects.filter(
                schedule=self.schedule,
                user=self.member_user,
            ).exists()
        )

    def test_leave_schedule_rejects_admin(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:leave_schedule",
                args=[self.schedule.id],
            )
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any(
                "Administradores não podem sair da agenda" in str(message)
                for message in messages
            )
        )

        self.assertTrue(
            Participant.objects.filter(
                schedule=self.schedule,
                user=self.admin_user,
            ).exists()
        )

    def test_validate_participant_username_rejects_non_authenticated_user(self):
        response = self.client.get(
            reverse("schedules:validate_participant_username")
        )

        self.assertEqual(response.status_code, 302)

    def test_validate_participant_username_rejects_empty_username(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("schedules:validate_participant_username"),
            {"username": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"valid": false')
        self.assertEqual(response.json()["message"], "Digite o nome do usuário para adicionar.")

    def test_validate_participant_username_rejects_unknown_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("schedules:validate_participant_username"),
            {"username": "inexistente"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["valid"], False)
        self.assertEqual(
            response.json()["message"],
            "Usuário não encontrado. Verifique o nome e tente novamente."
        )

    def test_validate_participant_username_accepts_known_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("schedules:validate_participant_username"),
            {"username": "member"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["valid"], True)
        self.assertContains(response, '"level": "success"')
        self.assertEqual(response.json()["username"], "member")

    def test_view_schedule_redirects_for_participant(self):
        self.client.force_login(self.member_user)

        response = self.client.get(
            reverse(
                "schedules:view_schedule",
                args=[self.schedule.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=agendas",
        )

    def test_view_schedule_rejects_non_participant_user(self):
        self.client.force_login(self.external_user)

        response = self.client.get(
            reverse(
                "schedules:view_schedule",
                args=[self.schedule.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem acesso a essa agenda." in str(message)
                for message in messages
            )
        )

    def test_main_calendar_view_handles_invalid_month_and_year(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("schedules:main_calendar_view"),
            {"mes": "13", "ano": "abcd"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["month"], date.today().month)
        self.assertEqual(response.context["year"], date.today().year)

    def test_main_calendar_view_filters_activities_by_kind_and_category(self):
        self.client.force_login(self.admin_user)

        today = date.today()
        Activity.objects.create(
            schedule=self.schedule,
            title="Evento de teste",
            kind="event",
            activity_type="class",
            date=today,
            start_time="10:00",
        )
        Activity.objects.create(
            schedule=self.schedule,
            title="Tarefa de teste",
            kind="task",
            activity_type="study",
            date=today,
        )

        response = self.client.get(
            reverse("schedules:main_calendar_view"),
            {"kind": ["event"], "category": ["class"]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_activities"], 1)
        self.assertIn(today.day, response.context["activities_by_day"])
        self.assertEqual(len(response.context["activities_by_day"][today.day]), 1)

    def test_create_schedule_shows_warning_for_unknown_participants(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("schedules:create_schedule"),
            {
                "name": "Agenda com participantes",
                "participant_usernames": ["external", "inexistente"],
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=agendas",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Alguns usuários não foram adicionados" in str(message)
                for message in messages
            )
        )
        self.assertTrue(
            Participant.objects.filter(
                schedule__name="Agenda com participantes",
                user=self.external_user,
            ).exists()
        )

    def test_create_schedule_get_redirects_to_agendas(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("schedules:create_schedule"))

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=agendas",
        )

    def test_quick_create_activity_rejects_missing_kind(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "activity_type": "class",
                "date": date.today().isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "O tipo da atividade é obrigatório." in str(message)
                for message in messages
            )
        )

    def test_quick_create_activity_rejects_missing_category(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "date": date.today().isoformat(),
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "A categoria da atividade é obrigatória." in str(message)
                for message in messages
            )
        )

    def test_remove_participant_rejects_non_admin_user(self):
        self.client.force_login(self.member_user)

        response = self.client.post(
            reverse(
                "schedules:remove_participant",
                args=[self.schedule.id],
            ),
            {"user_id": self.admin_user.id},
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem permissão para isso." in str(message)
                for message in messages
            )
        )

    def test_delete_activity_rejects_member_user(self):
        self.client.force_login(self.member_user)

        activity = Activity.objects.create(
            schedule=self.schedule,
            title="Tarefa para não deletar",
            kind="task",
            activity_type="study",
            date=date.today(),
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

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem permissão para isso." in str(message)
                for message in messages
            )
        )

        self.assertTrue(
            Activity.objects.filter(id=activity.id).exists()
        )

    def test_logout_view_logs_out_authenticated_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(reverse("schedules:logout"))

        self.assertRedirects(response, reverse("accounts:login_page"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_create_activity_rejects_missing_fields(self):
        self.client.force_login(self.admin_user)

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

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Preencha todos os campos obrigatórios." in str(message)
                for message in messages
            )
        )

    def test_create_activity_rejects_event_without_date(self):
        self.client.force_login(self.admin_user)

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

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Eventos precisam de uma data." in str(message)
                for message in messages
            )
        )

    def test_create_activity_get_redirects_to_calendario(self):
        self.client.force_login(self.admin_user)

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
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "Aula de amanhã",
                "kind": "event",
                "activity_type": "class",
                "date": date.today().isoformat(),
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

    def test_create_activity_allows_admin_user(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "Estudar Python",
                "kind": "task",
                "activity_type": "study",
                "date": "2026-06-20",
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

    def test_create_activity_rejects_member_user(self):
        self.client.force_login(self.member_user)

        response = self.client.post(
            reverse(
                "schedules:create_activity",
                args=[self.schedule.id],
            ),
            {
                "title": "Tarefa proibida",
                "kind": "task",
                "activity_type": "study",
                "date": "2026-06-20",
            },
        )

        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem permissão para isso." in str(message)
                for message in messages
            )
        )

    def test_quick_create_activity_rejects_non_participant(self):
        self.client.force_login(self.external_user)

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "activity_type": "class",
                "date": "2026-06-20",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem acesso a essa agenda." in str(message)
                for message in messages
            )
        )

    def test_quick_create_activity_rejects_member_user(self):
        self.client.force_login(self.member_user)

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "activity_type": "class",
                "date": "2026-06-20",
            },
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem permissão para criar atividades nessa agenda." in str(message)
                for message in messages
            )
        )

    def test_quick_create_activity_creates_activity(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("schedules:quick_create_activity"),
            {
                "schedule_id": self.schedule.id,
                "title": "Evento rápido",
                "kind": "event",
                "activity_type": "class",
                "date": "2026-06-20",
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

    def test_edit_activity_updates_activity(self):
        self.client.force_login(self.admin_user)

        activity = Activity.objects.create(
            schedule=self.schedule,
            title="Tarefa antiga",
            kind="task",
            activity_type="study",
            date="2026-06-20",
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
        self.client.force_login(self.member_user)

        activity = Activity.objects.create(
            schedule=self.schedule,
            title="Tarefa antiga",
            kind="task",
            activity_type="study",
            date="2026-06-20",
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

        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem permissão para isso." in str(message)
                for message in messages
            )
        )

    def test_delete_activity_deletes_activity(self):
        self.client.force_login(self.admin_user)

        activity = Activity.objects.create(
            schedule=self.schedule,
            title="Tarefa para remover",
            kind="task",
            activity_type="study",
            date="2026-06-20",
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
        self.client.force_login(self.admin_user)

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

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Atividade não encontrada." in str(message)
                for message in messages
            )
        )

    def test_quick_create_activity_get_redirects_to_calendario(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("schedules:quick_create_activity"))

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=calendario",
        )

    def test_sync_event_checks_creates_past_event_check_and_removes_future_check(self):
        self.client.force_login(self.admin_user)

        today = date.today()
        past_event = Activity.objects.create(
            schedule=self.schedule,
            title="Evento passado",
            kind="event",
            activity_type="class",
            date=today.replace(day=max(1, today.day - 1)),
            end_time="10:00",
        )
        future_event = Activity.objects.create(
            schedule=self.schedule,
            title="Evento futuro",
            kind="event",
            activity_type="class",
            date=today.replace(day=min(28, today.day + 1)),
            end_time="10:00",
        )

        ActivityCheck.objects.create(activity=future_event, user=self.admin_user)

        views.sync_event_checks(self.admin_user, [self.schedule.id])

        self.assertTrue(
            ActivityCheck.objects.filter(activity=past_event, user=self.admin_user).exists()
        )
        self.assertFalse(
            ActivityCheck.objects.filter(activity=future_event, user=self.admin_user).exists()
        )

    def test_sync_schedule_members_adds_and_removes_members_and_returns_missing_usernames(self):
        Participant.objects.create(
            schedule=self.schedule,
            user=self.external_user,
            role=Participant.Role.MEMBER,
        )

        missing_usernames = views.sync_schedule_members(
            self.schedule,
            ["external", "inexistente"],
        )

        self.assertEqual(missing_usernames, ["inexistente"])
        self.assertTrue(
            Participant.objects.filter(
                schedule=self.schedule,
                user=self.external_user,
                role=Participant.Role.MEMBER,
            ).exists()
        )

    def test_normalize_priority_returns_default_for_invalid_value(self):
        self.assertEqual(
            views.normalize_priority("invalid_priority"),
            Activity.Priority.IMPORTANT,
        )

    def test_extract_activity_type_colors_uses_default_for_empty_values(self):
        colors = views.extract_activity_type_colors(
            {"activity_type_color_class": "", "activity_type_color_exam": ""}
        )

        self.assertEqual(
            colors["class"],
            views.ACTIVITY_TYPE_COLOR_DEFAULTS["class"],
        )

    def test_resolve_activity_color_prefers_activity_color_then_schedule_color_then_default(self):
        schedule = self.schedule
        activity_with_color = Activity.objects.create(
            schedule=schedule,
            title="Com cor",
            kind="task",
            activity_type="class",
            date=date.today(),
            color="#123456",
        )
        activity_without_color = Activity.objects.create(
            schedule=schedule,
            title="Sem cor",
            kind="task",
            activity_type="class",
            date=date.today(),
        )

        self.assertEqual(
            views.resolve_activity_color(activity_with_color),
            "#123456",
        )
        self.assertEqual(
            views.resolve_activity_color(activity_without_color),
            schedule.activity_type_colors["class"],
        )

    def test_attach_resolved_colors_adds_resolved_color_to_activities(self):
        activity = Activity.objects.create(
            schedule=self.schedule,
            title="Teste cor",
            kind="task",
            activity_type="class",
            date=date.today(),
        )

        activities = views.attach_resolved_colors(Activity.objects.filter(id=activity.id))

        self.assertTrue(hasattr(activities[0], "resolved_color"))

    def test_toggle_check_marks_and_unmarks_activity(self):
        self.client.force_login(self.member_user)

        activity = Activity.objects.create(
            schedule=self.schedule,
            title="Tarefa a ser marcada",
            kind="task",
            activity_type="study",
            date="2026-06-20",
        )

        response = self.client.post(
            reverse(
                "schedules:toggle_check",
                args=[self.schedule.id, activity.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=tarefas",
        )

        self.assertTrue(
            ActivityCheck.objects.filter(
                activity=activity,
                user=self.member_user,
            ).exists()
        )

        response = self.client.post(
            reverse(
                "schedules:toggle_check",
                args=[self.schedule.id, activity.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("schedules:main_calendar_view") + "?tab=tarefas",
        )

        self.assertFalse(
            ActivityCheck.objects.filter(
                activity=activity,
                user=self.member_user,
            ).exists()
        )

    def test_toggle_check_rejects_non_participant(self):
        self.client.force_login(self.external_user)

        activity = Activity.objects.create(
            schedule=self.schedule,
            title="Tarefa protegida",
            kind="task",
            activity_type="study",
            date="2026-06-20",
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

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Você não tem acesso a essa agenda." in str(message)
                for message in messages
            )
        )
