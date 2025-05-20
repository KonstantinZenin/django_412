# Импорт служебных объектов Form
from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput
from core.models import Service, Order, Review

# Форма создания услуги - делаем форму свзанную с моделью

class ServiceForm(forms.ModelForm):
    # Расширим инициализатор для добавления form-control к полям формы
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
# Добавляем класс form-control к каждому полю формы (кроме чекбоксов)
        for field_name, field in self.fields.items():
            if field_name != 'is_popular':  # Пропускаем чекбокс
                field.widget.attrs.update({"class": "form-control"})
            else:  # Для чекбокса добавляем класс переключателя
                field.widget.attrs.update({"class": "form-check-input"})

    name = forms.CharField(
        label="Название услуги",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Введите название услуги"}),
    )

    # Переопределяем поле изображения, чтобы убрать ненужные элементы
    image = forms.ImageField(
        label="Изображение услуги",
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",  # Разрешаем только изображения
            }
        ),
    )

    # Валидатор deля поля description
    def clean_description(self):
        description = self.cleaned_data.get("description")
        if len(description) < 10:
            raise ValidationError("Описание должно содержать не менее 10 символов.")
        return description

    class Meta:
        model = Service
        # # Поля, которые будут отображаться в форме
        fields = ["name", "description", "price", "duration", "is_popular", "image"]


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс form-control к каждому полю формы
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

    # def save(self):
    #     # Сохраняем объект заказа
    #     Сюда можно вклинить логику валидации на бекенде (проверить что мастер предоставляет ВСЕ выбранные услуги)
    #     super().save()

    class Meta:
        model = Order
        fields = [
            "client_name",
            "phone",
            "comment",
            "master",
            "services",
            "appointment_date",
        ]


class ReviewForm(forms.ModelForm):
    """
    Форма для создания отзыва о мастере с использованием Bootstrap 5
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс form-control к каждому полю формы
        for field_name, field in self.fields.items():
            if (
                field_name != "rating"
            ):  # Для рейтинга будет специальная обработка через JS
                field.widget.attrs.update({"class": "form-control"})

    # Скрытое поле для рейтинга, которое будет заполняться через JS
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True,
    )

    class Meta:
        model = Review
        # Исключаем поле is_published из формы для пользователей
        exclude = ["is_published"]
        widgets = {
            "client_name": forms.TextInput(
                attrs={"placeholder": "Как к вам обращаться?", "class": "form-control"}
            ),
            "text": forms.Textarea(
                attrs={
                    "placeholder": "Расскажите о своем опыте посещения мастера",
                    "class": "form-control",
                    "rows": "3",
                }
            ),
            "photo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }
