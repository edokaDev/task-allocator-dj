from django import forms
from .models import User, Task, Project


class DateInput(forms.DateInput):
    input_type = 'date'


class TaskForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_employee=True),
        widget=forms.Select(
            attrs={
                "class": "form-control"
            }
        )
    )
    description = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "description",
                "class": "form-control"
            }
        )
    )
    sub_tasks = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "comma seperated sub tasks",
                "class": "form-control"
            }
        )
    )
    end = forms.DateTimeField(
        widget=DateInput(
            attrs={
                "class": "form-control"
            }
        )
    )


class ProjectForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Project Name",
                "class": "form-control"
            }
        )
    )
    description = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "description",
                "class": "form-control"
            }
        )
    )
    end = forms.DateTimeField(
        widget=DateInput(
            attrs={
                "class": "form-control"
            }
        )
    )
