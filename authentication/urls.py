from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    # User login
    path('login/', views.user_login, name='login'),

    # User logout
    path('logout/', views.user_logout, name='logout'),

    # User registration
    path('register/', views.user_register, name='register'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),
    path('', views.send_mail_page),
    path('password-reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),
]
