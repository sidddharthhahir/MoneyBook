from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='preferences'),  # handles http://127.0.0.1:8000/
]