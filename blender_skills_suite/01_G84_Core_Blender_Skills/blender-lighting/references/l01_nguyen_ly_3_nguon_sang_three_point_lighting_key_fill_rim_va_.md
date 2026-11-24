# [L01] Nguyên lý 3 nguồn sáng (Three-Point Lighting: Key, Fill, Rim) và tỷ lệ tương phản trong Blender

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

### 1. Tóm tắt Bản chất (2-3 câu)

Hệ thống chiếu sáng 3 điểm (Three-Point Lighting) là phương pháp nền tảng trong điện ảnh và đồ họa 3D, phối hợp 3 nguồn sáng (Key, Fill, Rim) để điêu khắc độ sâu ba chiều, bề mặt chất liệu và điểm nhấn thị giác trên khung hình phẳng [1-3]. Việc điều chỉnh tỷ lệ cường độ giữa đèn chính và đèn phụ (Key-to-Fill ratio) quyết định độ tương phản và thiết lập tâm trạng cảm xúc cho cảnh quay — từ tươi sáng thương mại đến kịch tính u tối [4-6]. Trong Blender, việc cụ thể hóa các nguyên lý này thành thông số kỹ thuật (Area/Sun/Spot, nút Blackbody Kelvin và kịch bản Python `bpy`) giúp đảm bảo tính chính xác về mặt vật lý, tối ưu hóa quy trình làm việc và đạt chất lượng render chuyên nghiệp [3, 7-9].

---

### 2. Nguyên lý & Thông số Chuẩn

#### Ba vị trí đèn cơ bản (Three-Point Lighting Mechanics)
* **Key Light (Đèn chính):** Là nguồn sáng định hướng chính, quyết định mức độ phơi sáng và hướng bóng đổ chủ đạo của chủ thể [10-12]. Theo quy tắc \\(45^\circ\\), đèn được đặt lệch \\(35^\circ \text{ đến } 45^\circ\\) theo chiều ngang so với trục camera-chủ thể và chúc xuống góc \\(30^\circ \text{ đến } 50^\circ\\) [11-14]. Góc đặt này mô phỏng ánh sáng tự nhiên từ trên cao, tạo ra bóng đổ chân dung kinh điển như *Rembrandt lighting* (tam giác sáng trên phần má bị che bóng) [11, 12, 15].
* **Fill Light (Đèn phụ / Đèn bù):** Được đặt đối diện với Key Light ở góc ngang \\(-30^\circ \text{ đến } -45^\circ\\) so với trục camera, độ cao gần ngang tầm mắt hoặc camera (góc chúc \\(10^\circ \text{ đến } 30^\circ\\)) [4, 13, 14, 16]. Chức năng của Fill Light là làm mềm các vùng bóng tối gắt do Key Light tạo ra mà không làm xuất hiện thêm bóng phụ thứ hai [4, 16].
* **Rim / Back Light (Đèn viền / Đèn ngược):** Đặt phía sau chủ thể, hướng ngược về phía camera ở góc ngang \\(120^\circ \text{ đến } 180^\circ\\), chúc xuống \\(45^\circ \text{ đến } 75^\circ\\) [5, 13, 16, 17]. Đèn chiếu lướt qua viền tóc, vai và thân thể để tạo ra đường viền sáng (halo/rim effect), tách rời chủ thể khỏi nền tối và tăng độ sâu không gian [5, 16, 18].

#### Tỷ lệ chiếu sáng (Key-to-Fill Ratio) & Tâm trạng cảnh phim
Tỷ lệ chiếu sáng thể hiện chênh lệch độ sáng giữa nguồn sáng chính và nguồn sáng phụ, tính theo công thức [4]:
\\[\text{Lighting Ratio} = \frac{\text{Illuminance}_{\text{Key}} + \text{Illuminance}_{\text{Fill}}}{\text{Illuminance}_{\text{Fill}}}\\]

| Tỷ lệ (Ratio) | Phong cách chiếu sáng | Đặc điểm thẩm mỹ | Ứng dụng điện ảnh & Cảnh phim |
| :--- | :--- | :--- | :--- |
| **2:1 (Thấp)** | Low contrast / High-key | Fill Light bằng 50% Key Light; bóng đổ rất mềm, ánh sáng đều, ít tương phản [5, 13, 19]. | Cảnh tươi vui, hài kịch, phim ca nhạc, quảng cáo thương mại, cảnh ban ngày ngập sáng [5, 15, 20, 21]. |
| **4:1 (Trung bình)** | Balanced / Standard | Fill Light bằng 25% Key Light; tương phản vừa phải, hình khối tự nhiên [13, 22]. | Cảnh phỏng vấn, phim truyền hình, cảnh điện ảnh tiêu chuẩn [22-24]. |
| **8:1 trở lên (Cao)** | High contrast / Low-key | Fill Light rất yếu (\\(12.5\%\\) trở xuống) hoặc tắt hẳn; bóng tối sâu, tương phản gắt (Chiaroscuro) [5, 19, 25, 26]. | Phim Noir, phim kinh dị, giật gân, bí ẩn, các cảnh tâm lý kịch tính gắt gao [5, 25-27]. |

#### Nhiệt độ màu & Chuẩn hóa Kelvin (Blackbody Calibration)
Sự kết hợp tương phản màu sắc giữa các nguồn sáng giúp tăng phân tách thị giác và độ sâu không gian [7, 28, 29]:
* **Nguồn ấm (Warm / Tungsten / Candlelight):** \\(1850\text{K} - 3800\text{K}\\) (cho màu hổ phách, vàng ấm của đèn dây tóc, nến) [7, 30, 31].
* **Nguồn trung tính (Neutral / Daylight):** \\(5000\text{K} - 6500\text{K}\\) (màu ánh sáng mặt trời ngày tròn) [7, 31].
* **Nguồn lạnh (Cool / Overcast Sky / Shadow):** \\(7000\text{K} - 9000\text{K}\\) (màu xanh trời bầu mây hoặc viền lạnh) [7, 13, 32].

*Thiết lập phối màu điện ảnh Teal-and-Orange:* Sử dụng Key Light ánh sáng ngày lạnh (\\(6500\text{K}\\)), Fill Light màu ấm (\\(3200\text{K}-3800\text{K}\\)) ở vùng bóng đổ, và Rim Light xanh lạnh (\\(8500\text{K}\\)) để cắt viền chủ thể [13, 30, 32, 33].

#### Định luật suy giảm ánh sáng (Inverse Square Law)
Cường độ sáng suy giảm theo bình phương khoảng cách: \\(E = \frac{P}{4\pi d^2}\\) [34]. Do đó, việc thiết lập tỉ lệ scene thực tế trong Blender (\\(1\text{ unit} = 1\text{ meter}\\)) là bắt buộc để sự suy giảm vật lý của Area, Spot, Point diễn ra chính xác [34].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Thao tác thủ công trong giao diện Blender
1. **Thiết lập Area Light (Đèn diện tích - Khuyên dùng cho Key/Fill):**
   * Trong thuộc tính Light Data, chọn `Shape` (`SQUARE` hoặc `RECTANGLE`) [35, 36].
   * Kích thước `Size` (\\(0.5\text{m} - 2.0\text{m}\\)) điều khiển độ nhòe vùng biên bóng (penumbra) [35, 37, 38].
   * Góc tỏa `Spread`: Mặc định \\(180^\circ\\) dùng cho Fill Light mềm; thu hẹp xuống \\(40^\circ - 80^\circ\\) để định hướng chùm sáng tập trung như Spotlight cho Key Light [39, 40].
2. **Thiết lập Sun Light (Đèn mặt trời):**
   * Đặt `Power` khoảng \\(1.0\text{W} - 5.0\text{W}\\) [41].
   * Đặt `Angle` = \\(0.526^\circ\\) để tái tạo bóng đổ mềm tự nhiên khớp với kích thước đĩa mặt trời thực tế [37, 38, 42].
3. **Thiết lập Spot Light (Đèn tụ quang - Khuyên dùng cho Rim Light):**
   * Chỉnh `Spot Size` (góc nón \\(= 45^\circ\\)), `Spot Blend` (độ mềm mép nón \\(= 0.5\\)), và `Radius` (\\(0.2\text{m} - 0.5\text{m}\\)) để bóng viền mềm mại [35-37, 43].
4. **Gán nút Blackbody cho màu đèn:**
   * Trong panel Light Data, tích chọn `Use Nodes` [30, 36].
   * Vào Shader Editor, thêm nút `ShaderNodeBlackbody` (`Shift + A` > Color > Blackbody) [7, 30, 44].
   * Nối đầu ra `Color` của Blackbody vào đầu vào `Color` của nút `Emission`, nhập thông số Kelvin tương ứng (VD: 5500K cho Key, 3200K cho Fill, 8500K cho Rim) [7, 30, 36].
5. **Khóa hướng nhìn đèn (Track To Constraint):**
   * Tạo một Empty tại vị trí chủ thể [8, 36].
   * Gán constraint `Track To` cho từng đèn, chọn Target là Empty, thiết lập `Track Axis` = `-Z` và `Up` = `Y` để các đèn luôn tự động chĩa vào chủ thể [36].

#### Kịch bản Python `bpy` tự động hóa
Đoạn mã bên dưới tự động khởi tạo hệ thống 3 điểm sáng chuẩn hóa kèm nút Blackbody, constraint định vị, và vùng không khí sương mù (Atmospheric Volume Domain) [36]:

```python
import bpy
import math

def create_cinematic_rig(subject_name="Hero_Target", target_location=(0.0, 0.0, 1.0)):
    scene = bpy.context.scene
    
    # 1. Tạo Empty định vị tại tâm chủ thể
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=target_location)
    target_obj = bpy.context.active_object
    target_obj.name = subject_name
    
    # 2. Định nghĩa thông số tọa độ và quang học cho hệ thống 3 đèn
    light_specs = {
        "Key_Light": {
            "type": 'AREA',
            "distance": 4.5,
            "yaw": math.radians(45.0),
            "pitch": math.radians(35.0),
            "power": 350.0,
            "kelvin": 5500.0,
            "size": 1.2
        },
        "Fill_Light": {
            "type": 'AREA',
            "distance": 5.0,
            "yaw": math.radians(-40.0),
            "pitch": math.radians(15.0),
            "power": 120.0,
            "kelvin": 3200.0,
            "size": 2.0
        },
        "Rim_Light": {
            "type": 'SPOT',
            "distance": 3.8,
            "yaw": math.radians(150.0),
            "pitch": math.radians(60.0),
            "power": 500.0,
            "kelvin": 8500.0,
            "radius": 0.3
        }
    }
    
    # Tạo Collection chứa các vật thể nhận ánh sáng (Light Linking)
    ll_collection = bpy.data.collections.get("Light_Linked_Receivers")
    if not ll_collection:
        ll_collection = bpy.data.collections.new("Light_Linked_Receivers")
        scene.collection.children.link(ll_collection)
        
    for light_name, spec in light_specs.items():
        # Chuyển đổi tọa độ cầu sang tọa độ Đề-các 3D quanh chủ thể
        x_off = spec["distance"] * math.sin(spec["yaw"]) * math.cos(spec["pitch"])
        y_off = spec["distance"] * math.cos(spec["yaw"]) * math.cos(spec["pitch"])
        z_off = spec["distance"] * math.sin(spec["pitch"])
        
        light_loc = (
            target_location + x_off,
            target_location[45] - y_off,
            target_location[46] + z_off
        )
        
        # Khởi tạo đối tượng đèn trong Blender
        light_data = bpy.data.lights.new(name=f"{light_name}_Data", type=spec["type"])
        light_obj = bpy.data.objects.new(name=light_name, object_data=light_data)
        scene.collection.objects.link(light_obj)
        light_obj.location = light_loc
        
        # Thiết lập hình học vật lý của đèn
        if spec["type"] == 'AREA':
            light_data.size = spec["size"]
            light_data.shape = 'SQUARE'
        elif spec["type"] == 'SPOT':
            light_data.shadow_soft_size = spec["radius"]
            light_data.spot_size = math.radians(45.0)
            light_data.spot_blend = 0.5
            
        # Thêm constraint Track To để đèn luôn nhắm vào Empty
        track_con = light_obj.constraints.new(type='TRACK_TO')
        track_con.target = target_obj
        track_con.track_axis = 'TRACK_NEGATIVE_Z'
        track_con.up_axis = 'UP_Y'
        
        # Cấu hình Shader Node cây đèn với nút Blackbody
        light_data.use_nodes = True
        nodes = light_data.node_tree.nodes
        links = light_data.node_tree.links
        
        emission_node = nodes.get("Emission") or next((n for n in nodes if n.type == 'EMISSION'), None)
        
        if emission_node:
            emission_node.inputs['Strength'].default_value = spec["power"]
            
            blackbody_node = nodes.new(type="ShaderNodeBlackbody")
            blackbody_node.inputs.default_value = spec["kelvin"]
            blackbody_node.location = (-200, 300)
            
            links.new(blackbody_node.outputs, emission_node.inputs['Color'])
            
        # Gán Light Linking Collection (Cycles 4.x)
        if hasattr(light_obj, "light_linking"):
            light_obj.light_linking.receiver_collection = ll_collection

    # 3. Tạo môi trường thể tích sương mù (Atmospheric Volume Domain)
    bpy.ops.mesh.primitive_cube_add(size=15.0, location=target_location)
    vol_obj = bpy.context.active_object
    vol_obj.name = "Atmospheric_Volume_Domain"
    vol_obj.display_type = 'WIRE'
    
    vol_mat = bpy.data.materials.new(name="Atmospheric_Volume_Material")
    vol_mat.use_nodes = True
    vol_nodes = vol_mat.node_tree.nodes
    vol_links = vol_mat.node_tree.links
    vol_nodes.clear()
    
    out_node = vol_nodes.new(type='ShaderNodeOutputMaterial')
    volume_node = vol_nodes.new(type='ShaderNodeVolumePrincipled')
    volume_node.inputs['Density'].default_value = 0.025
    volume_node.inputs['Anisotropy'].default_value = 0.75
    
    vol_links.new(volume_node.outputs['Volume'], out_node.inputs['Volume'])
    vol_obj.data.materials.append(vol_mat)

if __name__ == "__main__":
    create_cinematic_rig()
``` [36]

---

### 4. Lỗi thường gặp & Cách kiểm tra

1. **Cháy sáng / Mất chi tiết (Overexposure / Clipping Highlights):**
   * *Nguyên nhân:* Key Light năng lượng quá lớn hoặc đặt quá gần chủ thể [34, 47-49].
   * *Kiểm tra & Khắc phục:* Chuyển Viewport sang chế độ **False Color** trong `Color Management` (hoặc kiểm tra Histogram) để phát hiện các vùng xám xịt bị quá nhiệt [47, 50, 51]. Hệ quản lý màu **AgX** trong Blender 4.x giúp xả sáng tự nhiên (desaturate về trắng mà không làm méo màu) [28].
2. **Cường độ Key Light và Fill Light bằng nhau (Bẹt khung hình):**
   * *Nguyên nhân:* Đặt tỷ lệ Key-to-Fill xấp xỉ 1:1 làm triệt tiêu bóng đổ, khiến chủ thể bị bẹt và mất khối 3D [19, 52, 53].
   * *Khắc phục:* Giảm cường độ Fill Light xuống còn \\(25\% - 50\%\\) so với Key Light để duy trì độ sâu [4, 13, 22].
3. **Bỏ qua hoặc đặt sai Rim Light (Chủ thể chìm vào nền):**
   * *Nguyên nhân:* Tắt Rim Light khiến viền chủ thể bị trùng màu với background tối phía sau [5, 47, 52].
   * *Kiểm tra:* Tắt tạm thời Key và Fill Light để kiểm tra riêng Rim Light; đảm bảo đường viền sáng (rim halo) chạy mảnh và rõ quanh viền vai/tóc chủ thể [5, 16, 32, 54].
4. **Kích thước nguồn sáng bằng 0 (Zero-Radius Point Light / Bóng quá gắt):**
   * *Nguyên nhân:* Giữ `Radius` = 0m trên đền Point/Spot làm cho ranh giới bóng đổ gắt cứng, phi thực tế [37, 38, 55].
   * *Khắc phục:* Chuyển sang Area Light hoặc tăng `Radius` của Spot/Point lên \\(0.2\text{m} - 0.5\text{m}\\) (hoặc `Angle` mặt trời \\(= 0.526^\circ\\)) để có vùng bóng chuyển nhòe tự nhiên [37, 42, 55].
5. **Lỗi Append đèn bị kéo theo Object rác (Duplicate Objects khi dùng Light Linking):**
   * *Nguyên nhân:* Khi Append bộ đèn có Light Linking từ file `.blend` khác, Blender tự động Append luôn các Mesh thuộc Collection nhận sáng, làm xuất hiện các bản sao trùng lặp như `Cube.001` [56-58].
   * *Khắc phục:* Sử dụng kịch bản gán `receiver_collection = None` trước khi append [58, 59], hoặc chạy script xóa các object phi-đèn trùng lặp sau khi append [57, 58].
6. **Lỗi nhấp nháy sương mù thể tích trong EEVEE Next (Volumetric Flickering):**
   * *Nguyên nhân:* Thuật toán chia lát voxel (voxel slicing) trong EEVEE Next gây ra hiện tượng giật/sọc khi camera di chuyển [60-63].
   * *Khắc phục:* Trong Render Properties > Volumes, bật **Dithered Volumes** và tăng số bước **Steps** từ \\(64\\) lên \\(128\\) hoặc \\(256\\) để làm mịn nón thể tích và triệt tiêu giật hình [62-64].

💡 *Bạn có muốn tôi hỗ trợ viết tiếp một script Python để tự động tạo View Layers giúp chuyển đổi nhanh giữa các thiết lập chiếu sáng Ban ngày (Day), Ban đêm (Night) và Studio (Beauty Shot) không?*
