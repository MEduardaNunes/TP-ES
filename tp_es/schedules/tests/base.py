from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from datetime import date

from schedules.models import Activity, Participant, Schedule

class BaseScheduleTestCase(TestCase):
    REFERENCE_DATE = date(2026, 6, 21)
    PAST_DATE = date(2026, 6, 20)
    FUTURE_DATE = date(2026, 6, 22)
    EVENT_DAY = date(2026, 6, 23)
    
    ADMIN_PASSWORD = "senha123"
    
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_user(
            username="admin",
            password=cls.ADMIN_PASSWORD,
        )

        cls.member_user = get_user_model().objects.create_user(
            username="member",
            password=cls.ADMIN_PASSWORD,
        )

        cls.external_user = get_user_model().objects.create_user(
            username="external",
            password=cls.ADMIN_PASSWORD,
        )

        cls.schedule = Schedule.objects.create(
            name="Agenda de Teste",
            description="Descrição da agenda",
            color="#59e7ec",
        )

        Participant.objects.create(
            schedule=cls.schedule,
            user=cls.admin_user,
            role=Participant.Role.ADMIN,
        )

        Participant.objects.create(
            schedule=cls.schedule,
            user=cls.member_user,
            role=Participant.Role.MEMBER,
        )
    
    def _login_admin(self):
        self.client.login(username=self.admin_user.username, password=self.ADMIN_PASSWORD)

    def _login_member(self):
        self.client.login(username=self.member_user.username, password=self.ADMIN_PASSWORD)

    def _login_external(self):
        self.client.login(username=self.external_user.username, password=self.ADMIN_PASSWORD)

    def _assert_message(self, response, text):
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(text in str(m) for m in messages), f"expected message containing: {text}")
    
    def _create_schedule(self, **kwargs):
        data = {
            "name": "Agenda Helper",
            "description": "desc",
            "color": "#abcdef",
        }
        data.update(kwargs)
        return Schedule.objects.create(**data)

    def _create_participant(self, user, schedule=None, role=Participant.Role.MEMBER):
        return Participant.objects.create(
            schedule=schedule or self.schedule, 
            user=user, 
            role=role
        )

    def _create_activity(self, **kwargs):
        defaults = {
            "schedule": self.schedule,
            "title": "Atividade de teste",
            "kind": "task",
            "activity_type": "study",
            "date": self.REFERENCE_DATE,
        }
        defaults.update(kwargs)
        return Activity.objects.create(**defaults)