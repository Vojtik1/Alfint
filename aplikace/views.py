import simfin as sf
import csv
from django.shortcuts import render, redirect
import io
from django.core.paginator import Paginator
from django.contrib.auth import login
import plotly.graph_objs as go
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

def home(request):
    if request.user.is_authenticated:
        return redirect('main_page')  # Přesměrování na hlavní stránku pro přihlášené uživatele
    return render(request, 'home.html')

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

                # Update nebo create IncomeStatement
                if ticker in income_data.index.get_level_values('Ticker'):
                    income_records = income_data.loc[ticker]
                    for year in income_records.index.get_level_values('Fiscal Year'):
                        IncomeStatement.objects.update_or_create(
                            stock=stock,
                            fiscal_year=year,
                            defaults={
                                'revenue': income_records.at[
                                    year, 'Revenue'] if 'Revenue' in income_records.columns else None,
                                'gross_profit': income_records.at[
                                    year, 'Gross Profit'] if 'Gross Profit' in income_records.columns else None,
                                'operating_income': income_records.at[
                                    year, 'Operating Income (Loss)'] if 'Operating Income (Loss)' in income_records.columns else None,
                                'net_income': income_records.at[
                                    year, 'Net Income'] if 'Net Income' in income_records.columns else None,
                                'interest_expense': income_records.at[
                                    year, 'Interest Expense, Net'] if 'Interest Expense, Net' in income_records.columns else None,
                                'depreciation_amortization': income_records.at[
                                    year, 'Depreciation & Amortization'] if 'Depreciation & Amortization' in income_records.columns else None,
                            }
                        )

                # Update nebo create BalanceSheet
                if ticker in balance_data.index.get_level_values('Ticker'):
                    balance_records = balance_data.loc[ticker]
                    for year in balance_records.index.get_level_values('Fiscal Year'):
                        BalanceSheet.objects.update_or_create(
                            stock=stock,
                            fiscal_year=year,
                            defaults={
                                'total_assets': balance_records.at[
                                    year, 'Total Assets'] if 'Total Assets' in balance_records.columns else None,
                                'total_current_assets': balance_records.at[
                                    year, 'Total Current Assets'] if 'Total Current Assets' in balance_records.columns else None,
                                'total_current_liabilities': balance_records.at[
                                    year, 'Total Current Liabilities'] if 'Total Current Liabilities' in balance_records.columns else None,
                                'inventories': balance_records.at[
                                    year, 'Inventories'] if 'Inventories' in balance_records.columns else None,
                                'total_liabilities': balance_records.at[
                                    year, 'Total Liabilities'] if 'Total Liabilities' in balance_records.columns else None,
                                'total_equity': balance_records.at[
                                    year, 'Total Equity'] if 'Total Equity' in balance_records.columns else None,
                                'short_term_debt': balance_records.at[
                                    year, 'Short Term Debt'] if 'Short Term Debt' in balance_records.columns else None,
                                'long_term_debt': balance_records.at[
                                    year, 'Long Term Debt'] if 'Long Term Debt' in balance_records.columns else None,
                            }
                        )

                # Update nebo create CashFlowStatement
                if ticker in cashflow_data.index.get_level_values('Ticker'):
                    cashflow_records = cashflow_data.loc[ticker]
                    for year in cashflow_records.index.get_level_values('Fiscal Year'):
                        CashFlowStatement.objects.update_or_create(
                            stock=stock,
                            fiscal_year=year,
                            defaults={
                                'operating_cash_flow': cashflow_records.at[
                                    year, 'Net Cash from Operating Activities'] if 'Net Cash from Operating Activities' in cashflow_records.columns else None,
                                'investing_cash_flow': cashflow_records.at[
                                    year, 'Net Cash from Investing Activities'] if 'Net Cash from Investing Activities' in cashflow_records.columns else None,
                                'financing_cash_flow': cashflow_records.at[
                                    year, 'Net Cash from Financing Activities'] if 'Net Cash from Financing Activities' in cashflow_records.columns else None,
                                'free_cash_flow': (
                                    cashflow_records.at[year, 'Net Cash from Operating Activities'] -
                                    cashflow_records.at[year, 'Change in Fixed Assets & Intangibles']
                                    if 'Net Cash from Operating Activities' in cashflow_records.columns and
                                       'Change in Fixed Assets & Intangibles' in cashflow_records.columns else None
                                ),
                                'capital_expenditures': cashflow_records.at[
                                    year, 'Change in Fixed Assets & Intangibles'] if 'Change in Fixed Assets & Intangibles' in cashflow_records.columns else None,
                                'dividends_paid': cashflow_records.at[
                                    year, 'Dividends Paid'] if 'Dividends Paid' in cashflow_records.columns else None,
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
    pe_ratio_min = request.GET.get('pe_ratio_min')
    pe_ratio_max = request.GET.get('pe_ratio_max')
    roe_min = request.GET.get('roe_min')
    roe_max = request.GET.get('roe_max')
    debt_to_equity_max = request.GET.get('debt_to_equity_max')

    if market_cap_min:
        stocks = stocks.filter(market_cap__gte=market_cap_min)
    if market_cap_max:
        stocks = stocks.filter(market_cap__lte=market_cap_max)
    if pe_ratio_min:
        stocks = stocks.filter(pe_ratio__gte=pe_ratio_min)
    if pe_ratio_max:
        stocks = stocks.filter(pe_ratio__lte=pe_ratio_max)
    if roe_min:
        stocks = stocks.filter(roe__gte=roe_min)
    if roe_max:
        stocks = stocks.filter(roe__lte=roe_max)
    if debt_to_equity_max:
        stocks = stocks.filter(debt_to_equity__lte=debt_to_equity_max)

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
            # Načtení finančních dat
            income_statement = IncomeStatement.objects.filter(stock=stock).order_by('-fiscal_year').first()
            balance_sheet = BalanceSheet.objects.filter(stock=stock).order_by('-fiscal_year').first()
            cash_flow_statement = CashFlowStatement.objects.filter(stock=stock).order_by('-fiscal_year').first()

            if income_statement and balance_sheet:
                # P/E Ratio
                if stock.market_cap and income_statement.net_income and income_statement.net_income != 0:
                    stock.pe_ratio = round(stock.market_cap / income_statement.net_income, 2)

                # Return on Assets (ROA)
                if income_statement.net_income and balance_sheet.total_assets and balance_sheet.total_assets != 0:
                    stock.roa = round((income_statement.net_income / balance_sheet.total_assets) * 100, 2)

                # Return on Equity (ROE)
                if income_statement.net_income and balance_sheet.total_equity and balance_sheet.total_equity != 0:
                    stock.roe = round((income_statement.net_income / balance_sheet.total_equity) * 100, 2)

                # Net Profit Margin
                if income_statement.net_income and income_statement.revenue and income_statement.revenue != 0:
                    stock.net_profit_margin = round((income_statement.net_income / income_statement.revenue) * 100, 2)

                # Debt to Equity Ratio
                if balance_sheet.total_liabilities and balance_sheet.total_equity and balance_sheet.total_equity != 0:
                    stock.debt_to_equity = round(balance_sheet.total_liabilities / balance_sheet.total_equity, 2)

                # Debt Ratio
                if balance_sheet.total_liabilities and balance_sheet.total_assets and balance_sheet.total_assets != 0:
                    stock.debt_ratio = round(balance_sheet.total_liabilities / balance_sheet.total_assets, 2)

                # Current Ratio
                if balance_sheet.total_current_assets and balance_sheet.total_current_liabilities and balance_sheet.total_current_liabilities != 0:
                    stock.current_ratio = round(balance_sheet.total_current_assets / balance_sheet.total_current_liabilities, 2)

                # Quick Ratio
                if balance_sheet.total_current_assets and balance_sheet.inventories is not None and balance_sheet.total_current_liabilities and balance_sheet.total_current_liabilities != 0:
                    stock.quick_ratio = round((balance_sheet.total_current_assets - balance_sheet.inventories) / balance_sheet.total_current_liabilities, 2)

                # Gross Profit Margin
                if income_statement.gross_profit and income_statement.revenue and income_statement.revenue != 0:
                    stock.gross_profit_margin = round((income_statement.gross_profit / income_statement.revenue) * 100, 2)

                # Operating Profit Margin
                if income_statement.operating_income and income_statement.revenue and income_statement.revenue != 0:
                    stock.operating_profit_margin = round((income_statement.operating_income / income_statement.revenue) * 100, 2)

                # Current Liabilities to Total Liabilities Ratio
                if balance_sheet.total_current_liabilities and balance_sheet.total_liabilities and balance_sheet.total_liabilities != 0:
                    stock.current_liabilities_ratio = round(balance_sheet.total_current_liabilities / balance_sheet.total_liabilities, 2)

                # Free Cash Flow Yield
                if cash_flow_statement and cash_flow_statement.free_cash_flow and stock.market_cap and stock.market_cap != 0:
                    stock.free_cash_flow_yield = round((cash_flow_statement.free_cash_flow / stock.market_cap) * 100, 2)

                # Operating Cash Flow to Total Liabilities
                if cash_flow_statement and cash_flow_statement.operating_cash_flow and balance_sheet.total_liabilities and balance_sheet.total_liabilities != 0:
                    stock.operating_cash_flow_to_liabilities = round((cash_flow_statement.operating_cash_flow / balance_sheet.total_liabilities) * 100, 2)

                # Interest Coverage Ratio
                if income_statement.operating_income and income_statement.interest_expense and income_statement.interest_expense != 0:
                    stock.interest_coverage_ratio = round(income_statement.operating_income / income_statement.interest_expense, 2)

                # Dividend Payout Ratio
                if income_statement.net_income and cash_flow_statement and cash_flow_statement.dividends_paid and income_statement.net_income != 0:
                    stock.dividend_payout_ratio = round((cash_flow_statement.dividends_paid / income_statement.net_income) * 100, 2)

                # Dividend Yield
                if cash_flow_statement and cash_flow_statement.dividends_paid and stock.market_cap and stock.market_cap != 0:
                    stock.dividend_yield = round((cash_flow_statement.dividends_paid / stock.market_cap) * 100, 2)

                # Cash Flow to Debt Ratio
                if cash_flow_statement and cash_flow_statement.operating_cash_flow and balance_sheet.total_liabilities and balance_sheet.total_liabilities != 0:
                    stock.cash_flow_to_debt_ratio = round((cash_flow_statement.operating_cash_flow / balance_sheet.total_liabilities) * 100, 2)

                # ROIC
                if income_statement.net_income and balance_sheet.total_equity and balance_sheet.total_liabilities:
                    invested_capital = balance_sheet.total_equity + balance_sheet.total_liabilities
                    if invested_capital != 0:
                        stock.roic = round((income_statement.net_income / invested_capital) * 100, 2)

                # Free Cash Flow to Revenue Ratio
                if cash_flow_statement and cash_flow_statement.free_cash_flow and income_statement.revenue and income_statement.revenue != 0:
                    stock.free_cash_flow_to_revenue_ratio = round((cash_flow_statement.free_cash_flow / income_statement.revenue) * 100, 2)

                # Price-to-Sales Ratio (P/S)
                if stock.market_cap and income_statement.revenue and income_statement.revenue != 0:
                    stock.price_to_sales_ratio = round(stock.market_cap / income_statement.revenue, 2)

                # Price-to-Book Ratio (P/B)
                if stock.market_cap and balance_sheet.total_equity and balance_sheet.total_equity != 0:
                    stock.price_to_book_ratio = round(stock.market_cap / balance_sheet.total_equity, 2)

                # EV/Revenue Ratio
                if stock.enterprise_value and income_statement.revenue and income_statement.revenue != 0:
                    stock.ev_to_revenue_ratio = round(stock.enterprise_value / income_statement.revenue, 2)

                # Altman Z-Score
                if (balance_sheet.total_current_assets and balance_sheet.total_current_liabilities and
                        balance_sheet.total_assets and income_statement.revenue and
                        balance_sheet.total_liabilities and balance_sheet.retained_earnings):
                    working_capital = balance_sheet.total_current_assets - balance_sheet.total_current_liabilities
                    z_score = (
                        1.2 * (working_capital / balance_sheet.total_assets) +
                        1.4 * (balance_sheet.retained_earnings / balance_sheet.total_assets) +
                        3.3 * (income_statement.operating_income / balance_sheet.total_assets) +
                        0.6 * (stock.market_cap / balance_sheet.total_liabilities) +
                        1.0 * (income_statement.revenue / balance_sheet.total_assets)
                    )
                    stock.altman_z_score = round(z_score, 2)

                # Uložení vypočítaných ukazatelů
                stock.save()
                print(f"Ratios calculated for {stock.ticker}")

        except Exception as e:
            print(f"Failed to calculate ratios for {stock.ticker}: {e}")

    print("Finished calculating financial ratios.")



def main_page(request):
    shared_portfolios = Portfolio.objects.filter(is_shared=True)
    context = {
        'shared_portfolios': shared_portfolios,
    }
    return render(request, 'main_page.html', context)

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
        clean_ticker = ticker.split(' - ')[0].strip()  # Odebrání názvu společnosti
        if not Stock.objects.filter(ticker=clean_ticker).exists():
            print(f"Tento ticker neexistuje: {clean_ticker}")
            continue

        if not PortfolioStock.objects.filter(portfolio=portfolio, ticker=clean_ticker).exists():
            PortfolioStock.objects.create(portfolio=portfolio, ticker=clean_ticker)

    messages.success(request, "All filtered stocks have been successfully added to your portfolio.")
    return redirect('view_portfolio', portfolio_id=portfolio_id)


from django.db.models import Min, Max


@login_required
def view_portfolio(request, portfolio_id):
    # Načtení portfolia bez omezení na vlastníka
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)

    # Načítání akcií v portfoliu
    portfolio_stocks = PortfolioStock.objects.filter(portfolio=portfolio)

    # Načítání dat o cenách pro všechny akcie
    prices_data = {}
    stocks = []  # Seznam akcií v portfoliu s dodatečnými údaji
    for stock_item in portfolio_stocks:
        stock = get_object_or_404(Stock, ticker=stock_item.ticker)
        share_prices = SharePrices.objects.filter(stock=stock).order_by('date')

        # Výpočet návratnosti pro konkrétní akcii
        stock_return = None
        if share_prices.exists():
            first_price = share_prices.first().close_price
            last_price = share_prices.last().close_price
            if first_price and last_price and first_price != 0:
                stock_return = ((last_price - first_price) / first_price) * 100

            # Uložení dat o cenách pro analýzu
            prices_data[stock.ticker] = {price.date: price.close_price for price in share_prices}

        # Přidáme akcii do seznamu s návratností
        stocks.append({
            'stock': stock,
            'return': stock_return,  # Návratnost akcie
        })

    # Pokud nejsou žádné ceny, ukončíme funkci
    if not prices_data:
        context = {
            'portfolio': portfolio,
            'stocks': stocks,
            'avg_return': None,
            'chart_data': None,
        }
        return render(request, 'portfolio_detail.html', context)

    # Převod dat do DataFrame
    df = pd.DataFrame(prices_data).sort_index()

    # Vypočítáme průměrnou hodnotu každý den (ignorujeme NaN hodnoty)
    df['ETF'] = df.mean(axis=1)

    # Normalizace na první den (pomyslné ETF začíná na hodnotě 100)
    df['ETF'] = (df['ETF'] / df['ETF'].iloc[0]) * 100

    # Vytvoření dat pro interaktivní graf
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['ETF'], mode='lines', name='Pomyslné ETF'))

    # Převod grafu do JSON
    chart_data = fig.to_json()

    # Průměrná návratnost portfolia
    avg_return = ((df['ETF'].iloc[-1] - df['ETF'].iloc[0]) / df['ETF'].iloc[0]) * 100

    # Kontext pro šablonu
    context = {
        'portfolio': portfolio,
        'stocks': stocks,  # Seznam akcií s návratností
        'avg_return': avg_return,
        'chart_data': chart_data,  # Data pro interaktivní graf
    }
    return render(request, 'portfolio_detail.html', context)

@login_required
def user_portfolios(request):
    # Získání všech portfolií přihlášeného uživatele
    portfolios = Portfolio.objects.filter(user=request.user)
    context = {
        'portfolios': portfolios,
    }
    return render(request, 'user_portfolios.html', context)

@login_required
def toggle_share(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    portfolio.is_shared = not portfolio.is_shared
    portfolio.save()
    return redirect('view_portfolio', portfolio_id=portfolio_id)

#to run this just use command prompt and:
#python manage.py shell
#from aplikace.views import load_data_command
#load_data_command()

def load_data_command():
   # load_simfin_data()
  #  load_yfinance_data()
    calculate_ratios()







