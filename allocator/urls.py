from django.urls import path
from .views import (
    IndexView,
    logout_view,
    DashboardView,
    AllTaskView,
    TaskView,
    DeleteTaskView,
    CompleteSubTaskView,
    NotificationView,
    AllNotificationsView,
    DeleteNotificationView,
    EmployeeTasksView
)

app_name = 'allocator'

urlpatterns = [
    path('', IndexView.as_view(), name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('tasks/', EmployeeTasksView.as_view(), name='employee_tasks'),
    path('alltasks/', AllTaskView.as_view(), name='tasks'),
    path('tasks/<int:id>/', TaskView.as_view(), name='task'),
    path('tasks/<int:id>/delete', DeleteTaskView.as_view(), name='delete_task'),
    path('tasks/<int:taskid>/<int:subid>', CompleteSubTaskView.as_view(), name='complete_task'),
    path('notifications/', AllNotificationsView.as_view(), name='all_notifications'),
    path('notifications/<int:id>/', NotificationView.as_view(), name='notification'),
    path('notifications/<int:id>/delete', DeleteNotificationView.as_view(), name='delete_notification'),
]
