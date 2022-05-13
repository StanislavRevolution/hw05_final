from django.utils import timezone


def year(request):
    now = timezone.now()
    """Добавляет переменную с текущим годом."""
    return {
        'year': now.year
    }
