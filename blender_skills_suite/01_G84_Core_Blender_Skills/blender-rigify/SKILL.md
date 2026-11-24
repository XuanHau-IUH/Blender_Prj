---
name: blender-rigify
description: Kỹ năng Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify) trong Blender 5.1 cho Gate 84. Bao gồm chuẩn bị Mesh, Bone Roll, Rigify Metarig, Weight Painting, cơ chế IK/FK, Bone Constraints, Facial Rigging và Pose Library. Được bồi đắp tự động mỗi 9h sáng từ sổ NotebookLM NB_Character_Rigging.
---

# Kỹ năng Blender: Gắn xương & Điều khiển Nhân vật (`blender-rigify`)

> **Nguồn tri thức gốc:** Sổ NotebookLM `NB_Character_Rigging` (32 nguồn tài liệu)  
> **Cập nhật tự động:** 09:00 sáng hàng ngày (3 bài học/ngày từ Cơ bản → Nâng cao)  
> **Công cụ MCP liên kết:** `execute_blender_code` (Blender MCP), `char_rigify_autorig`, `char_sketch2pose`, `char_pose_library`

---

## 1. Mục đích & Khi nào sử dụng
Kỹ năng này tổng hợp quy trình **gắn xương (Rigging), gán da (Skinning/Weight Paint) và điều khiển diễn xuất (Animation Controls)** cho nhân vật 3D trong Blender 5.1:
- Kiểm tra và chuẩn hóa mô hình nhân vật trước khi gắn xương (Scale = 1, Rotation = 0, Origin tại gốc tọa độ giữa hai bàn chân).
- Dựng bộ xương chuẩn với `Rigify` hoặc xương tùy chỉnh (Custom Armature), đảm bảo hướng xoay khớp (`Bone Roll`) và độ cong mồi (`Pre-bend`) cho IK.
- Xử lý biến dạng lưới mượt mà bằng Weight Painting, Corrective Shape Keys và chuyển Weight sang quần áo (`Data Transfer`).

---

## 2. Danh sách Kiểm tra Bắt buộc Trước khi Rig (Pre-Flight Checklist)

1. **Apply All Transforms (`Ctrl + A` → All Transforms):** Mọi mesh nhân vật và Armature bắt buộc phải có `Location = (0,0,0)`, `Rotation = (0,0,0)`, `Scale = (1,1,1)`. Nếu quên bước này, khi xoay xương nhân vật sẽ bị méo xệch (Shearing).
2. **Hướng mặt nhân vật:** Nhân vật phải đứng nhìn thẳng về phía **trục `-Y`** (Front View khi bấm `Numpad 1`), hai bên trái/phải đối xứng qua trục `X`.
3. **Độ cong mồi cho khớp IK (Pre-bend):** Đầu gối phải hơi nhô nhẹ về phía trước (`-Y`), khuỷu tay hơi cong nhẹ về phía sau (`+Y`) trong Edit Mode để bộ giải IK biết chiều gập tự nhiên.
4. **Quy tắc đặt tên đối xứng:** Mọi xương bên trái phải kết thúc bằng `.L` (ví dụ `hand.L`), bên phải kết thúc bằng `.R` (`hand.R`) để dùng được `Symmetrize` và `Paste Flipped Pose`.

---

## 3. Mẫu Code Python (`bpy`) Chuẩn Hóa

### 3.1. Kiểm tra & Chuẩn hóa Mesh trước khi gắn xương + Kích hoạt Rigify Metarig
```python
import bpy

def prepare_mesh_and_add_metarig(mesh_name):
    """Chuẩn hóa Transform cho Mesh nhân vật và tạo bộ xương mẫu Human Metarig của Rigify."""
    if not bpy.context.preferences.addons.get("rigify"):
        bpy.ops.preferences.addon_enable(module="rigify")

    mesh_obj = bpy.data.objects.get(mesh_name)
    if mesh_obj:
        bpy.ops.object.select_all(action='DESELECT')
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Thêm Human Metarig tại gốc tọa độ
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.name = f"META_{mesh_name}"
    metarig.show_in_front = True
    return metarig
```

---

### 3.2. Bộ Script Thực Thi Tự Động Chuẩn Blender 5.2 (scripts/)
- [scripts/bx_rig.py](scripts/bx_rig.py): Thư viện Rigging 3,120 dòng chuẩn Blender 5.2 (it_metarig, check_metarig, upgrade_face, generate, ind kèm Voxel Proxy fallback khi Bone Heat lỗi, clean_weights, strip_opposite_side, pply_pose, deformation_report, pose_sheet, joint_sheet, shape_set('arkit')).
- [scripts/rigify_build.py](scripts/rigify_build.py), [scripts/bind_mesh.py](scripts/bind_mesh.py), [scripts/rig_check.py](scripts/rig_check.py), [scripts/stress_poses.py](scripts/stress_poses.py): Tự động sinh Rigify, gán da và uốn thử các tư thế cực hạn (Stress Poses) để kiểm tra rách lưới.
- [scripts/shapekeys.py](scripts/shapekeys.py) & [scripts/garment.py](scripts/garment.py): Tạo bộ 52 Shape Keys mặt ARKit / Visemes khẩu hình và chuyển Weight tự động sang quần áo nhiều lớp.

---

## 4. Danh mục Bài học Trích xuất Hàng ngày từ NotebookLM
*(Mỗi sáng 9h00, 3 kiến thức mới từ cơ bản đến nâng cao sẽ được tự động trích xuất từ `NB_Character_Rigging`, lưu chi tiết vào thư mục `references/` và cập nhật mục lục dưới đây)*

<!-- DAILY_LESSONS_INDEX -->
- **[R01 — Cơ bản (Level 1)] Nguyên lý Armature, hệ thống phân cấp xương (Bone Hierarchy: Root, Spine, Limbs) và chuẩn hóa Mesh trước khi Rig** *(Ngày 2026-10-30)* → Chi tiết: [`references/r01_nguyen_ly_armature_he_thong_phan_cap_xuong_bone_hierarchy_ro.md`](references/r01_nguyen_ly_armature_he_thong_phan_cap_xuong_bone_hierarchy_ro.md)
- **[R02 — Cơ bản (Level 1)] Hướng xoay trục xương (Bone Roll) và quy tắc uốn khớp chuẩn giải phẫu học trong Edit Mode** *(Ngày 2026-10-30)* → Chi tiết: [`references/r02_huong_xoay_truc_xuong_bone_roll_va_quy_tac_uon_khop_chuan_gi.md`](references/r02_huong_xoay_truc_xuong_bone_roll_va_quy_tac_uon_khop_chuan_gi.md)
- **[R03 — Cơ bản (Level 1)] Quy trình tạo Metarig chuẩn với Rigify và sinh bộ điều khiển (Generate Rig)** *(Ngày 2026-10-30)* → Chi tiết: [`references/r03_quy_trinh_tao_metarig_chuan_voi_rigify_va_sinh_bo_dieu_khien.md`](references/r03_quy_trinh_tao_metarig_chuan_voi_rigify_va_sinh_bo_dieu_khien.md)
- **[R04 — Trung cấp (Level 2)] Skinning & Weight Painting: Automatic Weights, Normalize, xử lý vùng vai, hông và khớp gấp** *(Ngày 2026-11-04)* → Chi tiết: [`references/r04_skinning_weight_painting_automatic_weights_normalize_xu_ly_v.md`](references/r04_skinning_weight_painting_automatic_weights_normalize_xu_ly_v.md)
- **[R05 — Trung cấp (Level 2)] Cơ chế Forward Kinematics (FK) vs Inverse Kinematics (IK), Pole Target và IK-FK Snapping** *(Ngày 2026-11-04)* → Chi tiết: [`references/r05_co_che_forward_kinematics_fk_vs_inverse_kinematics_ik_pole_t.md`](references/r05_co_che_forward_kinematics_fk_vs_inverse_kinematics_ik_pole_t.md)
- **[R06 — Trung cấp (Level 2)] Hệ thống Bone Constraints cốt lõi: Copy Transforms, Damped Track, Limit Rotation và Child Of** *(Ngày 2026-11-04)* → Chi tiết: [`references/r06_he_thong_bone_constraints_cot_loi_copy_transforms_damped_tra.md`](references/r06_he_thong_bone_constraints_cot_loi_copy_transforms_damped_tra.md)
- **[R07 — Nâng cao (Level 3)] Rig khuôn mặt (Facial Rigging) kết hợp Corrective Shape Keys và Drivers tự động** *(Ngày 2026-11-05)* → Chi tiết: [`references/r07_rig_khuon_mat_facial_rigging_ket_hop_corrective_shape_keys_v.md`](references/r07_rig_khuon_mat_facial_rigging_ket_hop_corrective_shape_keys_v.md)
- **[R08 — Nâng cao (Level 3)] Rig phụ kiện, quần áo nhiều lớp (Mesh Deform / Surface Deform / Data Transfer Weights)** *(Ngày 2026-11-05)* → Chi tiết: [`references/r08_rig_phu_kien_quan_ao_nhieu_lop_mesh_deform_surface_deform_da.md`](references/r08_rig_phu_kien_quan_ao_nhieu_lop_mesh_deform_surface_deform_da.md)
- **[R09 — Nâng cao (Level 3)] Tối ưu hóa Rig cho diễn xuất & Tự động hóa Pose (Pose Library, Sketch2Pose & Retargeting Mocap)** *(Ngày 2026-11-05)* → Chi tiết: [`references/r09_toi_uu_hoa_rig_cho_dien_xuat_tu_dong_hoa_pose_pose_library_s.md`](references/r09_toi_uu_hoa_rig_cho_dien_xuat_tu_dong_hoa_pose_pose_library_s.md)
- **[C10 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: 6 simple step to have an IK Rig | Beginner Tutorial Blender** *(Ngày 2026-11-06)* → Chi tiết: [`references/c10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_6_simple_step_to_hav.md`](references/c10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_6_simple_step_to_hav.md)
- **[C11 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: A better way to shrinkwrap a curve to a surface? - Blender Artists Community** *(Ngày 2026-11-06)* → Chi tiết: [`references/c11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_a_better_way_to_shri.md`](references/c11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_a_better_way_to_shri.md)
- **[C12 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: Advanced Character Staging, Rigging, and Pose Management Pipelines in Blender** *(Ngày 2026-11-06)* → Chi tiết: [`references/c12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_advanced_character_s.md`](references/c12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_advanced_character_s.md)
