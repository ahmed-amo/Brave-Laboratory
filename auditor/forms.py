
from django import forms

from main_home.models import Report, TestResult
from nurse.models import Nurse

class NurseForm(forms.Form):
    nurse = forms.ModelChoiceField(queryset=Nurse.objects.all(), empty_label=None)

class UpdateTestsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        test_result = kwargs.pop('test_result')
        super().__init__(*args, **kwargs)
        
        # Iterate over the tests in the test result and create form fields for each test
        for test in test_result.request.tests.all():
            # Create a form field for the test value
            self.fields[f'test_{test.id}_value'] = forms.CharField(
                label=test.test_offered.name,
                initial=test.value,
                required=False
            )
            
            # Iterate over the components of the test and create form fields for each component
            for component in test.components.all():
                # Create a form field for the component value
                self.fields[f'component_{component.id}_value'] = forms.FloatField(
                    label=component.info.name,
                    initial=component.value,
                    required=False
                )
                
