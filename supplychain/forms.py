from django import forms
from django.forms import TextInput
from .models import User, Register, Customer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AddEntityForm(forms.Form):
    ENTITY_CHOICES = [
        ('M', 'Manufacturer'),
        ('D', 'Distributor'),
        ('R', 'Retailer')
    ]
    entity_type = forms.ChoiceField(choices=ENTITY_CHOICES, label="Entity Type")
    address = forms.CharField(max_length=100)
    name = forms.CharField(max_length=100)
    place = forms.CharField(max_length=100)

class AddProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=500)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    image = forms.ImageField()


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = "__all__"
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2' ]

