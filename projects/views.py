from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm

def project_list_view(request):
    projects_qs = Project.objects.all().order_by('-created_at')
    paginator = Paginator(projects_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {"projects": page_obj}
    return render(request, 'projects/project_list.html', context)

def project_detail_view(request, pk):
    # Получаем проект или отдаем 404 ошибку
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project-details.html', {"project": project})

@login_required(login_url='/users/login/')
def project_create_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Сохраняем
            project = form.save(commit=False)
            project.owner = request.user # Автором становится текущий пользователь
            project.save()
            # Добавляем автора в список участников
            project.participants.add(request.user)
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()
        
    return render(request, 'projects/create-project.html', {"form": form, "is_edit": False})

@login_required(login_url='/users/login/')
def project_edit_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем, что редактирует именно автор
    if request.user != project.owner:
        return redirect('projects:detail', pk=pk)
        
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
        
    return render(request, 'projects/create-project.html', {"form": form, "is_edit": True})

@login_required(login_url='/users/login/')
def project_complete_view(request, pk):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=pk)
        # Проверяем права и текущий статус
        if request.user == project.owner and project.status == 'open':
            project.status = 'closed'
            project.save()
            return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"status": "error"}, status=400)

@login_required(login_url='/users/login/')
def project_participate_view(request, pk):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=pk)
        
        # Проверяем и меняем статус
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            # Флаг для JS: пользователь НЕ участник
            is_participating = False
        else:
            project.participants.add(request.user)
            # Флаг для JS: пользователь участник
            is_participating = True
            
        # Возвращаем JSON с флагом
        return JsonResponse({
            "status": "ok", 
            "participant": is_participating
        })
        
    return JsonResponse({"error": "Bad request"}, status=400)