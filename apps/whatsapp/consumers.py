import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CampaignConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.campaign_id = self.scope['url_route']['kwargs']['campaign_id']
        self.group_name = f'campaign_{self.campaign_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def campaign_update(self, event):
        await self.send(text_data=json.dumps(event['data']))


class WhatsAppConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'whatsapp_status'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def status_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
