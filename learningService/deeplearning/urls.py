from django.urls import path, include
from . import views


urlpatterns = [
    path('training',views.training,name='training'),
    path('training-test',views.trainingTest,name='trainingTest'),
    path('parameter',views.parameter,name='parameter'),
]