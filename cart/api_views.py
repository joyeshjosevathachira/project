from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from products.models import Product
from .cart import Cart


class CartAPIView(APIView):
    """
    GET    /api/v1/cart/              -> view current session cart
    POST   /api/v1/cart/               -> add a product {product_id, quantity, override}
    DELETE /api/v1/cart/               -> clear the whole cart
    """
    permission_classes = [permissions.AllowAny]  # cart works for anonymous sessions too

    def get(self, request):
        cart = Cart(request)
        return Response(cart.as_dict())

    def post(self, request):
        cart = Cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        override = bool(request.data.get('override', False))

        if not product_id:
            return Response({'detail': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        if quantity < 1:
            return Response({'detail': 'quantity must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)

        cart.add(product=product, quantity=quantity, override_quantity=override)
        return Response(cart.as_dict(), status=status.HTTP_201_CREATED)

    def delete(self, request):
        cart = Cart(request)
        cart.clear()
        return Response({'detail': 'Cart cleared.'}, status=status.HTTP_204_NO_CONTENT)


class CartItemAPIView(APIView):
    """
    PUT/PATCH /api/v1/cart/items/<product_id>/  -> update quantity of a single item
    DELETE    /api/v1/cart/items/<product_id>/  -> remove a single item
    """
    permission_classes = [permissions.AllowAny]

    def put(self, request, product_id):
        return self._update(request, product_id)

    def patch(self, request, product_id):
        return self._update(request, product_id)

    def _update(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.data.get('quantity', 1))
        if quantity < 1:
            return Response({'detail': 'quantity must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)
        cart.add(product=product, quantity=quantity, override_quantity=True)
        return Response(cart.as_dict())

    def delete(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return Response(cart.as_dict())
