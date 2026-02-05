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
import csv
from django.http import HttpResponse
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from .models import HoTro
from django.contrib import messages


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
            
            # ===> LẤY ĐỊA CHỈ DÂN NHẬP <===
            diachi = request.POST.get('dia_chi') 
            
            hinh = request.FILES.get('hinh_anh')

            # Tạo đối tượng
            new_pa = PhanAnh(
                tieu_de=tieude,
                mo_ta=mota,
                
                # ===> LƯU VÀO DATABASE <===
                dia_chi=diachi,
                
                du_lieu_toa_do=toado,
                hinh_anh=hinh
            )

            # Nếu người dùng đang đăng nhập -> Gán tên họ vào hồ sơ
            if request.user.is_authenticated:
                new_pa.nguoi_gui = request.user
            
            # Lưu xuống Database
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
# Bổ sung các hàm bị thiếu
def trang_thong_ke(request):
    from django.contrib.auth.models import User
    tong_so = PhanAnh.objects.count()
    cho_duyet = PhanAnh.objects.filter(trang_thai='cho_duyet').count()
    dang_xu_ly = PhanAnh.objects.filter(trang_thai='dang_xu_ly').count()
    da_xu_ly = PhanAnh.objects.filter(trang_thai='da_xu_ly').count()
    ty_le = 0
    if tong_so > 0: ty_le = round((da_xu_ly / tong_so) * 100, 1)

    context = {'tong_so': tong_so, 'cho_duyet': cho_duyet, 'dang_xu_ly': dang_xu_ly, 'da_xu_ly': da_xu_ly, 'ty_le': ty_le, 'so_nguoi_dung': User.objects.count(), 'bai_moi': PhanAnh.objects.all().order_by('-id')[:5]}
    return render(request, 'maps/thong_ke.html', context)

@login_required
def cap_nhat_trang_thai(request, id_phan_anh, trang_thai_moi):
    phan_anh = get_object_or_404(PhanAnh, id=id_phan_anh)
    phan_anh.trang_thai = trang_thai_moi
    phan_anh.save()
    return redirect('quan_ly_hien_truong')

def api_get_points(request):
    danh_sach = PhanAnh.objects.exclude(trang_thai='cho_duyet')
    data = []
    for item in danh_sach:
        lat, lng = 0, 0
        try:
            if item.du_lieu_toa_do:
                parts = item.du_lieu_toa_do.split(',')
                lat, lng = float(parts[0].strip()), float(parts[1].strip())
        except: pass
        data.append({'id': item.id, 'title': item.tieu_de, 'lat': lat, 'lng': lng, 'status': item.trang_thai, 'image_url': item.hinh_anh.url if item.hinh_anh else '', 'detail_url': f"/chi-tiet/{item.id}/"})
    return JsonResponse(data, safe=False)


def quan_ly_hien_truong(request):
    # Lấy các điểm ĐANG XỬ LÝ (đang thi công)
    danh_sach = PhanAnh.objects.filter(trang_thai='dang_xu_ly').order_by('-thoi_gian')
    
    context = {
        'danh_sach': danh_sach,
        'so_luong': danh_sach.count()
    }
    return render(request, 'maps/quan_ly_hien_truong.html', context)

def export_excel(request):
    # 1. Cấu hình response là file CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bao_cao_su_co.csv"'
    
    # 2. Fix lỗi font tiếng Việt (BOM header)
    response.write(u'\ufeff'.encode('utf8')) 

    # 3. Tạo bút ghi
    writer = csv.writer(response)
    
    # 4. Ghi dòng tiêu đề
    writer.writerow(['ID', 'Tiêu đề', 'Tọa độ', 'Thời gian', 'Trạng thái'])

    # 5. Lấy dữ liệu và ghi từng dòng
    for pa in PhanAnh.objects.all().order_by('-id'):
        writer.writerow([
            pa.id, 
            pa.tieu_de, 
            pa.du_lieu_toa_do, 
            pa.thoi_gian.strftime("%d/%m/%Y %H:%M"), 
            pa.get_trang_thai_display()
        ])

    return response


def tin_tuc(request):
    # Link RSS VnExpress
    rss_url = "https://vnexpress.net/rss/thoi-su.rss"
    feed = feedparser.parse(rss_url)
    
    # Bộ lọc từ khóa (Giữ nguyên)
    keywords = [
        'giao thông', 'đô thị', 'ngập', 'kẹt xe', 'ùn tắc', 
        'cầu', 'đường', 'hầm', 'chung cư', 'quy hoạch', 
        'môi trường', 'rác', 'metro', 'xe buýt', 'vỉa hè',
        'cây xanh', 'chiếu sáng', 'hcm', 'sài gòn', 'quận'
    ]

    posts = []
    for entry in feed.entries:
        content_to_check = (entry.title + entry.description).lower()
        
        if any(word in content_to_check for word in keywords):
            # XỬ LÝ ẢNH BẰNG BEAUTIFULSOUP (MỚI & XỊN) 
            image_url = 'https://s1.vnecdn.net/vnexpress/restruct/i/v884/logo_default.jpg' # Hình mặc định
            
            # Dùng "cái muỗng" để múc nội dung HTML trong phần mô tả
            soup = BeautifulSoup(entry.description, 'lxml')
            
            # Tìm thẻ <img> đầu tiên
            img_tag = soup.find('img')
            
            # Nếu tìm thấy thẻ img và nó có thuộc tính src (link ảnh)
            if img_tag and img_tag.get('src'):
                image_url = img_tag.get('src')

            # XỬ LÝ MÔ TẢ CHO SẠCH SẼ 
            # Dùng soup.get_text() để lấy toàn bộ chữ, bỏ hết các thẻ HTML thừa
            summary_text = soup.get_text()
            
            # Cắt bỏ mấy cái chữ thừa ở cuối nếu có (ví dụ ">> Chi tiết")
            if '>>' in summary_text:
                summary_text = summary_text.split('>>')[0]

            posts.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'summary': summary_text.strip(), # Xóa khoảng trắng thừa đầu đuôi
                'image': image_url
            })

        if len(posts) >= 12:
            break

    return render(request, 'maps/tin_tuc.html', {'news_list': posts})


def huong_dan(request):
    return render(request, 'maps/huong_dan.html')



def hotline(request):
    return render(request, 'maps/hotline.html')


def xoa_phan_anh(request, pk):
    # 1. Tìm phản ánh theo ID và phải đúng là của người đang đăng nhập gửi (nguoi_gui=request.user)
    # Để tránh ông A xóa trộm bài của ông B
    pa = get_object_or_404(PhanAnh, pk=pk, nguoi_gui=request.user)
    
    # 2. Kiểm tra trạng thái: Chỉ cho xóa khi "Chờ tiếp nhận"
    if pa.trang_thai == 'cho_duyet':
        pa.delete()
        messages.success(request, "✅ Đã xóa phản ánh thành công!")
    else:
        messages.error(request, "⚠️ Không thể xóa phản ánh đang hoặc đã xử lý!")
        
    return redirect('profile')

def cskh(request):
    if request.method == 'POST':
        # 1. Lấy dữ liệu từ form người dùng gửi lên
        ho_ten = request.POST.get('ho_ten')
        email = request.POST.get('email')
        sdt = request.POST.get('sdt')
        chu_de = request.POST.get('chu_de')
        noi_dung = request.POST.get('noi_dung')

        # 2. Tạo phiếu hỗ trợ mới
        phieu = HoTro(
            ho_ten=ho_ten,
            email=email,
            sdt=sdt,
            chu_de=chu_de,
            noi_dung=noi_dung
        )
        
        # Nếu người dùng đang đăng nhập, gắn luôn user vào để dễ theo dõi
        if request.user.is_authenticated:
            phieu.nguoi_gui = request.user
            
        phieu.save()

        # 3. Thông báo thành công
        messages.success(request, "Đã gửi yêu cầu hỗ trợ! Chúng tôi sẽ phản hồi qua Email sớm nhất.")
        return redirect('cskh') # Load lại trang để xóa form

    return render(request, 'maps/cskh.html')

