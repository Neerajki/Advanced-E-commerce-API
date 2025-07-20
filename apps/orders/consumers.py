from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            print("❌ WebSocket rejected: Anonymous user")
            await self.close()
        else:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"✅ WebSocket connected: {self.group_name}")

    async def disconnect(self, close_code):
        group_name = getattr(self, 'group_name', None)
        if group_name:
            await self.channel_layer.group_discard(group_name, self.channel_name)
            print(f"🔌 WebSocket disconnected: {group_name}")
        else:
            print("⚠️ No group_name found during disconnect (probably rejected connection)")

    async def order_status_update(self, event):
        message = event.get('message', 'No message')
        await self.send(text_data=json.dumps({
            "type": "order_status",
            "message": message
        }))
