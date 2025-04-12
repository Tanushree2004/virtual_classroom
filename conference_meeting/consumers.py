import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class MeetingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"conference_{self.room_name}"
        self.participants = set()
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        # If the user was in the participant list, remove them
        username = self.scope['user'].username if self.scope['user'].is_authenticated else "Unknown"
        self.participants.discard(username)

        # Broadcast that a user left and update participant list
        """await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "user_left",
                "username": username
            }
        )"""
        if username and username in self.participants:
            self.participants.discard(username)
            await self.broadcast_participant_list()

        await self.broadcast_participant_list()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "join":
            username = data["username"]
            self.participants.add(username)
            await self.broadcast_participant_list()
            # Notify everyone that a user joined
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user_joined",
                    "username": username
                }
            )

              # Send updated list to all users

        elif message_type == "leave":
            username = data["username"]
            self.participants.discard(username)
            await self.broadcast_participant_list()
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "user_left",
                    "username": username
                }
            )

              # Update list for all users

        elif message_type == "get_participants":
            await self.send_participant_list()  # Send list only to the requesting user

        elif message_type == "chat":
            await self.channel_layer.group_send(
                self.room_group_name, {
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
        """ Send the participant list to the requesting user """
        await self.send(text_data=json.dumps({
            "type": "participant_list",
            "participants": list(self.participants)
        }))

    async def broadcast_participant_list(self):
        """ Send the updated participant list to all users """
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "participant_list",
                "participants": list(self.participants)
            }
        )
    async def participant_list(self, event):
        """ Handles sending the updated participant list to all clients """
        await self.send(text_data=json.dumps({
            "type": "participant_list",
            "participants": event["participants"]
        }))
