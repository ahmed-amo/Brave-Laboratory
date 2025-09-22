from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('' , views.home , name="home" ),
    path('register/' , views.register , name="register" ),
    path('check_email/' , views.check_email , name="check_email" ),
    path('policy/', TemplateView.as_view(template_name='main_home/policy.html'), name='policy'),
    path('login/' , views.login_view , name="login" ),
    path('logout/' ,auth_views.LogoutView.as_view(template_name="main_home/logout.html")  , name="logout" ),
    path('profile/',views.profile_update,name="profile_update"),
    path('settings/',views.profile_settings,name="profile_settings"),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name="main_home/password/password_reset.html" 
            ), 
         name="password_reset"),
    
    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(
            template_name='main_home/password/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password_reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
            template_name='main_home/password/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password_reset_complete/', 
         auth_views.PasswordResetCompleteView.as_view(
            template_name='main_home/password/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    
   path("results/<int:invoice_id>/pdf_client_invoice", views.pdf_client_invoice, name="pdf_client_invoice"),
   path("results/<int:invoice_id>/pdf_client_results", views.pdf_client_results, name="pdf_client_results"),

]