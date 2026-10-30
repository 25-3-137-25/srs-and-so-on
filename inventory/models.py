from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Equipment(models.Model):
    """Модель оборудования (справочник)."""
    CATEGORY_CHOICES = [
        ('lab', 'Лабораторное'),
        ('pc', 'Вычислительное'),
        ('measure', 'Измерительное'),
        ('tool', 'Инструмент'),
    ]

    name = models.CharField('Название', max_length=150)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES)
    inventory_number = models.CharField('Инвентарный номер', max_length=30, unique=True)
    total_stock = models.PositiveIntegerField('Общее количество', default=1)
    available_stock = models.PositiveIntegerField('Доступно для выдачи', default=1)
    location = models.CharField('Местоположение', max_length=100, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.inventory_number})'


class EquipmentRequest(models.Model):
    """Заявка на выдачу оборудования — основная сущность бизнес-процесса."""
    STATUS_CHOICES = [
        ('draft', 'Создана'),
        ('approved', 'Согласована'),
        ('issued', 'Выдана'),
        ('returned', 'Возвращена'),
        ('rejected', 'Отклонена'),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='equipment_requests',
        verbose_name='Заявитель'
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name='requests',
        verbose_name='Оборудование'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='draft')
    purpose = models.TextField('Цель использования', blank=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Заявка на оборудование'
        verbose_name_plural = 'Заявки на оборудование'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.id} — {self.equipment.name} ({self.get_status_display()})'

    # Бизнес-правила переходов
    ALLOWED_TRANSITIONS = {
        'draft': ['approved', 'rejected'],
        'approved': ['issued', 'rejected'],
        'issued': ['returned'],
        'returned': [],
        'rejected': [],
    }

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])

    def clean(self):
        if self.quantity < 1:
            raise ValidationError({'quantity': 'Количество должно быть не менее 1'})
        if self.quantity > self.equipment.available_stock and self.status == 'draft':
            raise ValidationError({'quantity': f'Доступно только {self.equipment.available_stock} ед.'})


class RequestEvent(models.Model):
    """Журнал событий по заявке — история бизнес-процесса."""
    ACTION_CHOICES = [
        ('created', 'Создана'),
        ('approved', 'Согласована'),
        ('issued', 'Выдана'),
        ('returned', 'Возвращена'),
        ('rejected', 'Отклонена'),
        ('deleted', 'Удалена'),
    ]

    request = models.ForeignKey(
        EquipmentRequest,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Заявка'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Инициатор'
    )
    action = models.CharField('Действие', max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Время', auto_now_add=True)

    class Meta:
        verbose_name = 'Событие заявки'
        verbose_name_plural = 'События заявок'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.request_id}: {self.get_action_display()} ({self.actor})'