# [C03] Bố cục khung hình (Rule of Thirds, Leading Lines, Frame within a Frame, Headroom & Lookroom)

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

### 1. Tóm tắt Bản chất
Bố cục khung hình trong điện ảnh và Blender là nghệ thuật sắp xếp chủ thể, ánh sáng và camera nhằm tạo sự cân bằng, độ sâu không gian và thu hút sự chú ý của người xem [1, 2]. Việc nắm vững các quy tắc bố cục giúp định hướng ánh mắt khán giả, làm nổi bật đường nét hình khối 3D và truyền tải câu chuyện của cảnh quay một cách chuyên nghiệp [1, 3, 4].

---

### 2. Nguyên lý & Thông số Chuẩn (Trích xuất từ tài liệu)

* **Quy tắc 1/3 (Rule of Thirds):** Bố trí chủ thể chính (ví dụ: mô hình ngôi nhà) nằm lệch về phía bên trái hoặc bên phải khung hình thay vì đặt chính giữa [1]. Việc này chừa không gian phía đối diện cho các yếu tố phụ trợ, tạo sự cân bằng tự nhiên cho cảnh quay [1].
* **Thông số tiêu cự camera (Focal Length):** Tài liệu hướng dẫn sử dụng các tiêu cự góc rộng từ **30mm đến 35mm** cho các cảnh môi trường quy mô lớn để mở rộng góc nhìn và tăng chiều sâu không gian [5].
* **Cấu trúc lớp độ sâu (Depth Layers):** Bố cục điện ảnh đạt hiệu quả cao khi kết hợp đầy đủ ba tầng không gian:
  * **Tiền cảnh (Foreground / FG):** Cây cối, thuyền hoặc các mảng lá cây nằm sát camera [6-8].
  * **Trung cảnh (Midground):** Chủ thể chính của cảnh quay [1, 5].
  * **Hậu cảnh (Background):** Cây cối phía xa, dãy núi và lớp sương mù thể hiện khoảng cách không gian [9, 10].
* **Nguyên lý ánh sáng tạo khối (Outside Lighting):** Đặt nguồn sáng ở vị trí phía sau hoặc phía trên chủ thể thay vì chiếu thẳng từ góc nhìn camera, giúp tận dụng bóng đổ mềm để tôn lên đường nét và hình khối 3D [11-14].

> **Lưu ý về dữ liệu trong sổ:** Các quy tắc như **Đường dẫn (Leading Lines)**, **Khung trong khung (Frame within Frame)**, và **Khoảng thở (Lookroom / Headroom)** hiện không có thông tin chi tiết trong các tài liệu được cung cấp.

---

### 3. Cách áp dụng trong Blender

* **Thao tác căn chỉnh góc máy & Bố cục:**
  1. **Căn camera theo góc nhìn hiện tại:** Chọn góc quan sát ưng ý trong Viewport, sau đó ấn tổ hợp phím **`Ctrl + Alt + Numpad 0`** (hoặc `Ctrl + Alt + 0`) để đưa camera chính về đúng góc nhìn đó [5].
  2. **Chia màn hình làm việc (Split Viewport):** Chia giao diện làm hai cửa sổ; một bên giữ góc nhìn Camera (`Camera View`) để kiểm tra bố cục liên tục, bên còn lại thao tác sắp xếp vật thể trong không gian 3D [15].
  3. **Cài đặt tiêu cự:** Chọn đối tượng Camera, chuyển tới bảng thuộc tính Camera (`Camera Properties`) và chỉnh thông số **Focal Length** thành `30mm` hoặc `35mm` [5].
  4. **Điều khiển Camera linh hoạt bằng Empty:** Tạo một vật thể Rỗng (`Shift + A` \\(\rightarrow\\) `Empty`), chọn Camera rồi chọn Empty và nhấn **`Ctrl + P`** để gán cha-con [16, 17]. Khi chọn Empty và nhấn phím **`R` hai lần** (Trackball Rotation), bạn có thể xoay camera quanh chủ thể mượt mà để tìm góc máy đẹp nhất [17].

> **Lưu ý về Composition Guides & Code Python `bpy`:** Hướng dẫn thao tác bật tính năng `Composition Guides` trong thuộc tính Viewport Display của Camera cũng như đoạn mã lệnh Python (`bpy`) để bật tự động hiện chưa được đề cập trong tài liệu của bạn.

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Đặt chủ thể ở chính giữa khung hình một cách thụ động:** Làm cho bức ảnh bị cứng và thiếu sự linh hoạt [1]. *Cách khắc phục:* Áp dụng Quy tắc 1/3 để đặt chủ thể lệch sang 1/3 bên trái hoặc bên phải khung hình [1].
* **Để lộ viền cắt của tiền cảnh (FG Cuts):** Các vật thể tiền cảnh bị cắt mép làm lộ sơ hở kỹ xảo và giảm tính chân thực [7, 15]. *Cách kiểm tra:* Di chuyển camera tiến về phía trước một chút hoặc bổ sung chi tiết che chắn viền khung hình [7, 15].
* **Chiếu sáng trực diện từ vị trí camera:** Làm cảnh quay bị phẳng lì và mất chi tiết hình khối [11-13]. *Cách khắc phục:* Đặt nguồn sáng lệch góc hoặc phía sau chủ thể để tận dụng bóng đổ định hình [12-14].
* **Đứt gãy nhịp chuyển động giữa các cảnh:** Mất đi sự nối tiếp hướng chuyển động (Continuation of motion) khi đổi góc máy [17]. *Cách khắc phục:* Đảm bảo hướng chuyển động của camera hoặc chủ thể giữa các cảnh quay được duy trì liên tục [17].

---

💡 *Tài liệu hiện tại chưa bao gồm các định nghĩa về Đường dẫn, Khung trong khung, Lookroom/Headroom và đoạn mã Python `bpy` bật Composition Guides. Bạn có muốn tôi thực hiện tìm kiếm trên mạng về các chủ đề này không?*
