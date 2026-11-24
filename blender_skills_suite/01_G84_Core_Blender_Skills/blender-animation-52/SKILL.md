---
name: blender-animation-52
description: Kỹ năng Diễn xuất Nhân vật & Chuyển động Mềm Chuẩn Kỹ Thuật trên Blender 5.1/5.2+ cho Gate 84. Bao gồm API Slotted Action (channelbag) mới của Blender 5.2, quy trình Blocking-to-Spline (AUTO_CLAMPED Bezier + Moving Holds), đi bộ theo đường dẫn (walk_path IK), Retarget Mocap/Mixamo, chống trượt chân (foot_slip), chống giật khớp gối (limb_extension), nhịp thở tự nhiên và xuất Onion-Skin / Đồ thị F-Curve để kiểm định chuyển động.
---

# Kỹ năng Blender 5.2: Diễn xuất & Chuyển động Mềm Chuẩn Kỹ Thuật (`blender-animation-52`)

> **Mục đích:** Đảm bảo mọi nhân vật 3D và máy quay trong phim trường Gate 84 di chuyển **mềm mại, có trọng lượng, có nhịp nghỉ (Moving Holds), có gia tốc tự nhiên (Ease-In / Ease-Out)** và tuân thủ tuyệt đối **Slotted Action API (`channelbag`) của Blender 5.0–5.2+**.

---

## 1. Quy tắc Sống Còn để Tạo "Chuyển Động Mềm Chuẩn Kỹ Thuật"

1. **Tuyệt đối không dùng `act.fcurves` trực tiếp trên Blender 5.2 mà không qua `channelbag`:**
   Từ Blender 5.0–5.2, một `Action` chứa nhiều `Slots` và `Layers`. Luôn dùng hàm `bx_anim.channelbag(id_block, create=True)` hoặc `_bpyx.ensure_action()` trong bộ `scripts/` của skill này để lấy đúng `fcurves`.
2. **Quy trình 3 bước của Blender Studio (`Stepped Blocking` → `Moving Holds` → `Auto-Clamped Spline`):**
   - **Bước 1 (Đặt dáng chính / Key Poses):** Đặt các tư thế kể chuyện rõ ràng ở chế độ `CONSTANT` (Stepped).
   - **Bước 2 (Giữ nhịp / Pillars & Moving Holds):** Dùng `bx_anim.auto_holds()` và `bx_anim.hold_copy()` để nhân bản tư thế ở đầu và cuối mỗi nhịp dừng — giúp nhân vật không bị "trôi bồng bềnh như dưới nước" (floaty CGI).
   - **Bước 3 (Mượt hóa / Blocking to Spline):** Dùng `bx_anim.blocking_to_spline(rig, body_bones)` để chuyển sang `BEZIER` với tay nắm `AUTO_CLAMPED` (chống vọt lố `overshoot`) và chèn `ease_inbetweens(mode="slow_in" / "slow_out")`.
3. **Đi bộ & Di chuyển có bước chân thật (`bx_kits.walk_path`):**
   Khi nhân vật di chuyển từ điểm A sang điểm B, dùng `bx_kits.walk_path(fig, path, stride, swing_deg, bob=True)` để tự động tính toán chu kỳ bước chân, độ nhấp nhô hông (`bob`) và độ vung tay theo vận tốc thực tế, không bao giờ kéo trượt nhân vật trên sàn.
4. **Kiểm định toán học sau khi làm hoạt hình (Không đoán mò):**
   Luôn chạy bộ kiểm tra trong `bx_anim.py`:
   - `foot_slip(rig, bone, contact_ranges)` → Bắt lỗi trượt bàn chân trên mặt đất.
   - `limb_extension(rig, chain, frames)` → Bắt lỗi duỗi thẳng 100% gây giật khớp gối/khuỷu tay (`knee pop`).
   - `rotation_flips(rig)` & `fix_rotation_flips(rig)` → Sửa lỗi lật góc Euler/Quaternion 180 độ giữa 2 frame.
   - `onion_skin(out_path, frames, objects)` & `graph_image(out_path, rig)` → Xuất ảnh bóng mờ chuyển động (Onion Skin) và biểu đồ đường cong F-Curve ra file PNG để Cúc nhìn kiểm tra trực tiếp.

---

## 2. Bộ Công Cụ Thực Thi (`scripts/`)

| File Script | Chức năng chính |
| :--- | :--- |
| [`scripts/bx_anim.py`](scripts/bx_anim.py) | Thư viện lõi 2,142 dòng cho Blender 5.2: `channelbag`, `key_pose`, `world_pose`, `blocking_to_spline`, `auto_holds`, `breakdown`, `ease_inbetweens`, `offset_keys`, `foot_slip`, `limb_extension`, `balance_report`, `onion_skin`, `graph_image`. |
| [`scripts/bx_kits.py`](scripts/bx_kits.py) | Chứa hàm `walk_path`, `crowd`, `drive`, `pedal` để tạo chuyển động bước đi, đạp xe, lái xe và đám đông tự động theo quỹ đạo. |
| [`scripts/retarget.py`](scripts/retarget.py) | Chuyển đổi (Retarget) chuyển động từ file Mocap FBX/BVH (Mixamo, Rokoko...) sang bộ xương Rigify chuẩn Blender 5.2. |
| [`scripts/bake_action.py`](scripts/bake_action.py) | Nướng (Bake) toàn bộ Constraints/IK/Retarget thành Keyframe sạch để xuất sang engine khác hoặc render ổn định. |
| [`scripts/loop_check.py`](scripts/loop_check.py) | Kiểm tra và ép khớp frame đầu – frame cuối cho các chuyển động lặp (idle, walk cycle, run cycle). |
| [`scripts/animation_contact_sheet.py`](scripts/animation_contact_sheet.py) | Xuất bảng lưới ảnh (Contact Sheet) cắt đều theo thời gian để nghiệm thu độ mượt của hoạt hình. |

---

## 3. Tài Liệu Tham Chiếu Chuyên Sâu (`references/`)
- [`references/ref_anim_procedures.md`](references/ref_anim_procedures.md): Hướng dẫn chi tiết cách gọi toàn bộ hàm API trong `bx_anim.py`.
- [`references/ref_anim_expert_notes.md`](references/ref_anim_expert_notes.md): Ghi chú kỹ thuật của các chuyên gia hoạt hình Blender Studio (Hjalti Hjalmarsson, Rik Schutte, Pierrick Picaut).
- [`references/ref_anim_critique.md`](references/ref_anim_critique.md): Tiêu chuẩn bắt lỗi chuyển động (stiff, floaty, knee-pop, foot-sliding, twinning).
- [`references/g84_action_engine_architecture.md`](references/g84_action_engine_architecture.md): Quy chuẩn **G84 Action Engine (Biên đạo võ thuật 5 pha + Khinh công Wire-Fu + Khóa vũ khí + Phá hủy có điều kiện)** cho các cảnh đánh nhau 30 giây (`720 frames @ 24fps`).
