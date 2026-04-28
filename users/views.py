from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from .models import User, Skill
from .forms import RegistrationForm, LoginForm

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Сразу авторизуем после регистрации
            return redirect('/projects/list/')
    else:
        form = RegistrationForm()
    
    return render(request, 'users/register.html', {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/projects/list/')
            else:
                form.add_error(None, "Неверный имейл или пароль")
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('/projects/list/')

def user_list_view(request):
    # Базовый список всех пользователей, сортировка по id (в порядке добавления)
    users_qs = User.objects.all().order_by('id')
    
    active_skill = request.GET.get('skill')
    if active_skill:
        # Оставляем только тех пользователей, у которых есть навык с таким именем
        users_qs = users_qs.filter(skills__name=active_skill).distinct()
        
    # Пагинация: 12 пользователей на страницу
    paginator = Paginator(users_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем все навыки по алфавиту для отображения облака тегов
    all_skills = Skill.objects.all().order_by('name')
    
    context = {
        "participants": page_obj,
        "all_skills": all_skills,
        "active_skill": active_skill
    }
    return render(request, 'users/participants.html', context)

def user_detail_view(request, pk):
    # Получаем пользователя по id
    user_obj = get_object_or_404(User, pk=pk)
    context = {"user": user_obj}
    return render(request, 'users/user-details.html', context)

@login_required(login_url='/users/login/')
def profile_edit_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            # После успеха кидаем на страницу своего профиля
            return redirect('users:detail', pk=request.user.pk)
    else:
        # Заполняем форму текущими данными пользователя
        form = ProfileEditForm(instance=request.user)
        
    return render(request, 'users/edit_profile.html', {"form": form})

def skill_autocomplete_view(request):
    """Возвращает до 10 навыков, начинающихся с переданной подстроки (для JS)"""
    q = request.GET.get('q', '')
    if q:
        skills = Skill.objects.filter(name__istartswith=q).order_by('name')[:10]
    else:
        skills = Skill.objects.none()
        
    # Формируем список словарей
    data =[{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)

@login_required(login_url='/users/login/')
@require_POST
def skill_add_view(request, pk):
    """Добавление существующего или нового навыка пользователю"""
    # Проверка, что пользователь редактирует свои навыки, а не чужие
    if request.user.pk != pk:
        return JsonResponse({"error": "Forbidden"}, status=403)
        
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
        # Если такого навыка нет, создаем его
        skill, created = Skill.objects.get_or_create(name=name)

    if skill:
        # Если у пользователя еще нет этого навыка — добавляем
        if not request.user.skills.filter(id=skill.id).exists():
            request.user.skills.add(skill)
            added = True

        return JsonResponse({
            "skill_id": skill.id,
            "created": created,
            "added": added
        })
        
    return JsonResponse({"error": "Bad request"}, status=400)

@login_required(login_url='/users/login/')
@require_POST
def skill_remove_view(request, pk, skill_id):
    """Удаление навыка у пользователя"""
    if request.user.pk != pk:
        return JsonResponse({"error": "Forbidden"}, status=403)
        
    skill = get_object_or_404(Skill, id=skill_id)
    if request.user.skills.filter(id=skill.id).exists():
        request.user.skills.remove(skill)
        
    return JsonResponse({"status": "ok"})

@login_required(login_url='/users/login/')
def change_password_view(request):
    if request.method == 'POST':
        # Передаем текущего пользователя и данные из POST
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Обновляем сессию, чтобы пользователя не разлогинило
            update_session_auth_hash(request, user)
            # Перекидываем в профиль
            return redirect('users:detail', pk=user.pk)
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'users/change_password.html', {'form': form})