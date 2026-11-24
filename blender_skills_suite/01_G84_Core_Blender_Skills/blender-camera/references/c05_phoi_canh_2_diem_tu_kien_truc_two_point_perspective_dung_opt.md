# [C05] Phối cảnh 2 điểm tụ kiến trúc (Two-Point Perspective): Dùng Optical Lens Shift (shift_x, shift_y) trong hẻm hẹp

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

Tài liệu trong sổ tay tập trung vào thuộc tính cơ bản của camera (tiêu cự, dải động Filmic), bố cục góc quay công trình (tiêu cự 30mm–35mm, Quy tắc 1/3) và kỹ thuật điều khiển camera (Parenting camera vào Empty) [1-5]. Tuy nhiên, **kỹ thuật cụ thể về việc giữ góc Pitch = 90 độ kết hợp với dịch chuyển trục quang học (Shift X, Shift Y)** để duy trì phối cảnh 2 điểm tụ (Two-Point Perspective) **không có trong các nguồn tài liệu hiện tại của sổ tay**. 

Dưới đây là phần giải thích và các thông số được trích xuất từ tài liệu hiện có:

### 1. Tóm tắt Bản chất (2-3 câu)
Trong Blender, việc kiểm soát camera kết hợp giữa thông số ống kính vật lý (tiêu cự, field of view) và vị trí không gian để định hình bố cục kiến trúc và chiều sâu cho cảnh quay [1, 3]. Việc điều chỉnh camera đúng cách giúp giữ vững cấu trúc khung hình, hạn chế méo hình học và hướng sự chú ý của người xem vào đối tượng chính [1, 6].

### 2. Nguyên lý & Thông số Chuẩn (Trích xuất từ tài liệu)
* **Tiêu cự chuẩn (Focal Length):** Khi thiết lập góc quay cho công trình kiến trúc hoặc ngoại cảnh lớn, tài liệu hướng dẫn sử dụng ống kính góc rộng với tiêu cự **30mm đến 35mm** và lùi camera ra xa để bao quát toàn cảnh [1].
* **Bố cục khung hình (Rule of Thirds):** Đặt công trình/tòa nhà chính theo quy tắc một phần ba (lệch sang bên trái hoặc bên phải khung hình) thay vì đặt chính giữa để tạo khoảng trống cân bằng cho khung hình [2].
* **Quản lý dải động (Filmic Color Management):** Thiết lập **Color Management** sang **Filmic** (cung cấp dải động 25 stops) thay vì **Standard** (chỉ có 8 stops) để giữ lại chi tiết vùng sáng/tối trên mảng tường kiến trúc [4].
* **Điều khiển góc quay (Empty Camera Parenting):** Để xoay camera linh hoạt xung quanh tòa nhà mà không bị chệch góc nhìn, đặt một vật thể rỗng (Empty) tại tâm công trình và gán liên kết cha-con (`Ctrl + P`) từ Camera sang Empty [5].

### 3. Cách áp dụng trong Blender & Mã Python `bpy`
* **Thao tác thiết lập theo tài liệu:**
  1. Thêm camera mới bằng tổ hợp phím `Shift + A` -> **Camera** [1].
  2. Đặt góc nhìn hiện tại thành góc nhìn camera bằng `Ctrl + Alt + Numpad 0` [1].
  3. Chọn Camera, truy cập bảng *Camera Properties* và chỉnh tiêu cự **Focal Length = 30mm** hoặc **35mm** [1, 3].
  4. Thêm một vật thể *Empty* ở tâm công trình, chọn Camera rồi chọn Empty và nhấn `Ctrl + P` (*Set Parent to Object*) để điều khiển ống kính xoay quanh công trình [5].
* **Về mã Python `bpy` và thông số Shift X/Y:**
  * Các nguồn tài liệu hiện tại **chưa cung cấp** đoạn mã Python `bpy` cũng như các thông số điều chỉnh thuộc tính `shift_x`, `shift_y` hoặc cố định trục xoay Pitch (Rotation X = 90°).

### 4. Lỗi thường gặp & Cách kiểm tra
* **Quên chuyển sang Filmic Color Management:** Khiến khung hình bị cháy sáng ở các mảng tường do dải động bị giới hạn ở 8 stops thay vì 25 stops [4].
* **Đặt camera quá gần hoặc góc nhìn bị lún:** Dễ làm cắt phạm vào chân tường/nền môi trường khiến công trình bị hẫng [1, 7].
* **Chưa áp dụng Apply Rotation & Scale:** Quên nhấn `Ctrl + A` -> **Rotation & Scale** cho các vật thể trước khi căn chỉnh hoặc làm animation khiến các thông số góc xoay và tỉ lệ bị sai lệch [8].

---

📷 **Gợi ý tiếp theo:** Bạn có muốn tôi thực hiện **nghiên cứu trên Web** để tìm kiếm cú pháp Python `bpy` chính xác cho `shift_x`/`shift_y` và quy trình từng bước thiết lập Two-Point Perspective (Pitch = 90°) trong Blender để bổ sung vào câu trả lời không?
