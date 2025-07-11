from unicodedata import name
from django.urls import path
from App import views
from django.contrib.auth.views import LogoutView
from .views import order_product, reserve_product, cancel_order, cancel_reservation

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
    path('commander/', order_product, name='order_product'),
    path('reserver/', reserve_product, name='reserve_product'),
    path('annuler_commande/', cancel_order, name='cancel_order'),
    path('annuler_reservation/', cancel_reservation, name='cancel_reservation'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/medicaments-populaires/', views.medicaments_populaires_api, name='api_medicaments_populaires'),
]