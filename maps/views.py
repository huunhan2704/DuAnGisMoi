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
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
import json
from .models import PhanAnh, HinhAnhPhanAnh

#trang admin 
@staff_member_required(login_url='login') 
def trang_quan_ly(request):
    # Lấy dữ liệu từ bảng PhanAnh và HoTro và User 
    ds_phan_anh = PhanAnh.objects.all().prefetch_related('danh_sach_anh').order_by('-id')
    ds_ho_tro = HoTro.objects.all().order_by('-id')
    ds_user = User.objects.all().order_by('-id')
    
    context = {
        'ds_phan_anh': ds_phan_anh,
        'ds_ho_tro': ds_ho_tro,
        'ds_user': ds_user,
    }
    return render(request, 'maps/quan_ly.html', context)

@staff_member_required(login_url='login')
def duyet_phan_anh(request, id):
    # Tìm phản ánh theo ID
    phan_anh = get_object_or_404(PhanAnh, id=id)
    
    # Nếu đang chờ duyệt thì chuyển sang đang xử lý
    if phan_anh.trang_thai == 'cho_duyet':
        phan_anh.trang_thai = 'dang_xu_ly'
    # Nếu đang xử lý thì chuyển sang đã xử lý xong
    elif phan_anh.trang_thai == 'dang_xu_ly':
        phan_anh.trang_thai = 'da_xu_ly'
        
    phan_anh.save()
    return redirect('trang_quan_ly') # Làm xong thì load lại trang quản lý

@staff_member_required(login_url='login')
def xoa_phan_anh(request, id):
    phan_anh = get_object_or_404(PhanAnh, id=id)
    phan_anh.delete() # Lệnh xóa khỏi Database
    return redirect('trang_quan_ly')

@staff_member_required(login_url='login')
def khoa_user(request, id):
    user_can_khoa = get_object_or_404(User, id=id)
    
    # BẢO HIỂM: Không cho phép tự khóa Admin Tổng (chống tự hủy)
    if not user_can_khoa.is_superuser: 
        user_can_khoa.is_active = not user_can_khoa.is_active  # Đảo ngược trạng thái
        user_can_khoa.save()
        
    return redirect('trang_quan_ly')

@staff_member_required(login_url='login')
def xoa_user(request, id):
    user_can_xoa = get_object_or_404(User, id=id)
    
    # BẢO HIỂM: Không cho phép tự xóa Admin Tổng
    if not user_can_xoa.is_superuser:
        user_can_xoa.delete()
        
    return redirect('trang_quan_ly')

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
            # --- 1. LẤY DỮ LIỆU TỪ FORM ---
            tieude = request.POST.get('tieu_de')
            mota = request.POST.get('mo_ta')
            toado = request.POST.get('points_data')
            diachi = request.POST.get('dia_chi') 
            
            # --- 2. KHỞI TẠO ĐỐI TƯỢNG PHẢN ÁNH ---
            new_pa = PhanAnh(
                tieu_de=tieude,
                mo_ta=mota,
                dia_chi=diachi,
                du_lieu_toa_do=toado,
            )

            # --- 3. XỬ LÝ TỌA ĐỘ (POSTGIS) ---
            if toado and toado != "[]":
                try:
                    points_list = json.loads(toado)
                    if len(points_list) > 0:
                        # Lấy điểm đầu tiên làm tọa độ chính
                        lat = float(points_list[0]['lat'])
                        lng = float(points_list[0]['lng'])
                        new_pa.vi_tri = Point(lng, lat, srid=4326)
                except Exception as e:
                    print("⚠️ Lỗi chuyển đổi PostGIS:", e)

            # Gắn người dùng nếu đã đăng nhập
            if request.user.is_authenticated:
                new_pa.nguoi_gui = request.user
            
            # Lưu vào Database lần 1 để lấy ID của Phản ánh
            new_pa.save()

            # --- 4. XỬ LÝ LƯU NHIỀU HÌNH ẢNH (BỘ LỌC THÔNG MINH) ---
            # Dùng 'getlist' để hốt toàn bộ file gửi lên từ khóa 'hinh_anh'
            danh_sach_hinh = request.FILES.getlist('hinh_anh')
            
            # --- MÁY QUÉT X-QUANG (DEBUG TRÊN TERMINAL) ---
            print("\n" + "="*40)
            print(f"🚀 THÔNG TIN NHẬN ĐƯỢC:")
            print(f"👉 Tiêu đề: {tieude}")
            print(f"👉 Số lượng ảnh nhận được: {len(danh_sach_hinh)} file")
            print("="*40)
            
            if danh_sach_hinh:
                # A. Lấy tấm đầu tiên làm ảnh đại diện (Hiển thị ngoài danh sách)
                new_pa.hinh_anh = danh_sach_hinh[0]
                new_pa.save() # Cập nhật lại ảnh đại diện
                print("✅ 1. Đã lưu Ảnh đại diện.")
                
                # B. Lưu các tấm còn lại vào Kho ảnh phụ (HinhAnhPhanAnh)
                # Dùng [1:] để bỏ qua tấm đầu tiên đã lưu ở trên, tránh bị trùng lặp
                dem_anh_phu = 0
                for file_anh in danh_sach_hinh[1:]:
                    HinhAnhPhanAnh.objects.create(
                        phan_anh=new_pa, 
                        hinh_anh=file_anh
                    )
                    dem_anh_phu += 1
                
                print(f"✅ 2. Đã lưu thêm {dem_anh_phu} ảnh vào kho phụ.")
                print("="*40 + "\n")

            return JsonResponse({'success': True, 'message': 'Gửi phản ánh thành công!'})
        
        except Exception as e:
            # In lỗi chi tiết ra màn hình Terminal nếu có sự cố ngầm
            print(f"❌ LỖI HỆ THỐNG: {str(e)}")
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
    # Lấy hồ sơ kèm theo toàn bộ ảnh trong kho phụ 'danh_sach_anh'
    ho_so = get_object_or_404(PhanAnh.objects.prefetch_related('danh_sach_anh'), id=id_ho_so)
    
    # Ở đây ông dùng tên file là 'maps/detail.html'
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
from django.contrib.gis.measure import D

def api_quet_vung_postgis(request):
    """
    TOOL GIS BACKEND: Tìm các sự cố nằm trong vòng tròn bán kính R 
    (Sử dụng hàm __distance_lte của PostGIS)
    """
    # 1. Nhận tọa độ tâm và bán kính từ Frontend gửi lên (mặc định lấy chợ Bến Thành)
    lat = float(request.GET.get('lat', 10.7725))
    lng = float(request.GET.get('lng', 106.6980))
    ban_kinh_met = float(request.GET.get('radius', 500)) 

    # 2. Tạo điểm tâm (Nhớ là Kinh độ trước, Vĩ độ sau)
    tam_diem = Point(lng, lat, srid=4326)

    # 3. QUAN TRỌNG NHẤT: Truy vấn DB bằng hàm không gian của GeoDjango/PostGIS
    ds_su_co = PhanAnh.objects.filter(
        vi_tri__distance_lte=(tam_diem, D(m=ban_kinh_met))
    )

    # 4. Trả kết quả ra dạng JSON
    data = []
    for sc in ds_su_co:
        data.append({
            'id': sc.id,
            'tieu_de': sc.tieu_de,
            # Tính luôn khoảng cách thực tế từ tâm đến điểm đó để show ra báo cáo
            'khoang_cach': round(sc.vi_tri.distance(tam_diem) * 100000, 2) # Nhân để đổi ra mét tương đối
        })

    return JsonResponse({'tam_diem': {'lat': lat, 'lng': lng}, 'tong_so': len(data), 'du_lieu': data})

@staff_member_required(login_url='login')
def tra_loi_ho_tro(request, id):
    # 1. Tìm cái yêu cầu hỗ trợ theo ID
    ht = get_object_or_404(HoTro, id=id)

    if request.method == 'POST':
        # 2. Lấy nội dung Admin nhập từ form
        noidung_admin_tra_loi = request.POST.get('noidung_phan_hoi')

        # 3. GÓI GHÉM VÀ GỬI EMAIL BẰNG MAILTRAP
        tieu_de = f"[Urban Manager] Phản hồi yêu cầu hỗ trợ #{ht.id}"
        loi_nhan = f"""Chào {ht.ho_ten},

Chúng tôi đã nhận được yêu cầu của bạn về vấn đề: {ht.get_chu_de_display()}.
Nội dung bạn gửi: "{ht.noi_dung}"

PHẢN HỒI TỪ BAN QUẢN TRỊ:
{noidung_admin_tra_loi}

Trân trọng,
Đội ngũ Urban Manager.
"""
        # Bấm nút gửi!
        send_mail(
            subject=tieu_de,
            message=loi_nhan,
            from_email='admin@urbanmanager.com', 
            recipient_list=[ht.email], 
            fail_silently=False,
        )

        # 4. Cập nhật lại Database
        ht.da_xu_ly = True
        ht.phan_hoi_admin = noidung_admin_tra_loi
        ht.save()

        # Báo cáo thành công và quay về trang quản lý của ông (tên là trang_quan_ly)
        messages.success(request, f'Đã gửi email trả lời cho {ht.ho_ten} thành công!')
        return redirect('trang_quan_ly') 

    # Nếu chưa bấm gửi thì gọi cái giao diện soạn thư ra
    return render(request, 'maps/tra_loi_ho_tro.html', {'ht': ht})
