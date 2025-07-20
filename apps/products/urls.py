from django.urls import path
from .views import (
    CategoryListView, CategoryManageView,
    ProductListView, ProductManageView
)

urlpatterns = [
    # Public Routes
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),

    # Admin Routes
    path('admin/categories/', CategoryManageView.as_view(), name='category-manage'),
    path('admin/categories/<int:pk>/', CategoryManageView.as_view(), name='category-detail'),
    path('admin/products/', ProductManageView.as_view(), name='product-manage'),
    path('admin/products/<int:pk>/', ProductManageView.as_view(), name='product-detail'),
]
