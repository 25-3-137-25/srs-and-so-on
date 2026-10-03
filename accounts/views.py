from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from .models import Course
from .forms import (
    AcademicGroupForm,
    CourseForm,
    DepartmentForm,
)
from .forms import DepartmentForm
from .models import (
 AcademicGroup,
 Course,
 Department,
)
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Department, Course, AcademicGroup, StudentProfile


@login_required
def department_list(request):
    departments = Department.objects.all()

    return render(
        request,
        'department_list.html',
        {
            'departments': departments,
            'is_methodist': is_methodist(request.user),
        }
    )

def is_methodist(user):
  return user.groups.filter(
    name='Методист'
  ).exists()

@login_required
def profile(request):
  return render(
    request,
    'profile.html',
    {
      'is_methodist': is_methodist(
        request.user
        )
    }
  )

@login_required
def course_list(request):
    courses = Course.objects.all()

    return render(
        request,
        'course_list.html',
        {
            'courses': courses,
            'is_methodist': is_methodist(request.user),
        }
    )

@login_required
@user_passes_test(is_methodist)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Добавление курса',
            'cancel_url': reverse('course_list'),
        }
    )

@login_required
@user_passes_test(is_methodist)
def course_update(request, pk):
    course = get_object_or_404(
        Course,
        pk=pk
    )

    if request.method == 'POST':
        form = CourseForm(
            request.POST,
            instance=course
        )

        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(
            instance=course
        )

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Изменение курса',
            'cancel_url': reverse('course_list'),
        }
    )

@login_required
@user_passes_test(is_methodist)
def course_delete(request, pk):
    course = get_object_or_404(
        Course,
        pk=pk
    )

    if request.method == 'POST':
        course.delete()
        return redirect('course_list')

    return render(
        request,
        'object_confirm_delete.html',
        {
            'object': course,
            'title': 'Удаление курса',
            'cancel_url': reverse('course_list'),
            'deletion_warning': 'Это действие нельзя отменить.'
        }
    )


@login_required
@user_passes_test(is_methodist)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Добавление факультета',
            'cancel_url': reverse('department_list'),
        }
    )

@login_required
@user_passes_test(is_methodist)
def department_update(request, pk):
    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == 'POST':
        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(
            instance=department
        )

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Изменение факультета',
            'cancel_url': reverse('department_list'),
        }
    )

@login_required
@user_passes_test(is_methodist)
def department_delete(request, pk):
    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == 'POST':
        department.delete()
        return redirect('department_list')

    return render(
        request,
        'object_confirm_delete.html',
        {
            'object': department,
            'title': 'Удаление факультета',
            'cancel_url': reverse('department_list'),
            'deletion_warning': 'Связанные курсы и группы также будут удалены.'
        }
    )

@login_required
def academic_group_list(request):
    groups = AcademicGroup.objects.all()

    return render(
        request,
        'academic_group_list.html',
        {
            'groups': groups,
            'is_methodist': is_methodist(request.user),
        }
    )

@login_required
@user_passes_test(is_methodist)
def academic_group_create(request):
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm()

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Добавление учебной группы',
            'cancel_url': reverse('academic_group_list'),
        }
    )

@login_required
@user_passes_test(is_methodist)
def academic_group_update(request, pk):
    group = get_object_or_404(
        AcademicGroup,
        pk=pk
    )

    if request.method == 'POST':
        form = AcademicGroupForm(
            request.POST,
            instance=group
        )

        if form.is_valid():
            form.save()
            return redirect('academic_group_list')
    else:
        form = AcademicGroupForm(
            instance=group
        )

    return render(
        request,
        'object_form.html',
        {
            'form': form,
            'title': 'Изменение учебной группы',
            'cancel_url': reverse('academic_group_list'),
        }
    )

@login_required
@user_passes_test(is_methodist)
def academic_group_delete(request, pk):
    group = get_object_or_404(
        AcademicGroup,
        pk=pk
    )

    if request.method == 'POST':
        group.delete()
        return redirect('academic_group_list')

    return render(
        request,
        'object_confirm_delete.html',
        {
            'object': group,
            'title': 'Удаление учебной группы',
            'cancel_url': reverse('academic_group_list'),
            'deletion_warning': 'Это действие нельзя отменить.'
        }
    )



@login_required
@user_passes_test(is_methodist)
def dashboard_view(request):
    return render(request, 'dashboard/index.html')


@login_required
@user_passes_test(is_methodist)
def dashboard_api(request):
    
    total_students = StudentProfile.objects.count()
    total_departments = Department.objects.count()
    total_groups = AcademicGroup.objects.count()
    total_courses = Course.objects.count()

    
    dept_stats = Department.objects.annotate(
        student_count=Count('students', distinct=True)
    ).values('name', 'student_count').order_by('-student_count')

   
    course_stats = Course.objects.annotate(
        student_count=Count('students', distinct=True)
    ).order_by('-student_count')[:5].values('title', 'student_count')

    
    faculty_load = Department.objects.annotate(
        student_count=Count('students', distinct=True),
        course_count=Count('courses', distinct=True)
    ).values('name', 'student_count', 'course_count').order_by('-student_count')

   
    students_by_courses = {}
    for profile in StudentProfile.objects.annotate(courses_count=Count('courses')):
        cnt = profile.courses_count
        bucket = '5+' if cnt >= 5 else str(cnt)
        students_by_courses[bucket] = students_by_courses.get(bucket, 0) + 1
    sorted_buckets = sorted(students_by_courses.keys(), key=lambda x: (len(x), x))
    courses_distribution = [
        {'bucket': b, 'count': students_by_courses[b]} for b in sorted_buckets
    ]

    
    top_groups = AcademicGroup.objects.annotate(
        student_count=Count('students', distinct=True)
    ).order_by('-student_count')[:10].values('name', 'student_count')

    return JsonResponse({
        'summary': {
            'students': total_students,
            'departments': total_departments,
            'groups': total_groups,
            'courses': total_courses,
        },
        'department_distribution': list(dept_stats),
        'top_courses': list(course_stats),
        'faculty_load': list(faculty_load),
        'courses_distribution': courses_distribution,
        'top_groups': list(top_groups),
    })