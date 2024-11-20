from django.urls import path
from . import views

urlpatterns = [
    path('production/', views.ProductionApiView.as_view(), name='production'),
    path('sales/', views.SalesApiView.as_view(), name='sales'),
    path('available-years/', views.AvailableYearsApiView.as_view(), name='available-years'),
    path('available-months/', views.AvailableMonthsApiView.as_view(), name='available-months'),

    # path('sells/', views.SellsApiView.as_view(), name='sells'),
]
