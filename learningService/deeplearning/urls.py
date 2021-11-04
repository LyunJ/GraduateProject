from django.urls import path, include
from . import views


urlpatterns = [
    path('training',views.training,name='training'),
    path('parameter',views.parameter,name='parameter'),
]