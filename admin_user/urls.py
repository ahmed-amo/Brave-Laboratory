from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("home/users/",views.admin_user,name="admin_user"),
    path("home/users/user/<int:user_id>/",views.user_detail,name="user_detail"),
    path("home/users/user/<int:user_id>/update",views.user_update,name="user_update"),
    
    path("account/add/",views.account_add,name="account_add"),
    path("account/add/nurse",views.account_add_nurse,name="account_add_nurse"),
    path("account/add/receptionist",views.account_add_receptionist,name="account_add_receptionist"),
    path("account/add/auditor",views.account_add_auditor,name="account_add_auditor"),

    path("blood_banks/",views.blood_banks,name="blood_banks"),
    path("blood_banks/<int:bank_id>/",views.blood_bank_detail,name="blood_bank_detail"),
    path("blood_banks/add/",views.blood_bank_add,name="blood_bank_add"),

]