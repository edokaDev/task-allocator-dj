from django.contrib import admin
from .models import User, Project, Task, SubTask, Notification

# Register your models here.

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(Notification)
