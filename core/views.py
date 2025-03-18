from django.shortcuts import render
from django.http import HttpResponse

masters = [
    {"id": 1, "name": "Эльдар 'Бритва' Рязанов"},
    {"id": 2, "name": "Зоя 'Ножницы' Космодемьянская"},
    {"id": 3, "name": "Борис 'Фен' Пастернак"},
    {"id": 4, "name": "Иннокентий 'Лак' Смоктуновский"},
    {"id": 5, "name": "Раиса 'Бигуди' Горбачёва"},
] 

def main(request):
    return HttpResponse("Добро пожаловать в барбершоп!")


def master_detail(request, master_id):
    try:
        master = [m for m in masters if m["id"] == master_id][0]
    except IndexError:
        return HttpResponse(f"Мастер не найден")
    return HttpResponse(f"<h1>{master['name']}</h1>")


def thanks(request):
    masters_count = len(masters)

    context = {
        "masters_count": masters_count,
    }

    return render(request, "thanks.html", context)
