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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Pokud je nová instance
            # Nastavíme defaultní váhu, která je rovnoměrně rozdělena mezi všechny akcie
            total_stocks = PortfolioStock.objects.count()
            default_weight = 100 / total_stocks if total_stocks > 0 else 0
            self.fields['weight'].initial = default_weight

