from django.db import models
"""
CharField - строковое поле, которое может хранить текестовые данные.
TextField - текстовое поле, которое может хранить большие объемы текстовых данных.
IntegerField - целочисленное поле, которое может хранить целые числа.
DateField - поле для хранения дат.
BooleanField - логическое поле, которое может хранить значения True или False.
JsonField - поле для хранения данных в формате JSON.
"""

class Order(models.Model):

    # Статусы заказов
    STATUS_CHOISES = [
        ("not_approved", "Не подтвержден"),
        ("moderated", "Прошёл модерацию"),
        ("spam", "Спам"),
        ("approved", "Подтвержден"),
        ("in_awaitinng", "В ожидании"),
        ("completed", "Завершен"),
        ("canceled", "Отменен"),
    ]

    # id - генерируетс автоматически
    client_name = models.CharField(max_length=100)
    services = models.CharField(max_length=200)
    master_id = models.IntegerField()
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOISES, default="not_approved"
    )
