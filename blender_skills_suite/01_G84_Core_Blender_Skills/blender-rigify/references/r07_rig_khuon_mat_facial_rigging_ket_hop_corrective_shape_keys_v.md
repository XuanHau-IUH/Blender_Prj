# [R07] Rig khuôn mặt (Facial Rigging) kết hợp Corrective Shape Keys và Drivers tự động

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

### 1. Tóm tắt Bản chất
Kỹ thuật kết hợp xương mặt (Facial Bones) với Shape Keys (Blendshapes) và Driver giúp duy trì thể tích khối cơ cũng như hình dạng bề mặt mượt mà khi các khớp xương vận động ở góc gập lớn [1, 2]. Trọng số tự động (Automatic Weights) của hệ thống xương thông thường hay gặp giới hạn khi co gập mạnh, dễ làm móp méo lưới (mesh deformation) [1, 3]. Việc sử dụng Driver tự động kích hoạt Shape Keys dựa trên góc xoay của xương giúp khắc phục triệt để các biến dạng xấu này, giữ cho biểu cảm khuôn mặt tự nhiên và sắc nét [1, 4].

---

### 2. Nguyên lý & Thông số Chuẩn
Dựa trên tài liệu trong sổ, hệ thống xương mặt và Shape Keys cần tuân thủ các quy tắc không gian và hình học sau:

* **Quy tắc đặt vị trí xương mặt (Facial Bone Placement):**
  * **Xương hàm (Jaw Hinge Bone):** Đặt gần xương tai (ear bone) để tạo điểm xoay nhai (mastication pivot) tự nhiên [1, 2].
  * **Xương môi trên & dưới (Upper & Lower Lip Bones):** Phải tách biệt khoảng cách rõ ràng; nếu đặt quá gần nhau, thuật toán tính trọng số nhiệt (volumetric heat diffusion) sẽ làm khâu dính hai môi lại [1, 2].
  * **Xương cằm (Chin Bones):** Đặt nằm sâu bên trong thể tích của lưới (mesh volume). Việc đặt quá gần bề mặt sẽ khiến trọng số bị lem (bleed) sang các vùng lân cận như xương đòn hoặc giáp ngực [1, 2].
  * **Xương trán (Forehead Bones):** Đặt cao trên phần trán, xa khu vực lông mày để tránh xung đột trọng số ở vùng mặt trên [1, 2].
* **Căn chỉnh hình học & Nâng cấp Facial Rig:**
  * Khi nâng cấp hệ thống điều khiển Master Control cho môi và lông mày, nếu gặp lỗi căn chỉnh dạng `RIGIFY ERROR: Bone 'cheek_glue.T.L.001'`, cần dùng con trỏ 3D (`Shift + S -> Cursor to Selected` và `Selection to Cursor`) để đưa khớp xương về đúng vị trí hình học [2, 5].
* **Shape Keys trong Pipeline:**
  * Shape Keys cho phép điều chỉnh hình dạng linh hoạt và có thể diễn hoạt được ngay cả khi mô hình được liên kết dạng Library Overrides [4]. Tuy nhiên, Shape Keys không được tính đến trực tiếp khi tính trọng số tự động nên cần được hiệu chỉnh độc lập [3].

*Lưu ý:* Tài liệu trong sổ chưa bao hàm các con số góc gập cụ thể (như 45° hay 90°) hoặc biểu thức toán học chi tiết thiết lập cho Driver Shape Key. 

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Thao tác thủ công trong Blender:
1. **Đặt vị trí xương:** Căn chỉnh xương hàm, môi, cằm và trán chuẩn theo các quy tắc vị trí ở mục 2 [1, 2].
2. **Tạo Shape Key hiệu chỉnh (Corrective Shape Key):** Xoay xương mặt đến góc tối đa, sau đó thêm Shape Key mới trên Mesh và nắn lại khối cơ cho đẹp mắt.
3. **Thêm Driver:** Nhấp chuột phải vào thanh **Value** của Shape Key -> chọn **Add Driver**.
4. **Cấu hình Driver:**
   * **Type:** Select *Scripted Expression*.
   * **Variable Type:** Chọn *Transform Channel* hoặc *Rotational Difference*.
   * **Target:** Chọn Armature và đặt Bone target là xương điều khiển tương ứng.
   * **Mode / Space:** Đặt `Transform Space` thành *Local Space* và chọn trục xoay (ví dụ `Rotation X`).
   * **Expression:** Nhập biểu thức toán học (ví dụ: `clamp(var / 0.5, 0.0, 1.0)`) để khi góc xoay đạt ngưỡng mong muốn, Shape Key sẽ tăng tuyến tính từ 0.0 đến 1.0.

#### Hướng dẫn thiết lập bằng Script Python (`bpy`):
*(Đoạn mã mẫu dưới đây giúp tự động hóa quá trình gán Driver cho Shape Key dựa trên góc xoay của xương mặt)*:

```python
import bpy

# 1. Lấy đối tượng Mesh và Armature
mesh_obj = bpy.data.objects.get("Character_Mesh")
armature_obj = bpy.data.objects.get("Character_Rig")

if mesh_obj and mesh_obj.data.shape_keys:
    shape_keys = mesh_obj.data.shape_keys.key_blocks
    
    # 2. Chọn Corrective Shape Key cần gán Driver
    sk = shape_keys.get("Jaw_Open_Corrective")
    
    if sk:
        # Thêm Driver vào thuộc tính value của Shape Key
        driver_curve = sk.driver_add("value")
        driver = driver_curve.driver
        driver.type = 'SCRIPTED'
        
        # 3. Tạo biến liên kết với góc xoay trục X của xương hàm (jaw)
        var = driver.variables.new()
        var.name = "jaw_rot"
        var.type = 'TRANSFORM'
        
        target = var.targets
        target.id = armature_obj
        target.bone_target = "jaw"            # Tên xương điều khiển
        target.data_path = 'rotation_euler' # Trục xoay X
        target.transform_type = 'ROT_X'
        target.transform_space = 'LOCAL_SPACE'
        
        # 4. Biểu thức điều khiển (Giới hạn giá trị Shape Key trong khoảng [0.0, 1.0])
        driver.expression = "clamp(jaw_rot / 0.5, 0.0, 1.0)"
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1. **Dính môi khi Bind Automatic Weights:** Đặt xương môi trên và dưới quá gần nhau làm cho thuật toán tính trọng số khâu dính hai môi lại [1, 2].
   * *Cách kiểm tra:* Kiểm tra khoảng cách giữa hai hàng xương môi trong Metarig trước khi nhấn *Generate Rig* và *Bind Automatic Weights* [1, 2].
2. **Lem trọng số sang vùng cổ/ngực:** Xương cằm nằm quá gần bề mặt mesh làm lem trọng số ra ngoài [1, 2].
   * *Cách kiểm tra:* Đảm bảo đầu xương cằm nằm sâu bên trong thể tích của lưới [1, 2].
3. **Lỗi đứt gãy kết nối xương Glue (`cheek_glue` Error):** Xương dạng glue bị lệch khớp làm script tạo rig bị đứt đoạn [2, 5].
   * *Cách kiểm tra:* Đặt 3D Cursor vào đỉnh khớp Octahedral target (`Shift + S -> Cursor to Selected`), chọn đuôi xương glue và chọn `Selection to Cursor` để căn chỉnh lại [2, 5].
4. **Vòng lặp phụ thuộc (Dependency Loop) ở Driver:** Lập trình Driver tạo sự phụ thuộc vòng giữa vị trí lưới và biến đổi của xương làm hệ thống bị lag hoặc phản hồi sai vị trí [6].
   * *Cách kiểm tra:* Mở *System Console* của Blender để kiểm tra xem có thông báo lỗi "Dependency Cycle Detected" hay không, và đảm bảo Driver chỉ đọc dữ liệu xoay Local Space của xương mà không bị ảnh hưởng ngược lại bởi Mesh.

---

💡 Bạn có muốn tìm hiểu thêm về cách quản lý các Shape Keys biểu cảm này trong Pose Library hoặc tối ưu hóa Pipeline Rigify cho nhân vật không?
