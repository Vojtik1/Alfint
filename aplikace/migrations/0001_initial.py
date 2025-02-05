# Generated by Django 5.1.1 on 2024-11-25 17:03

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('last_price', models.FloatField(blank=True, null=True)),
                ('market_cap', models.FloatField(blank=True, null=True)),
                ('pe_ratio', models.FloatField(blank=True, null=True)),
                ('ebitda', models.FloatField(blank=True, null=True)),
                ('beta', models.FloatField(blank=True, null=True)),
                ('enterprise_value', models.FloatField(blank=True, null=True)),
                ('sector', models.CharField(blank=True, max_length=100, null=True)),
                ('industry', models.CharField(blank=True, max_length=100, null=True)),
                ('roa', models.FloatField(blank=True, null=True)),
                ('roe', models.FloatField(blank=True, null=True)),
                ('debt_to_equity', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='customuser_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='customuser_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='My Portfolio', max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolios', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='PortfolioStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=10)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='aplikace.portfolio')),
            ],
        ),
        migrations.CreateModel(
            name='SharePrices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('close_price', models.FloatField(blank=True, null=True)),
                ('open_price', models.FloatField(blank=True, null=True)),
                ('high_price', models.FloatField(blank=True, null=True)),
                ('low_price', models.FloatField(blank=True, null=True)),
                ('volume', models.FloatField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplikace.stock')),
            ],
        ),
        migrations.CreateModel(
            name='IncomeStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscal_year', models.IntegerField()),
                ('revenue', models.FloatField(blank=True, null=True)),
                ('gross_profit', models.FloatField(blank=True, null=True)),
                ('operating_income', models.FloatField(blank=True, null=True)),
                ('net_income', models.FloatField(blank=True, null=True)),
                ('ebitda', models.FloatField(blank=True, null=True)),
                ('operating_expenses', models.FloatField(blank=True, null=True)),
                ('cost_of_revenue', models.FloatField(blank=True, null=True)),
                ('interest_expense', models.FloatField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplikace.stock')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('founded_year', models.IntegerField(blank=True, null=True)),
                ('employees', models.IntegerField(blank=True, null=True)),
                ('headquarters', models.CharField(blank=True, max_length=255, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplikace.stock')),
            ],
        ),
        migrations.CreateModel(
            name='CashFlowStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscal_year', models.IntegerField()),
                ('operating_cash_flow', models.FloatField(blank=True, null=True)),
                ('investing_cash_flow', models.FloatField(blank=True, null=True)),
                ('financing_cash_flow', models.FloatField(blank=True, null=True)),
                ('free_cash_flow', models.FloatField(blank=True, null=True)),
                ('capital_expenditures', models.FloatField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplikace.stock')),
            ],
        ),
        migrations.CreateModel(
            name='BalanceSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscal_year', models.IntegerField()),
                ('total_assets', models.FloatField(blank=True, null=True)),
                ('total_liabilities', models.FloatField(blank=True, null=True)),
                ('total_equity', models.FloatField(blank=True, null=True)),
                ('cash_and_equivalents', models.FloatField(blank=True, null=True)),
                ('short_term_debt', models.FloatField(blank=True, null=True)),
                ('long_term_debt', models.FloatField(blank=True, null=True)),
                ('accounts_receivable', models.FloatField(blank=True, null=True)),
                ('inventories', models.FloatField(blank=True, null=True)),
                ('retained_earnings', models.FloatField(blank=True, null=True)),
                ('total_current_assets', models.FloatField(blank=True, null=True)),
                ('total_current_liabilities', models.FloatField(blank=True, null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplikace.stock')),
            ],
        ),
    ]
