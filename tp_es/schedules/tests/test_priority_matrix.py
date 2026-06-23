from django.urls import reverse
from schedules.tests.base import BaseScheduleTestCase
from schedules.models import Activity, ActivityCheck, Schedule

class PriorityMatrixTests(BaseScheduleTestCase):
    def setUp(self):
        super().setUp()
        self._login_admin()

    def test_priority_matrix_tab_view(self):
        response = self.client.get(reverse("schedules:main_calendar_view") + "?tab=matriz")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "schedules/calendar.html")
        self.assertEqual(response.context["active_tab"], "matriz")
        self.assertIn("priority_sections", response.context)

    def test_priority_matrix_distribution(self):
        # Create activities with each priority
        act_ui = self._create_activity(
            title="Urgent & Important Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.URGENT_IMPORTANT,
        )
        act_u = self._create_activity(
            title="Urgent Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.URGENT,
        )
        act_i = self._create_activity(
            title="Important Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.IMPORTANT,
        )
        act_nuni = self._create_activity(
            title="Not Urgent Not Important Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.NOT_URGENT_NOT_IMPORTANT,
        )

        response = self.client.get(reverse("schedules:main_calendar_view") + "?tab=matriz")
        self.assertEqual(response.status_code, 200)
        
        priority_sections = response.context["priority_sections"]
        
        # Verify mapping of sections
        sections_dict = {sec["value"]: sec["tasks"] for sec in priority_sections}
        
        self.assertIn(act_ui, sections_dict[Activity.Priority.URGENT_IMPORTANT])
        self.assertIn(act_u, sections_dict[Activity.Priority.URGENT])
        self.assertIn(act_i, sections_dict[Activity.Priority.IMPORTANT])
        self.assertIn(act_nuni, sections_dict[Activity.Priority.NOT_URGENT_NOT_IMPORTANT])

    def test_priority_matrix_excludes_checked_tasks(self):
        # Create a task
        task = self._create_activity(
            title="Pending Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.IMPORTANT,
        )
        # Create a completed task
        completed_task = self._create_activity(
            title="Completed Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.IMPORTANT,
        )
        ActivityCheck.objects.create(
            activity=completed_task,
            user=self.admin_user,
        )

        response = self.client.get(reverse("schedules:main_calendar_view") + "?tab=matriz")
        self.assertEqual(response.status_code, 200)
        
        priority_sections = response.context["priority_sections"]
        important_tasks = next(
            sec["tasks"] for sec in priority_sections if sec["value"] == Activity.Priority.IMPORTANT
        )
        
        # Uncompleted task should be in the matrix
        self.assertIn(task, important_tasks)
        # Completed task should be excluded from the matrix
        self.assertNotIn(completed_task, important_tasks)

    def test_priority_matrix_resolved_colors(self):
        # Create a task with specific color
        task_with_color = self._create_activity(
            title="Colored Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.IMPORTANT,
            color="#FF0000",
        )
        # Create a task without color (resolves to activity type color default)
        task_default_color = self._create_activity(
            title="Default Color Task",
            kind=Activity.Kind.TASK,
            priority=Activity.Priority.IMPORTANT,
            color="",
        )

        response = self.client.get(reverse("schedules:main_calendar_view") + "?tab=matriz")
        self.assertEqual(response.status_code, 200)
        
        priority_sections = response.context["priority_sections"]
        important_tasks = next(
            sec["tasks"] for sec in priority_sections if sec["value"] == Activity.Priority.IMPORTANT
        )
        
        # Verify colored task color
        colored_task_in_context = next(t for t in important_tasks if t.id == task_with_color.id)
        self.assertEqual(colored_task_in_context.resolved_color, "#FF0000")

        # Verify default task color
        default_task_in_context = next(t for t in important_tasks if t.id == task_default_color.id)
        schedule_type_color = self.schedule.activity_type_colors.get(task_default_color.activity_type)
        self.assertEqual(default_task_in_context.resolved_color, schedule_type_color)
