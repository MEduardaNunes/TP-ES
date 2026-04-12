from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Schedule, Participant

def home(request):
    return render(request, "home.html")

@login_required
def calendar(request):
    return render(request, "calendar.html")

def get_participant(user, schedule):
    try:
        return schedule.participants.get(user=user)
    except Participant.DoesNotExist:
        return None

def participant_required(view_func):
    """Garante que o usuário é participante da agenda."""
    @login_required
    def wrapper(request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        participant = get_participant(request.user, schedule)
        if not participant:
            messages.error(request, "Você não tem acesso a essa agenda.")
            return redirect("calendar")
        return view_func(request, schedule, participant, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Garante que o usuário é admin da agenda."""
    @login_required
    def wrapper(request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        participant = get_participant(request.user, schedule)
        if not participant or not participant.is_admin:
            messages.error(request, "Você não tem permissão para isso.")
            return redirect("calendar")
        return view_func(request, schedule, participant, *args, **kwargs)
    return wrapper


@login_required
def calendar(request):
    """Lista todas as agendas do usuário logado."""
    participations = request.user.participations.select_related("schedule").all()
    return render(request, "schedules/calendar.html", {"participations": participations})

@login_required
def create_schedule(request):
    if request.method == "POST":
        name = request.POST.get("name")
        color = request.POST.get("color", "#6366f1")

        if not name:
            messages.error(request, "Preencha o nome da agenda.")
            return redirect("create_schedule")

        schedule = Schedule.objects.create(name=name, color=color)
        Participant.objects.create(
            schedule=schedule,
            user=request.user,
            role=Participant.Role.ADMIN,
        )
        messages.success(request, "Agenda criada com sucesso.")
        return redirect("calendar")

    return render(request, "schedules/create_schedule.html")

@admin_required
def edit_schedule(request, schedule, participant):
    if request.method == "POST":
        schedule.name = request.POST.get("name", schedule.name)
        schedule.color = request.POST.get("color", schedule.color)
        schedule.save()
        messages.success(request, "Agenda atualizada com sucesso.")
        return redirect("view_schedule", schedule_id=schedule.id)

    return render(request, "schedules/edit_schedule.html", {"schedule": schedule})

@admin_required
@require_POST
def delete_schedule(request, schedule, participant):
    schedule.delete()
    messages.success(request, "Agenda deletada com sucesso.")
    return redirect("calendar")

@participant_required
def view_schedule(request, schedule, participant):
    events = schedule.events.all()
    return render(request, "schedules/view_schedule.html", {
        "schedule": schedule,
        "participant": participant,
        "events": events,
    })