from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField

# 0. MODEL QUẬN HUYỆN (Danh mục khu vực)
class QuanHuyen(models.Model):
    ten_quan = models.CharField(max_length=100, verbose_name="Tên Khu Vực")
    ranh_gioi = models.MultiPolygonField(srid=4326, verbose_name="Ranh giới", null=True, blank=True)
    mau_sac = models.CharField(max_length=7, default="#3388ff", help_text="Mã màu Hex (VD: #3388ff)")

    def __str__(self):
        return self.ten_quan

    class Meta:
        verbose_name = "Quận/Huyện"
        verbose_name_plural = "Danh sách Quận/Huyện"
# 1. MODEL PHẢN ÁNH
class PhanAnh(models.Model):
    # 1. Tiêu đề
    tieu_de = models.CharField(max_length=200, verbose_name="Tiêu đề")

    # --- 🌟 BƯỚC MỚI: THÊM CỘT PHÂN LOẠI SỰ CỐ ---
    CHUYEN_MON_CHOICES = [
        ('an_ninh', 'An ninh & Cứu nạn'),
        ('dien_luc', 'Điện lực (EVN)'),
        ('cap_thoat_nuoc', 'Cấp thoát nước'),
        ('cay_xanh', 'Công viên Cây xanh'),
        ('chieu_sang', 'Chiếu sáng Đô thị'),
        ('giao_thong', 'Hạ tầng Giao thông'),
        ('khac', 'Khác'), 
    ]
    loai_su_co = models.CharField(
        max_length=50, 
        choices=CHUYEN_MON_CHOICES, 
        default='khac', 
        verbose_name="Thuộc lĩnh vực"
    )

    # 2. Mô tả
    mo_ta = models.TextField(verbose_name="Mô tả chi tiết")
    dia_chi = models.CharField(max_length=200, blank=True, null=True, verbose_name="Địa chỉ/Tên đường")
    
    #  Phản ánh này thuộc Quận nào
    quan_huyen = models.ForeignKey(QuanHuyen, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Thuộc Quận/Huyện")
    
    # 3. Tọa độ
    du_lieu_toa_do = models.TextField(verbose_name="Danh sách tọa độ")
    
    # 4. Hình ảnh
    vi_tri = models.PointField(srid=4326, null=True, blank=True, verbose_name="Tọa độ chuẩn GIS")
    hinh_anh = models.ImageField(upload_to='hien_truong/', blank=True, null=True, verbose_name="Ảnh hiện trường")
    
    # 5. Thời gian
    thoi_gian = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian gửi")

    # 6. Trạng thái
    TRANG_THAI_CHOICES = [
        ('cho_duyet', 'Chờ duyệt'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý xong'),
    ]
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='cho_duyet', verbose_name="Trạng thái")

    # 7. NGƯỜI GỬI
    nguoi_gui = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.tieu_de

    class Meta:
        verbose_name = "Tin Phản Ánh"
        verbose_name_plural = "Danh sách Phản Ánh"

    # 8. THÙNG RÁC
    da_xoa = models.BooleanField(default=False, verbose_name="Đã chuyển vào thùng rác")
    ngay_xoa = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xóa")
# 2. MODEL PROFILE
class Profile(models.Model):
    # --- 🌟 DANH SÁCH 6 CHUYÊN MÔN (VÀ 1 CÁI TỔNG HỢP CHO ADMIN) ---
    CHUYEN_MON_CHOICES = [
        ('an_ninh', 'An ninh & Cứu nạn'),
        ('dien_luc', 'Điện lực (EVN)'),
        ('cap_thoat_nuoc', 'Cấp thoát nước'),
        ('cay_xanh', 'Công viên Cây xanh'),
        ('chieu_sang', 'Chiếu sáng Đô thị'),
        ('giao_thong', 'Hạ tầng Giao thông'),
        ('tong_hop', 'Quản lý Tổng hợp'), # Mặc định
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    so_dien_thoai = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True, verbose_name="Ảnh đại diện") 
    
    # Cấp quyền nhân viên quản lý quận nào
    quan_quan_ly = models.ForeignKey(QuanHuyen, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Quận/Huyện quản lý (Dành cho nhân viên)")
    
    # --- 🌟 CỘT CHUYÊN MÔN VỪA THÊM MỚI ---
    chuyen_mon = models.CharField(
        max_length=50, 
        choices=CHUYEN_MON_CHOICES, 
        default='tong_hop', 
        verbose_name="Chuyên môn phụ trách"
    )
    
    def __str__(self):
        # Nâng cấp hàm in ra cho dễ nhìn trong Admin
        if self.quan_quan_ly:
            return f"Profile của {self.user.username} - {self.get_chuyen_mon_display()} (Quản lý: {self.quan_quan_ly.ten_quan})"
        return f"Profile của {self.user.username} - {self.get_chuyen_mon_display()}"
    
# 3. SIGNAL TỰ ĐỘNG (ĐÃ SỬA LỖI ADMIN CŨ)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        # Cố gắng lưu Profile nếu đã có
        instance.profile.save()
    except Profile.DoesNotExist:
        # Nếu chưa có (như ông Admin cũ này) thì TẠO MỚI luôn
        Profile.objects.create(user=instance)
        
# 4. HỖ TRỢ CSKH
class HoTro(models.Model):
    CHU_DE_CHOICES = [
        ('tai_khoan', '🔑 Lỗi tài khoản / Đăng nhập'),
        ('sai_hien_trang', '⚠️ Báo cáo sai hiện trạng'),
        ('huong_dan', '📘 Cần hướng dẫn sử dụng'),
        ('gop_y', '💡 Góp ý tính năng mới'),
        ('khac', '💬 Khác'),
    ]
    
    # Người gửi (có thể để trống nếu họ chưa đăng nhập được)
    nguoi_gui = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ho_ten = models.CharField(max_length=100, verbose_name="Họ tên người gửi")
    email = models.EmailField(verbose_name="Email liên hệ")
    sdt = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    
    chu_de = models.CharField(max_length=50, choices=CHU_DE_CHOICES, default='khac')
    noi_dung = models.TextField(verbose_name="Nội dung chi tiết")
    
    # Trạng thái xử lý của Admin
    da_xu_ly = models.BooleanField(default=False, verbose_name="Đã xử lý xong?")
    phan_hoi_admin = models.TextField(blank=True, null=True, verbose_name="Admin trả lời")
    thoi_gian = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Yêu cầu Hỗ trợ"
        verbose_name_plural = "Danh sách Hỗ trợ"

    def __str__(self):
        return f"[{self.get_chu_de_display()}] - {self.ho_ten}"
    
# 5. KHO CHỨA NHIỀU HÌNH ẢNH CHO PHẢN ÁNH
class HinhAnhPhanAnh(models.Model):
    # Liên kết với bảng PhanAnh (Khi xóa Phản ánh thì xóa luôn ảnh)
    phan_anh = models.ForeignKey(PhanAnh, on_delete=models.CASCADE, related_name='danh_sach_anh')
    
    # Cột chứa file ảnh
    hinh_anh = models.ImageField(upload_to='hien_truong/chi_tiet/', verbose_name="Ảnh chi tiết")
    
    ngay_tai_len = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hình Ảnh Phản Ánh"
        verbose_name_plural = "Danh sách Hình Ảnh Chi Tiết"

    def __str__(self):
        return f"Ảnh phụ của sự cố: {self.phan_anh.tieu_de}"
    
class GioiThieu(models.Model):
    tieu_de = models.CharField(max_length=200, verbose_name="Tiêu đề chính")
    mo_ta_ngan = models.TextField(verbose_name="Mô tả ngắn (Slogan)")
    # Sử dụng RichTextField để có thanh công cụ định dạng
    noi_dung_chi_tiet = RichTextUploadingField(verbose_name="Nội dung chi tiết")
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quản lý Giới thiệu"
        verbose_name_plural = "Quản lý Giới thiệu"

    def __str__(self):
        return self.tieu_de

# Model mới để lưu nhiều ảnh cho Slide
class AnhGioiThieu(models.Model):
    gioi_thieu = models.ForeignKey(GioiThieu, related_name='images', on_delete=models.CASCADE)
    hinh_anh = models.ImageField(upload_to='gioi_thieu/', verbose_name="Hình ảnh Slide")
    mo_ta_anh = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mô tả ảnh")

    class Meta:
        verbose_name = "Hình ảnh Giới thiệu"
        verbose_name_plural = "Danh sách ảnh Slide"