from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime, time
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from functools import wraps
import calendar
from urllib.parse import urlparse, parse_qs
from accounts.models import UserThemePreference
from .models import Schedule, Participant, Activity, ActivityCheck, DEFAULT_ACTIVITY_TYPE_COLORS
from django.contrib.auth import logout, login
from django.db.models import Exists, OuterRef


ACTIVITY_TYPE_COLOR_KEYS = [
    Activity.Type.CLASS,
    Activity.Type.EXAM,
    Activity.Type.ASSIGNMENT,
    Activity.Type.STUDY,
    Activity.Type.MEETING,
    Activity.Type.PRESENTATION,
    Activity.Type.PERSONAL,
]

ACTIVITY_TYPE_COLOR_DEFAULTS = {
    Activity.Type.CLASS: DEFAULT_ACTIVITY_TYPE_COLORS[Activity.Type.CLASS],
    Activity.Type.EXAM: DEFAULT_ACTIVITY_TYPE_COLORS[Activity.Type.EXAM],
    Activity.Type.ASSIGNMENT: DEFAULT_ACTIVITY_TYPE_COLORS[Activity.Type.ASSIGNMENT],
    Activity.Type.STUDY: DEFAULT_ACTIVITY_TYPE_COLORS[Activity.Type.STUDY],
    Activity.Type.MEETING: DEFAULT_ACTIVITY_TYPE_COLORS[Activity.Type.MEETING],
    Activity.Type.PRESENTATION: DEFAULT_ACTIVITY_TYPE_COLORS[Activity.Type.PRESENTATION],
    Activity.Type.PERSONAL: DEFAULT_ACTIVITY_TYPE_COLORS[Activity.Type.PERSONAL],
}

PRIORITY_MATRIX_SECTIONS = [
    {
        "value": Activity.Priority.URGENT_IMPORTANT,
        "title": "Fazer agora",
        "label": "Urgente e importante",
        "description": "Entregas e provas que precisam de atenção imediata.",
    },
    {
        "value": Activity.Priority.URGENT,
        "title": "Resolver em breve",
        "label": "Urgente",
        "description": "Pendências com prazo curto que podem ser delegadas ou aceleradas.",
    },
    {
        "value": Activity.Priority.IMPORTANT,
        "title": "Planejar com foco",
        "label": "Importante",
        "description": "Estudos e preparações que movem seu desempenho, mas não exigem pressa.",
    },
    {
        "value": Activity.Priority.NOT_URGENT_NOT_IMPORTANT,
        "title": "Baixa prioridade",
        "label": "Não urgente e nem importante",
        "description": "Atividades que podem esperar ou ser revisadas depois.",
    },
]

VALID_MAIN_TABS = {"calendario", "eventos", "tarefas", "matriz", "agendas"}


def resolve_main_tab(request, fallback="calendario"):
    referer_tab = ""
    referer = request.META.get("HTTP_REFERER", "")
    if referer:
        parsed = urlparse(referer)
        referer_tab = (parse_qs(parsed.query).get("tab") or [""])[0]

    tab = (request.POST.get("tab") or request.GET.get("tab") or referer_tab or fallback or "calendario").strip()
    return tab if tab in VALID_MAIN_TABS else fallback


def redirect_main_calendar_with_tab(request, fallback="calendario"):
    tab = resolve_main_tab(request, fallback=fallback)
    return redirect(reverse("schedules:main_calendar_view") + f"?tab={tab}")


def normalize_priority(raw_priority, default=Activity.Priority.IMPORTANT):
    if raw_priority in Activity.Priority.values:
        return raw_priority
    return default


def extract_activity_type_colors(post_data):
    colors = {}
    for activity_type in ACTIVITY_TYPE_COLOR_KEYS:
        raw_color = (post_data.get(f"activity_type_color_{activity_type}") or "").strip()
        colors[activity_type] = raw_color or ACTIVITY_TYPE_COLOR_DEFAULTS[activity_type]
    return colors


def resolve_activity_color(activity):
    schedule_type_colors = activity.schedule.activity_type_colors or {}
    return (
        activity.color
        or schedule_type_colors.get(activity.activity_type)
        or ACTIVITY_TYPE_COLOR_DEFAULTS.get(activity.activity_type)
        or activity.schedule.color
        or "#59e7ec"
    )


def attach_resolved_colors(activities):
    items = list(activities)
    for activity in items:
        activity.resolved_color = resolve_activity_color(activity)
    return items

def sync_event_checks(user, schedule_ids):
    now = timezone.localtime()
    today = now.date()

    events = Activity.objects.filter(
        schedule_id__in=schedule_ids,
        kind=Activity.Kind.EVENT,
    )

    for event in events:
        if event.end_time:
            dt = datetime.combine(event.date, event.end_time)
        else:
            dt = datetime.combine(event.date, time(23, 59))

        dt = timezone.make_aware(dt)
        is_past = dt < now

        check_exists = ActivityCheck.objects.filter(
            activity=event,
            user=user
        ).exists()

        if is_past and not check_exists:
            ActivityCheck.objects.create(
                activity=event,
                user=user
            )

        elif not is_past and check_exists:
            ActivityCheck.objects.filter(
                activity=event,
                user=user
            ).delete()

def sync_schedule_members(schedule, selected_usernames):
    """Mantém os membros da agenda sincronizados com os nomes enviados pelo formulário."""
    User = get_user_model()
    normalized_usernames = {
        str(username).strip()
        for username in selected_usernames
        if str(username).strip()
    }

    matched_users = list(User.objects.filter(username__in=normalized_usernames))
    matched_usernames = {user.username for user in matched_users}
    missing_usernames = sorted(normalized_usernames - matched_usernames)

    current_admin_ids = set(
        schedule.participants.filter(role=Participant.Role.ADMIN).values_list("user_id", flat=True)
    )
    matched_user_ids = {user.id for user in matched_users} - current_admin_ids

    existing_member_ids = set(
        schedule.participants.filter(role=Participant.Role.MEMBER).values_list("user_id", flat=True)
    )

    member_ids_to_remove = existing_member_ids - matched_user_ids
    if member_ids_to_remove:
        schedule.participants.filter(
            role=Participant.Role.MEMBER,
            user_id__in=member_ids_to_remove,
        ).delete()

    member_ids_to_add = matched_user_ids - existing_member_ids
    if member_ids_to_add:
        Participant.objects.bulk_create(
            [
                Participant(
                    schedule=schedule,
                    user=user,
                    role=Participant.Role.MEMBER,
                )
                for user in matched_users
                if user.id in member_ids_to_add
            ]
        )

    return missing_usernames

@login_required
def validate_participant_username(request):
    username = (request.GET.get("username") or "").strip()
    if not username:
        return JsonResponse({
            "valid": False,
            "level": "warning",
            "message": "Digite o nome do usuário para adicionar.",
        })

    user_exists = get_user_model().objects.filter(username=username).exists()
    if not user_exists:
        return JsonResponse({
            "valid": False,
            "level": "warning",
            "message": "Usuário não encontrado. Verifique o nome e tente novamente.",
        })

    return JsonResponse({
        "valid": True,
        "level": "success",
        "message": f'Usuário "{username}" encontrado e adicionado.',
        "username": username,
    })

@login_required
def calendar_view(request):
    """Lista todas as agendas do usuário logado."""
    participations = request.user.participations.select_related("schedule").all()
    return render(request, "calendar.html", {"participations": participations})

def get_participant(user, schedule):
    try:
        return schedule.participants.get(user=user)
    except Participant.DoesNotExist:
        return None

def participant_required(view_func):
    """Garante que o usuário é participante da agenda."""
    @login_required
    @wraps(view_func)  
    def wrapper(request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        participant = get_participant(request.user, schedule)
        if not participant:
            messages.error(request, "Você não tem acesso a essa agenda.")
            return redirect_main_calendar_with_tab(request)
        return view_func(request, schedule, participant, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Garante que o usuário é admin da agenda."""
    @login_required
    @wraps(view_func)  
    def wrapper(request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        participant = get_participant(request.user, schedule)
        if not participant or not participant.is_admin:
            messages.error(request, "Você não tem permissão para isso.")
            return redirect_main_calendar_with_tab(request)
        return view_func(request, schedule, participant, *args, **kwargs)
    return wrapper

@login_required
def main_calendar_view(request):
    """
    Exibe o calendário mensal com atividades do usuário.
    Inclui atividades do mês, eventos futuros e tarefas pendentes na aba lateral.
    """
    today = date.today()
    active_tab = resolve_main_tab(request)

    try:
        month = int(request.GET.get("mes", today.month))
        year = int(request.GET.get("ano", today.year))
        if not (1 <= month <= 12):
            month, year = today.month, today.year
    except (ValueError, TypeError):
        month, year = today.month, today.year
 
    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)
    next_month, next_year = (1, year + 1) if month == 12 else (month + 1, year)
 
    cal = calendar.Calendar(firstweekday=6)
    calendar_days = list(cal.itermonthdays(year, month))
 
    participations = request.user.participations.select_related("schedule").prefetch_related(
        "schedule__participants__user"
    ).all()
    schedule_ids = participations.values_list("schedule_id", flat=True)
    sync_event_checks(request.user, schedule_ids)
    
    filter_kinds = request.GET.getlist("kind")
    filter_categories = request.GET.getlist("category")

    if not filter_kinds:
        filter_kinds = ["event", "task"]

    if not filter_categories:
        filter_categories = [
        "class", "exam", "assignment",
        "study", "meeting", "presentation", "personal"
        ]
  
    admin_participations = request.user.participations.select_related("schedule").prefetch_related(
        "schedule__participants__user"
    ).filter(
        role=Participant.Role.ADMIN
    )
    admin_schedule_ids = list(admin_participations.values_list("schedule_id", flat=True))
    
    user_checks = ActivityCheck.objects.filter(
    activity_id=OuterRef("pk"),
    user=request.user
)
 
    activities = Activity.objects.filter(
        schedule_id__in=schedule_ids,
        date__year=year,
        date__month=month,
    ).annotate(
        is_checked_for_user=Exists(user_checks)
    ).select_related("schedule").order_by("start_time")
    
    if filter_kinds:
        activities = activities.filter(kind__in=filter_kinds)
    if filter_categories:   
        activities = activities.filter(activity_type__in=filter_categories)
    
    checked_ids = set(
    ActivityCheck.objects.filter(
        user=request.user,
        activity__schedule_id__in=schedule_ids,
    ).values_list("activity_id", flat=True)
    )
 
    activities_by_day = {}
    for activity in activities:
        if activity.date:
            activity.resolved_color = resolve_activity_color(activity)
            day = activity.date.day
            activities_by_day.setdefault(day, []).append(activity)
 
    # Atividades futuras ou não concluídas para a aba lateral
    future_events = attach_resolved_colors(Activity.objects.filter(
        schedule_id__in=schedule_ids,
        kind=Activity.Kind.EVENT,
        date__gte=today,
    ).exclude(
        checks__user=request.user
    ).select_related("schedule").order_by("date", "start_time"))

    completed_events = attach_resolved_colors(Activity.objects.filter(
        schedule_id__in=schedule_ids,
        kind=Activity.Kind.EVENT,
        checks__user=request.user,
    ).select_related("schedule").order_by("date", "start_time"))
 
    pending_tasks_base = Activity.objects.filter(
        schedule_id__in=schedule_ids,
        kind=Activity.Kind.TASK,
    ).exclude(
        checks__user=request.user
    ).select_related("schedule")

    pending_tasks = attach_resolved_colors(
        pending_tasks_base.order_by("date", "start_time", "created_at")
    )

    # Matrix shows all unchecked activities (events + tasks) organized by priority
    all_pending_activities = Activity.objects.filter(
        schedule_id__in=schedule_ids,
    ).exclude(
        checks__user=request.user
    ).select_related("schedule")

    priority_sections = [
        {
            "value": section["value"],
            "title": section["title"],
            "label": section["label"],
            "description": section["description"],
            "tasks": attach_resolved_colors(
                all_pending_activities.filter(priority=section["value"]).order_by(
                    "date", "start_time", "created_at"
                )
            ),
        }
        for section in PRIORITY_MATRIX_SECTIONS
    ]
 
    month_names = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    completed_tasks = attach_resolved_colors(Activity.objects.filter(
        schedule_id__in=schedule_ids,
        kind=Activity.Kind.TASK,
        checks__user=request.user,
    ).select_related("schedule").order_by("date"))
 
    return render(request, "schedules/calendar.html", {
        "participations": participations,
        "admin_participations": admin_participations,
        "calendar_days": calendar_days,
        "activities_by_day": activities_by_day,
        "total_activities": activities.count(),
        "month": month,
        "year": year,
        "month_name": month_names[month],
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "today_day": today.day,
        "today_month": today.month,
        "today_year": today.year,
        "future_events": future_events,
        "pending_tasks": pending_tasks,
        "priority_sections": priority_sections,
        "admin_schedule_ids": admin_schedule_ids,
        "checked_ids": checked_ids,
        "completed_events": completed_events,
        "completed_tasks": completed_tasks,
        "activity_type_color_defaults": ACTIVITY_TYPE_COLOR_DEFAULTS,
        "active_tab": active_tab,
    })
    
@login_required
def create_schedule(request):
    """Cria uma nova agenda para o usuário logado."""
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "").strip()
        color = request.POST.get("color", "#59e7ec")
 
        if not name:
            messages.error(request, "Preencha o nome da agenda.")
            return redirect("schedules:create_schedule")
 
        schedule = Schedule.objects.create(
            name=name,
            description=description,
            color=color,
            icon_emoji=request.POST.get("icon_emoji", "").strip(),
            icon_image=request.FILES.get("icon_image"),
            activity_type_colors=extract_activity_type_colors(request.POST),
        )
        Participant.objects.create(
            schedule=schedule,
            user=request.user,
            role=Participant.Role.ADMIN,
        )
        missing_usernames = sync_schedule_members(schedule, request.POST.getlist("participant_usernames"))
        if missing_usernames:
            messages.warning(
                request,
                "Alguns usuários não foram adicionados porque não existem: "
                + ", ".join(missing_usernames)
            )
        messages.success(request, "Agenda criada com sucesso.")
        return redirect(reverse("schedules:main_calendar_view") + "?tab=agendas")
 
    return redirect_main_calendar_with_tab(request, fallback="agendas")

@admin_required
def edit_schedule(request, schedule, participant):
    if request.method == "POST":
        schedule.name = request.POST.get("name", schedule.name)
        schedule.description = request.POST.get("description", schedule.description).strip()
        schedule.color = request.POST.get("color", schedule.color)
        schedule.icon_emoji = request.POST.get("icon_emoji", schedule.icon_emoji).strip()
        if request.POST.get("clear_icon_image") == "1" and schedule.icon_image:
            schedule.icon_image.delete(save=False)
            schedule.icon_image = None
        if request.FILES.get("icon_image"):
            schedule.icon_image = request.FILES["icon_image"]
        schedule.activity_type_colors = extract_activity_type_colors(request.POST)
        schedule.save()
        missing_usernames = sync_schedule_members(schedule, request.POST.getlist("participant_usernames"))
        if missing_usernames:
            messages.warning(
                request,
                "Alguns usuários não foram adicionados porque não existem: "
                + ", ".join(missing_usernames)
            )
        messages.success(request, "Agenda atualizada com sucesso.")
        return redirect(reverse("schedules:main_calendar_view") + "?tab=agendas")
 
    return redirect_main_calendar_with_tab(request, fallback="agendas")

@admin_required
@require_POST
def delete_schedule(request, schedule, participant):
    schedule.delete()
    messages.success(request, "Agenda deletada com sucesso.")
    return redirect(reverse('schedules:main_calendar_view') + '?tab=agendas')


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu do sistema com sucesso!")
    return redirect('accounts:login_page')

@participant_required
def view_schedule(request, schedule, participant):
    """Exibe os detalhes de uma agenda específica com suas atividades."""
    activities = schedule.activities.order_by("date", "start_time")
 
    checked_ids = set(
        ActivityCheck.objects.filter(
            user=request.user,
            activity__schedule=schedule,
        ).values_list("activity_id", flat=True)
    )
 
    return redirect_main_calendar_with_tab(request, fallback="agendas")
    
@admin_required
def add_participant(request, schedule, participant):
    if request.method == "POST":
        username = request.POST.get("username")
        User = get_user_model()
 
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect("schedules:view_schedule", schedule_id=schedule.id)
 
        if schedule.participants.filter(user=user).exists():
            messages.error(request, "Usuário já é participante.")
            return redirect("schedules:view_schedule", schedule_id=schedule.id)
 
        Participant.objects.create(
            schedule=schedule,
            user=user,
            role=Participant.Role.MEMBER
        )
        messages.success(request, "Participante adicionado.")
        return redirect("schedules:view_schedule", schedule_id=schedule.id)
 
    return redirect("schedules:view_schedule", schedule_id=schedule.id)

@admin_required
@require_POST
def remove_participant(request, schedule, participant):
    user_id = request.POST.get("user_id")
    target = get_object_or_404(Participant, schedule=schedule, user_id=user_id)
 
    if target.is_admin:
        messages.error(request, "Não é possível remover um administrador.")
        return redirect("schedules:view_schedule", schedule_id=schedule.id)
 
    target.delete()
    messages.success(request, "Participante removido.")
    return redirect("schedules:view_schedule", schedule_id=schedule.id)

@participant_required
@require_POST
def leave_schedule(request, schedule, participant):
    if participant.is_admin:
        messages.error(request, "Administradores não podem sair da agenda por essa opção.")
        return redirect(reverse('schedules:main_calendar_view') + '?tab=agendas')

    participant.delete()
    messages.success(request, "Você saiu da agenda com sucesso.")
    return redirect(reverse('schedules:main_calendar_view') + '?tab=agendas')

@admin_required
def create_activity(request, schedule, participant):
    """Cria uma nova atividade (evento ou tarefa) na agenda."""
    if request.method == "POST":
        title = request.POST.get("title")
        kind = request.POST.get("kind")
        activity_type_value = request.POST.get("activity_type")
 
        if not title or not kind or not activity_type_value:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return redirect_main_calendar_with_tab(request)
 
        date_value = request.POST.get("date") or None
        if kind == Activity.Kind.EVENT and not date_value:
            messages.error(request, "Eventos precisam de uma data.")
            return redirect_main_calendar_with_tab(request, fallback="eventos")
 
        preference, _ = UserThemePreference.objects.get_or_create(user=request.user)
        icon_emoji = request.POST.get("icon_emoji", "").strip() or preference.default_activity_icon_emoji

        Activity.objects.create(
            schedule=schedule,
            title=title,
            kind=kind,
            activity_type=activity_type_value,
            priority=normalize_priority(request.POST.get("priority")),
            date=date_value,
            start_time=request.POST.get("start_time") or None,
            end_time=request.POST.get("end_time") or None,
            notes=request.POST.get("notes", ""),
            color=request.POST.get("color", ""),
            icon_emoji=icon_emoji,
            icon_image=request.FILES.get("icon_image") or preference.default_activity_icon_image,
        )
        messages.success(request, "Atividade criada com sucesso.")
        tab_fallback = "eventos" if kind == Activity.Kind.EVENT else "tarefas"
        return redirect_main_calendar_with_tab(request, fallback=tab_fallback)
        # return redirect("schedules:view_schedule", schedule_id=schedule.id)
 
    return redirect_main_calendar_with_tab(request)
    
@login_required
def quick_create_activity(request):
    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")
        schedule = get_object_or_404(Schedule, id=schedule_id)
 
        participant = get_participant(request.user, schedule)
        if not participant:
            messages.error(request, "Você não tem acesso a essa agenda.")
            return redirect_main_calendar_with_tab(request)
 
        if not participant.is_admin:
            messages.error(request, "Você não tem permissão para criar atividades nessa agenda.")
            return redirect_main_calendar_with_tab(request)
 
        title = request.POST.get("title")
        kind = request.POST.get("kind")
        activity_type_value = request.POST.get("activity_type")
 
        if not title:
            messages.error(request, "O título é obrigatório.")
            return redirect_main_calendar_with_tab(request)
 
        if not kind:
            messages.error(request, "O tipo da atividade é obrigatório.")
            return redirect_main_calendar_with_tab(request)
 
        if not activity_type_value:
            messages.error(request, "A categoria da atividade é obrigatória.")
            return redirect_main_calendar_with_tab(request)
 
        date_value = request.POST.get("date") or None
 
        if kind == Activity.Kind.EVENT and not date_value:
            messages.error(request, "Eventos precisam de uma data.")
            return redirect_main_calendar_with_tab(request, fallback="eventos")
        
        notes = request.POST.get("notes", "").strip()
 
        preference, _ = UserThemePreference.objects.get_or_create(user=request.user)
        icon_emoji = request.POST.get("icon_emoji", "").strip() or preference.default_activity_icon_emoji

        Activity.objects.create(
            schedule=schedule,
            title=title,
            kind=kind,
            activity_type=activity_type_value,  
            priority=normalize_priority(request.POST.get("priority")),
            date=date_value,
            start_time=request.POST.get("start_time") or None,
            end_time=request.POST.get("end_time") or None,
            icon_emoji=icon_emoji,
            icon_image=request.FILES.get("icon_image") or preference.default_activity_icon_image,
            notes=notes,
        )
        messages.success(request, "Atividade criada com sucesso.")
        tab_fallback = "eventos" if kind == Activity.Kind.EVENT else "tarefas"
        return redirect_main_calendar_with_tab(request, fallback=tab_fallback)

    return redirect_main_calendar_with_tab(request)
    
@admin_required
def edit_activity(request, schedule, participant, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, schedule=schedule)
 
    if request.method == "POST":
        activity.title = request.POST.get("title", activity.title)
        activity.kind = request.POST.get("kind", activity.kind)
        activity.activity_type = request.POST.get("activity_type", activity.activity_type)
        activity.priority = normalize_priority(request.POST.get("priority"), activity.priority)
        activity.date = request.POST.get("date") or None
        activity.start_time = request.POST.get("start_time") or None
        activity.end_time = request.POST.get("end_time") or None
        activity.notes = request.POST.get("notes", activity.notes)
        activity.color = request.POST.get("color", activity.color)
        activity.icon_emoji = request.POST.get("icon_emoji", activity.icon_emoji).strip()
        if request.POST.get("clear_icon_image") == "1" and activity.icon_image:
            activity.icon_image.delete(save=False)
            activity.icon_image = None
        if request.POST.get("clear_icon_emoji") == "1":
            activity.icon_emoji = ""
        if request.FILES.get("icon_image"):
            activity.icon_image = request.FILES["icon_image"]
        activity.save()
        messages.success(request, "Atividade atualizada com sucesso.")
        tab = "eventos" if activity.kind == Activity.Kind.EVENT else "tarefas"
        return redirect_main_calendar_with_tab(request, fallback=tab)
 
    return redirect_main_calendar_with_tab(request)

    
@admin_required
@require_POST
def delete_activity(request, schedule, participant, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id, schedule=schedule)
    except Activity.DoesNotExist:
        messages.error(request, "Atividade não encontrada.")
        return redirect_main_calendar_with_tab(request)
    
    activity_kind = activity.kind
    activity.delete()
    messages.success(request, "Atividade deletada com sucesso.")
    tab = "eventos" if activity_kind == Activity.Kind.EVENT else "tarefas"
    return redirect_main_calendar_with_tab(request, fallback=tab)

@participant_required
@require_POST
def toggle_check(request, schedule, participant, activity_id):
    """Marca ou desmarca uma atividade como realizada/estudada para o usuário logado."""
    activity = get_object_or_404(Activity, id=activity_id, schedule=schedule)

    check, created = ActivityCheck.objects.get_or_create(
        activity=activity,
        user=request.user,
    )

    if not created:
        check.delete()
        messages.success(request, "Atividade desmarcada.")
    else:
        messages.success(request, "Atividade marcada como realizada/estudada.")

    tab = "eventos" if activity.kind == Activity.Kind.EVENT else "tarefas"
    return redirect_main_calendar_with_tab(request, fallback=tab)

def settings_page(request):
    # Adapte com a lógica que você já tem para carregar as preferências e ícones
    context = {
        'preference': request.user.preferences, # Exemplo
        'ui_theme': ..., 
        'ui_icons': ...
    }
    return render(request, 'accounts/settings.html', context)
