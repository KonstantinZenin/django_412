from .data import MENU_ITEMS


def menu_context(request):
    """контекстный процессор для передачи menu_items в шаблоны"""
    return {"menu_items": MENU_ITEMS}
