from django.urls import path
from .views import home, pricing, product

urlpatterns = [
    path('', home, name='home'),
    path('pricing/', pricing, name='pricing'),
    path('product/', product, name='product'),
]
