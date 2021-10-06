from django.urls import path, include
from . import views


urlpatterns = [
    path('parameter',views.parameter,name='parameter')
]