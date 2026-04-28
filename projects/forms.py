from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # Перечисляем нужные поля
        fields =['name', 'description', 'github_url', 'status']