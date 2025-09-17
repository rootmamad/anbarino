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
    path('product/<int:pk>/', views.get_product, name='get_product'),
    path('orders/start_purchase/', views.start_purchase, name='start_purchase_request'),
    path('products/', views.product_list, name='product_list'),
    path('check/', views.inventory_check, name='inventory_check'),
    path('api/search/', views.search_products),
    path('api/reindex/', views.index_all),
    path("damaged/action/<int:item_id>/", views.damaged_action, name="damaged_action"),
    path("approvals/", views.admin_approvals, name="admin_approvals"),
    path("return/action/<int:item_id>/", views.return_action, name="return_action"),
    path("purchase/action/<int:item_id>/", views.purchase_action, name="purchase_action"),
    path("add/", views.add_product, name="add_product"),
    path("help/", views.help_, name="help"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("search/", views.search_results, name="search_results"),
    path("add-balance/", views.add_balance_view, name="add_balance"),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
