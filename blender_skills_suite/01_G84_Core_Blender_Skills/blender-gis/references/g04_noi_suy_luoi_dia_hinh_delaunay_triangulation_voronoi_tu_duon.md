# [G04] Nội suy lưới địa hình (Delaunay Triangulation & Voronoi) từ đường đồng mức hoặc đám mây điểm

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

**Thuật toán Delaunay Triangulation trong BlenderGIS** là giải pháp tối ưu để chuyển đổi các dữ liệu độ cao rời rạc như đường đồng mức (Contours) hoặc điểm đo (Point Cloud / Shapefile) thành bề mặt địa hình 3D liên tục [1-4]. Dưới đây là giải thích chi tiết theo các yêu cầu thiết lập và chuẩn hóa [1, 3, 5]:

---

### 1. Tóm tắt Bản chất
**Delaunay Triangulation** trong BlenderGIS là thuật toán dựng lưới không gian 2.5D (Triangulated Irregular Network - TIN) trực tiếp từ tập hợp các đỉnh dữ liệu địa lý rời rạc [1-4]. Thuật toán thực hiện chiếu tọa độ các điểm lên mặt phẳng 2D và liên kết chúng theo **tiêu chuẩn đường tròn ngoại tiếp** (circumcircle criterion), đảm bảo không có điểm nào nằm bên trong đường tròn ngoại tiếp của bất kỳ tam giác nào [1-4]. Nhờ đó, bề mặt địa hình 3D tạo ra có độ phân bố lưới đều đặn, mịn màng và tránh được các hiện tượng biến dạng hay chồng lấp tam giác khi xử lý dữ liệu địa lý thưa thớt [1-4].

---

### 2. Nguyên lý & Thông số Chuẩn

* **Cấu trúc hình học 2.5D TIN:**
  * Thuật toán chiếu tọa độ 3D của các đường đồng mức hoặc điểm đo xuống mặt phẳng 2D, nối các đỉnh thành mạng lưới tam giác không chồng lấp, sau đó gán lại độ cao Z để trả về mô hình địa hình 3D hoàn chỉnh [1-4].

* **Giới hạn độ chính xác Float32 & Hệ tọa độ (CRS):**
  * Blender xử lý tọa độ dưới dạng số thực đơn **Float32** (chỉ có khoảng 7 chữ số có nghĩa) [6-8].
  * Trên Trái Đất, \\(1^\circ\\) kinh/vĩ độ tương đương khoảng **111 km**, nên **1 mét** xấp xỉ **\\(0.00001^\circ\\)** (\\(1 \times 10^{-5}\\) độ) [6-8].
  * **Quy tắc bắt buộc:** Tránh nhập dữ liệu Shapefile lưu trữ ở dạng **độ thập phân (Decimal Degrees / Longitude-Latitude)** vì các điểm gần nhau dưới 1 mét sẽ bị làm tròn và gộp lại (rounded and merged), làm mất độ chính xác [6-8]. Dữ liệu phải được chuyển đổi sang **Hệ tọa độ tham chiếu chiếu phẳng (Projected CRS)** tính bằng đơn vị mét (ví dụ: UTM) [6, 7, 9, 10].

* **Phép dịch chuyển gốc tọa độ local (Local Translation Offset):**
  * Tọa độ GIS thực tế thường nằm rất xa gốc tọa độ thế giới (world origin) [11-14].
  * BlenderGIS áp dụng công thức dịch chuyển local:
    \\[\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\]
    Trong đó \\(\mathbf{T}_{\text{offset}} = (X_{\text{geo\_origin}}, Y_{\text{geo\_origin}}, Z_{\text{geo\_origin}})\\) giúp đưa mô hình về gần gốc Cartesian \\((0,0,0)\\) [12, 13, 15]. Việc này bảo toàn độ chính xác mô hình hóa ở mức **dưới 1 mm (sub-millimeter precision)** và ngăn chặn hiện tượng giật rung đỉnh (vertex jitter) [12-15].

* **Định dạng dữ liệu Vector tương thích:**
  * **Hỗ trợ:** Shapefile thuộc các dạng `point`, `pointZ`, `polyline`, `polylineZ`, `polygon`, `polygonZ` [9, 10, 16, 17].
  * **Không hỗ trợ:** Các định dạng phức hợp `multipoint`, `multipointZ`, `pointM`, `polylineM`, `polygonM`, và `multipatch` [9, 10, 16, 17].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Quy trình thao tác trên giao diện (UI)
1. **Thiết lập Georeferencing cho Scene:** Mở bảng **Geoscene Manager** trong tab **GIS** (ở thanh công cụ 3D View Tool Shelf) để thiết lập hệ tọa độ chiếu phẳng (CRS) chuẩn trước khi nhập dữ liệu [6, 18, 19].
2. **Import Shapefile:** Vào menu **GIS > Import > Shapefile**, chọn file `.shp` chứa đường đồng mức hoặc điểm đo cao độ [9, 10, 16, 17]. Lựa chọn chế độ **Merged Mesh Mode** để gộp toàn bộ thực thể thành một mesh duy nhất, giúp tối ưu hóa bộ nhớ GPU và giảm thiểu số lượng draw call [20-22].
3. **Chọn đối tượng Mesh:** Chuyển sang **Edit Mode** hoặc giữ đối tượng lưới vector được chọn ở **Object Mode** [23-26].
4. **Chạy toán tử Delaunay:** Ở tab **GIS** trên thanh công cụ 3D View, chọn công cụ **Delaunay** (hoặc `Make terrain mesh with Delaunay triangulation`) để tạo bề mặt địa hình [25-28].

#### Đoạn mã Python (`bpy`) tự động hóa
Dưới đây là mã Python gọi trực tiếp toán tử Delaunay Triangulation trong BlenderGIS:

```python
import bpy

# 1. Tên đối tượng mesh chứa vector / điểm cao độ đã import
mesh_name = "Contour_Lines"
terrain_obj = bpy.data.objects.get(mesh_name)

if terrain_obj:
    # Bỏ chọn tất cả đối tượng và kích hoạt đối tượng địa hình
    bpy.ops.object.select_all(action='DESELECT')
    terrain_obj.select_set(True)
    bpy.context.view_layer.objects.active = terrain_obj
    
    # 2. Gọi toán tử Delaunay Triangulation của BlenderGIS
    bpy.ops.gis.delaunay_voronoi(mode='DELAUNAY')
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Lỗi giật hình và biến dạng lưới (Vertex Jitter & Mesh Distortion):**
  * *Nguyên nhân:* Do import trực tiếp file ở dạng độ thập phân (Decimal Degrees) hoặc đối tượng nằm cách xa gốc tọa độ thế giới quá \\(30.000\text{ m}\\) [6, 7, 14].
  * *Cách kiểm tra/Sửa:* Kiểm tra lại CRS trong QGIS và chuyển đổi về hệ tọa độ chiếu phẳng (mét) trước khi nhập [6-8], đồng thời đảm bảo bật tính năng local projection offset \\(\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\) [12, 13, 15].

* **Lỗi Polygon bị lấp kín lỗ (Polygon Hole Error):**
  * *Nguyên nhân:* Nhập Shapefile kiểu polygon có các vùng lỗ (holes), nhưng toán tử vẫn tự động tạo mặt kín lấp đè lên các lỗ đó [16, 17, 23, 24].
  * *Cách kiểm tra/Sửa:* Làm sạch hình học (repair/clean geometry) bằng QGIS trước khi import [23, 24, 29, 30], hoặc chọn loại bỏ các đỉnh trùng lặp (remove duplicate vertices với tolerance khoảng cách phù hợp) [23, 24, 29, 30].

* **Lỗi mặt bị đen / Lỗi hiển thị Render (Black Faces & Camera Clipping):**
  * *Nguyên nhân:* Phạm vi địa hình quá rộng làm vượt giới hạn độ sâu Z-depth của Camera [23, 24, 29, 30].
  * *Cách kiểm tra/Sửa:* Tăng giá trị `Clip End` và kéo `Clip Start` của Camera về gần scene hơn để Blender cải thiện độ chính xác tính toán Z-depth của các đỉnh [23, 24, 29, 30].

* **Lỗi đọc file Shapefile (`pyShp` Parser Issues):**
  * *Nguyên nhân:* Xuất hiện thông báo *"Unable to read shapefile"*, *"Unable to extract geometry"* hoặc *"Unable to read DBF table"* do lỗi thư viện `pyshp` [18, 19, 31].
  * *Cách kiểm tra/Sửa:* Mở file Shapefile trong QGIS, tiến hành xóa các trường dữ liệu DBF không cần thiết và export lại file mới để làm sạch dữ liệu [23, 24].

---

🗺️ Bạn có muốn tìm hiểu thêm về cách gắn ảnh hàng không/ảnh vệ tinh (Georeferenced Raster) lên bề mặt địa hình 3D vừa tạo không?
