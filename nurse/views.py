
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required , permission_required
from auditor.models import Auditor
from client.forms import AppointmentForm
from main_home.forms import BloodSampleForm
from main_home.models import AnalysisRequest, Appointment, ChatRoom, Complaint, Evaluation, Lobby, Message, Payment, Test , TestResult
from django.utils import timezone
from nurse.forms import AddComponentForm, AddTestForm, EvaluationForm, TestFinalizeForm

from django.core.serializers import serialize
from django.utils import formats

from nurse.models import Nurse

from django.contrib import messages


# Create your views here.

################################################################

# Home - Lobby

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def nurse_home(request):
    nurse = request.user.nurse
    lobby = nurse.lobby
    clients = lobby.clients.all()
    
    if request.GET.get('urgency') :
        urgency = request.GET.get('urgency')
        
        if urgency == 'True':
            clients = clients.order_by("-urgent")
            sort_urgency= 'False'
        elif urgency == 'False':
            clients = clients.order_by("urgent")
            sort_urgency= 'True'
            
    else :
        sort_urgency = 'True'
    
    

    context = {
        'nurse': nurse,
        'clients': clients,
        "lobby":lobby,
        'sort_urgency':sort_urgency,
    }

    return render(request,'nurse/nurse.html', context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def lobby_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    context = {
        'appointment': appointment
    }
    
    return render(request,'nurse/lobby/lobby_detail.html', context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def evaluation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    nurse = request.user.nurse
    lobby = nurse.lobby

    if request.method == 'POST' and 'preformed' in request.POST:
        
        # Validate Evaluation Form
        
        form = EvaluationForm(request.POST)
        
        if form.is_valid():
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            hypertension = request.POST.get('hypertension')
            heart_disease = request.POST.get('heart_disease')
            smoking_history = request.POST.get('smoking_history')
            bmi = (float(weight)) / (float(height) * float(height))
            evaluation = Evaluation(appointment= appointment, gender=gender,age=age,bmi=bmi,
                                          heart_disease=heart_disease,hypertension=hypertension,
                                          smoking_history=smoking_history)
            evaluation.save()
                    
        
            # Mark Appointment as performed
            appointment.performed = True
            appointment.save()
            lobby.clients.remove(appointment)
            
            # Create the Analysis Request
            analysis_request = AnalysisRequest.objects.create(nurse=nurse, appointment=appointment )
            
            
            # Get the tests_requested from the appointment and create Test objects for each one
            tests_requested = appointment.tests_requested.all()
            
            if tests_requested :
                for test_offered in tests_requested:
                    test = Test.objects.create(test_offered=test_offered)
                    analysis_request.tests.add(test)
                
            messages.success(request,"Patient Information Saved ,  Analysis Request Added")
            
            return redirect('request_list')
        
    else : 
        form = EvaluationForm()
    
    context = {
        'appointment': appointment,
        'form':form,
    }
    
    return render(request,'nurse/lobby/evaluation.html', context)

################################################################

# Analysis Requests

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def request_list(request):
    nurse = request.user.nurse
                 
    analysis_requests = AnalysisRequest.objects.select_related('appointment__client').all().filter(nurse=nurse).all().order_by("-creation_time")
   
    if request.GET.get('date_sort') :
        date = request.GET.get('date')
        
        if date == 'True' :
            analysis_requests= analysis_requests.order_by('creation_time')
            sort_date = 'False'
        elif date == "False":
            analysis_requests= analysis_requests.order_by('-creation_time')
            sort_date = 'True'
            
        sort_urgency= request.GET.get('urgency')
    
            
    if request.GET.get('urgency_sort'):
        urgency = request.GET.get('urgency')
        
        if urgency == 'True':
            analysis_requests = analysis_requests.order_by("-appointment__urgent")
            sort_urgency= 'False'
        elif urgency == 'False':
            analysis_requests = analysis_requests.order_by("appointment__urgent")
            sort_urgency= 'True'
            
        
        sort_date= request.GET.get('date')
        
            
    if not (request.GET.get('urgency_sort')) and not (request.GET.get('date_sort')) :
        sort_date = 'True'
        sort_urgency = 'True'
        
    
    if request.method == "POST" and "search" in request.POST :
        search = request.POST.get("search")
        if search != "" :
            try:
                parsed_number = int(search)
                parsable = True
            except ValueError:
                parsable = False
            
            if parsable and analysis_requests.filter(nurse=nurse,appointment__id=int(search)).exists() :    
                    analysis_requests = analysis_requests.filter(nurse=nurse,appointment__id=int(search)).all()
                
            elif analysis_requests.filter(nurse=nurse,appointment__client__user__username=search).exists() :
                analysis_requests = analysis_requests.filter(nurse=nurse,appointment__client__user__username=search).all()
                
            else :
                context={
                    'sort_urgency':sort_urgency,
                    'sort_date':sort_date,
                }
                
                return render(request,'nurse/request/request_list.html',context)
            
    pending_requests = analysis_requests.filter(status=AnalysisRequest.PENDING)
    working_on_requests = analysis_requests.filter(status=AnalysisRequest.WORKING_ON)
    finished_requests = analysis_requests.filter(status=AnalysisRequest.FINISHED)
    
    state = request.GET.get('state')
    if state != "all" :
        if state == "pending" :
            context = {
                'pending_requests': pending_requests,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'nurse/request/request_list.html',context)
        if state == "working" :
            context = {
                'working_on_requests': working_on_requests,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'nurse/request/request_list.html',context)
        if state == "finished" :
            context = {
                'finished_requests': finished_requests,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'nurse/request/request_list.html',context)
       
            
            
    state = 'all'
            
    
    context = {
        'pending_requests': pending_requests,
        'working_on_requests': working_on_requests,
        'finished_requests': finished_requests,
        'sort_urgency':sort_urgency,
        'sort_date':sort_date,
        'state':state
    }

    
    return render(request,'nurse/request/request_list.html', context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def request_detail(request, analysis_request_id):
    analysis_request = get_object_or_404(AnalysisRequest, id=analysis_request_id)
    context = {
        'analysis_request': analysis_request,
    }
    return render(request,'nurse/request/request_detail.html', context)


@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def start_analysis(request, analysis_request_id):
    analysis_request = get_object_or_404(AnalysisRequest, id=analysis_request_id)

    if request.method == 'POST':
        analysis_request.start_time = timezone.now()
        analysis_request.status = AnalysisRequest.WORKING_ON
        analysis_request.accepted = True
        analysis_request.save()
        
        messages.success(request,"Analysis Procedure Started")

        return redirect('request_test_list', analysis_request_id=analysis_request.id)

    return redirect('request_list')

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def finish_analysis(request, analysis_request_id):
    analysis_request = get_object_or_404(AnalysisRequest, id=analysis_request_id)
    
    if request.method == 'POST':
        if analysis_request.all_tests_confirmed():
            # Mark analysis request as finished
            analysis_request.finished = True
            analysis_request.finish_time = timezone.now()
            analysis_request.status = AnalysisRequest.FINISHED
            analysis_request.save()
            
            # Create TestResult object
            test_result = TestResult.objects.create(
                request=analysis_request,
                duration=analysis_request.duration_unformated()
            )
            
            messages.success(request,"Analysis Tests Submitted Successfully")
            
            return redirect('request_detail', analysis_request.id)
    
    # If the request is not a POST request or tests are not confirmed, redirect back to request detail page
    return redirect('request_detail', analysis_request.id)


################################################################

# Analysis Requests Tests

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def request_test_add(request, analysis_request_id):
    
    analysis_request = AnalysisRequest.objects.get(id=analysis_request_id)
    appointment = analysis_request.appointment
    
    if request.method == 'POST':
        form = AddTestForm(appointment, request.POST)
        if form.is_valid():
            test_offered = form.cleaned_data['test_offered']
            test = Test.objects.create(test_offered=test_offered)
            analysis_request.tests.add(test)
            
            # Update payment status and fees
            payment = Payment.objects.get(appointment=analysis_request.appointment)
            payment.payed_nurse_tests_fee = False
            payment.nurse_tests_fee += test_offered.price
            payment.save()
            
            appointment.total_price += test_offered.price
            appointment.payment_status = False
            appointment.save()
            
            messages.success(request,'Test Added Successfully')
            
            return redirect('request_test_list', analysis_request_id=analysis_request_id)
    else:
        form = AddTestForm(appointment)
        
    context = {
        'form': form, 
        'analysis_request': analysis_request
    }
        
    return render(request,'nurse/request/test/request_test_add.html', context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def request_test_add_component(request, analysis_request_id, test_id):
    analysis_request = AnalysisRequest.objects.get(id=analysis_request_id)
    test = Test.objects.get(id=test_id)

    if request.method == 'POST':
        form = AddComponentForm(request.POST, test=test)
        if form.is_valid():
            component = form.cleaned_data['component']
            test.components.create(info=component)
            
            messages.success(request,'Component Added Successfully')
            
            return redirect('request_test_add_component', analysis_request_id=analysis_request_id, test_id=test_id)
    else:
        form = AddComponentForm(test=test)

    context = {
        'form': form,
        'analysis_request': analysis_request,
        'test': test
    }


    return render(request,'nurse/request/test/request_test_add_component.html', context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def request_test_list(request, analysis_request_id):
    analysis_request = get_object_or_404(AnalysisRequest, id=analysis_request_id)
    tests = analysis_request.tests.all()
    context = {
        'analysis_request': analysis_request,
        'tests': tests
    }
    
    return render(request,'nurse/request/test/request_test_list.html', context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def request_test_detail(request, analysis_request_id, test_id):
    analysis_request = AnalysisRequest.objects.get(id=analysis_request_id)
    test = Test.objects.get(id=test_id)

    context = {
        'analysis_request': analysis_request,
        'test': test
    }
    
    return render(request,'nurse/request/test/request_test_detail.html', context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def request_test_finalize(request, analysis_request_id, test_id):
    test = get_object_or_404(Test, id=test_id)

    if request.method == 'POST':
        form = TestFinalizeForm(request.POST, instance=test)
        if form.is_valid():
            form.save()  # Save the form data
            test.confirmed = True  # Mark the test as confirmed
            test.save()
            
            messages.success(request,'Test Finalized Successfully')
            
            return redirect('request_test_detail', analysis_request_id=analysis_request_id, test_id=test_id)
    else:
        form = TestFinalizeForm(instance=test)

    context = {
        'form': form,
        'analysis_request_id': analysis_request_id,
        'test': test,
    }


    return render(request,'nurse/request/test/request_test_finalize.html', context)

################################################################

# Chat

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def message_chat(request):
    messages = Message.objects.filter(sender=request.user) | Message.objects.filter(receiver=request.user)
    messages = messages.order_by('timestamp')
    room = ChatRoom.objects.get(nurse=request.user.nurse)
    room_id = room.id
    context={
        'room_id':room_id,
        'room':room,
        'messages':messages,
    }
    
    return render(request,'nurse/message/message_chat.html',context)

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def nurse_send(request):
    room_id = request.POST.get('room_id')
    message = request.POST.get('message')
    
    sender = request.user  # Current nurse
    receiver = Auditor.objects.first().user  # First auditor in the database
    
    # Create and save the message with the sender, receiver, and other fields
    message = Message.objects.create(sender=sender, receiver=receiver, room_id=room_id, content=message)
    
    print(f'message created :{message}')
    return HttpResponse('Message sent successfully')

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def getMessages(request):
    messages = Message.objects.filter(sender=request.user) | Message.objects.filter(receiver=request.user)
    messages = messages.order_by('timestamp')
    room = ChatRoom.objects.get(nurse=request.user.nurse)
    nurse_id = request.user.id
    room_id = room.id

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
        
    return JsonResponse({"messages":serialized_messages,"nurse_id":nurse_id})
    



################################################################


# Result


@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def result_list(request):
    
    return render(request,'nurse/result/result_list.html')

@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def result_detail(request, result_id):
    
    return render(request,'nurse/result/result_detail.html')


@login_required
@permission_required('nurse.view_nurse', raise_exception=True)
def blood_add(request):
    if request.method == 'POST':
        form = BloodSampleForm(request.POST)
        if form.is_valid():
            blood_sample = form.save() 
            client = blood_sample.client
            client.blood_type = blood_sample.blood_type
            client.save()
            blood_added = 'Blood sample added successfully!'
            form = BloodSampleForm()
            context={
                'form': form,
                'blood_added':blood_added,
            }
            
            messages.success(request,'Blood Sample Added Successfully')
            
            return render(request,'nurse/add/blood_add.html',context)  
    else:
        form = BloodSampleForm()

    context = {
        'form': form
    }

    return render(request,'nurse/add/blood_add.html',context)



