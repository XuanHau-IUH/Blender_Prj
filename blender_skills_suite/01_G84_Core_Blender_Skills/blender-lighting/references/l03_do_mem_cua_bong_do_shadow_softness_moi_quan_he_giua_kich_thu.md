# [L03] Độ mềm của bóng đổ (Shadow Softness): Mối quan hệ giữa kích thước nguồn sáng (Radius/Size) và khoảng cách

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
Trong Blender, độ sắc nét hay mềm mại của bóng đổ (**Hard vs Soft Shadows**) không phụ thuộc vào công suất hay độ sáng của đèn mà được quyết định bởi **kích thước vật lý tương đối của nguồn sáng so with chủ thể** và **khoảng cách giữa chúng** [1, 2]. Việc nắm vững nguyên lý này giúp kiểm soát chính xác vùng chuyển bóng mờ (penumbra) và hiện tượng tiếp xúc cứng (contact hardening), tạo chiều sâu không gian và tính chân thực vật lý cho khung hình trong cả hai render engine Cycles và EEVEE Next [2-4].

---

### 2. **Nguyên lý & Thông số Chuẩn**

* **Nguyên lý kích thước nguồn sáng (Emitter Size):**
  * **Nguồn sáng nhỏ / Điểm mút (Point-like emitter):** Tạo ra bóng đổ sắc nét, ranh giới bóng cứng (Hard Shadows) [4].
  * **Nguồn sáng lớn (Large emitter / Softbox):** Tạo ra bóng đổ mềm mại (Soft Shadows) với vùng mờ xung quanh bóng (penumbra) rộng [4].
  * **Hiện tượng Contact Hardening:** Bóng đổ luôn đạt độ sắc nét nhất tại điểm tiếp xúc trực tiếp giữa chủ thể và bề mặt, sau đó mờ dần ra khi khoảng cách xa dần [4, 5].

* **Ảnh hưởng của Khoảng cách & Định luật Nghịch đảo Bình phương (Inverse Square Law):**
  * **Độ suy giảm ánh sáng:** Cường độ chiếu sáng \\(E\\) tỷ lệ nghịch với bình phương khoảng cách \\(d\\) (\\(E = \frac{P}{4\pi d^2}\\)) [1].
  * **Khoảng cách làm thay đổi góc chiếu tương đối:** Đưa đèn lại gần chủ thể sẽ làm tăng góc chiếu tương đối (angular size) của nguồn sáng, làm vùng mép bóng mờ hơn [1, 4]. Ngược lại, lùi nguồn sáng ra xa sẽ làm kích thước tương đối của đèn "nhỏ đi", làm bóng đổ trở nên sắc nét hơn [4, 6].
  * **Tỷ lệ không gian:** Để tính toán suy giảm và bóng đổ chính xác theo vật lý, cảnh trong Blender cần duy trì đúng tỷ lệ thực (\\(1\text{ unit} = 1\text{ meter}\\)) [1].

* **Các thông số điều chỉnh độ mềm bóng đổ theo từng loại đèn:**
  * **Point Light & Spot Light:** Điều chỉnh qua thuộc tính **Radius** (trong code Python `bpy` gọi là `shadow_soft_size`) [2, 7, 8]. Giá trị `0.0m` cho bóng cứng tuyệt đối; tăng lên `0.2m` – `0.5m+` để làm mềm bóng [7, 9].
  * **Area Light:** Điều chỉnh thuộc tính **Size** (hoặc `Width` và `Height` nếu dùng dạng hình chữ nhật / elip) [2, 7]. Sử dụng kích thước từ `0.5m` đến `2.0m+` để mô phỏng tấm tản sáng/softbox [9].
  * **Sun Light:** Điều chỉnh thuộc tính **Angle** [2, 7]. Mặc định là \\(0.526^\circ\\) (khớp với góc đường kính Mặt Trời thực tế) [4, 7]; tăng góc lên \\(2^\circ - 5^\circ\\) sẽ tạo hiệu ứng ánh sáng ngày nhiều mây [7].

* **So sánh giữa Cycles và EEVEE Next (Blender 4.2+):**
  * **Cycles:** Sử dụng thuật toán dò tia Path-tracing để tính toán chính xác bóng đổ dựa trên hình học thực tế của nguồn sáng [10].
  * **EEVEE Next:** Sử dụng công nghệ **Virtual Shadow Maps (VSM)** kết hợp với ray-traced shadow maps [9-12]. Độ phân giải bóng đổ được cấu hình từ `1024` đến `4096` pixel cho từng đèn cùng các mẫu bóng mềm (soft shadow samples) [12].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### **Thao tác trên giao diện (UI):**
1. Chọn nguồn sáng trong Viewport hoặc Outliner.
2. Mở tab **Data Properties** (biểu tượng bóng đèn màu xanh).
3. Thiết lập thông số độ lớn tương ứng với loại đèn:
   * **Area Light:** Tăng thuộc tính `Size` (ví dụ: \\(1.2\text{m} - 1.5\text{m}\\)) [7, 8].
   * **Point / Spot Light:** Tăng thuộc tính `Radius` (ví dụ: \\(0.3\text{m} - 0.5\text{m}\\)) [7, 8].
   * **Sun Light:** Tăng thuộc tính `Angle` (ví dụ: \\(1.5^\circ - 3.0^\circ\\)).
4. Đối với **EEVEE Next**, truy cập **Render Properties > Shadows**, cài đặt độ phân giải Shadow Map (`1024` – `4096`) và bật tính năng Ray Tracing / Soft Shadows [9, 12].

#### **Code Python (`bpy`) cấu hình tự động:**
Ví dụ mã nguồn thiết lập các loại đèn với thông số bóng đổ chuẩn:

```python
import bpy
import math

# 1. Tạo Area Light với bóng đổ mềm (Soft Shadow)
area_data = bpy.data.lights.new(name="Area_Soft_Key", type='AREA')
area_data.size = 1.5  # Kích thước 1.5m tạo hiệu ứng Softbox
area_data.energy = 350.0
area_obj = bpy.data.objects.new(name="Area_Soft_Key", object_data=area_data)
bpy.context.scene.collection.objects.link(area_obj)

# 2. Tạo Point Light với bán kính làm mềm bóng
point_data = bpy.data.lights.new(name="Point_Soft_Fill", type='POINT')
point_data.shadow_soft_size = 0.3  # Radius = 0.3m làm mờ mép bóng
point_data.energy = 120.0
point_obj = bpy.data.objects.new(name="Point_Soft_Fill", object_data=point_data)
bpy.context.scene.collection.objects.link(point_obj)

# 3. Tạo Sun Light với góc chiếu rộng hơn thực tế để bóng mềm
sun_data = bpy.data.lights.new(name="Sun_Soft_Day", type='SUN')
sun_data.angle = math.radians(2.5)  # Đặt góc 2.5 độ (mặc định là 0.526 deg)
sun_data.energy = 1.0
sun_obj = bpy.data.objects.new(name="Sun_Soft_Day", object_data=sun_data)
bpy.context.scene.collection.objects.link(sun_obj)
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

* **Để `Radius` hoặc `Size` bằng 0 (`0.0m`):** Khiến bóng đổ quá cứng, xuất hiện vệt sắc nhọn không tự nhiên và dễ gây ra hạt nhiễu (fireflies) trong Cycles [9].
* **Sai lệch tỷ lệ xựng hình (Scene Scale):** Nếu vật thể quá to hoặc quá nhỏ so với quy chuẩn \\(1\text{ unit} = 1\text{ meter}\\), các thông số `Size` hay `Radius` tính bằng mét sẽ bị lệch tỷ lệ, khiến bóng mờ quá đà hoặc không đủ mềm [1].
* **Nhầm lẫn giữa Công suất (Power) và Kích thước (Size):** Tăng số Watt/Lumen chỉ làm cảnh sáng hơn chứ không làm bóng mờ đi [2, 7].
* **Hiện tượng nhấp nháy bóng (Flickering Volume / Shadows) trong EEVEE Next:** Do độ phân giải Shadow Map quá thấp hoặc bước nhảy thể tích (`Volume Step Rate` / `Steps`) chưa đủ cao (cần tăng lên 128 hoặc 256) [12, 13].
* **Phương pháp kiểm tra:** Xem trước kết quả qua chế độ **Viewport Shading (Rendered)** [14, 15]. Mở công cụ **False Color** trong bảng **Color Management** để đánh giá sự cân bằng giữa vùng phơi sáng, vùng tối và độ mờ mượt của bóng đổ [15, 16].

---
💡 *Bạn có muốn tìm hiểu thêm cách kết hợp kỹ thuật bóng mờ này với phương pháp chiếu sáng 3 điểm (Three-Point Lighting) hoặc cấu hình nhiệt độ màu Blackbody cho cảnh quay không?*
