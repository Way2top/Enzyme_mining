from django.urls import path
from . import views

urlpatterns = [
    path('', views.similarenzyme_view, name='similarenzyme'),
    path('api/search_enzyme', views.EnzymeSearchAPIView.as_view(), name='search_enzyme_api'),
] 