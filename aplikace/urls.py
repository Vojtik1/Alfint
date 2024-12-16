from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('main_page/', views.main_page, name='main_page'),
    path('filter/', views.filter, name='filter'),
    path('filter/update/', views.filter, name='filter_update'),
    path('create_portfolio/', views.create_portfolio, name='create_portfolio'),
    path('stock_suggestions/', views.stock_suggestions, name='stock_suggestions'),
    path('add_stock_to_portfolio/', views.add_stock_to_portfolio, name='add_stock_to_portfolio'),
    path('load_stocks/', views.load_stocks, name='load_stocks'),
    path('stock/<str:ticker>/', views.stock_detail, name='stock_detail'),
    path('signup/', views.signup, name='signup'),
    path('add_all_filtered_to_portfolio/', views.add_all_filtered_to_portfolio, name='add_all_filtered_to_portfolio'),
    path('user_portfolios/', views.user_portfolios, name='user_portfolios'),
    path('portfolio/<int:portfolio_id>/', views.view_portfolio, name='view_portfolio'),
    path('portfolio/<int:portfolio_id>/toggle_share/', views.toggle_share, name='toggle_share'),

]

