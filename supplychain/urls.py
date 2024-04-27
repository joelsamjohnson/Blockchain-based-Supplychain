from django.urls import path
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('register/', add_entity, name='register_roles'),
    path('register-url/', register, name='register_url'),
    path('admin-home/', admin_home_page, name='admin_home'),
    path('user-home/', user_home_page, name='user_home'),
    path('product-details/', product_details_initial, name='product_details_initial'),
    path('show-product-details/<int:product_id>/', show_product_details, name='show_product_details'),
    path('add-product/', add_product, name='add_product'),
    path('supply/', supply, name='supply'),
    path('manage/', manage, name='manage'),
    path('track/', track_product, name='track'),
    path('customer-home', ecommerce, name='ecommerce')
]