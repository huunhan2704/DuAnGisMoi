from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. Trang chủ
    path('', views.home, name='home'),
    
    # 2. Bản đồ
    path('ban-do/', views.map_home, name='map_home'),

    # 3. Danh sách (Thêm cái này để nút "Danh sách" hoạt động)
    path('danh-sach/', views.list_view, name='list'),

    # 4. Chức năng Tài khoản (Thêm logout để hết lỗi)
    path('dang-ky/', views.register_view, name='register'),
    path('dang-nhap/', views.login_view, name='login'),
    path('dang-xuat/', views.logout_view, name='logout'),

    # 5. API
    path('luu-phan-anh/', views.luu_phan_anh, name='luu_phan_anh'),
    path('quen-mat-khau/', auth_views.PasswordResetView.as_view(template_name='maps/password_reset.html'), name='password_reset'),
    path('quen-mat-khau/xong/', auth_views.PasswordResetDoneView.as_view(template_name='maps/password_reset_done.html'), name='password_reset_done'),
    path('dat-lai-mat-khau/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='maps/password_reset_confirm.html'), name='password_reset_confirm'),
    path('dat-lai-mat-khau/thanh-cong/', auth_views.PasswordResetCompleteView.as_view(template_name='maps/password_reset_complete.html'), name='password_reset_complete'),
    path('ho-so-cua-toi/', views.profile, name='profile'),
    # 6. Đường dẫn cho chi tiết hồ sơ
    path('chi-tiet/<int:id_ho_so>/', views.chi_tiet_ho_so, name='chi_tiet'),
    path('chinh-sua-thong-tin/', views.edit_profile, name='edit_profile'),
]