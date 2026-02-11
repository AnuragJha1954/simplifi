from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'income_range', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full h-14 px-5 rounded-2xl border border-slate-300 '
                         'bg-white text-slate-800 placeholder-slate-400 '
                         'focus:outline-none focus:ring-4 focus:ring-cyan-200 '
                         'focus:border-cyan-500 transition',
                'placeholder': field.label,
            })
            field.label = ""


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full h-14 px-5 rounded-2xl border border-slate-300 '
                         'bg-white text-slate-800 placeholder-slate-400 '
                         'focus:outline-none focus:ring-4 focus:ring-cyan-200 '
                         'focus:border-cyan-500 transition',
                'placeholder': field.label,
            })
            field.label = ""
