import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message

ONLINE_USERS = {}


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        if not self.user.is_authenticated:
            await self.close()
            return

        is_participant = await self.is_user_participant()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Track this user as online in this room
        if self.room_group_name not in ONLINE_USERS:
            ONLINE_USERS[self.room_group_name] = set()
        ONLINE_USERS[self.room_group_name].add(self.user.username)

        # Broadcast this user's online status to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "user_status", "username": self.user.username, "status": "online"}
        )

        # Send current status of other participants to this newly connected user
        other_participants = await self.get_other_participants()
        for username in other_participants:
            status = "online" if username in ONLINE_USERS.get(self.room_group_name, set()) else "offline"
            await self.send(text_data=json.dumps({
                "type": "status",
                "username": username,
                "status": status
            }))

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            if self.room_group_name in ONLINE_USERS:
                ONLINE_USERS[self.room_group_name].discard(self.user.username)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_status", "username": self.user.username, "status": "offline"}
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))

    @database_sync_to_async
    def is_user_participant(self):
        return Conversation.objects.filter(
            id=self.conversation_id,
            participants=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, message):
        conversation = Conversation.objects.get(id=self.conversation_id)
        Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=message
        )

    @database_sync_to_async
    def get_other_participants(self):
        conversation = Conversation.objects.get(id=self.conversation_id)
        return list(conversation.participants.exclude(id=self.user.id).values_list('username', flat=True))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "username": event["username"],
            "status": event["status"]
        }))