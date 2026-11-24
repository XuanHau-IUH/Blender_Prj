# [L02] Nhiệt độ màu (Kelvin) và thiết lập ánh sáng mặt trời vật lý (Nishita Sky Texture & Sun Light)

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

Dưới đây là tổng hợp bài học kỹ thuật về **Nhiệt độ màu (Kelvin / Blackbody)** theo các khung giờ trong ngày và cách **đồng bộ Sun Light với Sky Texture** trong Blender, trích xuất dựa trên tài liệu trong sổ tay của bạn.

---

### 1. Tóm tắt Bản chất (2-3 câu)
Kiến thức về **Nhiệt độ màu (Kelvin / Blackbody)** và **đồng bộ Sun Light với Sky Texture** là nền tảng cốt lõi trong chiếu sáng 3D vật lý (Physically Based Lighting) [1-3]. Việc thiết lập đúng dải quang phổ Kelvin cho từng thời điểm trong ngày kết hợp với sự đồng bộ chính xác giữa nguồn sáng trực tiếp (Sun Light) và ánh sáng môi trường (Sky Texture) đảm bảo màu sắc bóng đổ, hướng nắng và độ tương phản tự nhiên, giúp tác phẩm đạt chất lượng điện ảnh và độ chân thực tối đa [1, 3, 4].

---

### 2. Nguyên lý & Thông số Chuẩn

#### **A. Bảng thông số Nhiệt độ màu Kelvin (Blackbody) theo khung giờ**
Chuyển đổi nhiệt độ Kelvin trực tiếp sang không gian màu RGB thông qua node **Blackbody** giúp tái tạo nguồn sáng thực tế thay vì gán giá trị RGB ngẫu nhiên [1, 5]:

* **Bình minh (Sunrise / Dawn):** **\\(1850\text{K} - 3200\text{K}\\)**  
  * *Đặc điểm:* Nguồn sáng ấm, ngả sắc hổ phách và vàng cam gắt (amber / golden-yellow) do ánh sáng đi qua tầng khí quyển dày [1, 2].
* **Giờ vàng (Golden Hour / Hoàng hôn / Nắng chiều tà):** **\\(2000\text{K} - 4500\text{K}\\)**  
  * *Đặc điểm:* Ánh nắng dịu ấm, tạo góc chiếu thấp với bóng đổ dài và viền bóng mềm [1, 6, 7].
* **Giữa trưa (Midday / Direct Sun / Standard Daylight):** **\\(5000\text{K} - 6500\text{K}\\)**  
  * *Đặc điểm:* Ánh sáng trắng trung tính chuẩn (Daylight White Balance). Ánh nắng trưa trực tiếp thường đạt từ \\(5000\text{K}\\) đến \\(5400\text{K}\\), khớp với chuẩn cân bằng trắng của ống kính [1, 2, 7].
* **Chạng vạng & Bóng râm (Blue Hour / Dusk / Overcast Sky):** **\\(7000\text{K} - 9000\text{K}+\\)**  
  * *Đặc điểm:* Tông xanh mát lạnh (cool, sky-tinted blues). Lúc này mặt trời đã lặn hoặc bị che khuất, ánh sáng chủ yếu là phản xạ tán xạ từ bầu trời khí quyển [1, 8].

#### **B. Quy tắc Vật lý & Cấu hình Sun Light chuẩn**
* **Góc đường kính Mặt trời (`Sun Angle`):** Đặt chính xác **\\(0.526^\circ\\)** (đây là góc bán kính vật lý thực tế của đĩa mặt trời chiếu xuống Trái Đất) [9, 10]. Điều này quyết định vùng viền mờ của bóng đổ (penumbra) và tạo hiệu ứng **Contact Hardening** (bóng gắt ở chân đối tượng và mềm dần ra xa) [10, 11].
* **Quy tắc Nghịch đảo Bình phương Khoảng cách (Inverse Square Law):** Đèn suy giảm theo công thức \\(E = \frac{P}{4 \pi d^2}\\) [12, 13]. Do đó, bắt buộc phải dựng file theo đúng tỷ lệ thực tế (\\(1\text{ unit} = 1\text{ meter}\\)) để các hiệu ứng phân rã ánh sáng và sương mù khí quyển (Volumetric) hoạt động chính xác [12, 14].
* **Tương phản nhiệt độ màu (Warm/Cool Separation):** Phối hợp giữa đèn chính mang sắc Daylight (\\(5500\text{K}-6500\text{K}\\)) và đèn phụ/bầu trời Tungsten hoặc Cool Sky (\\(3200\text{K}\\) / \\(7500\text{K}-9000\text{K}\\)) để tạo chiều sâu màu sắc điện ảnh (Teal & Orange split) [1, 15, 16].
* **Quản lý màu AgX (Blender 4.x):** Giúp xử lý các vùng ánh sáng rực rỡ bão hòa tự nhiên xả về sắc trắng ở vùng highlight thay vì bị lệch hệ màu (hue shift) như các hệ thống cũ [17].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### **A. Hướng dẫn thao tác thủ công (GUI)**
1. **Thiết lập World Sky Texture:**
   * Trong cửa sổ **Shader Editor**, chuyển sang chế độ **World**.
   * Thêm node **Sky Texture** (chọn model *Nishita* cho bầu trời vật lý) và nối cổng `Color` vào node `Background` [18].
2. **Đồng bộ hướng chiếu của Sun Light:**
   * Thêm một đèn **Sun Light** vào cảnh 3D (`Shift + A > Light > Sun`).
   * Sử dụng Add-on **Sun Position** tích hợp sẵn trong Blender (*Edit > Preferences > Add-ons > Sun Position*) và chọn ánh xạ trực tiếp đối tượng `Sun Light` với thuộc tính của node `Sky Texture`.
   * *Mẹo xoay thủ công:* Bật Node Wrangler (`Ctrl + T`) trên Environment Texture để điều chỉnh góc `Z-Rotation` sao cho đĩa mặt trời trên môi trường trùng khớp tuyệt đối với hướng đổ bóng của đối tượng Sun Light [4, 19].
3. **Gán node Blackbody cho Sun Light:**
   * Chọn `Sun Light` > thuộc tính **Data** > chọn **Use Nodes** [5, 15].
   * Trong Node Tree của đèn, thêm node **Blackbody** (`ShaderNodeBlackbody`), gán giá trị Kelvin tương ứng với khung giờ (ví dụ: \\(5500\text{K}\\)) và nối cổng `Color` vào cổng `Color` của node **Emission** [1, 5].
   * Đặt thuộc tính **Angle** của Sun Light thành **\\(0.526^\circ\\)** [9, 10].

---

#### **B. Đoạn mã Tự động hóa bằng Python (`bpy`)**
Đoạn script chuẩn sản xuất dưới đây tự động khởi tạo Sun Light gán node Blackbody, thiết lập thông số góc mặt trời vật lý và kết nối hệ thống Nishita Sky Texture [5]:

```python
import bpy
import math

def setup_sun_and_nishita_sky(kelvin_temp=5500.0, sun_power=1000.0, sun_angle_deg=0.526):
    scene = bpy.context.scene
    
    # 1. Khởi tạo đối tượng Sun Light
    sun_data = bpy.data.lights.new(name="Physic_Sun_Data", type='SUN')
    sun_obj = bpy.data.objects.new(name="Physic_Sun", object_data=sun_data)
    scene.collection.objects.link(sun_obj)
    
    # Đặt hướng chiếu (Góc Euler: Pitch & Yaw)
    sun_obj.rotation_euler = (math.radians(45.0), 0.0, math.radians(30.0))
    
    # Thiết lập góc Sun Angle vật lý cho viền bóng mềm tự nhiên (0.526 độ)
    sun_data.angle = math.radians(sun_angle_deg)
    
    # 2. Tạo Shader Node cho Sun Light sử dụng Kelvin Blackbody
    sun_data.use_nodes = True
    nodes = sun_data.node_tree.nodes
    links = sun_data.node_tree.links
    
    emission_node = nodes.get("Emission") or next((n for n in nodes if n.type == 'EMISSION'), None)
    if emission_node:
        emission_node.inputs['Strength'].default_value = sun_power
        
        # Thêm node Blackbody để tính toán phổ màu chuẩn Kelvin
        blackbody_node = nodes.new(type="ShaderNodeBlackbody")
        blackbody_node.inputs.default_value = kelvin_temp
        blackbody_node.location = (-220, 200)
        
        links.new(blackbody_node.outputs['Color'], emission_node.inputs['Color'])
        
    # 3. Khởi tạo và thiết lập Nishita Sky Texture trong World Shader
    world = scene.world or bpy.data.worlds.new("Nishita_Sky_World")
    scene.world = world
    world.use_nodes = True
    
    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links
    w_nodes.clear()
    
    w_output = w_nodes.new(type='ShaderNodeOutputWorld')
    background = w_nodes.new(type='ShaderNodeBackground')
    sky_texture = w_nodes.new(type='ShaderNodeTexSky')
    
    # Chuyển kiểu Bầu trời sang mô hình Nishita
    if hasattr(sky_texture, 'sky_type'):
        sky_texture.sky_type = 'NISHITA'
    
    # Sắp xếp vị trí và nối dây node
    sky_texture.location = (-300, 0)
    background.location = (0, 0)
    w_output.location = (200, 0)
    
    w_links.new(sky_texture.outputs['Color'], background.inputs['Color'])
    w_links.new(background.outputs['Background'], w_output.inputs['Surface'])
    
    print(f"-> Đã thiết lập thành công Sun Light ({kelvin_temp}K) đồng bộ với Nishita Sky Texture.")

# Chạy thiết lập với nguồn sáng ban ngày 5500K
if __name__ == "__main__":
    setup_sun_and_nishita_sky(kelvin_temp=5500.0, sun_power=1000.0)
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1. **Lỗi để Sun Angle = \\(0^\circ\\) (hoặc dùng Point Light bán kính \\(0\text{m}\\)):**
   * *Hậu quả:* Tạo ra bóng đổ sắc gắt phi thực tế như máy cắt kim loại, mất đi độ chuyển mờ tự nhiên (penumbra) [10, 11, 20].
   * *Cách khắc phục:* Luôn kiểm tra và cài đặt `Angle` của Sun Light về mức **\\(0.526^\circ\\)** [9, 10].
2. **Lỗi bất đồng bộ hướng nắng giữa Background Sky và Sun Light:**
   * *Hậu quả:* Đĩa mặt trời trên ảnh nền hiển thị một góc nhưng bóng đổ của vật thể lại đâm ra hướng khác, làm suy giảm tính thực tế của khung cảnh [4].
   * *Cách khắc phục:* Kiểm tra qua Viewport Shading, căn chỉnh tham số `Sun Elevation` và `Sun Rotation` trên Nishita Sky khớp hoàn toàn với góc xoay Transform Euler của nguồn `Sun Light` [4, 19].
3. **Sử dụng màu RGB tùy chỉnh thay vì Node Blackbody:**
   * *Hậu quả:* Màu sắc ánh sáng bị thiên lệch, không tuân theo dải phổ bức xạ nhiệt thực tế, dễ gây chói hoặc sai lệch khi hòa trộn màu [1, 5].
   * *Cách khắc phục:* Luôn bật `Use Nodes` trên Sun Light và dùng node `Blackbody` nhập con số Kelvin chính xác [1, 5, 15].
4. **Sai lệch tỷ lệ mô hình 3D (Scene Scale):**
   * *Hậu quả:* Quy tắc Inverse Square Law (\\(E = \frac{P}{4\pi d^2}\\)) tính toán sai độ suy giảm ánh sáng làm cho bóng đổ và ánh sáng môi trường sương mù (Volumetric Fog) bị quá dày hoặc quá nhạt [12-14].
   * *Cách khắc phục:* Đảm bảo kích thước vật thể chuẩn tỷ lệ thực tế (\\(1\text{ unit} = 1\text{ meter}\\)) [12].

---
*Bạn có muốn khám phá thêm về cách phối hợp ánh sáng ba điểm (Three-Point Lighting) hoặc kỹ thuật điều chỉnh dải sương mù Volumetric Fog cho các khung cảnh ngoại thất không?*
