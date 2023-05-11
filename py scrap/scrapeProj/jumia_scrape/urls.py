from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:id>/', views.product_details, name='product_details'),
    path('smartphone/<str:name>', views.smartphone_detail, name='smartphone_detail'),
   
]