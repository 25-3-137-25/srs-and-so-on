from rest_framework import serializers
from .models import Equipment, EquipmentRequest, RequestEvent


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'category', 'inventory_number',
            'total_stock', 'available_stock', 'location', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'available_stock']


class RequestEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = RequestEvent
        fields = ['id', 'actor_name', 'action', 'action_display', 'comment', 'created_at']
        read_only_fields = fields


class EquipmentRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.username', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    events = RequestEventSerializer(many=True, read_only=True)

    class Meta:
        model = EquipmentRequest
        fields = [
            'id', 'requester', 'requester_name', 'equipment', 'equipment_name',
            'quantity', 'status', 'status_display', 'purpose',
            'created_at', 'updated_at', 'events'
        ]
        read_only_fields = ['id', 'requester', 'status', 'created_at', 'updated_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Количество должно быть не менее 1')
        return value

    def validate(self, attrs):
        equipment = attrs.get('equipment')
        quantity = attrs.get('quantity', 1)
        if equipment and quantity > equipment.available_stock:
            raise serializers.ValidationError(
                {'quantity': f'Доступно только {equipment.available_stock} ед.'}
            )
        return attrs


class StatusTransitionSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(
        choices=['approved', 'issued', 'returned', 'rejected']
    )
    comment = serializers.CharField(required=False, allow_blank=True)