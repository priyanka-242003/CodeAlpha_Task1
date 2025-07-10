# app.py

import os
import django
from django.conf import settings
from django.urls import path
from django.http import JsonResponse
from django.db import models
from django.core.management import execute_from_command_line
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers

# ----------------------------------------
# Django Setup
# ----------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True

settings.configure(
    DEBUG=DEBUG,
    SECRET_KEY='your-secret-key',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    MIDDLEWARE=[
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ],
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'rest_framework',
        '__main__',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
)

django.setup()

# ----------------------------------------
# Models
# ----------------------------------------

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.URLField()

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

# ----------------------------------------
# Serializers
# ----------------------------------------

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

# ----------------------------------------
# Views
# ----------------------------------------

@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    return Response(ProductSerializer(products, many=True).data)

@api_view(['POST'])
@csrf_exempt
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered'})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@csrf_exempt
def place_order(request):
    try:
        user = User.objects.get(id=request.data.get('user_id'))
        order = Order.objects.create(user=user)
        order.products.set(request.data.get('products', []))
        return Response({'message': 'Order placed'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

# ----------------------------------------
# URLs
# ----------------------------------------

urlpatterns = [
    path('api/products/', product_list),
    path('api/register/', register_user),
    path('api/order/', place_order),
]

# ----------------------------------------
# Run Server / Commands
# ----------------------------------------

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "__main__")

    import sys
    args = sys.argv

    if args[1] == "runserver":
        from django.core.management.commands.runserver import Command as runserver
        runserver.default_port = "8000"

    execute_from_command_line(sys.argv)
