# [C07] Chuyển động máy quay (Camera Movement): Dolly, Truck, Pan, Tilt, Crane và chống cảm giác CGI giả tạo

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

1. **Tóm tắt Bản chất (2-3 câu)**
Việc làm chủ chuyển động camera trong Blender giúp mô phỏng chính xác cơ chế ống kính và thân máy ảnh thực tế, định hướng sự chú ý của người xem và nâng tầm tính điện ảnh (Cinematography) cho cảnh quay 3D [1, 2]. Bằng cách kết hợp điều khiển camera qua vật thể trung gian (Empty), tùy chỉnh đường cong nội suy keyframe và bổ sung độ rung cầm tay (Handheld Shake) tinh tế, bạn có thể tạo ra những cú bấm máy mượt mà, chân thực và mang đậm ngôn ngữ kể chuyện [3-5].

---

2. **Nguyên lý & Thông số Chuẩn**

*   **Dolly (Tiến/Lùi thật) vs. Zoom (Thay đổi tiêu cự):**
    *   **Dolly (Camera Movement):** Camera di chuyển vật lý thật trong không gian 3D, làm thay đổi vị trí điểm nhìn và mối tương quan không gian, chiều sâu giữa tiền cảnh và hậu cảnh [2, 3].
    *   **Zoom (Focal Length Change):** Camera đứng yên tại chỗ, chỉ thay đổi tiêu cự của ống kính (Focal Length) làm thu hẹp hoặc mở rộng góc nhìn (Field of View) [1, 3].
    *   **Dolly Zoom (Vertigo Effect):** Được Alfred Hitchcock khởi xướng từ thập niên 1940 [2, 3]. Kỹ thuật này kết hợp việc lùi camera ra xa (Dolly) đồng thời tăng tiêu cự ống kính (Zoom In) — hoặc ngược lại — sao cho kích thước vật thể chính không đổi [3]. Kết quả tạo ra sự biến dạng góc nhìn liên tục (continuous perspective distortion), gợi cảm giác choáng ngợp hoặc phi thực tế [2, 3].
    *   **Khi nào dùng Dolly thay vì Zoom:** Dùng **Dolly** khi muốn người xem cảm nhận được sự di chuyển thực sự trong môi trường 3D; dùng **Zoom** khi chỉ muốn tập trung thu phóng khung hình từ một vị trí cố định [1, 3].

*   **Thông số cấu hình chuẩn trong Blender:**
    *   **Tốc độ khung hình (FPS) & Frame Range:** Cài đặt trong mục *Output Properties* (mặc định chuẩn điện ảnh là **24 FPS**, xác định tổng số frame dựa trên số giây cần diễn hoạt) [6].
    *   **Quản lý màu sắc (Color Management):** Luôn đảm bảo thiết lập ở chế độ **Filmic** (cung cấp dải động dynamic range lên tới **25 stops**), không nên dùng `Standard` vì bị hạn chế ở **8 stops** [7].
    *   **Motion Blur & Shutter Speed:** Bật tính năng *Motion Blur* trong cài đặt Render [8]. Thông số *Shutter* mô phỏng tốc độ màn cửa của máy ảnh thực tế (giá trị *Shutter* nhỏ tương ứng tốc độ màn cửa nhanh, giá trị lớn cho hiệu ứng nhòe chuyển động nhiều hơn) [7, 8].
    *   **Nội suy Keyframe (Linear vs. Bezier):** Nhấn phím **`T`** trong Timeline hoặc Graph Editor để chọn kiểu nội suy [3]. Chế độ `Linear` giữ vận tốc di chuyển đều, trong khi `Bezier` tạo độ gia tốc mượt mà.
    *   **Độ rung cầm tay (Handheld Noise):** Sử dụng Add-on miễn phí **Camera Shakeify** (do Ian Hubert và Nathan Vegdahl thiết kế) [5] hoặc thêm **Noise Modifier** trong Graph Editor [9]. Chọn preset `Investigation`, sau đó hạ thấp thông số **Influence** và **Scale** để độ rung tự nhiên, không nên làm quá đà [5].

---

3. **Cách áp dụng trong Blender (Thao tác & Ghi chú về Code)**

*   **Điều khiển Camera bằng Empty (Empty Camera Control):**
    1. Nhấn `Shift + A` tạo một vật thể `Empty` đặt tại vị trí tâm của vật thể cần quay [4].
    2. Đặt camera hướng trực diện vào vật thể [3, 4].
    3. Chọn Camera, sau đó giữ `Shift` chọn `Empty`, nhấn tổ hợp phím **`Ctrl + P`** để gắn quan hệ cha-con (Parent) [4].
    4. Chọn `Empty` và nhấn phím **`R` hai lần** để bật chế độ xoay Trackball, giúp xoay camera quanh mục tiêu một cách mượt mà [4].

*   **Thiết lập Cú bấm máy Dolly Zoom:**
    1. Đặt keyframe vị trí lùi xa cho Camera [3].
    2. Chọn các keyframe vị trí trong Timeline, nhấn phím **`T`** và chọn **`Linear`** để camera di chuyển với vận tốc đều [3].
    3. Đặt keyframe tiêu cự (*Focal Length*) ở khung hình đầu và khung hình cuối sao cho kích thước vật thể chủ thể trùng khớp nhau [3].

*   **Thiết lập Chuyển nét (Rack Focus) & Độ sâu trường ảnh:**
    1. Bật tính năng *Depth of Field* trong thuộc tính Camera [2, 10].
    2. Gán ô *Focus Target* trỏ đến vật thể `Empty` [2].
    3. Đặt keyframe di chuyển vị trí cho `Empty` để điều khiển điểm lấy nét dịch chuyển giữa tiền cảnh và hậu cảnh [2].

*   **Lưu ý về Code Python `bpy` & Ràng buộc nâng cao:**
    *   *Tài liệu trong sổ tập trung hướng dẫn quy trình thao tác trực tiếp trên giao diện Blender (UI Shortcuts) và sử dụng add-on. Tài liệu hiện tại không cung cấp đoạn mã Python `bpy` cụ thể hay hướng dẫn chi tiết về các ràng buộc Follow Path/Track To constraint.*

---

4. **Lỗi thường gặp & Cách kiểm tra**

*   **Quên Reset Transform trước khi Keyframe:** Không nhấn **`Ctrl + A` -> `Rotation & Scale`** trước khi làm animation, dẫn đến việc các thông số xoay và tỉ lệ bị tính toán sai lệch [11].
*   **Để Color Management ở mức Standard:** Khiến cảnh quay dễ bị cháy sáng hoặc mất chi tiết vùng tối do dải động quá thấp (8 stops so với 25 stops của Filmic) [7].
*   **Lạm dụng hiệu ứng Rung camera (Overdone Camera Shake):** Để thông số *Influence* hoặc *Scale* quá cao khiến khung hình giật cục gây khó chịu cho người xem, hoặc gán độ rung cho những cảnh vốn cần đặt trên chân đế cố định (Tripod) [5].
*   **Không đồng bộ tốc độ trong Dolly Zoom:** Đặt đường cong nội suy lệch nhau giữa vị trí camera và tiêu cự ống kính, làm mất hiệu ứng biến dạng góc nhìn liên tục [3].

🎬 *Bạn có muốn thử thiết lập một kịch bản chiếu sáng điện ảnh (Cinematic Lighting) với 1 nguồn sáng diện tích (Area Light) để tôn lên hình khối của vật thể trong cảnh này không?*
