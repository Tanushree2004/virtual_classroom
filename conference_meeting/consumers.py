import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.cache import cache


class MeetingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"conference_{self.room_name}"
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        username = self.scope['user'].username if self.scope['user'].is_authenticated else "Unknown"
        participants = cache.get(self.room_group_name, set())

        if username in participants:
            participants.discard(username)
            cache.set(self.room_group_name, participants)
            await self.broadcast_participant_list()
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "join":
            username = data["username"]
            participants = cache.get(self.room_group_name, set())
            participants.add(username)
            cache.set(self.room_group_name, participants)

            await self.broadcast_participant_list()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_joined",
                    "username": username
                }
            )

        elif message_type == "leave":
            username = data["username"]
            participants = cache.get(self.room_group_name, set())
            participants.discard(username)
            cache.set(self.room_group_name, participants)

            await self.broadcast_participant_list()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_left",
                    "username": username
                }
            )

        elif message_type == "get_participants":
            await self.send_participant_list()

        elif message_type == "chat":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "username": data["username"],
                    "message": data["message"]
                }
            )

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_joined",
            "username": event["username"]
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_left",
            "username": event.get("username", "Unknown User")
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "username": event["username"],
            "message": event["message"]
        }))

    async def send_participant_list(self):
        participants = cache.get(self.room_group_name, set())
        await self.send(text_data=json.dumps({
            "type": "participant_list",
            "participants": list(participants)
        }))

    async def broadcast_participant_list(self):
        participants = cache.get(self.room_group_name, set())
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "participant_list",
                "participants": list(participants)
            }
        )

    async def participant_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "participant_list",
            "participants": event["participants"]
        }))
