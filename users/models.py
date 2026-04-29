import random
from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_SIZE, AVATAR_TEXT_POSITION, SKILL_NAME_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH, USER_NAME_MAX_LENGTH, USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH, AvatarColor
)
from .managers import UserManager


class Skill(models.Model):
    name = models.CharField(
        max_length=SKILL_NAME_MAX_LENGTH, 
        unique=True, 
        verbose_name="Название навыка"
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    # 1. Поля базы данных
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH, # Использована константа
        verbose_name="Имя"
    )
    surname = models.CharField(
        max_length=USER_SURNAME_MAX_LENGTH, # Использована константа
        verbose_name="Фамилия"
    )
    avatar = models.ImageField(upload_to="avatars/", verbose_name="Аватар")
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH, # Использована константа
        verbose_name="Телефон"
    )
    github_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на Github")
    about = models.TextField(
        max_length=USER_ABOUT_MAX_LENGTH, # Использована константа
        blank=True, 
        verbose_name="О себе"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    skills = models.ManyToManyField(
        Skill, 
        related_name="users", 
        blank=True, 
        verbose_name="Навыки",
    )

    # 2. Менеджеры и константы класса
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    # 3. Мета-класс
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    # 4. Магические методы
    def __str__(self):
        return f"{self.name} {self.surname}"

    # 5. Переопределенные методы Django
    def save(self, *args, **kwargs):
        if not self.avatar:
            self.generate_avatar()
        super().save(*args, **kwargs)

    # 6. Кастомные методы
    def generate_avatar(self):
        # Используем константы и Enum
        bg_color = random.choice(list(AvatarColor))
        img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        letter = self.name[0].upper() if self.name else "U"
        font = ImageFont.load_default()
        
        draw.text(AVATAR_TEXT_POSITION, letter, fill="white", font=font, align="center")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.avatar.save(f'{self.email}_avatar.png', ContentFile(buffer.getvalue()), save=False)
