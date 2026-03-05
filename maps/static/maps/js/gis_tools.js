// # 1. CÔNG CỤ CHỈ ĐƯỜNG (ROUTING)
// Chức năng: Lấy vị trí GPS hiện tại của người dùng và vẽ đường đi ngắn nhất đến điểm sự cố.
function veDuongDi(diemDenLat, diemDenLng) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var viTriCuaToi = L.latLng(position.coords.latitude, position.coords.longitude);
                var diemDen = L.latLng(diemDenLat, diemDenLng);

                // Xóa đường đi cũ nếu có
                if (routingControl != null) map.removeControl(routingControl);

                // Gọi API của OSRM để vẽ đường
                routingControl = L.Routing.control({
                    waypoints: [viTriCuaToi, diemDen],
                    routeWhileDragging: false,
                    language: 'en', // Đã sửa thành tiếng Anh để không bị lỗi
                    showAlternatives: true,
                    router: L.Routing.osrmv1({ serviceUrl: 'https://router.project-osrm.org/route/v1' }),
                    createMarker: function(i, w, n) {
                        var c = (i === 0) ? '#198754' : '#dc3545'; 
                        var t = (i === 0) ? '📍 Vị trí thật của bạn' : '⚠️ Điểm sự cố';
                        return L.circleMarker(w.latLng, { color: 'white', fillColor: c, fillOpacity: 1, radius: 8, weight: 2 }).bindPopup(t).openPopup();
                    },
                    lineOptions: { styles: [{color: '#0d6efd', opacity: 0.8, weight: 6}] }
                }).addTo(map);
            }, 
            function(error) {
                console.log("Trình duyệt báo lỗi GPS ngầm: " + error.message);
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        alert("Trình duyệt không hỗ trợ GPS.");
    }
}

// # 2. CÔNG CỤ NỘI SUY BẢN ĐỒ NHIỆT (HEATMAP INTERPOLATION)
// Chức năng: Tạo các điểm ảo (nội suy) nằm giữa các điểm thật để vẽ bản đồ nhiệt liền mạch, mượt mà hơn.
function addSeamlessHeatmap(targetArray, coords) {
    if (coords.length === 0) return;
    if (coords.length === 1) { targetArray.push([coords[0].lat, coords[0].lng, 1.0]); return; }
    for (let i = 0; i < coords.length; i++) {
        targetArray.push([coords[i].lat, coords[i].lng, 1.0]);
        if (i < coords.length - 1) {
            let p1 = coords[i], p2 = coords[i+1];
            // Cắt nhỏ khoảng cách làm 4 phần để vẽ
            for (let j = 1; j < 4; j++) { 
                let lat = p1.lat + (p2.lat - p1.lat) * (j / 4);
                let lng = p1.lng + (p2.lng - p1.lng) * (j / 4);
                targetArray.push([lat, lng, 1.0]); 
            }
        }
    }
}

// # 3. HIỂN THỊ DỮ LIỆU LÊN BẢN ĐỒ (RENDER MAP)
// Chức năng: Đọc dữ liệu từ Database, phân loại theo trạng thái (màu sắc), tạo Marker và Popup gắn lên bản đồ.
function renderMap(dataToRender) {
    lopChoDuyet.clearLayers(); lopDangXuLy.clearLayers(); lopDaXong.clearLayers();
    var tmpChoDuyet = [], tmpDangXuLy = [], tmpDaXong = [];

    dataToRender.forEach(function(item) {
        if (Array.isArray(item.coords) && item.coords.length > 0) {
            // Phân loại điểm cho bản đồ nhiệt
            if (item.status_code === 'da_xu_ly') addSeamlessHeatmap(tmpDaXong, item.coords);
            else if (item.status_code === 'dang_xu_ly') addSeamlessHeatmap(tmpDangXuLy, item.coords);
            else addSeamlessHeatmap(tmpChoDuyet, item.coords);

            item.coords.forEach(function(c) {
                var color = '#dc3545', targetLayer = lopChoDuyet;
                if (item.status_code === 'da_xu_ly') { color = '#198754'; targetLayer = lopDaXong; }
                else if (item.status_code === 'dang_xu_ly') { color = '#ffc107'; targetLayer = lopDangXuLy; }

                // ĐÃ FIX LỖI LINK GOOGLE MAPS Ở DƯỚI ĐÂY
                var googleMapsLink = `https://www.google.com/maps?q=${c.lat},${c.lng}`;
                var popupContent = `
                    <div class="popup-header">${item.title}</div>
                    <div class="popup-body">
                        <span class="badge text-dark popup-status mb-2" style="background:${color}; color:white!important;">${item.status_text}</span>
                        ${ item.image ? "<img src='" + item.image + "' class='popup-img'>" : "" }
                        <hr class="my-2">
                        <button onclick="veDuongDi(${c.lat}, ${c.lng})" class="btn btn-sm btn-outline-primary w-100 fw-bold">
                            <i class="fa-solid fa-directions me-1"></i> Chỉ đường đi
                        </button>
                    </div>`;
                    
                var marker = L.circleMarker([c.lat, c.lng], { color: 'white', fillColor: color, fillOpacity: 1, radius: 8, weight: 2 }).bindPopup(popupContent);
                targetLayer.addLayer(marker);
            });
        }
    });

    arrChoDuyet = tmpChoDuyet; arrDangXuLy = tmpDangXuLy; arrDaXong = tmpDaXong;
    if(heatLayerChoDuyet) heatLayerChoDuyet.setLatLngs(arrChoDuyet);
    if(heatLayerDangXuLy) heatLayerDangXuLy.setLatLngs(arrDangXuLy);
    if(heatLayerDaXong) heatLayerDaXong.setLatLngs(arrDaXong);
    
    syncHeatmap(); 
}

// # 4. ĐỒNG BỘ NÚT BẬT/TẮT BẢN ĐỒ NHIỆT
// Chức năng: Kiểm tra xem người dùng có đang gạt nút xem Bản đồ nhiệt không để ẩn/hiện lớp nhiệt.
function syncHeatmap() {
    var isMasterOn = document.getElementById('toggleHeatmap').checked;
    if (isMasterOn && map.hasLayer(lopChoDuyet)) { if (!map.hasLayer(heatLayerChoDuyet)) map.addLayer(heatLayerChoDuyet); } else { map.removeLayer(heatLayerChoDuyet); }
    if (isMasterOn && map.hasLayer(lopDangXuLy)) { if (!map.hasLayer(heatLayerDangXuLy)) map.addLayer(heatLayerDangXuLy); } else { map.removeLayer(heatLayerDangXuLy); }
    if (isMasterOn && map.hasLayer(lopDaXong)) { if (!map.hasLayer(heatLayerDaXong)) map.addLayer(heatLayerDaXong); } else { map.removeLayer(heatLayerDaXong); }
}

// # 5. KHỞI TẠO BỘ LỌC DANH MỤC
// Chức năng: Tự động gom nhóm các loại sự cố (ổ gà, rác thải...) để tạo thành menu Dropdown (Bộ lọc).
function initCategoryDropdown() {
    var container = document.getElementById('categoryList');
    var standardTypes = [
        "Đường hư / Ổ gà", "Nắp cống hư hỏng", "Biển báo hư hỏng",
        "Cây ngã đổ", "Ngập nước", "Rác thải bừa bãi",
        "Đèn đường hư", "Sự cố dây điện", "Lấn chiếm vỉa hè", "Khác"
    ];
    var existingTypes = allData.map(item => item.title);
    var allTypes = [...new Set([...standardTypes, ...existingTypes])].sort();

    allTypes.forEach(type => {
        var div = document.createElement('div');
        div.className = 'multi-select-item';
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = type;
        checkbox.id = 'cat_' + type.replace(/\s+/g, '_');
        checkbox.onchange = function() { updateSelectedCategories(); };
        var label = document.createElement('label');
        label.htmlFor = checkbox.id;
        label.innerText = type;
        div.appendChild(checkbox);
        div.appendChild(label);
        div.onclick = function(e) { if (e.target.tagName !== 'INPUT') { checkbox.checked = !checkbox.checked; updateSelectedCategories(); } e.stopPropagation(); };
        container.appendChild(div);
    });
}
initCategoryDropdown();

// # 6. CẬP NHẬT BỘ LỌC & KÍCH HOẠT VÙNG ĐỆM
// Chức năng: Ghi nhận người dùng đang tick chọn loại sự cố nào, sau đó gọi hàm vẽ vùng đệm.
function updateSelectedCategories() {
    selectedCategories = [];
    var checkboxes = document.querySelectorAll('#categoryList input:checked');
    checkboxes.forEach(cb => selectedCategories.push(cb.value));

    var btnText = document.querySelector('#categoryDropdownBtn span');
    if (selectedCategories.length === 0) {
        btnText.innerText = "📍 Chọn loại sự cố đang xử lý...";
        exitGisMode(); // Reset nếu không chọn gì
    } else {
        btnText.innerText = `Đã chọn ${selectedCategories.length} loại`;
        performBufferAnalysis();
    }
}

// # 7. THOÁT CHẾ ĐỘ GIS (RESET UI)
// Chức năng: Xóa hết các vòng tròn đỏ, bỏ tick bộ lọc, trả bản đồ về trạng thái bình thường.
function exitGisMode() {
    bufferLayerGroup.clearLayers();
    isBufferMode = false;
    document.getElementById('map').style.cursor = '';
    selectedCategories = [];
    document.querySelectorAll('#categoryList input:checked').forEach(cb => cb.checked = false);
    document.querySelector('#categoryDropdownBtn span').innerText = "📍 Chọn loại sự cố đang xử lý...";
    var btnBuffer = document.getElementById('btnBufferMode');
    btnBuffer.innerHTML = '<i class="fa-solid fa-crosshairs me-1"></i> Hoặc Click chọn tâm';
    btnBuffer.className = 'btn btn-primary w-100 btn-sm fw-bold mb-2';
    document.getElementById('bufferResult').innerHTML = "";
    document.getElementById('btnExportBuffer').style.display = 'none';
    renderMap(allData);
    document.getElementById('gisToolsBody').style.display = 'none';
    document.getElementById('iconToggle').className = 'fa-solid fa-plus';
}

// # 8. CÔNG CỤ VẼ VÒNG TRÒN VÙNG ĐỆM (BUFFER ANALYSIS)
// Chức năng: Dựa vào bán kính nhập vào, vẽ vòng tròn đỏ bao quanh các điểm sự cố đã được chọn ở Bộ lọc.
function performBufferAnalysis() {
    var rM = parseFloat(document.getElementById('bufferRadius').value);
    bufferLayerGroup.clearLayers(); 
    var analysisCenters = [];

    allData.forEach(item => {
        if (item.status_code === 'dang_xu_ly' && selectedCategories.includes(item.title) && item.coords.length > 0) {
            var latLng = L.latLng(item.coords[0].lat, item.coords[0].lng);
            analysisCenters.push(latLng);
            L.circle(latLng, { color: 'red', fillColor: '#f03', fillOpacity: 0.1, radius: rM }).addTo(bufferLayerGroup);
        }
    });

    if (analysisCenters.length > 0) {
        var group = new L.featureGroup(analysisCenters.map(c => L.marker(c)));
        map.fitBounds(group.getBounds().pad(0.2));
    }
    analyzeData(analysisCenters);
}

// # 9. LỌC KHÔNG GIAN BẰNG TURF.JS (SPATIAL QUERY)
// Chức năng: Tính toán xem có những điểm sự cố nào khác NẰM BÊN TRONG vùng đệm (vòng tròn) vừa vẽ hay không.
function analyzeData(centers) {
    // LẤY GIÁ TRỊ BÁN KÍNH TỪ Ô INPUT (VD: 500)
    var rM = parseFloat(document.getElementById('bufferRadius').value);
    var radiusKm = rM / 1000;
    foundPointsData = []; var filteredMapData = []; 

    allData.forEach(function(item) {
        var keepItem = false;
        var validCoords = [];

        if (item.status_code === 'dang_xu_ly') {
            if (selectedCategories.length > 0) {
                if (selectedCategories.includes(item.title)) {
                    keepItem = true; validCoords = item.coords;
                }
            } else if (isBufferMode) { }
        } 
        else {
            if (selectedCategories.length > 0 || isBufferMode) { keepItem = false; } 
            else { keepItem = true; validCoords = item.coords; }
        }

        if (!keepItem && isBufferMode && item.status_code === 'dang_xu_ly') {
            if (Array.isArray(item.coords)) {
                item.coords.forEach(function(c) {
                    var pt = turf.point([c.lng, c.lat]);
                    // Thuật toán quét điểm xem có nằm trong bán kính không
                    var isInside = centers.some(center => {
                        var centerPt = turf.point([center.lng, center.lat]);
                        return turf.distance(centerPt, pt, {units: 'kilometers'}) <= radiusKm;
                    });
                    if (isInside) { validCoords.push(c); keepItem = true; }
                });
            }
        }
        
        if (keepItem) {
            filteredMapData.push({ ...item, coords: validCoords });
            if(validCoords.length > 0) {
                validCoords.forEach(c => {
                     // ĐÃ SỬA LỖI TẠI ĐÂY: ddress -> address
                    foundPointsData.push({ 
                        title: item.title, 
                         address: item.address, // <-- Đã sửa
                        desc: item.desc,
                        status: item.status_text, 
                        lat: c.lat, 
                        lng: c.lng, 
                        dist: rM 
                    });
                });
            }
        }
    });

    // Cập nhật lại bản đồ chỉ hiện các điểm trong vùng quét
    renderMap(filteredMapData); 

    document.getElementById('bufferResult').innerHTML = `Tìm thấy <b>${foundPointsData.length}</b> điểm liên quan`;
    document.getElementById('btnExportBuffer').style.display = (foundPointsData.length > 0) ? 'block' : 'none';
}

// # 10. XUẤT BÁO CÁO KẾT QUẢ GIS RA FILE CSV
// Chức năng: Nén danh sách các điểm tìm được trong vùng đệm thành file Excel/CSV tải về máy.
function exportBufferReport() {
    if (foundPointsData.length === 0) { alert("Không có dữ liệu!"); return; }
    var csv = "\uFEFFTên sự cố,Địa chỉ,Mô tả,Trạng thái,Khoảng cách (m),Vĩ độ,Kinh độ\n";
    foundPointsData.forEach(r => { 
        let cleanDesc = r.desc ? r.desc.replace(/"/g, '""') : "";
        csv += `"${r.title}","${r.address}","${cleanDesc}","${r.status}","${r.dist}",${r.lat},${r.lng}\n`; 
    });
    var link = document.createElement("a");
    link.href = encodeURI("data:text/csv;charset=utf-8," + csv); link.download = "baocao_phan_tich.csv";
    document.body.appendChild(link); link.click(); document.body.removeChild(link);
}

// # 11. ẨN/HIỆN BẢNG CÔNG CỤ GIS 
function toggleGisPanel() { 
    var b = document.getElementById('gisToolsBody'); 
    var i = document.getElementById('iconToggle'); 
    if (b.style.display === 'none') { b.style.display = 'block'; i.className = 'fa-solid fa-minus'; } 
    else { b.style.display = 'none'; i.className = 'fa-solid fa-plus'; } 
}

// # 12. CÁC HÀM XỬ LÝ FORM GỬI BÁO CÁO SỰ CỐ TỪ NGƯỜI DÂN
// Hiển thị danh sách tọa độ người dùng đã click
function renderPointsList() {
    var list = document.getElementById('points-list'); if (!list) return;
    var empty = document.getElementById('empty-msg'); var input = document.getElementById('points-data');
    var items = list.querySelectorAll('li:not(#empty-msg)'); items.forEach(e => e.remove());
    if (markers.length === 0) { empty.style.display = 'block'; input.value = ""; } 
    else { 
        empty.style.display = 'none'; 
        markers.forEach((item, i) => { 
            var li = document.createElement('li'); 
            li.innerHTML = `<span><strong>#${i + 1}</strong> (${item.lat.toFixed(4)}, ${item.lng.toFixed(4)})</span>`; 
            var btn = document.createElement('button'); 
            btn.className = 'btn btn-outline-danger btn-sm border-0'; 
            btn.innerHTML = '<i class="fa-solid fa-trash"></i>'; 
            btn.onclick = () => removePoint(i); 
            li.appendChild(btn); list.appendChild(li); 
        }); 
        input.value = JSON.stringify(markers.map(m => ({lat: m.lat, lng: m.lng}))); 
    }
}

// Thêm điểm báo cáo lên bản đồ
function addMarker(lat, lng) { 
    var newM = L.circleMarker([lat, lng], { color: 'white', fillColor: '#0d6efd', fillOpacity: 1, radius: 8, weight: 2 }); 
    lopChoDuyet.addLayer(newM); markers.push({ marker: newM, lat: lat, lng: lng }); renderPointsList(); 
}

// Xóa điểm báo cáo
function removePoint(i) { lopChoDuyet.removeLayer(markers[i].marker); markers.splice(i, 1); renderPointsList(); }

// Zoom tới vị trí hiện tại của user
function locateUser() { map.locate({setView: true, maxZoom: 15}); }
map.on('locationfound', e => { L.popup().setLatLng(e.latlng).setContent("📍 Vị trí của bạn").openOn(map); });

// Xử lý ô chọn "Khác" trong menu tiêu đề
var selectElement = document.getElementById('tieu_de');
if (selectElement) { 
    selectElement.addEventListener('change', function() { 
        var inputKhac = document.getElementById('input_khac'); 
        if (this.value === 'Khác') { inputKhac.style.display = 'block'; inputKhac.focus(); } 
        else { inputKhac.style.display = 'none'; inputKhac.value = ''; } 
    }); 
}

// # 13. API GỬI DỮ LIỆU LÊN SERVER (DJANGO)
// Chức năng: Lấy thông tin từ Form (Tiêu đề, ảnh, tọa độ...) và gọi Fetch API gửi lên file views.py
function guiBaoCao() { 
    var selectVal = document.getElementById('tieu_de').value; 
    var tieude = selectVal; 
    if (selectVal === 'Khác') tieude = document.getElementById('input_khac').value; 
    if (!tieude) { alert("⚠️ Chưa nhập tiêu đề!"); return; } 
    var points = document.getElementById('points-data').value; 
    if (!points || points === "[]") { alert("⚠️ Chưa chọn điểm!"); return; } 
    
    var btn = document.querySelector('button[onclick="guiBaoCao()"]'); 
    var oldText = btn.innerHTML; 
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang gửi...'; 
    btn.disabled = true; 
    
    var fd = new FormData(); 
    fd.append('tieu_de', tieude); 
    fd.append('dia_chi', document.getElementById('dia_chi').value); 
    fd.append('mo_ta', document.getElementById('mo_ta').value); 
    fd.append('points_data', points); 
    if(document.getElementById('hinh_anh').files[0]) fd.append('hinh_anh', document.getElementById('hinh_anh').files[0]); 
    var csrf = document.querySelector('[name=csrfmiddlewaretoken]'); 
    if(csrf) fd.append('csrfmiddlewaretoken', csrf.value); 
    
    fetch('/luu-phan-anh/', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(d => { 
        if(d.success) { alert("✅ Gửi thành công!"); location.reload(); } 
        else alert("❌ Lỗi: " + d.message); 
    })
    .catch(() => alert("❌ Lỗi mạng!"))
    .finally(() => { btn.innerHTML = oldText; btn.disabled = false; }); 
}