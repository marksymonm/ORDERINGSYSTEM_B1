# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Checkout
import json
from urllib.parse import parse_qs

# -----------------------
# Print Consumer
# -----------------------
class PrintConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("printers", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("printers", self.channel_name)

    async def send_print_job(self, event):
        await self.send(text_data=json.dumps(event["data"]))


# -----------------------
# Notification Consumer (Owner)
# -----------------------
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.channel_layer.group_add("notifications", self.channel_name)
            await self.accept()

            # Async DB query with fail-safe
            try:
                data = await self.get_counts()
            except Exception as e:
                data = {"pending_count": 0, "unseen_count": 0}
                print(f"[NotificationConsumer] get_counts error: {e}")

            await self.send(text_data=json.dumps({
                'type': 'send_notification',
                'count': data["unseen_count"],
                'dashboard_count': data["pending_count"]
            }))
        except Exception as e:
            print(f"[NotificationConsumer] Connect error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def send_pending_count(self, event):
        await self.send(text_data=json.dumps({
            'type': 'send_notification',
            'count': event.get('unseen_count', 0),
            'dashboard_count': event['pending_count']
        }))

    @sync_to_async
    def get_counts(self):
        return {
            "pending_count": Checkout.objects.filter(status="pending").values("order_code").distinct().count(),
            "unseen_count": Checkout.objects.filter(status="pending", is_seen_by_owner=False).values("order_code").distinct().count()
        }

    # Safe no-op handlers
    async def delivery_fee_response(self, event):
        print(f"[NotificationConsumer] Ignoring delivery_fee_response: {event}")

    async def delivery_fee_rejected(self, event):
        print(f"[NotificationConsumer] Ignoring delivery_fee_rejected: {event}")


# -----------------------
# Customer Notification Consumer
# -----------------------
class CustomerNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            query_params = parse_qs(self.scope['query_string'].decode())
            raw_email = query_params.get('email', [None])[0]
            if not raw_email:
                await self.close()
                return

            self.email = raw_email
            self.group_name = f"customer_{self.sanitize_email(raw_email)}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            try:
                count = await self.get_customer_notification_count()
            except Exception:
                count = 0

            await self.send(text_data=json.dumps({
                'type': 'send_customer_notification',
                'customer_count': count
            }))
        except Exception as e:
            print(f"[CustomerNotificationConsumer] Connect error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_customer_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'send_customer_notification',
            'message': event['message'],
            'customer_count': event['customer_count'],
        }))

    @sync_to_async
    def get_customer_notification_count(self):
        return Checkout.objects.filter(
            email=self.email,
            status__in=["accepted", "rejected", "Preparing", "Packed", "Ready for Pickup", "Out for Delivery", "Completed"],
            is_seen_by_customer=False
        ).values("order_code").distinct().count()

    async def delivery_fee_response(self, event):
        pass  # safe no-op

    async def delivery_fee_rejected(self, event):
        pass  # safe no-op

    def sanitize_email(self, email):
        return email.replace('@', '_at_').replace('.', '_dot_')


# -----------------------
# Delivery Fee Consumers (Owner & Customer)
# -----------------------
class DeliveryFeeOwnerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("owners", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("owners", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "send_fee":
            customer_group = f"customer_{self.sanitize_email(data['customer_email'])}"
            await self.channel_layer.group_send(
                customer_group,
                {"type": "delivery_fee_response", "delivery_fee": data["delivery_fee"]}
            )
        elif data.get("action") == "reject_fee":
            customer_group = f"customer_{self.sanitize_email(data['customer_email'])}"
            await self.channel_layer.group_send(
                customer_group,
                {"type": "delivery_fee_rejected", "reason": data.get("reason", "Rejected")}
            )

    async def delivery_fee_request(self, event):
        await self.send(text_data=json.dumps({
            "type": "delivery_fee_request",
            "customer_email": event["customer_email"],
            "order_details": event["order_details"],
        }))

    async def delivery_fee_rejected(self, event):
        pass  # safe no-op

    def sanitize_email(self, email):
        return email.replace('@', '_at_').replace('.', '_dot_')


class DeliveryFeeCustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope['query_string'].decode())
        self.customer_email = query_params.get('email', [None])[0]
        if not self.customer_email:
            await self.close()
            return

        self.group_name = f"customer_{self.sanitize_email(self.customer_email)}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "request_fee":
            await self.channel_layer.group_send(
                "owners",
                {"type": "delivery_fee_request", "customer_email": data["customer_email"], "order_details": data["order_details"]}
            )

    async def delivery_fee_response(self, event):
        await self.send(text_data=json.dumps({
            "type": "delivery_fee_response",
            "delivery_fee": event["delivery_fee"],
        }))

    async def delivery_fee_rejected(self, event):
        await self.send(text_data=json.dumps({
            "type": "delivery_fee_rejected",
            "reason": event["reason"],
        }))

    def sanitize_email(self, email):
        return email.replace('@', '_at_').replace('.', '_dot_')
