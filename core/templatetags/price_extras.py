from django import template

register = template.Library()

@register.filter(name='format_price')
def format_price(value, currency='₽'):
    """форматирует цену добавляя знак рубля"""
    try:
        # Преобразуем значение в число, если оно вдруг пришло как строка
        numeric_value = float(value)
        # Форматируем число с разделителями тысяч
        formatted_number = '{:,.0f}'.format(numeric_value).replace(',', ' ')
        # Добавляем символ рубля
        return f"{formatted_number} {currency}"
    except (ValueError, TypeError):
        # Если значение не может быть преобразовано в число, возвращаем исходное значение
        return value
    

# Мы можем сделать простой и инклюзтвный тэг для шаблонизатора
@register.simple_tag(name='format_name')
def format_name(name):
    "форматирует имя, делаяя первую букву заглавной и добавляет перед именем Мастер"
    if not name:
        return ""
    return f"Мастер {name.capitalize()}"

# Мы можем сделать простой тэг с параметрами для position
@register.simple_tag(name='format_position')
def format_position(position, param1, param2):
    "форматирует позицию, добавляя перед ней Должность"
    if not position:
        return ""
    return f"Должность: {position.capitalize()} {param1} {param2}"
