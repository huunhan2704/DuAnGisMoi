from django.db import models

class PhanAnh(models.Model):
    # 1. Tiêu đề phản ánh (Ngắn gọn)
    tieu_de = models.CharField(max_length=200, verbose_name="Tiêu đề")
    
    # 2. Mô tả chi tiết (Dài)
    mo_ta = models.TextField(verbose_name="Mô tả chi tiết")
    
    # 3. Dữ liệu tọa độ
    # Ví dụ: "[{'lat':10.1, 'lng':106.1}, {'lat':10.2, 'lng':106.2}]"
    du_lieu_toa_do = models.TextField(verbose_name="Danh sách tọa độ")
    
    # 4. Hình ảnh hiện trường (Cho phép để trống nếu không chụp)
    hinh_anh = models.ImageField(upload_to='hien_truong/', blank=True, null=True, verbose_name="Ảnh hiện trường")
    
    # 5. Thời gian báo cáo (Tự động lấy giờ hiện tại)
    thoi_gian = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian gửi")

    # 6. Trạng thái xử lý (Để Admin quản lý)
    TRANG_THAI_CHOICES = [
        ('cho_duyet', 'Chờ duyệt'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý xong'),
    ]
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='cho_duyet', verbose_name="Trạng thái")

    def __str__(self):
        return self.tieu_de

    class Meta:
        verbose_name = "Tin Phản Ánh"
        verbose_name_plural = "Danh sách Phản Ánh"