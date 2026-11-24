# [G03] Truy vấn dữ liệu OpenStreetMap (OSM): Tái tạo khối nhà (Buildings), đường giao thông và hẻm phố

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

### 1. Tóm tắt Bản chất (2-3 câu)
Nhập dữ liệu vector OpenStreetMap (OSM) vào BlenderGIS là quá trình chuyển đổi dữ liệu không gian dạng 2D/3D trực tuyến hoặc từ tệp XML thành các mô hình lưới 3D có tọa độ địa lý chuẩn xác trong Blender [1, 2]. Quy trình này cho phép **tự động dựng khối công trình kiến trúc** theo chiều cao thực tế và **phân loại hệ thống hạ tầng** (đường xá, sông rạch) thành các lớp đối tượng riêng biệt [3, 4]. Đây là nền tảng cốt lõi phục vụ công tác quy hoạch đô thị, tái thiết lập môi trường địa lý và diễn họa kiến trúc 3D trực quan [2, 5].

---

### 2. Nguyên lý & Thông số Chuẩn
* **Cơ chế truy vấn thuộc tính chiều cao công trình:** Khi xử lý các thẻ (`tags`) của tòa nhà (`building`), bộ nhập dữ liệu sẽ truy vấn hai thuộc tính chính là `height` (chiều cao tuyệt đối tính bằng mét) và `building:levels` (số tầng để tính chiều cao tỷ lệ) [4].
* **Extrusion & Randomization (Chiều cao mặc định & Biến thiên ngẫu nhiên):** Đối với các công trình thiếu dữ liệu chiều cao trong cơ sở dữ liệu OSM, hệ thống áp dụng một giá trị chiều cao mặc định (*default height*) [4, 6]. Người dùng có thể thiết lập khoảng lệch ngẫu nhiên (ví dụ: \\(12.0\,\text{m} \pm 3.5\,\text{m}\\)) để tạo độ nhấp nhô tự nhiên cho mái nhà, tránh sự đơn điệu đồng dạng [4].
* **Khớp cao độ địa hình (Terrain Conformance):** Khi bật tùy chọn **Elevation from object** và chọn bề mặt địa hình (DEM/SRTM), các chân công trình dạng 2D sẽ được chiếu thẳng đứng lên bề mặt địa hình và đẩy khối tương đối theo điểm tiếp xúc mặt đất [4, 6].
* **Nguyên lý phân tách lớp đường xá và sông kênh (Tag Filtering):**
  * **Đường chính (Main Roads):** Lọc loại đường `way` với các thẻ `highway=primary`, `highway=secondary`, `highway=tertiary` [3].
  * **Hẻm nhỏ / Đường nội bộ (Alleys/Minor Roads):** Lọc thẻ `highway=residential`, `highway=service`, `highway=unclassified` [3].
  * **Sông, kênh rạch (Waterways):** Lọc theo thẻ `waterway=river`, `waterway=canal`, `waterway=stream` hoặc `natural=water` [3].
* **Cấu trúc lưới ngầm định:** BlenderGIS mặc định gộp các yếu tố có cùng sự kết hợp giữa loại hình học (`way`, `area`) và thẻ lọc thành một lưới (*mesh*) duy nhất, đồng thời khởi tạo các *Vertex Group* để lưu giữ tên và thuộc tính mối quan hệ [3, 7].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Thao tác trên giao diện (GUI Workflow):
1. **Thiết lập không gian địa lý:** Tạo bề mặt địa hình georeference (bằng tính năng *Basemaps* hoặc *Get SRTM*) [1, 6].
2. **Kích hoạt Get OSM:** Chuyển góc nhìn Viewport sang Top Orthographic (`Numpad 7`), mở thẻ **GIS** ở thanh công cụ bên phải và nhấn nút **Get OSM** (hoặc chọn menu *Import > OpenStreetMap (.osm)* nếu dùng tệp XML offline) [1, 6].
3. **Cấu hình bảng điều khiển Extrude & Layers:**
   * Trong danh sách danh mục, giữ phím `Shift` để chọn **Ways** và **Buildings** [6].
   * Nhập **Default height** (ví dụ: `12.0`) và chọn khoảng lệch ngẫu nhiên [4, 6].
   * Tích chọn **Elevation from object** và chọn lưới địa hình mặt đất đã tạo [4, 6].
   * Giữ thiết lập phân tách Mesh theo kết hợp loại đối tượng và thẻ lọc để tự động tách các lớp lưới riêng [3].

#### Đoạn mã Python (`bpy`) tự động hóa:
Bạn có thể chạy đoạn mã Python sau trong thẻ **Scripting** của Blender để tự động hóa quá trình nhập và tổ chức các lớp dữ liệu:

```python
import bpy

# 1. Khai báo tên đối tượng địa hình mặt đất đã georeference
terrain_mesh_name = "Terrain_SRTM"

# 2. Gọi operator nhập dữ liệu OSM và đẩy khối tự động
# Lưu ý: Nếu dùng file .osm offline, sử dụng bpy.ops.import_scene.osm
bpy.ops.import_scene.osm(
    filepath="C:/geodata/city_map.osm",
    import_buildings=True,
    default_height=12.0,          # Chiều cao mặc định (mét)
    random_height_range=3.5,      # Độ lệch ngẫu nhiên (+/- mét)
    elevation_from_object=True,   # Ép bám chân công trình theo địa hình
    target_object=terrain_mesh_name
)

# 3. Tự động đổi tên và phân loại Collection cho các lớp dữ liệu
osm_collection = bpy.data.collections.get("OSM_Data") or bpy.context.scene.collection

for obj in osm_collection.objects:
    if obj.type == 'MESH':
        name_lower = obj.name.lower()
        if "building" in name_lower:
            obj.name = "OSM_Buildings_3D"
        elif any(tag in name_lower for tag in ["primary", "secondary", "tertiary"]):
            obj.name = "OSM_Main_Roads"
        elif any(tag in name_lower for tag in ["residential", "service", "unclassified"]):
            obj.name = "OSM_Minor_Alleys"
        elif any(tag in name_lower for tag in ["waterway", "river", "canal"]):
            obj.name = "OSM_Rivers_Canals"
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Lỗi ngắt kết nối Overpass API (`Get OSM` bị thất bại):** Lỗi xảy ra khi máy chủ Overpass bên thứ ba quá tải, bảo trì hoặc kết nối mạng không ổn định [1].
  * *Cách xử lý:* Xuất tệp `.osm` (XML) trực tiếp từ trang web `www.openstreetmap.org` về máy, sau đó dùng tính năng nhập tệp XML offline trong BlenderGIS [1].
* **Lỗi nhấp nháy / biến dạng mặt lưới (Z-fighting & Clipping Distortions):** Do bản đồ địa lý có quy mô quá lớn, vượt quá dải tĩnh độ sâu mặc định của Viewport Camera [8, 9].
  * *Cách xử lý:* Mở bảng thuộc tính Viewport (`N`), điều giảm khoảng cách **Clip Start** xuống nhỏ hơn và điều chỉnh **Clip End** phù hợp với quy mô thực tế của cảnh [8, 9].
* **Lỗi các công trình có sân trong bị lấp kín (Polygon Holes Issue):** Các polygon tòa nhà chứa lỗ thủng ở giữa (như chung cư dạng giếng trời) không được hệ thống đa giác Blender hỗ trợ mặc định, dẫn đến mặt phẳng bị điền kín [10, 11].
  * *Cách xử lý:* Làm sạch và sửa chữa lại hình học vector trên phần mềm QGIS trước khi xuất/nhập, hoặc xử lý loại bỏ các đỉnh trùng lặp (*Merge duplicate vertices*) [8, 10].
* **Sụt giảm hiệu năng nặng do tách thành hàng nghìn đối tượng độc lập:** Khi chọn tùy chọn tách từng yếu tố OSM thành một Object riêng lẻ, Blender sẽ bị quá tải vì cấu trúc không thiết kế cho hàng nghìn đối tượng rời rạc [3, 7, 12].
  * *Cách xử lý:* Giữ nguyên phương pháp nhập chuẩn (gộp chung các yếu tố thành một Mesh duy nhất cho từng nhóm thẻ) để tối ưu hóa bộ nhớ [7, 13].

---

Bạn có muốn tôi hướng dẫn chi tiết thêm về cách trải vật liệu (*Materials*) tự động cho từng lớp tòa nhà/đường xá vừa nhập, hay cách kết hợp Geometry Nodes để phân tán cây xanh dọc theo các tuyến đường không?
