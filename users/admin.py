from django.contrib import admin
from .models import User, Skill

# Регистрируем модель пользователя
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'is_staff')
    search_fields = ('email', 'name', 'surname')

# Регистрируем модель навыков
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)