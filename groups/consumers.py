import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Group, GroupMessage

ONLINE_USERS = {}

class GroupChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.room_group_name = f"group_{self.group_id}"

        if not self.user.is_authenticated:
            await self.close()
            return

        is_member = await self.is_user_member()
        if not is_member:
            await self.close()
            return
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()

        if self.room_group_name not in ONLINE_USERS:
            ONLINE_USERS[self.room_group_name] = set()
        ONLINE_USERS[self.room_group_name].add(self.user.username)

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type":"user_status",
             "username": self.user.username,
             "status":"online"}
        )

        other_members = await self.get_other_members()
        for username in other_members:
            status = "online" if username in ONLINE_USERS.get(self.room_group_name, set()) else "offline"
            await self.send(text_data=json.dumps({
                "type":"status",
                "username": username,
                "status": status
            }))

        self.last_pong  = asyncio.get_event_loop().time()
        self.heartbeat_task  = asyncio.create_task(self.send_heartbeat())

    async def send_heartbeat(self):
        try:
            while True:
                await asyncio.sleep(10)
                now  = asyncio.get_event_loop().time()
                if now - self.last_pong > 20:
                    await self.close()
                    break
                await self.send(text_data=json.dumps({"type":"ping"}))
        except Exception:
            pass


    async def disconnect(self, close_code):
        if hasattr(self, "heartbeat_task"):
            self.heartbeat_task.cancel()

        if hasattr(self, "room_group_name"):
            if self.room_group_name in ONLINE_USERS:
                ONLINE_USERS[self.room_group_name].discard(self.user.username)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type":"user_status",
                 "username":self.user.username,
                 "status":"offline"}
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json.get("type") == "pong":
                self.last_pong  =  asyncio.get_event_loop().time()
                return

        if text_data_json.get("type") == "typing":
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type":"typing_indicator",
                     "username": self.user.username,
                     "is_typing": text_data_json.get("is_typing")}
                )
                return
        message = text_data_json["message"]
        await self.save_message(message)

        await self.channel_layer.group_send(
                   self.room_group_name,
                   {"type": "chat_message",
                    "message": message,
                    "sender": self.user.username}
              )

    async def chat_message(self,event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))

    @database_sync_to_async
    def is_user_member(self):
        return Group.objects.filter(
            id=self.group_id,
            members = self.user
        ).exists()
    
    @database_sync_to_async
    def save_message(self,message):
        group = Group.objects.get(id=self.group_id)
        GroupMessage.objects.create(group=group,
                                    sender = self.user,
                                    content=message)

    @database_sync_to_async
    def get_other_members(self):
        group = Group.objects.get(id = self.group_id)
        return list(group.members.exclude(id=self.user.id).values_list('username', flat=True))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type":"status",
            "username": event["username"],
            "status": event["status"]
        }))

    async def typing_indicator(self,event):
        if event["username"] != self.user.username:
            await self.send(text_data=json.dumps({
                "type":"typing",
                "username":event["username"],
                "is_typing":event["is_typing"]
            }))

    
        
            




    