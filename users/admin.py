from django.contrib import admin
from django.db.models import Count

from .models import Skill, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'email', 
        'name', 
        'surname', 
        'is_active', 
        'is_staff', 
        'participated_projects_count'
    )
    
    search_fields = ('email', 'name', 'surname', 'phone')
    list_filter = ('is_active', 'is_staff')
    filter_horizontal = ('skills',)
    ordering = ('id',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 'participated_projects' - это related_name из модели Project
        return qs.annotate(projects_count=Count('participated_projects'))

    @admin.display(description='Участвует в проектах', ordering='projects_count')
    def participated_projects_count(self, obj):
        return obj.projects_count


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)