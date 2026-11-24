# [L08] Chiếu sáng ban đêm, đèn Neon & Practical Lights (Emission + Bloom/Glare + Wet Surface Reflections)

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

### 1. Tóm tắt Bản chất (2-3 câu)

Quy trình chiếu sáng cảnh đêm kết hợp giữa đèn thực tế (Practical Lights) và đèn trợ sáng (Area Lights) nhằm tái tạo bầu không khí điện ảnh với độ tương phản cao và chiều sâu không gian ấn tượng [1, 2]. Sự kết hợp này lợi dụng sự phản xạ rực rỡ của biển hiệu Emission trên mặt đường ướt để phân tách các lớp không gian và thu hút ánh nhìn [1, 3]. Việc làm chủ nhiệt độ màu Kelvin và hệ thống quản lý màu sắc hiện đại giúp khung cảnh 3D tránh bị cháy sáng, giữ được độ chân thực và đắm chìm cho thị giác [4-6].

---

### 2. Nguyên lý & Thông số Chuẩn

*   **Bản chất nguồn sáng cảnh đêm & Mặt đường ướt:**
    *   Khác với cảnh ban ngày có một nguồn sáng chủ đạo (mặt trời) và bầu trời mềm, cảnh đêm được cấu thành từ hàng chục đến hàng trăm nguồn sáng nhỏ, gắt và có độ tương phản cao (đèn đường, biển hiệu neon, đèn xe) [1, 3, 7].
    *   Mặt đường ướt đóng vai trò như một tấm gương phản xạ nhòe, hứng trọn các vệt màu (splotches) từ biển hiệu và đèn giao thông, tạo ra nhịp điệu thị giác sống động [1, 3].
*   **Quy luật suy giảm cường độ (Inverse Square Law):**
    *   Ánh sáng suy giảm theo bình phương khoảng cách: \\(E = \frac{P}{4 \pi d^2}\\) [8]. Việc duy trì tỉ lệ cảnh thực (\\(1\text{ unit} = 1\text{ meter}\\)) trong Blender là bắt buộc để các thông số suy giảm của đèn Area và khả năng tán xạ thể tích (volumetric scattering) đạt độ chuẩn xác vật lý [8].
*   **Thang nhiệt độ màu Kelvin & Nút Blackbody:**
    *   Sử dụng nút **Blackbody** để chuyển đổi nhiệt độ Kelvin trực tiếp sang dải màu RGB [5, 9, 10]:
        *   **Nguồn ấm (Nến, đèn tungsten, neon ấm):** \\(1850\text{K} - 3200\text{K}\\) [5, 11].
        *   **Nguồn trung tính (Đèn LED chuẩn, daylight):** \\(5000\text{K} - 6500\text{K}\\) [5, 11].
        *   **Nguồn lạnh (Ánh trăng, đêm muộn, cyan/blue neon):** \\(7000\text{K} - 9000\text{K}\\) [5, 12].
    *   **Tách màu điện ảnh (Teal & Orange / Cool vs Warm):** Phối hợp đèn môi trường/rim lạnh (\\(7000\text{K} - 9000\text{K}\\)) với các nguồn thực tế (Practical) ấm (\\(1850\text{K} - 3800\text{K}\\)) để tạo độ tương phản sắc thái [5, 6, 13, 14].
*   **Quản lý màu sắc (Color Management - AgX):**
    *   Chuyển View Transform từ *Standard* sang **AgX** (mặc định từ Blender 4.x) [4, 6, 15]. AgX giúp các nguồn sáng Emission/Neon cường độ cao không bị gắt lệch màu mà sẽ cuộn sáng (highlight rolloff) tự nhiên về màu trắng [6].
*   **Đèn trợ sáng (Area Light) & Thể tích không khí (Volumetrics):**
    *   Đèn Area trợ sáng cần có kích thước (Size) từ \\(0.2\text{m} - 2.0\text{m}\\) để tạo vùng viền bóng mềm (penumbra) mềm mại, tránh dùng đèn Point có bán kính bằng 0 gây gắt bóng [16, 17].
    *   Khối thể tích không khí (`Principled Volume`): Đặt mật độ **Density** khoảng \\(0.025\\) và **Anisotropy** khoảng \\(0.75\\) để bắt các chùm sáng (god rays/light shafts) đâm xuyên qua sương đêm [18, 19].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Các bước thao tác giao diện:
1.  **Thiết lập không gian màu:** Vào `Render Properties` > `Color Management` > Đổi `View Transform` thành **AgX** và `Look` thành **Medium High Contrast** [4, 6, 15].
2.  **Tạo vật liệu Biển hiệu Emission (Practical):** Tạo Shader cho biển hiệu, kết nối nút `Blackbody` (đặt \\(8500\text{K}\\) cho màu xanh Cyan lạnh hoặc \\(2800\text{K}\\) cho màu cam ấm) vào cổng Color của nút `Emission`, chỉnh Strength từ \\(15 - 50\\) [5, 9, 10, 20].
3.  **Bố trí đèn Area phụ trợ & Light Linking:**
    *   Thêm đèn Area, điều chỉnh kích thước \\(1.5\text{m}\\), dùng nút `Blackbody` đặt nhiệt độ màu \\(3200\text{K}\\) để giả lập ánh sáng hắt từ cửa sổ hẻm [5, 13, 16].
    *   Trong tab `Object Properties` > `Light Linking`, kéo Collection chứa mặt đường ướt và nhân vật vào để đèn Area chỉ chiếu sáng vùng này mà không làm cháy mảng tường phía sau [21-24].
4.  **Tạo khối sương đêm (Atmospheric Fog):** Thêm một Cube bao trùm cảnh, gán chất liệu có nút `Principled Volume` nối vào cổng Volume của Output. Đặt `Density` = \\(0.025\\), `Anisotropy` = \\(0.75\\) [18, 19].

#### Đoạn Code Python `bpy` tự động hóa thiết lập:

```python
import bpy
import math

def setup_cyberpunk_night_lighting():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    
    # 1. Quản lý màu sắc AgX cho dải động cao
    scene.display_settings.display_device = 'sRGB'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'Medium High Contrast'
    
    # 2. Tạo Collection cho Light Linking
    ll_collection = bpy.data.collections.get("Street_Receivers")
    if not ll_collection:
        ll_collection = bpy.data.collections.new("Street_Receivers")
        scene.collection.children.link(ll_collection)
        
    # 3. Tạo Đèn Area Phụ trợ với nút Blackbody (Kelvin)
    light_data = bpy.data.lights.new(name="Area_Fill_Cyberpunk_Data", type='AREA')
    light_data.size = 1.5  # Kích thước 1.5m tạo penumbra mềm mại
    light_data.use_nodes = True
    
    nodes = light_data.node_tree.nodes
    links = light_data.node_tree.links
    nodes.clear()
    
    out_node = nodes.new(type='ShaderNodeOutputLight')
    emission_node = nodes.new(type='ShaderNodeEmission')
    blackbody_node = nodes.new(type='ShaderNodeBlackbody')
    
    emission_node.inputs['Strength'].default_value = 250.0
    blackbody_node.inputs['Temperature'].default_value = 3200.0  # Ấm áp (Tungsten)
    
    links.new(blackbody_node.outputs['Color'], emission_node.inputs['Color'])
    links.new(emission_node.outputs['Emission'], out_node.inputs['Surface'])
    
    light_obj = bpy.data.objects.new(name="Area_Fill_Cyberpunk", object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = (2.0, -3.0, 3.5)
    light_obj.rotation_euler = (math.radians(45), 0, math.radians(30))
    
    # Gán Light Linking cho Cycles
    if hasattr(light_obj, "light_linking"):
        light_obj.light_linking.receiver_collection = ll_collection
        
    # 4. Tạo Chất liệu Biển hiệu Neon (Practical Emission)
    neon_mat = bpy.data.materials.new(name="Neon_Sign_Material")
    neon_mat.use_nodes = True
    mat_nodes = neon_mat.node_tree.nodes
    mat_links = neon_mat.node_tree.links
    mat_nodes.clear()
    
    mat_out = mat_nodes.new(type='ShaderNodeOutputMaterial')
    mat_emission = mat_nodes.new(type='ShaderNodeEmission')
    mat_blackbody = mat_nodes.new(type='ShaderNodeBlackbody')
    
    mat_emission.inputs['Strength'].default_value = 25.0
    mat_blackbody.inputs['Temperature'].default_value = 8500.0  # Cool Cyan Neon
    
    mat_links.new(mat_blackbody.outputs['Color'], mat_emission.inputs['Color'])
    mat_links.new(mat_emission.outputs['Emission'], mat_out.inputs['Surface'])
    
    # 5. Tạo Khối thể tích không khí (Atmospheric Fog Domain)
    bpy.ops.mesh.primitive_cube_add(size=20.0, location=(0, 0, 5))
    vol_obj = bpy.context.active_object
    vol_obj.name = "Night_Atmosphere_Domain"
    vol_obj.display_type = 'WIRE'
    
    vol_mat = bpy.data.materials.new(name="Night_Fog_Material")
    vol_mat.use_nodes = True
    vol_nodes = vol_mat.node_tree.nodes
    vol_links = vol_mat.node_tree.links
    vol_nodes.clear()
    
    v_out = vol_nodes.new(type='ShaderNodeOutputMaterial')
    v_princ = vol_nodes.new(type='ShaderNodeVolumePrincipled')
    
    v_princ.inputs['Density'].default_value = 0.025
    v_princ.inputs['Anisotropy'].default_value = 0.75  # Tán xạ hướng tới camera
    
    vol_links.new(v_princ.outputs['Volume'], v_out.inputs['Volume'])
    vol_obj.data.materials.append(vol_mat)

if __name__ == "__main__":
    setup_cyberpunk_night_lighting()
``` [5, 9, 18, 19, 25]

---

### 4. Lỗi thường gặp & Cách kiểm tra

*   **Lỗi 1: Đèn bị gắt bóng hoặc để lại vệt shadow line lạ trên tường.**
    *   *Nguyên nhân:* Sử dụng Point Light có bán kính (Radius) bằng 0 hoặc đặt nguồn sáng quá sát mép tường [16, 26].
    *   *Cách khắc phục:* Đổi sang Area Light với kích thước Size từ \\(0.5\text{m} - 2.0\text{m}\\) hoặc tăng chỉ số Radius/Angle để tạo vùng viền bóng mềm tự nhiên [16, 17].
*   **Lỗi 2: Biển hiệu Neon bị mờ nhạt hoặc cháy sáng mất màu khi lên hình.**
    *   *Nguyên nhân:* Sử dụng View Transform *Standard* dẫn đến việc các màu neon có độ bão hòa cao bị gắt và đổi màu bất thường [4, 6].
    *   *Cách khắc phục:* Đảm bảo đã chuyển sang không gian màu **AgX** trong phần `Color Management` [4, 6, 15].
*   **Lỗi 3: Sương mù bị giật/nhấp nháy (Flickering Volume) trong EEVEE Next (Blender 4.2+).**
    *   *Nguyên nhân:* Số bước cắt thể tích (Volume Steps) mặc định quá thấp [27, 28].
    *   *Cách khắc phục:* Vào `Render Properties` > `Volumes`, tăng thông số **Steps** từ 64 lên 128 hoặc 256 và kích hoạt phân bố dithered [28, 29].
*   **Lỗi 4: Nhân bản vật thể rác (như Cube.001) khi Append đèn có Light Linking.**
    *   *Nguyên nhân:* Blender tự động lôi các vật thể thuộc Collection liên kết ánh sáng từ file cũ sang file mới [30-32].
    *   *Cách khắc phục:* Sử dụng script Python để gán `light_linking.receiver_collection = None` trước khi Append hoặc dùng add-on dọn dẹp liên kết thừa sau khi liên kết [25, 30, 32].

💡 Bạn có muốn tôi hỗ trợ viết tiếp một script Python để tự động thiết lập chất liệu mặt đường ướt phản xạ PBR (Wet Asphalt Material) kết hợp với hiệu ứng mưa không?
