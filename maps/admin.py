from django.contrib import admin
from .models import PhanAnh, HoTro,Profile
from .models import GioiThieu, AnhGioiThieu
from .models import QuanHuyen

@admin.register(PhanAnh)
class PhanAnhAdmin(admin.ModelAdmin):
    list_display = ('tieu_de', 'thoi_gian', 'trang_thai') # Hiện 3 cột này ra ngoài
    list_filter = ('trang_thai', 'thoi_gian') # Bộ lọc bên phải
    search_fields = ('tieu_de', 'mo_ta') # Thanh tìm kiếm
    
@admin.register(HoTro)
class HoTroAdmin(admin.ModelAdmin):
    list_display = ('ho_ten', 'chu_de', 'email', 'sdt', 'thoi_gian', 'da_xu_ly')
    list_filter = ('da_xu_ly', 'chu_de')
    search_fields = ('ho_ten', 'email', 'noi_dung', 'sdt')
    readonly_fields = ('thoi_gian',) # Không cho sửa ngày giờ gửi

# Cho phép thêm ảnh ngay trong trang chỉnh sửa nội dung
class AnhGioiThieuInline(admin.TabularInline):
    model = AnhGioiThieu
    extra = 3 # Hiển thị sẵn 3 ô để up ảnh

@admin.register(GioiThieu)
class GioiThieuAdmin(admin.ModelAdmin):
    inlines = [AnhGioiThieuInline]
    list_display = ('tieu_de', 'ngay_cap_nhat')

@admin.register(QuanHuyen)
class QuanHuyenAdmin(admin.ModelAdmin):
    list_display = ('id', 'ten_quan')
    search_fields = ('ten_quan',)

# 2. Đăng ký Profile để Admin phân công "Lãnh địa" cho nhân viên
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'so_dien_thoai', 'quan_quan_ly')
    list_filter = ('quan_quan_ly',) # Bộ lọc tìm nhanh nhân viên theo quận
    search_fields = ('user__username', 'so_dien_thoai')