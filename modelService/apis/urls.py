from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = format_suffix_patterns([
    path('auth/',include('rest_framework.urls',namespace='rest_framework')),
    path('labeling',views.labeling, name='labeling')
])