from django.urls import path
from .views import finance_overview, transactions,delete_card,goal_dashboard

urlpatterns = [
    path('overview/', finance_overview, name='finance_overview'),
    path('transactions/', transactions, name='transactions'),
    path('delete-card/<int:pk>/', delete_card, name='delete_card'),
    path("goals/", goal_dashboard, name="goal_dashboard"),

]
