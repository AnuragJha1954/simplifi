from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.utils.timezone import now

def home(request):
    return render(request, 'core/home.html')

def pricing(request):
    return render(request, 'core/pricing.html')

def product(request):
    return render(request, 'core/product.html')
