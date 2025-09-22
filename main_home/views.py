from django.conf import settings
from django.contrib.auth import (
    authenticate, login, update_session_auth_hash
)
from django.contrib.auth.forms import (
    AuthenticationForm ,
    PasswordChangeForm
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required,  permission_required
from django.contrib.auth.models import Group
from django.shortcuts import render,redirect
from brave_lab_project.settings import EMAIL_HOST_USER
from client.models import Client
from main_home.models import Invoice
from .forms import (
   AdminUserUpdateForm,
   UserRegisterForm, 
   UserUpdateForm, 
   ClientUpdateForm,
   NurseUpdateForm,
   ReceptionistUpdateForm,
   AuditorUpdateForm,
   HomeContactUsForm,
)
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .utils import is_admin_user, is_client, is_nurse, is_receptionist, is_auditor

from django.contrib.auth.hashers import check_password

from django.template.loader import get_template
from django.http import HttpResponse

from main_home.utils import render_to_pdf

from verify_email.email_handler import send_verification_email
from django.utils import timezone
from django.contrib.auth.models import User
# Create your views here.



@login_required

def profile_settings(request):
    old_pass_correct = False
    old_password =""
    if request.method == 'POST':
        if 'update' in request.POST :
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                print("hello")
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile_settings')
            
        elif 'confirm' in request.POST :
            entered_password = request.POST.get("old_password")
            if check_password(entered_password, request.user.password):
                old_pass_correct = True
                form = PasswordChangeForm(request.user)
                old_password=entered_password
            else:
                form = PasswordChangeForm(request.user)
    else:
        form = PasswordChangeForm(request.user)
        
    group_name = request.user.groups.first().name
    
    context={
        'old_pass_correct':old_pass_correct,
        'old_password':old_password,
        'form':form,
    }
        
    return render(request, f'{group_name}/profile/settings.html',context)


def home(request):
    # Accessing the home page requires log out
    user = request.user
    if user.is_authenticated : 
        if user.is_superuser :
            return redirect('/admin/')
        elif is_client(user) :
            return redirect('client')
        elif is_nurse(user) :
            return redirect('nurse')
        elif is_receptionist(user) :
            return redirect('receptionist')
        elif is_auditor(user) :
            return redirect('auditor')
        elif is_admin_user(user) :
            return redirect('admin_user')
        
    if request.method == 'POST':
        
        form = HomeContactUsForm(request.POST)
        
        if form.is_valid():
            
            email = form.cleaned_data["email"]
            content = form.cleaned_data["content"]
            
            html = render_to_string('main_home/contact_email_template.html',{
                "email": email,
                'content':content
            })
            try:
                send_mail("Internet User Support",content ,EMAIL_HOST_USER,["bravelaboratory2023@gmail.com"],html_message=html)
            except:
                
                return redirect('home')
                
            return redirect('home')
        
    else:
        form = HomeContactUsForm()
        
    context = {
        'form':form,
    }
    
    return render(request,'main_home/home.html',context)



def register(request):
    # Accessing the register page requires log out
    one_day_ago = timezone.now() - timezone.timedelta(days=1)
    User.objects.filter(is_active=False, date_joined__lt=one_day_ago).delete()
    
    user = request.user
    if user.is_authenticated : 
        if user.is_superuser :
            return redirect('/admin/')
        elif is_client(user) :
            return redirect('client')
        elif is_nurse(user) :
            return redirect('nurse')
        elif is_receptionist(user) :
            return redirect('receptionist')
        elif is_auditor(user) :
            return redirect('auditor')
        elif is_admin_user(user) :
            return redirect('admin_user')
    
    # handling of a post request from register page
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Automaticly save the client and add him to the client group
            # save the user into the user database
            # user = form.save()
            user = send_verification_email(request, form)
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
            
            return redirect('check_email')
            
    else :
        form = UserRegisterForm()

    return render(request,'main_home/register.html', {'form':form})

def check_email(request):
    user = request.user
    if user.is_authenticated : 
        if user.is_superuser :
            return redirect('/admin/')
        elif is_client(user) :
            return redirect('client')
        elif is_nurse(user) :
            return redirect('nurse')
        elif is_receptionist(user) :
            return redirect('receptionist')
        elif is_auditor(user) :
            return redirect('auditor')
        elif is_admin_user(user) :
            return redirect('admin_user')
    
    return render(request,'main_home/check_email.html')
        
    

def login_view(request):
    # Accessing the register page requires log out
    user = request.user
    if user.is_authenticated : 
        if user.is_superuser :
            return redirect('/admin/')
        elif is_client(user) :
            return redirect('client')
        elif is_nurse(user) :
            return redirect('nurse')
        elif is_receptionist(user) :
            return redirect('receptionist')
        elif is_auditor(user) :
            return redirect('auditor')
        elif is_admin_user(user) :
            return redirect('admin_user')
    
    # handling of a post request from register page
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None :
                login(request,user)
                
                if user.is_superuser :
                    return redirect('/admin/')
                elif is_client(user) :
                    return redirect('client')
                elif is_nurse(user) :
                    return redirect('nurse')
                elif is_receptionist(user) :
                    return redirect('receptionist')
                elif is_auditor(user) :
                    return redirect('auditor')
                elif is_admin_user(user) :
                    return redirect('admin_user')
                
    else:
        form = AuthenticationForm()
        
    return render(request, 'main_home/login.html', {'form': form})


@login_required

def profile_update(request):
    
    user = request.user
    
    if request.method == 'POST':
        
        user_form = UserUpdateForm(request.POST, instance=user)
        
        if is_client(user) :
            actor_form = ClientUpdateForm(request.POST, request.FILES, instance=user.client)
        elif is_nurse(user) :
            actor_form = NurseUpdateForm(request.POST, request.FILES, instance=user.nurse)
        elif is_receptionist(user) :
            actor_form = ReceptionistUpdateForm(request.POST, request.FILES, instance=user.receptionist)
        elif is_auditor(user) :
            actor_form = AuditorUpdateForm(request.POST, request.FILES, instance=user.auditor)
        elif is_admin_user(user) :
            actor_form = AdminUserUpdateForm(request.POST, request.FILES, instance=user.adminuser)
        
        if user_form.is_valid() and actor_form.is_valid():
            user_form.save()
            actor_form.save()
            return redirect('profile_update')
        
    else:
        user_form = UserUpdateForm(instance=user)
        
        if is_client(user) :
            actor_form = ClientUpdateForm(instance=user.client)
        elif is_nurse(user) :
            actor_form = NurseUpdateForm(instance=user.nurse)
        elif is_receptionist(user) :
            actor_form = ReceptionistUpdateForm(instance=user.receptionist)
        elif is_auditor(user) :
            actor_form = AuditorUpdateForm(instance=user.auditor)
        elif is_admin_user(user) :
            actor_form = AdminUserUpdateForm(instance=user.adminuser)

        
    context={
        "user_form":user_form,
        "actor_form":actor_form,
    }
    
    group_name = user.groups.first().name
    
        
    return render(request, f'{group_name}/profile/profile.html', context)






@login_required
def pdf_client_invoice(request, invoice_id):
    template = get_template('pdf/invoice.html')
    
    invoice = Invoice.objects.get(id=invoice_id)
    test_result = invoice.report.test_result
    test_request = test_result.request
    tests = test_request.tests.all()
    appointment = test_request.appointment
    context = {
        "invoice":invoice,
        "test_result":test_result,
        "test_request":test_request,
        "tests":tests,
        "appointment":appointment,
        "STATIC_ROOT":settings.MEDIA_ROOT,
    }
    
    html = template.render(context)
    pdf = render_to_pdf('pdf/invoice.html', context)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" % (invoice.id)
        content = f"inline; filename={filename}"
        download = request.GET.get("download")
        
        if download:
            content = f"attachment; filename={filename}" 
        
        response['Content-Disposition'] = content
        return response
    
    return HttpResponse("Not found")
    
@login_required
def pdf_client_results(request, invoice_id):
    template = get_template('pdf/test_results.html')
    
    invoice = Invoice.objects.get(id=invoice_id)
    test_result = invoice.report.test_result
    test_request = test_result.request
    tests = test_request.tests.all()
    appointment = test_request.appointment
    context = {
        "invoice":invoice,
        "test_result":test_result,
        "test_request":test_request,
        "tests":tests,
        "appointment":appointment,
        "gender":appointment.client.gender,
        "STATIC_ROOT":settings.MEDIA_ROOT,
    }
    
    html = template.render(context)
    pdf = render_to_pdf('pdf/test_results.html', context)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" % (invoice.id)
        content = f"inline; filename={filename}"
        download = request.GET.get("download")
        
        if download:
            content = f"attachment; filename={filename}" 
        
        response['Content-Disposition'] = content
        return response
    
    return HttpResponse("Not found")


