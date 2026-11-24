# [L06] Phân lớp sáng-tối (Light & Shadow Framing / Chiaroscuro) để dẫn hướng mắt người xem

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
**Kỹ thuật xen kẽ mảng sáng - mảng tối (Light-Dark Alternation)** kết hợp với **Chiaroscuro** và **Gobo/Cucoloris** là phương pháp bố cục ánh sáng luân phiên giữa các vùng sáng và tối trên từng lớp không gian [1, 2]. Phương pháp này tạo ra chiều sâu thị giác (3D spatial depth), giúp bóc tách rõ ràng giữa tiền cảnh, trung cảnh và hậu cảnh [2-4]. Nhờ đó, ánh mắt khán giả được định hướng tự nhiên và tập trung trực tiếp vào nhân vật chính (hero element) trong khung hình [2, 4, 5].

---

### 2. **Nguyên lý & Thông số Chuẩn**

* **Mô hình xen kẽ mảng tương phản (Spatial Layering):**
  * Thiết lập chuỗi độ sáng luân phiên từ gần đến xa theo công thức **Tối (Tiền cảnh) - Sáng (Trung cảnh / Nhân vật) - Tối (Hậu cảnh)** hoặc **Sáng - Tối - Sáng** để tách các lớp không gian [2, 6].
  * Bổ sung **Ánh sáng viền (Rim Light / Backlight)** đặt phía sau nhân vật để tách viền vai, tóc khỏi phông nền tối [3, 4].

* **Tỷ lệ chiếu sáng (Lighting Ratios) & Chiaroscuro:**
  * **Chiaroscuro** nhấn mạnh sự đối lập gắt giữa mảng sáng rực và mảng tối sâu để tạo khối thẩm mỹ và tính kịch tính [5, 7, 8].
  * **Công thức Tỷ lệ Key-to-Fill (Lighting Ratio):**
    \\[\text{Lighting Ratio} = \frac{\text{Cường độ Key} + \text{Cường độ Fill}}{\text{Cường độ Fill}}\\] [9]
  * **Các cấp độ tương phản chuẩn:**
    * **Tương phản cao / Low-key (Dramatic, Film Noir, Thriller):** Tỷ lệ **\\(8:1\\) trở lên**, bóng sâu, diện sáng thu hẹp [3, 7, 8, 10].
    * **Tương phản tiêu chuẩn (Cinematic / Drama):** Tỷ lệ **\\(4:1\\)**, cân bằng giữa chi tiết bóng và khối sáng [11].
    * **Tương phản thấp / High-key (Commercial, TV, Comedy):** Tỷ lệ **\\(2:1\\)**, ánh sáng chan hòa, bóng rất mềm [3, 10, 12, 13].

* **Bảng thông số vị trí & Nhiệt độ màu chuẩn:**

| Nguồn sáng | Góc ngang (Yaw) | Góc hạ (Pitch) | Nhiệt độ màu (Kelvin) | Tỷ lệ cường độ | Đặc tính bóng |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Key Light (Đèn chính)** | \\(35^\circ \text{ đến } 45^\circ\\) [1, 14-16] | \\(30^\circ \text{ đến } 50^\circ\\) [14] | \\(5500\text{K} - 6500\text{K}\\) (Daylight) [14] | \\(1.0\\) (Mốc chuẩn) [14] | Rõ nét, bóng mềm vừa phải [14] |
| **Fill Light (Đèn phụ)** | \\(-30^\circ \text{ đến } -45^\circ\\) [1, 9, 14] | \\(10^\circ \text{ đến } 30^\circ\\) [14] | \\(3200\text{K} - 3800\text{K}\\) (Warm Tungsten) [14, 17] | \\(0.25 - 0.50\\) [14] | Khuếch tán cao, không tạo bóng phụ [9, 14] |
| **Rim Light (Đèn viền)** | \\(120^\circ \text{ đến } 180^\circ\\) [1, 3, 14] | \\(45^\circ \text{ đến } 75^\circ\\) [14] | \\(7500\text{K} - 9000\text{K}\\) (Cool Blue) [14, 18] | \\(1.50 - 3.00\\) [14] | Đanh sắc, bám sát đường viền chủ thể [3, 14] |

* **Gobo / Cucoloris:**
  * Sử dụng tấm chắn đục lỗ hoặc họa tiết (như tán cây, rèm cửa) đặt trước nguồn sáng để chiếu bóng hoa văn mảng sáng/tối lên phông nền hoặc sàn nhà, phá vỡ sự phẳng lỳ đơn điệu của bề mặt [6, 19].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### **A. Thao tác thủ công trong Blender Viewport**
1. **Thiết lập Gobo họa tiết trên Spot / Area Light:**
   * Bật **Use Nodes** cho Shader của Đèn trong tab Data [20].
   * Thêm node **Image Texture** (hoặc node procedural như **Voronoi / Noise Texture**) kết nối qua node **Mapping** và **Texture Coordinate** vào đầu vào Color hoặc Strength của node **Emission** [21-23].
2. **Dùng mảng chắn đen (Black Backdrop / Flag):**
   * Đặt một tấm mặt phẳng màu đen (Black Plane) ngay phía sau camera hoặc ở tiền cảnh để triệt tiêu ánh sáng dội ngược, tăng độ tương phản cho khung hình [24, 25].
3. **Cách ly ánh sáng (Light Linking & Shadow Linking):**
   * Chọn đèn chính hoặc đèn viền \\(\rightarrow\\) Thẻ **Object Properties** \\(\rightarrow\\) Mục **Shading** / **Light Linking** [26].
   * Nhấn **New** và kéo Collection chứa nhân vật chính (Hero Collection) vào danh sách để bật chế độ **Include** (đèn chỉ chiếu sáng nhân vật) hoặc **Exclude** (bỏ qua phông nền) [26-28].

#### **B. Kịch bản Python `bpy` tự động hóa hệ thống**

```python
import bpy

def setup_chiaroscuro_gobo_rig():
    # 1. Tạo nguồn sáng Spot Light cho Gobo / Key Light
    light_data = bpy.data.lights.new(name="Key_Gobo_Light", type='SPOT')
    light_data.energy = 1000.0
    light_data.spot_size = 0.8  # Góc mở khoảng ~45 độ
    light_data.spot_blend = 0.3 # Độ mềm biên đèn
    
    light_obj = bpy.data.objects.new(name="Key_Gobo_Light", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (3.0, -3.0, 4.0)

    # 2. Kích hoạt Shader Nodes cho Đèn
    light_data.use_nodes = True
    nodes = light_data.node_tree.nodes
    links = light_data.node_tree.links
    nodes.clear()

    # Tạo các Node: Output, Emission, Voronoi (Gobo), Blackbody (Nhiệt độ màu)
    node_output = nodes.new(type='ShaderNodeOutputLight')
    node_emission = nodes.new(type='ShaderNodeEmission')
    node_blackbody = nodes.new(type='ShaderNodeBlackbody')
    node_gobo = nodes.new(type='ShaderNodeTexVoronoi')

    # Cấu hình tham số chuẩn
    node_blackbody.inputs['Temperature'].default_value = 5500.0  # Daylight Key
    node_gobo.inputs['Scale'].default_value = 4.0               # Độ dày họa tiết Gobo

    # Trộn màu nhiệt độ với họa tiết Gobo
    node_mix = nodes.new(type='ShaderNodeMix')
    node_mix.data_type = 'RGBA'
    node_mix.blend_type = 'MULTIPLY'
    node_mix.inputs.default_value = 1.0  # Factor

    # Nối dây Shader
    links.new(node_blackbody.outputs['Color'], node_mix.inputs[29])
    links.new(node_gobo.outputs['Color'], node_mix.inputs[30])
    links.new(node_mix.outputs[26], node_emission.inputs['Color'])
    links.new(node_emission.outputs['Emission'], node_output.inputs['Surface'])

    # 3. Cấu hình Light Linking cho Nhân vật chính (HeroCharacter)
    hero_coll = bpy.data.collections.get("HeroCharacter")
    if not hero_coll:
        hero_coll = bpy.data.collections.new("HeroCharacter")
        bpy.context.scene.collection.children.link(hero_coll)

    # Thiết lập Light Linking
    if hasattr(light_data, "light_linking"):
        light_data.light_linking.receiver_collection = hero_coll

setup_chiaroscuro_gobo_rig()
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

* **Lỗi thường gặp:**
  * **Đèn chính quá gắt làm phẳng khối:** Đặt Key Light quá gắt hoặc sai góc làm mất mảng tối tự nhiên trên mặt nhân vật, tạo cảm giác hình bị bệt [31].
  * **Lệch tông màu (Muddy Palette):** Không kiểm soát nhiệt độ màu giữa các đèn, làm cho các mảng màu nóng/lạnh bị triệt tiêu lẫn nhau [31].
  * **Dùng Area Light quá rộng cho toàn cảnh:** Nguồn sáng diện tích lớn tạo ra bóng đổ quá mềm, làm mất đi sự đối lập mảng sáng - tối và làm khung hình bệt phẳng như trời âm u (Overcast look) [32, 33].
  * **Trùng lặp vật thể (Mesh Duplication) khi Append:** Khi Append hệ thống đèn chứa **Light Linking Collection** từ file `.blend` khác sang, Blender sẽ tự động import và nhân bản luôn các vật thể liên kết (tạo ra `Cube.001` hay trùng lặp nhân vật) [34-37].
  * **Vệt Rim Light bị chói lóa:** Cường độ Rim Light quá đà làm tràn vệt sáng qua má hoặc mũi nhân vật thay vì chỉ ôm nhẹ đường viền [2].

* **Cách kiểm tra & Đánh giá chuẩn xác:**
  * **False Color & Histogram:** Chuyển View Transform sang **False Color** trong thẻ *Color Management* để theo dõi dải phơi sáng, kiểm soát chính xác các vùng tối (Blacks), vùng trung tính (Midtones) và vùng cháy sáng (Highlights) [31].
  * **Chuyển chế độ Grayscale / Monochromatic:** Tạm thời chuyển Viewport sang đen trắng để đánh giá riêng độ sáng (Luminance) và nhịp điệu tương phản mảng sáng - tối mà không bị màu sắc làm nhiễu [31, 38].

💡 **Gợi ý tiếp theo:** Bạn có muốn mở rộng đoạn mã Python trên để tự động tạo hoàn chỉnh cả bộ thiết lập 3 điểm sáng (Key, Fill, Rim) kết hợp cùng môi trường sương mù khí quyển (Volumetric Environment) không?
