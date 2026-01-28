from django.contrib import admin
from .models import PhanAnh

@admin.register(PhanAnh)
class PhanAnhAdmin(admin.ModelAdmin):
    list_display = ('tieu_de', 'thoi_gian', 'trang_thai') # Hiện 3 cột này ra ngoài
    list_filter = ('trang_thai', 'thoi_gian') # Bộ lọc bên phải
    search_fields = ('tieu_de', 'mo_ta') # Thanh tìm kiếm