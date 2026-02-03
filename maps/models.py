from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- 1. MODEL PHẢN ÁNH ---
class PhanAnh(models.Model):
    # 1. Tiêu đề
    tieu_de = models.CharField(max_length=200, verbose_name="Tiêu đề")
    
    # 2. Mô tả
    mo_ta = models.TextField(verbose_name="Mô tả chi tiết")
    

    # ===> THÊM MỚI CỘT ĐỊA CHỈ TẠI ĐÂY <===
    dia_chi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ/Tên đường")
    
    # 3. Tọa độ
    du_lieu_toa_do = models.TextField(verbose_name="Danh sách tọa độ")
    
    # 4. Hình ảnh
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
    
# --- 2. MODEL PROFILE ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    so_dien_thoai = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True, verbose_name="Ảnh đại diện")

    def __str__(self):
        return f"Profile của {self.user.username}"

# --- 3. SIGNAL TỰ ĐỘNG (ĐÃ SỬA LỖI ADMIN CŨ) ---
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