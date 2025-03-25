# core/urls.py
from django.contrib import admin
from django.urls import path
from core.views import master_detail, thanks, test, orders_list, orders_detail


#  Эти маршруты будут доступны с префиксом /barbershop/

urlpatterns = [
    path("master/<int:master_id>/", master_detail),
    path("thanks/", thanks),
    path("orders/", orders_list),
    path("orders/<int:order_id>/", orders_detail),
]
