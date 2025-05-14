"""
URL configuration for TreeMartTwo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path,include
from.import views


urlpatterns = [
    path('create-tree', views.create_tree, name='create-tree'),
    path('update-tree/<int:t_id>', views.update_tree, name='update-tree'),
    path('delete-tree/<int:t_id>', views.delete_tree, name='delete-tree'),
    path('', views.tree_list, name='tree_list'),

    path('photos/', views.photo_list, name='photo_list'),
    path('photos/upload/', views.photo_upload, name='photo_upload'),
    path('add-to-cart/<int:t_id>/', views.add_to_cart, name='add-to-cart'),
    # path('season/', views.select_season, name='select_season'),
    # path('season/<str:season>/', views.plants_by_season, name='plants_by_season'),
    path('add-to-cart/<int:t_id>/', views.add_to_cart, name='add-to-cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:t_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear-cart'),
    path('cart/increase/<int:t_id>/', views.update_cart_quantity, {'action': 'increase'}, name='cart-increase'),
    path('cart/decrease/<int:t_id>/', views.update_cart_quantity, {'action': 'decrease'}, name='cart-decrease'),
    path('cart/remove/<int:t_id>/', views.update_cart_quantity, {'action': 'remove'}, name='cart-remove'),
    path('', views.tree_list, name='tree_list'),  # Tree list page
    path('rate-tree/', views.rate_tree, name='rate_tree'),


]