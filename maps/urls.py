from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # 1. Trang chủ
    path('', views.home, name='home'),
    
    # 2. Bản đồ
    path('ban-do/', views.map_home, name='map_home'),

    # 3. Danh sách
    path('danh-sach/', views.list_view, name='list'),

    # 4. Chức năng Tài khoản
    path('dang-ky/', views.register_view, name='register'),
    path('dang-nhap/', views.login_view, name='login'),
    path('dang-xuat/', views.logout_view, name='logout'),

    # 5. API và Quên mật khẩu
    path('luu-phan-anh/', views.luu_phan_anh, name='luu_phan_anh'),
    path('quen-mat-khau/', auth_views.PasswordResetView.as_view(template_name='maps/password_reset.html'), name='password_reset'),
    path('quen-mat-khau/xong/', auth_views.PasswordResetDoneView.as_view(template_name='maps/password_reset_done.html'), name='password_reset_done'),
    path('dat-lai-mat-khau/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='maps/password_reset_confirm.html'), name='password_reset_confirm'),
    path('dat-lai-mat-khau/thanh-cong/', auth_views.PasswordResetCompleteView.as_view(template_name='maps/password_reset_complete.html'), name='password_reset_complete'),
    
    path('ho-so-cua-toi/', views.profile, name='profile'),
    
    # 6. ĐƯỜNG DẪN CHI TIẾT (KHAI BÁO CẢ 2 TÊN ĐỂ CHIỀU LÒNG CẢ 2 TRANG)
    path('chi-tiet/<int:id_ho_so>/', views.chi_tiet_ho_so, name='chi_tiet'),       # Dòng này cho trang Profile
    path('chi-tiet/<int:id_ho_so>/', views.chi_tiet_ho_so, name='chi_tiet_ho_so'), # Dòng này cho trang Quản lý hiện trường
    
    path('chinh-sua-thong-tin/', views.edit_profile, name='edit_profile'),
    
    # 8. Quản lý hiện trường
    path('quan-ly-hien-truong/', views.quan_ly_hien_truong, name='quan_ly_hien_truong'),

    # 9. Xuất Excel
    path('xuat-excel/', views.export_excel, name='export_excel'),

    
    # 9. Trang tin tức
    path('tin-tuc/', views.tin_tuc, name='tin_tuc'),
    
    # 10. Trang hướng dẫn
    path('huong-dan/', views.huong_dan, name='huong_dan'),
    
    # 11. Trang danh bạ khẩn cấp 
    path('danh-ba-khan-cap/', views.hotline, name='hotline'),
    
    # 12. Xóa phản ánh
    path('xoa-phan-anh/<int:id>/', views.xoa_phan_anh, name='xoa_phan_anh'),
    
    # 13. CSKH
    path('trung-tam-ho-tro/', views.cskh, name='cskh'),
    
    #14. admin 
    path('quan-ly/', views.trang_quan_ly, name='trang_quan_ly'),
    path('duyet-phan-anh/<int:id>/', views.duyet_phan_anh, name='duyet_phan_anh'),
    path('tra-loi-ho-tro/<int:id>/', views.tra_loi_ho_tro, name='tra_loi_ho_tro'),
    
    # 15. Quản lý User
    path('khoa-user/<int:id>/', views.khoa_user, name='khoa_user'),
    path('xoa-user/<int:id>/', views.xoa_user, name='xoa_user'),
    # 16. API quét vùng
    path('api/quet-vung/', views.api_quet_vung_postgis, name='api_quet_vung'),
    # 17. Thùng rác
    path('khoi-phuc/<int:id>/', views.khoi_phuc_phan_anh, name='khoi_phuc_phan_anh'),
    path('xoa-vinh-vien/<int:id>/', views.xoa_vinh_vien_phan_anh, name='xoa_vinh_vien'),
]