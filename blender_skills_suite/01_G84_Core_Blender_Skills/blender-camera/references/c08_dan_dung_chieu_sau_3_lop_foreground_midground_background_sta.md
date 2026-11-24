# [C08] Dàn dựng chiều sâu 3 lớp (Foreground - Midground - Background Staging) trong không gian 3D

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

Hiệu ứng thị sai (**Parallax Effect**) khi máy quay di chuyển là chìa khóa để chuyển đổi một cảnh quay từ dạng "hình ảnh phẳng" thành một không gian 3D có độ sâu điện ảnh [1-3].

---

### 1. Tóm tắt Bản chất (2-3 câu)
Hiệu ứng thị sai xảy ra khi máy quay di chuyển, khiến các vật thể ở gần (Tiền cảnh) lướt qua màn hình với tốc độ nhanh hơn so với các vật thể ở xa (Trung cảnh và Hậu cảnh) [1-5]. Việc phân tách rõ ràng 3 lớp không gian không chỉ giúp che mờ các mép khung hình vụng về mà còn dẫn dắt ánh nhìn của khán giả tập trung tự nhiên vào nhân vật/chủ thể chính [1-3, 6-11].

---

### 2. Nguyên lý & Thông số Chuẩn (Trích xuất từ tài liệu)

#### **Phân lớp cấu trúc không gian 3 lớp:**
* **Tiền cảnh (Foreground Silhouette / Frame - FG):** 
  * Đặt các chi tiết như cành cây, khung cửa, thuyền, đá hoặc bóng đen (silhouette) ở khoảng cách rất gần ống kính máy quay [8-13]. 
  * Tiền cảnh thường được làm mờ nhẹ nhờ độ sâu trường ảnh (Depth of Field) hoặc che bớt một phần viền khung hình để tạo điểm bám thị giác cho mắt người xem [9, 12, 14, 15].
* **Trung cảnh (Midground - MG):**
  * Nơi đặt nhân vật hoặc vật thể chính (ngôi nhà, sản phẩm, nhân vật) [6, 7]. 
  * Áp dụng **Quy tắc 1/3 (Rule of Thirds)** bằng cách đặt chủ thể lệch về phía bên trái hoặc bên phải khung hình thay vì chính giữa [7].
* **Hậu cảnh (Background - BG):**
  * Xây dựng môi trường quy mô lớn (dãy núi, rừng cây, mặt nước kéo dài đến đường chân trời) [8, 16-20].
  * Phủ sương mù thể tích (Volumetric Fog) và ánh sáng nền để tạo sự tách biệt về màu sắc và khoảng cách khí quyển [21-23].

#### **Thông số kỹ thuật chuẩn trong Blender:**
* **Tiêu cự Camera (Focal Length):** Sử dụng ống kính góc rộng **30mm – 35mm** cho môi trường lớn để mở rộng góc nhìn và phóng đại khoảng cách di chuyển giữa các lớp, từ đó tạo Parallax mạnh mẽ hơn [6].
* **Độ phân giải & Tần số khung hình (FPS):** Thiết lập chuẩn **24 FPS**, dải khung hình chuẩn từ frame 1 đến 120 (5 giây) hoặc 240 (10 giây) [24].
* **Chuẩn hóa Vật thể:** Nhấn `Ctrl + A` -> chọn **Rotation & Scale** cho toàn bộ vật thể trước khi tạo keyframe animation để tránh sai lệch thông số [25].
* **Độ sâu trường ảnh (Depth of Field & Bokeh):** Bật DoF trên Camera và gán **Focus Target** vào một `Empty` đặt tại chủ thể ở Trung cảnh [1, 2]. Thiết lập số cánh khẩu (Aperture Blades) để tạo dáng Bokeh: `0` (tròn mặc định), `3` (tam giác), `4` (vuông), `5` (ngũ giác), `6` (lục giác) [26].
* **Sương mù thể tích (Volumetric Fog):** Sử dụng shader `Principled Volume` với chỉ số `Density = 0.005` [22]. Lùi khối Cube sương mù xa khỏi ống kính máy quay để giữ Tiền cảnh trong trẻo và làm mờ dần Hậu cảnh [14].
* **Quản lý dải động màu sắc (Color Management):** Chuyển chế độ Color Management sang **Filmic** thay vì Standard để sở hữu dải động 25 stop (so với 8 stop của Standard), giúp giữ lại chi tiết cả ở bóng tối Tiền cảnh và vùng sáng Hậu cảnh [27].
* **Hướng ánh sáng điện ảnh (Outside Lighting):** Đặt nguồn sáng chính (Area Light hoặc Sun) ở phía sau hoặc bên hông chủ thể ("outside lighting"), tránh chiếu trực diện từ phía máy quay để tạo viền sáng (rim light) và hình thành bóng đen nổi bật hình khối [13, 28-36].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### **Các bước thao tác trên giao diện Blender:**
1. **Thiết lập Camera & Bố cục:** Tạo Camera, cài đặt tiêu cự 35mm [6]. Đặt nhân vật chính ở Trung cảnh theo quy tắc 1/3 [7].
2. **Thêm Tiền cảnh:** Đặt các vật thể (như cành cây, lá cây khô, khối kiến trúc) sát ngay trước ống kính [9, 12].
3. **Tạo Empty Parenting:** Tạo một đối tượng `Empty` tại vị trí chủ thể Trung cảnh [4]. Chọn Camera, sau đó chọn Empty, nhấn `Ctrl + P` -> chọn **Keep Transform** để làm cha-con [4, 5].
4. **Cài đặt DoF:** Chọn Camera, bật **Depth of Field**, đặt ô **Focus Object** trỏ tới `Empty` ở Trung cảnh [2].
5. **Animation Parallax:** Xoay hoặc trượt `Empty` (hoặc di chuyển máy quay theo phương ngang/tiến lùi), đặt keyframe trên Timeline (`phím I`) [4, 5, 25, 37-40]. Có thể áp dụng thêm kỹ thuật **Dolly Zoom** (kéo máy quay lùi ra xa đồng thời zoom tiêu cự vào) để tạo sự biến dạng không gian kịch tính [2, 3].

#### **Đoạn mã Python (`bpy`) thiết lập tự động:**

```python
import bpy

# 1. Tạo Empty làm tâm ngắm (Target) ở Trung cảnh (Midground)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 5, 1))
target_empty = bpy.context.active_object
target_empty.name = "MG_Target_Empty"

# 2. Tạo Camera và thiết lập thông số (Tiêu cự 35mm góc rộng, DoF)
bpy.ops.object.camera_add(location=(0, 0, 1.2), rotation=(1.35, 0, 0))
camera_obj = bpy.context.active_object
camera_obj.name = "Main_Camera"
bpy.context.scene.camera = camera_obj

camera_data = camera_obj.data
camera_data.lens = 35  # Tiêu cự 35mm gia tăng biến dạng thị sai Parallax
camera_data.dof.use_dof = True
camera_data.dof.focus_object = target_empty  # Tự động lấy nét vào nhân vật chính
camera_data.dof.aperture_fstop = 2.8  # Mở khẩu F2.8 xóa phông Tiền cảnh & Hậu cảnh

# 3. Gắn Parent Camera vào Empty để quỹ đạo di chuyển quanh chủ thể mượt mà
camera_obj.select_set(True)
target_empty.select_set(True)
bpy.context.view_layer.objects.active = target_empty
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

# 4. Cài đặt thông số Timeline (24 FPS, 120 Frames = 5 giây)
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120
bpy.context.scene.render.fps = 24

# 5. Đặt Keyframe xoay Empty để máy quay trượt ngang tạo hiệu ứng Parallax rõ rệt
target_empty.rotation_euler = (0, 0, -0.15)
target_empty.keyframe_insert(data_path="rotation_euler", frame=1)

target_empty.rotation_euler = (0, 0, 0.15)
target_empty.keyframe_insert(data_path="rotation_euler", frame=120)
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Lỗi 1: Quên chưa Apply Rotation & Scale:** Làm vật thể bị biến dạng sai lệch hoặc chuyển động animation bị giật/méo [25].
  * *Cách sửa:* Chọn tất cả vật thể trong cảnh, nhấn `Ctrl + A` -> chọn **Rotation & Scale** trước khi đặt keyframe [25].
* **Lỗi 2: Tiền cảnh che mất chủ thể hoặc đặt quá xa Camera:** Khiến hiệu ứng Parallax bị nhạt nhòa hoặc làm xấu bố cục [9].
  * *Cách kiểm tra:* Chia màn hình làm 2 (Split Screen): một bên mở Viewport 3D để di chuyển vật thể, một bên mở góc nhìn Camera View để theo dõi mép khung hình thực tế [9, 30, 31].
* **Lỗi 3: Ánh sáng chiếu thẳng từ mặt trước máy quay (Flat Lighting):** Làm tiêu biến bóng đổ, khiến các lớp không gian bị bẹt dí vào nhau [13, 28-36].
  * *Cách sửa:* Đặt nguồn sáng ở phía sau hoặc bên cạnh chủ thể ("outside lighting") để đổ bóng phía trước, làm nổi bật đường nét hình khối [13, 28-36].
* **Lỗi 4: Sương mù sương thể tích trùm kín lên ống kính Camera:** Phủ đục Tiền cảnh, làm mất độ tương phản và chi tiết [14].
  * *Cách sửa:* Đẩy khối Cube Volumetric lùi về phía sau Camera sao cho khu vực Tiền cảnh nằm ngoài khối sương [14].
* **Lỗi 5: Chuyển động máy quay quá cứng hoặc nhanh gây nhức mắt:**
  * *Cách sửa:* Bật tính năng **Motion Blur** trong tab Render [1, 27] hoặc cài đặt add-on miễn phí **Camera Shakeify** để thêm độ rung lắc nhẹ tự nhiên cho máy quay [26, 41].

🎬 Bạn có muốn tôi hướng dẫn chi tiết thêm về kỹ thuật tạo hiệu ứng trượt ống kính **Dolly Zoom** (kéo máy quay kết hợp đổi tiêu cự) để gia tăng hiệu ứng Parallax ấn tượng hơn không?
