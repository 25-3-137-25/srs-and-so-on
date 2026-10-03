from django import forms
from .models import (
 AcademicGroup,
 Course,
 Department,
)
class DepartmentForm(forms.ModelForm):
    class Meta:
        labels = {"name": "Название факультета"}
        model = Department
        fields = [
            'name',
            ]
        widgets = {
           'name': forms.TextInput(
              attrs={
                 'class': 'form-control'
                 }
            ),
        }
class AcademicGroupForm(forms.ModelForm):
   class Meta:
      labels = {"name": "Название группы", "department": "Факультет"}
      model = AcademicGroup
      fields = [
          'name',
          'department',
          ]
      widgets = {
            'name': forms.TextInput(
                attrs={
                'class': 'form-control'
                }
            ),
            'department': forms.Select(
               attrs={
                'class': 'form-select'
                }
            ),
        }
class CourseForm(forms.ModelForm):
   class Meta:
      labels = {"title": "Название курса", "description": "Описание", "department": "Факультет"}
      model = Course
      fields = [
         'title',
         'description',
         'department',
         ]
      widgets = {
         'title': forms.TextInput(
            attrs={
               'class': 'form-control'
               }
            ),
         'description': forms.Textarea(
            attrs={
               'class': 'form-control',
               'rows': 4,
               }
            ),
         'department': forms.Select(
            attrs={
               'class': 'form-select'
               }
            ),
         }