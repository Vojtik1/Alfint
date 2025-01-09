from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import PortfolioStock

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

class PortfolioStockForm(forms.ModelForm):
    class Meta:
        model = PortfolioStock
        fields = ['ticker', 'weight', 'quantity']