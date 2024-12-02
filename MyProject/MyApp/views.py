from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from .forms import UserProfileForm, PasswordChangeForm, DeleteAccountForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Project, ProjectMember
from .forms import AddMemberForm, UpdateRoleForm
from .models import Project, Task, User
from .forms import ProjectForm
from .models import Task
from .forms import TaskForm
import logging
from django.http import HttpResponse, HttpResponseForbidden

class TeamLeaderRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(('/tasks', '/projects')) and request.user.role != 'project_leader':
            return HttpResponseForbidden("You are not authorized to access this resource.")
        return self.get_response(request)

@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    print(tasks)  # Debugging: Print tasks in the console
    return render(request, 'task_list.html', {'tasks': tasks})


logger = logging.getLogger(__name__)

@login_required
def task_create(request):
    if request.user.role != 'project_leader':
        return HttpResponseForbidden("You are not authorized to create tasks.")
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    if request.user.role != 'project_leader':
        return HttpResponseForbidden("You are not authorized to update tasks.")
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    if request.user.role != 'project_leader':
        return HttpResponseForbidden("You are not authorized to delete tasks.")
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'task_confirm_delete.html', {'task': task})

@login_required
def project_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'project_list.html', {'projects': projects})


@login_required
def project_create(request):
    if request.user.role != 'project_leader':
        return HttpResponseForbidden("You are not authorized to create projects.")
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form})

@login_required
def project_update(request, pk):
    if request.user.role != 'project_leader':
        return HttpResponseForbidden("You are not authorized to update projects.")
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_form.html', {'form': form})

@login_required
def project_delete(request, pk):
    if request.user.role != 'project_leader':
        return HttpResponseForbidden("You are not authorized to delete projects.")
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'project_confirm_delete.html', {'project': project})

@login_required
def project_members(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    members = ProjectMember.objects.filter(project=project)

    if request.method == "POST":
        form = AddMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.project = project
            member.save()
            messages.success(request, "Member added successfully!")
            return redirect('project_members', project_id=project.id)
    else:
        form = AddMemberForm()

    return render(request, 'project_members.html', {'project': project, 'members': members, 'form': form})


@login_required
def update_member_role(request, project_id, member_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    member = get_object_or_404(ProjectMember, id=member_id, project=project)

    if request.method == "POST":
        form = UpdateRoleForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Role updated successfully!")
            return redirect('project_members', project_id=project.id)
    else:
        form = UpdateRoleForm(instance=member)

    return render(request, 'update_role.html', {'form': form, 'member': member})


@login_required
def remove_member(request, project_id, member_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    member = get_object_or_404(ProjectMember, id=member_id, project=project)

    if request.method == "POST":
        member.delete()
        messages.success(request, "Member removed successfully!")
        return redirect('project_members', project_id=project.id)

    return render(request, 'remove_member.html', {'member': member})

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm']:
            request.user.delete()
            messages.success(request, "Your account has been deleted.")
            return redirect('home')  # Redirect to the home page or login page after account deletion
    else:
        form = DeleteAccountForm()

    return render(request, 'delete_account.html', {'form': form})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect back to profile page after saving
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        # Pass the current user instance to the form
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update session auth hash to keep the user logged in after changing the password
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password has been successfully changed!")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})

@login_required
def profile_view(request):
    profile_form = UserProfileForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    delete_form = DeleteAccountForm()

    if request.method == "POST":
        if "edit_profile" in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')

        elif "change_password" in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed successfully.")
                return redirect('profile')

        elif "delete_account" in request.POST:
            delete_form = DeleteAccountForm(request.POST)
            if delete_form.is_valid() and delete_form.cleaned_data['confirm']:
                request.user.delete()
                messages.success(request, "Your account has been deleted.")
                return redirect('home')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'delete_form': delete_form,
    }
    return render(request, 'profile.html', context)

User = get_user_model()

def user_list_view(request):
    users = User.objects.all()
    return render(request, "user_list.html", {"users": users})

def logout_view(request):
    """Logs out the user and redirects to the login page."""
    logout(request)
    return redirect("login")  # Ensure "login" is the name of your login URL pattern

def dashboard_view(request):
    total_projects = Project.objects.filter(created_by=request.user).count()
    tasks_completed = Task.objects.filter(assigned_to=request.user, status='completed').count()
    tasks_pending = Task.objects.filter(assigned_to=request.user, status='pending').count()
    team_members = User.objects.filter(projects__created_by=request.user).distinct().count()
    recent_tasks = Task.objects.filter(assigned_to=request.user).order_by('-due_date')[:5]

    context = {
        'total_projects': total_projects,
        'tasks_completed': tasks_completed,
        'tasks_pending': tasks_pending,
        'team_members': team_members,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'dashboard.html', context)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("/dashboard/")
        else:
            messages.error(request, "Invalid email or password")
    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")  # Get the selected role from the form

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered")
        else:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=username)
            user.role = role  # Save the role
            user.save()
            messages.success(request, "Registration successful!")
            return redirect("/login/")
    return render(request, "register.html")
