---
name: blender-lighting
description: Kỹ năng Thiết lập Ánh sáng & Khí quyển (Lighting & Atmosphere) trong Blender 5.1 cho Gate 84. Bao gồm chiếu sáng vật lý (Sun, Area, Spot, Nishita Sky), nhiệt độ màu Kelvin, sương mù thể tích (Volumetrics / God Rays), Light Linking, và chiếu sáng hẻm đô thị Việt Nam. Được bồi đắp tự động mỗi 9h sáng từ sổ NotebookLM NB_Lighting_Atmosphere.
---

# Kỹ năng Blender: Ánh sáng & Khí quyển (`blender-lighting`)

> **Nguồn tri thức gốc:** Sổ NotebookLM `NB_Lighting_Atmosphere` (29 nguồn tài liệu)  
> **Cập nhật tự động:** 09:00 sáng hàng ngày (3 bài học/ngày từ Cơ bản → Nâng cao)  
> **Công cụ MCP liên kết:** `execute_blender_code` (Blender MCP), `light_physical_daylight`, `render_cycles_pathtracer`, `render_eevee_next`

---

## 1. Mục đích & Khi nào sử dụng
Kỹ năng này giúp đọc hiểu và thực thi toàn bộ quy trình **đánh sáng điện ảnh (Cinematic Lighting)** và **tạo bầu khí quyển (Atmosphere / Volumetrics)** trong Blender bằng cả thao tác node lẫn code Python `bpy`:
- Giả lập ánh sáng tự nhiên theo giờ (Bình minh, Nắng gắt Sài Gòn, Hoàng hôn Golden Hour, Đêm đèn đường/Neon).
- Thiết lập hệ thống 3 nguồn sáng (Key / Fill / Rim) với tỷ lệ tương phản chuẩn điện ảnh.
- Tạo chiều sâu không khí bằng sương mù thể tích (`Principled Volume`), tia nắng xuyên khe hẹp (`God Rays`).
- Tách lớp sáng-tối (Chiaroscuro) và dùng `Light Linking` để làm nổi bật nhân vật mà không làm cháy sáng tường hẻm.

---

## 2. Bảng Thông Số Vàng (Quick Reference cho Blender `bpy`)

| Bối cảnh / Hiệu ứng | Loại đèn / Shader | Nhiệt độ màu (Kelvin) / RGB | Cường độ (`energy`) & Kích thước | Ghi chú thực chiến |
| :--- | :--- | :--- | :--- | :--- |
| **Nắng trưa Sài Gòn** | `SUN` + `Nishita Sky` | `5500K – 6000K` (Trắng hơi vàng) | `energy = 3.0 – 5.0`, `angle = 0.53°` | Bóng đổ sắc nét, kết hợp Bounce Light dưới mái hiên |
| **Giờ vàng (Golden Hour)** | `SUN` (`Sun Elevation ~ 8°–15°`) | `3200K – 3800K` (Cam ấm) | `energy = 1.5 – 2.5`, `angle = 2.0° – 4.0°` | Tăng `Ozone` và `Dust` trong Nishita Sky |
| **Chạng vạng / Đêm xanh** | `World Sky` / `AREA` lớn trên cao | `6500K – 8500K` (Xanh lạnh) | `energy = 0.2 – 0.8`, `size = 10m+` | Làm nền tối lạnh để tôn đèn vàng trong nhà/biển hiệu |
| **Đèn hẻm / Đèn dây tóc** | `POINT` hoặc `AREA` nhỏ | `2700K – 3000K` (Vàng ấm) | `energy = 30W – 150W`, `radius = 0.05m – 0.2m` | Bật `Multiple Importance` để giảm hạt noise |
| **Sương mù / Khói bếp nhẹ** | `Principled Volume` (Cube bao cảnh) | Màu trắng ngà hoặc xanh xám nhạt | `Density = 0.005 – 0.02`, `Anisotropy = 0.6 – 0.8` | `Anisotropy > 0.5` giúp tia nắng (God Rays) hiện rõ trước ống kính |

---

## 3. Mẫu Code Python (`bpy`) Chuẩn Hóa

### 3.1. Tạo hệ thống 3 đèn (Key - Fill - Rim) hướng vào nhân vật
```python
import bpy
import mathutils

def setup_three_point_lighting(target_loc=(0.0, 0.0, 1.5), key_energy=250.0, ratio_key_fill=4.0):
    """
    Tạo bộ 3 đèn Key, Fill, Rim tự động xoay hướng vào tọa độ chủ thể (target_loc).
    ratio_key_fill = 2.0 (High-key tươi sáng), 4.0 (Tự nhiên), 8.0 (Low-key kịch tính).
    """
    target = mathutils.Vector(target_loc)
    specs = [
        ("LGT_Key",  target + mathutils.Vector((2.2, -2.0, 2.2)), key_energy, (1.0, 0.94, 0.86), 1.2),
        ("LGT_Fill", target + mathutils.Vector((-2.5, -1.8, 1.6)), key_energy / ratio_key_fill, (0.82, 0.90, 1.0), 2.5),
        ("LGT_Rim",  target + mathutils.Vector((-0.8, 2.2, 2.4)), key_energy * 0.8, (1.0, 0.98, 0.92), 0.6),
    ]
    created = []
    for name, loc, energy, color, size in specs:
        light_data = bpy.data.lights.new(name=name, type='AREA')
        light_data.energy = energy
        light_data.color = color
        light_data.size = size
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = loc
        # Xoay đèn nhìn thẳng vào chủ thể
        direction = target - loc
        light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        created.append(light_obj)
    return created
```

### 3.2. Tạo khối khí quyển sương mù thể tích (Volumetric Fog Box)
```python
import bpy

def create_volumetric_fog_box(center=(0, 0, 4), scale=(20, 20, 8), density=0.01, anisotropy=0.7):
    """Tạo hộp sương mù thể tích bao quanh khu vực diễn xuất để bắt tia sáng God Rays."""
    bpy.ops.mesh.primitive_cube_add(location=center)
    fog_box = bpy.context.active_object
    fog_box.name = "ENV_Atmosphere_Volume"
    fog_box.scale = scale
    fog_box.display_type = 'WIRE'  # Hiển thị dạng khung dây trên Viewport cho đỡ che tầm nhìn

    mat = bpy.data.materials.new(name="MAT_Atmosphere_Volume")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    vol_node = nodes.new(type='ShaderNodeVolumePrincipled')
    vol_node.inputs['Density'].default_value = density
    vol_node.inputs['Anisotropy'].default_value = anisotropy
    links.new(vol_node.outputs['Volume'], out_node.inputs['Volume'])

    fog_box.data.materials.append(mat)
    return fog_box
```

---

### 3.3. Bộ Script Thực Thi Tự Động Chuẩn Blender 5.2 (scripts/)
- [scripts/scene_mood.py](scripts/scene_mood.py): Tự động thiết lập bầu trời vật lý và tâm trạng ánh sáng theo thời gian trong ngày (Bình minh, Trưa, Hoàng hôn, Đêm).
- [scripts/precipitation.py](scripts/precipitation.py), [scripts/surface_weather.py](scripts/surface_weather.py), [scripts/lightning.py](scripts/lightning.py): Tạo hiệu ứng mưa rơi, tuyết, vũng nước phản chiếu đèn phố (puddles), vệt nước chảy và chớp bằng Geometry Nodes 5.2.
- [scripts/night_city_lights.py](scripts/night_city_lights.py): Thiết lập hệ thống đèn đường, cửa sổ phát sáng và khí quyển đô thị ban đêm.
- [scripts/build_cycles_npr.py](scripts/build_cycles_npr.py), [scripts/build_eevee_npr.py](scripts/build_eevee_npr.py), [scripts/toon_setup.py](scripts/toon_setup.py): Dựng vật liệu và ánh sáng Toon/Ghibli 2D NPR trên cả Cycles và EEVEE Next 5.2.
- [scripts/validate_lighting_plan.py](scripts/validate_lighting_plan.py) & [scripts/render_batch.py](scripts/render_batch.py): Kiểm tra tỷ lệ đèn Key/Fill/Rim và chạy render hàng loạt chuẩn AgX.

---

## 4. Danh mục Bài học Trích xuất Hàng ngày từ NotebookLM
*(Mỗi sáng 9h00, 3 kiến thức mới từ cơ bản đến nâng cao sẽ được tự động trích xuất từ `NB_Lighting_Atmosphere`, lưu chi tiết vào thư mục `references/` và cập nhật mục lục dưới đây)*

<!-- DAILY_LESSONS_INDEX -->
- **[L01 — Cơ bản (Level 1)] Nguyên lý 3 nguồn sáng (Three-Point Lighting: Key, Fill, Rim) và tỷ lệ tương phản trong Blender** *(Ngày 2026-10-30)* → Chi tiết: [`references/l01_nguyen_ly_3_nguon_sang_three_point_lighting_key_fill_rim_va_.md`](references/l01_nguyen_ly_3_nguon_sang_three_point_lighting_key_fill_rim_va_.md)
- **[L02 — Cơ bản (Level 1)] Nhiệt độ màu (Kelvin) và thiết lập ánh sáng mặt trời vật lý (Nishita Sky Texture & Sun Light)** *(Ngày 2026-10-30)* → Chi tiết: [`references/l02_nhiet_do_mau_kelvin_va_thiet_lap_anh_sang_mat_troi_vat_ly_ni.md`](references/l02_nhiet_do_mau_kelvin_va_thiet_lap_anh_sang_mat_troi_vat_ly_ni.md)
- **[L03 — Cơ bản (Level 1)] Độ mềm của bóng đổ (Shadow Softness): Mối quan hệ giữa kích thước nguồn sáng (Radius/Size) và khoảng cách** *(Ngày 2026-10-30)* → Chi tiết: [`references/l03_do_mem_cua_bong_do_shadow_softness_moi_quan_he_giua_kich_thu.md`](references/l03_do_mem_cua_bong_do_shadow_softness_moi_quan_he_giua_kich_thu.md)
- **[L04 — Trung cấp (Level 2)] Khí quyển & Sương mù thể tích (Volumetric Fog, Mist & God Rays / Tia nắng xuyên qua khe hẹp)** *(Ngày 2026-11-04)* → Chi tiết: [`references/l04_khi_quyen_suong_mu_the_tich_volumetric_fog_mist_god_rays_tia.md`](references/l04_khi_quyen_suong_mu_the_tich_volumetric_fog_mist_god_rays_tia.md)
- **[L05 — Trung cấp (Level 2)] Chiếu sáng hẻm đô thị & Nội thất thiếu sáng (Bounce Light, Light Portal & Ambient Fill)** *(Ngày 2026-11-04)* → Chi tiết: [`references/l05_chieu_sang_hem_do_thi_noi_that_thieu_sang_bounce_light_light.md`](references/l05_chieu_sang_hem_do_thi_noi_that_thieu_sang_bounce_light_light.md)
- **[L06 — Trung cấp (Level 2)] Phân lớp sáng-tối (Light & Shadow Framing / Chiaroscuro) để dẫn hướng mắt người xem** *(Ngày 2026-11-04)* → Chi tiết: [`references/l06_phan_lop_sang_toi_light_shadow_framing_chiaroscuro_de_dan_hu.md`](references/l06_phan_lop_sang_toi_light_shadow_framing_chiaroscuro_de_dan_hu.md)
- **[L07 — Nâng cao (Level 3)] Light Linking & Shadow Linking: Tách riêng đèn cho nhân vật và môi trường trong Blender** *(Ngày 2026-11-05)* → Chi tiết: [`references/l07_light_linking_shadow_linking_tach_rieng_den_cho_nhan_vat_va_.md`](references/l07_light_linking_shadow_linking_tach_rieng_den_cho_nhan_vat_va_.md)
- **[L08 — Nâng cao (Level 3)] Chiếu sáng ban đêm, đèn Neon & Practical Lights (Emission + Bloom/Glare + Wet Surface Reflections)** *(Ngày 2026-11-05)* → Chi tiết: [`references/l08_chieu_sang_ban_dem_den_neon_practical_lights_emission_bloom_.md`](references/l08_chieu_sang_ban_dem_den_neon_practical_lights_emission_bloom_.md)
- **[L09 — Nâng cao (Level 3)] Quản lý màu sắc AgX / Filmic, Exposure, Gamma và Compositing Light Groups** *(Ngày 2026-11-05)* → Chi tiết: [`references/l09_quan_ly_mau_sac_agx_filmic_exposure_gamma_va_compositing_lig.md`](references/l09_quan_ly_mau_sac_agx_filmic_exposure_gamma_va_compositing_lig.md)
- **[L10 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: Area light creates shadow lines - Lighting and Rendering - Blender Artists Community** *(Ngày 2026-11-06)* → Chi tiết: [`references/l10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_area_light_creates_s.md`](references/l10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_area_light_creates_s.md)
- **[L11 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: Behind the Scenes: Heart of the Industry - BlenderNation** *(Ngày 2026-11-06)* → Chi tiết: [`references/l11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_behind_the_scenes_he.md`](references/l11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_behind_the_scenes_he.md)
- **[L12 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: Blackbody | Adobe Substance 3D Designer - Experience League** *(Ngày 2026-11-06)* → Chi tiết: [`references/l12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_blackbody_adobe_subs.md`](references/l12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_blackbody_adobe_subs.md)
