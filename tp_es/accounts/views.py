from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

def home(request):
    if request.user.is_authenticated:
        return redirect("schedules:main_calendar_view")
    return render(request, "home.html")

@login_required
def user_space(request):
    return render(request, "user.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("schedules:main_calendar_view")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nome de usuário já existe")
            return redirect("home") 

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem")
            return redirect("home")
        
        User.objects.create_user(username=username, password=password)
        messages.success(request, "Usuário criado com sucesso")
    
    return redirect("home")

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
            return redirect("home")
        
    return redirect("home")
        
def logout_user(request):
    logout(request)
    return redirect("home")

def edit_user(request):
    """Edita o perfil do usuário logado."""
    if not request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, "Nome de usuário já existe")
            return redirect("user_space") 

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem")
            return redirect("user_space")
        
        user = request.user
        user.username = username
        if password:
            user.set_password(password)
        user.save()

        messages.success(request, "Usuário atualizado com sucesso")
        update_session_auth_hash(request, user)
       
        return redirect("user_space")
    
    return redirect("user_space")

@login_required
def delete_user(request):
    """Deleta a conta do usuário logado."""
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Usuário deletado com sucesso")
        return redirect("home")
    
    return redirect("user_space")