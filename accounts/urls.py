from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # 1. ГЛАВНАЯ СТРАНИЦА
    path('', views.home_view, name='home'),

    # 2. ПРОФИЛЬ
    path('profile/', views.profile, name='profile'),

    # 3. КУРСЫ
    path('courses/', views.course_list, name='course_list'),

    # 4. ФАКУЛЬТЕТЫ
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department_update'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # 5. ГРУППЫ
    path('groups/', views.academic_group_list, name='academic_group_list'),
    path('groups/add/', views.academic_group_create, name='academic_group_create'),
    path('groups/<int:pk>/edit/', views.academic_group_update, name='academic_group_update'),
    path('groups/<int:pk>/delete/', views.academic_group_delete, name='academic_group_delete'),

    # 6. КУРСЫ CRUD
    path('courses/add/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),

    # 7. API ДАШБОРДОВ
    path('api/dashboard/stats/', api_views.get_dashboard_stats, name='api_dashboard_stats'),
    path('api/dashboard/academic/', api_views.get_academic_analytics, name='api_academic_analytics'),
    path('api/dashboard/activity/', api_views.get_user_activity, name='api_user_activity'),

    # 8. ДАШБОРДЫ
    path('dashboard/', views.dashboard_hub, name='dashboard'),
    path('dashboard/overview/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/academic/', views.dashboard_academic, name='dashboard_academic'),
    path('dashboard/activity/', views.dashboard_activity, name='dashboard_activity'),
]