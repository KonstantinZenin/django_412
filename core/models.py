from doctest import master
from email.mime import image
from django.db import models
from sqlalchemy import ForeignKey
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

    # id - генерируется автоматически
    client_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOISES, default="not_approved")
    date_create = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    # один ко многим
    master = models.ForeignKey("Master", on_delete=models.SET_NULL, null=True, related_name="orders")
    services = models.ManyToManyField(
        "Service", related_name="orders", blank=True, null=True
    )
    appointment_date = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return f"Заказ №{self.id} от {self.client_name} на {self.appointment_date}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        # Сортировка по умолчанию. "-" перед полем означает, что сортировка будет по убыванию
        ordering = ["-date_create"]
        # Создаём индексы.
        indexes = [
            # Индекс по полю "status"
            models.Index(fields=["status"], name="status_idx"),
            # Индекс по полям "date_create"
            models.Index(fields=["date_create"], name="date_create_idx"),
            # Пример составного индекса, если бы мы часто искали заказы мастера за перииод
            # models.Index(fields=["client_name", "phone"], name="client_phone_idx"),
        ]
        


class Master(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="images/masters/", blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    experience = models.PositiveIntegerField()
    # многие ко многим
    services = models.ManyToManyField("Service", related_name="masters")
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    duration = models.PositiveIntegerField(
        help_text="Время в минутах", verbose_name="Длительность"
    )
    is_popular = models.BooleanField(default=False, verbose_name="Популярная услуга")
    image = models.ImageField(upload_to="images/services/", blank=True, null=True, verbose_name="Изображение")


    def __str__(self):
        return f"{self.name}, {self.price} руб."
    

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
