from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import product_list

urlpatterns = [
    path('admin/', admin.site.urls),

    # Convenience alias so `redirect('home')` / LOGIN_REDIRECT_URL work
    path('', product_list, name='home'),

    # Server-rendered app
    path('', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),

    # REST API (versioned under /api/v1/)
    path('api/v1/', include('products.api_urls')),
    path('api/v1/', include('orders.api_urls')),
    path('api/v1/', include('cart.api_urls')),
    path('api/v1/', include('accounts.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
