from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models


class Stock(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    last_price = models.FloatField(null=True, blank=True)
    market_cap = models.IntegerField(null=True, blank=True)
    pe_ratio = models.FloatField(null=True, blank=True)
    ebitda = models.FloatField(null=True, blank=True)
    beta = models.FloatField(null=True, blank=True)
    enterprise_value = models.FloatField(null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    roa = models.FloatField(null=True, blank=True)
    roe = models.FloatField(null=True, blank=True)
    net_profit_margin = models.FloatField(null=True, blank=True)
    debt_to_equity = models.FloatField(null=True, blank=True)
    debt_ratio = models.FloatField(null=True, blank=True)
    current_ratio = models.FloatField(null=True, blank=True)
    quick_ratio = models.FloatField(null=True, blank=True)
    gross_profit_margin = models.FloatField(null=True, blank=True)
    operating_profit_margin = models.FloatField(null=True, blank=True)
    current_liabilities_ratio = models.FloatField(null=True, blank=True)
    operating_cash_flow_to_liabilities = models.FloatField(null=True, blank=True)
    interest_coverage_ratio = models.FloatField(null=True, blank=True)
    dividend_payout_ratio = models.FloatField(null=True, blank=True)
    dividend_yield = models.FloatField(null=True, blank=True)
    cash_flow_to_debt_ratio = models.FloatField(null=True, blank=True)
    roic = models.FloatField(null=True, blank=True)
    price_to_sales_ratio = models.FloatField(null=True, blank=True)
    price_to_book_ratio = models.FloatField(null=True, blank=True)
    ev_to_revenue_ratio = models.FloatField(null=True, blank=True)
    altman_z_score = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)


    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        ordering = ['-market_cap']

    def __str__(self):
        return f"{self.ticker} - {self.name}"


class IncomeStatement(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    revenue = models.FloatField(null=True, blank=True)
    cost_of_revenue = models.FloatField(null=True, blank=True)
    gross_profit = models.FloatField(null=True, blank=True)
    operating_expenses = models.FloatField(null=True, blank=True)
    depreciation_amortization = models.FloatField(null=True, blank=True)
    net_income = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Income Statement"
        verbose_name_plural = "Income Statements"
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"{self.stock.ticker} - {self.fiscal_year}"


class BalanceSheet(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    inventories = models.FloatField(null=True, blank=True)
    total_current_assets = models.FloatField(null=True, blank=True)
    total_noncurrent_assets = models.FloatField(null=True, blank=True)
    total_assets = models.FloatField(null=True, blank=True)
    payables_accruals = models.FloatField(null=True, blank=True)
    total_current_liabilities = models.FloatField(null=True, blank=True)
    total_noncurrent_liabilities = models.FloatField(null=True, blank=True)
    total_liabilities = models.FloatField(null=True, blank=True)
    retained_earnings = models.FloatField(null=True, blank=True)
    total_equity = models.FloatField(null=True, blank=True)
    total_liabilities_and_equity = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Balance Sheet"
        verbose_name_plural = "Balance Sheets"
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"{self.stock.ticker} - {self.fiscal_year}"



class CashFlowStatement(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    depreciation_amortization = models.FloatField(null=True, blank=True)
    non_cash_items = models.FloatField(null=True, blank=True)
    change_in_working_capital = models.FloatField(null=True, blank=True)
    operating_cash_flow = models.FloatField(null=True, blank=True)
    change_in_fixed_assets = models.FloatField(null=True, blank=True)
    investing_cash_flow = models.FloatField(null=True, blank=True)
    dividends_paid = models.FloatField(null=True, blank=True)
    financing_cash_flow = models.FloatField(null=True, blank=True)
    net_change_in_cash = models.FloatField(null=True, blank=True)
    free_cash_flow = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Cash Flow Statement"
        verbose_name_plural = "Cash Flow Statements"
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"{self.stock.ticker} - {self.fiscal_year}"



class SharePrices(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    close_price = models.FloatField(null=True, blank=True)
    open_price = models.FloatField(null=True, blank=True)
    high_price = models.FloatField(null=True, blank=True)
    low_price = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Share Price"
        verbose_name_plural = "Share Prices"
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.ticker} - {self.date}"


class CompanyInformation(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    founded_year = models.IntegerField(null=True, blank=True)
    employees = models.IntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"

    def __str__(self):
        return f"{self.stock.ticker} - {self.stock.name}"


class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Portfolio(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=255, default='My Portfolio')
    is_shared = models.BooleanField(default=False, blank=True, null=False)
    is_hearted = models.BooleanField(default=False, blank=True, null=False)

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return f"{self.user.username}'s Portfolio: {self.name}"


class PortfolioStock(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='stocks')
    ticker = models.CharField(max_length=10)
    weight = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = "Portfolio Stock"
        verbose_name_plural = "Portfolio Stocks"

    def __str__(self):
        return f"{self.ticker} in {self.portfolio}"

    def clean(self):
        # Zkontroluj, zda součet vah v portfoliu nepřesahuje 100 %
        total_weight = sum(stock.weight for stock in self.portfolio.stocks.exclude(pk=self.pk)) + self.weight
        if total_weight > 100.0:
            raise ValidationError("Součet vah akcií v portfoliu nemůže být větší než 100 %.")

    def save(self, *args, **kwargs):
        if self.weight == 0:  # Pokud je váha 0, nastavíme na stejnou hodnotu pro všechny akcie
            portfolio_size = PortfolioStock.objects.count()
            if portfolio_size > 0:
                self.weight = 100 / portfolio_size  # Stejná váha pro všechny akcie
            else:
                self.weight = 0  # Pokud není žádná akcie, nastavíme 0
        super().save(*args, **kwargs)
