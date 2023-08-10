from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .models import User, Task, Project, Notification, SubTask
from .forms import TaskForm


# Create your views here.

class IndexView(View):
    def get(self, request):
        title = 'Welcome'

        context = {
            'title': title,
        }
        # return HttpResponse("Home Page")
        return render(request, 'landing.html', context)

    def post(self, request):
        if 'login' in request.POST:
            context = {}
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'dashboard.html', context)
            else:
                context['login_error'] = 'Invalid Credentials, try again!'
            return render(request, 'landing.html', context)

        if 'register' in request.POST:
            username = request.POST['email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']

            new_user = User(
                username = username,
                email = username,
                first_name = first_name,
                last_name = last_name,
            )
            if 'manager' in request.POST:
                new_user.is_manager = True
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


class DashboardView(View, LoginRequiredMixin):
    login_url = '/'

    def get(self, request):
        title = 'Dashboard'
        tasks = Task.objects.all()
        users = User.objects.all() # employees
        project_count = Project.objects.all().count()
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
        return render(request, 'dashboard.html', context)

    def post(self, request):
        return HttpResponse("Dashboard: post")

class AllNotificationsView(View, LoginRequiredMixin):
    login_url = '/'

    def get(self, request):
        if not request.user.is_employee:
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        title = 'Dashboard'
        notifications = Notification.objects.filter(user=request.user)
        context = {
            'title': title,
            'segment': ['dashboard'],
            'notifications': notifications
        }
        return render(request, 'all_notifications.html', context)


class NotificationView(View, LoginRequiredMixin):
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
            'notifications': Notification.objects.filter(user=request.user)
        }
        return render(request, 'notification.html', context)

class DeleteNotificationView(View, LoginRequiredMixin):
    login_url = '/'

    def get(self, request, id):
        notification = Notification.objects.get(id=id)
        if notification != None:
            notification.delete()
            return HttpResponseRedirect(reverse('allocator:dashboard'))
        else:
            return HttpResponseRedirect(reverse('allocator:notification', args=(id,)))
    
class EmployeeTasksView(View, LoginRequiredMixin):
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
        }
        return render(request, 'employee_tasks.html', context)


class AllTaskView(View, LoginRequiredMixin):
    login_url = '/'

    def get(self, request):
        title = 'All Tasks'
        tasks = Task.objects.all()
        users = User.objects.all() # employees
        project_count = Project.objects.all().count()
        form = TaskForm(request.POST or None)

        context = {
            'title': title,
            'tasks': tasks,
            't_count': tasks.count(),
            'users': users,
            'u_count': users.count(),
            'projects': project_count,
            'segment': ['tasks', 'all-task'],
            'form': form
        }
        return render(request, 'all_tasks.html', context)

    def post(self, request):
        title = 'All Tasks'
        tasks = Task.objects.all()
        users = User.objects.all() # employees
        project_count = Project.objects.all().count()
        form = TaskForm(request.POST or None)
        if form.is_valid():
            
            new_task = Task(
                description=form.cleaned_data.get("description"),
                project=form.cleaned_data.get("project"),
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
            'tasks': tasks,
            't_count': tasks.count(),
            'users': users,
            'u_count': users.count(),
            'projects': project_count,
            'segment': ['tasks', 'all-task'],
            'form': form,
            'msg': msg
        }
        return render(request, 'all_tasks.html', context)


class TaskView(View, LoginRequiredMixin):
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
        }
        return render(request, 'task.html', context)
    def post(self, request, id):
        return HttpResponse("Task: post")


class DeleteTaskView(View, LoginRequiredMixin):
    login_url = '/'

    def get(self, request, id):
        task = Task.objects.get(id=id)
        if task != None:
            task.delete()
            return HttpResponseRedirect(reverse('allocator:tasks'))
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
