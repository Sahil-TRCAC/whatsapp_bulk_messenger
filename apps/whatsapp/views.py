import json
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .selenium_service import whatsapp_service
from apps.contacts.models import Contact
from apps.campaigns.models import Campaign, CampaignRecipient


def whatsapp_page(request):
    return render(request, 'whatsapp.html', {'active_page': 'whatsapp'})


def whatsapp_qr(request):
    if whatsapp_service.status == 'disconnected':
        return JsonResponse({'status': 'disconnected', 'qr': None})
    if whatsapp_service.status == 'loading':
        return JsonResponse({'status': 'loading', 'qr': None})
    if whatsapp_service.status == 'connected':
        return JsonResponse({'status': 'connected', 'qr': None})

    qr = whatsapp_service.get_qr_code()
    if qr is None:
        if whatsapp_service.is_logged_in():
            whatsapp_service.status = 'connected'
            return JsonResponse({'status': 'connected', 'qr': None})
        return JsonResponse({'status': 'transitioning', 'qr': None})
    return JsonResponse({'status': 'scanning', 'qr': qr})


def whatsapp_status(request):
    return JsonResponse({
        'status': whatsapp_service.status,
        'phone': whatsapp_service.phone,
        'name': whatsapp_service.name,
    })


def whatsapp_connect(request):
    try:
        whatsapp_service.start_driver()
        return JsonResponse({'success': True, 'status': whatsapp_service.status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def whatsapp_disconnect(request):
    whatsapp_service.stop_driver()
    return JsonResponse({'success': True})


def dashboard(request):
    total_contacts = Contact.objects.count()
    total_campaigns = Campaign.objects.count()
    today = timezone.now().date()
    sent_today = CampaignRecipient.objects.filter(
        status='sent',
        sent_at__date=today
    ).count()
    running_campaigns = Campaign.objects.filter(status='running').count()
    recent_campaigns = Campaign.objects.all()[:5]

    ws_status = whatsapp_service.status

    return render(request, 'dashboard.html', {
        'total_contacts': total_contacts,
        'total_campaigns': total_campaigns,
        'sent_today': sent_today,
        'running_campaigns': running_campaigns,
        'recent_campaigns': recent_campaigns,
        'whatsapp_status': ws_status,
        'active_page': 'dashboard',
    })
