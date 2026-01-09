from django import forms
from .models import ClassGroup
from accounts.models import UserProfile

class ClassGroupForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.filter(role='student'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Alumnos del grupo'        
    )

    class Meta:
        model = ClassGroup
        fields = ['name', 'students']
        labels = {
            'name': 'Nombre del grupo',
        }
