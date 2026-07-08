from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Seed the database with sample categories and products.'

    def handle(self, *args, **options):
        categories_data = {
            'Electronics': 'Gadgets, devices and accessories.',
            'Books': 'Fiction, non-fiction and everything in between.',
            'Clothing': 'Apparel for everyone.',
        }
        categories = {}
        for name, desc in categories_data.items():
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories[name] = cat

        products_data = [
            ('Wireless Mouse', 'Electronics', 19.99, 50, 'A smooth, responsive wireless mouse.'),
            ('Mechanical Keyboard', 'Electronics', 79.99, 30, 'Tactile mechanical keyboard with RGB.'),
            ('Noise Cancelling Headphones', 'Electronics', 149.99, 20, 'Over-ear headphones with ANC.'),
            ('The Pragmatic Programmer', 'Books', 34.99, 40, 'A classic guide for software developers.'),
            ('Clean Code', 'Books', 29.99, 35, 'Writing maintainable, readable code.'),
            ('Cotton T-Shirt', 'Clothing', 14.99, 100, 'Soft, breathable everyday t-shirt.'),
            ('Denim Jacket', 'Clothing', 59.99, 25, 'Classic denim jacket for all seasons.'),
        ]

        created = 0
        for name, cat_name, price, stock, description in products_data:
            _, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': categories[cat_name],
                    'price': price,
                    'stock': stock,
                    'description': description,
                    'available': True,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete. {len(categories)} categories ensured, {created} new products created.'
        ))
