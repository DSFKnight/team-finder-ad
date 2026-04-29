import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.services import get_paginated_page
from .constants import MAX_AUTOCOMPLETE_SKILLS, USERS_PER_PAGE
from .forms import LoginForm, ProfileEditForm, RegistrationForm
from .models import Skill, User


def register_view(request):
    form = RegistrationForm(request.POST or None)
    
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('projects:list')
        
    return render(request, 'users/register.html', {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
    
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('projects:list')
            
        form.add_error(None, "Неверный имейл или пароль")

    return render(request, 'users/login.html', {"form": form})


def logout_view(request):
    logout(request)
    return redirect('projects:list')


def user_list_view(request):
    users_qs = User.objects.all().order_by('id')
    
    active_skill = request.GET.get('skill')
    if active_skill:
        users_qs = users_qs.filter(skills__name=active_skill).distinct()
        
    page_obj = get_paginated_page(request, users_qs, USERS_PER_PAGE)
    
    all_skills = Skill.objects.all().order_by('name')
    
    context = {
        "participants": page_obj,
        "all_skills": all_skills,
        "active_skill": active_skill
    }
    return render(request, 'users/participants.html', context)


def user_detail_view(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    context = {"user": user_obj}
    return render(request, 'users/user-details.html', context)


@login_required
def profile_edit_view(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    
    if form.is_valid():
        form.save()
        return redirect('users:detail', pk=request.user.pk)
        
    return render(request, 'users/edit_profile.html', {"form": form})


def skill_autocomplete_view(request):
    """Возвращает навыки, начинающиеся с переданной подстроки (для JS)."""
    query = request.GET.get('q', '')
    
    if query:
        skills = Skill.objects.filter(name__istartswith=query).order_by('name')[:MAX_AUTOCOMPLETE_SKILLS]
    else:
        skills = Skill.objects.none()
        
    data =[{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def skill_add_view(request, pk):
    """Добавление существующего или нового навыка пользователю."""
    if request.user.pk != pk:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
        
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    skill_id = data.get('skill_id')
    name = data.get('name')

    created = False
    added = False
    skill = None

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name.strip())

    if skill:
        if not request.user.skills.filter(id=skill.id).exists():
            request.user.skills.add(skill)
            added = True

        return JsonResponse({
            "skill_id": skill.id,
            "created": created,
            "added": added
        })
        
    return JsonResponse({"error": "Bad request"}, status=HTTPStatus.BAD_REQUEST)


@login_required
@require_POST
def skill_remove_view(request, pk, skill_id):
    """Удаление навыка у пользователя."""
    if request.user.pk != pk:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
        
    skill = get_object_or_404(Skill, id=skill_id)
    
    if request.user.skills.filter(id=skill.id).exists():
        request.user.skills.remove(skill)
        
    return JsonResponse({"status": "ok"})


@login_required
def change_password_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('users:detail', pk=user.pk)
        
    return render(request, 'users/change_password.html', {'form': form})
