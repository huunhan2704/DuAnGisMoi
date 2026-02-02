from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import PhanAnh
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import DangKyForm 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import DangKyForm, UserEditForm, ProfileEditForm 
from .models import Profile

# 1. Trang chủ
def home(request):
    return render(request, 'maps/home.html')

# 2. Trang Bản đồ
def map_home(request):
    # Lấy dữ liệu điểm cũ ra để hiển thị
    danh_sach = PhanAnh.objects.all()
    return render(request, 'maps/index.html', {'phan_anh': danh_sach})

# 3. Trang Danh sách
def list_view(request):
    danh_sach = PhanAnh.objects.all().order_by('-id') # Sửa thành -id để bài mới nhất lên đầu
    return render(request, 'maps/list.html', {'phan_anh': danh_sach})

# 4. ĐĂNG KÝ
def register_view(request):
    if request.method == 'POST':
        form = DangKyForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('map_home')
    else:
        form = DangKyForm()
    return render(request, 'maps/register.html', {'form': form})

# 5. ĐĂNG NHẬP
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('map_home')
    else:
        form = AuthenticationForm()
    return render(request, 'maps/login.html', {'form': form})

# 6. ĐĂNG XUẤT
def logout_view(request):
    logout(request)
    return redirect('login')

# 7. API Lưu phản ánh (ĐÃ SỬA: LƯU NGƯỜI GỬI)
def luu_phan_anh(request):
    if request.method == 'POST':
        try:
            tieude = request.POST.get('tieu_de')
            mota = request.POST.get('mo_ta')
            toado = request.POST.get('points_data')
            hinh = request.FILES.get('hinh_anh')

            # Tạo đối tượng nhưng chưa lưu ngay
            new_pa = PhanAnh(
                tieu_de=tieude,
                mo_ta=mota,
                du_lieu_toa_do=toado,
                hinh_anh=hinh
            )

            # Nếu người dùng đang đăng nhập -> Gán tên họ vào hồ sơ
            if request.user.is_authenticated:
                new_pa.nguoi_gui = request.user
            
            # Giờ mới lưu xuống Database
            new_pa.save()

            return JsonResponse({'success': True, 'message': 'Gửi phản ánh thành công!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ!'})

# 8. TRANG HỒ SƠ CÁ NHÂN (ĐÃ SỬA: LỌC ĐÚNG CỘT nguoi_gui)
@login_required
def profile(request):
    # Dùng .filter(nguoi_gui=...) thay vì user=...
    danh_sach = PhanAnh.objects.filter(nguoi_gui=request.user).order_by('-id')
    
    context = {
        'user': request.user,
        'danh_sach': danh_sach,
        'tong_so': danh_sach.count()
    }
    return render(request, 'maps/profile.html', context)

@login_required
def chi_tiet_ho_so(request, id_ho_so):
    # Lấy hồ sơ theo ID, nếu không thấy thì báo lỗi 404
    ho_so = get_object_or_404(PhanAnh, id=id_ho_so)
    
    # Bảo mật: Chỉ cho xem nếu là chủ sở hữu (hoặc Admin sau này)
    # Nếu không phải chủ -> Báo lỗi hoặc đá về trang chủ (Ở đây mình tạm bỏ qua để test cho dễ)
    
    return render(request, 'maps/detail.html', {'ho_so': ho_so})


@login_required
def edit_profile(request):
    # Đảm bảo user luôn có profile (tránh lỗi cho user cũ)
    Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'maps/edit_profile.html', context)