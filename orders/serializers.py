from rest_framework import serializers
from products.models import Product
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    cost = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'cost']
        read_only_fields = ['price']

    def get_cost(self, obj):
        return obj.get_cost()


class OrderItemWriteSerializer(serializers.Serializer):
    """Used when creating an order: only needs product id + quantity."""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = OrderItemWriteSerializer(many=True, write_only=True)
    total_cost = serializers.SerializerMethodField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'address',
            'postal_code', 'city', 'status', 'items', 'order_items',
            'total_cost', 'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def get_total_cost(self, obj):
        return obj.get_total_cost()

    def validate_order_items(self, value):
        if not value:
            raise serializers.ValidationError('An order must contain at least one item.')
        for entry in value:
            product = entry['product']
            if entry['quantity'] > product.stock:
                raise serializers.ValidationError(
                    f'Only {product.stock} unit(s) of "{product.name}" are available.'
                )
        return value

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for entry in order_items_data:
            product = entry['product']
            quantity = entry['quantity']
            OrderItem.objects.create(
                order=order, product=product, price=product.price, quantity=quantity
            )
            product.stock = max(product.stock - quantity, 0)
            product.save(update_fields=['stock'])
        return order
