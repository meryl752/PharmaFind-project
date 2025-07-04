from django.contrib import admin
from .models import Product
from .models import Insurance
from .models import Category
from .models import User
from .models import City
from .models import District
from .models import PharmacyProduct
from .models import Order, OrderItem, Reservation, ReservationItem
 
# Register your models hee.
class AdminProduct(admin.ModelAdmin):
    list_display = ('name','price', 'category', 'description', 'photo', 'with_ordonance', 'get_insurances')
    def get_insurances(self, obj):
        return ", ".join([i.name for i in obj.insurance.all()])
    get_insurances.short_description = "Assurances"

admin.site.register(Product, AdminProduct)

class AdminInsurance(admin.ModelAdmin):
    list_display = ('name' )

admin.site.register(Insurance)

class AdminCategory(admin.ModelAdmin):
    list_display = ('name')

admin.site.register(Category)

class AdminUser(admin.ModelAdmin):
    list_display = ('tel','address','email','city', 'sexe','role','opening_hours','closing_hours', 'get_insurance_covered')
    def get_insurance_covered(self, obj):
        return ", ".join([i.name for i in obj.insurance_covered.all()])
    get_insurance_covered.short_description = "Assurances couvertes"

admin.site.register(User, AdminUser)


class AdminCity(admin.ModelAdmin):
    list_display = ('name')

admin.site.register(City)

class AdminDistrict(admin.ModelAdmin):
    list_display = ('name','city')

admin.site.register(District)

class PharmacyProductAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'product', 'quantity')

admin.site.register(PharmacyProduct, PharmacyProductAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'pharmacy', 'order_date', 'status')
    inlines = [OrderItemInline]

class ReservationItemInline(admin.TabularInline):
    model = ReservationItem
    extra = 0

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'pharmacy', 'reservation_date', 'status')
    inlines = [ReservationItemInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(Reservation, ReservationAdmin)

