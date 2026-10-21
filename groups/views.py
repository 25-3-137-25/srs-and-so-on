from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Faculty, StudyGroup
from .serializers import FacultySerializer, StudyGroupSerializer


@login_required(login_url="/admin/login/")
@ensure_csrf_cookie
def groups_dashboard(request):
    """Главная страница управления группами"""
    return render(request, "groups/dashboard.html")


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение — справочник факультетов"""
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]


class StudyGroupViewSet(viewsets.ModelViewSet):
    """Полный CRUD для учебных групп"""
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StudyGroup.objects.select_related("faculty", "curator").all()

        faculty_id = self.request.query_params.get("faculty")
        if faculty_id:
            queryset = queryset.filter(faculty_id=faculty_id)

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")