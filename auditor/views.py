from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required , permission_required
from auditor.forms import NurseForm, UpdateTestsForm
from auditor.models import Auditor
from django.contrib.auth.models import User
from django.contrib import messages

from main_home.models import AnalysisRequest, ChatRoom, Component, Invoice, Laboratory, Message, Report, Statistics, Test, TestResult


from django.core.serializers import serialize
from django.utils import formats

from nurse.models import Nurse

from django.contrib import messages
# Create your views here.

################################################################

# Home - Stats

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def auditor_home(request):
    top_tests = Statistics.get_most_common_tests()
    app_count = Statistics.get_last_four_months_appointments_count()
    total_income = Statistics.get_total_earnings()
    monthly_revenue = Statistics.get_monthly_revenue()
    client_count = Statistics.get_client_count()
    new_client_count = Statistics.get_new_clients()
    total_complaints = Statistics.get_total_complaints()
    complaints_last_7_days = Statistics.get_complaints_last_7_days()
    
    context={
        "top_tests":top_tests,
        'app_count':app_count,
        'total_income':total_income,
        'monthly_revenue':monthly_revenue,
        'client_count':client_count,
        'new_client_count':new_client_count,
        'total_complaints':total_complaints,
        'complaints_last_7_days':complaints_last_7_days,
    }
    return render(request,'auditor/auditor.html',context)

################################################################

# Chat

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def chat_rooms(request):
    chat_rooms = ChatRoom.objects.all()
    
    context = {
        'chat_rooms': chat_rooms
    }
    
    return render(request,'auditor/message/chat_rooms.html', context)

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def message_chat(request,room_id):
    room = ChatRoom.objects.get(id=room_id)
    
    messages = Message.objects.filter(room=room)
    messages = messages.order_by('timestamp')
    
    context={
        'room_id':room_id,
        'room':room,
        'messages':messages,
    }
    
    return render(request,'auditor/message/message_chat.html',context)


@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def auditor_send(request):
    room_id = request.POST.get('room_id')
    room = ChatRoom.objects.get(id=room_id)
    message = request.POST.get('message')
    
    sender = request.user  # Current auditor
    receiver = room.nurse.user # the nurse from the room
    
    # Create and save the message with the sender, receiver, and other fields
    message = Message.objects.create(sender=sender, receiver=receiver, room_id=room_id, content=message)
    
    return HttpResponse('Message sent successfully')

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def getMessages(request):
    room_id = request.GET.get('room_id')
    room = ChatRoom.objects.get(id=room_id)
    nurse = room.nurse
    messages = Message.objects.filter(sender=nurse.user) | Message.objects.filter(receiver=nurse.user)
    messages = messages.order_by('timestamp')
    auditor_id = request.user.id    

    def serialize_timestamp(timestamp):
        return formats.date_format(timestamp, "F j, Y, P")

    serialized_messages = []
    for message in messages:
        serialized_message = {
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'room_id': message.room_id,
            'content': message.content,
            'timestamp': serialize_timestamp(message.timestamp),
        }
        serialized_messages.append(serialized_message)
        
    return JsonResponse({"messages":serialized_messages,"auditor_id":auditor_id})


################################################################

# Analysis Requests

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def request_list(request):
                 
    analysis_requests = AnalysisRequest.objects.select_related('appointment__client').all()
   
    if request.GET.get('date_sort') :
        date = request.GET.get('date')
        
        if date == 'True' :
            analysis_requests= analysis_requests.order_by('creation_time')
            sort_date = 'False'
        elif date == "False":
            analysis_requests= analysis_requests.order_by('-creation_time')
            sort_date = 'True'
            
        sort_nurse= request.GET.get('nurse')
    
            
    if request.GET.get('nurse_sort'):
        nurse = request.GET.get('nurse')
        
        if nurse == 'True':
            analysis_requests = analysis_requests.order_by("-nurse")
            sort_nurse= 'False'
        elif nurse == 'False':
            analysis_requests = analysis_requests.order_by("nurse")
            sort_nurse= 'True'
            
        
        sort_date= request.GET.get('date')
        
            
    if not (request.GET.get('nurse_sort')) and not (request.GET.get('date_sort')) :
        sort_date = 'True'
        sort_nurse = 'True'
        
    
    if request.method == "POST" and "search" in request.POST :
        search = request.POST.get("search")
        if search != "" :
            try:
                parsed_number = int(search)
                parsable = True
            except ValueError:
                parsable = False
            
            if parsable and analysis_requests.filter(appointment__id=int(search)).exists() :    
                    analysis_requests = analysis_requests.filter(appointment__id=int(search)).all()
                
            elif analysis_requests.filter(nurse__user__username=search).exists() :
                analysis_requests = analysis_requests.filter(nurse__user__username=search).all()
                
            else :
                context={
                    'sort_nurse':sort_nurse,
                    'sort_date':sort_date,
                }
                
                return render(request,'auditor/request/request_list.html',context)
            
    pending_requests = analysis_requests.filter(status=AnalysisRequest.PENDING)
    working_on_requests = analysis_requests.filter(status=AnalysisRequest.WORKING_ON)
    finished_requests = analysis_requests.filter(status=AnalysisRequest.FINISHED)
    
    state = request.GET.get('state')
    if state != "all" :
        if state == "pending" :
            context = {
                'pending_requests': pending_requests,
                'sort_nurse':sort_nurse,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'auditor/request/request_list.html',context)
        if state == "working" :
            context = {
                'working_on_requests': working_on_requests,
                'sort_nurse':sort_nurse,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'auditor/request/request_list.html',context)
        if state == "finished" :
            context = {
                'finished_requests': finished_requests,
                'sort_nurse':sort_nurse,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'auditor/request/request_list.html',context)
       
            
            
    state = 'all'
            
    
    context = {
        'pending_requests': pending_requests,
        'working_on_requests': working_on_requests,
        'finished_requests': finished_requests,
        'sort_nurse':sort_nurse,
        'sort_date':sort_date,
        'state':state
    }

    return render(request,'auditor/request/request_list.html', context)

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def request_detail(request, analysis_request_id):
    analysis_request = get_object_or_404(AnalysisRequest, id=analysis_request_id)
    form = NurseForm()
    context = {
        'analysis_request': analysis_request,
        "form":form,
    }
    
    return render(request,'auditor/request/request_detail.html', context)


@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def change_nurse(request, analysis_request_id):
    
    if request.method == "POST":
        
        form = NurseForm(request.POST)
        
        if form.is_valid():
            nurse = form.cleaned_data['nurse']
            user = User.objects.get(username=nurse)
            nurse = Nurse.objects.get(user = user)
            analysis_request = AnalysisRequest.objects.get(id = analysis_request_id)
            analysis_request.nurse = nurse
            analysis_request.save()
            
            # nurse = Nurse.objects.get(id=nurse_id)
            print(analysis_request.nurse)
            
            messages.success(request,'Nurse Changed Successfully')
    
    
    return redirect('auditor_request_detail',analysis_request_id=analysis_request_id)


################################################################

# Results

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def result_list(request):
                 
    test_result = TestResult.objects.all().order_by('-creation_time')
   
    if request.GET.get('date_sort') :
        date = request.GET.get('date')
        
        if date == 'True' :
            test_result= test_result.order_by('creation_time')
            sort_date = 'False'
        elif date == "False":
            test_result= test_result.order_by('-creation_time')
            sort_date = 'True'
            
        sort_urgency= request.GET.get('urgency')
        sort_nurse= request.GET.get('nurse')
    
            
    if request.GET.get('urgency_sort'):
        urgency = request.GET.get('urgency')
        
        if urgency == 'True':
            test_result = test_result.order_by("-request__appointment__urgent")
            sort_urgency= 'False'
        elif urgency == 'False':
            test_result = test_result.order_by("request__appointment__urgent")
            sort_urgency= 'True'
            
        
        sort_date= request.GET.get('date')
        sort_nurse= request.GET.get('nurse')
        
    if request.GET.get('nurse_sort'):
        nurse = request.GET.get('nurse')
        
        if nurse == 'True':
            test_result = test_result.order_by("-request__nurse")
            sort_nurse= 'False'
        elif nurse == 'False':
            test_result = test_result.order_by("request__nurse")
            sort_nurse= 'True'
            
        
        sort_date= request.GET.get('date')
        sort_urgency= request.GET.get('urgency')
        
            
    if not (request.GET.get('urgency_sort')) and not (request.GET.get('date_sort')) and not (request.GET.get('nurse_sort')):
        sort_date = 'True'
        sort_urgency = 'True'
        sort_nurse = 'True'
        
    
    if request.method == "POST" and "search" in request.POST :
        search = request.POST.get("search")
        if search != "" :
            try:
                parsed_number = int(search)
                parsable = True
            except ValueError:
                parsable = False
            
            if parsable and test_result.filter(request__appointment__id=int(search)).exists() :    
                    test_result = test_result.filter(request__appointment__id=int(search)).all()
                
            elif test_result.filter(request__nurse__user__username=search).exists() :
                test_result = test_result.filter(request__nurse__user__username=search).all()
                
            else :
                context={
                    'sort_urgency':sort_urgency,
                    'sort_date':sort_date,
                    'sort_nurse':sort_nurse,
                }
                
                return render(request,'auditor/result/result_list.html',context)
    
    unapproved_results = test_result.filter(approved=False)
    approved_results = test_result.filter(approved=True)
    
    state = request.GET.get('state')
    if state != "all" :
        if state == "approved" :
            context = {
                'approved_results': approved_results,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'sort_nurse':sort_nurse,
                'state':state,
            }
            return render(request,'auditor/result/result_list.html',context)
        if state == "unapproved" :
            context = {
                'unapproved_results': unapproved_results,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'sort_nurse':sort_nurse,
                'state':state,
            }
            return render(request,'auditor/result/result_list.html',context)
       
            
    state = 'all'
        
    
    context = {
        'unapproved_results': unapproved_results,
        'approved_results': approved_results,
        'sort_urgency':sort_urgency,
        'sort_date':sort_date,
        'sort_nurse':sort_nurse,
        'state':state
    }
    return render(request,'auditor/result/result_list.html', context)

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def result_detail(request , test_result_id):
    test_result = get_object_or_404(TestResult, id=test_result_id)
  
    context = {
        'test_result': test_result,
    }

    return render(request,'auditor/result/result_detail.html', context)


@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def approve_result(request, test_result_id):
    
    if 'approve' in request.POST:
        test_result = get_object_or_404(TestResult, id=test_result_id)

        # Update the approval status of the test result
        test_result.approved = True
        test_result.save()
        
        description = request.POST.get("report-desc")
        report = Report.objects.create(test_result=test_result,description=description)
        laboratory = Laboratory.objects.get(name="Brave Laboratory")
        
        invoice = Invoice.objects.create(
            report=report,
            total_price=report.test_result.request.appointment.total_price,
            payment_status=report.test_result.request.appointment.payment_status,
            client=report.test_result.request.appointment.client,
            laboratory=laboratory
        )
        
        messages.success(request, 'Test Result Approved !')
        

    return redirect('test_result_detail', test_result_id=test_result_id)

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def result_update(request, test_result_id):
    test_result = get_object_or_404(TestResult, id=test_result_id)

    if request.method == 'POST':
        # Process the form submission to update the tests

        form = UpdateTestsForm(request.POST, test_result=test_result)
        if form.is_valid():
            # Iterate over the tests in the form data and update their values
            for test in test_result.request.tests.all():
                test_value_key = f'test_{test.id}_value'
                if test_value_key in form.cleaned_data:
                    test.value = form.cleaned_data[test_value_key]
                    test.save()

                    # Iterate over the components of the test and update their values
                    for component in test.components.all():
                        component_value_key = f'component_{component.id}_value'
                        if component_value_key in form.cleaned_data:
                            component.value = form.cleaned_data[component_value_key]
                            component.save()
                            
            messages.success(request ,'Test Results Updated Successfully')

            return redirect('test_result_detail', test_result_id=test_result_id)
    else:
        # Display the form for modifying tests

        form = UpdateTestsForm(test_result=test_result)

    context = {
        'test_result': test_result,
        'form': form,
    }

    return render(request, 'auditor/result/result_update.html', context)

################################################################

# Reports

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def report_list(request):
    reports = Report.objects.all().order_by("-creation_time")
   
    if request.GET.get('date_sort') :
        date = request.GET.get('date')
        
        if date == 'True' :
            reports= reports.order_by('creation_time')
            sort_date = 'False'
        elif date == "False":
            reports= reports.order_by('-creation_time')
            sort_date = 'True'
            
        sort_client= request.GET.get('client')
    
            
    if request.GET.get('client_sort'):
        client = request.GET.get('client')
        
        if client == 'True':
            reports = reports.order_by("-invoice__client")
            sort_client= 'False'
        elif client == 'False':
            reports = reports.order_by("invoice__client")
            sort_client= 'True'
            
        
        sort_date= request.GET.get('date')
        
            
    if not (request.GET.get('client_sort')) and not (request.GET.get('date_sort')) :
        sort_date = 'True'
        sort_client = 'True'
        
    
    if request.method == "POST" and "search" in request.POST :
        search = request.POST.get("search")
        if search != "" :
            try:
                parsed_number = int(search)
                parsable = True
            except ValueError:
                parsable = False
            
            if parsable and reports.filter(id=int(search)).exists() :
                reports = reports.filter(id=int(search)).all()       
                
            elif reports.filter(invoice__client__user__username=search).exists() :
                reports = reports.filter(invoice__client__user__username=search).all()
            
            else : 
                context={
                    'sort_client':sort_client,
                    'sort_date':sort_date,
                }
            
                return render(request,'auditor/report/report_list.html',context)

    
    context ={
        'reports':reports,
        'sort_client':sort_client,
        'sort_date':sort_date,
    }
    
    return render(request,'auditor/report/report_list.html', context)

@login_required
@permission_required('auditor.view_auditor', raise_exception=True)
def report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    context = {
        'report': report,
    }
    return render(request,'auditor/report/report_detail.html', context)
