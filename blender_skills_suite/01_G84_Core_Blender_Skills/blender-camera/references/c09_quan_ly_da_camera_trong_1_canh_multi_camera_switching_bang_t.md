# [C09] Quản lý đa Camera trong 1 cảnh (Multi-Camera Switching bằng Timeline Markers & Bind Camera to Markers)

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

Dưới đây là hướng dẫn chi tiết theo các nội dung được tổng hợp từ tài liệu trong sổ của bạn, đồng thời minh định rõ những phần thông tin mà tài liệu chưa đề cập.

---

### 1. **Tóm tắt Bản chất**
Trong quy trình làm phim và diễn hoạt 3D trên Blender, việc phối hợp giữa **vật thể 3D, camera và nguồn sáng** là ba yếu tố nền tảng để tạo ra hình ảnh hoặc video xuất bản hoàn chỉnh [1, 2]. Thiết lập nhiều góc camera và kiểm soát góc quay giúp định hình bố cục, điều hướng sự chú ý của người xem thông qua tiêu cự (focal length), độ sâu trường ảnh (depth of field) [3] và sự nối tiếp chuyển động (continuation of motion) giữa các góc cắt [4]. 

*Lưu ý về nguồn tài liệu:* Các tài liệu hiện có trong sổ chưa có nội dung hướng dẫn về tính năng **Timeline Markers (`Bind Camera to Markers`)** để tự động chuyển góc quay trên Timeline, cũng như chưa có quy trình phân chia cụ thể 4 góc máy (*Master Shot, Close-up A/B, Insert Shot*) hay đoạn mã Python `bpy` tương ứng.

---

### 2. **Nguyên lý & Thông số Chuẩn (Trích xuất từ tài liệu)**

* **Kích thước & Độ phân giải khung hình:** Kích thước xuất video chuẩn được thiết lập ở mức **1920×1080** pixels [5].
* **Tốc độ khung hình (FPS) & Chiều dài Frame:** Tốc độ khung hình chuẩn mặc định là **24 FPS** [5-7]. Thông số này được cài đặt trong mục **Output Properties** chứ không nằm trong thuộc tính riêng của Camera [7]. Chiều dài phân cảnh tính bằng công thức `Số giây × FPS` (ví dụ: 10 giây tương ứng 240 frames với Frame Start = 1, Frame End = 240 [6]; hoặc 5 giây tương ứng 120 frames [8]).
* **Tiêu cự (Focal Length):** Tiêu cự quyết định góc nhìn (Field of View); đối với các góc quay toàn cảnh hoặc không gian rộng, tiêu cự góc rộng thường dùng là **30mm** hoặc **35mm** [9, 10].
* **Dải tương phản động (Dynamic Range):** Thiết lập **Filmic Color Management** cung cấp dải tương phản tới **25 stops**, vượt trội hơn hẳn so với dải màu Standard chuẩn (chỉ có 8 stops) [7].
* **Quy tắc chuyển động giữa các góc cắt (Continuation of Motion):** Giữ hướng chuyển động của camera/vật thể đồng nhất qua 2–3 góc cắt liên tiếp để tạo sự mượt mà cho nhịp phim, hoặc sử dụng chuyển động ngược hướng (opposed motion) để tạo sự tương phản mạnh thu hút sự chú ý [4, 11].
* **Độ sâu trường ảnh & Hình dạng Bokeh:** Số lá khẩu (aperture blades) điều chỉnh hình dạng vết mờ Bokeh: mặc định `= 0` (tròn), `3` (tam giác), `4` (hình vuông), `5` (ngũ giác), `6` (lục giác) [12].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Hạn chế về Code Python `bpy`)**

#### **A. Thao tác thiết lập Camera & Điều khiển góc máy (Có trong tài liệu)**
1. **Tạo Camera & Canh góc nhìn:** 
   * Nhấn `Shift + A` > **Camera** để tạo máy quay mới [13].
   * Để đưa camera về chính xác vị trí góc nhìn hiện tại trong 3D Viewport, chọn `View` > `Align View` > `Align Active Camera to View` (hoặc phím tắt `Ctrl + Alt + Numpad 0`) [9, 13]. 
   * Di chuyển camera lùi hoặc tiến theo trục Z cục bộ bằng cách nhấn `G` rồi nhấn `Z` hai lần (`G` > `Z` > `Z`) [13, 14].
2. **Điều khiển Camera xoay quanh mục tiêu (Empty Camera Control):** 
   * Đặt một vật thể **Empty** tại vị trí trung tâm của đối tượng cần quay [15].
   * Chọn Camera, sau đó chọn Empty và nhấn `Ctrl + P` để gắn quan hệ cha-con (Parenting) [15].
   * Chọn Empty và nhấn `R` hai lần (`R` > `R`) để bật chế độ xoay tự do (Trackball rotation), giúp camera xoay quanh mục tiêu mượt mà [4].
3. **Thiết lập Rack Focus (Chuyển tiêu điểm lấy nét):**
   * Bật **Depth of Field** trong bảng thuộc tính Camera [12].
   * Chọn mục tiêu lấy nét (*Focus Distance / Target*) là vật thể Empty và gắn keyframe vị trí cho Empty đó để chuyển nét từ điểm này sang điểm khác [3, 16].
4. **Cài đặt Xuất bản (Render Output):**
   * Trong bảng **Output Properties**, đặt độ phân giải `1920x1080`, tốc độ `24 FPS`, định dạng xuất video `FFmpeg video` [5].
   * Nhấn `F12` để render ảnh đơn hoặc `Ctrl + F12` để render toàn bộ chuỗi chuyển động (Animation) [2, 5, 17].

#### **B. Giới hạn thông tin về Timeline Markers & Python Script**
Tài liệu hiện tại **chưa có thông tin** hướng dẫn thao tác `Bind Camera to Markers` (gắn camera vào Marker trên Timeline để tự động cắt cảnh) cũng như mã nguồn Python `bpy` cho tính năng này. 

---

### 4. **Lỗi thường gặp & Cách kiểm tra (Trích xuất từ tài liệu)**

* **Quên Apply Rotation & Scale trước khi tạo chuyển động:** Nếu không nhấn `Ctrl + A` > **Rotation & Scale** ở Object Mode trước khi keyframe, thông số quay và phóng to/thu nhỏ của vật thể sẽ bị biến dạng hoặc hoạt động sai lệch khi diễn hoạt [18].
* **Tìm cài đặt FPS sai vị trí:** Cố gắng tìm tùy chọn FPS trong thuộc tính của Camera thay vì bảng *Output Properties* [7].
* **Đặt ánh sáng trực diện từ góc nhìn Camera:** Chiếu sáng thẳng từ hướng camera làm hình ảnh bị phẳng (flat). Nên đặt nguồn sáng ở phía sau hoặc bên hông đối tượng để tạo bóng đổ (shadows), giúp bộc lộ rõ hình khối chi tiết của vật thể [19-25].
* **Mất thời gian vào chi tiết nhỏ không cần thiết:** Tốn quá nhiều thời gian làm chi tiết vi mô mà người xem không bao giờ nhận ra; thay vào đó nên ưu tiên hoàn thiện bố cục tổng thể, ánh sáng và chất liệu trước [26, 27].
* **Thiếu Keyframe điểm bắt đầu và kết thúc:** Để tạo bất kỳ chuyển động nào đều cần tối thiểu 2 keyframe (điểm đi và điểm đến) bằng cách nhấn phím `I` trên Timeline [28, 29].

---

🎬 Bạn có muốn tôi tìm kiếm thêm trên web về cú pháp lệnh `Bind Camera to Markers` và đoạn mã Python `bpy` tự động hóa quy trình này để bổ sung vào tài liệu không?
