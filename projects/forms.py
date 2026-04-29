from django import forms

from users.mixins import GithubUrlCleanMixin
from .models import Project


class ProjectForm(GithubUrlCleanMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
