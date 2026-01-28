from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn trang chủ
    path('', views.map_home, name='map_home'),
    
    # HÀM MỚI: Đường dẫn để Web gửi dữ liệu về (API)
    path('luu-phan-anh/', views.luu_phan_anh, name='luu_phan_anh'),
]