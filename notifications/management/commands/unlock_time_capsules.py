from django.core.management.base import BaseCommand
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chat.models import Message
from groups.models import GroupMessage


class Command(BaseCommand):
    help = "Unlocks Time Capsule messages whose scheduled_at time has arrived"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        channel_layer = get_channel_layer()

        # --- 1-on-1 messages ---
        due_messages = Message.objects.filter(is_unlocked=False, scheduled_at__lte=now)
        for msg in due_messages:
            msg.is_unlocked = True
            msg.save(update_fields=["is_unlocked"])

            room_group_name = f"chat_{msg.conversation_id}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {"type": "chat_message", "message": msg.content, "sender": msg.sender.username}
            )
            self.stdout.write(f"Unlocked Message id={msg.id}")

        # --- Group messages ---
        due_group_messages = GroupMessage.objects.filter(is_unlocked=False, scheduled_at__lte=now)
        for msg in due_group_messages:
            msg.is_unlocked = True
            msg.save(update_fields=["is_unlocked"])

            room_group_name = f"group_{msg.group_id}"
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {"type": "chat_message", "message": msg.content, "sender": msg.sender.username}
            )
            self.stdout.write(f"Unlocked GroupMessage id={msg.id}")

        self.stdout.write(self.style.SUCCESS("Time capsule check complete."))