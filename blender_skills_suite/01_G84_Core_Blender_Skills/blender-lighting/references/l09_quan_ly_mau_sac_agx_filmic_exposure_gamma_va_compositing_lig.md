# [L09] Quản lý màu sắc AgX / Filmic, Exposure, Gamma và Compositing Light Groups

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

Dưới đây là giải thích chi tiết về cách thiết lập **Color Management** và phân tách **Light Groups** trong Blender để làm chủ công đoạn hậu kỳ ánh sáng mà không cần render lại.

---

### 1. Tóm tắt Bản chất (2-3 câu)
Thiết lập **Color Management** (với View Transform hiện đại như AgX hoặc Filmic) kết hợp với **tách Light Groups trong Render Passes** là phương pháp chuẩn hóa quy trình ánh sáng tuyến tính (Linear Color Workflow) và phân tách đóng góp quang học của từng nguồn sáng riêng biệt [1-4]. Kỹ thuật này giải phóng artist khỏi việc phải render lại toàn bộ cảnh 3D khi muốn tinh chỉnh ánh sáng, cho phép can thiệp linh hoạt về cường độ, màu sắc và hiệu ứng trong giai đoạn hậu kỳ (Compositor) [4-6].

---

### 2. Nguyên lý & Thông số Chuẩn

* **Quản lý màu sắc (Color Management)**:
  * **View Transform**:
    * **AgX** (mặc định từ Blender 4.x): Sử dụng kỹ thuật *spectral upsampling* giúp xử lý hạ tông vùng sáng (*highlight rolloff*) mượt mà, giúp các vùng ánh sáng bão hòa cao không bị xê dịch sắc độ (*hue shift*) hay cháy bệt [1, 2, 7].
    * **Filmic**: Chuẩn tối ưu cho các phiên bản Blender trước 4.x, vượt trội so với chế độ **Standard** vốn hay gây cháy sáng bệt [1, 2].
  * **Look (Tương phản)**: Thiết lập mức độ tương phản trực quan (ví dụ: *None* cho ảnh trung tính, *Medium High Contrast* hoặc *High Contrast* để tạo độ khối nổi bật) [1].
  * **Exposure (Phơi sáng)**: Điều chỉnh độ sáng tổng thể cảnh theo đơn vị EV (Stop) thay vì tăng cường độ đèn quá mức làm xáo trộn tính chất vật lý của dải sáng [1, 8].
  * **Thang nhiệt độ màu Kelvin (Node Blackbody)** [9-11]:
    * **Nguồn ấm (Warm / Tungsten / Nến)**: \\(1850\text{K} - 3200\text{K}\\) (tạo tone màu vàng hổ phách, ấm áp) [9, 12, 13].
    * **Nguồn trung tính (Neutral / Daylight)**: \\(5000\text{K} - 6500\text{K}\\) (chuẩn White Balance ban ngày) [9, 11, 12].
    * **Nguồn lạnh (Cool / Trời âm u / Bóng râm)**: \\(7000\text{K} - 9000\text{K}\\) (tone xanh mát của bầu trời) [9].

* **Light Groups & Render Passes**:
  * Phân tách năng lượng chiếu sáng trực tiếp và gián tiếp của từng nguồn sáng (Key Light, Fill Light, Rim Light, Environment HDRI) thành các kênh thông tin (Passes) riêng biệt [4-6, 14].
  * Trong Compositor, các kênh Light Groups này được tổng hợp lại bằng phép cộng tuyến tính (Mix Node / Add Mode), cho phép thay đổi màu sắc, điều chỉnh phơi sáng riêng cho từng đèn, hoặc thêm hiệu ứng Bloom/Glare mà không cần tính toán ray-tracing lại [5, 6, 15, 16].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác giao diện (UI Workflow)
1. **Cấu hình Color Management**: Vào tab **Render Properties** \\(\rightarrow\\) **Color Management** \\(\rightarrow\\) Đổi **View Transform** thành **AgX** (hoặc Filmic), chọn **Look** là `Medium High Contrast`, tinh chỉnh **Exposure** [1].
2. **Gán Light Groups cho Đèn**: Chọn từng nguồn sáng \\(\rightarrow\\) Vào **Object Data Properties** (hoặc **Object Properties**) \\(\rightarrow\\) Tìm mục **Light Group** và nhập/gán tên nhóm tương ứng (ví dụ: `"Key_Group"`, `"Fill_Group"`, `"Rim_Group"`) [17].
3. **Kích hoạt Passes**: Vào tab **View Layer Properties** \\(\rightarrow\\) Mở mục **Passes** \\(\rightarrow\\) **Light Groups** và thêm/bật các nhóm pass vừa gán.
4. **Tổng hợp trong Compositor**: Mở tab **Compositing** \\(\rightarrow\\) Bật `Use Nodes`. Nối các đầu ra của từng Light Group qua node **Mix Color (chế độ Add)** để ghép thành hình ảnh hoàn chỉnh.

#### B. Code Python (`bpy`) tự động hóa
```python
import bpy

def setup_color_management_and_light_groups():
    scene = bpy.context.scene
    
    # 1. Cấu hình Color Management chuẩn (AgX, Look, Exposure)
    scene.display_settings.display_device = 'sRGB'
    scene.view_settings.view_transform = 'AgX'  # Sử dụng AgX cho Blender 4.x+
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = 0.0
    
    # 2. Khởi tạo các Light Groups trên View Layer
    view_layer = bpy.context.view_layer
    groups_to_create = ["Key_Group", "Fill_Group", "Rim_Group", "Env_Group"]
    
    for g_name in groups_to_create:
        if hasattr(view_layer, "lightgroups") and g_name not in view_layer.lightgroups:
            view_layer.lightgroups.add(name=g_name)
            
    # 3. Gán các đèn trong cảnh vào Light Group tương ứng
    light_mapping = {
        "Key_Light": "Key_Group",
        "Fill_Light": "Fill_Group",
        "Rim_Light": "Rim_Group",
        "Sun": "Env_Group"
    }
    
    for obj_name, group_name in light_mapping.items():
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
            if obj.type == 'LIGHT':
                obj.lightgroup = group_name

    # 4. Kích hoạt Compositor Nodes
    scene.use_nodes = True
    print("Đã thiết lập thành công Color Management và Light Groups!")

setup_color_management_and_light_groups()
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Sử dụng View Transform "Standard" gây cháy sáng**: Dùng chế độ *Standard* làm mất chi tiết vùng sáng gắt (*clipping*) và xê dịch sắc độ [1, 2]. 
  * *Cách kiểm tra*: Bật chế độ hiển thị **False Color** hoặc xem **Histogram** trong tab Color Management để kiểm tra các vùng bị vượt ngưỡng sáng [18].
* **Quá nhiệt node Blackbody (Overdriving Blackbody)**: Đẩy công suất node Blackbody lên mức quá cao làm giá trị màu RGB vượt \\(1.0\\), khiến AgX tự động hạ bão hòa màu về xám/trắng nhạt [19-21]. 
  * *Cách khắc phục*: Giữ công suất đèn ở mức vật lý hợp lý và điều chỉnh độ sáng tổng thể thông qua slider **Exposure** [1, 8].
* **Xuất sai định dạng ảnh hậu kỳ (Mất dải động HDR)**: Xuất Render Passes ra file 8-bit PNG/JPEG làm mất thông tin dải động rộng, gây gãy dải màu (*color banding*) khi trộn kênh trong Compositor [14, 22, 23]. 
  * *Cách khắc phục*: Luôn xuất định dạng **OpenEXR (16-bit Float hoặc 32-bit Float)** ở **Linear Color Space** để đảm bảo nguyên vẹn dữ liệu quang học [14, 22, 23].
* **Lỗi rò rỉ hoặc trùng lặp vật thể khi Append dàn đèn**: Khi append dàn đèn có cài đặt Light Linking / Light Groups giữa các file dự án, Blender có thể tự động nhân bản cả các vật thể liên kết (tạo ra `Cube.001`, `Model.001`) [24-27]. 
  * *Cách khắc phục*: Sử dụng script Python để dọn dẹp thuộc tính `light_linking` về `None` trước khi append [25, 28].

---

💡 **Gợi ý tiếp theo**: Nếu bạn muốn đi sâu hơn vào thiết lập ánh sáng nghệ thuật, ta có thể xây dựng một sơ đồ ánh sáng 3 điểm (Key, Fill, Rim) chuẩn điện ảnh cho một phân cảnh cụ thể trong Blender.
