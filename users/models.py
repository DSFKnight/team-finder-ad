from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True, verbose_name="Название навыка")

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=124, verbose_name="Имя")
    surname = models.CharField(max_length=124, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to="avatars/", verbose_name="Аватар")
    phone = models.CharField(max_length=12, verbose_name="Телефон")
    github_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на Github")
    about = models.TextField(max_length=256, blank=True, verbose_name="О себе")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # M2M связь для навыков
    skills = models.ManyToManyField(Skill, related_name="users", blank=True, verbose_name="Навыки")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        # Генерация аватарки с первой буквой имени
        size = 200
        bg_color = random.choice(['#E57373', '#81C784', '#64B5F6', '#FFD54F', '#BA68C8'])
        img = Image.new('RGB', (size, size), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        letter = self.name[0].upper() if self.name else "U"
        
        font = ImageFont.load_default()
        
        draw.text((85, 85), letter, fill="white", font=font, align="center")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.avatar.save(f'{self.email}_avatar.png', ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return f"{self.name} {self.surname}"