from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth.models import User, Group
from .models import Department, Course, AcademicGroup, StudentProfile
from datetime import datetime, timedelta


def get_dashboard_stats(request):
    """API endpoint для получения общей статистики"""
    days = int(request.GET.get('days', 30))
    current_period_start = datetime.now() - timedelta(days=days)
    previous_period_start = datetime.now() - timedelta(days=days * 2)

    def calc_trend(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100)

    curr_depts = Department.objects.count()
    curr_groups = AcademicGroup.objects.count()
    curr_courses = Course.objects.count()
    curr_students = StudentProfile.objects.count()

    prev_students = StudentProfile.objects.filter(
        user__date_joined__range=(previous_period_start, current_period_start)
    ).count()
    student_trend = calc_trend(curr_students, prev_students)

    registrations_qs = User.objects.filter(date_joined__gte=current_period_start)
    registrations = []
    for user in registrations_qs:
        day_str = user.date_joined.strftime('%Y-%m-%d')
        found = False
        for item in registrations:
            if item['day'] == day_str:
                item['count'] += 1
                found = True
                break
        if not found:
            registrations.append({'day': day_str, 'count': 1})
    registrations.sort(key=lambda x: x['day'])

    courses_by_dept = list(
        Course.objects.filter(department__isnull=False)
        .values('department__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    students_by_dept = list(
        StudentProfile.objects.filter(department__isnull=False)
        .values('department__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return JsonResponse({
        'stats': {
            'departments': {'value': curr_depts, 'trend': 0},
            'groups': {'value': curr_groups, 'trend': 0},
            'courses': {'value': curr_courses, 'trend': 0},
            'students': {'value': curr_students, 'trend': student_trend}
        },
        'registrations': registrations,
        'courses_by_dept': courses_by_dept,
        'students_by_dept': students_by_dept
    })


def get_academic_analytics(request):
    """Академическая аналитика"""
    group_load = list(
        AcademicGroup.objects.annotate(student_count=Count('students'))
        .filter(student_count__gt=0)
        .values('name', 'student_count')
        .order_by('-student_count')[:5]
    )
    if not group_load:
        group_load = [{'name': 'Нет данных', 'student_count': 0}]

    return JsonResponse({'group_load': group_load})


def get_user_activity(request):
    """Активность пользователей"""
    roles = list(
        Group.objects.annotate(user_count=Count('user'))
        .values('name', 'user_count')
    )
    recent_users = list(
        User.objects.order_by('-date_joined')[:10]
        .values('username', 'date_joined', 'groups__name')
    )

    return JsonResponse({
        'roles': roles,
        'recent_users': recent_users
    })