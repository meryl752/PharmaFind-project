from unicodedata import name
from django.urls import path
from App import views
from django.contrib.auth.views import LogoutView
from .views import order_product, reserve_product, cancel_order, cancel_reservation, pharma_connexion_view, add_stock_ajax, remove_stock_ajax, edit_stock_ajax

urlpatterns = [
    path('', views.index, name='home'),
    path('connexion', views.login_view, name='connexion'),
    path('Ins', views.UserCreate, name='Ins'),
    path('head', views.index1, name='head'),
    path('reservations', views.Reservations, name='reservations'),
    path('commandes', views.Orders, name='commandes'),
    path('profil', views.Profil, name='profil'),
    path('search/', views.search, name='search'),
    path('reg', views.index3, name='reg'),
    path('welcome', views.welcome, name='welcome'),
    path('pharmacy_connection/', views.pharmacy_login_view, name='pharmacy_connection'),
    path('pharmacy_dashboard/', views.pharma_dashboard_view, name='pharmacy_dashboard'),
    path('pharma_connexion/', pharma_connexion_view, name='pharma_connexion'),
    path('commander/', order_product, name='order_product'),
    path('reserver/', reserve_product, name='reserve_product'),
    path('annuler_commande/', cancel_order, name='cancel_order'),
    path('annuler_reservation/', cancel_reservation, name='cancel_reservation'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/medicaments-populaires/', views.medicaments_populaires_api, name='api_medicaments_populaires'),
    path('commandes_partial/', views.commandes_partial, name='commandes_partial'),
    path('produits_partial/', views.produits_partial, name='produits_partial'),
    path('panier', views.panier, name='panier'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart_content/', views.cart_content, name='cart_content'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('add_product_ajax/', views.add_product_ajax, name='add_product_ajax'),
    path('add_stock_ajax/', add_stock_ajax, name='add_stock_ajax'),
    path('remove_stock_ajax/', remove_stock_ajax, name='remove_stock_ajax'),
    path('edit_stock_ajax/', edit_stock_ajax, name='edit_stock_ajax'),
]