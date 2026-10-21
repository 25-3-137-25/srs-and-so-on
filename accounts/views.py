from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .models import Department, Course, AcademicGroup, StudentProfile
from .forms import DepartmentForm, CourseForm, AcademicGroupForm
from django.db.models import Count
from django.http import JsonResponse
from datetime import datetime, timedelta


# === ГЛАВНАЯ СТРАНИЦА ===

def home_view(request):
    """Главная страница"""
    is_methodist = False
    if request.user.is_authenticated:
        is_methodist = request.user.groups.filter(name='Методист').exists()
    return render(request, 'home.html', {'is_methodist': is_methodist})


# === ПРОФИЛЬ ===

@login_required
def profile(request):
    """Профиль пользователя"""
    return render(request, 'profile.html')


# === КУРСЫ (Студенческий просмотр) ===

def course_list(request):
    """Список курсов для студентов"""
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})


# === CRUD ФАКУЛЬТЕТОВ ===

@login_required
def department_list(request):
    """Список факультетов"""
    departments = Department.objects.all()
    return render(request, 'department_list.html', {'departments': departments})


@login_required
def department_create(request):
    """Создание факультета"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Факультет успешно создан!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'department_form.html', {'form': form})


@login_required
def department_update(request, pk):
    """Редактирование факультета"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Факультет успешно обновлён!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'department_form.html', {'form': form})


@login_required
def department_delete(request, pk):
    """Удаление факультета"""
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Факультет успешно удалён!')
        return redirect('department_list')
    return render(request, 'object_confirm_delete.html', {'object': department})


# === CRUD УЧЕБНЫХ ГРУПП ===

@login_required
def academic_group_list(request):
    """Список учебных групп"""
    groups = AcademicGroup.objects.all()
    return render(request, 'academic_group_list.html', {'groups': groups})


@login_required
def academic_group_create(request):
    """Создание учебной группы"""
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа успешно создана!')
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm()
    return render(request, 'academic_group_form.html', {'form': form})


@login_required
def academic_group_update(request, pk):
    """Редактирование учебной группы"""
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа успешно обновлена!')
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm(instance=group)
    return render(request, 'academic_group_form.html', {'form': form})


@login_required
def academic_group_delete(request, pk):
    """Удаление учебной группы"""
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Группа успешно удалена!')
        return redirect('academic_group_list')
    return render(request, 'object_confirm_delete.html', {'object': group})


# === CRUD КУРСОВ (Методист) ===

@login_required
def course_create(request):
    """Создание курса"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс успешно создан!')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form})


@login_required
def course_update(request, pk):
    """Редактирование курса"""
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс успешно обновлён!')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form})


@login_required
def course_delete(request, pk):
    """Удаление курса"""
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Курс успешно удалён!')
        return redirect('course_list')
    return render(request, 'object_confirm_delete.html', {'object': course})


# === ДАШБОРДЫ ===

def dashboard_hub(request):
    """Главная страница дашбордов — хаб с карточками"""
    is_methodist = False
    if request.user.is_authenticated:
        is_methodist = request.user.groups.filter(name='Методист').exists()
    return render(request, 'includes/dashboard/dashboard.html', {'is_methodist': is_methodist})


def dashboard_overview(request):
    """Дашборд 1: Обзор системы"""
    is_methodist = False
    if request.user.is_authenticated:
        is_methodist = request.user.groups.filter(name='Методист').exists()
    return render(request, 'includes/dashboard/overview.html', {'is_methodist': is_methodist})


def dashboard_academic(request):
    """Дашборд 2: Академическая аналитика"""
    is_methodist = False
    if request.user.is_authenticated:
        is_methodist = request.user.groups.filter(name='Методист').exists()
    return render(request, 'includes/dashboard/academic.html', {'is_methodist': is_methodist})


def dashboard_activity(request):
    """Дашборд 3: Активность пользователей"""
    is_methodist = False
    if request.user.is_authenticated:
        is_methodist = request.user.groups.filter(name='Методист').exists()
    return render(request, 'includes/dashboard/activity.html', {'is_methodist': is_methodist})