# [R02] Hướng xoay trục xương (Bone Roll) và quy tắc uốn khớp chuẩn giải phẫu học trong Edit Mode

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

Dưới đây là lời giải thích chi tiết và hướng dẫn thiết lập **Bone Roll** cũng như **Pre-bend** trong Blender dựa trên tài liệu sổ tay rigging của bạn:

---

### 1. Tóm tắt Bản chất (2-3 câu)
**Bone Roll** định hình hướng xoay cục bộ quanh trục dọc của xương (trục X/Y/Z) [1, 2], trong khi **Pre-bend** tạo một độ gập góc nhỏ ban đầu tại các khớp bản lề như đầu gối hay khuỷu tay ngay từ không gian dựng xương [3]. Hai yếu tố này giúp bộ giải Động học ngược (IK - Inverse Kinematics) xác định chính xác mặt phẳng co gập giải phẫu và hướng xoay khớp [3-5]. Nếu thiếu Pre-bend hoặc đặt Bone Roll sai, bộ giải IK sẽ bị mất phương hướng toán học, dẫn đến hiện tượng chân/tay bị vặn xoắn, lật ngược khớp hoặc giật bất thường khi diễn họa [3-5].

---

### 2. Nguyên lý & Thông số Chuẩn

* **Nguyên lý Pre-bend (Độ cong nhẹ ban đầu):**
  * Trong **Edit Mode**, 3 điểm nối của chuỗi khớp (Hông – Đầu gối – Cổ chân hoặc Vai – Khuỷu tay – Cổ tay) không bao giờ được xếp nằm trên một đường thẳng tuyệt đối (\\(180^\circ\\)) [3, 6].
  * Cần đặt vị trí khớp giữa (đầu gối/khuỷu tay) hơi chệch về phía trước (forward bend) để cung cấp cho bộ giải IK "manh mối" mặt phẳng gập [3, 6, 7].
  * **Chiều dài chuỗi IK (`Chain Length`):** Phải đặt cố định bằng **2** đối với chân hoặc tay để giới hạn tầm ảnh hưởng chỉ nằm trong 2 xương (Đùi + Cẳng chân hoặc Cánh tay + Cạu tay) [8-10].
  * **Căn bằng mặt sàn:** Xương gót chân (`Heel bone`) phải aligned nằm ngang với xương ngón chân (`Toe bone`) để thiết lập mặt phẳng tiếp đất phẳng [3, 7].

* **Nguyên lý Bone Roll (Hướng trục cục bộ):**
  * Trục Y chạy dọc theo thân xương, trong khi trục X và Z định hướng góc xoay vuông góc [1, 2, 4].
  * **Quy tắc hướng trục chuẩn:** Trục X (hoặc trục Z tùy chế độ) của xương đùi và cẳng chân trong Edit Mode phải chỉ thẳng trực diện về phía xương điều hướng Pole Target (`knee_IK`) [1, 2, 4].
  * **Thông số Roll Chuẩn:** Giá trị Roll trong Edit Mode thường xoay về góc chuẩn **90°** hoặc **-90°** (tùy thuộc hướng dựng Armature) [1, 2]. Chỉnh Roll chuẩn từ Edit Mode giúp đặt `Pole Angle = 0°` trong Constraint IK mà không làm xoay vặn bàn chân [1, 2, 4].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác trên giao diện UI (Manual Steps):
1. **Apply Transform:** Chọn nhân vật và Armature ở Object Mode, nhấn **`Ctrl + A` \\(\rightarrow\\) `All Transforms`** để đưa Scale và Rotation về chuẩn (Scale = 1, Rotation = 0) [11, 12].
2. **Tạo Pre-bend (Edit Mode):**
   * Vào **Edit Mode** của Armature [9, 13, 14].
   * Ở góc nhìn nghiêng (Side View), chọn khớp đầu gối/khuỷu tay và di chuyển hơi nhếch về phía trước [3, 13, 15].
3. **Tạo xương Pole Target & IK Controller:**
   * Extrude một xương từ đầu gối ra phía trước làm Pole Target (`knee_IK`), nhấn `Alt + P` \\(\rightarrow\\) *Clear Parent* và di chuyển ra phía trước [9, 13, 14, 16]. Bỏ chọn `Deform` trong Bone Properties [9, 13, 14, 16].
   * Extrude/Duplicate xương cổ chân làm xương điều khiển (`foot_IK`), Clear Parent và bỏ `Deform` [9, 13, 14, 16].
4. **Hiệu chỉnh Bone Roll:**
   * Bật hiển thị **Axes** trong bảng `Armature Properties` \\(\rightarrow\\) `Viewport Display` [2, 4].
   * Mở bảng `N` \\(\rightarrow\\) `Item` \\(\rightarrow\\) `Roll` (hoặc dùng `Ctrl + R`), chỉnh thông số Roll của xương đùi và cẳng chân sao cho trục X chỉ thẳng vào xương `knee_IK` (thường đặt góc **90°** hoặc **-90°**) [1, 2].
5. **Thiết lập IK Constraint (Pose Mode):**
   * Sang **Pose Mode**, chọn xương cẳng chân (`leg_lower` / `shin`), thêm constraint **Inverse Kinematics** [8-10].
   * Đặt `Target` = Armature, `Bone` = `foot_IK` [8-10].
   * Đặt `Pole Target` = Armature, `Pole Bone` = `knee_IK` [8-10].
   * Đặt `Chain Length` = **2**, giữ `Pole Angle` = **0°** [4, 8-10].

---

#### B. Code Python (`bpy`) thiết lập tự động:

```python
import bpy
import math

# Select and set active Armature
armature_obj = bpy.data.objects.get("Armature")
bpy.context.view_layer.objects.active = armature_obj

# 1. Edit Mode: Set Bone Roll for Leg Bones
bpy.ops.object.mode_set(mode='EDIT')
edit_bones = armature_obj.data.edit_bones

upper_leg = edit_bones.get("leg_upper.L")
lower_leg = edit_bones.get("leg_lower.L")

if upper_leg and lower_leg:
    # Set local X-axis pointing towards Pole Target
    upper_leg.roll = math.radians(90.0)
    lower_leg.roll = math.radians(90.0)

# 2. Pose Mode: Add IK Constraint
bpy.ops.object.mode_set(mode='POSE')
pose_lower_leg = armature_obj.pose.bones.get("leg_lower.L")

if pose_lower_leg:
    # Clean old IK constraints
    for constraint in pose_lower_leg.constraints:
        if constraint.type == 'IK':
            pose_lower_leg.constraints.remove(constraint)

    # Assign Inverse Kinematics Constraint
    ik_constraint = pose_lower_leg.constraints.new(type='IK')
    ik_constraint.target = armature_obj
    ik_constraint.subtarget = "foot_IK.L"
    ik_constraint.pole_target = armature_obj
    ik_constraint.pole_subtarget = "knee_IK.L"
    ik_constraint.chain_count = 2
    ik_constraint.pole_angle = math.radians(0.0)
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1. **Khớp bị lật/bẻ ngược ra sau (Knee/Elbow Reversing):**
   * *Nguyên nhân:* Xương đùi và cẳng chân nằm trên 1 đường thẳng tuyệt đối (\\(180^\circ\\)) trong Edit Mode khiến thuật toán IK không xác định được hướng gập [3].
   * *Khắc phục:* Vào Edit Mode, kéo nhẹ khớp đầu gối ra phía trước để tạo Pre-bend [3, 7].
2. **Cẳng chân/Bàn chân bị xoắn khi gán Pole Target:**
   * *Nguyên nhân:* Trục cục bộ của xương trong Edit Mode không hướng tới Pole Target [1, 2, 4].
   * *Khắc phục:* Bật hiển thị **Axes**, điều chỉnh `Roll` về góc 90° / -90° trong Edit Mode thay vì cố xoay thông số `Pole Angle` phức tạp ở Pose Mode [1, 2].
3. **Kéo chân làm co rút cả hông và toàn bộ cơ thể:**
   * *Nguyên nhân:* Đặt sai hoặc quên chỉnh `Chain Length` (khi để mặc định = 0, IK sẽ tác động ngược lên tới gốc Armature) [8-10].
   * *Khắc phục:* Đặt `Chain Length = 2` [8-10].
4. **Lỗi biến dạng/xoay vô lý do quên Apply Transform:**
   * *Nguyên nhân:* Scale hoặc Rotation của Armature khác 1 và 0 ở Object Mode [11, 12, 17].
   * *Khắc phục:* Thực hiện `Ctrl + A` \\(\rightarrow\\) `All Transforms` trước khi thực hiện thiết lập xương [11, 12, 17].

---

🦴 *Bạn có muốn mình hướng dẫn chi tiết thêm về cách thiết lập hệ thống Foot Roll (xoay cổ chân, nhón ngón chân) hoặc hệ thống IK/FK Switch cho cánh tay không?*
