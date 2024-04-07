from django.db import models


class User(models.Model):
    User_type = (
        ('S', 'Supplier'),
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
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

class Chat(models.Model):
    sender = models.ForeignKey(Register, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Register, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        return f"{self.sender} to {self.receiver} at {self.timestamp}"