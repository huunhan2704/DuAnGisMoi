from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .models import GioiThieu

# 1. FORM ĐĂNG KÝ (Cũ - Giữ nguyên)
class DangKyForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Địa chỉ Email") 

    class Meta:
        model = User
        fields = ("username", "email") 
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng rồi!")
        return email

# 2. FORM SỬA THÔNG TIN CÁ NHÂN (Mới - Ông đang thiếu cái này nè)
class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Địa chỉ Email")
    first_name = forms.CharField(max_length=30, label="Tên", required=False)
    last_name = forms.CharField(max_length=30, label="Họ", required=False)

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email')
    
# 3. FORM SỬA AVATAR & SĐT (Cũ - Giữ nguyên)
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('so_dien_thoai', 'avatar')
        
class GioiThieuForm(forms.ModelForm):
    class Meta:
        model = GioiThieu
        # Chỗ này cực kỳ quan trọng: Phải liệt kê tên các cột ông muốn hiện ra
        fields = ['tieu_de', 'mo_ta_ngan', 'noi_dung_chi_tiet']
        
        # Cái này giúp giao diện form nhìn xịn xò chuẩn Bootstrap
        widgets = {
            'tieu_de': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nhập tiêu đề chính...'
            }),
            'mo_ta_ngan': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Nhập mô tả ngắn gọn (Slogan)...'
            }),
            # Ô noi_dung_chi_tiet ông đang dùng ckeditor nên không cần widget
        }