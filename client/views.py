from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render ,redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required , permission_required
from django.template.loader import render_to_string
from brave_lab_project.settings import EMAIL_HOST_USER
from main_home.models import Appointment, Complaint, Invoice, MedicalDocument, Payment, TestOffered
from .forms import  AppointmentForm, AppointmentPaymentForm, ClientContactForm, ComplaintForm
from django.core.files.storage import default_storage
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.middleware.csrf import get_token
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

################################################################

# Home

@login_required
@permission_required('client.view_client', raise_exception=True)
def client_home(request):
    #
    appointments = Appointment.objects.filter(client=request.user.client).order_by('-date')
    for appointment in appointments:
        appointment.check_overdue
                 
   
    if request.GET.get('date') :
        date = request.GET.get('date')
        
        if date == 'True' :
            appointments= appointments.order_by('date')
            sort_date = 'False'
        elif date == "False":
            appointments= appointments.order_by('-date')
            sort_date = 'True'
            
    if not (request.GET.get('date')) :
        sort_date = 'True'
        
        
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
            
            else : 
                context={
                    'sort_date':sort_date,
                }
            
                return render(request,'client/client.html',context)


    booked_appointments = []
    performed_appointments = []
    canceled_appointments = []

    state = request.GET.get('state')
    
    

    for appointment in appointments:
        if appointment.performed :
            performed_appointments.append(appointment)
        elif appointment.cancelled or (appointment.status == appointment.OVERDUE):
            canceled_appointments.append(appointment)
        else:
            booked_appointments.append(appointment)
    
    if state != "all" :
        if state == "booked" :
            context = {
                'booked_appointments': booked_appointments,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'client/client.html',context)
        if state == "performed" :
            context = {
                'performed_appointments': performed_appointments,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'client/client.html',context)
        if state == "canceled" :
            context = {
                'canceled_appointments': canceled_appointments,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'client/client.html',context)
        
                  
    state = 'all'
   

    context = {
        'booked_appointments': booked_appointments,
        'performed_appointments': performed_appointments,
        'canceled_appointments': canceled_appointments,
        'sort_date':sort_date,
        'state':state,
    }
    return render(request,'client/client.html',context)

################################################################

# Appointment

@login_required
@permission_required('client.view_client', raise_exception=True)
def appointment_book(request):
    client = request.user.client
    appointments = Appointment.objects.all().filter(client=client,cancelled=False)
    for appointment in appointments:
        appointment.check_overdue
        
    if request.method == 'POST' :
        
        form = AppointmentForm(request.POST,request.FILES)

        if form.is_valid():
            dates=[]
            for appointment in appointments:
                dates.append(appointment.date)
            date = form.cleaned_data['date']
            pending_app_count = appointments.filter(performed=False,arrived=False).count()
            
            if pending_app_count >= 2:
                limit=f"You have {pending_app_count} appointments pending, Limit reached !"
                return render(request,'client/appointment/appointment_book.html',{'form':form,'limit':limit})  
            
            if date in dates :
                limit= f"One appointment per day, {date} is already booked"
                return render(request,'client/appointment/appointment_book.html',{'form':form,'limit':limit})  
            
            date = date.strftime("%Y-%m-%d")
            description = form.cleaned_data['description']
            tests_requested = form.cleaned_data['tests_requested']
            
            if 'document' in request.FILES :
                document_file = request.FILES['document']
                document = default_storage.save('medical_documents/' + document_file.name, document_file)
            else :
                document = None
            
            total_price = 0
            for test in tests_requested:
                total_price+=test.price
            
            data = {
                'date':date,
                'description':description,
                'document':document,
                'tests_requested':tests_requested,
                'total_price':total_price,
            }
            
            context ={
                'data':data,
            }

            return render(request,'client/appointment/appointment_confirm.html',context)

    else :      
        form = AppointmentForm()   
        
         
    return render(request,'client/appointment/appointment_book.html',{'form':form})

@login_required
@permission_required('client.view_client', raise_exception=True)
def client_appointment_confirm(request):
        
    if request.method == 'POST':
            
        if "confirm" in request.POST and request.POST.get('data.date') :
            
            client = request.user.client
            
            tests_requested=[]
            test_count = int(request.POST.get("data.test_count"))
            for i in range(1,test_count+1):
                test_id = int(request.POST.get(f"data.tests_requested{i}"))
                tests_requested.append(test_id)
                
            date = request.POST.get("data.date")
            description = request.POST.get('data.description')
            if "data.document" in request.POST:
                document = request.POST.get('data.document')
            else:
                document=None
                
            total_price = Decimal(request.POST.get('data.total_price'))
            
            data = {
                'date':date,
                'description':description,
                'document':document,
                'tests_requested':tests_requested,
                'total_price':total_price,
                'test_count':test_count,
            }
            
            context ={
                'data':data,
            }
            
            return render(request,'client/appointment/appointment_contract.html',context)
            

    return redirect('client_appointment_book')
    
@login_required
@permission_required('client.view_client', raise_exception=True)
def client_appointment_contract(request):
     
    if request.method == 'POST' :
        
        if "contract" in request.POST and request.POST.get("data.date"):
        
            tests_requested=[]
            test_count = int(request.POST.get("data.test_count"))
            for i in range(1,test_count+1):
                test_id = int(request.POST.get(f"data.tests_requested{i}"))
                tests_requested.append(test_id)
                
            date = request.POST.get("data.date")
            description = request.POST.get('data.description')
            if "data.document" in request.POST:
                document = request.POST.get('data.document')
            else:
                document=None
                
            total_price = Decimal(request.POST.get('data.total_price'))
            
            data = {
                'date':date,
                'description':description,
                'document':document,
                'tests_requested':tests_requested,
                'total_price':total_price,
                'test_count':test_count,
            }
            
            context ={
                'data':data,
            }
            
            return render(request,'client/appointment/appointment_pay.html',context)

        elif "cancel" in request.POST:
            
            return redirect("client")

    
    return redirect('client_appointment_book')
    

@login_required
@permission_required('client.view_client', raise_exception=True)
def client_appointment_pay(request):
    
    session = SessionStore(session_key=request.session.session_key)
    
    if request.method == 'POST' and "cash" in request.POST :
        
        form_token = request.POST.get('csrfmiddlewaretoken')
        used_tokens = session.get('used_tokens', [])
        
        date = datetime.strptime(request.POST.get("data.date"), "%Y-%m-%d").date()
        client = request.user.client
        appointment_exists = Appointment.objects.filter(client=client,date=date).all().exists()

        if form_token in used_tokens or appointment_exists:
            messages.error(request, 'Appointment Already Booked')
                
            return redirect('client')
        
        used_tokens.append(form_token)
        session['used_tokens'] = used_tokens
        session.save()
        
        
        
        client = request.user.client
        payed = request.POST.get('payed')
        
        urgent = False
        tests_requested=[]
        test_count = int(request.POST.get("data.test_count"))
        for i in range(1,test_count+1):
            test_id = int(request.POST.get(f"data.tests_requested{i}"))
            test = TestOffered.objects.get(id=test_id)
            if test.urgent: 
                urgent = True
            tests_requested.append(test)
            
        date = datetime.strptime(request.POST.get("data.date"), "%Y-%m-%d").date()
        description = request.POST.get('data.description')
        
        if "data.document" in request.POST:
            document = request.POST.get('data.document')
            doc_was_provided=True
        else:
            document=None
            doc_was_provided=False
            
        total_price = Decimal(request.POST.get('data.total_price'))
        
  
        appointment = Appointment()
        appointment.client = client
        appointment.date = date
        appointment.description = description
        if doc_was_provided :
            appointment.document = document
        appointment.total_price = total_price
        appointment.urgent = urgent
        appointment.save()

        # Add the tests_requested to the appointment
        appointment.tests_requested.add(*tests_requested)
        
        # 
        payment = Payment(appointment=appointment)
        payment.save()
        
        payment.tests_fee = appointment.total_price
        
        payment.save()
        appointment.save()
        
        if payed == 'payed':
            payment.total_amount_payed += payment.appointment_fee
            payment.payed_appointment_fee = True
            
            payment.save()
            
        
        messages.success(request, f"Please remember your Appointment ID #{appointment.id}")
            
        return redirect('client')
        
    return redirect('client_appointment_book')

@login_required
@permission_required('client.view_client', raise_exception=True)
def verify_token(request):
    if request.method == 'POST':
        session = SessionStore(session_key=request.session.session_key)
        used_tokens = session.get('used_tokens', [])
        
        form_token = request.POST.get('csrfmiddlewaretoken')
        
        date = datetime.strptime(request.POST.get("date"), "%Y-%m-%d").date()
        client = request.user.client
        appointment_exists = Appointment.objects.filter(client=client,date=date).all().exists()
        
        if form_token in used_tokens or appointment_exists:
            # Token is invalid or already used
            return HttpResponse('invalid')
        
        # Token is valid
        return HttpResponse('valid')
    
    # Invalid request method
    return HttpResponse(status=400)

@login_required
@permission_required('client.view_client', raise_exception=True)
def appointment_detail(request, appointment_id):
    # Retrieve the appointment based on the provided ID
    appointment = get_object_or_404(Appointment, id=appointment_id)
    time_difference = appointment.date - timezone.now().date()
    context = {
        'appointment': appointment,
        'time_difference': time_difference.days,
    }
    
    return render(request,'client/appointment/appointment_detail.html',context)


@login_required
@permission_required('client.view_client', raise_exception=True)
def cancel_appointment(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        time_difference = appointment.date - timezone.now().date()
        if time_difference >= timedelta(days=3):
            # Cancel appointment logic here
            appointment.cancelled = True
            appointment.save()
            messages.success(request, "Appointment Successfully Cancelled")
        else:
            messages.error(request, "Cannot cancel Appointment with less than 3 days remaining.")
    else:
        messages.error(request, "Invalid request.")
    
    return redirect('client_appointment_detail', appointment_id=appointment_id)

################################################################

# Request

@login_required
@permission_required('client.view_client', raise_exception=True)
def request_list(request):
    appointments = Appointment.objects.filter(cancelled=False,client=request.user.client)
    
    context = {
        'appointments': appointments
    }
    return render(request,'client/request/request_list.html',context)

@login_required
@permission_required('client.view_client', raise_exception=True)
def request_detail(request):
    
    
    return render(request,'client/request/request_detail.html')

################################################################

# Result

@login_required
@permission_required('client.view_client', raise_exception=True)
def result_list(request):
    
    test_result = Invoice.objects.all().order_by('creation_time')
    
    if request.GET.get('date') :
        date = request.GET.get('date')
        
        if date == 'True' :
            test_result= test_result.order_by('creation_time')
            sort_date = 'False'
        elif date == "False":
            test_result= test_result.order_by('-creation_time')
            sort_date = 'True'
            
            
    if not (request.GET.get('date')) :
        sort_date = 'True'
        
    
    if request.method == "POST" and "search" in request.POST :
        search = request.POST.get("search")
        if search != "" :
            try:
                parsed_number = int(search)
                parsable = True
            except ValueError:
                parsable = False
            
            if parsable and test_result.filter(report__test_result__request__appointment__id=int(search)).exists() :    
                    test_result = test_result.filter(report__test_result__request__appointment__id=int(search)).all()
                
            else :
                context={
                    'sort_date':sort_date,
                }
                
                return render(request,'client/result/result_list.html',context)
    
    invoices = test_result.filter(client=request.user.client, payment_status=True).all()
    unpaid_invoices = test_result.filter(client=request.user.client, payment_status=False).all()

    
    state = request.GET.get('state')
    if state != "all" :
        if state == "unpaid" :
            context = {
                'unpaid_invoices': unpaid_invoices,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'client/result/result_list.html',context)
        if state == "paid" :
            context = {
                'invoices': invoices,
                'sort_date':sort_date,
                'state':state,
            }
            return render(request,'client/result/result_list.html',context)
       
            
    state = 'all'
        
    context = {
        'invoices': invoices,
        'unpaid_invoices': unpaid_invoices,
        'sort_date':sort_date,
        'state':state,
    }
    
    return render(request,'client/result/result_list.html', context)

@login_required
@permission_required('client.view_client', raise_exception=True)
def result_detail(request, invoice_id):
    
    invoice = Invoice.objects.get(id=invoice_id)
    test_result = invoice.report.test_result
    test_request = test_result.request
    appointment = test_request.appointment
    
    context = {
        "invoice":invoice,
        "test_result":test_result,
        "test_request":test_request,
        "appointment":appointment
    }
    
    return render(request,'client/result/result_detail.html' , context )



    
@login_required
@permission_required('client.view_client', raise_exception=True)
def online_pay(request, invoice_id):
    
    invoice = Invoice.objects.get(id=invoice_id)
    test_result = invoice.report.test_result
    test_request = test_result.request
    appointment = test_request.appointment
    
    if request.method == "POST":
        appointment=invoice.report.test_result.request.appointment
        
        # Update the payment status of the invoice
        invoice.payment_status = True
        invoice.save()

        # Update the payment model with the amount paid
        payment = appointment.payment
        payment.payed_nurse_tests_fee = True
        payment.payed_tests_fee = True
        payment.total_amount_payed += invoice.total_price
        payment.save()
        
        appointment.payment_status = True
        appointment.save()
        
        messages.success(request, "Payed Successfully")
        
        return redirect("client_result_list")
    
    context = {
        "invoice":invoice,
        "test_result":test_result,
        "test_request":test_request,
        "appointment":appointment
    }
    
    return render(request,'client/result/online_pay.html' , context )

################################################################

# Profile

@login_required
@permission_required('client.view_client', raise_exception=True)
def client_help(request):
    
    return render(request,'client/profile/help.html')

@login_required
@permission_required('client.view_client', raise_exception=True)
def client_contact(request):
     
    if request.method == 'POST':
        form = ClientContactForm(request.POST)
        
        if form.is_valid():
            
            content = form.cleaned_data["content"]
            subject = f'{ request.user.first_name } { request.user.last_name } is Requesting Support';
            
            html = render_to_string('client/profile/contact_email_template.html',{
                "user":request.user,
                'content':content
            })
            
            try:
                send_mail(subject,content ,EMAIL_HOST_USER,["bravelaboratory2023@gmail.com"],html_message=html)
            except : 
                messages.error(request,'Wireless Connection Failed')
                return redirect('client')

            messages.success(request,'Email Sent Successfully')
            return redirect('client')
        
    else:
        form = ClientContactForm()
        
    context = {
        'form':form,
    }
    
    return render(request,'client/profile/contact.html',context)

@login_required
@permission_required('client.view_client', raise_exception=True)
def client_policy(request):
    
    return render(request,'client/profile/policy.html')

################################################################

# Complaint

@login_required
@permission_required('client.view_client', raise_exception=True)
def create_complaint(request):
    
    if request.method == 'POST':
        
        form = ComplaintForm(request.POST)
        
        if form.is_valid():
            
            content = form.cleaned_data["description"]
            topic = form.cleaned_data["topic"]
            subject = f'{ request.user.first_name } { request.user.last_name } Customer Complaint';
            
            html = render_to_string('client/complaint/complaint_email_template.html',{
                "user":request.user,
                "topic":topic,
                'content':content,
            })
            
            complaint = Complaint(client = request.user.client , description = content , topic = topic)
            complaint.save()
            
            try :
                send_mail(subject,content ,EMAIL_HOST_USER,["bravelaboratory2023@gmail.com"],html_message=html)
            except :
                messages.success(request,"Complaint Sent Successfully")
                return redirect('client')
                
            messages.success(request,"Complaint Sent Successfully")
            return redirect('client')
        
    else:
        form = ComplaintForm()

    context = {
        'form': form
    }
    return render(request, 'client/complaint/complaint.html', context)
    