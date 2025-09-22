from django import forms
from client.models import Client

from main_home.models import Appointment

class ConfirmationForm(forms.Form):
    appointment_fee_paid = forms.BooleanField(required=True)
    
    def __init__(self, *args, **kwargs):
        appointment_fee = kwargs.pop('appointment_fee', None)
        super().__init__(*args, **kwargs)
        
        if appointment_fee:
            self.fields['appointment_fee_paid'].label = f'Appointment Fee Paid? (Appointment Fee: {appointment_fee})'


class AppointmentForm(forms.ModelForm):
    
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}),required=False)
    client = forms.ModelChoiceField(queryset=Client.objects.all(), widget=forms.Select(attrs={'class': 'formbold-form-input select-1'}))
    class Meta:
        model = Appointment
        fields = ['client','date', "tests_requested",'description', 'document']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].required = False
        self.fields['tests_requested'].required = False
