from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.
def home(request):
    return render(request, "home.html")

@login_required
def calendar(request):
    return render(request, "calendar.html")

@login_required
def user_space(request):
    return render(request, "user.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("calendar")
    
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if User.objects.filter(username=name).exists():
            messages.error(request, "Nome de usuário já existe")
            return redirect("home")

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem")
            return redirect("home")
        
        User.objects.create_user(username=name, password=password)
        messages.success(request, "Usuário criado com sucesso")
        return redirect("home")

def login_user(request):
    if request.user.is_authenticated:
        return redirect("calendar")
    
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        user = authenticate(request, username=name, password=password)

        if user is not None:
            login(request, user)
            return redirect("calendar")
        
        else:
            messages.error(request, "Nome de usuário ou senha incorretos")
            return redirect("home")
        
def logout_user(request):
    logout(request)
    return redirect("home")