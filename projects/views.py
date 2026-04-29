from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .constants import PROJECTS_PER_PAGE
from .forms import ProjectForm
from .models import Project
from .services import get_paginated_page


def project_list_view(request):
    projects_qs = Project.objects.select_related('owner').prefetch_related(
        'participants'
    ).order_by('-created_at')
    
    page_obj = get_paginated_page(request, projects_qs, PROJECTS_PER_PAGE)
    
    context = {"projects": page_obj}
    return render(request, 'projects/project_list.html', context)


def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project-details.html', {"project": project})


@login_required
def project_create_view(request):
    form = ProjectForm(request.POST or None)
    
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect('projects:detail', pk=project.pk)
        
    return render(request, 'projects/create-project.html', {"form": form, "is_edit": False})


@login_required
def project_edit_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.user != project.owner:
        return redirect('projects:detail', pk=pk)
        
    form = ProjectForm(request.POST or None, instance=project)
    
    if form.is_valid():
        form.save()
        return redirect('projects:detail', pk=project.pk)
        
    return render(request, 'projects/create-project.html', {"form": form, "is_edit": True})


@login_required
def project_complete_view(request, pk):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=pk)
        
        if request.user == project.owner and project.status == Project.STATUS_OPEN:
            project.status = Project.STATUS_CLOSED
            project.save()
            return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})
            
    return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)


@login_required
def project_participate_view(request, pk):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=pk)
        
        if is_participating := project.participants.filter(pk=request.user.pk).exists():
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)
            
        return JsonResponse({
            "status": "ok", 
            "participant": not is_participating
        })
        
    return JsonResponse({"error": "Bad request"}, status=HTTPStatus.BAD_REQUEST)
