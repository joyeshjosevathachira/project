from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from cart.cart import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .forms import OrderCreateForm


# ---------------------------------------------------------------------------
# Server-rendered checkout flow (uses the session cart)
# ---------------------------------------------------------------------------
@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                product = item['product']
                product.stock = max(product.stock - item['quantity'], 0)
                product.save(update_fields=['stock'])
            cart.clear()
            return render(request, 'orders/order_success.html', {'order': order})
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = OrderCreateForm(initial=initial)

    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'orders/order_history.html', {'orders': orders})


# ---------------------------------------------------------------------------
# REST API viewset (full CRUD, scoped to the authenticated user)
# ---------------------------------------------------------------------------
class OrderViewSet(viewsets.ModelViewSet):
    """
    Authenticated users can list/retrieve/create/update/cancel their own orders.
    Staff users can see and manage all orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related('items__product')
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in [Order.STATUS_SHIPPED, Order.STATUS_DELIVERED]:
            return Response(
                {'detail': 'Cannot cancel an order that has already shipped.'}, status=400
            )
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])
        return Response(self.get_serializer(order).data)
