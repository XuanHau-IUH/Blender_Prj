# [C02] Cỡ cảnh điện ảnh (Shot Sizes: EWS, WS, MS, MCU, CU, ECU) và chiều cao đặt máy (Camera Height & Angle)

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

Dưới đây là tổng hợp hệ thống thiết lập camera, góc máy và tư duy cinematographic được trích xuất từ các tài liệu trong sổ của bạn:

---

### 1. **Tóm tắt Bản chất**
Thiết lập camera và góc máy trong môi trường 3D (Cinematography) là cầu nối giữa công cụ kỹ thuật phần mềm và nghệ thuật kể chuyện thị giác [1]. Nó giúp định hình cảm xúc, dẫn dắt sự chú ý của người xem, tạo chiều sâu cho không gian và truyền tải thông điệp câu chuyện thông qua việc làm chủ tiêu cự, chuyển động, độ sâu trường ảnh và mối tương quan với ánh sáng [2-4].

> **Lưu ý về phạm vi tài liệu:** Các nguồn trong sổ tập trung chuyên sâu vào các **nguyên lý quay phim 3D trong Blender** (tiêu cự, Dolly Zoom, Rack Focus, quy tắc 1/3, tùy chỉnh Bokeh, góc chiếu sáng Outside/Inside) [2, 4-8]. Tuy nhiên, tài liệu không chứa danh mục phân loại lý thuyết truyền thống về các **cỡ cảnh** (như *Extreme Long Shot, Medium Shot, Close-up...*) cũng như định nghĩa góc độ chính xác của *High Angle, Low Angle hay Dutch Tilt*. Nếu bạn muốn mình thực hiện tìm kiếm trên web để bổ sung phần lý thuyết phân loại cỡ cảnh và góc máy này, hãy báo cho mình biết nhé!

---

### 2. **Nguyên lý & Thông số Chuẩn**

- **Tiêu cự (Focal Length) & Bố cục khung hình**:
  - **30mm – 35mm**: Thích hợp cho các cảnh môi trường/ngoại cảnh quy mô lớn (large-scale landscape) để tạo độ mở không gian [5].
  - **Quy tắc 1/3 (Rule of Thirds)**: Đặt chủ thể lệch về 1/3 bên trái hoặc bên phải khung hình nhằm tạo sự cân bằng thị giác và chừa khoảng trống cho bối cảnh xung quanh [6].
- **Dải tương phản động (Dynamic Range) & Quản lý màu**:
  - Luôn chọn chế độ Quản lý màu **Filmic** (đạt dải tương phản tới **25 stops**), vượt trội hơn tầm mắt người (15–20 stops) và chế độ Standard mặc định (chỉ có **8 stops**) [9].
- **Tốc độ màn cửa & Độ mờ chuyển động (Motion Blur)**:
  - Độ mờ chuyển động được điều khiển thông qua chỉ số **Shutter**: Giá trị Shutter nhỏ tương ứng với tốc độ màn cửa nhanh (ít mờ), giá trị Shutter lớn mô phỏng tốc độ màn cửa chậm (mờ nhiều) [2, 9].
- **Các kỹ thuật chuyển động & Lấy nét điện ảnh**:
  - **Rack Focus (Chuyển tiêu điểm)**: Thay đổi độ sâu trường ảnh (Depth of Field - DoF) từ đối tượng này sang đối tượng khác nhằm hé lộ tình tiết quan trọng và điều hướng mắt người xem [2, 3].
  - **Dolly Zoom (Hiệu ứng Vertigo)**: Di chuyển camera lùi ra xa chủ thể đồng thời tăng tiêu cự (zoom in) hoặc ngược lại, giúp duy trì kích thước chủ thể nhưng tạo sự biến dạng góc nhìn liên tục [3, 7].
  - **Tùy chỉnh hình dạng Bokeh (Aperture Blades)**: Tùy chỉnh số lá khẩu trong cài đặt DoF. Mặc định **0** = hình tròn, **3** = tam giác, **4** = hình vuông, **5** = ngũ giác, **6** = lục giác [8, 10].
  - **Tiếp diễn chuyển động (Continuation of Motion)**: Duy trì luồng hướng chuyển động liên tục của camera hoặc đối tượng qua các góc cắt cảnh (cut shots) để giữ nhịp điệu cho animation [11].
  - **Mối tương quan Góc máy & Ánh sáng (Outside vs. Inside Lighting)**: Bố trí ánh sáng ở góc "Outside" (phía sau chủ thể, nằm giữa chủ thể và background) giúp tạo điểm nhấn đường viền (highlight) và lớp bóng đổ tự nhiên tạo cảm giác bí ẩn, thay vì đặt ở góc "Inside" (phía trước camera) gây bẹt hình [4, 12-14].
- **Thông số Cấu hình khung hình**:
  - Tốc độ khung hình tiêu chuẩn: **24 FPS** [15-17].
  - Độ phân giải tiêu chuẩn: **1920x1080** [16, 17].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### a) Thao tác thủ công trong Blender:
1. **Tạo & Căn góc Camera**:
   - Nhấn `Shift + A` > **Camera** [5, 18].
   - Nhấn `Ctrl + Alt + Numpad 0` để đưa camera về đúng góc nhìn Viewport hiện tại [5, 18].
2. **Xoay máy quanh chủ thể (Empty Camera Parenting)**:
   - Tạo một **Empty** tại vị trí chủ thể (`Shift + A` > Empty) [19].
   - Chọn Camera, giữ `Shift` chọn Empty -> nhấn `Ctrl + P` chọn **Object** [11, 19].
   - Chọn Empty và nhấn `R` hai lần (`R R` - trackball rotation) để xoay camera mượt mà quanh chủ thể [11].
3. **Thiết lập Rack Focus**:
   - Chọn Camera > bật **Depth of Field** [3, 8].
   - Tại mục **Focus on Object**, chọn vật thể Empty [3]. Đặt keyframe vị trí cho Empty để chuyển tiêu điểm nét giữa các khung hình [3].
4. **Thiết lập Dolly Zoom**:
   - Tạo keyframe di chuyển camera lùi ra xa (đặt kiểu nội suy tuyến tính bằng phím `T` > chọn **Linear** trong Timeline) [7].
   - Tạo keyframe cho chỉ số **Focal Length** ở frame đầu và frame cuối sao cho tỉ lệ kích thước chủ thể khớp nhau [7].

#### b) Code Python (`bpy`) thiết lập Camera chuẩn:

```python
import bpy

# 1. Tạo và kích hoạt Camera mới
cam_data = bpy.data.cameras.new(name="Cinematic_Camera")
cam_obj = bpy.data.objects.new(name="Cinematic_Camera", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# 2. Thiết lập Tiêu cự (Focal Length) & Khung hình
cam_data.lens = 35  # Tiêu cự 35mm phù hợp cho ngoại cảnh/môi trường

# 3. Cấu hình Depth of Field (DoF) & Bokeh
cam_data.dof.use_dof = True

# Tạo Empty làm Target cho Rack Focus
target_empty = bpy.data.objects.new("Focus_Target", None)
bpy.context.collection.objects.link(target_empty)
cam_data.dof.focus_object = target_empty

# Tùy chỉnh lá khẩu Bokeh (Ví dụ: 5 lá khẩu -> Ngũ giác)
cam_data.dof.aperture_blades = 5

# 4. Thiết lập Color Management & Motion Blur cho Scene
scene = bpy.context.scene
scene.view_settings.view_transform = 'Filmic'  # Đạt dải tương phản 25 stops

# Thông số Output & Motion Blur
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = 0.5  # Thiết lập tốc độ màn cửa
scene.render.fps = 24  # 24 FPS chuẩn điện ảnh
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

- **Quên Reset Transformation trước khi Keyframe**: Để thông tin xoay/tỉ lệ gốc bị lệch khiến chuyển động camera hoặc vật thể bị biến dạng không mong muốn.
  - *Cách sửa*: Chuyển sang Object Mode, chọn vật thể/camera và nhấn `Ctrl + A` > chọn **Rotation & Scale** để đưa rotation về (0,0,0) và scale về (1,1,1) [20].
- **Giữ Quản lý màu ở chế độ Standard thay vì Filmic**: Dẫn đến vùng sáng dễ bị cháy và vùng tối bị mất chi tiết (chỉ có 8 stops so với 25 stops của Filmic) [9].
  - *Cách kiểm tra*: Mở bảng *Render Properties > Color Management*, đảm bảo mục *View Transform* đang chọn **Filmic** [9].
- **Đặt ánh sáng thẳng góc với Camera (Inside Lighting)**: Khiến cảnh quay bị phẳng (flat), làm mất đường nét và chiều sâu khối của chủ thể [12, 14, 21].
  - *Cách sửa*: Đặt nguồn sáng lệch góc hoặc chiếu từ phía sau chủ thể ("Outside") để làm nổi bật hình khối qua đường viền sáng và bóng đổ tự nhiên [4, 12, 13, 22].
- **Lạm dụng Rung máy (Camera Shake)**: Cài đặt cường độ rung quá mạnh khiến cảnh quay bị giật lắc, gây khó chịu cho người xem [23].
  - *Cách sửa*: Khi sử dụng add-on như *Camera Shakeify*, hãy tinh chỉnh chỉ số *Influence* và *Scale* ở mức nhỏ vừa phải (subtle) [23].

---

🎬 Bạn có muốn mình tạo một kịch bản script Python để tự động gán keyframe chuyển động cho hiệu ứng Dolly Zoom hoặc Rack Focus không?
