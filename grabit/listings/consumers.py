import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BookingStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        booking_id = data["booking_id"]
        status = data["status"]

        # Send update to frontend
        await self.send(text_data=json.dumps({
            "booking_id": booking_id,
            "status": status,
        }))

