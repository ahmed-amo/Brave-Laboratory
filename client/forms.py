from django import forms
from client.models import Client

from main_home.models import Appointment, Complaint, MedicalDocument 

TOPIC_CHOICES = [ ('Billing', 'Billing'),    ('Customer Service', 'Customer Service'),    ('Facilities', 'Facilities'),    ('Quality of Service', 'Quality of Service'),    ('Other', 'Other'),]

class ComplaintForm(forms.ModelForm):
    topic = forms.ChoiceField(choices=TOPIC_CHOICES)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    
    class Meta:
        model = Complaint
        fields = ['topic','description']

class AppointmentForm(forms.ModelForm):
    
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}),required=False)
    
    class Meta:
        model = Appointment
        fields = ['date', "tests_requested",'description', 'document']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].required = False
        self.fields['tests_requested'].required = False

        
class AppointmentPaymentForm(forms.ModelForm):
    
    PAYMENT_CHOICES = [
        ('PP', 'Pre-Pay'),
        ('OR', 'On-Receive'),
    ]

    payment_option = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.Select)
    
    class Meta:
        model = Appointment
        fields = ["payment_option"]
        


class ClientContactForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)