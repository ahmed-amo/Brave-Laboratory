from django.contrib import admin
from django.urls import path
from . import views
from main_home import views as home_views

urlpatterns = [
    path("home/report/",views.receptionist_home,name="receptionist"),
    path("home/report/<int:report_id>/detail/",views.receptionist_report_detail,name="receptionist_report_detail"),
    path("home/report/<int:report_id>/invoice/<int:invoice_id>/",views.invoice_detail,name="invoice_detail"),
    path('home/report/<int:report_id>/invoice/<int:invoice_id>/confirm_payment/', views.confirm_payment, name='confirm_payment'),
    
    
    path("client/add/",views.client_add,name="client_add"),
    path("appointment/add/",views.appointment_add,name="appointment_add"),
    
    path("appointments/",views.appointment_list,name="appointment_list"),
    path("appointments/detail/<int:appointment_id>/",views.appointment_detail,name="appointment_detail"),
    path("appointments/confirm/<int:appointment_id>/",views.appointment_confirm,name="appointment_confirm"),
    
    path("complaints/",views.complaint_list,name="complaint_list"),
    path("complaints/detail/<int:complaint_id>/",views.complaint_detail,name="complaint_detail"),
    path("complaints/detail/<int:complaint_id>/reply",views.reply_complaint,name="reply_complaint"),
]