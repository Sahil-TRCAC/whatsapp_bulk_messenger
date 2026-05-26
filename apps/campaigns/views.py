import csv
import json
import random
import time
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Campaign, CampaignRecipient
from apps.contacts.models import Contact, ContactGroup


def campaign_list(request):
    campaigns = Campaign.objects.all()
    data = []
    for c in campaigns:
        data.append({
            'id': c.id,
            'name': c.name,
            'status': c.status,
            'status_display': c.get_status_display(),
            'total': c.total_recipients,
            'sent': c.sent_count,
            'failed': c.failed_count,
            'progress': c.progress,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
            'started_at': c.started_at.strftime('%Y-%m-%d %H:%M') if c.started_at else None,
        })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'campaigns': data})

    return render(request, 'campaigns.html', {'campaigns': data})


def campaign_compose(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        message_template = request.POST.get('message_template', '').strip()
        delay_min = int(request.POST.get('delay_min', 5))
        delay_max = int(request.POST.get('delay_max', 10))
        recipient_type = request.POST.get('recipient_type', '')
        group_ids = request.POST.getlist('groups')
        custom_numbers = request.POST.get('custom_numbers', '').strip()
        image = request.FILES.get('image')
        action = request.POST.get('action', 'draft')

        if not name or not message_template:
            return JsonResponse({'error': 'Name and message template are required.'}, status=400)

        campaign = Campaign.objects.create(
            name=name,
            message_template=message_template,
            delay_min=delay_min,
            delay_max=delay_max,
            image=image,
            status='draft',
        )

        contacts = []
        if recipient_type == 'all':
            contacts = Contact.objects.filter(is_active=True)
        elif recipient_type == 'groups' and group_ids:
            contacts = Contact.objects.filter(groups__id__in=group_ids, is_active=True).distinct()
        elif recipient_type == 'custom' and custom_numbers:
            for line in custom_numbers.strip().split('\n'):
                line = line.strip()
                if line:
                    name_val = f'Custom-{line[-4:]}'
                    contact, _ = Contact.objects.get_or_create(
                        phone=line,
                        defaults={'name': name_val}
                    )
                    contacts.append(contact)

        for contact in contacts:
            CampaignRecipient.objects.create(campaign=campaign, contact=contact)

        if action == 'launch' and contacts:
            campaign.status = 'running'
            campaign.started_at = timezone.now()
            campaign.save()
            from .tasks import launch_campaign_thread
            launch_campaign_thread(campaign.id)

        return JsonResponse({
            'success': True,
            'campaign_id': campaign.id,
            'recipients_count': len(contacts),
        })

    groups = ContactGroup.objects.all()
    return render(request, 'compose.html', {'groups': groups})


def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    return render(request, 'logs.html', {'campaign': campaign})


def campaign_launch(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if campaign.status in ['draft', 'failed', 'completed'] and campaign.total_recipients > 0:
        campaign.status = 'running'
        campaign.started_at = timezone.now()
        campaign.save()
        from .tasks import launch_campaign_thread
        launch_campaign_thread(campaign.id)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Campaign cannot be launched.'}, status=400)


def campaign_pause(request, pk):
    from django.core.cache import cache
    cache.set(f'campaign:{pk}:paused', True)
    campaign = get_object_or_404(Campaign, pk=pk)
    campaign.status = 'paused'
    campaign.save()
    return JsonResponse({'success': True})


def campaign_resume(request, pk):
    from django.core.cache import cache
    cache.delete(f'campaign:{pk}:paused')
    campaign = get_object_or_404(Campaign, pk=pk)
    campaign.status = 'running'
    campaign.save()
    from .tasks import launch_campaign_thread
    launch_campaign_thread(campaign.id)
    return JsonResponse({'success': True})


def campaign_cancel(request, pk):
    from django.core.cache import cache
    cache.set(f'campaign:{pk}:paused', True)
    campaign = get_object_or_404(Campaign, pk=pk)
    campaign.status = 'failed'
    campaign.completed_at = timezone.now()
    campaign.save()
    return JsonResponse({'success': True})


def campaign_delete(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    campaign.delete()
    return JsonResponse({'success': True})


def campaign_recipients(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    page = int(request.GET.get('page', 1))
    recipients = campaign.recipients.all()
    paginator = Paginator(recipients, 50)
    page_obj = paginator.get_page(page)

    data = []
    for r in page_obj:
        data.append({
            'id': r.id,
            'name': r.contact.name,
            'phone': r.contact.phone,
            'status': r.status,
            'status_display': r.get_status_display(),
            'sent_at': r.sent_at.strftime('%Y-%m-%d %H:%M:%S') if r.sent_at else None,
            'error': r.error_message,
        })

    return JsonResponse({
        'recipients': data,
        'total': campaign.total_recipients,
        'sent': campaign.sent_count,
        'failed': campaign.failed_count,
        'pending': campaign.pending_count,
        'progress': campaign.progress,
        'status': campaign.status,
        'status_display': campaign.get_status_display(),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_prev': page_obj.has_previous(),
    })


def campaign_export_logs(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="campaign_{campaign.id}_logs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Status', 'Sent At', 'Error'])

    for r in campaign.recipients.all():
        writer.writerow([
            r.contact.name,
            r.contact.phone,
            r.status,
            r.sent_at.strftime('%Y-%m-%d %H:%M:%S') if r.sent_at else '',
            r.error_message,
        ])

    return response
