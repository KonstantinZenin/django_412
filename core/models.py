from doctest import master
from django import db
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    STATUS_CHOICES = [
        ("not_approved", "Не подтвержден"),
        ("moderated", "Прошёл модерацию"),
        ("spam", "Спам"),
        ("approved", "Подтвержден"),
        ("in_awaitinng", "В ожидании"),
        ("completed", "Завершен"),
        ("canceled", "Отменен"),
    ]

    # id - генерируется автоматически
    client_name = models.CharField(max_length=100, db_index=True, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, db_index=True, verbose_name="Телефон клиента")
    comment = models.TextField(blank=True, db_index=True, verbose_name="Комментарий клиента")
    # Для поля choises будет добавлен метод display_status
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="not_approved", verbose_name="Статус заказа",)
    date_create = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name="Дата создания"
    )
    date_update = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    # один ко многим
    master = models.ForeignKey(
        "Master",
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders",
        verbose_name="Мастер",
    )
    services = models.ManyToManyField(
        "Service", related_name="orders", blank=True, null=True, verbose_name="Выбранные услуги")
    appointment_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Дата и время записи"
    )


    def __str__(self):
        return f"Заказ №{self.id} от {self.client_name} на {self.appointment_date}"


    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        # Сортировка по умолчанию. "-" перед полем означает, что сортировка будет по убыванию
        ordering = ["-date_create"]
        # Создаём индексы.
        indexes = [
            # Индекс по полю status
            models.Index(fields=["status"], name="status_idx"),
            # Индекс по полю date_created (хотя для сортировки он может создаться и так,
            # но явное указание не повредит и поможет при фильтрации)
            models.Index(fields=["date_create"], name="created_at_idx"),
            # Пример составного индекса, если бы мы часто искали заказы мастера за период
            models.Index(
                fields=["client_name", "phone", "comment"],
                name="client_phone_comment_idx",
            ),
        ]


class Master(models.Model):
    first_name = models.CharField(
        max_length=100, db_index=True, verbose_name="Имя мастера"
    )
    last_name = models.CharField(max_length=100, verbose_name="Фамилия мастера")
    photo = models.ImageField(
        upload_to="images/masters/", blank=True, null=True, verbose_name="Фото мастера"
    )
    phone = models.CharField(
        max_length=20, db_index=True, verbose_name="Телефон мастера"
    )
    address = models.CharField(max_length=255, verbose_name="Адрес мастера")
    email = models.EmailField(blank=True, verbose_name="Email мастера")
    experience = models.PositiveIntegerField(verbose_name="Опыт работы")
    # многие ко многим
    services = models.ManyToManyField(
        "Service", related_name="masters", verbose_name="Услуги мастера"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")

    def avg_rating(self) -> float:
        """Вычисляет среднюю оценку мастера на основе опубликованных отзывов"""
        # Получаем только опубликованные отзывы
        published_reviews = self.reviews.filter(is_published=True)
        # Проверяем, есть ли отзывы
        if published_reviews.exists():
            # Вычисляем среднее значение и округляем до 1 знака после запятой
            return round(sum(review.rating for review in published_reviews) / published_reviews.count(), 1)
        else:
            # Если отзывов нет, возвращаем 0 или None
            return 0.0


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"
        ordering = ["-experience"] 


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги", db_index=True)
    description = models.TextField(verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    duration = models.PositiveIntegerField(
        help_text="Время в минутах",
        verbose_name="Время выполнения услуги",
        default=20,
        blank=True,
    )
    is_popular = models.BooleanField(default=False, verbose_name="Популярная услуга", blank=True)
    image = models.ImageField(upload_to="images/services/", blank=True, null=True, verbose_name="Изображение")


    def __str__(self):
        return f"{self.name}, {self.price} руб."
    

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["name"]



class Review(models.Model):
    """
    Модель для хранения отзывов клиентов о мастерах
    """

    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.IntegerField(
        verbose_name="Оценка", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    master = models.ForeignKey(
        "Master",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Мастер",
    )
    photo = models.ImageField(
        upload_to="images/reviews/", blank=True, null=True, verbose_name="Фотография"
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Отзыв от {self.client_name} о мастере {self.master}. Статус: {'Опубликован' if self.is_published else 'Не опубликован'}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
