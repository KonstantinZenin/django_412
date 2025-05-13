# Импорт служебных объектов Form
from typing import Any
from django import forms
from django.core.exceptions import ValidationError

from core.models import Service, Order

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

    # Валидатор для поля description
    def clean_description(self):
        description = self.cleaned_data.get("description")
        if len(description) < 10:
            raise ValidationError("Описание должно содержать не менее 10 символов.")
        return description


    class Meta:
        model = Service
        # Подя, которые будут отображаться в форме
        fields = ["name", "description", "price", "duration", "is_popular", "image"]


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс form-control к каждому полю формы (кроме чекбоксов)
        for field_name, field in self.fields.items():           
                field.widget.attrs.update({"class": "form-control"})


    # def save(self):
    #     # Сюда можно вклинить логику валидации на бэкэнде
    #     super().save()


    class Meta:
        model= Order
        fields = ["client_name", "phone", "comment", "master", "services", "appointment_date"]