from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .models import User, Task, Project, Notification, SubTask
from .forms import TaskForm, ProjectForm

import datetime

# Create your views here.

class IndexView(View):
    title = 'Welcome'

    def get(self, request):

        context = {
            'title': self.title,
        }
        # return HttpResponse("Home Page")
        return render(request, 'landing.html', context)

    def post(self, request):
        context = {
            'title': self.title,
        }
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('allocator:dashboard')
            else:
                context['message'] = 'Invalid Credentials, try again!'
            return render(request, 'landing.html', context)

        if 'register' in request.POST:
            username = request.POST['email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']

            # check if user exist
            try:

                user_exist = User.objects.get(username=username)
                if user_exist:
                    context['message'] = 'Username already taken'
                    return render(request, 'landing.html', context)
            except:
                new_user = User(
                    username = username,
                    email = username,
                    first_name = first_name,
                    last_name = last_name,
                )
                if 'manager' in request.POST:
                    new_user.is_manager = True
                    new_user.is_staff = True
                else:
                    new_user.is_employee = True
                new_user.set_password(password)

                new_user.save()

                user = authenticate(request, username=username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect('allocator:dashboard')
            return HttpResponse('unsuccessful')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('allocator:landing'))


class DashboardView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        title = 'Dashboard'
        tasks = Task.objects.all()
        users = User.objects.all() # employees
        notifications = Notification.objects.filter(user_id=request.user.id)

        context = {
            'title': title,
            'segment': ['dashboard'],
        }
        if request.user.is_employee:
            user_tasks = tasks.filter(user=request.user)
            
            completed = 0
            for t in user_tasks:
                if t.status == 'completed':
                    completed += 1

            context['tasks'] = user_tasks[:5]
            context['task_count'] = user_tasks.count()
            context['completed_tasks'] = completed #status='completed'
            context['outstanding_tasks'] = user_tasks.count() - completed #status='inprogress'
            context['notifications'] = notifications

            return render(request, 'employee_dashboard.html', context)
        else:
            outstanding = 0
            for t in tasks:
                if t.status == 'inprogress':
                    outstanding += 1
            employees = users.filter(is_employee=True)
            if request.user.is_manager:
                context['users'] = employees
                context['user_count'] = employees.count()
            else:
                context['users'] = users
                context['user_count'] = users.count()
            context['tasks'] = tasks[:5]
            context['outstanding'] = outstanding
            context['project_count'] = Project.objects.all().count()

            return render(request, 'staff_dashboard.html', context)

    def post(self, request):
        return HttpResponse("Dashboard: post")

class AllNotificationsView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        if not request.user.is_employee:
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        title = 'Dashboard'
        notifications = Notification.objects.filter(user=request.user)
        context = {
            'title': title,
            'segment': ['dashboard'],
            'notifications': notifications,
            'back': True
        }
        return render(request, 'all_notifications.html', context)


class NotificationView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, id):
        if not request.user.is_employee:
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        title = 'Dashboard'
        notification = Notification.objects.get(pk=id)
        context = {
            'title': title,
            'segment': ['dashboard'],
            'notification': notification,
            'notifications': Notification.objects.filter(user=request.user),
            'back': True
        }
        return render(request, 'notification.html', context)

class DeleteNotificationView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, id):
        notification = Notification.objects.get(id=id)
        if notification != None:
            notification.delete()
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        else:
            return HttpResponseRedirect(reverse('allocator:notification', args=(id,)))
    
class EmployeeTasksView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        if not request.user.is_employee:
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        title = 'My Tasks'
        tasks = Task.objects.all().filter(user=request.user)

        context = {
            'title': title,
            'tasks': tasks,
            'segment': ['tasks'],
            'back': True
        }
        return render(request, 'employee_tasks.html', context)

class AllProjectsView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        if request.user.is_employee:
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        title = 'All Projects'
        projects = Project.objects.all()
        form = ProjectForm(request.POST or None)

        context = {
            'title': title,
            'projects': projects,
            'segment': ['projects'],
            'project_form': form,
            'back': True
        }
        return render(request, 'all_projects.html', context)

    def post(self, request):
        if request.user.is_employee:
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        title = 'All Projects'
        projects = Project.objects.all()
        form = ProjectForm(request.POST or None)
        if form.is_valid():
            
            new_project = Project(
                name=form.cleaned_data.get("name"),
                description=form.cleaned_data.get("description"),
                end = form.cleaned_data.get("end"),
            )
            new_project.save()
            msg = 'project creation successful'

        else:
            msg = 'Error validating the form'

        context = {
            'title': title,
            'projects': projects,
            'segment': ['projects'],
            'project_form': form,
            'back': True
        }
        return render(request, 'all_projects.html', context)


class ProjectView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, id):
        title = 'Project'
        project = Project.objects.get(id=id)
        tasks = Task.objects.filter(project_id=id)
        form = TaskForm(request.POST or None)

        context = {
            'title': title,
            'project': project,
            'tasks': tasks,
            'segment': ['projects'],
            'task_form': form,
            'back': True
        }
        return render(request, 'project.html', context)

    def post(self, request, id):
        title = 'All Tasks'
        tasks = Task.objects.all()
        project = Project.objects.get(id=id)
        users = User.objects.all() # employees
        project_count = Project.objects.all().count()
        form = TaskForm(request.POST or None)
        if form.is_valid():
            
            new_task = Task(
                description=form.cleaned_data.get("description"),
                project_id=id,
                user = form.cleaned_data.get("user"),
                end = form.cleaned_data.get("end")
            )
            new_task.save()
            subs = form.cleaned_data.get("sub_tasks").split(",")
            if len(subs) == 0:
                SubTask.objects.create(
                    description=form.cleaned_data.get("description"),
                    task_id = new_task.id
                )
            else:
                for sub in subs:
                    SubTask.objects.create(
                        description=sub.strip(),
                        task_id = new_task.id
                    )
            msg = 'task creation successful'

        else:
            msg = 'Error validating the form'

        context = {
            'title': title,
            'project': project,
            'tasks': tasks,
            'segment': ['projects'],
            'task_form': form,
            'msg': msg,
            'back': True
        }
        return render(request, 'project.html', context)


class EditProjectView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, id):
        title = 'Edit Project'
        project = Project.objects.get(id=id)

        context = {
            'title': title,
            'project': project,
            'segment': ['projects'],
            'back': True
        }
        return render(request, 'edit_project.html', context)

    def post(self, request, id):
        project = Project.objects.get(id=id)

        project.name = request.POST['name']
        project.description = request.POST['description']

        project.save()

        return HttpResponseRedirect(reverse('allocator:project', args=(id,)))


class DeleteProjectView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, id):
        project = Project.objects.get(id=id)
        if project != None:
            project.delete()
            return HttpResponseRedirect(reverse('allocator:all_projects'))
        else:
            return HttpResponseRedirect(reverse('allocator:project', args=(id,)))




class TaskView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, id):
        title = 'Tasks'
        task = Task.objects.get(id=id)
        subs = SubTask.objects.filter(task_id=id)

        context = {
            'title': title,
            'task': task,
            'subtasks': subs,
            'segment': ['tasks', 'one-task'],
            'back': True
        }
        return render(request, 'task.html', context)
    def post(self, request, id):
        return HttpResponse("Task: post")


class DeleteTaskView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, id):
        task = Task.objects.get(id=id)
        project_id = task.project.pk
        if task != None:
            task.delete()
            return HttpResponseRedirect(reverse('allocator:project', args=(project_id,)))
        else:
            return HttpResponseRedirect(reverse('allocator:task', args=(id,)))

class CompleteSubTaskView(View):
    login_url = '/'

    def get(self, request, taskid, subid):
        sub = SubTask.objects.get(id=subid)

        if sub != None:
            sub.is_completed = True
            sub.save()
        return HttpResponseRedirect(reverse('allocator:task', args=(taskid,)))


class AllUserView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):
        if request.user.is_employee:
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        title = 'All Users'
        if request.user.is_manager:
            users = User.objects.filter(is_employee=True)
        else:
            users = User.objects.all()
        context = {
            'title': title,
            'users': users,
            'segment': ['employees', 'users'],
            'back': True
        }
        return render(request, 'users.html', context)

