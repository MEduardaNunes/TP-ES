    
from schedules.tests.base import BaseScheduleTestCase
from schedules import views
from schedules.models import Activity, Participant

class UtilsTests(BaseScheduleTestCase):  
    # --- testes de sincronização de mebros ---
    def test_sync_schedule_members_returns_missing_usernames(self):
        missing_usernames = views.sync_schedule_members(
            self.schedule,
            ["inexistente"],
        )
        self.assertEqual(missing_usernames, ["inexistente"])
    
    def test_sync_schedule_members_adds_or_keeps_valid_users(self):
        self._create_participant(
            user=self.external_user,
            role=Participant.Role.MEMBER,
        )

        views.sync_schedule_members(
            self.schedule,
            ["external"],
        )

        self.assertTrue(
            Participant.objects.filter(
                schedule=self.schedule,
                user=self.external_user,
                role=Participant.Role.MEMBER,
            ).exists()
        )

    # --- testes de utilitários ---
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

    # --- testes de cores ---
    def test_resolve_activity_color_returns_activity_color_when_present(self):
        activity_with_color = self._create_activity(
            schedule=self.schedule,
            title="Com cor",
            kind="task",
            activity_type="class",
            date=self.REFERENCE_DATE,
            color="#123456",
        )
        self.assertEqual(
            views.resolve_activity_color(activity_with_color),
            "#123456",
        )
        
    def test_resolve_activity_color_returns_schedule_color_when_activity_color_is_blank(self):
        activity_without_color = self._create_activity(
            schedule=self.schedule,
            title="Sem cor",
            kind="task",
            activity_type="class",
            date=self.REFERENCE_DATE,
        )
        self.assertEqual(
            views.resolve_activity_color(activity_without_color),
            self.schedule.activity_type_colors["class"],
        )

    def test_attach_resolved_colors_adds_resolved_color_to_activities(self):
        activity = self._create_activity(
            schedule=self.schedule,
            title="Teste cor",
            kind="task",
            activity_type="class",
            date=self.REFERENCE_DATE,
        )

        activities = list(
            views.attach_resolved_colors(
                Activity.objects.filter(id=activity.id)
            )
        )
            
        self.assertEqual(
            activities[0].resolved_color,
            self.schedule.activity_type_colors["class"],
        )

    def test_normalize_priority_returns_valid_priority(self):
        self.assertEqual(
            views.normalize_priority("urgent_important"),
            Activity.Priority.URGENT_IMPORTANT,
        )

    def test_resolve_main_tab_with_referer(self):
        from django.test import RequestFactory
        factory = RequestFactory()
        
        # Test request with referer containing a valid tab
        request = factory.get("/some-path/")
        request.META["HTTP_REFERER"] = "http://testserver/calendar/?tab=matriz"
        self.assertEqual(views.resolve_main_tab(request), "matriz")

        # Test request with referer containing an invalid tab
        request = factory.get("/some-path/")
        request.META["HTTP_REFERER"] = "http://testserver/calendar/?tab=invalid_tab"
        self.assertEqual(views.resolve_main_tab(request), "calendario")

        