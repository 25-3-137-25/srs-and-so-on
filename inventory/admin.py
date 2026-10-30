from django.contrib import admin
from .models import Equipment, EquipmentRequest, RequestEvent


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'inventory_number', 'category', 'total_stock', 'available_stock')
    list_filter = ('category',)
    search_fields = ('name', 'inventory_number')


@admin.register(EquipmentRequest)
class EquipmentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'equipment', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'equipment__category')
    search_fields = ('requester__username', 'equipment__name')


@admin.register(RequestEvent)
class RequestEventAdmin(admin.ModelAdmin):
    list_display = ('request', 'actor', 'action', 'created_at')
    list_filter = ('action',)