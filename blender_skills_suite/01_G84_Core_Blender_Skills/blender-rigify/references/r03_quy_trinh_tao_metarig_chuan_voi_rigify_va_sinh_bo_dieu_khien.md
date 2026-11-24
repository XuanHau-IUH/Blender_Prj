# [R03] Quy trình tạo Metarig chuẩn với Rigify và sinh bộ điều khiển (Generate Rig)

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

Dưới đây là hướng dẫn chi tiết từng bước về quy trình sử dụng add-on **Rigify** trong Blender để thiết lập bộ xương nhân vật (Human Metarig), căn chỉnh các khớp và tạo bộ điều khiển (Generate Rig) không bị lỗi [1-3].

---

### 1. Tóm tắt Bản chất
**Rigify** là một add-on tích hợp sẵn trong Blender giúp tự động hóa đến **75%** quy trình rigging nhân vật bằng cách sinh ra hệ thống điều khiển IK/FK và các xương chỉnh sửa (tweak bones) phức tạp từ một khung xương mẫu (Metarig) [1, 3]. Khung **Human Metarig** đóng vai trò là sơ đồ định vị không gian; việc căn chỉnh chính xác Metarig khớp với hình khối mesh sẽ quyết định tính chính xác của bộ điều khiển sinh ra và khả năng gán trọng số tự động (Automatic Weights) [2, 4, 5]. Do đó, việc làm sạch lưới mesh và tuân thủ các quy tắc đặt xương không gian là yếu tố cốt lõi để tránh mọi sự cố khi khởi tạo rig [1, 6, 7].

---

### 2. Nguyên lý & Thông số Chuẩn

* **Tọa độ và Biến đổi (Transforms):** Mô hình nhân vật và Metarig phải được đặt chính xác tại **World Origin** (gốc tọa độ thế giới) [4, 8]. Trước khi khởi tạo rig, toàn bộ giá trị vị trí, góc xoay và tỷ lệ phải được áp dụng hoàn toàn (`Ctrl + A` -> **All Transforms** hoặc **Apply Rotation and Scale**) để tránh hiện tượng khung rig bị co rút hay lệch vị trí [4, 8, 9].
* **Định hướng khớp bản lề (Hinges):** Khuỷu tay (elbows) và đầu gối (knees) bắt buộc phải được uốn cong nhẹ về phía trước trong không gian 3D [10, 11]. Góc cong nhẹ này hướng dẫn cho bộ giải Động học ngược (IK Solvers) xác định đúng mặt phẳng co duỗi giải phẫu, ngăn ngừa lỗi lật gãy chi khi diễn hoạt [10, 11]. Xương gót chân (heel) phải nằm trên cùng một đường nằm ngang với xương ngón chân (toe) [10, 11].
* **Căn chỉnh ngón tay:** Dùng công cụ chọn hình tròn (`C`) để thao tác nhanh với các nhóm xương ngón tay [4, 11]. Các xương ngón tay phải nằm trung tâm khối mesh, uốn nhẹ theo khớp và có mặt phẳng của hình octahedral hướng xuống dưới để tránh hiện tượng ngón tay bị xoắn hông khi cuộn nắm đấm [11, 12].
* **Tỷ lệ và Vị trí xương khuôn mặt (Facial Bones):**
  * **Xương khớp hàm (`jaw`):** Đặt tâm xoay của khớp hàm gần xương tai (`ear`) để mô phỏng chuyển động nhai tự nhiên [13, 14].
  * **Xương môi (`lip`):** Tách rời khoảng cách giữa xương môi trên và môi dưới, tránh đặt quá sát làm thuật toán gán trọng số tự động khâu dính miệng nhân vật [13, 14].
  * **Xương cằm (`chin`):** Đặt chìm sâu bên trong thể tích khối mesh trán/cằm; nếu đặt quá gần bề mặt, trọng số sẽ bị lem sang vùng cổ hoặc giáp ngực [13, 14].
  * **Xương trán (`forehead`):** Đặt cao ở nửa trên vùng trán, cách xa lông mày để tránh xung đột trọng số [13, 14].
* **Quy tắc bảo toàn cấu trúc xương:** Không được phép xóa lẻ các xương khỏi Metarig mặc định ngay cả khi nhân vật không có tai hay đuôi [4, 14]. Việc xóa lẻ xương sẽ làm hỏng cấu trúc chuỗi xương (Rigify Type) và khiến script sinh rig bị lỗi [4, 15]. Nếu không dùng đến, hãy ẩn xương hoặc loại chúng khỏi nhóm biến dạng [4, 14]. *(Lưu ý: Nếu muốn bỏ hoàn toàn khung mặt, phải chọn toàn bộ Bộ sưu tập xương mặt / Select Face bone collections và xóa sạch cùng lúc)* [16, 17].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Các bước thao tác thủ công trên giao diện
1. **Kích hoạt Add-on:** Vào `Edit` -> `Preferences` -> `Add-ons`, tìm "Rigify" và tích chọn kích hoạt [18, 19].
2. **Làm sạch Mesh:** Select toàn bộ nhân vật, vào `Edit Mode`, bấm `M` -> **By Distance** (khoảng cách `0.000`) để xóa đỉnh trùng [2, 20]. Bấm `Shift + N` để recalculate normals hướng ra ngoài [2, 21]. Nếu mesh có nhiều chi tiết rời (răng, mắt, trang phục), dùng `P` -> **Separate by Loose Parts** để tách riêng giúp gán trọng số không bị nhiễu [6, 22, 23].
3. **Thêm Metarig:** Bấm `Shift + A` -> `Armature` -> **Human (Meta-Rig)** [18, 24]. Bật thuộc tính **In Front** trong `Viewport Display` để xương luôn hiển thị đè lên mesh [2, 18, 25].
4. **Căn chỉnh Metarig (Edit Mode):** Bật tùy chọn **X-Axis Mirror** trên thanh công cụ để thao tác đối xứng hai bên [2, 4, 11]. Căn chỉnh vị trí các khớp tay, chân, cột sống, ngón tay và khuôn mặt theo đúng các tỷ lệ nguyên lý ở Phần 2 [4, 10, 13].
5. **Áp dụng Transforms:** Chuyển sang `Object Mode`, chọn Metarig và bấm `Ctrl + A` -> **All Transforms** [4, 9, 18].
6. **Tạo Rig điều khiển:** Chọn Metarig, vào tab `Object Data Properties` (biểu tượng xương màu xanh), tìm bảng *Rigify Buttons* và nhấn **Generate Rig** [18, 26].
7. **Parent Rig vào Mesh:** Chọn khối Mesh nhân vật trước, giữ `Shift` chọn bộ Rig vừa sinh ra (tên mặc định là `rig`), bấm `Ctrl + P` -> **With Automatic Weights** [5, 6, 18, 22].

#### B. Script Python (`bpy`) tự động hóa thiết lập ban đầu
Đoạn script dưới đây giúp tự động bật add-on, thêm Human Metarig, bật tính năng hiển thị đè và áp dụng biến đổi chuẩn bị cho bước căn chỉnh:

```python
import bpy

# 1. Kích hoạt Add-on Rigify trong Preferences
bpy.ops.preferences.addon_enable(module="rigify")

# 2. Thêm Human Metarig tại gốc tọa độ
bpy.ops.object.armature_human_metarig_add()
metarig = bpy.context.active_object
metarig.name = "Human_Metarig"

# Bật hiển thị In Front để dễ căn chỉnh trong Viewport
metarig.show_in_front = True

# 3. Chuyển sang Edit Mode và bật X-Axis Mirror để đối xứng
bpy.ops.object.mode_set(mode='EDIT')
metarig.data.use_mirror_x = True
bpy.ops.object.mode_set(mode='OBJECT')

# 4. Áp dụng toàn bộ Transform (Location, Rotation, Scale)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 5. Thực thi Generate Rig (Chạy sau khi đã căn chỉnh xong các xương)
# bpy.ops.pose.rigify_generate()
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

| Lỗi thường gặp | Nguyên nhân chính | Quy trình kiểm tra & Sửa lỗi |
| :--- | :--- | :--- |
| **`Bone heat weighting: failed to find solution...`** [6, 21, 27] | Mesh bị hở (non-manifold), có đỉnh trùng, hoặc các khối hình học tự giao cắt nhau (như răng, mắt bên trong hốc đầu) làm thuật toán Laplacian bị lỗi [6, 21, 28]. | **Sửa theo Quy trình Scale 10x:** Scale cả Rig và Mesh lên 10 lần (`S` -> `10` -> `Enter`), bind `Automatic Weights`, sau đó thu nhỏ lại tỷ lệ cũ (`Alt + S` hoặc `S * 0.1`) [22, 29, 30].<br>**Sửa theo Quy trình Tách Loose Parts:** Vào Edit Mode bấm `P` -> *Separate by Loose Parts*, parent riêng rẽ từng phần với Rig rồi ghép lại bằng `Ctrl + J` [22, 29, 31]. |
| **`RIGIFY ERROR: Bone 'cheek_glue...': Could not match control node...`** [14, 32] | Do xương kết nối khuôn mặt ("glue" bone) bị ngắt liên kết parent hoặc lệch tâm không gian sau khi nâng cấp mặt [14, 32]. | Vào **Edit Mode** của Metarig, chọn khớp nối mục tiêu, bấm `Shift + S` -> **Cursor to Selected** [32]. Chọn đầu xương glue bị gãy, bấm `Shift + S` -> **Selection to Cursor** để hít chặt hai điểm khớp vào nhau [14, 32]. |
| **Ngón tay xoắn/cuộn sai hướng (`Finger roll sideways`)** [12] | Do ngón tay trong Metarig đặt quá thẳng hoặc trục xoay Roll của xương ngón tay bị lệch [12]. | Trong Metarig Edit Mode, chỉnh các ngón tay uốn cong nhẹ [12]. Chọn các xương ngón tay bấm `Alt + R` để reset roll, hoặc chỉnh thuộc tính Roll trong thanh N-panel sao cho mặt phẳng của xương octahedral hướng xuống [12]. |
| **`Input to rig type must be a chain of 2 or more bones...`** [15] | Do lỡ tay xóa mất một xương lẻ nằm trong chuỗi xương bắt buộc của Rigify [4, 15]. | Không xóa lẻ từng xương [4]. Nếu không dùng mặt, hãy chọn toàn bộ tập hợp xương mặt (Select Face bone collection) và xóa toàn bộ bộ xương mặt cùng lúc [16, 17]. |

---

💡 **Bước tiếp theo gợi ý:** Bạn có muốn tìm hiểu quy trình thiết lập các ràng buộc chân bám sàn tự động (Terrain-Adaptive Feet IK) kết hợp giữa ràng buộc *Shrinkwrap* và *Floor* để nhân vật tự điều chỉnh bàn chân theo địa hình không bằng phẳng không? [33, 34]
