# Опишем сигнал, который будет слушать создание записи в модель Review и проверять есть ли в поле text слова "плохо" или "ужасно". - Если нет, то меняем is_published на True

from calendar import c
from email import message
from http import client

from django.contrib.admin import action
import telegram
from .models import Order, Review
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .mistral import is_bad_reviw
from .telegram_bot import send_telegram_message
from asyncio import run
from django.conf import settings

TELEGRAM_BOT_API_KEY = settings.TELEGRAM_BOT_API_KEY
TELEGRAM_USER_ID = settings.TELEGRAM_USER_ID

@receiver(post_save, sender=Review)
def check_review_text(sender, instance, created, **kwargs):
    """
    Проверяет текст отзыва на наличие слов "плохо" или "ужасно".
    Если таких слов нет, то устанавливает is_published в True.
    """
    if created:
        if not is_bad_reviw(instance.text):
            instance.is_published = True
            instance.save()
            # Отправка в телеграм
            message = f"""
*Новый отзыв от клиента!*
*Имя*: {instance.client_name}
*Текст*: {instance.text}
*Оценка*: {instance.rating}
*Ссылка на отзыв:* http://127.0.0.1:8000/admin/core/review/{instance.id}/change/

#отзыв
"""
            run(send_telegram_message(TELEGRAM_BOT_API_KEY, TELEGRAM_USER_ID, message))
        else:
            instance.is_published = False
            instance.save()
            # Вывод в терминал 
            print(f"Отзыв '{instance.client_name}' не опубликован из-за негативных слов.")


@receiver(m2m_changed, sender=Order.services.through)
def telegram_order_notification(sender, instance, action, **kwargs):
    """
    Обработчик сигнала m2m_changed для модели Order.
    ОН обрабатывает добавление КАЖДОЙ услуги в запись на приём.

    """
    if action == "post_add" and kwargs.get("pk_set"):
        # Получаем список услуг из заказа
        services = [service.name for service in instance.services.all()]

        # Форматирование даты и времени для желаемой даты записи и даты создания услуги
        if instance.appointment_date:
            formatted_appointment_date = instance.appointment_date.strftime("%d.%m.%Y %H:%M")
        else:
            formatted_appointment_date = "не указана"

        if instance.date_create:
            formatted_date_create = instance.date_create.strftime("%d.%m.%Y %H:%M")
        else:
            formatted_date_create = "не указана"

        # Формируем сообщение
        telegram_message = f"""
*Новая запись на прием*

*Имя* {instance.client_name}
*Телефон* {instance.phone or 'не указан'}
*Комментарий* {instance.comment or 'не указан'}
*Услуги* {', '.join(services) or 'не указаны'}
*дата создания:* {formatted_date_create}
*Мастер* {instance.master.first_name} {instance.master.last_name}
*Желаемая дата записи:* {formatted_appointment_date}
*Ссылка на админ-панель:* https://127.0.0.1:8000/admin/core/order/{instance.id}/change/

#запись #{instance.master.last_name.lower()}
______________________________________
"""
        # логика отправки сообщения в Telegram
        run(send_telegram_message(TELEGRAM_BOT_API_KEY, TELEGRAM_USER_ID, telegram_message))
