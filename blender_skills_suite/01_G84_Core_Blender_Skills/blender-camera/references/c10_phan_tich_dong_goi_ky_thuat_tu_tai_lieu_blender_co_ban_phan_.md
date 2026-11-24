# [C10] Phân tích & Đóng gói kỹ thuật từ tài liệu: Blender Cơ Bản - Phần 13: Animation - Chuyển động cơ bản với Blender ( Blender Tutorial )

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Chuyên sâu theo Nguồn (Level 4)
- **Ngày trích xuất:** 2026-11-06

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
Animation cơ bản trong Blender là quá trình thiết lập các thông số khung hình (FPS, Frame Range) và ghi lại trạng thái biến đổi (vị trí, xoay, tỷ lệ) của vật thể theo thời gian thông qua các **keyframe** [1-3]. Kỹ thuật này giúp chuyển đổi các đối tượng tĩnh thành chuyển động mượt mà nhờ việc phần mềm tự động tính toán khoảng chuyển tiếp giữa các mốc keyframe [3]. Việc nắm vững quy trình từ chuẩn hóa vật thể, đặt keyframe đến tinh chỉnh thời gian xuất hiện trong **Dopesheet Editor** là nền tảng cốt lõi để tạo nên các đoạn hoạt hình chỉn chu [4-6].

---

### 2. **Nguyên lý & Thông số Chuẩn**
* **Tốc độ khung hình (Frame Rate / FPS):** Mặc định thiết lập là **24 FPS** (1 giây hoạt ảnh chứa 24 khung hình) [2].
* **Phạm vi khung hình (Frame Range):**
  * **Frame Start:** Khởi đầu ở frame **1** [2].
  * **Frame End:** Tính theo công thức \\(\text{Số giây} \times \text{FPS}\\). Ví dụ: Video 10 giây cần \\(10 \times 24 = \mathbf{240\text{ frame}}\\) [2]; video 5 giây cần \\(5 \times 24 = \mathbf{120\text{ frame}}\\) [7].
* **Nguyên lý Keyframe (Quy tắc "Vé xe buýt"):** Để tạo ra bất kỳ một chuyển động nào từ điểm A đến điểm B, bắt buộc phải có **tối thiểu 2 keyframe** ghi nhận thông tin trạng thái và mốc thời gian tại hai điểm đó [3].
* **Chuẩn hóa biến đổi (Baseline Transforms):** Trước khi tạo keyframe, tọa độ xoay (**Rotation**) của đối tượng phải đưa về **(0, 0, 0)** và tỷ lệ (**Scale**) phải đưa về **(1, 1, 1)** [4].
* **Quy tắc nhận biết màu sắc thuộc tính:**
  * **Màu vàng đậm (Dark Yellow/Orange):** Thuộc tính đã được chèn keyframe thành công tại khung hình hiện tại [8].
  * **Màu xanh lá cây (Green):** Thuộc tính đã bị thay đổi giá trị ở khung hình mới nhưng **chưa được chèn keyframe** lưu lại [8].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### **Thao tác thủ công trên giao diện Blender:**
1. **Cấu hình thuộc tính đầu ra (Output Properties):**
   * Vào thẻ **Output Properties**, đặt **Frame Rate** là `24 fps`, **Frame Start** là `1`, **Frame End** là `240` (hoặc `120`) [2, 7].
2. **Đặt lại tâm đối tượng (Set Origin):**
   * Chuyển sang **Edit Mode** (`Tab`), chọn các điểm/mặt ở đáy đối tượng [9].
   * Nhấn `Shift + S` \\(\rightarrow\\) Chọn **Cursor to Selected** [9].
   * Trở lại **Object Mode** \\(\rightarrow\\) Nhấp chuột phải chọn **Set Origin** \\(\rightarrow\\) **Set Origin to 3D Cursor** [9].
3. **Reset thông số gốc (Apply Rotation & Scale):**
   * Tại **Object Mode**, chọn tất cả đối tượng, nhấn `Ctrl + A` \\(\rightarrow\\) Chọn **Rotation & Scale** [4].
4. **Tạo và gắn Keyframe:**
   * Di chuyển đường chỉ thời gian (màu xanh) trên thanh **Timeline** đến khung hình mong muốn (dùng phím `Spacebar` để Play/Pause) [2, 4].
   * Chọn đối tượng, nhấn phím `I` trong viewport để chọn kiểu keyframe (**Rotation**, **Scale**, hoặc **Location & Rotation & Scale**) [8]. Hoặc di chuột trực tiếp lên thuộc tính cần lưu (như trục Z Rotation) và nhấn `I` [10].
5. **Sắp xếp nhịp điệu chuyển động (Staggering) với Dopesheet Editor:**
   * Mở cửa sổ **Dopesheet Editor** để quản lý keyframe của toàn bộ các đối tượng trong cảnh [5, 11].
   * Chọn các mốc keyframe của từng vật thể (như lá chanh, lát chanh) và nhấn phím `G` để kéo trượt sang trái/phải trên Timeline, giúp các chi tiết xuất hiện nối tiếp nhau thay vì xuất hiện cùng một lúc [6].
   * *(Lưu ý: Có thể mở thêm Graph Editor để tinh chỉnh đường cong chuyển động mượt mà hơn [12]).*

#### **Mở rộng bằng Python `bpy` (Đồng bộ theo thông số tài liệu):**
*(Lưu ý: Tài liệu video gốc tập trung hoàn toàn vào thao tác thủ công trên giao diện người dùng và phím tắt, không đề cập đến mã Python `bpy` hay Nodes [1-23]. Đoạn mã dưới đây minh họa cách tự động hóa đúng các thông số trong bài học):*

```python
import bpy

# 1. Thiết lập Frame Rate và Frame Range (24 FPS, Start 1, End 240)
scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 240

# 2. Chọn đối tượng active và Apply Rotation & Scale
obj = bpy.context.active_object
if obj:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    
    # Chuẩn hóa Rotation về 0,0,0 và Scale về 1,1,1
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    
    # 3. Tạo Keyframe Scale = 0 tại Frame 1
    scene.frame_set(1)
    obj.scale = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path="scale", frame=1)
    
    # 4. Tạo Keyframe Scale = 1 tại Frame 44
    scene.frame_set(44)
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert(data_path="scale", frame=44)
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**
* **Quên Apply Rotation & Scale (`Ctrl + A`):** Nếu không đưa Rotation về 0 và Scale về 1 trước khi làm animation, các chuyển động xoay hoặc phóng to/thu nhỏ sau đó sẽ bị bóp méo hoặc hoạt động sai kích thước [4].
* **Quên dời tâm (Origin Point) về vị trí mong muốn:** Ví dụ khi muốn vật thể phóng to/xoay từ gốc đáy lên, nếu không dời Origin về đáy, vật thể sẽ phóng to hoặc xoay quanh tâm giữa làm lệch bố cục [9].
* **Chỉnh sửa thông số nhưng quên nhấn phím `I`:** Khung thuộc tính hiển thị màu xanh lá cây báo hiệu giá trị đã đổi nhưng chưa chèn keyframe; nếu di chuyển playhead sang frame khác, thay đổi đó sẽ bị mất [8].
* **Đặt keyframe sai chiều/xoay ngược:** Nhập sai dấu của góc xoay (như âm/dương) khiến vật thể xoay ngược hướng mong muốn [18].
* **Cảnh quay bị đơ do xuất hiện đồng loạt:** Đặt keyframe xuất hiện cho tất cả vật thể ở cùng frame 1. Cần dùng **Dopesheet Editor** và phím `G` để dịch chuyển keyframe, tạo sự xuất hiện so le tự nhiên [6].

🎬 Bạn có muốn tìm hiểu thêm về cách hiệu chỉnh đường cong chuyển động trong **Graph Editor** hoặc cách kết hợp ống kính camera để tạo góc quay cinematic cho cảnh này không?
