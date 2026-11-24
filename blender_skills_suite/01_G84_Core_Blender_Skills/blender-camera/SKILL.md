---
name: blender-camera
description: Kỹ năng Bố cục Máy quay, Tiêu cự & Dàn dựng Không gian (Camera Blocking & Focal Length) trong Blender 5.1 cho Gate 84. Bao gồm lựa chọn tiêu cự (18mm-135mm), cỡ cảnh, phối cảnh 2 điểm tụ kiến trúc (shift_y), quy tắc trục 180 độ, chiều sâu trường ảnh (DOF) và chuyển động máy quay. Được bồi đắp tự động mỗi 9h sáng từ sổ NotebookLM Camera blocking, tiêu cự.
---

# Kỹ năng Blender: Bố cục Máy quay & Tiêu cự (`blender-camera`)

> **Nguồn tri thức gốc:** Sổ NotebookLM `Camera blocking, tiêu cự,...` (9 nguồn tài liệu)  
> **Cập nhật tự động:** 09:00 sáng hàng ngày (3 bài học/ngày từ Cơ bản → Nâng cao)  
> **Công cụ MCP liên kết:** `execute_blender_code` (Blender MCP), `cam_architectural_cinematography`, `core_viewport_screenshot`

---

## 1. Mục đích & Khi nào sử dụng
Kỹ năng này chuẩn hóa toàn bộ **ngôn ngữ điện ảnh của máy quay** trong Blender 5.1:
- Chọn đúng **tiêu cự (`lens`)** theo cảm xúc nhân vật và độ rộng không gian (đặc biệt là hẻm nhỏ Sài Gòn vs cận cảnh tâm lý).
- Dựng **phối cảnh 2 điểm tụ (`shift_y`, `shift_x`)** giữ tường nhà/cột điện thẳng đứng tuyệt đối, không bị nghiêng đổ méo mó.
- Dàn dựng vị trí đứng của nhân vật và máy quay (**Camera Blocking**, trục 180 độ, Over-The-Shoulder, phân lớp Tiền-Trung-Hậu cảnh).
- Kiểm soát độ xóa phông (**DOF / f-stop**) và chuyển động máy mượt mà.

---

## 2. Bảng Ngôn Ngữ Tiêu Cự (Chuẩn Cảm biến Full-Frame `sensor_width = 36mm`)

| Dải Tiêu Cự | Tên gọi | Đặc tính không gian & Phối cảnh | Ứng dụng trong phim Gate 84 / Hẻm Vít |
| :--- | :--- | :--- | :--- |
| **`18mm – 24mm`** | Góc siêu rộng (Ultra-Wide) | Phóng đại chiều sâu, kéo giãn khoảng cách gần-xa, bao trọn không gian hẹp | Toàn cảnh hẻm sâu, cảnh rượt đuổi, hoặc dí sát mặt tạo cảm giác bất an/hài hước |
| **`28mm – 35mm`** | Góc rộng điện ảnh (Wide / Classic Cinema) | Giữ được bối cảnh môi trường xung quanh nhân vật mà ít làm biến dạng mặt | Master Shot, cảnh sinh hoạt nhóm 2-4 người, cảnh đối thoại thấy rõ không gian quán/hẻm |
| **`50mm`** | Tiêu chuẩn mắt người (Normal Lens) | Tỷ lệ phối cảnh trung thực, tự nhiên, không bóp méo | Cảnh trung (Medium Shot), cảnh kể chuyện khách quan, đời thường |
| **`85mm – 135mm`** | Chân dung / Tele (Portrait / Telephoto) | Nén chặt hậu cảnh lại gần nhân vật, tách biệt nhân vật khỏi đám đông | Cận cảnh tâm lý (Close-Up), cảnh nhìn lén từ xa, hoặc ép không gian tạo cảm giác ngạt thở |

---

## 3. Mẫu Code Python (`bpy`) Chuẩn Hóa

### 3.1. Tạo Camera Điện ảnh kèm Phối cảnh 2 Điểm Tụ & Lấy nét tự động (DOF)
```python
import bpy
import math

def create_cinematic_camera(
    name="CAM_Shot01",
    location=(0.0, -6.0, 1.6),
    rotation_deg=(90.0, 0.0, 0.0),
    focal_length=35.0,
    shift_y=0.0,
    use_dof=True,
    fstop=2.8,
    focus_target_name=None
):
    """
    Tạo Camera chuẩn Full-Frame (36mm).
    - Để giữ tường thẳng đứng tuyệt đối (Two-Point Perspective): đặt rotation_deg[0] = 90.0
      và dùng shift_y (ví dụ 0.15 đến 0.30) để lấy ngọn nhà mà không ngửa máy lên.
    """
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.sensor_fit = 'HORIZONTAL'
    cam_data.sensor_width = 36.0
    cam_data.lens = focal_length
    cam_data.shift_y = shift_y
    cam_data.show_composition_thirds = True
    cam_data.passepartout_alpha = 0.85

    if use_dof:
        cam_data.dof.use_dof = True
        cam_data.dof.aperture_fstop = fstop
        if focus_target_name and focus_target_name in bpy.data.objects:
            cam_data.dof.focus_object = bpy.data.objects[focus_target_name]

    cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = location
    cam_obj.rotation_euler = tuple(math.radians(a) for a in rotation_deg)
    bpy.context.scene.camera = cam_obj
    return cam_obj
```

---

### 3.2. Bộ Script Thực Thi Tự Động Chuẩn Blender 5.2 (scripts/)
- [scripts/bx_previs.py](scripts/bx_previs.py): Tự động dàn dựng danh sách cảnh quay (uild_shots), đặt Camera theo cỡ cảnh/tiêu cự (place_camera), thêm độ rung cầm tay tự nhiên (handheld), vẽ mặt bằng bố trí máy quay (loor_plan), xuất bảng ảnh duyệt (contact_sheet) và kiểm tra trục 180 độ / đường nhìn (udit, line_of_sight).
- [scripts/bx_blockout.py](scripts/bx_blockout.py): Tạo Camera chạy trên đường ray (
ail_camera, key_rail), cắt cảnh theo Timeline Markers (ind_cuts) và kiểm định góc máy/khung hình (udit_framing, udit_occlusion, udit_cuts).
- [scripts/shakify_cams.py](scripts/shakify_cams.py) & [scripts/chase_camera_rig.py](scripts/chase_camera_rig.py): Tạo rung động máy quay cầm tay thực tế và Camera bám đuổi chủ thể.
- [scripts/track_camera.py](scripts/track_camera.py) & [scripts/vse_edit.py](scripts/vse_edit.py): Khóa mục tiêu Camera và dựng cắt cảnh trên Video Sequence Editor (VSE).

---

## 4. Danh mục Bài học Trích xuất Hàng ngày từ NotebookLM
*(Mỗi sáng 9h00, 3 kiến thức mới từ cơ bản đến nâng cao sẽ được tự động trích xuất từ `Camera blocking, tiêu cự`, lưu chi tiết vào thư mục `references/` và cập nhật mục lục dưới đây)*

<!-- DAILY_LESSONS_INDEX -->
- **[C01 — Cơ bản (Level 1)] Ngôn ngữ tiêu cự ống kính (Focal Length: 18mm, 24mm, 35mm, 50mm, 85mm, 135mm) và độ nén không gian** *(Ngày 2026-10-30)* → Chi tiết: [`references/c01_ngon_ngu_tieu_cu_ong_kinh_focal_length_18mm_24mm_35mm_50mm_8.md`](references/c01_ngon_ngu_tieu_cu_ong_kinh_focal_length_18mm_24mm_35mm_50mm_8.md)
- **[C02 — Cơ bản (Level 1)] Cỡ cảnh điện ảnh (Shot Sizes: EWS, WS, MS, MCU, CU, ECU) và chiều cao đặt máy (Camera Height & Angle)** *(Ngày 2026-10-30)* → Chi tiết: [`references/c02_co_canh_dien_anh_shot_sizes_ews_ws_ms_mcu_cu_ecu_va_chieu_ca.md`](references/c02_co_canh_dien_anh_shot_sizes_ews_ws_ms_mcu_cu_ecu_va_chieu_ca.md)
- **[C03 — Cơ bản (Level 1)] Bố cục khung hình (Rule of Thirds, Leading Lines, Frame within a Frame, Headroom & Lookroom)** *(Ngày 2026-10-30)* → Chi tiết: [`references/c03_bo_cuc_khung_hinh_rule_of_thirds_leading_lines_frame_within_.md`](references/c03_bo_cuc_khung_hinh_rule_of_thirds_leading_lines_frame_within_.md)
- **[C04 — Trung cấp (Level 2)] Camera Blocking cho đối thoại: Quy tắc trục 180 độ, Over-The-Shoulder (OTS) và Shot/Reverse-Shot** *(Ngày 2026-11-04)* → Chi tiết: [`references/c04_camera_blocking_cho_doi_thoai_quy_tac_truc_180_do_over_the_s.md`](references/c04_camera_blocking_cho_doi_thoai_quy_tac_truc_180_do_over_the_s.md)
- **[C05 — Trung cấp (Level 2)] Phối cảnh 2 điểm tụ kiến trúc (Two-Point Perspective): Dùng Optical Lens Shift (shift_x, shift_y) trong hẻm hẹp** *(Ngày 2026-11-04)* → Chi tiết: [`references/c05_phoi_canh_2_diem_tu_kien_truc_two_point_perspective_dung_opt.md`](references/c05_phoi_canh_2_diem_tu_kien_truc_two_point_perspective_dung_opt.md)
- **[C06 — Trung cấp (Level 2)] Độ sâu trường ảnh (Depth of Field - DOF): Khẩu độ f-stop, kích thước cảm biến (Sensor Width) và lấy nét theo Object** *(Ngày 2026-11-04)* → Chi tiết: [`references/c06_do_sau_truong_anh_depth_of_field_dof_khau_do_f_stop_kich_thu.md`](references/c06_do_sau_truong_anh_depth_of_field_dof_khau_do_f_stop_kich_thu.md)
- **[C07 — Nâng cao (Level 3)] Chuyển động máy quay (Camera Movement): Dolly, Truck, Pan, Tilt, Crane và chống cảm giác CGI giả tạo** *(Ngày 2026-11-05)* → Chi tiết: [`references/c07_chuyen_dong_may_quay_camera_movement_dolly_truck_pan_tilt_cr.md`](references/c07_chuyen_dong_may_quay_camera_movement_dolly_truck_pan_tilt_cr.md)
- **[C08 — Nâng cao (Level 3)] Dàn dựng chiều sâu 3 lớp (Foreground - Midground - Background Staging) trong không gian 3D** *(Ngày 2026-11-05)* → Chi tiết: [`references/c08_dan_dung_chieu_sau_3_lop_foreground_midground_background_sta.md`](references/c08_dan_dung_chieu_sau_3_lop_foreground_midground_background_sta.md)
- **[C09 — Nâng cao (Level 3)] Quản lý đa Camera trong 1 cảnh (Multi-Camera Switching bằng Timeline Markers & Bind Camera to Markers)** *(Ngày 2026-11-05)* → Chi tiết: [`references/c09_quan_ly_da_camera_trong_1_canh_multi_camera_switching_bang_t.md`](references/c09_quan_ly_da_camera_trong_1_canh_multi_camera_switching_bang_t.md)
- **[C10 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: Blender Cơ Bản - Phần 13: Animation - Chuyển động cơ bản với Blender ( Blender Tutorial )** *(Ngày 2026-11-06)* → Chi tiết: [`references/c10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_blender_co_ban_phan_.md`](references/c10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_blender_co_ban_phan_.md)
- **[C11 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: Create Custom Buildings in Blender - Lazy Tutorials** *(Ngày 2026-11-06)* → Chi tiết: [`references/c11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_create_custom_buildi.md`](references/c11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_create_custom_buildi.md)
- **[C12 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: Create Landscape Inside Blender 3D | Full Tutorial with project file** *(Ngày 2026-11-06)* → Chi tiết: [`references/c12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_create_landscape_ins.md`](references/c12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_create_landscape_ins.md)
