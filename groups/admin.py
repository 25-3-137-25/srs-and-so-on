# Register your models here.
from django.contrib import admin
from .models import Faculty, StudyGroup

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("name", "code")

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "faculty", "status", "students_count", "curator", "created_at")
    list_filter = ("status", "faculty")
    search_fields = ("name",)