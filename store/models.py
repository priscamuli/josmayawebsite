from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# New Category model
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Updated Product model with category
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    image = CloudinaryField('image')  # Cloudinary handles image storage
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Received", "Received"),
        ("Shipped", "Shipped"),
        ("In Transit", "In Transit"),
        ("Delivered", "Delivered"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    mpesa_merchant_request_id = models.CharField(max_length=100, null=True, blank=True)

    delivery_location = models.TextField(null=True, blank=True)
    notify_phone = models.CharField(max_length=20, null=True, blank=True)

    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"


    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price
