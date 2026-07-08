from decimal import Decimal
from django.conf import settings
from products.models import Product
import copy
from decimal import Decimal


class Cart:
    """
    A shopping cart that is persisted entirely in the user's Django session.
    This means the cart survives across requests/page loads for the same
    session without needing a database table, and works for both
    anonymous and authenticated users.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" so Django knows it needs saving
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()


    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        # Deep copy so session data is never modified
        cart = copy.deepcopy(self.cart)

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def as_dict(self):
        """Serializable representation of the cart, useful for the API."""
        items = []
        for product_id, item in self.cart.items():
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue
            price = Decimal(item['price'])
            items.append({
                'product_id': product.id,
                'name': product.name,
                'quantity': item['quantity'],
                'price': str(price),
                'total_price': str(price * item['quantity']),
            })
        return {
            'items': items,
            'total_items': len(self),
            'total_price': str(self.get_total_price()),
        }
