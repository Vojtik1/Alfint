from django.contrib.auth.models import AbstractUser
from django.db import models


class Stock(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    last_price = models.FloatField(null=True, blank=True)
    market_cap = models.FloatField(null=True, blank=True)
    pe_ratio = models.FloatField(null=True, blank=True)
    ebitda = models.FloatField(null=True, blank=True)
    beta = models.FloatField(null=True, blank=True)
    enterprise_value = models.FloatField(null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    roa = models.FloatField(null=True, blank=True)
    roe = models.FloatField(null=True, blank=True)
    debt_to_equity = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        ordering = ['ticker']

    def __str__(self):
        return f"{self.ticker} - {self.name}"


class IncomeStatement(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    revenue = models.FloatField(null=True, blank=True)
    gross_profit = models.FloatField(null=True, blank=True)
    operating_income = models.FloatField(null=True, blank=True)
    net_income = models.FloatField(null=True, blank=True)
    ebitda = models.FloatField(null=True, blank=True)
    operating_expenses = models.FloatField(null=True, blank=True)
    cost_of_revenue = models.FloatField(null=True, blank=True)
    interest_expense = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Income Statement"
        verbose_name_plural = "Income Statements"
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"{self.stock.ticker} - {self.fiscal_year}"


class BalanceSheet(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    total_assets = models.FloatField(null=True, blank=True)
    total_liabilities = models.FloatField(null=True, blank=True)
    total_equity = models.FloatField(null=True, blank=True)
    cash_and_equivalents = models.FloatField(null=True, blank=True)
    short_term_debt = models.FloatField(null=True, blank=True)
    long_term_debt = models.FloatField(null=True, blank=True)
    accounts_receivable = models.FloatField(null=True, blank=True)
    inventories = models.FloatField(null=True, blank=True)
    retained_earnings = models.FloatField(null=True, blank=True)
    total_current_assets = models.FloatField(null=True, blank=True)
    total_current_liabilities = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Balance Sheet"
        verbose_name_plural = "Balance Sheets"
        ordering = ['-fiscal_year']

    def __str__(self):
        return f"{self.stock.ticker} - {self.fiscal_year}"


class CashFlowStatement(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    fiscal_year = models.IntegerField()
    operating_cash_flow = models.FloatField(null=True, blank=True)
    investing_cash_flow = models.FloatField(null=True, blank=True)
    financing_cash_flow = models.FloatField(null=True, blank=True)
    free_cash_flow = models.FloatField(null=True, blank=True)
    capital_expenditures = models.FloatField(null=True, blank=True)

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
    is_shared = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return f"{self.user.username}'s Portfolio: {self.name}"


class PortfolioStock(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='stocks')
    ticker = models.CharField(max_length=10)

    class Meta:
        verbose_name = "Portfolio Stock"
        verbose_name_plural = "Portfolio Stocks"

    def __str__(self):
        return f"{self.ticker} in {self.portfolio}"
