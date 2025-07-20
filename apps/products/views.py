# from django.core.cache import cache
# from rest_framework import generics, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.response import Response

# from .models import Category, Product
# from .serializers import CategorySerializer, ProductSerializer


# # 🗂️ Category Views

# # ✅ Public: List Categories
# class CategoryListView(generics.ListAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.AllowAny]


# # ✅ Admin: Manage Categories (CRUD)
# class CategoryManageView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.IsAdminUser]


# # 📦 Product Views

# # ✅ Public: List Products (with Caching, Filtering, Sorting, Pagination)
# class ProductListView(generics.ListAPIView):
#     serializer_class = ProductSerializer
#     permission_classes = [permissions.AllowAny]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
#     filterset_fields = ['category', 'stock']            # Filter by category & stock
#     ordering_fields = ['price', 'name']                 # Sort by price or name
#     ordering = ['name']                                 # Default sort
#     search_fields = ['name', 'description']             # Search in name & description

#     def get_queryset(self):
#         # Optimize DB: join category data in single query
#         return Product.objects.select_related('category').all()

#     def list(self, request, *args, **kwargs):
#         # Dynamic cache key per query params
#         cache_key = f"product_list_{request.GET.urlencode() or 'default'}"
#         cached_response = cache.get(cache_key)

#         if cached_response:
#             print("✅ Cache HIT: Returning cached product list")
#             return Response(cached_response)

#         print("❌ Cache MISS: Fetching from DB")
#         response = super().list(request, *args, **kwargs)
#         cache.set(cache_key, response.data, timeout=3600)  # Cache for 1 hour
#         print("📦 Cached product list for 1 hour")
#         return response


# # ✅ Admin: Manage Products (CRUD)
# class ProductManageView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     permission_classes = [permissions.IsAdminUser]

#     def perform_create(self, serializer):
#         product = serializer.save()
#         self.clear_product_cache()
#         print(f"🆕 Product '{product.name}' created & cache cleared")

#     def perform_update(self, serializer):
#         product = serializer.save()
#         self.clear_product_cache()
#         print(f"✏️ Product '{product.name}' updated & cache cleared")

#     def perform_destroy(self, instance):
#         instance.delete()
#         self.clear_product_cache()
#         print(f"🗑️ Product '{instance.name}' deleted & cache cleared")

#     def clear_product_cache(self):
#         # Clear all cached product lists
#         cache.delete_pattern('product_list_*')




from django.core.cache import cache
from rest_framework import generics, permissions, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, BooleanFilter, ModelChoiceFilter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


# ✅ Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Default 10 per page
    page_size_query_param = 'page_size'
    max_page_size = 100


# ✅ Filtering
class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")
    in_stock = BooleanFilter(method='filter_in_stock')
    category = ModelChoiceFilter(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'in_stock']

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset.filter(stock=0)


# 📂 Category Views
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryManageView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


# 📦 Product Views
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        DjangoFilterBackend, 
        drf_filters.OrderingFilter, 
        drf_filters.SearchFilter
    ]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['name']
    search_fields = ['name', 'description']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Optimized DB query with select_related"""
        return Product.objects.select_related('category').all()

    def list(self, request, *args, **kwargs):
        cache_key = f"product_list_{request.GET.urlencode() or 'default'}"
        cached_response = cache.get(cache_key)
        if cached_response:
            print("✅ Redis Cache HIT")
            return Response(cached_response)
        print("❌ Redis Cache MISS")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=3600)  # 1-hour cache
        return response


class ProductManageView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        product = serializer.save()
        self.clear_cache()
        print(f"🆕 Created: {product.name}")

    def perform_update(self, serializer):
        product = serializer.save()
        self.clear_cache()
        print(f"✏️ Updated: {product.name}")

    def perform_destroy(self, instance):
        instance.delete()
        self.clear_cache()
        print(f"🗑️ Deleted: {instance.name}")

    def clear_cache(self):
        cache.delete_pattern('product_list_*')
        print("♻️ Redis Cache Cleared")
