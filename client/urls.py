from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("home/appointment",views.client_home,name="client"),
    path("home/appointment/detail/<int:appointment_id>",views.appointment_detail,name="client_appointment_detail"),
    path("home/appointment/detail/<int:appointment_id>/cancel",views.cancel_appointment,name="client_cancel_appointment"),
    
    path("help",views.client_help,name="profile_help"),
    path("contact",views.client_contact,name="profile_contact"),
    path("policy",views.client_policy,name="profile_policy"),
    path("complaint",views.create_complaint,name="create_complaint"),
    
    path("appointment/book/",views.appointment_book,name="client_appointment_book"),
    path("appointment/book/confirm/",views.client_appointment_confirm,name="client_appointment_confirm"),
    path("appointment/book/contract/",views.client_appointment_contract,name="client_appointment_contract"),
    path("appointment/book/pay/",views.client_appointment_pay,name="client_appointment_pay"),
    path("appointment/book/pay/verify_token",views.verify_token,name="verify_token"),

    
    path("requests/",views.request_list,name="client_request_list"),
    path("requests/detail",views.request_detail,name="client_request_detail"),
    
    path("results/",views.result_list,name="client_result_list"),
    path("results/<int:invoice_id>",views.result_detail,name="client_result_detail"),
    path("results/<int:invoice_id>/online_pay/confirm",views.online_pay,name="online_pay"),
]