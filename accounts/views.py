from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'accounts/auth.html', {'form': form, 'type': 'login'})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()

    return render(request, 'accounts/auth.html', {'form': form, 'type': 'signup'})


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


@login_required
def dashboard_home(request):
    return render(request, 'accounts/home.html')

@login_required
def settings_page(request):

    if request.method == "POST":
        request.user.phone = request.POST.get("phone")
        request.user.income_range = request.POST.get("income_range")
        request.user.save()
        return redirect("settings_page")

    return render(request, "accounts/settings.html")





