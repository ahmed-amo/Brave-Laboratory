
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.models import User,Group
from django.http import HttpResponse
from admin_user.forms import BloodBankAdd, UserAddForm, UserUpdateForm
from auditor.models import Auditor

from main_home.models import BloodBank
from django.contrib import messages

from nurse.models import Nurse
from receptionist.models import Receptionist

def admin_user(request):
    # Get the superuser
    superuser = User.objects.filter(is_superuser=True).first()

    # Get the admin_user group
    admin_group = Group.objects.get(name='admin_user')
                 
    users = User.objects.exclude(pk=superuser.pk).exclude(groups=admin_group).all().order_by('-date_joined')
   
    if request.GET.get('date_sort') :
        date = request.GET.get('date')
        
        if date == 'True' :
            users= users.order_by('date_joined')
            sort_date = 'False'
        elif date == "False":
            users= users.order_by('-date_joined')
            sort_date = 'True'
            
        sort_username= request.GET.get('username')
        sort_type= request.GET.get('type')
    
            
    if request.GET.get('username_sort'):
        username = request.GET.get('username')
        
        if username == 'True':
            users = users.order_by("-username")
            sort_username= 'False'
        elif username == 'False':
            users = users.order_by("username")
            sort_username= 'True'
            
        
        sort_date= request.GET.get('date')
        sort_type= request.GET.get('type')
        
    if request.GET.get('type_sort'):
        nurse = request.GET.get('type')
        
        if nurse == 'True':
            users = users.order_by("-groups__name")
            sort_type= 'False'
        elif nurse == 'False':
            users = users.order_by("groups__name")
            sort_type= 'True'
            
        
        sort_date= request.GET.get('date')
        sort_username= request.GET.get('username')
        
            
    if not (request.GET.get('username_sort')) and not (request.GET.get('date_sort')) and not (request.GET.get('type_sort')):
        sort_date = 'True'
        sort_username = 'True'
        sort_type = 'True'
        
    
    if request.method == "POST" and "search" in request.POST :
        search = request.POST.get("search")
        if search != "" :
            try:
                parsed_number = int(search)
                parsable = True
            except ValueError:
                parsable = False
            
            if parsable and users.filter(id=int(search)).exists() :    
                    users = users.filter(id=int(search)).all()
                
            elif users.filter(username=search).exists() :
                users = users.filter(username=search).all()
                
            else :
                context={
                    'sort_username':sort_username,
                    'sort_date':sort_date,
                    'sort_type':sort_type,
                }
                
                return render(request,'admin_user/admin_user.html',context)
    
        
    
    context = {
        'users':users,
        'sort_username':sort_username,
        'sort_date':sort_date,
        'sort_type':sort_type,
    }
    
    return render(request,'admin_user/admin_user.html',context)

def user_detail(request, user_id):
    user_detail = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if 'delete' in request.POST:
            user_detail.delete() 
            deleted="User Deleted Successfully !"
            messages.success(request,deleted)
            return redirect('admin_user')
        elif 'update' in request.POST:
            # Logic to update the user
            return redirect('user_update', user_id=user_id)

    context = {'user_detail': user_detail}    
    return render(request,'admin_user/users/user_detail.html',context)


def user_update(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = UserUpdateForm(instance=user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            updated="User Updated Successfully !"
            messages.success(request,updated)

            return redirect('user_detail', user_id=user_id)

    context = {'form': form}
    return render(request, 'admin_user/users/user_update.html', context)

def account_add(request):
    # Add your logic for the account_add view here
    return render(request,'admin_user/accounts/account_add.html')

def account_add_nurse(request):
    
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            # Automaticly save the client and add him to the client group
            # save the user into the user database
            user = form.save()
            # add him to the client group
            group = Group.objects.get(name="nurse")
            group.user_set.add(user)
            # extract form data
            data = form.cleaned_data
            phone_number = data.get("phone_number")
            gender = data.get("gender")
            address = data.get("address")
            date_of_birth = data.get("date_of_birth")
            # add him with any additionel information into the client table
            Nurse.objects.create(user = user,
                            phone_number = phone_number,
                            gender = gender,
                            address = address,
                            date_of_birth = date_of_birth)
            
            added="Nurse Added Successfully !"
            messages.success(request,added)       
            return redirect('account_add')
            
    else :
        form = UserAddForm()
    
    context ={
        'form':form,
    }
    
    return render(request,'admin_user/accounts/account_add_nurse.html',context)

def account_add_receptionist(request):
    
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            # Automaticly save the client and add him to the client group
            # save the user into the user database
            user = form.save()
            # add him to the client group
            group = Group.objects.get(name="receptionist")
            group.user_set.add(user)
            # extract form data
            data = form.cleaned_data
            phone_number = data.get("phone_number")
            gender = data.get("gender")
            address = data.get("address")
            date_of_birth = data.get("date_of_birth")
            # add him with any additionel information into the client table
            Receptionist.objects.create(user = user,
                            phone_number = phone_number,
                            gender = gender,
                            address = address,
                            date_of_birth = date_of_birth)
            
            added="Receptionist Added Successfully !"
            messages.success(request,added)       
            return redirect('account_add')
            
    else :
        form = UserAddForm()
    
    context ={
        'form':form,
    }
    
    return render(request,'admin_user/accounts/account_add_receptionist.html',context)

def account_add_auditor(request):
    
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            # Automaticly save the client and add him to the client group
            # save the user into the user database
            user = form.save()
            # add him to the client group
            group = Group.objects.get(name="auditor")
            group.user_set.add(user)
            # extract form data
            data = form.cleaned_data
            phone_number = data.get("phone_number")
            gender = data.get("gender")
            address = data.get("address")
            date_of_birth = data.get("date_of_birth")
            # add him with any additionel information into the client table
            Auditor.objects.create(user = user,
                            phone_number = phone_number,
                            gender = gender,
                            address = address,
                            date_of_birth = date_of_birth)
            
            added="Auditor Added Successfully !"
            messages.success(request,added)       
            return redirect('account_add')
            
    else :
        form = UserAddForm()
    
    context ={
        'form':form,
    }
    
    return render(request,'admin_user/accounts/account_add_auditor.html',context)

def blood_banks(request):
    banks = BloodBank.objects.all()
    
    context={
        'banks':banks,
    }
    
    return render(request,'admin_user/banks/blood_banks.html',context)

def blood_bank_detail(request, bank_id):
    # Add your logic for the blood_bank_detail view here
    bank = get_object_or_404(BloodBank, id=bank_id)  # Assuming you have a BloodBank model
    
    context={
        'bank':bank,
    }
    
    return render(request,'admin_user/banks/blood_bank_detail.html', context)

def blood_bank_add(request):
    # Add your logic for the blood_bank_add view here
    if request.method == 'POST':
        form = BloodBankAdd(request.POST)
        if form.is_valid():
            bank = form.save()
            
            added = "Blood Bank Added Successfully !"
            messages.success(request,added)
            
            return redirect("blood_bank_detail",bank_id=bank.id)
    else :
        form = BloodBankAdd()
    
    context = {
        'form':form,
    }
    
    return render(request,'admin_user/banks/blood_bank_add.html',context)