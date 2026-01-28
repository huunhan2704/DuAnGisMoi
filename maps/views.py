from django.shortcuts import render
from django.http import JsonResponse
from .models import PhanAnh # Gọi cái kho ra để dùng

# 1. Hàm hiển thị trang chủ (như cũ)
def map_home(request):
    return render(request, 'maps/index.html')

# 2. HÀM MỚI: Nhận dữ liệu từ nút "Gửi"
def luu_phan_anh(request):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ gói tin gửi lên
            tieude = request.POST.get('tieu_de')
            mota = request.POST.get('mo_ta')
            toado = request.POST.get('points_data') # Chuỗi JSON danh sách điểm
            hinh = request.FILES.get('hinh_anh')    # File ảnh (nếu có)

            # Lưu vào Database (Cất vào kho)
            PhanAnh.objects.create(
                tieu_de=tieude,
                mo_ta=mota,
                du_lieu_toa_do=toado,
                hinh_anh=hinh
            )
            
            # Báo lại là OK
            return JsonResponse({'success': True, 'message': 'Gửi phản ánh thành công!'})
            
        except Exception as e:
            # Nếu lỗi thì báo lỗi
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ!'})