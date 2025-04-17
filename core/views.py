from tabnanny import check
from warnings import filters
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order
from django.db.models import Q

masters = [
    {"id": 1, "name": "Эльдар 'Бритва' Рязанов"},
    {"id": 2, "name": "Зоя 'Ножницы' Космодемьянская"},
    {"id": 3, "name": "Борис 'Фен' Пастернак"},
    {"id": 4, "name": "Иннокентий 'Лак' Смоктуновский"},
    {"id": 5, "name": "Раиса 'Бигуди' Горбачёва"},
]


def landing(request):
    context = {
        "title": "Главная - Барбершоп Арбуз",
        "services": services, # Из data.py
        "masters": masters,   # Из data.py
        "years_on_market": 50
    }
    return render(request, "core/landing.html", context)


def master_detail(request, master_id):
    try:
        master = [m for m in masters if m["id"] == master_id][0]
    except IndexError:
        return HttpResponse(f"Мастер не найден")
    return HttpResponse(f"<h1>{master['name']}</h1>")


def thanks(request):
    masters_count = len(masters)

    context = {
        "masters_count": masters_count,
    }

    return render(request, "core/thanks.html", context)


@login_required
def orders_list(request,):
    if request.method == "GET":
        # Получаем все заказы
        # используем жадную загрузку для мастеров и услуг
        all_orders = (
            Order.objects.select_related("master").prefetch_related("services").all()
        )

        # Получаем строку поиска
        search_query = request.GET.get("search", None)
        
        if search_query:
            # Получаем чекбоксы
            check_boxes = request.GET.getlist("search_in")

            # Проверяем чекбоксы и добавляем Q объекты в запрос
            #  |= это оператор "или" для Q объектов
            filters = Q()

            if "phone" in check_boxes:
                filters |= Q(phone__icontains=search_query)

            if "name" in check_boxes:
                filters |= Q(client_name__icontains=search_query)

            if "comment" in check_boxes:
                filters |= Q(comment__icontains=search_query)

            if filters:
                all_orders = all_orders.filter(filters)

        # отправлем все заказы в контекст
        context = {
            "title": "Заказы",
            "orders": all_orders,
        }
        return render(request, "core/orders_list.html", context)


@login_required
def order_detail(request, order_id: int):

    order = orders = get_object_or_404(Order, id=order_id)


    context = {
        "title": f"Заказ № {order_id}",
        "order": order,
    }

    return render(request, "core/order_detail.html", context)
