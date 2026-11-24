# [L07] Light Linking & Shadow Linking: Tách riêng đèn cho nhân vật và môi trường trong Blender

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

1. **Tóm tắt Bản chất (2-3 câu)**
**Light Linking (Liên kết ánh sáng)** và **Shadow Linking (Liên kết bóng đổ)** là các tính năng kiểm soát ánh sáng nâng cao, cho phép chỉ định chính xác nguồn sáng nào được phép chiếu sáng hoặc tạo bóng đổ trên những vật thể cụ thể [1-3]. Tính năng này đặc biệt quan trọng khi cần đánh **Rim Light** (đèn viền tách nhân vật khỏi nền) hoặc **Eye Catchlight** (điểm sáng trong mắt) cho nhân vật mà không làm bùng sáng (overexpose) hay làm lóa tường và mặt đất xung quanh [2, 4-7]. Nhờ đó, họa sĩ 3D có thể chủ động tạo điểm nhấn thị giác nghệ thuật mà không làm phá vỡ tổng thể hệ thống ánh sáng chung của cảnh [7-9].

---

2. **Nguyên lý & Thông số Chuẩn**
* **Chế độ tác động (Linking Modes)**:
  * **Include Mode (Bao gồm)**: Đèn chỉ chiếu sáng duy nhất các vật thể hoặc Collection được liệt kê trong danh sách; toàn bộ môi trường còn lại sẽ hoàn toàn bỏ qua nguồn sáng này [2, 7]. Đây là lựa chọn tối ưu khi đánh Rim Light hoặc Catchlight riêng cho nhân vật [2, 5, 7].
  * **Exclude Mode (Loại trừ)**: Đèn chiếu sáng toàn bộ cảnh ngoại trừ các vật thể/Collection được đưa vào danh sách loại trừ [2, 7]. Thường dùng khi muốn đèn chiếu sáng nhân vật nhưng bỏ qua bức tường hay màn hình đằng sau [2, 4, 10].
* **Độc lập giữa Chiếu sáng (Illumination) và Bóng đổ (Shadow)**:
  * Hai kênh này có thể bật/tắt riêng biệt [11]. Bạn có thể giữ ánh sáng chiếu lên nhân vật nhưng tắt kênh Shadow để đèn Rim không tạo ra bóng đổ vô lý hay bóng đôi (double shadows) lên tường và mặt đất xung quanh [11-13].
* **Khả năng hỗ trợ của Render Engine**:
  * **Cycles**: Hỗ trợ native Light/Shadow Linking ở cấp độ Object và Collection từ Blender 4.0+ [3, 14].
  * **EEVEE Next**: Hỗ trợ native Light Linking chính thức từ **Blender 4.3+** [14-16]. Ở EEVEE trong Blender 4.2 trở xuống, kỹ thuật này được giả lập thông qua **View Layers** và quản lý ẩn/hiện Collection [17-19].
* **Thông số kỹ thuật chuẩn cho Rim Light / Spot Light**:
  * **Kiểu đèn**: Thường dùng **Area Light** (hình chữ nhật/đĩa) hoặc **Spot Light** [5, 20-22].
  * **Sắc độ / Nhiệt độ màu (Blackbody)**: Tông lạnh khoảng **6500K – 8500K** (xanh nhạt) để tạo sự tương phản rõ rệt với Key Light tông ấm (3200K - 3800K) [17, 22, 23].
  * **Kích thước nguồn sáng**: Bán kính Spot (`shadow_soft_size` / `radius`) khoảng **0.2m – 0.3m** [22, 24], hoặc Area Size **0.5m – 1.2m** giúp viền sáng mềm mại, tránh cạnh cứng gắt [22, 24, 25].
  * **Góc nón Spot (`spot_size`)**: Khoảng **40° – 45°** với độ làm mềm viền (`spot_blend`) khoảng **0.5** để gom luồng sáng tập trung vào nhân vật [17, 22, 26].

---

3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

### A. Thao tác trên giao diện Blender (GUI)
1. **Gom nhóm đối tượng**: Gom phần lưới nhân vật hoặc mắt vào một Collection riêng (ví dụ đặt tên là `Hero_Character`) [10, 22, 27].
2. **Chọn nguồn sáng**: Chọn đèn Rim Light hoặc Catchlight trong 3D Viewport [1, 27].
3. **Mở thiết lập Light Linking**:
   * Chuyển sang bảng **Object Properties** (biểu tượng hình vuông màu cam) \\(\rightarrow\\) tìm mục **Shading** \\(\rightarrow\\) chọn **Light Linking** (hoặc **Shadow Linking**) [1, 3, 27, 28].
   * (Hoặc trên Cycles: **Object Data Properties** \\(\rightarrow\\) **Visibility** \\(\rightarrow\\) **Light Linking**) [27].
4. **Tạo danh sách liên kết**: Nhấp nút **New** (hoặc Add Collection) để khởi tạo danh sách [1, 27].
5. **Gán đối tượng**: Kéo thả Collection `Hero_Character` vào ô danh sách và đảm bảo giữ ở chế độ **Include** [1, 2, 7, 27, 28].
6. **Tinh chỉnh Shadow Linking**: Nếu không muốn đèn Rim Light tạo thêm bóng đổ phụ lên sàn nhà hay tường, mở thẻ Shadow Linking của đèn và tắt kênh Shadow (biểu tượng bóng đổ) [11, 13, 29].

### B. Thao tác tự động hóa bằng Script Python (`bpy`)
Đoạn mã Python dưới đây khởi tạo một đèn Spot Rim Light, thiết lập nhiệt độ màu Blackbody chuẩn và gán Light Linking tự động cho Collection nhân vật [22, 30]:

```python
import bpy
import math

def setup_rim_light_linking(character_collection_name="Hero_Character"):
    scene = bpy.context.scene

    # 1. Lấy hoặc tạo Collection chứa nhân vật
    char_coll = bpy.data.collections.get(character_collection_name)
    if not char_coll:
        char_coll = bpy.data.collections.new(character_collection_name)
        scene.collection.children.link(char_coll)

    # 2. Tạo dữ liệu và Object cho đèn Rim Light
    light_data = bpy.data.lights.new(name="Rim_Light_Data", type='SPOT')
    light_data.shadow_soft_size = 0.3          # Bán kính điểm sáng mềm [22]
    light_data.spot_size = math.radians(45.0)  # Góc nón 45 độ [22]
    light_data.spot_blend = 0.5                # Mềm viền nón sáng [22]

    light_obj = bpy.data.objects.new(name="Rim_Light_Hero", object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = (2.0, -2.0, 3.0)      # Vị trí phía sau/bên hông nhân vật

    # 3. Cấu hình Node nhiệt độ màu Blackbody (8500K cho tông viền lạnh) [22]
    light_data.use_nodes = True
    nodes = light_data.node_tree.nodes
    links = light_data.node_tree.links

    emission_node = nodes.get("Emission") or next((n for n in nodes if n.type == 'EMISSION'), None)
    if emission_node:
        emission_node.inputs['Strength'].default_value = 400.0  # Cường độ đèn Rim [22]
        
        blackbody_node = nodes.new(type="ShaderNodeBlackbody")
        blackbody_node.inputs.default_value = 8500.0         # 8500K [22]
        blackbody_node.location = (-200, 300)
        links.new(blackbody_node.outputs, emission_node.inputs['Color'])

    # 4. Gán Light Linking (Chỉ chiếu sáng Collection nhân vật, không lóa tường/sàn) [22, 30]
    if hasattr(light_obj, "light_linking"):
        light_obj.light_linking.receiver_collection = char_coll

    print(f"Đã tạo {light_obj.name} và gán Light Linking tới Collection '{character_collection_name}'.")

# Chạy hàm thiết lập
setup_rim_light_linking("Hero_Character")
```

Khi muốn **gỡ bỏ Light Linking** bằng Python (đưa đèn về trạng thái chiếu sáng toàn bộ mặc định) [30-32]:
```python
import bpy

# Gỡ liên kết Light Linking của các đèn đang được chọn
for obj in bpy.context.selected_objects:
    if obj.type == 'LIGHT' and hasattr(obj, "light_linking"):
        obj.light_linking.receiver_collection = None
        obj.light_linking.blocker_collection = None
```

---

4. **Lỗi thường gặp & Cách kiểm tra**
* **Lỗi 1: Tự động nhân bản vật thể (`Cube.001`, `Character.001`) khi Append đèn từ file khác**:
  * *Nguyên nhân*: Khi Append một Collection đèn chứa Light Linking từ file `.blend` cũ sang cảnh mới, Blender sẽ tự động kéo theo và nhân bản toàn bộ đối tượng được liên kết trong Collection đó [33-36].
  * *Cách xử lý*: Trước khi Append, hãy gỡ liên kết `receiver_collection = None` hoặc sau khi Append hãy xóa các vật thể trùng lặp bằng script dọn dẹp [30, 31, 37, 38].
* **Lỗi 2: Sao chép đèn (Shift+D) làm thay đổi cài đặt linking của đèn gốc**:
  * *Nguyên nhân*: Các đèn được nhân bản có thể dùng chung dữ liệu Collection liên kết (Shared Linking Data) [32, 39].
  * *Cách xử lý*: Sử dụng lệnh **Make Single-User** cho dữ liệu linking của đèn hoặc bật tùy chọn *Auto Fix Shared Linking* trong add-on quản lý [32, 39].
* **Lỗi 3: Ánh sáng gián tiếp (GI Bounce) hoặc bóng đôi làm lem sáng lên môi trường**:
  * *Nguyên nhân*: Mặc dù Light Linking chặn tia sáng trực tiếp (Direct Rays), tia nảy gián tiếp (Global Illumination) vẫn có thể hắt từ nhân vật sang tường/sàn [12, 40]. Đồng thời, nếu không chỉnh Shadow Linking, bóng đổ của Rim Light có thể chồng lên bóng của Key Light tạo thành bóng đôi [12, 41].
  * *Cách xử lý*: Kiểm tra và ngắt kết nối Shadow Linking nếu cần [11, 13, 29], hoặc tắt bớt tính năng Ray Visibility không cần thiết [40, 42].
* **Lỗi 4: Không thấy mục Light Linking xuất hiện trên giao diện**:
  * *Nguyên nhân*: Đang sử dụng EEVEE trên các phiên bản trước Blender 4.3 [14-16] hoặc dùng Cycles phiên bản cũ trước 4.0 [27, 43].
  * *Cách xử lý*: Đảm bảo chuyển Render Engine sang **Cycles** (ở Blender 4.0+) hoặc nâng cấp Blender lên phiên bản **4.3 trở lên** nếu sử dụng EEVEE Next [14-16].

💡 Bạn có muốn mình tạo một kịch bản script tự động hóa trọn gói hệ thống Three-Point Lighting kèm Light Linking sẵn cho nhân vật không?
