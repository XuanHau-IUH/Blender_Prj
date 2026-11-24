# [G09] Tối ưu hóa đại cảnh môi trường lớn (Camera Frustum Culling, LOD, Linked Collections & Memory Budget)

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

### 1. Tóm tắt Bản chất

Tối ưu hóa cảnh đô thị và môi trường GIS quy mô lớn trong Blender là hệ thống phối hợp giữa **ẩn vật thể ngoài góc nhìn camera (Camera Frustum Culling)**, **thay đổi mức độ chi tiết theo khoảng cách (Level of Detail - LOD)** và **quản lý bộ nhớ thông qua instancing cùng việc tái định vị mốc tọa độ (Origin Re-Centering)** [1-4]. Kỹ thuật này giúp giải phóng bộ nhớ RAM/VRAM, duy trì tốc độ khung hình (FPS) mượt mà trong Viewport và tăng tốc độ rendering khi xử lý các môi trường chứa hàng triệu vật thể hay đám mây điểm (Point Cloud) [2, 3, 5, 6]. Đồng thời, nó loại bỏ triệt để hiện tượng rung lắc mô hình (mesh jittering) và tràn giới hạn bộ nhớ buffer của Blender khi làm việc với dữ liệu bản đồ diện rộng [5, 7-10].

---

### 2. Nguyên lý & Thông số Chuẩn

#### A. Tự động ẩn ngoài góc nhìn (Camera Frustum Culling)
* **Nguyên lý không gian**: Chuyển đổi tọa độ các điểm từ không gian thế giới (World Space) sang không gian màn hình chuẩn hóa (Normalized Screen Space) của Camera [11-13]. Tạo một mặt nạ Boolean kiểm tra điều kiện [3, 11, 12, 14]:
  \\[0.0 \le X_{\text{screen}} \le 1.0 \quad \text{và} \quad 0.0 \le Y_{\text{screen}} \le 1.0\\]
  Mặt nạ này được nối vào cổng **Selection** của các nút phân bố điểm (`Distribute Points on Faces`) hoặc `Instance on Points` để Blender chỉ khởi tạo hình học nằm trong tầm mắt camera [3, 11, 12, 14].
* **Thông số nút Frustum Culling**: Sử dụng dữ liệu từ nút **Camera Info** bao gồm Focal Length, Matrix Data, Sensor Size (mặc định **36 mm**), X/Y Shift và Resolution [11, 15, 16].
* **Khoảng cách Clip Distance**: Thiết lập `clip_start` và `clip_end` cho Viewport và Camera [17-21]. Khi xử lý cảnh lớn, việc kéo `clip_start` lại gần cảnh hơn sẽ giúp Blender tính toán độ chính xác vị trí đỉnh theo chiều sâu Z của camera tốt hơn, tránh lỗi rác đen mặt cắt render [17, 18, 20, 21].

#### B. Giảm mức chi tiết theo khoảng cách (Level of Detail - LOD)
* **Tính khoảng cách Euclidean (\\(d\\))**: Tính toán khoảng cách giữa vị trí camera và từng vị trí instance [22-24]:
  \\[d = \sqrt{(X_{\text{inst}} - X_{\text{cam}})^2 + (Y_{\text{inst}} - Y_{\text{cam}})^2 + (Z_{\text{inst}} - Z_{\text{cam}})^2}\\]
* **Phân cấp chỉ số Instance Index**: Đưa khoảng cách \\(d\\) qua nút **Map Range** (chế độ `Stepped Linear` / `Floor Integer`) để chuyển thành các số nguyên tương ứng với chỉ số của Collection [25-28]. Giá trị này nối vào cổng **Instance Index** của nút **Instance on Points** (kích hoạt `Pick Instance` và `Separate Children`) [25-27].
* **Ngưỡng khoảng cách phân cấp tiêu chuẩn**:
  * \\(0.0\,\text{m} \le d < 20.0\,\text{m} \implies 0\\) (**LOD0**: Mô hình lưới độ phân giải cao - High-Res Mesh) [25-27]
  * \\(20.0\,\text{m} \le d < 80.0\,\text{m} \implies 1\\) (**LOD1**: Mô hình chi tiết trung bình - Mid-Res Mesh) [25-27]
  * \\(80.0\,\text{m} \le d < \infty \implies 2\\) (**LOD2**: Card/Billboard chi tiết thấp - Low-Res Card) [25-27]
* **Làm mềm ranh giới chuyển LOD (Seamless Blend)**: Để xóa bỏ đường ranh giới vòng tròn cứng (circular swapping rings) gây giật hình khi camera di chuyển, thêm nút **Noise Texture** hoặc **Attribute Random** trộn vào giá trị khoảng cách để làm biến dạng và xáo trộn ranh giới chuyển đổi một cách ngẫu nhiên [28-32].
* **Khâu viền địa hình (Topological Boundary Stitching)**: Giải quyết vết nứt hở viền giữa các mảnh địa hình LOD khác nhau bằng cách cô lập cạnh biên (`Boundary Selection Mask`), chiếu các đỉnh biên tới lưới LOD thấp hơn (`Proximity Projection`), sau đó áp dụng nút **Merge by Distance** để hàn kín điểm hở [33-35].

#### C. Quản lý bộ nhớ Texture, Instances & Độ chính xác GIS
* **Tối ưu hóa Instancing**: Sử dụng nút **Instance on Points** để tạo các tham chiếu hình học (share Data Block) thay vì nhân bản thực thể mesh, giúp tiết kiệm RAM/VRAM khi rải hàng trăm nghìn cây cối, tòa nhà [36-40]. Phân bố điểm bằng thuật toán **Poisson Disk** với tham số `Distance Min` để đảm bảo khoảng cách tối thiểu giữa các vật thể, tránh chồng lấp [2, 41-44].
* **Giới hạn Buffer Point Cloud**: Blender có giới hạn bộ nhớ buffer điểm cố định khoảng **4.2 GB mỗi object** [5, 45, 46]. Khi nạp đám mây điểm dung lượng lớn, phải chia dữ liệu thành các object LOD riêng biệt để không vượt giới hạn này [5, 45, 46].
* **Khắc phục xung đột số thực (Single 32-bit vs. Double 64-bit Precision)**: Dữ liệu bản đồ GIS sử dụng số thực 64-bit (double precision) [7, 8, 47]. Trong khi đó, Blender sử dụng số thực 32-bit (single precision với khoảng **7 chữ số có nghĩa** ~ 7 significant digits) [7, 48-51]. Nếu nhập tọa độ tuyệt đối xa gốc (như tọa độ UTM vài trăm nghìn mét), đỉnh lưới sẽ bị snap sai lệch dẫn đến hiện tượng biến dạng và rung lắc (mesh jittering) [7, 10, 48-51].
* **Mô hình Geoscene (Origin Re-Centering)**: Đặt vectơ dịch chuyển \\(\mathbf{T}_{\text{offset}} = (X_{\text{geo\_origin}}, Y_{\text{geo\_origin}}, Z_{\text{geo\_origin}})\\) để dời mô hình về gần gốc tọa độ Cartesian (0,0,0) trong Blender [7, 52-55]. Tọa độ địa lý thực tế được lưu trữ dưới dạng các custom properties của Scene (`Scene CRS`, `Scene Origin Offset`) [7, 52, 54, 56].
* **Cắt lọc DEM & Raster**: Cắt nhỏ (clip) phạm vi dữ liệu DEM/Raster bằng thư viện GDAL hoặc phần mềm QGIS trước khi nạp vào Blender, đồng thời chọn đúng Bit Depth (`float32` so với `non-float raster`) [57-63].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Quyền Thao tác GUI
1. **Dời gốc tọa độ (Geoscene Re-Centering)**: Khi import dữ liệu bản đồ qua addon **BlenderGIS**, chọn tùy chọn *Sub-origin / Re-center space* để tự động dời mốc địa lý về gần gốc (0,0,0) [7, 52-54].
2. **Cấu hình Clipping Viewport & Camera**: Mở panel thuộc tính `N` > thẻ *View* > điều chỉnh `Clip Start` = `0.1m` và `Clip End` = `10000m` [19, 64, 65].
3. **Thiết lập Geometry Nodes LOD & Culling**:
   * Trên base mesh địa hình, tạo mới Geometry Nodes Modifier [66-68].
   * Kéo nhóm vật thể LOD (LOD0, LOD1, LOD2) vào Node Tree dưới dạng **Collection Info** [25, 67, 69, 70].
   * Nối nút **Camera Info** (Location) và nút **Position** vào nút **Vector Math** (`Distance`), sau đó đưa qua nút **Map Range** kết nối vào cổng `Instance Index` của nút **Instance on Points** (bật `Pick Instance` và `Separate Children`) [23-27].
   * Thêm nút **Noise Texture** cộng vào giá trị khoảng cách để làm mềm ranh giới chuyển LOD [28-32].

#### Đoạn Mã Python `bpy` Cấu hình Hệ thống Tối ưu hóa

```python
import bpy


def setup_gis_environment_optimization():
  scene = bpy.context.scene

  # 1. Cấu hình Camera Clipping
  if scene.camera and scene.camera.type == "CAMERA":
    cam_data = scene.camera.data
    cam_data.clip_start = 0.1
    cam_data.clip_end = 10000.0
    print(
        f"Camera '{scene.camera.name}' Clip range: {cam_data.clip_start}m -"
        f" {cam_data.clip_end}m"
    )

  # 2. Cấu hình Viewport 3D Clip Distances để tránh lỗi Z-buffer splitting
  for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
      for space in area.spaces:
        if space.type == "VIEW_3D":
          space.clip_start = 0.1
          space.clip_end = 10000.0

  # 3. Khởi tạo thuộc tính Geoscene Origin Re-Centering (Khắc phục Single Precision 32-bit Limit)
  scene["CRS"] = "EPSG:32648"  # Ví dụ Hệ tọa độ UTM Zone 48N
  scene["geo_origin_x"] = 485000.0  # Tọa độ thực (64-bit float offset)
  scene["geo_origin_y"] = 1200000.0
  scene["geo_origin_z"] = 0.0

  print(
      "Đã thiết lập Geoscene Origin Offset thành công tại (0,0,0) Cartesian."
  )


# Thực thi script
setup_gis_environment_optimization()
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

| Lỗi thường gặp | Nguyên nhân | Cách kiểm tra & Khắc phục |
| :--- | :--- | :--- |
| **Mô hình bị giật lag và nứt gãy mesh (Mesh Jittering / Distortion)** | Nhập mô hình ở tọa độ địa lý tuyệt đối xa mốc (0,0,0) làm vượt quá giới hạn **7 chữ số có nghĩa** của số thực 32-bit `float32` [7, 10, 48-51]. | Kiểm tra tọa độ X, Y của vật thể trong Viewport. Nếu giá trị > 10,000m, cần sử dụng tính năng Origin Re-Centering để dời mô hình về gốc Cartesian (0,0,0) [7, 10, 53, 55, 71]. |
| **Ranh giới chuyển LOD bị giật cứng (Abrupt Hard LOD Lines)** | Đường ranh giới giữa các cấp LOD dạng vòng tròn đồng tâm lộ rõ khi camera di chuyển [28, 30, 31, 72, 73]. | Thêm nút **Noise Texture** hoặc **Attribute Random** trộn vào giá trị khoảng cách Euclidean để xáo trộn đường ranh giới chuyển đổi [28-32]. |
| **Mặt cắt bị rác đen (Black Faces Error / Depth Artifacts)** | Đặt `clip_end` quá xa trong khi giữ nguyên `clip_start` mặc định quá nhỏ làm Z-buffer thiếu độ phân giải [17, 18, 20, 21]. | Kéo `clip_start` lên gần cảnh hơn (từ `0.01m` lên `0.1m` hoặc `1m`) để Blender phân bổ độ sâu Z chính xác hơn [17, 18, 20, 21]. |
| **Tràn bộ nhớ Viewport / Treo máy (Buffer Overflows)** | Dùng nút `Realize Instances` làm phá hủy tính năng Instancing [40, 74], nạp Point Cloud vượt quá **4.2 GB buffer limit** cho 1 object [5, 45, 46], hoặc nạp DEM quá lớn mà không dùng GDAL clip [57, 62]. | Giữ nguyên Instancing (hạn chế dùng `Realize Instances`) [40, 74], tách Point Cloud lớn thành các sub-object LOD [5, 45, 46] và dùng GDAL/QGIS để crop DEM trước khi nạp [57, 61-63]. |

---

💡 **Gợi ý bước tiếp theo**: Bạn có muốn tôi hướng dẫn cách xây dựng chi tiết từng node cụ thể trong Geometry Nodes để kết nối **Camera Frustum Culling** và **LOD Distance Switching** trên cùng một tuyến node (Node Tree) không?
