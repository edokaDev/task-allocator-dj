from django.db import models
from django.contrib.auth.models import AbstractUser, User


# Create your models here.


class User(AbstractUser):
    is_manager = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name
    
    @property
    def pending_tasks(self):
        tasks = Task.objects.filter(user_id=self.pk)
        return tasks.count()


class Project(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=40)
    start = models.DateField(auto_now_add=True)
    end = models.DateField()
    status = models.CharField(default='in-progress', max_length=30)

    def __str__(self):
        return self.name


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=128)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

    @property
    def progress(self):
        subs = SubTask.objects.filter(task_id=self.id)
        completed = subs.filter(is_completed=True)

        if subs.count() == 0:
            return 0
        return 100 * completed.count() // subs.count()
    
    @property
    def progress_class(self):
        if self.progress < 40:
            return 'danger'
        elif self.progress < 70:
            return 'warning'
        return 'success'

    @property
    def status(self):
        if self.progress < 100:
            return 'inprogress'
        return 'completed'


class SubTask(models.Model):
    description = models.CharField(max_length=128)
    is_completed = models.BooleanField(default=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

class Notification(models.Model):
    title = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

