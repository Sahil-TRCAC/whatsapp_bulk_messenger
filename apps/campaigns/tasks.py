import random
import time
import threading
from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from .models import Campaign, CampaignRecipient
from apps.whatsapp.selenium_service import whatsapp_service


def send_campaign_threaded(campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        return {'error': 'Campaign not found'}

    if campaign.status not in ['running', 'paused']:
        return {'error': f'Campaign status is {campaign.status}'}

    recipients = campaign.recipients.filter(status='pending')

    for recipient in recipients:
        if cache.get(f'campaign:{campaign_id}:paused'):
            campaign.status = 'paused'
            campaign.save()
            return {'status': 'paused'}

        try:
            if whatsapp_service.status != 'connected':
                raise Exception('WhatsApp is not connected. Please connect on the WhatsApp page first.')

            message = campaign.message_template.replace('{{name}}', recipient.contact.name)

            if campaign.image and campaign.image.path:
                whatsapp_service.send_image(
                    recipient.contact.phone,
                    campaign.image.path,
                    message
                )
            else:
                whatsapp_service.send_text(recipient.contact.phone, message)

            recipient.status = 'sent'
            recipient.sent_at = timezone.now()
            recipient.save()

        except Exception as e:
            recipient.status = 'failed'
            recipient.error_message = str(e)[:500]
            recipient.save()

        delay = random.randint(campaign.delay_min, campaign.delay_max)
        time.sleep(delay)

    campaign = Campaign.objects.get(id=campaign_id)
    remaining = campaign.recipients.filter(status='pending').count()

    if remaining == 0:
        campaign.status = 'completed'
        campaign.completed_at = timezone.now()
        campaign.save()

    return {
        'status': campaign.status,
        'sent': campaign.sent_count,
        'failed': campaign.failed_count,
        'remaining': remaining,
    }


def launch_campaign_thread(campaign_id):
    thread = threading.Thread(target=send_campaign_threaded, args=(campaign_id,), daemon=True)
    thread.start()
    return thread


@shared_task(bind=True, max_retries=3)
def send_campaign(self, campaign_id):
    return send_campaign_threaded(campaign_id)
