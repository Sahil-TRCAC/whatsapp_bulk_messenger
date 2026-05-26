from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/campaign/(?P<campaign_id>\d+)/$', consumers.CampaignConsumer.as_asgi()),
    re_path(r'ws/whatsapp/$', consumers.WhatsAppConsumer.as_asgi()),
]
