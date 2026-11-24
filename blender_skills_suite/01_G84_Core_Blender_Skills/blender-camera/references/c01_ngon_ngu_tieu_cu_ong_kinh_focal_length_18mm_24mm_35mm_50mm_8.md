# [C01] Ngôn ngữ tiêu cự ống kính (Focal Length: 18mm, 24mm, 35mm, 50mm, 85mm, 135mm) và độ nén không gian

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

**Tóm tắt Bản chất**
Trong Blender, camera 3D mô phỏng các thông số trực quan của ống kính thực tế như **tiêu cự (focal length)**, **khẩu độ (aperture/f-stop)** và **trường nhìn (field of view)** để điều chỉnh góc nhìn và phối cảnh của cảnh quay [1]. Việc lựa chọn tiêu cự và kiểm soát sự biến dạng phối cảnh (perspective distortion) giúp định hướng sự chú ý của người xem, làm nổi bật hình khối vật thể và tạo nên cảm xúc điện ảnh cho thước phim [2-4]. Đây là kiến thức cốt lõi trong nghệ thuật quay phim 3D (cinematography) để biến các cảnh dựng thô thành bối cảnh sống động và chân thực [1, 5].

---

**Nguyên lý & Thông số Chuẩn (Trích xuất từ tài liệu)**

1. **Cấu trúc Camera & Tiêu cự trong Blender**:
   - Đối tượng Camera trong Blender quản lý các thuộc tính của ống kính bao gồm **tiêu cự (focal length)**, **khẩu độ (aperture / f-stops)** và **trường nhìn (field of view)** [1, 6]. 
   - Với các khung cảnh thiên nhiên hoặc môi trường (landscape) quy mô lớn, tài liệu đề xuất thiết lập tiêu cự góc rộng (**wide angle**) ở mức **30mm đến 35mm** để bao quát toàn cảnh [7].

2. **Sự biến dạng phối cảnh & Hiệu ứng Dolly Zoom**:
   - Khoảng cách đặt camera kết hợp với tiêu cự quyết định độ biến dạng phối cảnh (perspective distortion) [3].
   - **Hiệu ứng Dolly Zoom** (tạo cảm giác chóng mặt / *vertigo* hoặc cảm giác phi thực tế) được thực hiện bằng cách di chuyển camera lùi xa hoặc tiến lại gần vật thể (dùng kiểu nội suy tuyến tính - *linear interpolation*), đồng thời điều chỉnh tiêu cự (focal length) sao cho kích thước vật thể trung tâm được giữ nguyên [3, 8].

3. **Độ sâu trường ảnh (Depth of Field) & Hình dạng Boke (Bokeh)**:
   - Khẩu độ (*f-stop*) và khoảng cách lấy nét (*focus distance*) tạo ra độ mờ tiền cảnh/hậu cảnh [2, 9, 10].
   - **Số lá khẩu (blade count)** quyết định hình dạng hạt Boke: `0` là hình tròn mặc định, `3` là hình tam giác, `4` là hình vuông, `5` là ngũ giác, và `6` là hình lục giác [10].

4. **Dải sáng (Dynamic Range)**:
   - Thiết lập Color Management ở chế độ `Filmic` mang lại dải sáng **25 stops** (vượt mức 15–20 stops của mắt người), trong khi chế độ `Standard` chỉ giới hạn ở **8 stops** [6].

> **Lưu ý về phạm vi tài liệu:** Các tài liệu trong sổ tay hiện tại tập trung vào nguyên lý ống kính chung, tiêu cự góc rộng 30–35mm và hiệu ứng Dolly Zoom, nhưng **chưa phân tích bảng phân loại chi tiết** cho từng dải tiêu cự riêng biệt (như 18–24mm, 50mm, 85mm+), tâm lý học cảm xúc cụ thể từng dải hay công thức toán học tính độ nén hậu cảnh (*Background Compression*). *(Nếu bạn muốn mở rộng tìm kiếm các dải tiêu cự này từ nguồn bên ngoài, tôi có thể thực hiện tìm kiếm trên web giúp bạn — bạn có muốn hỗ trợ không?)*

---

**Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

* **Thao tác thủ công trên giao diện Blender**:
  1. **Chỉnh tiêu cự & Depth of Field**: Chọn Camera \\(\rightarrow\\) vào bảng **Camera Properties** \\(\rightarrow\\) thiết lập **Focal Length** (ví dụ: `30mm`–`35mm` cho góc rộng) [6, 7]. Bật tùy chọn **Depth of Field**, chọn đối tượng lấy nét (*Focus Target*) hoặc điều chỉnh **Focus Distance** và **f-stop** [2, 10].
  2. **Kỹ thuật Rack Focus (Chuyển nét)**: Thêm đối tượng `Empty`, gán Empty làm mục tiêu *Depth of Field Target* của Camera, sau đó đặt keyframe vị trí của Empty để di chuyển vùng lấy nét giữa các vật thể trong cảnh [2, 8].
  3. **Tạo hiệu ứng Dolly Zoom**: Đặt keyframe di chuyển vị trí camera tiến/lùi (nhấn phím `T` trên timeline và chọn `Linear`), đồng thời đặt keyframe cho thông số `Focal Length` của camera để khớp kích thước vật thể giữa frame đầu và frame cuối [3].
  4. **Xoay quanh vật thể (Empty Camera Control)**: Tạo Empty tại vị trí vật thể, chọn Camera rồi chọn Empty, nhấn `Ctrl + P` để gán parent. Sau đó chọn Empty và nhấn `R` hai lần để xoay camera dạng trackball quanh vật thể [11].
  5. **Tạo độ rung tự nhiên (Camera Shakeify)**: Bật add-on `Camera Shakeify`, chọn preset rung (như `Investigation`) và chỉnh hai thông số `Influence` và `Scale` ở mức vừa phải [12].

* **Hướng dẫn thiết lập qua Python (`bpy`)**:
  *(Lưu ý: Đoạn mã `bpy` dưới đây được tổng hợp theo các thuộc tính cấu hình camera đã mô tả trong tài liệu)*:

  ```python
  import bpy

  # 1. Tạo hoặc lấy đối tượng Camera trong cảnh
  cam_data = bpy.data.cameras.new(name="Cinematic_Camera")
  cam_obj = bpy.data.objects.new(name="Cinematic_Camera", object_data=cam_data)
  bpy.context.collection.objects.link(cam_obj)
  bpy.context.scene.camera = cam_obj

  # 2. Thiết lập tiêu cự (Focal Length) - ví dụ 35mm
  cam_data.lens = 35  # Đơn vị: mm

  # 3. Kích hoạt Depth of Field & Khẩu độ (f-stop)
  cam_data.dof.use_dof = True
  cam_data.dof.aperture_fstop = 2.8  # Khẩu độ f/2.8

  # 4. Cấu hình hình dạng Boke (Số lá khẩu)
  cam_data.dof.aperture_blades = 6  # 6 lá khẩu tạo Boke hình lục giác
  ```

---

**Lỗi thường gặp & Cách kiểm tra**

1. **Để Color Management ở mức Standard**: Làm hẹp dải sáng xuống 8 stops khiến vùng sáng dễ bị cháy hoặc vùng tối mất chi tiết. **Cách kiểm tra:** Vào bảng *Render Properties > Color Management* và đảm bảo đặt thành `Filmic` (đạt 25 stops) [6].
2. **Lạm dụng hiệu ứng rung camera (Camera Shake)**: Đặt độ rung quá mạnh hoặc áp dụng cho cả các góc quay tĩnh trên chân đế (*tripod*) làm mất tính tự nhiên. **Cách kiểm tra:** Giữ chỉ số `Influence` ở mức tinh tế (`subtle`) [12].
3. **Đặt góc quay & chiếu sáng phẳng trực diện (Flat View/Lighting)**: Đặt camera và nguồn sáng đối diện thẳng mặt vật thể làm hình ảnh bị phẳng và mất chiều sâu. **Cách kiểm tra:** Đặt nguồn sáng và góc quay lệch hướng (*outside lighting*) để tạo mảng đổ bóng tôn lên hình khối 3D [4, 13, 14].
4. **Không chọn nội suy Linear khi làm Dolly Zoom**: Để mặc định dạng nội suy cong (*Bezier*) khiến tốc độ di chuyển và tốc độ zoom tiêu cự không lệch nhịp, làm hỏng hiệu ứng biến dạng liên tục. **Cách kiểm tra:** Chọn các keyframe trên timeline, nhấn phím `T` và chọn `Linear` [3].

🎬 Bạn có muốn tôi viết một script Python hoàn chỉnh để tự động hóa việc tạo keyframe cho hiệu ứng Dolly Zoom hoặc Rack Focus trong Blender không?
