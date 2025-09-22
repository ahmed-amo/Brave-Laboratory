# forms.py
from django import forms
from main_home.models import ComponentInformation, Evaluation, Report, Test, TestOffered, TestResult



class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history']


class AddTestForm(forms.Form):
    test_offered = forms.ModelChoiceField(queryset=TestOffered.objects.none(), empty_label=None)

    def __init__(self, appointment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing_tests = appointment.tests_requested.all()
        self.fields['test_offered'].queryset = TestOffered.objects.exclude(id__in=existing_tests.values_list('id', flat=True))
        
        
class AddComponentForm(forms.Form):
    component = forms.ModelChoiceField(queryset=ComponentInformation.objects.none(), empty_label=None)

    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test')
        super().__init__(*args, **kwargs)
        self.fields['component'].queryset = ComponentInformation.objects.exclude(id__in=test.components.values_list('info__id', flat=True))


class TestFinalizeForm(forms.ModelForm):
    
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    
    class Meta:
        model = Test
        fields = ['description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add fields for each component associated with the test
        for component in self.instance.components.all():
            field_name = f"component_{component.id}"
            label = f"{component.info.name} ({component.info.unit})"
            low_range = str(component.info.low_male_range) if component.info.low_male_range else 'haha'
            high_range = str(component.info.high_male_range) if component.info.high_male_range else 'haaa'
            self.fields[field_name] = forms.FloatField(label=label, 
                                            widget=forms.NumberInput(attrs=
                                            {'placeholder': f'{low_range} ~ {high_range}'}))

    def save(self, commit=True):
        test = super().save(commit=False)
        
        # Save the test value and description
        if commit:
            test.save()
        
        # Save the values of each component associated with the test
        for component in test.components.all():
            field_name = f"component_{component.id}"
            value = self.cleaned_data.get(field_name)
            if value is not None:
                component.value = value
                component.save()

        return test
    
    
