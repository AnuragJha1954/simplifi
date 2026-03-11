from django.urls import path
from .views import login_view, signup_view, dashboard_view,dashboard_home,settings_page,CustomLogoutView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path(
    'logout/',
    CustomLogoutView.as_view(),
    name='logout'
),
    path('dashboard/', dashboard_home, name='dashboard_home'),
    path('settings/', settings_page, name='settings_page'),

]
