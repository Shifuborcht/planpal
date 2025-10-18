import json
from channels.generic.websocket import AsyncWebsocketConsumer

class FriendConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{self.scope['user'].id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from server
    async def friend_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def feed_update(self, event):
        await self.send(text_data=json.dumps({
        "type": "feed_update",
        "message": event["message"],
        "activity": event["activity"],
    }))
