# [R05] Cơ chế Forward Kinematics (FK) vs Inverse Kinematics (IK), Pole Target và IK-FK Snapping

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

### 1. Tóm tắt Bản chất (2-3 câu)
**FK (Forward Kinematics - Động học thuận)** truyền chuyển động từ xương cha xuống xương con (Parent to Child), thích hợp cho các chuyển động vung vẩy tự do không va chạm với môi trường như tay đung đưa khi bước đi [1]. Ngược lại, **IK (Inverse Kinematics - Động học ngược)** tính toán góc xoay của toàn bộ chuỗi xương dựa trên vị trí của điểm điều khiển đầu cuối (Target Controller), giúp cố định vị trí chi trong không gian như chân đứng vững trên mặt sàn hay tay chống trên mặt bàn [2, 3]. Việc làm chủ FK và IK giúp nhân vật tương tác tự nhiên với môi trường và tránh hiện tượng trượt chân (foot-sliding) khi làm hoạt họa.

---

### 2. Nguyên lý & Thông số Chuẩn

* **Độ cong định hướng trong Metarig (Subtle Bend):** Trong Edit Mode, các khớp bản lề như đầu gối và cùi chỏ bắt buộc phải có một độ cong nhẹ về phía trước [4]. Góc uốn này đóng vai trò hướng dẫn thuật toán IK Solver tính toán hướng gập khớp chính xác, tránh hiện tượng chi bị lật ngược (limb-reversing artifacts) [4].
* **Độ dài chuỗi xương (`Chain Length`):** Đối với chi 2 đoạn (đùi và cẳng chân, hoặc cánh tay và cẳng tay), thuộc tính `Chain Length` bắt buộc phải thiết lập bằng **2** [2, 5]. Nếu đặt bằng 0, lực IK sẽ tác động lan lên toàn bộ trục xương sống đến tận gốc nhân vật [2, 6].
* **Pole Target & Pole Angle:**
  * **Role của Pole Target:** Xương định hướng (như `knee_IK` cho đầu gối hoặc `elbow_IK` cho cùi chỏ) kiểm soát hướng chĩa của khớp trong không gian 3D [2, 5, 7].
  * **Căn chỉnh trục (Roll Angle):** Trục X của xương trong Edit Mode phải hướng thẳng về phía Pole Target [8, 9]. Góc `Pole Angle` thường được thiết lập là **\\(90^\circ\\)** hoặc **\\(-90^\circ\\)** (hoặc \\(0^\circ\\)/\\(180^\circ\\) tùy thuộc vào hệ trục của Armature) để chân không bị xoay vặn khi bật IK [2, 5, 8, 9].
* **Cách ly bàn chân (`Foot Isolation`):** Xương bàn chân biến dạng chính cần nằm ngoài chuỗi lặp IK (outside the main IK loop) [10, 11]. Sử dụng ràng buộc `Copy Location` trỏ đến xương cẳng chân với thuộc tính **`Head/Tail = 1.0`** để giữ bàn chân nằm đúng vị trí cổ chân mà không bị kế thừa các vòng xoay bất thường từ chuỗi IK [2, 5, 12].
* **Tương tác mặt sàn & Địa hình:** 
  * Ràng buộc `Shrinkwrap Constraint` ở chế độ **`Project`** theo trục âm **`-Z`** giúp điểm mục tiêu bám theo độ nhấp nhô của địa hình [5].
  * Ràng buộc `Floor Constraint` ngăn không cho điều khiển bàn chân đâm xuyên xuống bên dưới mặt sàn [5].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác thủ công
1. **Thiết lập khung xương (Edit Mode):** 
   * Extrude xương `foot_IK` từ cổ chân và xương `knee_IK` từ đầu gối [5, 7].
   * Ngắt quan hệ cha con (`Alt + P` > *Clear Parent*) và bỏ tích mục **Deform** trong Bone Properties cho các xương điều khiển này [5, 7, 13].
2. **Thêm ràng buộc IK (Pose Mode):** 
   * Chọn xương cẳng chân (`leg_lower`), thêm constraint **Inverse Kinematics** [2, 5].
   * Gán `Target` = Armature, `Bone` = `foot_IK`, `Pole Target` = Armature, `Pole Bone` = `knee_IK` [2, 5].
   * Đặt `Chain Length` = **2** và tinh chỉnh `Pole Angle` sao cho đầu gối hướng thẳng về xương `knee_IK` [2, 5].
3. **Chuyển đổi IK/FK mượt mà trong Rigify:** 
   * Chọn xương điều khiển tay/chân trong Pose Mode, mở Sidebar (Phím **N**) > Tab **Item** (hoặc *Rig Main Properties*) [14].
   * Điều chỉnh thanh trượt **`FK/IK`** (0 = FK hoàn toàn, 1 = IK hoàn toàn) [14].
   * Nhấn các nút **`Snap IK->FK`** hoặc **`Snap FK->IK`** để tự động khớp vị trí và góc xoay của hai hệ thống điều khiển trước khi chèn keyframe, giúp chuyển đổi mượt mà mà không bị giật dáng [14].

#### B. Đội ngũ Kỹ thuật / Lập trình Python (`bpy`)

```python
import bpy

# 1. Thiết lập ràng buộc IK tự động cho cẳng chân
armature_obj = bpy.data.objects.get("Armature")
if armature_obj:
    pose_bones = armature_obj.pose.bones
    shin_bone = pose_bones.get("leg_lower.L")

    if shin_bone:
        # Tạo constraint Inverse Kinematics
        ik_constr = shin_bone.constraints.new(type='INVERSE_KINEMATICS')
        ik_constr.target = armature_obj
        ik_constr.subtarget = "foot_IK.L"       # Điều khiển vị trí bàn chân
        ik_constr.pole_target = armature_obj
        ik_constr.pole_subtarget = "knee_IK.L"   # Định hướng đầu gối
        ik_constr.chain_count = 2               # Giới hạn chuỗi 2 xương (đùi + cẳng chân)
        ik_constr.pole_angle = 1.5708           # 90 độ tính bằng Radian (1.5708 rad = 90 deg)

# 2. Thay đổi thuộc tính chuyển đổi IK/FK trong Rigify qua script
rigify_armature = bpy.data.objects.get("rig")
if rigify_armature:
    # Rigify lưu thuộc tính custom "IK_FK" trên xương MCH hoặc xương điều khiển cha
    ctrl_bone = rigify_armature.pose.bones.get("upper_arm.parent.L") or rigify_armature.pose.bones.get("MCH-forearm.L")
    if ctrl_bone and "IK_FK" in ctrl_bone:
        ctrl_bone["IK_FK"] = 1.0  # Chuyển sang IK (1.0 = IK, 0.0 = FK)
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Chân/Tay bị xoay vặn hoặc lật ngược khi bật IK:**
  * *Nguyên nhân:* Do các xương trong Metarig xếp thẳng hàng tuyệt đối (không có góc cong nhẹ) [4], hoặc trục X của xương không hướng về Pole Target [8, 9].
  * *Cách kiểm tra:* Trong Viewport Display của Armature, bật hiển thị **Axes** [8, 9]. Kiểm tra trong Edit Mode xem trục X của xương cẳng chân/cẳng tay có chỉ thẳng vào Pole Target hay chưa, sau đó điều chỉnh thông số `Roll` của xương hoặc `Pole Angle` trong constraint [8, 9].
* **Gốc nhân vật hoặc toàn bộ xương sống bị co rúm khi di chuyển xương IK:**
  * *Nguyên nhân:* Quên thiết lập `Chain Length` (để mặc định bằng 0) [2, 6].
  * *Cách kiểm tra:* Kiểm tra bảng thuộc tính IK Constraint, đảm bảo `Chain Length` được giới hạn chính xác là **2** đối với các chi 2 đoạn [2, 5, 6].
* **Bàn chân bị xoay méo hoặc biến dạng theo chuỗi IK:**
  * *Nguyên nhân:* Xương bàn chân deforming nằm trực tiếp trong chuỗi IK thay vì được cách ly ra ngoài [10, 11].
  * *Cách kiểm tra:* Đảm bảo xương cẳng chân nhận IK constraint, còn xương bàn chân nhận constraint `Copy Location` từ cẳng chân (`Head/Tail = 1.0`) và `Copy Rotation` / `Limit Rotation` từ xương điều khiển [2, 5, 11, 12].
* **Lỗi gán trọng số tự động (*Bone Heat Weighting Failed*):**
  * *Nguyên nhân:* Lưới mesh có các vùng đè chéo, đỉnh trùng, hoặc kích thước mô hình quá nhỏ khiến thuật toán Laplacian heat diffusion thất bại [15, 16].
  * *Cách kiểm tra:* Sử dụng quy trình phóng đại 10 lần (*10x Scale Pipeline*: Scale cả Rig và Mesh lên 10 lần -> Parent Automatic Weights -> Scale ngược lại 0.1) hoặc tách các phần lưới rời (*Separate by Loose Parts*) trước khi gán weights [16].

 Bạn có muốn tôi hướng dẫn chi tiết thêm về cách thiết lập hệ thống tự động thích ứng địa hình (Terrain-Adaptive Feet) với ràng buộc Shrinkwrap và Floor không?
