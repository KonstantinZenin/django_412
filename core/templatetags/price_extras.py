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