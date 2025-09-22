from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("home/",views.auditor_home,name="auditor"),
    
    path("message/chat/",views.chat_rooms,name="chat_rooms"),
    path("message/chat/<int:room_id>",views.message_chat,name="message_chat"),
    path("message/chat/auditor/send",views.auditor_send,name="auditor_send"),
    path("message/chat/getMessages/",views.getMessages,name="getMessages"),

    path("requests/",views.request_list,name="auditor_request_list"),
    path("requests/<int:analysis_request_id>/detail/",views.request_detail,name="auditor_request_detail"),
    path("requests/<int:analysis_request_id>/detail/change_nurse",views.change_nurse,name="change_nurse"),


    path("results/",views.result_list,name="test_result_list"),
    path("results/<int:test_result_id>/detail",views.result_detail,name="test_result_detail"),
    path("results/<int:test_result_id>/approve",views.approve_result,name="approve_result"),
    path("results/<int:test_result_id>/update", views.result_update, name="result_update"),
    
    path("reports/",views.report_list,name="report_list"),
    path("reports/<int:report_id>/detail/",views.report_detail,name="report_detail"),
]