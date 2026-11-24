# [R06] Hệ thống Bone Constraints cốt lõi: Copy Transforms, Damped Track, Limit Rotation và Child Of

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
Bone Constraints (ràng buộc xương) trong Blender là các quy tắc tự động hóa chuyển động và góc xoay của khung xương (Armature), giúp giảm thiểu thao tác thủ công khi đặt dáng và diễn hoạt [1, 2]. Chúng đóng vai trò nền tảng giúp các bộ phận như mắt hay đầu tự động hướng đúng mục tiêu, giới hạn biên độ gập của khớp để tránh biến dạng cơ thể, và xử lý tương tác động khi nhân vật cầm hoặc buông đồ vật [2-4].

---

### 2. **Nguyên lý & Thông số Chuẩn**
Trích xuất từ các quy trình rigging chuyên sâu trong tài liệu:
- **Copy Rotation (Sao chép góc xoay):** Ép xương hiện tại (Owner) sao chép chính xác góc xoay theo các trục chỉ định từ xương/vật thể mục tiêu (Target) [2, 3]. Trong hệ thống thích ứng địa hình, xương bàn chân sử dụng **Copy Rotation** nhắm vào xương kiểm tra mặt đất (`foot_ground_target.L`) có bật tùy chọn *Align to Normal* để bàn chân tự động xoay phẳng theo độ dốc địa hình [3].
- **Damped Track (Theo dõi triệt tiêu xoắn):** Định hướng một trục xác định của xương (như trục \\(-Z\\) hoặc \\(+Y\\)) trỏ thẳng về mục tiêu mà không gây ra hiện tượng xoắn xương (roll) ngoài ý muốn вокруг trục dọc [4]. Đây là giải pháp tiêu chuẩn cho hệ thống hướng mắt (Eye Tracking) và hướng đầu [4].
- **Limit Rotation (Giới hạn góc xoay):** Thiết lập ngưỡng góc xoay tối thiểu (Min) và tối đa (Max) trên từng trục X, Y, Z ở không gian cục bộ (**Local Space**) [3, 5]. Giúp bảo vệ các khớp (cổ chân, khuỷu tay, đầu gối) không bị gập ngược hoặc xoắn bất thường khi chịu tác động từ chuỗi IK hoặc xương cha [3, 5, 6].
- **Child Of (Ràng buộc Quan hệ Cha - Con động):** Cho phép một vật thể hoặc xương nhận dữ liệu dịch chuyển và xoay từ một mục tiêu khác như quan hệ Cha - Con, nhưng có thể điều chỉnh tỷ lệ ảnh hưởng linh hoạt qua thông số **Influence** (từ \\(0.0\\) đến \\(1.0\\)) [3, 7]. Đây là cơ chế chuẩn để nhân vật cầm, giữ rồi buông đồ vật tại các mốc thời gian (keyframe) khác nhau.

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### A. Copy Rotation (Áp dụng cho Bàn chân / Khớp đồng bộ)
* **Thao tác UI:**
  1. Ở **Pose Mode**, chọn xương bàn chân biến dạng [3].
  2. Tại bảng **Bone Constraints**, thêm **Copy Rotation** [3].
  3. Chọn **Target** là Armature và **Bone** là xương mục tiêu (ví dụ: `foot_ground_target.L`) [3].
  4. Đặt **Target Space** = `Local Space` và **Owner Space** = `Local Space` [3].
* **Code Python `bpy`:**
```python
import bpy

armature = bpy.context.object
pbone = armature.pose.bones.get("foot.L")

# Thêm ràng buộc Copy Rotation
crt = pbone.constraints.new('COPY_ROTATION')
crt.name = "Copy_Rot_Ground"
crt.target = armature
crt.subtarget = "foot_ground_target.L"
crt.target_space = 'LOCAL'
crt.owner_space = 'LOCAL'
crt.influence = 1.0
```

#### B. Damped Track (Áp dụng cho Mắt / Hướng đầu)
* **Thao tác UI:**
  1. Chọn xương Mắt (`eye.L`/`eye.R`) hoặc xương Đầu (`head`) trong **Pose Mode** [4].
  2. Thêm ràng buộc **Damped Track**.
  3. Chọn **Target** là vật thể/xương điều khiển hướng nhìn (ví dụ: `Target_LookAt`).
  4. Chọn **Track Axis** phù hợp với hướng dọc của xương (thường là `-Z` hoặc `Y`).
* **Code Python `bpy`:**
```python
import bpy

armature = bpy.context.object
pbone_eye = armature.pose.bones.get("eye.L")

# Thêm ràng buộc Damped Track cho mắt
dt = pbone_eye.constraints.new('DAMPED_TRACK')
dt.name = "Damped_Track_Eye"
dt.target = bpy.data.objects.get("Target_LookAt")  # Hoặc Target là Armature & Subtarget
dt.track_axis = 'TRACK_NEGATIVE_Z'  # Trục hướng thẳng về mục tiêu
dt.influence = 1.0
```

#### C. Limit Rotation (Áp dụng cho Bảo vệ Khớp)
* **Thao tác UI:**
  1. Chọn xương khớp cần bảo vệ (như xương bàn chân `foot.L` hoặc khuỷu tay/đầu gối) [3, 5].
  2. Thêm ràng buộc **Limit Rotation** [3, 5].
  3. Tích chọn các trục cần giới hạn (ví dụ: `X`, `Y`, `Z`), nhập giá trị **Min/Max** theo độ [3].
  4. Chuyển mục **Owner** sang **Local Space** [3].
* **Code Python `bpy`:**
```python
import math
import bpy

armature = bpy.context.object
pbone_foot = armature.pose.bones.get("foot.L")

# Thêm Limit Rotation bảo vệ khớp
lr = pbone_foot.constraints.new('LIMIT_ROTATION')
lr.name = "Limit_Rot_Ankle"
lr.use_limit_x = True
lr.min_x = math.radians(-30.0)  # Góc gập xuống tối đa
lr.max_x = math.radians(45.0)   # Góc ngửa lên tối đa
lr.owner_space = 'LOCAL'
```

#### D. Child Of (Áp dụng cho Cầm / Buông Đồ vật)
* **Thao tác UI:**
  1. Chọn đạo cụ/vật thể trong **Object Mode** (hoặc xương điều khiển vật thể) [7].
  2. Thêm ràng buộc **Child Of** [7].
  3. Chọn **Target** là Armature nhân vật, **Bone** là xương bàn tay (`hand.R`) [7].
  4. Nhấn nút **Set Inverse** để giữ nguyên vị trí hiện tại của đồ vật mà không bị văng lệch.
  5. Đặt Keyframe cho thông số **Influence**: \\(1.0\\) khi nhặt/cầm đồ, và \\(0.0\\) khi buông/thả đồ.
* **Code Python `bpy`:**
```python
import bpy

prop_obj = bpy.data.objects.get("Sword_Prop")
armature_obj = bpy.data.objects.get("Character_Rig")

# Thêm Child Of lên Vật thể
co = prop_obj.constraints.new('CHILD_OF')
co.name = "ChildOf_Hand"
co.target = armature_obj
co.subtarget = "hand.R"

# Đặt vị trí Ma trận nghịch đảo tương đương nút "Set Inverse"
context_override = {"object": prop_obj, "constraint": co}
with bpy.context.temp_override(**context_override):
    bpy.ops.constraint.childof_set_inverse(constraint="ChildOf_Hand", owner='OBJECT')

# Animate Influence: Frame 1 cầm (1.0), Frame 50 buông (0.0)
co.influence = 1.0
co.keyframe_insert(data_path="influence", frame=1)
co.influence = 0.0
co.keyframe_insert(data_path="influence", frame=50)
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**
- **Quên Apply All Transforms (Ctrl + A):** Nếu chưa chuẩn hóa Rotation & Scale của Armature và Mesh về \\(1.0\\) trước khi gán Constraint, tọa độ gốc bị lệch sẽ làm nút *Set Inverse* của Child Of bị biến dạng hoặc làm xương bị văng xa khi dùng *Align to Normal* [6, 8-10].
  * *Cách kiểm tra:* Chọn Armature/Mesh ở Object Mode, nhấn `N` kiểm tra bảng Transform; Scale phải là \\((1.0, 1.0, 1.0)\\) và Rotation là \\((0^\circ, 0^\circ, 0^\circ)\\) [6, 8, 10].
- **Vòng lặp phụ thuộc (Dependency Loop / Rig Loop):** Xảy ra khi Xương A ràng buộc theo Xương B, nhưng Xương B lại trực tiếp hoặc gián tiếp phụ thuộc ngược lại Xương A [11]. Việc này khiến rig bị giật (twitching) hoặc phản hồi chậm \\(1\\) frame [11].
  * *Cách kiểm tra:* Mở cửa sổ *Window -> Toggle System Console* trong Blender để xem thông báo lỗi `Dependency cycle detected`.
- **Nhầm lẫn giữa World Space và Local Space:** Đặt Target/Owner Space ở *World Space* thay vì *Local Space* khiến xương bị ảnh hưởng bởi tọa độ toàn cảnh, dẫn đến việc di chuyển nhân vật làm xương constraint bị xoay sai hướng [3].
- **Đặt Limit Rotation trực tiếp lên chuỗi IK đang hoạt động:** Bộ giải IK (IK Solver) có xu hướng ghi đè lên chuyển động của xương [5, 7]. Do đó, xương biến dạng chứa Limit Rotation nên nằm ngoài vòng lặp IK chính (beyond/outside the IK loop) [3, 5].

  Bạn có muốn tôi hỗ trợ viết tiếp một kịch bản Python hoàn chỉnh để tự động thiết lập toàn bộ hệ thống chân bám địa hình (IK + Shrinkwrap + Floor + Copy Rotation) cho mô hình của bạn không?
