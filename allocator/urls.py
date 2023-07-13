from django.urls import path
from .views import IndexView, logout_view, DashboardView, AllTaskView, TaskView, DeleteTaskView, CompleteSubTaskView

app_name = 'allocator'

urlpatterns = [
    path('', IndexView.as_view(), name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('tasks/', AllTaskView.as_view(), name='tasks'),
    path('tasks/<int:id>/', TaskView.as_view(), name='task'),
    path('tasks/<int:id>/delete', DeleteTaskView.as_view(), name='delete_task'),
    path('tasks/<int:taskid>/<int:subid>', CompleteSubTaskView.as_view(), name='complete_task'),
]