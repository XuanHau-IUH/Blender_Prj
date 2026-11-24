# [L04] Khí quyển & Sương mù thể tích (Volumetric Fog, Mist & God Rays / Tia nắng xuyên qua khe hẹp)

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

### 1. Tóm tắt Bản chất (2-3 câu)
Việc tạo sương mù thể tích (Volumetric Fog) và tia sáng God Rays bằng shader **Principled Volume** là kỹ thuật mô phỏng lại hiện tượng ánh sáng bị tán xạ và hấp thụ khi đi qua các hạt mịn lơ chửng trong không khí [1, 2]. Phương pháp này mang lại độ sâu không gian và tính điện ảnh (atmospheric perspective) vượt trội cho cảnh 3D [1, 3]. Việc làm chủ các thông số cốt lõi như **Density** (mật độ) và **Anisotropy** (hướng tán xạ) giúp kiểm soát hình dạng vệt sáng rõ nét mà không làm cháy vùng sáng (overexposure) hay gây nhiễu hạt/nhấp nháy (noise/flickering) khi render [2, 4-6].

---

### 2. Nguyên lý & Thông số Chuẩn
Dưới đây là các quy tắc toán - lý và thông số chuẩn được tổng hợp từ tài liệu [2, 5, 7]:

* **Các thông số trọng yếu của Principled Volume Shader**:
  * **Density (Mật độ)**: Kiểm soát nồng độ hạt lơ chửng per \\(m^3\\) [2]. Với sương mù/khí quyển tự nhiên, hãy cài đặt ở mức rất thấp từ **0.01 đến 0.05** [2]. Đặt quá cao sẽ làm thể tích bị đục ngầu, chắn sạch ánh sáng và tiêu tốn tài nguyên render [2, 8].
  * **Scatter Color (Màu tán xạ)**: Màu của ánh sáng phản xạ bởi hạt thể tích [2]. Nên giữ **trắng trung tính hoặc xám nhạt** để giữ nguyên phổ màu tự nhiên của nguồn sáng [2, 9].
  * **Absorption Color (Màu hấp thụ)**: Màu bị lọc *bớt* khi ánh sáng đâm xuyên qua thể tích [2]. (Ví dụ: Absorption màu xanh ngọc sẽ lọc bỏ sắc đỏ, khiến các vùng sâu phía xa mang tông màu lạnh) [2, 9].
  * **Anisotropy (\\(g\\))**: Điều khiển hướng tán xạ ánh sáng so với tia sáng tới, nằm trong khoảng \\([-1, 1]\\) [2, 5]. Hành vi này tuân theo hàm pha Henyey-Greenstein [5]:
    \\[P(\theta) = \frac{1}{4 \pi} \frac{1 - g^2}{(1 + g^2 - 2 g \cos\theta)^{3/2}}\\]
    * \\(g = 0\\) (Isotropic): Tán xạ đẳng hướng (dùng cho khói/hơi nước đồng nhất) [5, 9].
    * \\(g > 0\\) (Forward Scattering): Tán xạ tiến về phía trước [5]. Đặt giá trị cao từ **0.7 đến 0.9** là chìa khóa để tạo các tia sáng **God Rays** rực rỡ khi nhìn ngược về phía nguồn sáng [5].

* **Thiết lập nguồn sáng (Spotlight Cone Mechanics)**:
  * Góc hình nón (**Size/Cone Angle**) hẹp kết hợp **Blend** thấp tạo vệt sáng God Rays đâm thẳng sắc nét; góc rộng và Blend cao tạo quầng sáng mịn dịu [10].

* **Thông số Render tối ưu Noise & Cháy sáng (Cycles vs EEVEE Next)**:
  * **Cycles Engine**:
    * **Volume Step Rate**: Đặt từ **0.1 đến 0.5** cho bản render chính thức để chia nhỏ bước ray-marching, loại bỏ tình trạng vệt sọc (banding) [7, 11].
    * **Volume Bounces**: Mặc định là `0` (Single Scattering). Nâng lên **1 đến 2** (Multi-Scattering) để ánh sáng nảy mềm mại bên trong sương mù [7, 11, 12].
    * **Sampling & Denoising**: Đặt **256–512 samples** (hoặc 1024+ cho cảnh phức tạp) với **Noise Threshold = 0.01** [12-14]. Bật **OpenImageDenoise (OID)** [12, 15].
    * **Clamping Indirect**: Đặt mức **10** (hoặc 0.1) để dập tắt đốm nhiễu trắng (fireflies) và kiểm soát hiện tượng cháy sáng [12, 15].
  * **EEVEE Next Engine (Blender 4.x)**:
    * **Volume Steps**: Tăng từ mặc định 64 lên **128 đến 256** để làm mịn tia sáng God Rays [7, 16, 17].
    * **Dithered Volumes**: Kích hoạt chế độ Dithered để ngẫu nhiên hóa vị trí mẫu voxel, chuyển đường cắt slice cứng thành nhiễu hạt tần số cao dễ xử lý bởi Temporal Denoise, giúp loại bỏ nhấp nháy (flickering) khi camera di chuyển [4, 6, 7].
    * **Volume Shadow Samples**: Nâng từ 16 lên **64 hoặc 128** để tránh hiện tượng bóng râm bị vỡ khối vuông trong sương mù [18].
    * **Custom Range**: Giới hạn phạm vi tính toán (ví dụ: **0.5m đến 100m**) tránh kéo giãn mẫu voxel ra khoảng cách xa không cần thiết [7, 18].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

* **Thao tác thủ công trên giao diện UI**:
  1. **Tạo khối bao phủ (Container Mesh)**: Tạo một khối Cube lớn bao trọn không gian cảnh [19, 20]. *Lưu ý*: Không gán Principled Volume trực tiếp vào World Shader trong Blender 4.2+ vì World Volume sẽ chặn hoàn toàn ánh sáng xa (Sun Light/Environment Light) khiến cảnh đen xì [4, 16, 21].
  2. **Gán Shader**: Tạo Material mới cho Cube, xóa nút *Principled BSDF*, thêm nút **Principled Volume** và cắm đầu ra *Volume* vào cổng *Volume* của nút **Material Output** [19, 20].
  3. **Cấu hình Shader**: Đặt `Density = 0.01 – 0.03` và `Anisotropy = 0.8` [2, 5].
  4. **Bố trí đèn Spot Light**: Đặt một đèn Spot chiếu xuyên qua khe cửa hoặc tán cây vào trong khối Domain [10].
  5. **Cấu hình Render**: Điều chỉnh `Step Rate = 0.25`, `Volume Bounces = 1`, `Indirect Clamp = 10` trong Cycles [7, 11, 12, 15]; hoặc `Volume Steps = 128` + `Dithered Volumes` trong EEVEE Next [4, 6, 7, 16].

* **Mã nguồn Python (`bpy`) tự động hóa**:

```python
import bpy

# 1. Tạo Domain Container Cube chứa sương mù
bpy.ops.mesh.primitive_cube_add(size=20, location=(0, 0, 0))
fog_cube = bpy.context.active_object
fog_cube.name = "Volume_Atmosphere_Domain"

# Tạo Material sương mù thể tích
fog_mat = bpy.data.materials.new(name="Atmospheric_Fog_Material")
fog_mat.use_nodes = True
nodes = fog_mat.node_tree.nodes
links = fog_mat.node_tree.links

# Xóa Principled BSDF mặc định
bsdf = nodes.get("Principled BSDF")
if bsdf:
    nodes.remove(bsdf)

# Tạo Principled Volume Node
vol_node = nodes.new(type='ShaderNodeVolumePrincipled')
vol_node.location = (-300, 0)
vol_node.inputs['Density'].default_value = 0.02       # Mật độ nhẹ (0.01 - 0.05)
vol_node.inputs['Anisotropy'].default_value = 0.8     # Forward scattering cao tạo God Rays

# Nối vào cổng Volume của Material Output
output_node = nodes.get("Material Output")
links.new(vol_node.outputs['Volume'], output_node.inputs['Volume'])

# Gán material vào Cube
if fog_cube.data.materials:
    fog_cube.data.materials = fog_mat
else:
    fog_cube.data.materials.append(fog_mat)

# 2. Tạo nguồn sáng Spot Light chiếu tạo God Rays
bpy.ops.object.light_add(type='SPOT', location=(6, -6, 8))
spot_light = bpy.context.active_object
spot_light.name = "GodRay_SpotLight"
spot_light.data.energy = 800.0        # Công suất chiếu sáng (W)
spot_light.data.spot_size = 0.785     # Góc nón ~ 45 độ
spot_light.data.spot_blend = 0.2      # Làm mềm rìa vệt sáng

# 3. Cấu hình Render Settings tối ưu cho Cycles
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_adaptive_sampling = True
scene.cycles.noise_threshold = 0.01
scene.cycles.volume_step_rate = 0.25      # Mịn hóa bước ray-marching
scene.cycles.volume_bounces = 1           # Multi-scattering nhẹ
scene.cycles.sample_clamp_indirect = 10.0 # Khống chế cháy sáng & fireflies
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1. **Dùng Principled Volume trên World Shader trong Blender 4.2+ (EEVEE Next)**:
   * *Lỗi*: Khung cảnh biến thành màu đen xì hoặc mất sạch ánh sáng mặt trời/HDRI [4, 16, 21].
   * *Khắc phục*: Luôn sử dụng khối Mesh Container (Cube) riêng biệt làm phạm vi giới hạn sương mù thay vì dùng World Shader [19, 21, 22].
2. **Mật độ Density đặt quá lớn (> 0.1)**:
   * *Lỗi*: Cảnh bị đục đặc, vùng sát đèn bị cháy sáng rực còn vùng xa bị đen kịt, thời gian render tăng vọt [2, 8, 23].
   * *Khắc phục*: Giảm `Density` về khoảng **0.01 – 0.05** cho bầu khí quyển tự nhiên [2, 23].
3. **Quên nâng Anisotropy (\\(g\\)) làm vệt God Rays bị mờ nhạt**:
   * *Lỗi*: Ánh sáng bị tỏa đều thành quầng mờ thay vì hội tụ thành các luồng tia sáng rõ nét [5, 9, 19].
   * *Khắc phục*: Tăng `Anisotropy` lên mức **0.7 đến 0.9** [5, 19].
4. **Hiện tượng giật hình / nhấp nháy (Flickering) trong EEVEE Next Animation**:
   * *Lỗi*: Các đường sọc sương mù bị giật nhấp nháy liên tục qua từng khung hình [6, 24, 25].
   * *Khắc phục*: Bật **Dithered Volumes** [4, 6, 8], tăng **Volume Steps** lên 128–256 [7, 16, 17], tăng **Volume Shadows** lên 64/128 [18] và cài đặt **Custom Range** phù hợp với quy mô cảnh [7, 18].
5. **Nhiễu đốm trắng (Fireflies) và vệt cắt sọc (Banding) trong Cycles**:
   * *Lỗi*: Đốm trắng lấm tấm xuất hiện trong sương mù hoặc các quầng sáng bị giật bậc thang [12, 19].
   * *Khắc phục*: Giảm **Step Rate** xuống 0.25 [7, 19], bật **Indirect Clamping = 10** [12, 15], sử dụng **OpenImageDenoise** [12, 15, 24].

---

💡 Bạn có muốn mình hướng dẫn kỹ hơn về cách kết hợp kỹ thuật **Light Linking** để chiếu riêng luồng sáng God Rays vào sương mù mà không làm ảnh hưởng đến ánh sáng chính trên nhân vật không?
