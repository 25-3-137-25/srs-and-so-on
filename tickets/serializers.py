from rest_framework import serializers
from .models import Category, Ticket


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class TicketSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    allowed_statuses = serializers.SerializerMethodField()
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = (
            "id",
            "title",
            "description",
            "category",
            "category_name",
            "status",
            "status_label",
            "allowed_statuses",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_allowed_statuses(self, obj):
        return [
            {"value": status.value, "label": status.label}
            for status in obj.allowed_next_statuses()
        ]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Название должно содержать "
                "не менее 5 символов."
            )
        return value.strip()

    def validate(self, attrs):
        if self.instance is None:
            if attrs.get("status", Ticket.Status.NEW) != Ticket.Status.NEW:
                raise serializers.ValidationError({
                    "status": "Новая заявка должна иметь статус «Новая»."
                })
            return attrs

        old_status = self.instance.status
        new_status = attrs.get("status", old_status)

        if new_status != old_status:
            if new_status not in self.instance.allowed_next_statuses():
                raise serializers.ValidationError({
                    "status": "Недопустимый переход. Разрешено: «Новая» → «В работе» → «Выполнена»."
                })

        return attrs
