from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import UserThemePreference

def login_page(request):
    if request.user.is_authenticated:
        return redirect("schedules:main_calendar_view")
    return render(request, "login.html")

@login_required
def user_space(request):
    preference, _ = UserThemePreference.objects.get_or_create(user=request.user)
    return render(request, "user.html", {"preference": preference})

def sign_up(request):
    return render(request, "sign_up.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("schedules:main_calendar_view")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nome de usuário já existe")
            return redirect("accounts:sign_up") 

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem")
            return redirect("accounts:sign_up")
        
        User.objects.create_user(username=username, password=password)
        messages.success(request, "Usuário criado com sucesso")
    
    return redirect("accounts:login_page")


def login_user(request):
    if request.user.is_authenticated:
        return redirect("schedules:main_calendar_view")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("schedules:main_calendar_view")
        
        else:
            messages.error(request, "Nome de usuário ou senha incorretos")
            return redirect("accounts:login_page")
        
    return redirect("accounts:login_page")


@login_required      
def logout_user(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Você saiu do sistema com sucesso!")
        return redirect('accounts:login_page')
    return redirect('accounts:login_page')


@login_required
def edit_user(request):
    """Edita o perfil do usuário logado."""
    if not request.user.is_authenticated:
        return redirect('accounts:login_page')
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password", "").strip()
        password_confirm = request.POST.get("password_confirm", "").strip()

        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, "Nome de usuário já existe")
            return redirect("accounts:user_space") 

        # Validação de senha: ambas preenchidas ou nenhuma
        if password and not password_confirm:
            messages.error(request, "Por favor, confirme a nova senha.")
            return redirect("accounts:user_space")
        
        if not password and password_confirm:
            messages.error(request, "Por favor, preencha a nova senha.")
            return redirect("accounts:user_space")

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem")
            return redirect("accounts:user_space")
        
        user = request.user
        user.username = username
        if password:
            user.set_password(password)
        user.save()

        messages.success(request, "Usuário atualizado com sucesso")
        update_session_auth_hash(request, user)
       
        return redirect("accounts:user_space")
    
    return redirect("accounts:user_space")


@login_required
def delete_user(request):
    """Deleta a conta do usuário logado."""
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Usuário deletado com sucesso")
        return redirect("accounts:login_page")
    
    return redirect("accounts:user_space")


@login_required
def update_preferences(request):
    if request.method != "POST":
        return redirect("accounts:user_space")

    preference, _ = UserThemePreference.objects.get_or_create(user=request.user)

    preference.base_clr = request.POST.get("base_clr", preference.base_clr)
    preference.line_clr = request.POST.get("line_clr", preference.line_clr)
    preference.hover_clr = request.POST.get("hover_clr", preference.hover_clr)
    preference.text_clr = request.POST.get("text_clr", preference.text_clr)
    preference.accent_clr = request.POST.get("accent_clr", preference.accent_clr)
    preference.secondary_text_clr = request.POST.get("secondary_text_clr", preference.secondary_text_clr)
    preference.container_background_base = request.POST.get(
        "container_background_base",
        preference.container_background_base,
    )
    preference.secondary_base_clr = request.POST.get("secondary_base_clr", preference.secondary_base_clr)
    preference.sidebar_gradient_start = request.POST.get(
        "sidebar_gradient_start",
        preference.sidebar_gradient_start,
    )
    preference.sidebar_gradient_end = request.POST.get(
        "sidebar_gradient_end",
        preference.sidebar_gradient_end,
    )

    preference.profile_icon_emoji = request.POST.get("profile_icon_emoji", preference.profile_icon_emoji).strip()
    preference.agenda_icon_emoji = request.POST.get("agenda_icon_emoji", preference.agenda_icon_emoji).strip()
    preference.default_activity_icon_emoji = request.POST.get(
        "default_activity_icon_emoji",
        preference.default_activity_icon_emoji,
    ).strip()

    if request.POST.get("clear_profile_icon_image") == "1" and preference.profile_icon_image:
        preference.profile_icon_image.delete(save=False)
        preference.profile_icon_image = None
    if request.POST.get("clear_agenda_icon_image") == "1" and preference.agenda_icon_image:
        preference.agenda_icon_image.delete(save=False)
        preference.agenda_icon_image = None
    if request.POST.get("clear_default_activity_icon_image") == "1" and preference.default_activity_icon_image:
        preference.default_activity_icon_image.delete(save=False)
        preference.default_activity_icon_image = None

    if request.FILES.get("profile_icon_image"):
        preference.profile_icon_image = request.FILES["profile_icon_image"]
    if request.FILES.get("agenda_icon_image"):
        preference.agenda_icon_image = request.FILES["agenda_icon_image"]
    if request.FILES.get("default_activity_icon_image"):
        preference.default_activity_icon_image = request.FILES["default_activity_icon_image"]

    preference.save()
    messages.success(request, "Preferências visuais atualizadas com sucesso.")
    return redirect("accounts:user_space")