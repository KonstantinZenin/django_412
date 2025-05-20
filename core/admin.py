from django.contrib import admin
from .models import Order, Master, Service, Review

# Регистраци в одну строку
admin.site.register(Order)
admin.site.register(Master)
admin.site.register(Service)
admin.site.register(Review)
