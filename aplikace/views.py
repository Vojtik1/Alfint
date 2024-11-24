import simfin as sf
import csv
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
import yfinance as yf
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from simfin.names import *
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.http import HttpResponse, JsonResponse
from .models import Stock, IncomeStatement, BalanceSheet, CashFlowStatement, SharePrices, PortfolioStock, Portfolio
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.core.cache import cache
import time

sf.set_api_key('dacb95bc-907f-47cc-8c2d-2504aa3d32dd')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
simfin_data_path = os.path.join(BASE_DIR, 'simfin_data')
sf.set_data_dir(simfin_data_path)

# Kontrola a automatické stažení dat, pokud nejsou přítomná
datasets = [
    ('income', 'annual'),
    ('balance', 'annual'),
    ('cashflow', 'annual'),
    ('shareprices', 'daily')
]

for dataset_name, variant in datasets:
    dataset_path = os.path.join(simfin_data_path, f'us-{dataset_name}-{variant}.csv')
    if not os.path.exists(dataset_path):
        print(f"Dataset {dataset_name} není nalezen. Stahování ze SimFin API...")
        sf.load(dataset=dataset_name, variant=variant, market='us', index=['Ticker', 'Fiscal Year'])

def create_price_chart(close_prices):
    dates = [price['date'] for price in close_prices]
    prices = [price['close_price'] for price in close_prices]

    # Vytvoření grafu
    fig, ax = plt.subplots()
    ax.plot(dates, prices, label='Close Price')

    ax.set(xlabel='Date', ylabel='Close Price',
           title='Stock Price Over Time')
    ax.grid()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return image_base64

def load_simfin_data():
    print("Starting to load SimFin data...")
    # Load SimFin data for income, balance, cashflow, shareprices
    try:
        income_data = sf.load(dataset='income', variant='annual', market='us', index=['Ticker', 'Fiscal Year'])
        balance_data = sf.load(dataset='balance', variant='annual', market='us', index=['Ticker', 'Fiscal Year'])
        cashflow_data = sf.load(dataset='cashflow', variant='annual', market='us', index=['Ticker', 'Fiscal Year'])
        shareprices_data = sf.load(dataset='shareprices', variant='daily', market='us', index=['Ticker', 'Date'])

        # Iterate over tickers to store in database
        for ticker in income_data.index.get_level_values('Ticker').unique():
            print(f"Processing ticker: {ticker}")
            stock, created = Stock.objects.get_or_create(ticker=ticker)

            if created:
                stock.name = ticker  # Placeholder name until updated from Yahoo Finance
                stock.save()

            # Update or create IncomeStatement records
            if ticker in income_data.index.get_level_values('Ticker'):
                income_records = income_data.loc[ticker]
                for year in income_records.index.get_level_values('Fiscal Year'):
                    IncomeStatement.objects.update_or_create(
                        stock=stock,
                        fiscal_year=year,
                        defaults={
                            'revenue': income_records.at[year, 'Revenue'] if 'Revenue' in income_records.columns else None,
                            'gross_profit': income_records.at[year, 'Gross Profit'] if 'Gross Profit' in income_records.columns else None,
                            'operating_income': income_records.at[year, 'Operating Income (Loss)'] if 'Operating Income (Loss)' in income_records.columns else None,
                            'net_income': income_records.at[year, 'Net Income'] if 'Net Income' in income_records.columns else None,
                            'ebitda': income_records.at[year, 'EBITDA'] if 'EBITDA' in income_records.columns else None,
                        }
                    )

            # Update or create BalanceSheet records
            if ticker in balance_data.index.get_level_values('Ticker'):
                balance_records = balance_data.loc[ticker]
                for year in balance_records.index.get_level_values('Fiscal Year'):
                    BalanceSheet.objects.update_or_create(
                        stock=stock,
                        fiscal_year=year,
                        defaults={
                            'total_assets': balance_records.at[year, 'Total Assets'] if 'Total Assets' in balance_records.columns else None,
                            'total_liabilities': balance_records.at[year, 'Total Liabilities'] if 'Total Liabilities' in balance_records.columns else None,
                            'total_equity': balance_records.at[year, 'Total Equity'] if 'Total Equity' in balance_records.columns else None,
                            'cash_and_equivalents': balance_records.at[year, 'Cash, Cash Equivalents & Short Term Investments'] if 'Cash, Cash Equivalents & Short Term Investments' in balance_records.columns else None,
                            'short_term_debt': balance_records.at[year, 'Short Term Debt'] if 'Short Term Debt' in balance_records.columns else None,
                            'long_term_debt': balance_records.at[year, 'Long Term Debt'] if 'Long Term Debt' in balance_records.columns else None,
                            'total_current_assets': balance_records.at[year, 'Total Current Assets'] if 'Total Current Assets' in balance_records.columns else None,
                            'total_current_liabilities': balance_records.at[year, 'Total Current Liabilities'] if 'Total Current Liabilities' in balance_records.columns else None,
                            'inventories': balance_records.at[year, 'Inventories'] if 'Inventories' in balance_records.columns else None,
                        }
                    )

            # Update or create CashFlowStatement records
            if ticker in cashflow_data.index.get_level_values('Ticker'):
                cashflow_records = cashflow_data.loc[ticker]
                for year in cashflow_records.index.get_level_values('Fiscal Year'):
                    CashFlowStatement.objects.update_or_create(
                        stock=stock,
                        fiscal_year=year,
                        defaults={
                            'operating_cash_flow': cashflow_records.at[year, 'Net Cash from Operating Activities'] if 'Net Cash from Operating Activities' in cashflow_records.columns else None,
                            'investing_cash_flow': cashflow_records.at[year, 'Net Cash from Investing Activities'] if 'Net Cash from Investing Activities' in cashflow_records.columns else None,
                            'financing_cash_flow': cashflow_records.at[year, 'Net Cash from Financing Activities'] if 'Net Cash from Financing Activities' in cashflow_records.columns else None,
                            'free_cash_flow': cashflow_records.at[year, 'Free Cash Flow'] if 'Free Cash Flow' in cashflow_records.columns else None,
                        }
                    )

            # Update or create SharePrices records
            if ticker in shareprices_data.index.get_level_values('Ticker'):
                shareprice_records = shareprices_data.loc[ticker]
                for date in shareprice_records.index.get_level_values('Date'):
                    SharePrices.objects.update_or_create(
                        stock=stock,
                        date=date,
                        defaults={
                            'close_price': shareprice_records.at[date, 'Close'] if 'Close' in shareprice_records.columns else None,
                            'open_price': shareprice_records.at[date, 'Open'] if 'Open' in shareprice_records.columns else None,
                            'high_price': shareprice_records.at[date, 'High'] if 'High' in shareprice_records.columns else None,
                            'low_price': shareprice_records.at[date, 'Low'] if 'Low' in shareprice_records.columns else None,
                            'volume': shareprice_records.at[date, 'Volume'] if 'Volume' in shareprice_records.columns else None,
                        }
                    )
        print("Finished loading SimFin data.")
    except IntegrityError as e:
        print(f"Error saving data: {e}")

def load_yfinance_data():
            print("Starting to load Yahoo Finance data...")
            stocks = Stock.objects.all()
            for stock in stocks:
                try:
                    stock_data_yf = yf.Ticker(stock.ticker)
                    yf_info = stock_data_yf.info
                    stock.name = yf_info.get('shortName')
                    stock.last_price = yf_info.get('currentPrice') or yf_info.get('regularMarketPrice') or yf_info.get(
                        'previousClose')
                    stock.market_cap = yf_info.get('marketCap')
                    stock.pe_ratio = yf_info.get('trailingPE')
                    stock.ebitda = yf_info.get('ebitda')
                    stock.beta = yf_info.get('beta')
                    stock.enterprise_value = yf_info.get('enterpriseValue')
                    stock.sector = yf_info.get('sector')
                    stock.industry = yf_info.get('industry')
                    stock.save()
                    print(f"Data for {stock.ticker} updated from Yahoo Finance.")
                except Exception as e:
                    print(f"Failed to fetch or save data for {stock.ticker} from Yahoo Finance: {e}")
            print("Finished loading Yahoo Finance data.")

def filter(request):
    stocks = Stock.objects.all().order_by('-market_cap')

    # Filter stocks by market cap if requested
    market_cap_min = request.GET.get('market_cap_min')
    market_cap_max = request.GET.get('market_cap_max')

    if market_cap_min:
        stocks = stocks.filter(market_cap__gte=market_cap_min)
    if market_cap_max:
        stocks = stocks.filter(market_cap__lte=market_cap_max)

    # Calculate average return
    average_return = None
    if stocks.exists():
        total_return = 0
        count = 0
        for stock in stocks:
            share_prices = SharePrices.objects.filter(stock=stock).order_by('date')
            if share_prices.count() > 1:
                first_price = share_prices.first().close_price
                last_price = share_prices.last().close_price
                if first_price and last_price and first_price != 0:
                    total_return += (last_price - first_price) / first_price
                    count += 1
        if count > 0:
            average_return = (total_return / count) * 100

    context = {
        'stocks': stocks,
        'average_return': average_return,
    }

    return render(request, 'filter.html', context)

def stock_detail(request, ticker):
    stock_data_yf = yf.Ticker(ticker)
    yf_info = stock_data_yf.info

    # Nejprve načteme nebo vytvoříme záznam pro Stock
    stock, created = Stock.objects.get_or_create(ticker=ticker)
    stock.name = yf_info.get('shortName')
    stock.last_price = yf_info.get('currentPrice') or yf_info.get('regularMarketPrice') or yf_info.get('previousClose')
    stock.market_cap = yf_info.get('marketCap')
    stock.pe_ratio = yf_info.get('trailingPE')
    stock.ebitda = yf_info.get('ebitda')
    stock.beta = yf_info.get('beta')
    stock.enterprise_value = yf_info.get('enterpriseValue')
    stock.sector = yf_info.get('sector')
    stock.industry = yf_info.get('industry')
    stock.save()

    share_prices = SharePrices.objects.filter(stock=stock)

    close_prices = [
        {'date': price.date, 'close_price': price.close_price}
        for price in share_prices
    ]
    chart_image = create_price_chart(close_prices)

    income_statements = IncomeStatement.objects.filter(stock=stock)
    balance_sheets = BalanceSheet.objects.filter(stock=stock)
    cash_flow_statements = CashFlowStatement.objects.filter(stock=stock)

    context = {
        'stock': stock,
        'income_statements': income_statements,
        'balance_sheets': balance_sheets,
        'cash_flow_statements': cash_flow_statements,
        'share_prices': share_prices,
        'chart_image': chart_image
    }

    return render(request, 'stock_detail.html', context)

def calculate_ratios():
    print("Calculating financial ratios...")
    stocks = Stock.objects.all()
    for stock in stocks:
        try:
            # Load related financial data
            income_statement = IncomeStatement.objects.filter(stock=stock).order_by('-fiscal_year').first()
            balance_sheet = BalanceSheet.objects.filter(stock=stock).order_by('-fiscal_year').first()


            if income_statement and balance_sheet:
                # P/E Ratio
                if stock.market_cap and income_statement.net_income:
                    stock.pe_ratio = round(stock.market_cap / income_statement.net_income, 2)

                # Return on Assets (ROA)
                if income_statement.net_income and balance_sheet.total_assets:
                    stock.roa = round((income_statement.net_income / balance_sheet.total_assets) * 100, 2)

                # Return on Equity (ROE)
                if income_statement.net_income and balance_sheet.total_equity:
                    stock.roe = round((income_statement.net_income / balance_sheet.total_equity) * 100, 2)

                # Debt to Equity Ratio
                if balance_sheet.total_liabilities and balance_sheet.total_equity:
                    stock.debt_to_equity = round(balance_sheet.total_liabilities / balance_sheet.total_equity, 2)


                # Save the calculated ratios
                stock.save()
                print(f"Ratios calculated for {stock.ticker}")
        except Exception as e:
            print(f"Failed to calculate ratios for {stock.ticker}: {e}")
    print("Finished calculating financial ratios.")

def main_page(request):
    return render(request, 'main_page.html')

def create_portfolio(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        quantity = request.POST.get('quantity')


    return render(request, 'create_portfolio.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main_page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def stock_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        suggestions = Stock.objects.filter(ticker__icontains=query)[:10]
        data = [{"ticker": stock.ticker, "name": stock.name} for stock in suggestions]
    else:
        data = []
    return JsonResponse(data, safe=False)

@login_required
def create_portfolio(request):
    if request.method == 'POST':
        portfolio_name = request.POST.get('portfolio_name')
        if portfolio_name:
            if Portfolio.objects.filter(user=request.user, name=portfolio_name).exists():
                # Portfolio se stejným názvem už existuje
                return render(request, 'create_portfolio.html', {
                    'error_message': 'Portfolio with this name already exists.',
                })

            portfolio = Portfolio.objects.create(user=request.user, name=portfolio_name)
            return redirect('create_portfolio')

    # Získání všech dostupných akcií z modelu Stock
    stocks = Stock.objects.all().order_by('-market_cap')

    return render(request, 'create_portfolio.html', {'stocks': stocks})

@login_required
@require_POST
def add_stock_to_portfolio(request):
    ticker = request.POST.get('ticker')
    portfolio_id = request.POST.get('portfolio_id')

    if not ticker or not portfolio_id:
        return HttpResponse("Missing data: ticker or portfolio ID", status=400)

    # Kontrolní výpis hodnot pro ladění
    print(f"Ticker: {ticker}, Portfolio ID: {portfolio_id}")

    # Získání portfolia pro uživatele, nebo vrácení chyby 404, pokud neexistuje
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)

    # Přidání akcie do portfolia
    PortfolioStock.objects.create(portfolio=portfolio, ticker=ticker)
    return redirect('create_portfolio')

def load_stocks(request):
    page = request.GET.get('page', 1)
    stocks = Stock.objects.all().order_by('-market_cap')
    paginator = Paginator(stocks, 10)  # 10 akcií na stránku
    stocks_page = paginator.get_page(page)

    data = {
        'stocks': [
            {
                'ticker': stock.ticker,
                'name': stock.name,
                'pe_ratio': stock.pe_ratio,
                'roe': stock.roe,
                'debt_to_equity': stock.debt_to_equity,
                'market_cap': stock.market_cap,
                'roa': stock.roa,
            }
            for stock in stocks_page
        ],
        'has_next': stocks_page.has_next()
    }
    return JsonResponse(data)

@login_required
@require_POST
def add_all_filtered_to_portfolio(request):
    portfolio_id = request.POST.get('portfolio_id')
    filtered_tickers = request.POST.get('filtered_tickers')

    if not portfolio_id or not filtered_tickers:
        return HttpResponse("Missing data: portfolio ID or filtered tickers", status=400)

    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)

    tickers = filtered_tickers.split(',')
    for ticker in tickers:
        # Zkontrolujeme, zda akcie již není v portfoliu
        if not PortfolioStock.objects.filter(portfolio=portfolio, ticker=ticker).exists():
            PortfolioStock.objects.create(portfolio=portfolio, ticker=ticker)

    messages.success(request, "All filtered stocks have been successfully added to your portfolio.")
    return redirect('filter')


#to run this just use command prompt and:
#python manage.py shell
#from aplikace.views import load_data_command
#load_data_command()

def load_data_command():
    load_yfinance_data()
    load_simfin_data()


