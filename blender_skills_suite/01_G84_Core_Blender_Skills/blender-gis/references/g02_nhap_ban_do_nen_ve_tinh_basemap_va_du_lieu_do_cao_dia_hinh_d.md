# [G02] Nhập bản đồ nền vệ tinh (Basemap) và dữ liệu độ cao địa hình (DEM / SRTM Elevation)

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

### 1. Tóm tắt Bản chất
Quy trình sử dụng **BlenderGIS** cho phép kết nối trực tiếp môi trường 3D của Blender với các dịch vụ dữ liệu địa lý toàn cầu như Google Satellite, ESRI World Imagery và mô hình cao độ số SRTM từ OpenTopography [1-3]. Phương pháp này tự động chuyển đổi ảnh vệ tinh thực tế và dữ liệu độ cao không gian thành lưới 3D được định vị địa lý (georeferenced) chính xác [4-6]. Nhờ đó, người dùng có thể tái tạo cảnh quan tự nhiên và đô thị thực tế phục vụ quy hoạch, mô phỏng môi trường và diễn họa kiến trúc theo đúng tỷ lệ thực địa [5, 7, 8].

---

### 2. Nguyên lý & Thông số Chuẩn
- **Xung đột độ chính xác số thực (Single float32 vs Double float64):**
  - Dữ liệu địa lý thực tế (GIS) dùng số thực 64-bit (`double precision`) để mã hóa tọa độ chiếu (như hệ UTM) có giá trị cực lớn lên tới hàng triệu mét [9-11]. Trong khi đó, Blender hoạt động trên kiến trúc số thực 32-bit (`single precision float32`), chỉ đạt khoảng **7 chữ số có nghĩa** [9, 12-14].
  - Giới hạn độ phân giải không gian của Blender được tính theo công thức \\(\epsilon \approx X \cdot 2^{-23}\\) [12, 13]. Ví dụ: ở tọa độ UTM \\(4.500.000\text{ m}\\), sai số làm tròn \\(\epsilon \approx 0,536\text{ m}\\) [15, 16]; ở mốc \\(5.000.000\text{ m}\\), sai số lên tới \\(\approx 0,596\text{ m}\\) gây ra hiện tượng méo lưới, nhấp nháy đỉnh (vertex jittering), rách hình camera (catastrophic z-fighting) và hỏng bản đồ bóng đổ [14-16].
  - Việc nhập trực tiếp tọa độ độ (decimal degrees / lat-long) cũng gây mất chính xác vì \\(1^\circ\\) vĩ độ \\(\approx 111.320\text{ m}\\) (\\(\approx 111\text{ km}\\)), khiến số thực float32 không thể phân giải chi tiết dưới \\(1,11\text{ m}\\) [17-20].
- **Mô hình kép Geoscene & Vector dịch gốc tọa độ (Scene Origin Re-centering):**
  - BlenderGIS xử lý xung đột này bằng kiến trúc **Geoscene** [6, 21]. Khi khởi tạo, hệ thống tạo ra một **translation vector** \\(\mathbf{T}_{\text{offset}} = (X_{\text{geo\_origin}}, Y_{\text{geo\_origin}}, Z_{\text{geo\_origin}})\\) lưu trong custom properties của scene [6, 21-23].
  - Mọi tọa độ địa lý được tính chuyển về gốc Blender theo phép trừ: \\(\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\) để đưa lưới 3D về sát gốc Cartesian \\((0,0,0)\\), đảm bảo độ chính xác dưới milimét mà vẫn bảo toàn tọa độ thực trong metadata [6, 9, 21-23].
- **Yêu cầu API Key:** Để truy xuất cao độ SRTM toàn cầu từ dịch vụ OpenTopography, người dùng bắt buộc phải đăng ký API Key miễn phí tại `opentopography.org` [1, 3, 5].
- **Quy tắc tính lực biến dạng (Displacement Strength Calculation):**
  - Cao độ địa hình được áp dụng qua texture biến dạng theo công thức: \\(\text{Displacement} = (\text{Texture value} - \text{Midlevel}) \times \text{Strength}\\) [24, 25].
  - Giá trị `Midlevel` luôn thiết lập bằng \\(0\\) [24, 25]. Với ảnh raster float32, `Strength` mặc định bằng \\(1\\) [26, 27]. Với ảnh raster chuẩn hóa non-float, lực biến dạng tính theo độ sâu bit: \\(\text{Strength} = \Delta Z / (\Delta Z / (2^{\text{depth}} - 1))\\) [26, 27].
- **Giới hạn chia nhỏ lưới (Subdivision Limits):**
  - Giao diện Blender giới hạn mềm (soft limit) cấp độ Subsurf modifier mặc định là \\(6\\), có thể nâng lên \\(8\\)–\\(10\\) để giải phóng các chi tiết cao độ nhỏ hơn từ bản đồ SRTM [28, 29].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác trên giao diện Blender (GUI)
1. **Khởi tạo file:** Xóa toàn bộ vật thể mặc định và lưu file `.blend` để xác lập đường dẫn thư mục làm việc [3, 30].
2. **Tải ảnh vệ tinh Basemap:**
   - Trên menu 3D Viewport, chọn **GIS > Web geodata > Basemap** (hoặc nhấn phím tắt `*`) [2, 3, 30].
   - Chọn nguồn ảnh: **Google** / **Satellite** hoặc **ESRI World Imagery** [2, 3].
   - Điều hướng khung nhìn: Cuộn chuột để Zoom, giữ `Shift + chuột giữa` để Pan [2, 30].
   - Nhấn **`B`** để quét khung chọn khu vực khảo sát [2, 30].
   - Nhấn **`L`** để khóa khung nhìn (Lock viewport bounds), ép hệ thống tải tile chất lượng cao tối đa cho khu vực đã khóa [3].
   - Nhấn **`E`** để xuất vùng chọn thành vật thể mặt phẳng (plane mesh) có gắn ảnh vệ tinh đã định vị địa lý [2, 3, 30].
3. **Đắp dữ liệu cao độ SRTM (DEM):**
   - Chọn mặt phẳng bản đồ vừa tạo [3, 31].
   - Vào menu **GIS > Web geodata > Get elevation (SRTM)** [1, 31, 32].
   - Nhập **OpenTopography API Key** đã đăng ký [1, 3].
   - BlenderGIS sẽ tự động tải dữ liệu độ cao SRTM, thêm modifier **Subdivision** (chia lưới) và modifier **Displace** để nắn phẳng plane thành mô hình địa hình 3D [1, 3, 32].
   - Vào bảng Modifier, nâng cấp độ Subsurf trong Viewport/Render từ \\(6\\) lên \\(8\\)–\\(10\\) để hiển thị rõ các dãy núi và thung lũng [28, 29].
4. *(Tùy chọn) Đắp file DEM GeoTIFF có sẵn:*
   - Chọn mặt phẳng ảnh, vào **GIS > Import > Georaster**, chọn file `.tif`/`.geotiff`, chọn chế độ **DEM as displacement texture**, tích chọn `Apply on existing mesh`, `Clip to working extent` và `Fill nodata values` [33-36].

#### B. Tự động hóa và tinh chỉnh bằng Script Python (`bpy`)
Đoạn mã Python `bpy` dưới đây hỗ trợ tự động hóa việc gọi chức năng lấy cao độ và tinh chỉnh tối ưu các tham số Modifier địa hình trong Blender:

```python
import bpy

# 1. Khởi tạo lệnh tải Basemap vệ tinh của BlenderGIS
# (Thao tác chọn vùng tương tác ban đầu được thực hiện trên Viewport)
bpy.ops.gis.fetch_wmts(source='GOOGLE', layer='SATELLITE')

# 2. Lấy vật thể mặt phẳng địa hình đang chọn (Active Object)
terrain_obj = bpy.context.active_object

if terrain_obj:
    # 3. Kích hoạt lấy cao độ SRTM tự động từ OpenTopography API
    bpy.ops.gis.fetch_srtm(api_key="YOUR_OPENTOPOGRAPHY_API_KEY")

    # 4. Tinh chỉnh cấu hình Modifier để tối ưu độ chi tiết địa hình
    subsurf_mod = terrain_obj.modifiers.get("Subsurf")
    if subsurf_mod:
        subsurf_mod.levels = 8        # Nâng mức chia nhỏ lưới trong Viewport
        subsurf_mod.render_levels = 10 # Nâng mức chia nhỏ lưới khi Render

    displace_mod = terrain_obj.modifiers.get("Displace")
    if displace_mod:
        displace_mod.mid_level = 0.0  # Mặc định chuẩn Midlevel = 0
```

---

### 4. Lỗi thường gặp & Cách kiểm tra
1. **Mô hình bị rung giật, nhấp nháy mặt (Z-fighting) hoặc vỡ bóng đổ:**
   - *Nguyên nhân:* Nhập dữ liệu tọa độ UTM lớn mà không thông qua cơ chế re-centering của Geoscene, làm số thực 32-bit bị tràn giới hạn 7 chữ số có nghĩa [12, 13, 15, 16].
   - *Khắc phục:* Luôn để BlenderGIS khởi tạo Geoscene origin offset tự động, chuyển tâm mô hình về gần gốc Cartesian \\((0,0,0)\\) [6, 22, 23].
2. **Địa hình bị gai nhọn bất thường hoặc thủng lưới (Nodata Artifacts):**
   - *Nguyên nhân:* File cao độ DEM chứa các pixel lỗi/khuyết dữ liệu (nodata values) nhận giá trị cực âm hoặc cực dương (như \\(-9999\\)) [33, 36].
   - *Khắc phục:* Khi import DEM GeoTIFF thủ công, luôn bật tùy chọn **Fill nodata values** để script tự động nội suy làm mịn các vùng trống [33, 36, 37].
3. **Lỗi không tải được cao độ SRTM (Server Fail / Missing API Key):**
   - *Nguyên nhân:* Chưa nhập hoặc nhập sai OpenTopography API Key [1, 5].
   - *Khắc phục:* Đăng ký tài khoản miễn phí tại `opentopography.org`, dán API Key vào hộp thoại khi bấm `Get SRTM` hoặc lưu cố định trong **Addon Preferences** của BlenderGIS [1, 3, 5].
4. **Mô hình bị biến mất hoặc xé đen khi xoay camera (Viewport Clipping):**
   - *Nguyên nhân:* Mô hình địa hình thực tế phủ diện tích rộng hàng kilomet, vượt quá khoảng cách quan sát mặc định của camera (Clip Start/Clip End) [38-40].
   - *Khắc phục:* Mở N-Panel (`View`), điều chỉnh **Clip Start** lên \\(0,1\text{ m}\\) – \\(1,0\text{ m}\\) và nâng **Clip End** lên \\(10.000\text{ m}\\) – \\(50.000\text{ m}\\) [38-40].

---

🗺️ Bạn có muốn tôi hướng dẫn tiếp quy trình nhập tòa nhà 3D và mạng lưới đường giao thông từ OpenStreetMap (Get OSM) để đặt chính xác lên bề mặt địa hình 3D vừa tạo không?
