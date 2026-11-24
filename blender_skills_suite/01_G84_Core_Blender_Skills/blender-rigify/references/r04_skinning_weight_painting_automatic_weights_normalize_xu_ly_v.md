# [R04] Skinning & Weight Painting: Automatic Weights, Normalize, xử lý vùng vai, hông và khớp gấp

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

Kỹ thuật gán da tự động (**Parent With Automatic Weights**) và tinh chỉnh trọng số (**Weight Paint**) tại các vùng khớp phức tạp (bả vai, nách, háng, khuỷu tay) kết hợp tính năng **Auto-Normalize** và **Mirror Vertex Groups** trong Blender:

---

### 1. Tóm tắt Bản chất (2-3 câu)
**Parent With Automatic Weights** là kỹ thuật liên kết lưới nhân vật (Mesh) vào khung xương (Armature) bằng thuật toán phân tán nhiệt thể tích (Laplacian heat diffusion), giúp tự động tính toán trọng số biến dạng cho từng đỉnh lưới [1]. Kỹ thuật này đóng vai trò quyết định trong quy trình rigging, giúp nhân vật chuyển động tự nhiên; việc kết hợp tinh chỉnh **Weight Paint** cùng tính năng **Auto-Normalize** và **Mirror Vertex Groups** giúp xử lý các khu vực biến dạng rắc rối, tránh hiện tượng móp xẹp, Lem trọng số hoặc méo lưới khi pose nhân vật [1-3].

---

### 2. Nguyên lý & Thông số Chuẩn

* **Nguyên lý Laplacian Heat Diffusion Solver**: Thuật toán tính toán khoảng cách thể tích từ các xương biến dạng (**Deform Bones**) đến từng đỉnh trên lưới [1, 4]. Thuật toán đòi hỏi lưới phải là hình thể khép kín (**manifold mesh**), không có đỉnh trùng, ranh giới hở hay hình học tự giao [1, 4].
* **Quy tắc định vị xương chuẩn**:
  * **Độ uốn nắn khớp (Hinge Alignment)**: Khớp khuỷu tay (elbows) và đầu gối (knees) bắt buộc phải đặt uốn cong nhẹ về phía trước trong **Edit Mode** để định hướng chính xác cho các bộ giải Inverse Kinematics (IK), tránh hiện tượng giật hoặc lật ngược khớp [5, 6].
  * **Định vị đối xứng (X-Axis Mirror)**: Kích hoạt `X-Axis Mirror` trong Edit Mode để duy trì sự đối xứng qua mặt phẳng dọc (sagittal plane) [2, 5].
* **Thông số & Quy trình xử lý tự động khi gán da thất bại**:
  * **Quy trình Phóng đại 10x (10x Scale Pipeline)**: Khi mô hình quá nhỏ làm vượt giới hạn độ chính xác thể tích của bộ giải Laplacian, phóng đại rig và mesh lên 10 lần (`S -> 10 -> Enter`), gán `Automatic Weights`, sau đó thu nhỏ về kích thước ban đầu (scale x0.1 / `Alt + S`) [7-9].
  * **Quy trình Tách phần rời (Loose Parts Separation Pipeline)**: Tách các khối lưới rời rạc/chồng lấp (`Edit Mode` -> `P` -> `Separate by Loose Parts`), chọn tất cả cùng khung xương để gán `With Automatic Weights`, sau đó gộp lại bằng `Ctrl + J` [7, 10].
  * **Thời gian phản hồi chuẩn**: Khoảng dừng ngắn dưới 1 giây (< 1s) ngay sau khi bấm gán trọng số xác nhận Blender đã tính toán bản đồ trọng số thành công [8, 11].
* **Cơ chế Auto-Normalize & Mirror Vertex Groups**:
  * **Auto-Normalize**: Tự động cân bằng tổng trọng số của tất cả các vertex group tác động lên một đỉnh luôn bằng \\(1.0\\) (\\(100\%\\)), ngăn ngừa hiện tượng đỉnh bị kéo bởi nhiều xương vượt quá \\(100\%\\) hoặc thiếu trọng số gây biến dạng kì dị.
  * **Mirror Vertex Groups / Symmetry**: Tự động đối xứng nét vẽ trọng số giữa các xương bên trái (`.L`) và bên phải (`.R`).

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác trên giao diện Blender (UI)
1. **Chuẩn bị mô hình**:
   * Chuẩn hóa biến dạng: Chuyển sang **Object Mode**, chọn Mesh và Rig, bấm `Ctrl + A` -> **All Transforms** [2].
   * Làm sạch lưới: Vào **Edit Mode**, chọn toàn bộ lưới (`A`), bấm `Merge by Distance` để xóa đỉnh trùng [5] và tính lại hướng mặt phẳng (`Shift + N` -> **Recalculate Normals Outward**) [5].
2. **Thao tác Gán da (Parent With Automatic Weights)**:
   * Chuyển sang **Object Mode**, chọn **Mesh** trước, giữ `Shift` chọn **Armature** (Rig) sau [12, 13].
   * Bấm tổ hợp phím `Ctrl + P` -> Chọn **Armature Deform -> With Automatic Weights** [1, 12].
3. **Cấu hình & Tinh chỉnh trong Weight Paint Mode**:
   * Chọn Armature -> giữ `Shift` chọn Mesh -> Chuyển sang chế độ **Weight Paint Mode**.
   * Mở bảng điều khiển Sidebar (`N`) hoặc thanh công cụ Tool Settings ở góc trên:
     * Tích chọn **Auto-Normalize**.
     * Tích chọn **X-Axis Mirror** (hoặc Symmetry X).
   * **Sửa lỗi tại các vùng khó**:
     * Sử dụng công cụ **Smooth** (`Weights` -> **Smooth**, thiết lập Subset thành `All Groups`) [14].
     * Mở tính năng chọn đỉnh (**Vertex Selection Mode**) để khoanh vùng các đỉnh bị lem trọng số và dọn dẹp [14].

#### B. Đội mã Python (`bpy`) tự động hóa
```python
import bpy

# 1. Mở đối tượng Mesh và Armature
mesh_obj = bpy.data.objects.get("Character_Mesh")
armature_obj = bpy.data.objects.get("Character_Rig")

if mesh_obj and armature_obj:
    # Chuyển về Object Mode và bỏ chọn tất cả
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    # Chọn Mesh trước, chọn Armature sau (Active Object)
    mesh_obj.select_set(True)
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj

    # 2. Gán da tự động (Parent With Automatic Weights)
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # 3. Kích hoạt Weight Paint Mode trên Mesh
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')

    # Bật Auto-Normalize và Mirror Vertex Groups (X-Axis Symmetry)
    tool_settings = bpy.context.scene.tool_settings
    tool_settings.use_auto_normalize = True
    tool_settings.use_mesh_symmetry_x = True

    # 4. Thực hiện làm mịn trọng số (Smooth Weights) cho tất cả Vertex Groups
    bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=1)
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

* **Lỗi "Bone heat weighting: failed to find solution for one or more bones"**:
  * *Nguyên nhân*: Do mô hình có hình học tự giao (mắt, răng, trang phục nằm bên trong), đỉnh trùng chưa gộp, ranh giới phi đa giác (non-manifold) hoặc chi tiết quá nhỏ [1, 4, 7, 15].
  * *Khắc phục*: Sử dụng quy trình **10x Scale Pipeline** (phóng đại 10 lần trước khi bind) [7, 9] hoặc **Loose Parts Separation Pipeline** (tách rời các phần lưới, bind riêng rồi gộp lại bằng `Ctrl + J`) [7, 10].
* **Các lỗi lem trọng số (Weight Bleeding) phổ biến tại các vùng khó**:
  * **Bả vai & Nách**: Xương vai (`DEF-shoulder`) hoặc xương bắp tay (`DEF-upperarm`) lem trọng số sang ngực và cổ; các đỉnh dưới nách quá sát nhau gây nhiễu tia tính toán của thuật toán [3, 16].
  * **Háng & Đùi**: Xương đùi (`DEF-thigh`) hoặc xương chậu (`DEF-pelvis`) lem trọng số sang chân bên kia hoặc lem lên hông/nách; ngược lại, xương sống (`DEF-spine`) có \\(0\%\\) trọng số ở vùng háng khiến háng bị móp/kéo giãn bất thường khi xoay chân [3].
  * **Khuỷu tay**: Bị xoắn hoặc méo dị dạng do không uốn nhẹ xương ở Edit Mode [6].
* **Phương pháp kiểm tra thực tế**:
  * **Xoay kiểm tra ở Pose Mode**: Chọn Armature, chuyển sang **Pose Mode** và xoay thử các xương ở góc lớn (ví dụ: giơ tay, gập chân) để phát hiện các khu vực lưới bị kéo giãn hoặc móp xẹp [3].
  * **Kiểm tra nhóm đỉnh (Vertex Selection)**: Trong chế độ Weight Paint Mode, bật chế độ chọn đỉnh để hiển thị danh sách chính xác các Vertex Group đang tác động lên từng đỉnh đơn lẻ [14].

---

💡 **Gợi ý tiếp theo**: Bạn có muốn tìm hiểu chi tiết hơn về kỹ thuật chuyển giao trọng số từ thân người sang trang phục (**Transfer Mesh Data / Vertex Group Transfer**) [17] hoặc cấu hình hệ thống chân bám địa hình thích ứng (**Terrain-Adaptive Feet IK**) [18, 19] không?
