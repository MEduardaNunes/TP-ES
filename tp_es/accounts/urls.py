from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('user/', views.user_space, name='user_space'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('edit-user/', views.edit_user, name='edit_user'),
    path('delete-user/', views.delete_user, name='delete_user'),
]