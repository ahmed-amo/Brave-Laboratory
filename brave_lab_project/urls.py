"""
URL configuration for brave_lab_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path , include
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls , name='admin'),
    path('',include('main_home.urls')), 
    path('client/',include('client.urls'),name="client"),
    path('nurse/',include('nurse.urls'),name="nurse"),
    path('receptionist/',include('receptionist.urls'),name="receptionist"),
    path('auditor/',include('auditor.urls'),name="auditor"),
    path('admin_user/',include('admin_user.urls'),name="admin_user"),
    path('verification/', include('verify_email.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
