from .selenium_service import whatsapp_service


def whatsapp_status(request):
    return {
        'whatsapp_status': whatsapp_service.status,
        'whatsapp_phone': whatsapp_service.phone,
        'whatsapp_name': whatsapp_service.name,
    }
