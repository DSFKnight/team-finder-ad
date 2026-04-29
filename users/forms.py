import re

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .mixins import GithubUrlCleanMixin

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


# Наследуемся от GithubUrlCleanMixin (он должен идти первым)
class ProfileEditForm(GithubUrlCleanMixin, forms.ModelForm):
    class Meta:
        model = User
        fields =['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not re.match(r'^(8|\+7)\d{10}$', phone):
                raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")
            
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
                
            if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Пользователь с таким номером уже существует")
                
        return phone
