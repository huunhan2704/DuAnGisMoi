from django.contrib import admin
from .models import PhanAnh, HoTro

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