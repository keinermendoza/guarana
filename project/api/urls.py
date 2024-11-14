from django.urls import path
from . import views

urlpatterns = [
    path('production/', views.ProductionApiView.as_view(), name='production'),
    # path('sells/', views.SellsApiView.as_view(), name='sells'),
]
