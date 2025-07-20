from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_order_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",  # Group name for that user
        {
            "type": "order_status_update",  # Calls order_status_update in consumer
            "message": message
        }
    )
    print(f"📢 Notification sent to user_{user_id}: {message}")
