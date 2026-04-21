from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.urls import reverse
from functools import wraps
import calendar
from .models import Schedule, Participant, Activity, ActivityCheck
from django.contrib.auth import logout, login

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
            return redirect("schedules:main_calendar_view")
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
            return redirect("schedules:main_calendar_view")
        return view_func(request, schedule, participant, *args, **kwargs)
    return wrapper

@login_required
def main_calendar_view(request):
    """
    Exibe o calendário mensal com atividades do usuário.
    Inclui atividades do mês, eventos futuros e tarefas pendentes na aba lateral.
    """
    today = date.today()
 
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
 
    participations = request.user.participations.select_related("schedule").all()
    schedule_ids = participations.values_list("schedule_id", flat=True)
 
    admin_participations = request.user.participations.select_related("schedule").filter(
        role=Participant.Role.ADMIN
    )
 
    activities = Activity.objects.filter(
        schedule_id__in=schedule_ids,
        date__year=year,
        date__month=month,
    ).select_related("schedule").order_by("start_time")
 
    activities_by_day = {}
    for activity in activities:
        day = activity.date.day
        activities_by_day.setdefault(day, []).append(activity)
 
    # Atividades futuras ou não concluídas para a aba lateral
    future_events = Activity.objects.filter(
        schedule_id__in=schedule_ids,
        kind=Activity.Kind.EVENT,
        date__gte=today,
    ).select_related("schedule").order_by("date", "start_time")
 
    pending_tasks = Activity.objects.filter(
        schedule_id__in=schedule_ids,
        kind=Activity.Kind.TASK,
    ).exclude(
        checks__user=request.user
    ).select_related("schedule").order_by("date")
 
    month_names = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
 
    return render(request, "schedules/calendar.html", {
        "participations": participations,
        "admin_participations": admin_participations,  # NOVO: apenas agendas onde é admin, para o modal
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
    })
    
@login_required
def create_schedule(request):
    """Cria uma nova agenda para o usuário logado."""
    if request.method == "POST":
        name = request.POST.get("name")
        color = request.POST.get("color", "#6366f1")
 
        if not name:
            messages.error(request, "Preencha o nome da agenda.")
            return redirect("schedules:create_schedule")
 
        schedule = Schedule.objects.create(name=name, color=color)
        Participant.objects.create(
            schedule=schedule,
            user=request.user,
            role=Participant.Role.ADMIN,
        )
        messages.success(request, "Agenda criada com sucesso.")
        return redirect("schedules:main_calendar_view")
 
    return render(request, "schedules/create_schedule.html")

@admin_required
def edit_schedule(request, schedule, participant):
    if request.method == "POST":
        schedule.name = request.POST.get("name", schedule.name)
        schedule.color = request.POST.get("color", schedule.color)
        schedule.save()
        messages.success(request, "Agenda atualizada com sucesso.")
        return redirect("schedules:view_schedule", schedule_id=schedule.id)
 
    return render(request, "schedules/edit_schedule.html", {"schedule": schedule})

@admin_required
@require_POST
def delete_schedule(request, schedule, participant):
    schedule.delete()
    messages.success(request, "Agenda deletada com sucesso.")
    return redirect(reverse('schedules:main_calendar_view') + '?tab=agendas')

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
 
    return render(request, "schedules/view_schedule.html", {
        "schedule": schedule,
        "participant": participant,
        "events": activities.filter(kind=Activity.Kind.EVENT),
        "tasks": activities.filter(kind=Activity.Kind.TASK),
        "checked_ids": checked_ids,
    })
    
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

@admin_required
def create_activity(request, schedule, participant):
    """Cria uma nova atividade (evento ou tarefa) na agenda."""
    if request.method == "POST":
        title = request.POST.get("title")
        kind = request.POST.get("kind")
        activity_type_value = request.POST.get("activity_type")
 
        if not title or not kind or not activity_type_value:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            #return redirect("schedules:create_activity", schedule_id=schedule.id)
            return redirect("schedules:main_calendar_view")
 
        date_value = request.POST.get("date") or None
        if kind == Activity.Kind.EVENT and not date_value:
            messages.error(request, "Eventos precisam de uma data.")
            #return redirect("schedules:create_activity", schedule_id=schedule.id)
            return redirect("schedules:main_calendar_view")
 
        Activity.objects.create(
            schedule=schedule,
            title=title,
            kind=kind,
            activity_type=activity_type_value,
            date=date_value,
            start_time=request.POST.get("start_time") or None,
            end_time=request.POST.get("end_time") or None,
            notes=request.POST.get("notes", ""),
            color=request.POST.get("color", ""),
        )
        messages.success(request, "Atividade criada com sucesso.")
        return redirect("schedules:main_calendar_view")
        # return redirect("schedules:view_schedule", schedule_id=schedule.id)
 
    return render(request, "schedules/create_activity.html", {
        "schedule": schedule,
        "kinds": Activity.Kind.choices,
        "types": Activity.Type.choices,
    })
    
@login_required
def quick_create_activity(request):
    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")
        schedule = get_object_or_404(Schedule, id=schedule_id)
 
        participant = get_participant(request.user, schedule)
        if not participant:
            messages.error(request, "Você não tem acesso a essa agenda.")
            return redirect("schedules:main_calendar_view")
 
        if not participant.is_admin:
            messages.error(request, "Você não tem permissão para criar atividades nessa agenda.")
            return redirect("schedules:main_calendar_view")
 
        title = request.POST.get("title")
        kind = request.POST.get("kind")
        activity_type_value = request.POST.get("activity_type")
 
        if not title:
            messages.error(request, "O título é obrigatório.")
            return redirect("schedules:main_calendar_view")
 
        if not kind:
            messages.error(request, "O tipo da atividade é obrigatório.")
            return redirect("schedules:main_calendar_view")
 
        if not activity_type_value:
            messages.error(request, "A categoria da atividade é obrigatória.")
            return redirect("schedules:main_calendar_view")
 
        date_value = request.POST.get("date") or None
 
        if kind == Activity.Kind.EVENT and not date_value:
            messages.error(request, "Eventos precisam de uma data.")
            return redirect("schedules:main_calendar_view")
 
        Activity.objects.create(
            schedule=schedule,
            title=title,
            kind=kind,
            activity_type=activity_type_value,  
            date=date_value,
            start_time=request.POST.get("start_time") or None,
            end_time=request.POST.get("end_time") or None,
        )
        messages.success(request, "Atividade criada com sucesso.")
 
    return redirect("schedules:main_calendar_view")
    
@admin_required
def edit_activity(request, schedule, participant, activity_id):
    activity = get_object_or_404(Activity, id=activity_id, schedule=schedule)
 
    if request.method == "POST":
        activity.title = request.POST.get("title", activity.title)
        activity.kind = request.POST.get("kind", activity.kind)
        activity.activity_type = request.POST.get("activity_type", activity.activity_type)
        activity.date = request.POST.get("date") or None
        activity.start_time = request.POST.get("start_time") or None
        activity.end_time = request.POST.get("end_time") or None
        activity.notes = request.POST.get("notes", activity.notes)
        activity.color = request.POST.get("color", activity.color)
        activity.save()
        messages.success(request, "Atividade atualizada com sucesso.")
        tab = "eventos" if activity.kind == Activity.Kind.EVENT else "tarefas"
        return redirect(reverse('schedules:main_calendar_view') + f'?tab={tab}')
 
    return render(request, "schedules/edit_activity.html", {
        "schedule": schedule,
        "activity": activity,
        "kinds": Activity.Kind.choices,
        "types": Activity.Type.choices,
    })

    
@admin_required
@require_POST
def delete_activity(request, schedule, participant, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id, schedule=schedule)
    except Activity.DoesNotExist:
        messages.error(request, "Atividade não encontrada.")
        return redirect("schedules:main_calendar_view")
    
    activity_kind = activity.kind
    activity.delete()
    messages.success(request, "Atividade deletada com sucesso.")
    tab = "eventos" if activity_kind == Activity.Kind.EVENT else "tarefas"
    return redirect(reverse('schedules:main_calendar_view') + f'?tab={tab}')

@participant_required
@require_POST
def toggle_check(request, schedule, participant, activity_id):
    """Marca ou desmarca uma tarefa como concluída para o usuário logado."""
    activity = get_object_or_404(Activity, id=activity_id, schedule=schedule)
 
    if not activity.is_task:
        messages.error(request, "Apenas tarefas podem ser marcadas como concluídas.")
        return redirect(reverse('schedules:main_calendar_view') + '?tab=tarefas')
 
    check, created = ActivityCheck.objects.get_or_create(
        activity=activity,
        user=request.user,
    )
    if not created:
        check.delete()
 
    return redirect(reverse('schedules:main_calendar_view') + '?tab=tarefas')
 
 
def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu do sistema com sucesso!")
    return redirect('accounts:login')