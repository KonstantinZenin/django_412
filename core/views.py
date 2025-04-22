from re import M
from tabnanny import check
from warnings import filters
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Order, Master
from django.db.models import Q, F
from .data import *

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
    # Получаем мастера по id
    master = get_object_or_404(Master, id=master_id)

    # Проверем просматривал ли пользователь этого мастера ранее
    viewed_masters = request.session.get("viewed_masters", [])

    if master_id not in viewed_masters:

        # Увеличиваем счётчик просмотров мастера
        # F - это специальный объект, который позволяет ссылаться на поля модели

        Master.objects.filter(id=master_id).update(view_count=F("view_count") + 1)

        # Добавлем мастера в список просмотренных
        viewed_masters.append(master_id)
        request.session["viewed_masters"] = viewed_masters

        # Обновляем объект после изменения в БД
        master.refresh_from_db()

    # Получаем свзязанные услуги мастера
    services = master.services.all()

    context={
        "title": f"Мастер {master.first_name} {master.last_name}",
        "master": master,
        "services": services,
    }

    return render(request, "core/master_detail.html", context)



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
