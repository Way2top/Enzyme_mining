from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),  # 设置主页路由
    path('logout/', views.logout_view, name='logout'),
    path('page1/', views.page1, name='page1'),
    path('page2/', views.page2, name='page2'),
    path('enzymemodel/', views.enzymemodel, name='enzymemodel'),
    path('similarenzyme/', views.similarenzyme, name='similarenzyme'),
    path('about/', views.about, name='about'),
    path('importdatabase/', views.importdatabase, name='importdatabase'),
path('dataanalysis/', views.dataanalysis, name='dataanalysis'),
    path('get_fasta_content/<int:file_id>/', views.get_fasta_content, name='get_fasta_content'),
]
