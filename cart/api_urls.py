from django.urls import path
from .api_views import CartAPIView, CartItemAPIView

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='api_cart_detail'),
    path('cart/items/<int:product_id>/', CartItemAPIView.as_view(), name='api_cart_item'),
]
