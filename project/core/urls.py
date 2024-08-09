from django.urls import path, re_path
from . import views
from django.views.generic import RedirectView
from django.views.generic import RedirectView
app_name = 'core'

urlpatterns = [
    path('', RedirectView.as_view(url='/admin') )
]
