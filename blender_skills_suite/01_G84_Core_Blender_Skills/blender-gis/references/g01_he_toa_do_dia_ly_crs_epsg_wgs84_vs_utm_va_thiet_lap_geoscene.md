# [G01] Hệ tọa độ địa lý (CRS / EPSG, WGS84 vs UTM) và thiết lập GeoScene gốc tọa độ trong BlenderGIS

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
Hệ quy chiếu tọa độ (CRS) quy định cách chiếu tọa độ cong của Trái Đất lên mặt phẳng mét, trong khi việc đưa địa hình về gốc tọa độ (0,0,0) là yêu cầu bắt buộc để giải quyết xung đột độ chính xác số thực trong phần mềm 3D [1, 2]. Do các hệ cơ sở dữ liệu GIS sử dụng số thực độ chính xác kép 64-bit (double precision float64), còn Blender xử lý hình học bằng số thực độ chính xác đơn 32-bit (single precision float32), các tọa độ địa lý lớn sẽ bị vượt giới hạn biểu diễn của GPU [2, 3]. Việc dịch chuyển tâm địa hình về gốc tọa độ (0,0,0) giúp duy trì độ chính xác ở mức dưới milimét và triệt tiêu hoàn toàn hiện tượng rung/vỡ lưới hình học (Floating-point precision jitter) [4, 5].

---

### 2. **Nguyên lý & Thông số Chuẩn**

#### **Các Hệ quy chiếu Tọa độ (CRS) Phổ biến**
*   **WGS84 (EPSG:4326):** Hệ tọa độ địa lý toàn cầu dựa trên góc (Kinh độ/Vĩ độ tính bằng độ thập phân - Decimal Degrees) [6, 7]. Do \\(1^\circ\\) vĩ độ tương đương khoảng \\(111.320\text{ m}\\) (\\(1\text{ m} \approx 0,00001^\circ\\)), việc nhập trực tiếp dữ liệu độ thập phân vào Blender làm cho các điểm nằm gần nhau bị tròn/gộp lại thành một do giới hạn khoảng 7 chữ số có nghĩa của số thực 32-bit [6-9].
*   **Web Mercator (EPSG:3857):** Hệ tọa độ chiếu phẳng dạng mét được sử dụng phổ biến bởi các bản đồ nền web (Google Maps, Bing, OpenStreetMap) [10, 11].
*   **UTM (Universal Transverse Mercator) & UTM cho Việt Nam:** Hệ tọa độ chiếu vuông góc tính bằng đơn vị mét [9, 12, 13]. Đối với lãnh thổ Việt Nam, hai múi chiếu UTM tiêu chuẩn chính là **UTM Zone 48N (EPSG:32648)** (phù hợp cho khu vực Miền Bắc và Miền Trung) và **UTM Zone 49N (EPSG:32649)** (phù hợp cho khu vực Miền Đông Nam Bộ và hải đảo phía Đông).

#### **Nguyên lý Xung đột Độ chính xác (Single vs. Double Precision)**
*   Dữ liệu không gian GIS lưu trữ vị trí bằng số thực **64-bit (float64)** để thể hiện các khoảng cách hàng triệu mét [2, 3]. Tuy nhiên, Blender và các công cụ dựng hình 3D lại sử dụng số thực **32-bit (float32)** với 24-bit mantissa nhằm tối ưu hóa tính toán đồ họa trên GPU [2, 3, 9].
*   Giới hạn độ phân giải không gian \\(\epsilon\\) (khoảng cách nhỏ nhất có thể phân biệt) của số thực 32-bit được tính theo công thức:
    \\[\epsilon \approx X \cdot 2^{-23}\\]
    *(trong đó \\(X\\) là giá trị tọa độ chiếu tuyệt đối)* [4, 9].

#### **Bảng So sánh Độ chính xác theo Thang đo Tọa độ:**
| Ngữ cảnh Hệ Tọa độ | Giá trị Tọa độ Chiếu (\\(X\\)) | Giới hạn Độ phân giải (\\(\epsilon\\)) | Hiện tượng trong Viewport Blender |
| :--- | :--- | :--- | :--- |
| **Gốc tọa độ Cục bộ (Local Origin)** | \\(10\text{ m}\\) | \\(\approx 1,19 \times 10^{-6}\text{ m}\\) | Mô hình tuyệt đối ổn định; độ chính xác dưới milimét [4]. |
| **Khu vực Đô thị Trung bình** | \\(10.000\text{ m}\\) | \\(\approx 1,19 \times 10^{-3}\text{ m}\\) | Mức độ hiển thị cao; biến dạng đỉnh không đáng kể [4]. |
| **Lưới Tọa độ Vùng (Tọa độ Đông UTM)** | \\(500.000\text{ m}\\) | \\(\approx 5,96 \times 10^{-2}\text{ m}\\) (~6 cm) | Bắt đầu bị dính tọa độ nhẹ; xuất hiện hiện tượng rung texture [4]. |
| **Tọa độ UTM Tuyệt đối / Toàn cầu** | \\(4.500.000 \div 5.000.000\text{ m}\\) | \\(\approx 0,536 \div 0,596\text{ m}\\) (~0,5–0,6 m) | Vỡ lưới nghiêm trọng; tranh chấp chiều sâu Z (z-fighting); đứt gãy bóng đổ [4, 5, 9]. |

#### **Mô hình Geoscene & Phép Dịch tâm (Origin Re-Centering)**
*   Để giữ được độ chính xác tuyệt đối, BlenderGIS sử dụng cơ chế **Geoscene** bằng cách thiết lập một vectơ dịch chuyển offset [1, 14]:
    \\[\mathbf{T}_{\text{offset}} = (X_{\text{geo\_origin}}, Y_{\text{geo\_origin}}, Z_{\text{geo\_origin}})\\]
*   Tọa độ các đỉnh khi nạp vào Blender sẽ được tính lại theo phép trừ [5]:
    \\[\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\]
    Thao tác này đưa tâm hình học về sát gốc Cartesian (0,0,0) trong không gian 32-bit của Blender, trong khi giá trị tọa độ thực 64-bit vẫn được lưu trữ tại Custom Properties của Scene [5, 14, 15].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### **Thao tác Thủ công qua UI (BlenderGIS):**
1.  Nhấn `N` trong Viewport 3D để mở Sidebar, chuyển sang tab **GIS** và mở panel **Geoscene Manager** [16, 17].
2.  Cấu hình **Scene CRS** chính xác trước khi nạp dữ liệu (ví dụ chọn `EPSG:32648` cho UTM Zone 48N) [6, 18, 19].
3.  Khi nạp Shapefile, DEM Raster hoặc sử dụng Basemap (`*` -> nhấn `E` để export), BlenderGIS sẽ tự động thực hiện phép dịch tâm \\(\mathbf{T}_{\text{offset}}\\) đưa hình học về (0,0,0) và ghi nhận vị trí địa lý thực vào thuộc tính Custom Properties của Scene [5, 11, 14-16].
4.  Cấu hình khoảng khoảng nhìn `Clip Start` và `Clip End` của Camera/Viewport tương ứng với quy mô vùng dựng hình để tránh lỗi Z-buffer [20-22].

#### **Hướng dẫn Lập trình Python `bpy`:**
Đoạn mã dưới đây minh họa cách tự động lưu trữ thuộc tính **Geoscene** và dịch chuyển vị trí các đỉnh của một Mesh về gần gốc tọa độ (0,0,0):

```python
import bpy

# 1. Khai báo thuộc tính Geoscene cho Scene (Lưu vị trí thực GIS 64-bit)
scene = bpy.context.scene

# Thiết lập thông tin CRS và T_offset tuyệt đối
scene["crs"] = "EPSG:32648"  # UTM Zone 48N Việt Nam
origin_x = 585000.0  # Tọa độ Đông Projected Easting (m)
origin_y = 2320000.0 # Tọa độ Bắc Projected Northing (m)
origin_z = 0.0       # Cao độ gốc (m)

scene["geo_origin_x"] = origin_x
scene["geo_origin_y"] = origin_y
scene["geo_origin_z"] = origin_z

# 2. Thực hiện dịch chuyển các đỉnh lưới (P_local = P_geo - T_offset)
obj = bpy.context.active_object
if obj and obj.type == 'MESH':
    mesh = obj.data
    # Trừ giá trị Offset để đưa vị trí các đỉnh về tiệm cận gốc (0,0,0)
    for vertex in mesh.vertices:
        vertex.co.x -= origin_x
        vertex.co.y -= origin_y
        vertex.co.z -= origin_z
    mesh.update()

# 3. Tối ưu khoảng xem (Clip Distance) của 3D Viewport
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.clip_start = 0.1
                space.clip_end = 10000.0
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

*   **Lỗi 1: Nhập trực tiếp dữ liệu WGS84 (EPSG:4326) góc độ thập phân vào Blender**
    *   *Hiện tượng:* Dữ liệu bị biến dạng, các điểm nằm sát nhau bị gộp lại do sai số làm tròn, độ chính xác dưới \\(1\text{ m}\\) hoàn toàn mất đi [6-8, 23].
    *   *Cách kiểm tra:* Kiểm tra metadata của file vector/raster trong QGIS hoặc BlenderGIS. Đảm bảo dữ liệu đã được Chuyển chiếu (Reproject) sang hệ tọa độ vuông góc tính theo đơn vị mét (như UTM Zone 48N/49N) trước khi đưa vào Blender [6, 23, 24].
*   **Lỗi 2: Giữ nguyên tọa độ tuyệt đối UTM (hàng trăm ngàn mét) mà không dịch về (0,0,0)**
    *   *Hiện tượng:* Lưới địa hình bị rung giật (jitter) khi xoay/di chuyển camera, xuất hiện các vệt chớp nháy đè mặt (z-fighting) và hệ thống bóng đổ bị đứt gãy [4, 5, 25, 26].
    *   *Cách kiểm tra:* Chọn Object địa hình, nhấn `N` kiểm tra thông số **Transform > Location**. Nếu giá trị Location hiển thị ở mức \\(500.000\text{ m}\\) hay \\(2.000.000\text{ m}\\) thay vì gần \\(0\\), cần kích hoạt cơ chế dịch tâm (Origin Offset) lập tức [4, 5, 14, 27].
*   **Lỗi 3: Cấu hình khoảng xem Viewport / Camera Clip bất hợp lý**
    *   *Hiện tượng:* Đặt `Clip Start` quá nhỏ (ví dụ \\(0,001\text{ m}\\)) trong khi `Clip End` quá xa (ví dụ \\(100.000\text{ m}\\)) làm cạn kiệt độ phân giải Z-buffer, gây ra lỗi hiển thị mặt bị đen (black faces) [20-22, 25].
    *   *Cách kiểm tra:* Tăng giá trị `Clip Start` lên gần cận vùng quan sát (khoảng \\(0.1\text{ m} \div 1\text{ m}\\)) và điều chỉnh `Clip End` vừa đủ bao phủ toàn bộ vùng địa hình [20-22].

---

💡 **Gợi ý bước tiếp theo:** Bạn có muốn tôi hướng dẫn chi tiết quy trình dựng địa hình 3D từ tệp DEM/GeoTIFF thực tế kết hợp đổ bề mặt ảnh vệ tinh và hạ công trình OSM chuẩn tọa độ trong Blender không?
