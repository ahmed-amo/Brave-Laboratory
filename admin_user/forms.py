from django import forms
from django.contrib.auth.models import User,Group
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from datetime import date
from django.contrib.auth.hashers import make_password

from main_home.models import BloodBank

class BloodBankAdd(forms.ModelForm):
    class Meta:
        model= BloodBank
        fields=["codename","capacity"]
    
class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirmation', 'groups']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError('Passwords do not match')

        # Hash the password
        if password:
            hashed_password = make_password(password)
            cleaned_data['password'] = hashed_password

        return cleaned_data
    
phone_regex = RegexValidator(
    regex=r'^0[5-7][0-9]{8}$',
    message='Please enter a valid phone number starting with 05, 06 or 07 and has 10 digits in total'
)
    
class UserAddForm(UserCreationForm):
    phone_number = forms.CharField(max_length=10,validators=[phone_regex])
    gender = forms.ChoiceField(choices=((None, 'Choose Here :'),('M', 'Male'), ('F', 'Female')))
    address = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    phone_number.widget.attrs.update({"placeholder":"+213 0000000000"})
    address.widget.attrs.update({"placeholder":"Setif, El Eulma"})
    
    class Meta():
        model = User
        widgets = {
            'username' : forms.TextInput(attrs={'placeholder': 'ahmed'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ahmed.amokrane@gmail.com'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'John'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Doe'}),
        }
        fields = ['username','email','first_name', 'last_name' , 'phone_number',
                  'gender' , 'address' , 'date_of_birth', 'password1' , 'password2']
        
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < 14:
            raise forms.ValidationError("You must be 14 years old or older to register.")
        return date_of_birth