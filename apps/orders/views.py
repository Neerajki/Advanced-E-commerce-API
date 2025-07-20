# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from django.db import transaction
# from django.shortcuts import get_object_or_404
# from django.core.cache import cache
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# from .models import Cart, CartItem, Order, OrderItem
# from .serializers import CartSerializer, OrderSerializer
# from apps.products.models import Product


# # 🔔 Utility: Send WebSocket Notification
# def send_order_notification(user_id: int, message: str):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         f"user_{user_id}",  # User-specific group
#         {
#             "type": "order.status",  # Maps to method `order_status` in consumer
#             "message": message,
#         }
#     )
#     print(f"📢 WebSocket: Sent to user_{user_id} → {message}")


# # 🛒 View Cart
# class CartView(generics.RetrieveAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         user_id = self.request.user.id
#         cache_key = f"cart_{user_id}"
#         cached_cart = cache.get(cache_key)

#         if cached_cart:
#             print(f"✅ Cache HIT: Cart for user {user_id}")
#             return cached_cart

#         cart, _ = Cart.objects.prefetch_related('items__product').get_or_create(user=self.request.user)
#         serialized_cart = CartSerializer(cart).data
#         cache.set(cache_key, serialized_cart, timeout=300)  # Cache for 5 mins
#         print(f"📦 Cache MISS: Fetched Cart for user {user_id}")
#         return serialized_cart


# # 🛒 Add Item to Cart
# class AddToCartView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         product_id = request.data.get('product_id')
#         quantity = int(request.data.get('quantity', 1))

#         product = get_object_or_404(Product, id=product_id)
#         cart, _ = Cart.objects.get_or_create(user=request.user)
#         cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
#         cart_item.quantity += quantity
#         cart_item.save()

#         # Invalidate cart cache
#         cache.delete(f"cart_{request.user.id}")
#         print(f"🗑️ Cleared cart cache for user {request.user.id}")

#         return Response({"message": "Product added to cart"}, status=status.HTTP_201_CREATED)


# # 🛒 Remove Item from Cart
# class RemoveFromCartView(generics.DestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def delete(self, request, *args, **kwargs):
#         product_id = request.data.get('product_id')
#         cart = get_object_or_404(Cart, user=request.user)
#         cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
#         cart_item.delete()

#         # Invalidate cart cache
#         cache.delete(f"cart_{request.user.id}")
#         print(f"🗑️ Cleared cart cache for user {request.user.id}")

#         return Response({"message": "Product removed from cart"}, status=status.HTTP_204_NO_CONTENT)


# # 📦 Place Order from Cart
# class PlaceOrderView(generics.CreateAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         cart = get_object_or_404(Cart.objects.prefetch_related('items__product'), user=request.user)
#         if not cart.items.exists():
#             return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

#         total_price = 0
#         order = Order.objects.create(user=request.user)

#         for item in cart.items.all():
#             product = item.product
#             if product.stock < item.quantity:
#                 transaction.set_rollback(True)
#                 return Response(
#                     {"error": f"Insufficient stock for {product.name}"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             product.stock -= item.quantity
#             product.save()

#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=item.quantity
#             )
#             total_price += product.price * item.quantity

#         order.total_price = total_price
#         order.save()

#         # Clear cart and cache
#         cart.items.all().delete()
#         cache.delete(f"cart_{request.user.id}")
#         print(f"🗑️ Cleared cart and cache after placing order for user {request.user.id}")

#         # Send WebSocket notification
#         send_order_notification(request.user.id, f"Order #{order.id} placed successfully!")

#         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# # 🚚 Admin: Update Order Status
# class OrderUpdateStatusView(generics.UpdateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAdminUser]
#     lookup_field = 'id'

#     def patch(self, request, *args, **kwargs):
#         order = self.get_object()
#         new_status = request.data.get('status')

#         if new_status not in dict(Order.STATUS_CHOICES):
#             return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

#         order.status = new_status
#         order.save()

#         # Notify user via WebSocket
#         send_order_notification(order.user.id, f"Order #{order.id} status updated to {order.status}")

#         return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)




from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .utilts import send_order_notification  # ✅ Import notification util

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer
from apps.products.models import Product


# 🔔 Utility: Send WebSocket Notification
def send_order_notification(user_id: int, message: str):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "order.status", "message": message}
    )
    print(f"📢 WebSocket: Sent to user_{user_id} → {message}")


# 🛒 View Cart
class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.request.user.id
        cache_key = f"cart_{user_id}"

        # Try to fetch from cache
        cached_cart = cache.get(cache_key)
        if cached_cart:
            print(f"✅ Cache HIT: Cart for user {user_id}")
            return cached_cart  # ✅ Return Cart model instance

        # Fetch from DB and prefetch related objects
        cart, _ = Cart.objects.prefetch_related('items__product').get_or_create(user=self.request.user)
        cache.set(cache_key, cart, timeout=300)  # ✅ Cache the model
        print(f"📦 Cache MISS: Fetched Cart for user {user_id}")
        return cart



# 🛒 Add Item to Cart
class AddToCartView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        cart_item.quantity += quantity
        cart_item.save()

        # Invalidate cart cache
        cache.delete(f"cart_{request.user.id}")
        print(f"🗑️ Cleared cart cache for user {request.user.id}")

        action = "added" if created else "updated"
        return Response({"message": f"Product {action} in cart successfully"}, status=status.HTTP_201_CREATED)


# 🛒 Remove Item from Cart
class RemoveFromCartView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()

        # Invalidate cart cache
        cache.delete(f"cart_{request.user.id}")
        print(f"🗑️ Cleared cart cache for user {request.user.id}")

        return Response({"message": "Product removed from cart"}, status=status.HTTP_204_NO_CONTENT)


# 📦 Place Order from Cart
class PlaceOrderView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(
            Cart.objects.prefetch_related('items__product'), user=user
        )

        if not cart.items.exists():
            return Response(
                {"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )

        total_price = 0
        order = Order.objects.create(user=user)

        for item in cart.items.all():
            product = item.product
            if product.stock < item.quantity:
                transaction.set_rollback(True)
                return Response(
                    {"error": f"❌ Insufficient stock for {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deduct stock
            product.stock -= item.quantity
            product.save(update_fields=['stock'])

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity
            )
            total_price += product.price * item.quantity

        order.total_price = total_price
        order.save(update_fields=['total_price'])

        # Clear cart & cache
        cart.items.all().delete()
        cache.delete(f"cart_{user.id}")
        print(f"🗑️ Cleared cart & cache for user {user.id}")

        # 🔥 Send real-time WebSocket notification
        send_order_notification(
            user.id,
            f"🎉 Order #{order.id} placed successfully! Total: ₹{total_price}"
        )

        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED
        )

# 🚚 Admin: Update Order Status
# apps/orders/views.py
class OrderUpdateStatusView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"error": "❌ Invalid status choice."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update order status
        order.status = new_status
        order.save(update_fields=['status'])

        # 🔥 Notify user via WebSocket
        send_order_notification(
            order.user.id,
            f"📦 Order #{order.id} status updated to: {order.status}"
        )

        return Response(
            OrderSerializer(order).data, status=status.HTTP_200_OK
        )



class UserOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
