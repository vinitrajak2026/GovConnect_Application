from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.citizen_register, name='register'),
    path('login/', views.citizen_login, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.citizen_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
