from django.utils import timezone
from django.shortcuts import get_object_or_404, render , redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.views.decorators.http import require_POST
from .forms import AppointmentForm
from client.models import Client
from main_home.forms import UserRegisterForm
from django.contrib import messages

from main_home.models import Appointment, BloodBank, Complaint, Invoice, Lobby, Payment, Report
from nurse.models import Nurse
from receptionist.forms import ConfirmationForm
from django.db.models import Count, Q,F
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from brave_lab_project.settings import EMAIL_HOST_USER
from django.core.mail import send_mail

from django.core.files.storage import default_storage
# Create your views here.

################################################################

# Home Invoices

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def receptionist_home(request):
    reports = Report.objects.all().order_by('-creation_time')
    
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
            
            if parsable and reports.filter(test_result__request__appointment__id=int(search)).exists() :
                reports = reports.filter(test_result__request__appointment__id=int(search)).all()       

            elif reports.filter(invoice__client__user__username=search).exists() :
                reports = reports.filter(invoice__client__user__username=search).all()
            
            else : 
                context={
                    'sort_client':sort_client,
                    'sort_date':sort_date,
                }
            
                return render(request,'receptionist/receptionist.html',context)

    
    context ={
        'reports':reports,
        'sort_client':sort_client,
        'sort_date':sort_date,
    }
    return render(request,'receptionist/receptionist.html', context)

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def receptionist_report_detail(request,report_id):
    report = Report.objects.get(id=report_id)
    context ={
        'report':report,
    }
    
    return render(request,'receptionist/report/report_detail.html', context)
    

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def invoice_detail(request, report_id, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    payment = invoice.report.test_result.request.appointment.payment 
    unpaid = invoice.total_price - payment.total_amount_payed
    context ={
        'invoice':invoice,
        'payment':payment,
        'unpaid':unpaid
    }
    
    return render(request,'receptionist/invoice/invoice_detail.html', context)

def confirm_payment(request,report_id , invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        appointment=invoice.report.test_result.request.appointment
        
        # Update the payment status of the invoice
        invoice.payment_status = True
        invoice.save()

        # Update the payment model with the amount paid
        payment = Payment.objects.get(appointment=appointment)
        payment.payed_nurse_tests_fee = True
        payment.payed_tests_fee = True
        payment.total_amount_payed += invoice.total_price
        payment.save()
        
        appointment.payment_status = True
        appointment.save()
        
        messages.success(request,"Appointment Marked as Payed")
        
        return redirect("receptionist_report_detail",report_id=report_id)

    return redirect('invoice_detail',report_id=report_id, invoice_id=invoice_id)
################################################################


@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def client_add(request):
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # add him to the client group
            group = Group.objects.get(name="client")
            group.user_set.add(user)
            # extract form data
            data = form.cleaned_data
            phone_number = data.get("phone_number")
            gender = data.get("gender")
            address = data.get("address")
            policy = data.get("policy")
            date_of_birth = data.get("date_of_birth")
            # add him with any additionel information into the client table
            Client.objects.create(user = user,
                            phone_number = phone_number,
                            gender = gender,
                            address = address,
                            policy = policy,
                            date_of_birth = date_of_birth)
            
            messages.success(request,"Client Added Successfully")
            
            return redirect('receptionist')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form
    }
    
    return render(request,'receptionist/add/client_add.html',context)


@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def appointment_add(request):
    appointments = Appointment.objects.all().filter(cancelled=False)
    for appointment in appointments:
        appointment.check_overdue
    
    if request.method == 'POST' :
        form = AppointmentForm(request.POST,request.FILES)
        if form.is_valid():
            client = form.cleaned_data['client']
            appointments = appointments.filter(client=client)
            date = form.cleaned_data['date']
            date = date.strftime("%Y-%m-%d")
            description = form.cleaned_data['description']
            tests_requested = form.cleaned_data['tests_requested']
            
            dates=[]
            for appointment in appointments:
                dates.append(appointment.date)
                
            pending_app_count = appointments.filter(performed=False,arrived=False).count()


            if pending_app_count >= 2:
                limit=f"Client has {pending_app_count} appointments pending, Limit reached !"
                return render(request,'receptionist/add/appointment_add.html',{'form':form,'limit':limit})  
                
            if date in dates :
                limit= f"One appointment per day, {date} is already booked"
                return render(request,'receptionist/add/appointment_add.html',{'form':form,'limit':limit})  

            
            if 'document' in request.FILES :
                document_file = request.FILES['document']
                document = default_storage.save('medical_documents/' + document_file.name, document_file)
            else :
                document = None
            urgent=False
            total_price = 0
            if tests_requested:
                for test in tests_requested:
                    if test.urgent :
                        urgent = True
                    total_price+=test.price
            
            
            
            appointment = Appointment()
            appointment.client = client
            appointment.date = date
            appointment.description = description
            if document :
                appointment.document = document
            appointment.total_price = total_price
            appointment.urgent = urgent
            appointment.save()
            
            if tests_requested :
                appointment.tests_requested.add(*tests_requested)
            
            payment = Payment(appointment=appointment)
            payment.save()
            
            payment.tests_fee = appointment.total_price
            
            payment.save()
            appointment.save()
            
            
            messages.success(request, f"Please remember your Appointment ID #{appointment.id}")
            
            return redirect('appointment_detail',appointment_id=appointment.id)
    else:
        form = AppointmentForm() 
       
    
        
    context={
        'form':form,
    }
         
    return render(request,'receptionist/add/appointment_add.html',context)

################################################################

# Appointments

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def appointment_list(request):
    
    appointments = Appointment.objects.exclude(cancelled=True).all().order_by('-date')
    appointments_today = []
    appointments_tomorrow = []
    appointments_upcoming = []
    paid_appointments = []
    
    receptionist = request.user.receptionist
                 
   
    if request.GET.get('date_sort') :
        date = request.GET.get('date')
        
        if date == 'True' :
            appointments= appointments.order_by('date')
            sort_date = 'False'
        elif date == "False":
            appointments= appointments.order_by('-date')
            sort_date = 'True'
            
        sort_urgency= request.GET.get('urgency')
    
            
    if request.GET.get('urgency_sort'):
        urgency = request.GET.get('urgency')
        
        if urgency == 'True':
            appointments = appointments.order_by("-urgent")
            sort_urgency= 'False'
        elif urgency == 'False':
            appointments = appointments.order_by("urgent")
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
            
            if parsable and appointments.filter(id=int(search)).exists() :
                appointments = appointments.filter(id=int(search)).all()       
                
            elif appointments.filter(client__user__username=search).exists() :
                appointments = appointments.filter(client__user__username=search).all()
            
            else : 
                context={
                    'sort_urgency':sort_urgency,
                    'sort_date':sort_date,
                }
            
                return render(request,'receptionist/appointment/appointment_list.html',context)


    
    
    for appointment in appointments:
        if appointment.payment.payed_appointment_fee and appointment.arrived:
            paid_appointments.append(appointment)
        elif appointment.status == appointment.TODAY:
            appointments_today.append(appointment)
        elif appointment.status == appointment.TOMORROW:
            appointments_tomorrow.append(appointment)
        elif appointment.status == appointment.UPCOMING:
            appointments_upcoming.append(appointment)

    state = request.GET.get('state')
    if state != "all" :
        if state == "today" :
            context = {
                'appointments_today': appointments_today,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'receptionist/appointment/appointment_list.html',context)
        if state == "tomorrow" :
            context = {
                'appointments_tomorrow': appointments_tomorrow,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'receptionist/appointment/appointment_list.html',context)
        if state == "upcoming" :
            context = {
                'appointments_upcoming': appointments_upcoming,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'receptionist/appointment/appointment_list.html',context)
        if state == "paid" :
            context = {
                'paid_appointments': paid_appointments,
                'sort_urgency':sort_urgency,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'receptionist/appointment/appointment_list.html',context)
            
            
    state = 'all'
    
    context = {
        'appointments_today': appointments_today,
        'appointments_tomorrow': appointments_tomorrow,
        'appointments_upcoming': appointments_upcoming,
        'paid_appointments': paid_appointments,
        'sort_urgency':sort_urgency,
        'sort_date':sort_date,
        'state':state,
    }
    

    
    return render(request,'receptionist/appointment/appointment_list.html',context)

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def appointment_detail(request,appointment_id):
    
    appointment = get_object_or_404(Appointment, id=appointment_id)

    context = {
        'appointment': appointment
    }
    
    return render(request,'receptionist/appointment/appointment_detail.html',context)


@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def appointment_confirm(request, appointment_id):
    
    appointment = Appointment.objects.get(id=appointment_id)
    payment = appointment.payment
    appointment_fee = payment.appointment_fee
    
    if request.method == 'POST':
        form = ConfirmationForm(request.POST, appointment_fee=appointment_fee)
        if form.is_valid():
            #
            payed = request.POST.get("payed")
            nurse = Nurse.objects.annotate(
                        lobby_clients_count=Count('lobby__clients'),
                        analysis_requests_count=Count(
                            'analysisrequest',
                            filter=Q(analysisrequest__status__in=['pending', 'working-on'])
                        )
                    ).order_by(
                        'lobby_clients_count', 'analysis_requests_count'
                    ).first()

            if nurse:
                lobby, _ = Lobby.objects.get_or_create(nurse=nurse)
                lobby.clients.add(appointment)
                
                
            appointment_fee_paid = form.cleaned_data["appointment_fee_paid"]
            
            if appointment_fee_paid and payed != "payed":
                print("appointment payed through form")
                payment.total_amount_payed+=appointment_fee
                payment.payed_appointment_fee = True   
                
            appointment.arrived = True
            
            payment.save()
            appointment.save()
            
            messages.success(request,'Client Arrived Successfully')
            
            return redirect("appointment_detail",appointment_id=appointment_id)
                
    else:
        form = ConfirmationForm(appointment_fee=appointment_fee)

    context={
        'form': form, 
        'appointment': appointment
    }
    
    return render(request,'receptionist/appointment/appointment_confirm.html',context)

################################################################

# Complaints 

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def complaint_list(request):
    complaints = Complaint.objects.all().order_by('-date')
    
    if request.method == "POST" and "search" in request.POST :
        search = request.POST.get("search")
        if search != "" :
            try:
                parsed_number = int(search)
                parsable = True
            except ValueError:
                parsable = False
            
            if parsable and complaints.filter(id=int(search)).exists() :
                complaints = complaints.filter(id=int(search)).all()       
                
            elif complaints.filter(client__user__username=search).exists() :
                complaints = complaints.filter(client__user__username=search).all()
            
            else :
                return render(request,'receptionist/complaint/complaint_list.html')



    context = {
        'complaints': complaints
    }
    
    return render(request,'receptionist/complaint/complaint_list.html',context)

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def complaint_detail(request,complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    context = {
        'complaint': complaint
    }
    return render(request,'receptionist/complaint/complaint_detail.html',context)

################################################################


## reply to complaint 

@login_required
@permission_required('receptionist.view_receptionist', raise_exception=True)
def reply_complaint(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    client=complaint.client
    if request.method == 'POST':
        content = request.POST.get("description")
        title = f"{complaint.topic}"
        topic = f"Replying to Customer Complaint No.{complaint_id}"
        subject = f'{ client.user.first_name } { client.user.last_name } Customer Complaint Reply'
        
        html = render_to_string('receptionist/complaint/complaint_email_template.html',{
            "user":request.user,
            "topic":topic,
            'content':content,
            'title':title,
        })
        
        send_mail(subject,content ,EMAIL_HOST_USER,[f"{client.user.email}"],html_message=html)
        
        messages.success(request,"Reply Composed Successfully")
        
        return redirect('complaint_detail',complaint_id=complaint_id)
        

    return render(request, 'receptionist/complaint/complaint_detail.html')