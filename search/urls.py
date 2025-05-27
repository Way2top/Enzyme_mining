from django.contrib import admin
from django.urls import path, include,re_path
from django.views.static import serve
from enzyme_2.settings import MEDIA_ROOT
from search import views
from .views import ProteinEmbeddingView

urlpatterns = [
    path('', views.home, name='home'),  # 设置主页路由

    path('api/embedding/', views.ProteinEmbeddingView.as_view(), name='protein_embedding'),
    path('api/martix/', views.ProteinMatrixView.as_view(), name='protein_matrix'),  # 新增路由
    path('api/protein-data-api/', views.ProteinDataAnalysisView.as_view(), name='protein_data_api'),

    # path('protein-structure/', views.protein_structure_view, name='protein_structure'),


]