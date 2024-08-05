from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks_completed/', views.tasks_completed, name='tasks_completed'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    #path('task/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    #path('task/<int:task_id>/delete/', views.task_delete, name='task_delete'),

    #path('profile/', views.profile, name='profile'),
    #path('settings/', views.settings, name='settings'),
    #path('password_change/', views.password_change, name='password_change'),
]
