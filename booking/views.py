from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ReservationForm
from .models import Reservation


@login_required
def reservation_list(request):
    # Шаг 9, Задание 2: Фильтрация по оборудованию
    items = Reservation.objects.filter(user=request.user).select_related("equipment").order_by("start")
    equipment_id = request.GET.get('equipment_id')
    if equipment_id:
        items = items.filter(equipment_id=equipment_id)
    return render(request, "booking/list.html", {"items": items})


@login_required
def reservation_create(request):
    form = ReservationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect("reservation_list")
    return render(request, "booking/form.html", {"form": form})


@login_required
def reservation_edit(request, pk):
    # Шаг 9, Задание 4: Защита от изменения чужой брони (вернет 404)
    item = get_object_or_404(Reservation, pk=pk, user=request.user)
    form = ReservationForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("reservation_list")
    return render(request, "booking/form.html", {"form": form})


@login_required
@require_POST
def reservation_delete(request, pk):
    item = get_object_or_404(Reservation, pk=pk, user=request.user)
    item.delete()
    return redirect("reservation_list")


@login_required
@require_POST
def reservation_cancel(request, pk):
    # Шаг 9, Задание 1: Мягкая отмена
    item = get_object_or_404(Reservation, pk=pk, user=request.user)
    item.is_cancelled = True
    item.save()
    return redirect("reservation_list")