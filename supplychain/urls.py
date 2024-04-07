from django.urls import path
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('register/', add_entity, name='register_roles'),
    path('register-url/', register, name='register_url'),
    path('admin-home/', admin_home_page, name='admin_home'),
    path('user-home/', user_home_page, name='user_home'),
    path('product-stage/', product_stage_initial, name='product_stage_initial'),
    path('show-product-stage/<int:product_id>/', show_product_stage, name='show_product_stage'),
    path('add-product/', add_product, name='add_product'),
    path('supply/', supply, name='supply'),
    path('manage/', manage, name='manage'),
    path('track/', track_product, name='track'),
    path('viewchat/',viewchat,name='view_chat'),
    path('chatuser/',chatuser,name='chatuser'),
    path('chatadmin/<int:user_id>',chatadmin,name='chatadmin'),
    path('addchat_user/',addchat_user,name='addchat_user'),
    path('user-search', user_search,name='user_search'),
    path('chatadmin/addchat_admin',addchat_admin,name='addchat_admin'),

]