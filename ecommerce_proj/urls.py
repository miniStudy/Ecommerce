
from django.contrib import admin
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from ecommerce_customer import urls
from ecommerce_delivery_boy import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ecommerce_app.urls')),
    path('customer/', include('ecommerce_customer.urls')),
    path('delivery/', include('ecommerce_delivery_boy.urls')),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)