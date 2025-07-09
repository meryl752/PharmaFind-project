from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"
    


class City(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.name}"
    


class Insurance(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.name}"
    


class District(models.Model):
    name = models.CharField(max_length=25)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="quartiers")
    def __str__(self):
        return f"{self.name} "
    


class Product(models.Model):
    name = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(max_length=200, blank=True)  # Sans default bizarre
    photo = models.ImageField(upload_to='products/')
    with_ordonance = models.BooleanField(default=False)
    insurance = models.ManyToManyField(Insurance,  related_name="product")

    def __str__(self):
        return f"{self.name}"
    


class User(AbstractUser):
    tel = models.CharField(max_length=15)
    address = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    sexe = models.CharField(
        max_length=1,
        choices=[('M', 'Masculin'), ('F', 'Feminin')],
        blank=True, null=True
    )
    role = models.CharField(
        max_length=10,
        choices=[
            ('customer', 'Customer'),
            ('pharmacy', 'Pharmacy')
        ],
        default='customer'
    )
    opening_hours = models.TimeField(null=True, blank=True)
    closing_hours = models.TimeField(null=True, blank=True)
    insurance_covered = models.ManyToManyField(Insurance, blank=True, related_name="pharmacies")
    photo = models.ImageField(upload_to='pharmacies/', null=True, blank=True)
    is_on_duty = models.BooleanField(default=False, verbose_name="Pharmacie de garde")

    class Meta:
        verbose_name = " user"
        verbose_name_plural = " users"

        
    def is_open(self):
        now = timezone.localtime().time()
        if self.opening_hours and self.closing_hours:
            if self.opening_hours < self.closing_hours:
                return self.opening_hours <= now <= self.closing_hours
            else:
                return now >= self.opening_hours or now <= self.closing_hours
        return False

    def is_customer(self):
        return self.role == 'customer'

    def is_pharmacy(self):
        return self.role == 'pharmacy'
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    



    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_made')
    pharmacy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_received')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'pending'), ('confirmed', 'confirmed')],
        default='pending'
    )

    def clean(self):
        if self.customer.role != 'customer':
            raise ValidationError("Le champ 'customer' doit référencer un utilisateur ayant le rôle 'customer'.")
        if self.pharmacy.role != 'pharmacy':
            raise ValidationError("Le champ 'pharmacy' doit référencer un utilisateur ayant le rôle 'pharmacy'.")
        

        

class Reservation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations_made')
    pharmacy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations_received')
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'pending'), ('confirmed', 'confirmed')],
        default='pending'
    )

class ReservationItem(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)    

class PharmacyProduct(models.Model):
    pharmacy = models.ForeignKey('User', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('pharmacy', 'product')

    def __str__(self):
        return f"{self.pharmacy} - {self.product} : {self.quantity} en stock"    