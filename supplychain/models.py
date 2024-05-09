from django.db import models


class User(models.Model):
    User_type = (
        ('M', 'Manufacturer'),
        ('D', 'Distributor'),
        ('R', 'Retailer'),
        ('C', 'Customer'),
    )
    user_type = models.CharField(max_length=1, default='R', choices=User_type)
    address = models.CharField(max_length=42)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.address})"

class Register(models.Model):
    name = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.CharField(max_length=22)

class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=500, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    image = models.ImageField(upload_to='media/')

class Customer(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.name