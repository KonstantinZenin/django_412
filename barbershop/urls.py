# barbershop\urls.py
from django.contrib import admin
from django.urls import path
from core.views import main
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main),
    # Подключаем маршруты из приложения core
    path("barbershop/", include("core.urls")),
]

#  какие ещё типы конвертеров есть?
# str: - строка без слеша /master|eleonora-arbuzova|/
# int: - целое число /master/123/
# slug: - строка с дефисами /master/eleonora-arbuzova/
# uuid: - строка с дефисами и скобками /master/123e4567-e89b-12d3-a456-426614174000/
# path: - строка с любыми символами /master/eleonora-arbuzova/


