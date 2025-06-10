# core/urls.py
from django.contrib import admin
from django.urls import path
from .views import (
    master_detail,
    ThanksView,
    service_create,
    service_update,
    masters_services_by_id,
    order_create,
    GreetingView,
    ServiceDetailView,
    OrderDetailView,
    ServicesListView,
    OrdersListView,
    ServiceCreateView,
)


#  Эти маршруты будут доступны с префиксом /barbershop/

urlpatterns = [
    path("master/<int:master_id>/", master_detail, name="master_detail"),
    path("thanks/", ThanksView.as_view(), name="thanks"),
    path("thanks/<str:source>/", ThanksView.as_view(), name="thanks_with_source"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order_detail"),
    path("services/", ServicesListView.as_view(), name="services_list"),
    path("service/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
    path('service_create/<str:form_mode>/', ServiceCreateView.as_view(), name='service_create'),
    path('service_update/<int:service_id>/', service_update, name='service_update'),
    path("masters_services/", masters_services_by_id, name="masters_services_by_id_ajax"),
    path('order_create/', order_create, name="order_create"),
    path("greeting/", GreetingView.as_view(), name="greeting"),
]
