# [L05] Chiếu sáng hẻm đô thị & Nội thất thiếu sáng (Bounce Light, Light Portal & Ambient Fill)

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

Dưới đây là phân tích chi tiết về kỹ thuật chiếu sáng không gian hẹp (như phòng kín hay hẻm sâu) dựa trên tài liệu trong sổ tay của bạn:

---

### 1. **Tóm tắt Bản chất**
Chiếu sáng không gian hẹp tập trung vào việc dẫn hướng và phân bổ nguồn sáng tự nhiên từ bên ngoài đi sâu vào bên trong không gian mà không làm mất đi tính chân thực của môi trường [1, 2]. Bằng cách kết hợp **Light Portal** để tối ưu hóa thuật toán lấy mẫu của Cycles qua các khung mở, tăng số lần **Phản xạ gián tiếp (Indirect Bounce Light)** và bổ sung **Đèn phụ trợ (Fill Area Light)** dịu nhẹ, hệ thống giúp duy trì chi tiết vùng tối [1, 3-5]. Phương pháp này ngăn chặn hiện tượng bóng đổ bị bệt đen phẳng lì, tạo chuyển tiếp mềm mại và giàu chiều sâu cho khung hình [2, 6, 7].

---

### 2. **Nguyên lý & Thông số Chuẩn**

* **Light Portal (Cửa dẫn hướng ánh sáng):**
  * **Nguyên lý:** Đặt tại khung cửa sổ hoặc vị trí mở hẹp để định hướng thuật toán lấy mẫu (sampling algorithm) của Cycles truy vết ánh sáng từ môi trường HDRI bên ngoài vào nội thất [1, 8].
  * **Tác dụng:** Tăng hiệu quả lấy mẫu, giảm nhiễu hạt (noise) và tối ưu thời gian dựng hình mà vẫn giữ chất lượng ảnh chân thực [1, 8].

* **Phản xạ gián tiếp (Indirect Bounce Light) & Khóa bật nảy (Light Paths):**
  * **Diffuse Bounces:** Mặc định là 4, nhưng với không gian hẹp sâu hoặc phòng kín cần ánh sáng bật nảy sâu vào góc chết, nên tăng lên **6 – 8 lần nảy** [3].
  * **Glossy & Transmission Bounces:** Thiết lập khoảng **8 – 12** để đảm bảo ánh sáng phản xạ và truyền qua các lớp kính cửa [3, 9].
  * **Volume Bounces:** Đặt bằng **0** cho môi trường trong suốt [9]; tăng lên **1 – 2** nếu cảnh có hiệu ứng sương mù/khí quyển (Volumetric Scatter) [3, 10].
  * **Clamping:** Đặt **Clamp Indirect = 10.0** để triệt tiêu các đốm nhiễu sáng (fireflies) mà không làm suy giảm tổng thể lượng ánh sáng nảy [3].

* **Đèn phụ trợ (Fill Area Light) & Tỷ lệ chiếu sáng (Lighting Ratio):**
  * **Vị trí & Hình dạng:** Đặt ở góc đối diện đèn chính (Key Light), lệch khoảng \\(-30^\circ\\) đến \\(-45^\circ\\) so với trục camera và nâng cao ngang tầm camera (\\(10^\circ - 30^\circ\\)) [11, 12]. Sử dụng **Area Light** kích thước lớn (\\(0.2\text{m} - 2.0\text{m}\\)) thay vì Point Light nhỏ để tạo ra vùng nửa tối (penumbra) mịn màng [4, 13, 14].
  * **Tỷ lệ Key-to-Fill:** Giữ tỷ lệ ở mức thấp khoảng **2:1** (cường độ Fill Light bằng khoảng \\(0.25 - 0.5\\) so với Key Light) để làm mềm bóng đổ, giữ chi tiết vùng tối mà không làm mất hoàn toàn bóng [11, 12, 15].
  * **Nhiệt độ màu (Blackbody):** Áp dụng phối màu đối lập (Cool & Warm split) với nguồn sáng ngoài trời mang tông lạnh (\\(5500\text{K} - 6500\text{K}\\)) kết hợp Fill Light mang tông ấm nhẹ (\\(3200\text{K} - 3800\text{K}\\)) giúp vùng tối có sự chuyển màu phong phú, không bị u ám [12, 16, 17].

* **Color Management & View Transform:**
  * Chuyển View Transform từ Standard sang **AgX** (hoặc Filmic) để xử lý dải động rộng, giữ lại chi tiết cả vùng sáng gắt lẫn vùng tối sâu [18].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### **A. Thao tác thủ công trên giao diện UI:**
1. **Chế độ Render & Light Paths:** Chuyển Render Engine sang **Cycles**. Tại thẻ *Render Properties* > *Light Paths*, cài đặt `Max Bounces = 12`, `Diffuse Bounces = 6-8`, `Glossy = 8`, `Clamp Indirect = 10.0` [3]. Trong mục *Color Management*, chọn View Transform là **AgX** [18].
2. **Thiết lập Light Portal:** Thêm một Area Light (`Shift+A` > Light > Area), di chuyển và xoay sao cho vừa khít khung cửa/khe hẹp hướng vào phòng. Trong thẻ *Data Properties* của đèn, tích chọn **Portal** [1, 8].
3. **Thêm Fill Area Light:** Thêm một Area Light phía góc tối đối diện, chỉnh `Shape = Square` hoặc `Rectangle`, tăng `Size` lên \\(1.5\text{m}\\) [13, 14]. Tích chọn *Use Nodes*, gắn node **Blackbody** vào ô Color của node Emission và đặt giá trị `3800K` [12, 16].

#### **B. Mã nguồn Python (`bpy`) thiết lập tự động:**

```python
import bpy

# 1. Kich hoat Render Engine Cycles va thiet lap Light Paths
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
cycles = scene.cycles

# Thong so bat nay anh sang va khu nhieu (Bounce Limits & Clamping)
cycles.max_bounces = 12
cycles.diffuse_bounces = 6
cycles.glossy_bounces = 8
cycles.transmission_bounces = 8
cycles.volume_bounces = 0
cycles.sample_clamp_indirect = 10.0

# Sampling va Quan ly mau AgX
cycles.use_adaptive_sampling = True
cycles.adaptive_threshold = 0.01
scene.view_settings.view_transform = 'AgX'

# 2. Tao Light Portal tai khung cua so / khoang mo
portal_data = bpy.data.lights.new(name="Window_Portal_Light", type='AREA')
portal_data.is_portal = True  # Kich hoat tinh nang Light Portal trong Cycles
portal_obj = bpy.data.objects.new(name="Window_Portal_Light", object_data=portal_data)
scene.collection.objects.link(portal_obj)

# Vi tri va kich thuoc che phu khung cua
portal_obj.location = (0.0, -2.0, 1.5)
portal_obj.scale = (1.5, 1.5, 1.0)

# 3. Tao Fill Area Light cho vung toi
fill_data = bpy.data.lights.new(name="Fill_Area_Light", type='AREA')
fill_data.shape = 'SQUARE'
fill_data.size = 1.5      # Kich thuoc phat sang lon de tao penumbra mem
fill_data.energy = 50.0   # Ty le cuong do diu (khoang 25%-50% so voi Key)

fill_obj = bpy.data.objects.new(name="Fill_Area_Light", object_data=fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-1.5, 1.0, 1.2)

# Thiet lap Node Blackbody de tao mau am phu vung toi (3800K)
fill_data.use_nodes = True
nodes = fill_data.node_tree.nodes
links = fill_data.node_tree.links

emission_node = nodes.get("Emission")
if emission_node:
    blackbody_node = nodes.new(type="ShaderNodeBlackbody")
    blackbody_node.inputs["Temperature"].default_value = 3800.0  # Nhiet do mau vang am
    links.new(blackbody_node.outputs["Color"], emission_node.inputs["Color"])
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

* **Lỗi 1: Đèn Fill quá mạnh hoặc dùng Point Light bán kính bằng 0 (Zero Radius):**
  * *Hậu quả:* Làm phẳng toàn bộ khối không gian hoặc tạo ra ranh giới bóng quá sắc nét, làm mất vẻ tự nhiên [6, 13, 19].
  * *Khắc phục:* Giữ tỷ lệ Key-to-Fill quanh **2:1 đến 4:1** [12, 20], dùng Area Light kích thước lớn (\\(0.5\text{m} - 2.0\text{m}\\)) để tạo chuyển tiếp penumbra mịn màng [13, 14].
* **Lỗi 2: Sử dụng Light Portal sai cách hoặc sai Render Engine:**
  * *Hậu quả:* Bật Portal nhưng không dùng môi trường HDRI ngoài trời, hoặc chạy trên EEVEE (portal chỉ có hiệu lực trong Cycles). Light Portal không tự phát ra ánh sáng mà chỉ làm nhiệm vụ dẫn hướng lấy mẫu [1, 8, 21].
  * *Khắc phục:* Đặt Portal che vừa khít ô cửa, hướng mặt về phía trong phòng và render bằng Cycles [1, 8].
* **Lỗi 3: Khóa số lần nảy gián tiếp (Diffuse Bounces) quá thấp:**
  * *Hậu quả:* Ánh sáng không thể nảy qua các bề mặt tường trong không gian hẹp, khiến các góc chết hoàn toàn không nhận được ánh sáng phản xạ và bị bệt đen [3, 18].
  * *Khắc phục:* Nâng `Diffuse Bounces` lên ít nhất **6 – 8** [3].
* **Lỗi 4: Xuất hiện nhiễu hạt đốm sáng (Fireflies) ở vùng tối:**
  * *Hậu quả:* Do các tia sáng phản xạ gián tiếp cường độ quá cao nảy vô tận [3].
  * *Khắc phục:* Thiết lập `Clamp Indirect = 10.0` [3] và bật OpenImageDenoise với Adaptive Sampling [3, 22].
* **Cách kiểm tra phơi sáng chuyên nghiệp:**
  * Bật chế độ **False Color** hoặc xem **Histogram** trong mục *Color Management* của Blender. Vùng tối đạt chuẩn sẽ thể hiện sắc thái xám tối / xanh đậm mịn màng trên màn hình quan sát chứ không trượt về sắc đen tuyệt đối (\\(0.0\\) giá trị phơi sáng) [23, 24].

💡 *Bạn có muốn mình tạo một bài báo cáo (Report) hoặc Slide tóm tắt quy trình thiết lập ánh sáng này để tiện lưu trữ không?*
