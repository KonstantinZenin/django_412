from math import e
from pyexpat import model
import re
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse, JsonResponse
from voluptuous import extra
from .data import *
from django.contrib.auth.decorators import login_required
from .models import Order, Master, Service, Review
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy


# messages - это встроенный модуль Django для отображения сообщений пользователю
from django.contrib import messages
from .forms import ServiceForm, OrderForm, ReviewForm, ServiceEasyForm
import json

masters = [
    {"id": 1, "name": "Эльдар 'Бритва' Рязанов"},
    {"id": 2, "name": "Зоя 'Ножницы' Космодемьянская"},
    {"id": 3, "name": "Борис 'Фен' Пастернак"},
    {"id": 4, "name": "Иннокентий 'Лак' Смоктуновский"},
    {"id": 5, "name": "Раиса 'Бигуди' Горбачёва"},
]

class StaffRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, является ли пользователь сотрудником (is_staff).
    Если проверка не пройдена, пользователь перенаправляется на главную страницу
    с сообщением об ошибке.
    """
    def test_func(self):
        # Проверяем, аутентифицирован ли пользователь и является ли он сотрудником
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        # Этот метод вызывается, если test_func вернул False
        messages.error(self.request, "У вас нет доступа к этому разделу.")
        return redirect("landing") # Предполагаем, что 'landing' - это имя URL главной страницы



def landing(request):
    # Получаем список активных мастеров из базы данных
    masters_db = Master.objects.filter(is_active=True)

    # Получаем все услуги из базы данных вместо только популярных
    all_services = Service.objects.all()

    context = {
        "title": "Главная - Барбершоп Арбуз",
        "services": all_services,  # Все услуги из базы данных
        "masters": masters_db,  # Из базы данных
        "years_on_market": 50,
    }
    return render(request, "core/landing.html", context)



@login_required
def services_list(request):
    """
    Представление для отображения списка всех услуг
    с возможностью их редактирования или удаления
    """
    # Получаем все услуги из базы данных
    services = Service.objects.all()

    context = {
        "title": "Управление услугами",
        "services": services,
    }

    return render(request, "core/services_list.html", context)


class ServicesListView(StaffRequiredMixin, ListView):
    """
    Представление для отображения списка всех услуг
    с возможностью их редактирования или удаления
    """

    model = Service
    template_name = "core/services_list.html"
    context_object_name = "services"
    extra_context = {"title": "Управление услугами"}


def master_detail(request, master_id):
    # Получаем мастера по id
    master = get_object_or_404(Master, id=master_id)

    # Проверем просматривал ли пользователь этого мастера ранее
    viewed_masters = request.session.get("viewed_masters", [])

    if master_id not in viewed_masters:

        # Увеличиваем счётчик просмотров мастера
        # F - это специальный объект, который позволяет ссылаться на поля модели

        Master.objects.filter(id=master_id).update(view_count=F("view_count") + 1)

        # Добавлем мастера в список просмотренных
        viewed_masters.append(master_id)
        request.session["viewed_masters"] = viewed_masters

        # Обновляем объект после изменения в БД
        master.refresh_from_db()

    # Получаем свзязанные услуги мастера
    services = master.services.all()

    
    # Получаем опубликованные отзывы о мастере, сортируем по дате создания (сначала новые)
    reviews = master.reviews.filter(is_published=True).order_by("-created_at")

    context={
        "title": f"Мастер {master.first_name} {master.last_name}",
        "master": master,
        "services": services,
    }

    return render(request, "core/master_detail.html", context)


# Перепишем представление thanks на TemplateView
class ThanksView(TemplateView): # Существующий класс, дорабатываем его
    template_name = "core/thanks.html"

    def get_context_data(self, **kwargs):
        """
        Формирует и возвращает словарь контекста для шаблона "Спасибо".
        Добавляет количество активных мастеров, дополнительное сообщение
        и обрабатывает параметр 'source' из URL.
        """
        context = super().get_context_data(**kwargs)
        
        # Получаем количество активных мастеров из базы данных
        # Это полезная информация, которую можно отобразить на странице благодарности.
        masters_count = Master.objects.filter(is_active=True).count()
        context["masters_count"] = masters_count
        
        # Добавим новый статический элемент в контекст для демонстрации
        context["additional_message"] = "Спасибо, что выбрали наш первоклассный сервис!"
        
        # Проверим, передан ли параметр 'source' в URL.
        # kwargs содержит именованные аргументы, захваченные из URL-шаблона.
        # Например, если URL /thanks/order/, то kwargs будет {'source': 'order'}
        if 'source' in kwargs:
            source_page = kwargs['source']
            if source_page == 'order':
                context['source_message'] = "Ваш заказ успешно создан и принят в обработку."
            elif source_page == 'review':
                context['source_message'] = "Ваш отзыв успешно отправлен и будет опубликован после модерации."
            else:
                # Общий случай, если источник не 'order' и не 'review'
                context['source_message'] = f"Благодарим вас за ваше действие, инициированное со страницы: {source_page}."
        else:
            # Если параметр 'source' не передан
            context['source_message'] = "Благодарим вас за посещение!"
            
        return context


# @login_required
# def orders_list(request):
#     # Проверяем, что пользователь является сотрудником
#     if not request.user.is_staff:
#         # Если пользователь не сотрудник, перенаправляем его на главную
#         messages.error(request, "У вас нет доступа к этому разделу")
#         return redirect("landing")

#     if request.method == "GET":
#         # Получаем все заказы
#         # Используем жадную загрузку для мастеров и услуг
#         all_orders = (
#             Order.objects.select_related("master").prefetch_related("services").all()
#         )

#         # Получаем строку поиска
#         search_query = request.GET.get("search", None)

#         if search_query:
#             # Получаем чекбоксы
#             check_boxes = request.GET.getlist("search_in")

#             # Проверяем Чекбоксы и добавляем Q объекты в запрос
#             # |= это оператор "или" для Q объектов
#             filters = Q()

#             if "phone" in check_boxes:
#                 # Полная запись где мы увеличиваем фильтры
#                 filters = filters | Q(phone__icontains=search_query)

#             if "name" in check_boxes:
#                 # Сокращенная запись через inplace оператор
#                 filters |= Q(client_name__icontains=search_query)

#             if "comment" in check_boxes:
#                 filters |= Q(comment__icontains=search_query)

#             if filters:
#                 # Если фильтры появились. Если Q остался пустым, мы не попадем сюда
#                 all_orders = all_orders.filter(filters)

#         # Отправляем все заказы в контекст
#         context = {
#             "title": "Заказы",
#             "orders": all_orders,
#         }

#         return render(request, "core/orders_list.html", context)


class OrdersListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "core/orders_list.html"
    context_object_name = "orders"
    
    def get_queryset(self):
        # Получаем все заказы
        # Используем жадную загрузку для мастеров и услуг
        all_orders = (
            Order.objects.select_related("master").prefetch_related("services").all()
        )

        # Получаем строку поиска
        search_query = self.request.GET.get("search", None)

        if search_query:
            # Получаем чекбоксы
            check_boxes = self.request.GET.getlist("search_in")

            # Проверяем Чекбоксы и добавляем Q объекты в запрос
            # |= это оператор "или" для Q объектов
            filters = Q()

            if "phone" in check_boxes:
                # Полная запись где мы увеличиваем фильтры
                filters = filters | Q(phone__icontains=search_query)

            if "name" in check_boxes:
                # Сокращенная запись через inplace оператор
                filters |= Q(client_name__icontains=search_query)

            if "comment" in check_boxes:
                filters |= Q(comment__icontains=search_query)

            if filters:
                # Если фильтры появились. Если Q остался пустым, мы не попадем сюда
                all_orders = all_orders.filter(filters)

        return all_orders


class OrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = "core/order_detail.html"
    pk_url_kwarg = "order_id"



def service_create(request):

    # Если метод GET - возвращаем пустую форму
    if request.method == "GET":
        form = ServiceForm()
        context = {
            "title": "Создание услуги",
            "form": form,
            "button_txt": "Создать"
        }
        return render(request, "core/service_form.html", context)

    elif request.method == "POST":
        # Создаем форму и передаем в нее POST данные
        form = ServiceForm(request.POST, request.FILES) 

        # Если форма валидна:
        if form.is_valid():
            # Так как это ModelForm - нам не надо извлекать пол по отдельности
            # Сохраняем форму в БД
            form.save()
            service_name = form.cleaned_data.get("name")

            # Даем пользователю уведомление об успешном создании
            messages.success(request, f"Услуга {service_name} успешно создана!")

            # Перенаправляем на страницу со всеми услугами
            return redirect("services_list")

        # В случае ошибок валидации Django автоматически заполнит form.errors
        # и отобразит их в шаблоне, поэтому просто возвращаем форму
        context = {
            "title": "Создание услуги",
            "form": form,
            "button_txt": "Создать"
        }
        return render(request, "core/service_form.html", context)


def service_update(request, service_id):
    # Вне зависимости от метода - получаем услугу
    service = get_object_or_404(Service, id=service_id)

    # Если метод GET - возвращаем форму
    if request.method == "GET":
        # У нас форма связана с моделью. Рендер всех полей
        # Просто ложим в форму обьект услуги
        form = ServiceForm(instance=service)

        context = {
            "title": f"Редактирование услуги {service.name}",
            "form": form,
            "button_txt": "Обновить"
        }

        return render(request, "core/service_form.html", context)

    elif request.method == "POST":
        # Создаём форму и передаём в неё POST данные
        form = ServiceForm(request.POST, request.FILES, instance=service)

        # Если форма валидна
        if form.is_valid():
            # Форма связана с моделью просто сохраняем её
            form.save()

            service_name = form.cleaned_data.get("name")
            # Даём пользователю уведомление об успешном обновлении
            messages.success(request, f"Услуга {service.name} успешно обновлена!")

            # Перенаправлем на страницу со всеми услугами
            return redirect("services_list")
        else:
            # Если данные не валидны, возвращаем ошибку
            messages.error(request, "Ошибка: все поля должны быть заполнены!")

            context = {
            "title": f"Редактирование услуги {service.name}",
            "form": form,
            "button_txt": "Обновить"
            }
            
            return render(request, "core/service_form.html", context)


class ServiceCreateView(CreateView):
    """"
    Вью для создания услуги.
    service_create/<str:form_mode>/
    form_mode - режим формы.
    """
    form_class = ServiceForm
    template_name = "core/service_form.html"
    success_url = reverse_lazy("services_list")
    extra_context = {"title": "Создание услуги", "button_txt": "Создать"}

    def form_valid(self, form) -> HttpResponse:
        messages.success(
            self.request, f"Услуга {form.cleaned_data.get('name')} успешно создана!"
        )
        return super().form_valid(form)
    

    def form_invalid(self, form) -> HttpResponse:
        messages.error(self.request, "Ошибка формы: проверьте ввод данных")
        return super().form_invalid(form)
    

    def get_form_class(self):
        """
        Обрабатывает параметр form_mode и возвращает нужную форму
        2 варианта: "normal" и "easy"
        """
        form_mode = self.kwargs.get("form_mode")
        if form_mode == "normal":
            return ServiceForm
        
        elif form_mode == "easy":
            return ServiceEasyForm
        

class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "core/service_form.html"
    success_url = reverse_lazy("services_list")
    extra_context = {"button_txt": "Обновить"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактирование услуги {self.object.name}"
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, f"Услуга {form.cleaned_data.get('name')} успешно обновлена!"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка формы: проверьте ввод даных")


def masters_services_by_id(request, master_id=None):
    """
    Вью для ajax запросов фронтенда, для подгрузки услуг конкретного мастера в форму
    m2m выбора услуг
    """
    # Если master_id не передан в URL, пробуем получить его из POST-запроса
    if master_id is None:
        data = json.loads(request.body)
        master_id = data.get('master_id')
    # Получаем мастера по id
    master = get_object_or_404(Master, id=master_id)

    # Получаем услуги
    services = master.services.all()

    # Формируем ответ в виде JSON
    response_data = []

    for service in services:
        # Добавляем в ответ id и название услуги
        response_data.append(
            {
                "id": service.id,
                "name": service.name,
            }
        )
    # Возвращаем ответ в формате JSON
    return HttpResponse(
        json.dumps(response_data, ensure_ascii=False, indent=4),
        content_type="application/json",
    )

def order_create(request):
    if request.method == "GET":
        form = OrderForm()

        context = {
            "title": "Создание заказа",
            "form": form,
            "button_text": "Запись"
        }

        return render(request, "core/order_form.html", context)
    
    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            form.save()
            client_name = form.cleaned_data.get("client_name")
            messages.success(request, f"Заказ для {client_name} успешно создан!")

            return redirect("thanks")
        
        context = {
            "title": "Создание заказа",
            "form": form,
            "button_text": "Запись"
        }

        return render(request, "core/order_form.html", context)
    

def create_review(request):
    """
    Представление для создания отзыва о мастере
    """
    if request.method == "GET":
        # При GET-запросе показываем форму, если указан ID мастера, устанавливаем его в поле мастера
        master_id = request.GET.get("master_id")

        initial_data = {}
        if master_id:
            try:
                master = Master.objects.get(pk=master_id)
                initial_data["master"] = master
            except Master.DoesNotExist:
                pass

        form = ReviewForm(initial=initial_data)

        context = {
            "title": "Оставить отзыв",
            "form": form,
            "button_text": "Отправить",
        }
        return render(request, "core/review_form.html", context)

    elif request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            review = form.save(
                commit=False
            )  # Не сохраняем сразу, чтобы установить is_published=False
            review.is_published = False  # Отзыв по умолчанию не опубликован
            review.save()  # Сохраняем отзыв

            # Сообщаем пользователю, что его отзыв успешно добавлен и будет опубликован после модерации
            messages.success(
                request,
                "Ваш отзыв успешно добавлен! Он будет опубликован после проверки модератором.",
            )

            # Перенаправляем на страницу благодарности
            return redirect("thanks")

        # В случае ошибок валидации возвращаем форму с ошибками
        context = {
            "title": "Оставить отзыв",
            "form": form,
            "button_text": "Отправить",
        }
        return render(request, "core/review_form.html", context)


def get_master_info(request):
    """
    Универсальное представление для получения информации о мастере через AJAX.
    Возвращает данные мастера в формате JSON.
    """
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        master_id = request.GET.get("master_id")
        if master_id:
            try:
                master = Master.objects.get(pk=master_id)
                # Формируем данные для ответа
                master_data = {
                    "id": master.id,
                    "name": f"{master.first_name} {master.last_name}",
                    "experience": master.experience,
                    "photo": master.photo.url if master.photo else None,
                    "services": list(master.services.values("id", "name", "price")),
                }
                return JsonResponse({"success": True, "master": master_data})
            except Master.DoesNotExist:
                return JsonResponse({"success": False, "error": "Мастер не найден"})
        return JsonResponse({"success": False, "error": "Не указан ID мастера"})
    return JsonResponse({"success": False, "error": "Недопустимый запрос"})

# --- Этап 1: Базовые CBV ---
# 1. GreetingView на основе django.views.View
class GreetingView(View):
    """
    Простое представление на основе базового класса View.
    Демонстрирует обработку GET и POST запросов.
    """
    # Сообщения для разных типов запросов
    greeting_get_message = "Привет, мир! Это GET запрос из GreetingView."
    greeting_post_message = "Вы успешно отправили POST запрос в GreetingView!"

    # Атрибут http_method_names определяет, какие HTTP-методы разрешены для этого View.
    # По умолчанию он включает 'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'.
    # Мы можем его переопределить, если хотим ограничить поддерживаемые методы.
    # http_method_names = ['get', 'post'] # В данном случае это избыточно, т.к. мы реализуем get и post

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запросы.
        Возвращает простое HTTP-сообщение.
        """
        # request - это объект HttpRequest
        # args и kwargs - это позиционные и именованные аргументы, захваченные из URL
        return HttpResponse(self.greeting_get_message)

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запросы.
        Возвращает простое HTTP-сообщение.
        """
        # Здесь могла бы быть логика обработки данных из POST-запроса,
        # например, сохранение данных формы.
        return HttpResponse(self.greeting_post_message)


class ServiceDetailView(DetailView):
    """
    Представление для отображения детальной информации об услуге.
    Использует модель Service и явно указанное имя шаблона.
    в шаблон будет передан объект service (имя по умолчанию для контекстной переменной).
    """

    model = Service
    template_name = "core/service_detail.html"
