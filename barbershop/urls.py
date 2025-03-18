from django.contrib import admin
from django.urls import path
from core.views import main, master_detail, thanks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main),
    path("master/<int:master_id>/", master_detail),
    path("thanks/", thanks),
]
