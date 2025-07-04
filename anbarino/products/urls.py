from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.view, name='index'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart_finalize' , views.cart_finalize, name='cart_finalize'),
    path('damaged/', views.damaged_view, name='damaged_view'),
    path('damaged_finalize/', views.damaged_finalize, name='damaged_finalize'),
    path('returned_finalize/', views.returned_finalize, name='returned_finalize'),
    path('returned/', views.returned_view, name='returned_view'),
    path('orders/', views.orders_view, name='orders_view'),
    path('orders/start_returned/', views.start_returned_request, name='start_returned_request'),
    path('orders/start_damaged/', views.start_damaged_request, name='start_damaged_request'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
