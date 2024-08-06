from typing import Any, List
from django.db.models import QuerySet
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    View,
    TemplateView,
    FormView
)
