from django.urls import path
from .views import (
    CartView, AddToCartView, RemoveFromCartView, PlaceOrderView,UserOrdersView,OrderUpdateStatusView
)

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart-detail'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='cart-remove'),
    path('order/place/', PlaceOrderView.as_view(), name='order-place'),
    path('orders/', UserOrdersView.as_view(), name='user-orders'),
    path('orders/<int:id>/status/', OrderUpdateStatusView.as_view(), name='order-update-status'),

]
