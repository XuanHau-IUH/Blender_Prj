# [R09] Tối ưu hóa Rig cho diễn xuất & Tự động hóa Pose (Pose Library, Sketch2Pose & Retargeting Mocap)

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

Hướng dẫn chi tiết về cách tổ chức **Bone Collections/Layers**, lưu và quản lý tư thế qua **Pose Library trong Asset Browser**, cùng nguyên lý **Retargeting (Ánh xạ chuyển động)** lên bộ xương Rigify trong Blender dựa trên tài liệu:

---

### 1. Tóm tắt Bản chất (2-3 câu)
**Tổ chức Bone Collections, Pose Library và Retargeting** là bộ ba quy trình cốt lõi giúp chuẩn hóa và tối ưu hóa đường ống (pipeline) diễn họa nhân vật 3D trong Blender [cite: 7, 16, 194]. Việc phân chia tập hợp xương giúp người diễn họa dễ dàng quản lý hệ thống điều khiển phức tạp, trong khi Pose Library cho phép lưu trữ và tái sử dụng các tư thế chuẩn một cách nhanh chóng [cite: 16, 294]. Đồng thời, kỹ thuật Retargeting giúp truyền dữ liệu chuyển động từ các nguồn 2D/3D bên ngoài lên bộ xương Rigify mà không phải làm lại thủ công từ đầu [cite: 194, 208].

---

### 2. Nguyên lý & Thông số Chuẩn

*   **Tổ chức Bone Collections / Layers (Blender 4.0+):**
    *   Từ phiên bản Blender 4.0, hệ thống Bone Layers cũ đã được thay thế hoàn toàn bằng **Bone Collections** [cite: 294].
    *   Các tập hợp xương mới được quản lý qua giao diện **Bone Collection UI** và phải gán mã loại Rigify (*Rigify Type*) cho xương gốc (root bone) của chuỗi, như: `basic.super_copy`, `limbs.simple.tentacle`, hoặc `spines.basic_tail` [cite: 294, 295, 296].
    *   **Quy tắc đối xứng:** Các xương hai bên phải mang hậu tố chuẩn `.L` hoặc `.R` (ví dụ: `shoulder.L`, `knee.R`) để Blender tự động nhận diện khi thực hiện thao tác **Symmetrize** [cite: 19, 297].

*   **Quản lý Pose Library & Asset Browser:**
    *   Mỗi tư thế (*Pose Asset*) thực chất là một khối dữ liệu **Action 1 frame duy nhất** (*single-frame Action data-block*) [cite: 16, 390].
    *   Một Pose Asset hỗ trợ tính năng **Slots**, cho phép lưu trữ dữ liệu tư thế của nhiều bộ xương/nhân vật khác nhau trong cùng một asset [cite: 16, 391].
    *   **Thông số xem trước (Preview):** Ảnh xem trước của pose được xuất bằng **Workbench Engine** với camera active của Scene [cite: 63, 168, 396-397]. Tỷ lệ khung hình khuyến nghị là hình vuông (ví dụ: **\\(500 \times 500\\) pixel**) [cite: 166].
    *   **Trộn tư thế (Pose Blending):** Kéo chuột sang phải để hòa trộn tư thế thư viện vào tư thế hiện tại, kéo sang trái để trừ bớt [cite: 20, 400]. Nhấn phím **Tab** để bật/tắt so sánh, và phím **E** (*Extrapolate*) để suy rộng vượt quá \\(100\%\\) [cite: 20, 400].

*   **Nguyên lý & Thông số Retargeting:**
    *   **Khung tọa độ khớp:** Quá trình ánh xạ trích xuất dữ liệu từ **22 khớp xương chính** (như `pelvis`, `left/right foot`, `head`, `left/right wrist`) [cite: 207, 253].
    *   **Không gian đặc trưng chuyển động:** Chuẩn hóa dữ liệu dưới dạng ma trận đặc trưng \\(D = 263\\) chiều trên từng đoạn chuyển động (thường mặc định \\(N = 40\\) frames, tương đương 2 giây ở tốc độ 20 fps) [cite: 208-210].
    *   **Liên kết và Ghi đè (Library Override):** Bộ xương Rigify khi được liên kết (*Link*) từ file gốc sẽ ở dạng chỉ đọc; cần thực hiện **Make Library Override** để tạo khối ghi đè cục bộ cho phép áp dụngRetargeting và đặt keyframe [cite: 25-26, 265].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác trên giao diện (UI Workflow)
1.  **Thiết lập Metarig & Tạo Bone Collections:**
    *   Đặt nhân vật tại gốc tọa độ World (\\(0,0,0\\)), chọn lưới (mesh) và nhấn `Ctrl + A` -> **All Transforms** [cite: 9].
    *   Bật **X-Axis Mirror** và **In Front** trong mục Viewport Display của Armature [cite: 8, 9].
    *   Uốn nhẹ khớp gối và khuỷu tay về phía trước để định hướng cho IK solver [cite: 10, 30].
    *   Vào tab *Armature Properties* -> **Bone Collections**, tạo các collection mới (vd: *FK_Controls*, *IK_Controls*) và gán màu đại diện [cite: 294].
    *   Nhấn nút **Generate Rig** để tạo bộ xương Rigify hoàn chỉnh [cite: 8, 302].

2.  **Lưu tư thế vào Pose Library:**
    *   Mở cửa sổ **Asset Browser**, chuyển tùy chọn thư viện ở thanh Header thành **Current File** [cite: 17, 74, 168].
    *   Chuyển Rigify sang **Pose Mode**, chỉnh tư thế cho nhân vật và chọn các xương cần lưu [cite: 17, 393].
    *   Vào menu Header của 3D Viewport: `Pose` -> **Create Pose Asset** (hoặc nhấn *Create Pose Asset* trong Action Editor / Asset Browser) [cite: 17, 393].
    *   Để áp dụng tư thế đảo ngược, nhấp chuột phải vào tư thế trong Asset Browser và chọn **Apply Pose Flipped** [cite: 19, 172, 400].

3.  **Thực hiện Link và Library Override cho Retargeting:**
    *   Vào file làm việc chính: `File` -> `Link` -> chọn tập hợp nhân vật (*Character Collection*) từ file gốc [cite: 25, 369].
    *   Chọn Collection vừa Link trong Viewport, truy cập: `3D Viewport Header` -> `Object` -> `Relations` -> **Make Library Override** [cite: 26, 371-372].

#### B. Mã nguồn Python (`bpy`) tự động hóa

```python
import bpy

# ==============================================================================
# 1. TẠO VÀ GÁN BONE COLLECTION (BLENDER 4.0+)
# ==============================================================================
armature_obj = bpy.context.active_object

if armature_obj and armature_obj.type == 'ARMATURE':
    armature_data = armature_obj.data
    
    # Kiểm tra hỗ trợ Bone Collections (Blender 4.0+)
    if hasattr(armature_data, "collections"):
        # Tạo Bone Collection mới
        coll_name = "Arm_Controls"
        bone_coll = armature_data.collections.get(coll_name)
        if not bone_coll:
            bone_coll = armature_data.collections.new(name=coll_name)
        
        # Gán các xương đang chọn vào Collection
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in bpy.context.selected_editable_bones:
            bone_coll.assign(bone)
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"Đã gán xương vào Collection: {coll_name}")

# ==============================================================================
# 2. ĐÁNH DẤU ACTION HIỆN TẠI THÀNH POSE ASSET VÀ TẠO ANH XEM TRƯỚC
# ==============================================================================
if armature_obj and armature_obj.animation_data and armature_obj.animation_data.action:
    active_action = armature_obj.animation_data.action
    
    # Đánh dấu Action là Pose Asset trong Asset Browser
    active_action.asset_mark()
    
    # Tự động tạo ảnh xem trước (Preview) cho Asset
    active_action.asset_generate_preview()
    print(f"Đã lưu Action '{active_action.name}' thành Pose Asset thành công.")

# ==============================================================================
# 3. THỰC HIỆN MAKE LIBRARY OVERRIDE BẰNG PYTHON
# ==============================================================================
selected_objs = bpy.context.selected_objects
for obj in selected_objs:
    if obj.override_library is None and obj.type == 'EMPTY':
        # Áp dụng Library Override cho đối tượng được Link
        obj.override_hierarchy_create(
            scene=bpy.context.scene,
            view_layer=bpy.context.view_layer
        )
        print(f"Đã tạo Library Override cho: {obj.name}")
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1.  **Lỗi "Create Pose Asset" bị ẩn hoặc báo xám (Greyed out):**
    *   *Nguyên nhân:* Asset Browser chưa được thiết lập về thư viện tập tin hiện tại [cite: 17, 74, 346].
    *   *Cách khắc phục:* Mở cửa sổ Asset Browser, tìm ô chọn thư viện ở góc trên và chuyển từ *"All Libraries"* sang **"Current File"** [cite: 17, 74, 168, 346].

2.  **Lỗi gán trọng số tự động thất bại (`Bone heat weighting: failed to find solution`):**
    *   *Nguyên nhân:* Lưới nhân vật có các hình thể tự giao nhau (răng, mắt, tóc), đỉnh trùng lặp, hoặc kích thước lưới quá nhỏ làm solver Laplacian bị lỗi tính toán toán học [cite: 13, 14, 40].
    *   *Cách kiểm tra & khắc phục (Quy trình 10x Scale):*
        1. Phóng to bộ xương và lưới lên 10 lần (`S` -> `10` -> `Enter`) và gán lại với **Automatic Weights** [cite: 14, 310].
        2. Hoặc vào Edit Mode, chọn tất cả đỉnh và nhấn `P` -> **Separate by Loose Parts** để tách rời các chi tiết hình thể trước khi gán weights, sau đó nối lại bằng `Ctrl + J` [cite: 14, 41].

3.  **Lỗi khởi tạo Rigify (`RIGIFY ERROR: Bone 'cheek_glue...' Could not match control node`):**
    *   *Nguyên nhân:* Các xương phụ mặt (glue bones) bị đứt liên kết phụ thuộc với xương khớp octahedral mục tiêu [cite: 12, 300].
    *   *Cách khắc phục:* Chọn khớp mục tiêu trong Edit Mode -> nhấn `Shift + S` chọn **Cursor to Selected** -> chọn đầu xương glue bị hỏng -> nhấn `Shift + S` chọn **Selection to Cursor** để hít khớp xương vào vị trí chuẩn [cite: 13, 300].

4.  **Lỗi trượt chân (Foot-sliding) khi thay đổi tỷ lệ (Scale) nhân vật đã gán keyframe:**
    *   *Nguyên nhân:* Giá trị dịch chuyển (Location) của xương điều khiển không tự động co giãn theo tỷ lệ Rig trong Object Mode [cite: 27, 28].
    *   *Cách khắc phục:* Theo công thức biến đổi \\(Y' = s \cdot Y\\) (với \\(s\\) là hệ số tỷ lệ) [cite: 28]:
        1. Áp dụng Scale cho Armature (`Ctrl + A` -> *Scale*) [cite: 28].
        2. Mở cửa sổ **Graph Editor**, lọc các kênh chuyển động theo từ khóa `Location` [cite: 28].
        3. Đặt **2D Pivot Point** về vị trí **2D Cursor** tại góc tọa độ (Frame: 1, Value: 0) [cite: 28].
        4. Chọn tất cả đường cong Location và thu phóng theo trục Y theo hệ số \\(s\\) (`S` -> `Y` -> nhập \\(s\\)) [cite: 28].

---

💡 **Gợi ý bước tiếp theo:** Bạn có muốn tôi hỗ trợ viết một đoạn script Python nâng cao để tự động gán toàn bộ tập hợp xương (*Bone Collections*) và gán màu (*Color Sets*) hàng loạt cho bộ xương Rigify không?
