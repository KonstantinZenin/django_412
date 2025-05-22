from django.contrib import admin
from .models import Order, Master, Service, Review

# Регистраци в одну строку
admin.site.register(Order)
admin.site.register(Service)
admin.site.register(Review)


# Создание кастомной админки для модели Master
class MasterAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "experience", "is_active")
    list_display_links = ("first_name", "last_name")
    list_filter = ("is_active", "services", "experience")
    search_fields = ("first_name", "last_name", "phone")
    ordering = ("last_name", "first_name")
    


admin.site.register(Master, MasterAdmin)
