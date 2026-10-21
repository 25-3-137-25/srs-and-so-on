# Create your models here.
from django.db import models
from django.conf import settings

class Faculty(models.Model):
    """Справочник факультетов"""
    name = models.CharField(max_length=150, unique=True, verbose_name="Название факультета")
    code = models.CharField(max_length=20, unique=True, verbose_name="Код факультета")
    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"
        ordering = ["name"]
    def __str__(self):
        return f"{self.code} — {self.name}"


class StudyGroup(models.Model):
    """Учебная группа со статусами"""
    class Status(models.TextChoices):
        RECRUITING = "recruiting", "Набор открыт"
        STUDYING = "studying", "Обучение"
        GRADUATED = "graduated", "Выпущена"
    name = models.CharField(max_length=50, verbose_name="Номер группы")
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name="groups",
        verbose_name="Факультет"
    )
    curator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curated_groups",
        verbose_name="Куратор"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECRUITING,
        verbose_name="Статус"
    )
    students_count = models.PositiveIntegerField(default=0, verbose_name="Количество студентов")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"