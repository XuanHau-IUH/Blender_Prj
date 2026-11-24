# [C04] Camera Blocking cho đối thoại: Quy tắc trục 180 độ, Over-The-Shoulder (OTS) và Shot/Reverse-Shot

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

### 1. Tóm tắt Bản chất (2-3 câu)
**Dàn dựng máy quay (Virtual Cinematography/Camera Blocking) trong Blender là quá trình thiết lập vị trí, thông số tiêu cự, tiêu điểm và chuyển động của máy quay nhằm định hình bố cục và dẫn dắt sự chú ý của người xem [1, 2].** Việc làm chủ các nguyên lý máy quay giúp truyền tải cảm xúc và duy trì dòng chảy thị giác liền mạch giữa các góc cắt [2, 3]. *(Lưu ý: Nguồn tài liệu trong sổ hiện cung cấp đầy đủ về cơ chế máy quay, tiêu cự, liên kết Empty, chuyển nét và quản lý màu sắc trong Blender, nhưng chưa có tài liệu riêng về Quy tắc trục 180 độ đối thoại 2-4 người, góc Over-The-Shoulder (OTS) hay Eyeline Match).*

---

### 2. Nguyên lý & Thông số Chuẩn

* **Phân tách cơ chế Máy quay (Body vs. Lens):** Trong thực tế, máy quay gồm thân máy và ống kính [1]. Trong Blender, thuộc tính camera quản lý **Tiêu cự (Focal Length)**, **Khẩu độ (Aperture / f-stops)** và **Trường nhìn (Field of View)** [1]. Các thông số như tốc độ khung hình (FPS) hay độ phân giải nằm ở mục **Output Properties** [1, 4, 5].
* **Dải tương phản (Dynamic Range):** Thiết lập View Transform sang **Filmic** cung cấp dải tương phản rộng tới **25 stops**, vượt trội so với chuẩn **Standard** chỉ đạt **8 stops** [5].
* **Tốc độ khung hình chuẩn (FPS):** Mặc định chuẩn phim ảnh là **24 FPS** (được cấu hình trong Output Properties) [4-6].
* **Tiêu cự góc rộng (Focal Length):** Thường sử dụng tiêu cự **30mm – 35mm** cho các góc quay thiết lập bối cảnh hoặc đặt nhân vật theo quy tắc 1/3 (Rule of Thirds) [7].
* **Tính liên tục chuyển động (Continuation of Motion):** Chuyển động ở góc máy trước nên được tiếp diễn sang góc máy tiếp theo (hoặc sử dụng chuyển động đối lập - Opposed Motion) để tạo sự mượt mà hoặc tương phản thị giác giữa các cú cắt [3, 8].
* **Hình dáng Bokeh (Aperture Blades):** Số lá khẩu quyết định hình dạng đốm mờ Boke: **0** (tròn mặc định), **3** (tam giác), **4** (hình vuông), **5** (ngũ giác), **6** (lục giác) [9].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Thao tác thủ công trong Viewport:
1. **Căn góc nhìn máy quay nhanh:** Xoay Viewport đến góc nhìn ưng ý và nhấn **`Ctrl + Alt + Numpad 0`** (hoặc vào *View -> Align View -> Align Active Camera to View*) để đưa máy quay trực tiếp về góc nhìn đó [7, 10].
2. **Điều khiển máy quay qua Empty (Empty Camera Parenting):**
   * Tạo một đối tượng Empty tại vị trí mục tiêu/nhân vật [11].
   * Chọn Camera, giữ Shift chọn tiếp Empty và nhấn **`Ctrl + P`** (*Set Parent to Object*) [3, 11].
   * Chọn Empty và nhấn **`R` 2 lần** (Trackball rotation) để xoay máy quay quanh nhân vật một cách chính xác [3].
3. **Chuyển tiêu điểm nét (Rack Focus):** Bật tùy chọn **Depth of Field (DoF)** trên Camera, chọn mục tiêu Focus là đối tượng Empty, sau đó đặt keyframe vị trí cho Empty để dịch chuyển vùng nét giữa các nhân vật [2, 12].
4. **Chuẩn hóa thông số trước khi Animation:** Chọn máy quay/vật thể, nhấn **`Ctrl + A`** và chọn **Rotation & Scale** để đưa giá trị Rotation về `0,0,0` và Scale về `1,1,1` [13].

#### Đoạn mã Python (`bpy`) thiết lập Camera & Scene chuẩn:

```python
import bpy

# 1. Thêm Camera và cấu hình Tiêu cự / DoF
cam_data = bpy.data.cameras.new(name="Cinematic_Camera")
cam_data.lens = 35  # Tiêu cự 35mm
cam_data.dof.use_dof = True  # Bật Depth of Field

cam_obj = bpy.data.objects.new(name="Cinematic_Camera", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# 2. Tạo Empty làm mục tiêu theo dõi và lấy nét (Rack Focus Target)
target_empty = bpy.data.objects.new(name="Cam_Target_Empty", object_data=None)
bpy.context.collection.objects.link(target_empty)
cam_data.dof.focus_object = target_empty  # Gán Empty làm tiêu điểm DoF

# 3. Làm cha-con (Parenting) Camera vào Empty để xoay quanh nhân vật
cam_obj.parent = target_empty

# 4. Cấu hình màu sắc Filmic (25 stops) & Khung hình 24 FPS
bpy.context.scene.render.fps = 24
bpy.context.scene.view_settings.view_transform = 'Filmic'
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Quên chuyển sang dải màu Filmic:** Giữ nguyên mặc định Standard khiến hình ảnh dễ bị cháy sáng và mất chi tiết ở vùng tối (do giới hạn 8 stops) [5].
* **Chưa Apply Rotation & Scale (`Ctrl + A`):** Khiến các thao tác xoay máy quay hoặc biến đổi keyframe bị méo góc nhìn không mong muốn [13].
* **Bóng cắt của Area Light do giới hạn 180 độ:** Đèn Area Light trong Blender chỉ phát sáng trong góc 180 độ [14]. Khi đặt đèn quá bẹt dễ tạo vết cắt bóng không tự nhiên; nên đặt đèn hơi chếch phía sau đối tượng (*lighting from the outside*) để tạo viền sáng mềm mại [14, 15].
* **Lạm dụng chuyển động máy quay (Camera Shake/Motion):** Thêm quá nhiều nhịp rung lắc liên tục dễ gây nhức mắt; cần đan xen các góc quay cố định (Tripod Shot) để tạo khoảng nghỉ cho thị giác [8, 16].
* **Sa đà vào chi tiết vi mô:** Dành quá nhiều thời gian tỉ mỉ vào chi tiết nhỏ mà người xem không nhận ra thay vì tập trung tối ưu bố cục khung hình và ánh sáng chính [17, 18].

---

*Tài liệu trong sổ chưa bao hàm quy tắc đường trục 180 độ đối thoại hay kỹ thuật đặt góc OTS cho cảnh nhiều người. Bạn có muốn tôi tìm kiếm thêm thông tin trên web về quy tắc trục đối thoại và góc OTS để bổ sung vào sổ tay của bạn không?*

🎬 **Gợi ý tiếp theo:** Bạn có muốn thử nghiệm tạo một đoạn script Python tự động hóa kỹ thuật **Dolly Zoom** (phóng to tiêu cự kết hợp lùi máy quay) dựa trên các ghi chép trong tài liệu?
