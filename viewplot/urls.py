from django.urls import path

from . import views     

urlpatterns = [
    path('viewplot',views.plot, name='viewplot')
]