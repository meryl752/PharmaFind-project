from django.shortcuts import render, redirect
from .models import City
from .models import User
from .models import District
from .models import Product, Category, Insurance
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .form import UserForm
from .form import LoginForm
from .form import SearchForm
from .form import PharmacyLoginForm
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .models import PharmacyProduct
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order, Reservation
from django.db.models import Count
import random
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Cart, CartItem, Product
from django.contrib.auth import logout as django_logout
from django.utils import timezone
from django.core.files.storage import default_storage
import json




# create your views here 

def index3(request):
    return render(request, "App/Inscription.html")

def index(request):
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'pharmacy':
        return redirect('pharmacy_dashboard')
    categories = Category.objects.all()
    pharmacies = []
    if request.user.is_authenticated:
        user_city = request.user.city
        user_quartier = request.user.address
        pharmacies = User.objects.filter(
            role='pharmacy'
        ).filter(
            Q(city=user_city) | Q(address=user_quartier)
        )
    # Tous les produits pour l'affichage progressif (voir plus)
    popular_products = list(Product.objects.filter(category__name="Cosmétiques et hygiene de la peau"))
    # Compléter avec None si moins de 4 produits pour l'affichage initial
    popular_products_serialized = []
    for p in popular_products:
        popular_products_serialized.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'photo': p.photo.url if p.photo else '',
            'description': p.description,
            'category_name': p.category.name if p.category else '',
            'with_ordonance': p.with_ordonance,
        })
    initial_products = popular_products_serialized[:4]
    while len(initial_products) < 4:
        initial_products.append(None)
    # Récupérer 3 produits aléatoires de la catégorie Cosmétique et hygiène de la peau pour la section showcase
    cosmetic_products_qs = Product.objects.filter(category__name="Cosmétique et hygiene de la peau")
    cosmetic_products = list(cosmetic_products_qs)
    random.shuffle(cosmetic_products)
    cosmetic_showcase_products = cosmetic_products[:3]
    return render(request, "App/Index.html", {
        "categories": categories,
        "pharmacies": pharmacies,
        "popular_products": popular_products_serialized,
        "initial_products": initial_products,
        "cosmetic_showcase_products": cosmetic_showcase_products
    })

def index1(request):
    return render(request, "header2.html")

def search_results(request):
    return render(request, "App/Resultats_recherches.html")

def Reservations(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    reservations = Reservation.objects.filter(customer=request.user).order_by('-reservation_date')
    if request.GET.get('modal') == '1':
        return render(request, "App/_reservations_modal.html", { 'reservations': reservations })
    return render(request, "App/Réservations.html", { 'reservations': reservations })

def Orders(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    orders = Order.objects.filter(customer=request.user).order_by('-order_date')
    if request.GET.get('modal') == '1':
        return render(request, "App/_orders_modal.html", { 'orders': orders })
    return render(request, "App/orders.html", { 'orders': orders })

def Profil(request):
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'pharmacy':
        return redirect('pharmacy_dashboard')
    return render(request, "App/profil.html")

def new(request):
    return render(request, "App/new.html")

def welcome(request):
    return render(request, "App/Acceuil.html")






def Results(request):
    return render(request, "App/Resultats_recherches.html")

def login_view(request):
    # Si la méthode est POST → traitement
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            try: 
                user = User.objects.get(email=email)    
                user = authenticate(request, username=user.username, password=password)    

                if user is not None:
                    login(request, user)
                    messages.success(request, "Connexion réussie !")
                    firstname = user.first_name
                    return redirect('home')  # Vérifie l'orthographe dans urls.py
                else:
                    form.add_error(None, "mot de passe invalide !")
            except User.DoesNotExist:
                form.add_error(None, "Aucun utilisateur trouvé à cette adressse !")        
        else: 
            print('erreur:',request.POST)   
         
        # Affiche le formulaire avec erreurs
        return render(request, 'App/connexion.html', {'form': form})

    else:
        # GET request → afficher formulaire vide
        form = LoginForm()
    return render(request, 'App/connexion.html', {'form': form})



def UserCreate(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur bien enrégistré ")
            return redirect('home')
    else:
        form = UserForm()
    return render(request, 'App/Ins.html', {'form': form})    



def search(request):
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie')
    products = Product.objects.all()
    pharmacies_trouvees = []
    products_with_pharmacies = []
    user = request.user if request.user.is_authenticated else None

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        pharmacies_trouvees = User.objects.filter(role='pharmacy').filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(city__name__icontains=query) |
            Q(address__name__icontains=query)
        ).distinct()
    if categorie_id:
        products = products.filter(category_id=categorie_id)

    from .models import Order, OrderItem, Reservation, ReservationItem, PharmacyProduct

    # Nouvelle structure : une card par produit ET par pharmacie
    for product in products:
        pharmacies_stock = PharmacyProduct.objects.filter(product=product, quantity__gt=0)
        if pharmacies_stock.exists():
            for ps in pharmacies_stock:
                info = {
                    'product': product,
                    'pharmacy': ps.pharmacy,
                    'stock': ps.quantity,
                    'address': str(ps.pharmacy.address),
                    'city': str(ps.pharmacy.city),
                    'has_pending_order': False,
                    'has_pending_reservation': False
                }
                if user:
                    order = Order.objects.filter(customer=user, pharmacy=ps.pharmacy, status='pending').first()
                    if order and OrderItem.objects.filter(order=order, product=product).exists():
                        info['has_pending_order'] = True
                    reservation = Reservation.objects.filter(customer=user, pharmacy=ps.pharmacy, status='pending').first()
                    if reservation and ReservationItem.objects.filter(reservation=reservation, product=product).exists():
                        info['has_pending_reservation'] = True
                products_with_pharmacies.append(info)
        else:
            # Produit sans stock dans aucune pharmacie
            info = {
                'product': product,
                'pharmacy': None,
                'stock': 0,
                'address': '',
                'city': '',
                'has_pending_order': False,
                'has_pending_reservation': False,
                'out_of_stock': True
            }
            products_with_pharmacies.append(info)

    context = {
        'products': products,
        'products_with_pharmacies': products_with_pharmacies,
        'pharmacies_trouvees': pharmacies_trouvees,
        'query': query,
        'results_count': products.count(),
        'pharmacies_count': len(pharmacies_trouvees),
        'categories': Category.objects.all(),
        'selected_categorie': categorie_id,
    }
    return render(request, 'App/Resultats_recherches.html', context)



def pharma_connection_view(request):
        return render(request, "App/Pharma_connexion.html")


def pharma_dashboard_view(request):
    user = request.user
    pharmacy_fullname = f"{user.first_name} {user.last_name}" if user.role == 'pharmacy' else ''
    pharmacy_photo = user.photo.url if user.role == 'pharmacy' and user.photo else None
    # Présence en ligne : last_seen dans les 5 dernières minutes
    is_online = False
    if user.role == 'pharmacy' and user.last_seen:
        now = timezone.now()
        delta = now - user.last_seen
        is_online = delta.total_seconds() < 300  # 5 minutes
    # Récupérer les produits en stock pour cette pharmacie
    stock = PharmacyProduct.objects.filter(pharmacy=user).select_related('product', 'product__category')
    # Récupérer tous les produits pour la sélection dans la modale
    all_products = Product.objects.all()
    return render(request, "App/dashboard_pharma.html", {
        'pharmacy_fullname': pharmacy_fullname,
        'pharmacy_photo': pharmacy_photo,
        'is_online': is_online,
        'stock': stock,
        'all_products': all_products,
    })

def pharmacy_login_view(request):
    if request.method == 'POST':
        form = PharmacyLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    if user.role == 'pharmacy':
                        login(request, user)
                        return redirect('pharmacy_dashboard')
                    else:
                        form.add_error(None, "Ce compte n'est pas une pharmacie.")
                else:
                    form.add_error(None, "Mot de passe invalide !")
            except User.DoesNotExist:
                form.add_error(None, "Aucun utilisateur trouvé à cette adresse !")
        return render(request, 'App/Pharma_connexion.html', {'form': form})
    else:
        form = PharmacyLoginForm()
    return render(request, 'App/Pharma_connexion.html', {'form': form})

def search_fragment(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=403)
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie')
    products = Product.objects.all()
    pharmacies_trouvees = []
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        pharmacies_trouvees = User.objects.filter(role='pharmacy').filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(city__name__icontains=query) |
            Q(address__name__icontains=query)
        ).distinct()
    if categorie_id:
        products = products.filter(category_id=categorie_id)
    context = {
        'products': products,
        'pharmacies_trouvees': pharmacies_trouvees,
        'query': query,
        'results_count': products.count(),
        'pharmacies_count': len(pharmacies_trouvees),
        'categories': Category.objects.all(),
        'selected_categorie': categorie_id,
    }
    html = render_to_string('App/_search_results.html', context, request=request)
    return HttpResponse(html)

@csrf_exempt
@require_POST
def order_product(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentification requise.'}, status=403)
    try:
        product_id = int(request.POST.get('produit_id'))
        pharmacy_id = int(request.POST.get('pharmacie_id'))
        quantite = int(request.POST.get('quantite'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Paramètres invalides.'}, status=400)
    from .models import Product, User, PharmacyProduct, Order, OrderItem
    try:
        product = Product.objects.get(id=product_id)
        pharmacy = User.objects.get(id=pharmacy_id, role='pharmacy')
        stock = PharmacyProduct.objects.get(product=product, pharmacy=pharmacy)
    except (Product.DoesNotExist, User.DoesNotExist, PharmacyProduct.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Produit ou pharmacie introuvable.'}, status=404)
    if stock.quantity < quantite:
        return JsonResponse({'success': False, 'error': 'Stock insuffisant.'}, status=400)
    # Créer la commande
    order = Order.objects.create(customer=user, pharmacy=pharmacy, status='pending')
    OrderItem.objects.create(order=order, product=product, quantity=quantite, price=product.price)
    # Mettre à jour le stock
    stock.quantity -= quantite
    stock.save()
    return JsonResponse({'success': True, 'message': 'Commande enregistrée.'})

@csrf_exempt
@require_POST
def reserve_product(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentification requise.'}, status=403)
    try:
        product_id = int(request.POST.get('produit_id'))
        pharmacy_id = int(request.POST.get('pharmacie_id'))
        quantite = int(request.POST.get('quantite'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Paramètres invalides.'}, status=400)
    from .models import Product, User, PharmacyProduct, Reservation, ReservationItem
    try:
        product = Product.objects.get(id=product_id)
        pharmacy = User.objects.get(id=pharmacy_id, role='pharmacy')
        stock = PharmacyProduct.objects.get(product=product, pharmacy=pharmacy)
    except (Product.DoesNotExist, User.DoesNotExist, PharmacyProduct.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Produit ou pharmacie introuvable.'}, status=404)
    if stock.quantity < quantite:
        return JsonResponse({'success': False, 'error': 'Stock insuffisant.'}, status=400)
    # Créer la réservation
    reservation = Reservation.objects.create(customer=user, pharmacy=pharmacy, status='pending')
    ReservationItem.objects.create(reservation=reservation, product=product, quantity=quantite)
    # Mettre à jour le stock
    stock.quantity -= quantite
    stock.save()
    return JsonResponse({'success': True, 'message': 'Réservation enregistrée.'})

@csrf_exempt
@require_POST
def cancel_order(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentification requise.'}, status=403)
    try:
        product_id = int(request.POST.get('produit_id'))
        pharmacy_id = int(request.POST.get('pharmacie_id'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Paramètres invalides.'}, status=400)
    from .models import Product, User, PharmacyProduct, Order, OrderItem
    try:
        product = Product.objects.get(id=product_id)
        pharmacy = User.objects.get(id=pharmacy_id, role='pharmacy')
        order = Order.objects.filter(customer=user, pharmacy=pharmacy, status='pending').order_by('-order_date').first()
        if not order:
            return JsonResponse({'success': False, 'error': 'Commande non trouvée.'}, status=404)
        order_item = OrderItem.objects.get(order=order, product=product)
        # Rétablir le stock
        stock = PharmacyProduct.objects.get(product=product, pharmacy=pharmacy)
        stock.quantity += order_item.quantity
        stock.save()
        order_item.delete()
        order.delete()
        return JsonResponse({'success': True, 'message': 'Commande annulée.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def cancel_reservation(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentification requise.'}, status=403)
    try:
        product_id = int(request.POST.get('produit_id'))
        pharmacy_id = int(request.POST.get('pharmacie_id'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Paramètres invalides.'}, status=400)
    from .models import Product, User, PharmacyProduct, Reservation, ReservationItem
    try:
        product = Product.objects.get(id=product_id)
        pharmacy = User.objects.get(id=pharmacy_id, role='pharmacy')
        reservation = Reservation.objects.filter(customer=user, pharmacy=pharmacy, status='pending').order_by('-reservation_date').first()
        if not reservation:
            return JsonResponse({'success': False, 'error': 'Réservation non trouvée.'}, status=404)
        reservation_item = ReservationItem.objects.get(reservation=reservation, product=product)
        # Rétablir le stock
        stock = PharmacyProduct.objects.get(product=product, pharmacy=pharmacy)
        stock.quantity += reservation_item.quantity
        stock.save()
        reservation_item.delete()
        reservation.delete()
        return JsonResponse({'success': True, 'message': 'Réservation annulée.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def notifications(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    # Placeholder : à remplacer par la vraie logique de notifications plus tard
    return render(request, "App/notifications.html")

def medicaments_populaires_api(request):
    produits = list(Product.objects.all())
    random.shuffle(produits)
    selection = produits[:4]
    data = []
    for prod in selection:
        data.append({
            'id': prod.id,
            'name': prod.name,
            'photo_url': prod.photo.url if prod.photo else '',
            'price': float(prod.price),
            'description': prod.description,
        })
    return JsonResponse({'produits': data})

def commandes_partial(request):
    return render(request, 'App/commandes.html')



def produits_partial(request):
    return render(request, 'App/produits.html')

def panier(request):
    if not request.user.is_authenticated:
        return redirect('connexion')
    # À compléter plus tard avec les articles du panier
    return render(request, "App/panier.html")

@require_POST
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=403)
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produit introuvable'}, status=404)
    cart, created = Cart.objects.get_or_create(user=request.user, checked_out=False)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()
    return JsonResponse({'success': True, 'cart_count': cart.items.count()})

def cart_content(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=403)
    cart = Cart.objects.filter(user=request.user, checked_out=False).first()
    items = []
    if cart:
        for item in cart.items.select_related('product'):
            items.append({
                'id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'photo': item.product.photo.url if item.product.photo else '',
            })
    return JsonResponse({'success': True, 'items': items})

@require_POST
def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=403)
    product_id = request.POST.get('product_id')
    cart = Cart.objects.filter(user=request.user, checked_out=False).first()
    if not cart:
        return JsonResponse({'success': False, 'error': 'Aucun panier actif'}, status=404)
    try:
        item = CartItem.objects.get(cart=cart, product_id=product_id)
        item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produit non trouvé dans le panier'}, status=404)

def custom_logout(request):
    django_logout(request)
    return redirect('home')

@csrf_exempt
def add_product_ajax(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            price = request.POST.get('price')
            category_name = request.POST.get('category')
            description = request.POST.get('description', '')
            with_ordonance = request.POST.get('with_ordonance') == 'on'
            insurance_names = request.POST.get('insurance', '')
            photo = request.FILES.get('photo')

            # Catégorie
            category, _ = Category.objects.get_or_create(name=category_name)
            # Produit
            product = Product.objects.create(
                name=name,
                price=price,
                category=category,
                description=description,
                photo=photo,
                with_ordonance=with_ordonance
            )
            # Assurance
            if insurance_names:
                for ins_name in [i.strip() for i in insurance_names.split(',') if i.strip()]:
                    ins, _ = Insurance.objects.get_or_create(name=ins_name)
                    product.insurance.add(ins)
            product.save()
            return JsonResponse({'success': True, 'message': 'Produit créé avec succès.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})

@csrf_exempt
@require_POST
def add_stock_ajax(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'role') or request.user.role != 'pharmacy':
        return JsonResponse({'success': False, 'message': 'Authentification pharmacie requise.'}, status=403)
    try:
        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity'))
        price = float(request.POST.get('price'))
        from .models import Product
        product = Product.objects.get(id=product_id)
        pharmacy = request.user
        # Ajout ou mise à jour du stock
        stock, created = PharmacyProduct.objects.get_or_create(pharmacy=pharmacy, product=product)
        stock.quantity = quantity
        stock.save()
        # Mettre à jour le prix du produit si besoin (optionnel)
        product.price = price
        product.save()
        return JsonResponse({'success': True, 'message': 'Produit ajouté au stock.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def remove_stock_ajax(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'role') or request.user.role != 'pharmacy':
        return JsonResponse({'success': False, 'message': 'Authentification pharmacie requise.'}, status=403)
    try:
        product_id = int(request.POST.get('product_id'))
        from .models import Product, PharmacyProduct
        product = Product.objects.get(id=product_id)
        pharmacy = request.user
        PharmacyProduct.objects.get(pharmacy=pharmacy, product=product).delete()
        return JsonResponse({'success': True, 'message': 'Produit retiré du stock.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
@require_POST
def edit_stock_ajax(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'role') or request.user.role != 'pharmacy':
        return JsonResponse({'success': False, 'message': 'Authentification pharmacie requise.'}, status=403)
    try:
        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity'))
        price = float(request.POST.get('price'))
        from .models import Product, PharmacyProduct
        product = Product.objects.get(id=product_id)
        pharmacy = request.user
        stock = PharmacyProduct.objects.get(pharmacy=pharmacy, product=product)
        stock.quantity = quantity
        stock.save()
        product.price = price
        product.save()
        return JsonResponse({'success': True, 'message': 'Stock modifié.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def pharma_connexion_view(request):
    return render(request, 'App/Pharma_connexion.html')