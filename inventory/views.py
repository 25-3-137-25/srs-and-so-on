from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Equipment, EquipmentRequest, RequestEvent
from .serializers import (
    EquipmentSerializer,
    EquipmentRequestSerializer,
    StatusTransitionSerializer,
    RequestEventSerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Владелец может менять/удалять свою заявку, остальные — только читать."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.requester == request.user


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Справочник оборудования — только чтение."""
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class EquipmentRequestViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD заявок + бизнес-действия.
    Пользователь видит только свои заявки (кроме администратора).
    """
    serializer_class = EquipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = EquipmentRequest.objects.select_related('equipment', 'requester')
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(requester=user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        category_filter = self.request.query_params.get('category')
        if category_filter:
            qs = qs.filter(equipment__category=category_filter)
        return qs

    def perform_create(self, serializer):
        """Создание заявки + резервирование количества — атомарно."""
        equipment = serializer.validated_data['equipment']
        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            eq = Equipment.objects.select_for_update().get(pk=equipment.pk)
            if eq.available_stock < quantity:
                raise ValidationError(
                    {'quantity': f'Недостаточно: доступно {eq.available_stock} ед.'}
                )
            eq.available_stock = F('available_stock') - quantity
            eq.save(update_fields=['available_stock'])

            request_obj = serializer.save(requester=self.request.user)

            RequestEvent.objects.create(
                request=request_obj,
                actor=self.request.user,
                action='created',
                comment='Заявка создана'
            )

    def perform_destroy(self, instance):
        """Удаление заявки с возвратом зарезервированного количества."""
        with transaction.atomic():
            if instance.status == 'draft':
                eq = Equipment.objects.select_for_update().get(pk=instance.equipment_id)
                eq.available_stock = F('available_stock') + instance.quantity
                eq.save(update_fields=['available_stock'])

            RequestEvent.objects.create(
                request=instance,
                actor=self.request.user,
                action='deleted',
                comment='Заявка удалена'
            )
            instance.delete()

    @action(detail=True, methods=['post'], url_path='transition')
    def transition(self, request, pk=None):
        """Смена статуса заявки с проверкой бизнес-правил."""
        instance = self.get_object()
        serializer = StatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['new_status']
        comment = serializer.validated_data.get('comment', '')

        if not instance.can_transition_to(new_status):
            return Response(
                {'detail': f'Переход {instance.status} → {new_status} запрещён.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                eq = Equipment.objects.select_for_update().get(pk=instance.equipment_id)

                if new_status == 'returned':
                    eq.available_stock = F('available_stock') + instance.quantity
                    eq.save(update_fields=['available_stock'])
                elif new_status == 'rejected' and instance.status == 'draft':
                    eq.available_stock = F('available_stock') + instance.quantity
                    eq.save(update_fields=['available_stock'])

                instance.status = new_status
                instance.save(update_fields=['status', 'updated_at'])

                RequestEvent.objects.create(
                    request=instance,
                    actor=request.user,
                    action=new_status,
                    comment=comment
                )

            return Response(EquipmentRequestSerializer(instance).data)

        except Exception as e:
            return Response(
                {'detail': f'Ошибка операции: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        instance = self.get_object()
        events = instance.events.all()
        return Response(RequestEventSerializer(events, many=True).data)