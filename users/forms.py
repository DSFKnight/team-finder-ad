import re
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        # Переопределяем метод save, чтобы пароль хэшировался, а не хранился открытым текстом
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields =['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Проверяем формат: 8 или +7 и ровно 10 цифр после
            if not re.match(r'^(8|\+7)\d{10}$', phone):
                raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")
            
            # Приводим к единому формату
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
                
            # Проверяем уникальность (исключая текущего пользователя)
            if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Пользователь с таким номером уже существует")
                
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if 'github.com' not in url.lower():
                raise ValidationError("Ссылка должна вести на Github")
        return url