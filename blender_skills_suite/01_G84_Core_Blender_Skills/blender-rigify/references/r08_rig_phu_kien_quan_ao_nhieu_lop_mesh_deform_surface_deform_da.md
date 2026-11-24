# [R08] Rig phụ kiện, quần áo nhiều lớp (Mesh Deform / Surface Deform / Data Transfer Weights)

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

Dưới đây là hướng dẫn chi tiết cách gắn xương và xử lý trọng số (Weight) cho các chi tiết phụ như quần áo rộng, tạp dề, tóc hoặc phụ kiện bằng kỹ thuật **Data Transfer** và các modifier biến dạng (**Surface Deform / Mesh Deform / Shrinkwrap**) để chống xuyên thủng (Clipping), được tổng hợp từ các tài liệu hướng dẫn rigging trong sổ.

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
Kỹ thuật **Data Transfer** và các modifier biến dạng (**Surface Deform / Mesh Deform**) cho phép chuyển đổi và sao chép trực tiếp không gian trọng số (Vertex Groups) từ bề mặt cơ thể nhân vật sang các lớp lưới phụ bọc ngoài như áo quần, tạp dề hay tóc [1]. Phương pháp này giúp phụ kiện và trang phục chuyển động đồng bộ tuyệt đối theo từng nếp gấp của cơ thể mà không cần vẽ trọng số thủ công từng xương [1]. Nhờ đó, hiện tượng thịt/da đâm xuyên qua vải (**Clipping**) được loại bỏ triệt để trong quá trình diễn họa animation [1].

---

### 2. **Nguyên lý & Thông số Chuẩn**

#### **A. Quy trình Chuyển Trọng số (Data Transfer / Transfer Mesh Data)**
Khi chuyển giao trọng số từ lưới cơ thể (Body Mesh) sang lưới trang phục (Clothing Mesh), cần thiết lập các tham số chuẩn sau [2]:
* **Data Type:** `Vertex Groups` (Nhóm đỉnh / Trọng số xương) [2].
* **Vertex Mapping:** `Nearest Face Interpolated` (Nội suy theo mặt gần nhất) giúp tính toán khoảng cách và nội suy trọng số mịn màng nhất giữa hai bề mặt lưới [2].
* **Source Layers Selection:** `All Layers` (Sao chép toàn bộ các lớp nhóm đỉnh tương ứng với khung xương) [2].

#### **B. Quy trình Xử lý Lỗi Gán Weight Tự động (Troubleshooting Pipelines)**
Khi gắn xương cho trang phục hoặc mô hình phức tạp có nhiều chi tiết rời rạc, bộ giải Laplacian Heat Diffusion của Blender thường thất bại và báo lỗi *“Bone heat weighting: failed to find solution for one or more bones”* do hình học chồng chéo [3-5]. Tài liệu cung cấp 2 quy trình tự động để khắc phục [4]:
1. **Loose Parts Separation Pipeline (Tách rời chi tiết rời)** [4]:
   * Vào **Edit Mode**, chọn toàn bộ đỉnh (\\(A\\)) và thực hiện `P -> Separate by Loose Parts` để tách trang phục, tóc, răng thành các vật thể độc lập [4, 6, 7].
   * Chọn tất cả các phần đã tách cùng với Armature, nhấn `Ctrl + P -> With Automatic Weights` [4, 6].
   * Chọn lại các phần lưới và gộp lại bằng `Ctrl + J` [4, 6].
2. **The 10x Scale Pipeline (Phóng to 10 lần)** [4]:
   * Phóng to Armature và Mesh lên **10 lần** (`S -> 10 -> Enter`) để vượt qua giới hạn độ chính xác thể tích của bộ giải [4, 8].
   * Thao tác `Parent With Automatic Weights`, sau đó reset lại tỉ lệ (`Alt + S` hoặc `S * 0.1`) [4, 8].

#### **C. Chuẩn hóa Tọa độ & Ràng buộc Bề mặt (Shrinkwrap / Surface Deform)**
* **Apply All Transforms (`Ctrl + A`)**: Bắt buộc phải đưa Location, Rotation và Scale của cả Rig và các Mesh về trạng thái chuẩn trước khi gán modifier hoặc bind trọng số [9-11]. Nếu không Apply Transforms, thuật toán Shrinkwrap hay Data Transfer sẽ tính toán sai tọa độ không gian làm lưới bị biến dạng văng ra xa [10, 11].
* **Wrap Method (Shrinkwrap)**: Sử dụng phương thức `Project` hoặc `Nearest Surface Point`, bật cả hai chiều `Positive` và `Negative` cùng tùy chọn `Align to Normal` để giữ khoảng cách an toàn so với bề mặt da [12-14].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### **Các bước thao tác trên giao diện Blender (GUI):**
1. **Chuẩn bị:** Chọn Mesh trang phục/tóc, chọn Mesh cơ thể. Nhấn `Ctrl + A -> All Transforms` để chuẩn hóa dữ liệu không gian [9].
2. **Data Transfer:** 
   * Chọn Mesh trang phục, thêm modifier **Data Transfer**.
   * Tại ô **Target**, chọn Mesh cơ thể (Body Object) [1].
   * Tích chọn **Vertex Data** -> Chọn **Vertex Groups** [2].
   * Mục **Mapping**, chọn `Nearest Face Interpolated` [2].
   * Nhấn nút **Generate Data Layers** để tự động khởi tạo các nhóm đỉnh tương ứng trên trang phục.
3. **Surface Deform (Dành cho trang phục rộng/Tạp dề/Váy):**
   * Thêm modifier **Surface Deform** vào lưới trang phục bên dưới Data Transfer.
   * Chọn **Target** là Mesh cơ thể.
   * Nhấn nút **Bind** để khóa bề mặt trang phục theo sát biến dạng của cơ thể.

#### **Đoạn mã Python (`bpy`) tự động hóa thiết lập:**

```python
import bpy

# Đặt tên cho đối tượng Trang phục (Clothing) và Cơ thể (Body)
clothing_name = "Clothing_Mesh"
body_name = "Body_Mesh"

clothing_obj = bpy.data.objects.get(clothing_name)
body_obj = bpy.data.objects.get(body_name)

if clothing_obj and body_obj:
    # 1. Chuyển sang Object Mode và đặt Clothing làm Active Object
    bpy.ops.object.select_all(action='DESELECT')
    clothing_obj.select_set(True)
    body_obj.select_set(True)
    bpy.context.view_layer.objects.active = clothing_obj
    
    # Apply Transforms để tránh lỗi tọa độ
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # 2. Thêm và cấu hình Data Transfer Modifier
    dt_mod = clothing_obj.modifiers.new(name="DataTransfer_Weights", type='DATA_TRANSFER')
    dt_mod.target = body_obj
    dt_mod.use_vert_data = True
    dt_mod.data_types_verts = {'VGROUP_WEIGHTS'}
    dt_mod.vert_mapping = 'POLYINTERP_NEAREST'  # Nearest Face Interpolated
    
    # Tạo các Vertex Groups tương ứng trên đối tượng Clothing
    bpy.ops.object.datablock_create_vgroup_associated()
    print("Đã sao chép Vertex Groups từ Body sang Clothing thành công!")

    # 3. Thêm và cấu hình Surface Deform Modifier (Chống Clipping)
    sd_mod = clothing_obj.modifiers.new(name="SurfaceDeform_Bind", type='SURFACE_DEFORM')
    sd_mod.target = body_obj
    sd_mod.falloff = 4.0

    # Thực hiện Bind cho Surface Deform
    # Lưu ý: Yêu cầu cả 2 mesh đều không có lỗi nếp gấp rỗng (non-manifold)
    try:
        bpy.ops.object.surfacedeform_bind(modifier=sd_mod.name)
        print("Đã Bind Surface Deform thành công!")
    except Exception as e:
        print(f"Không thể Bind Surface Deform: {e}")
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

* **Lỗi "Bone heat weighting: failed to find solution" khi gán xương trực tiếp**:
  * *Nguyên nhân:* Do trang phục có các mặt cắt rời, chi tiết chồng chéo (dây kéo, nút áo, nếp gấp) làm nhiễu thuật toán lan truyền nhiệt [3-5, 15].
  * *Cách xử lý:* Áp dụng quy trình **Loose Parts Separation** (`P -> Separate by Loose Parts` trước khi gán weight) hoặc dùng **Data Transfer** sao chép weight từ lưới cơ thể đã chuẩn hóa thay vì chạy Auto-Weights trực tiếp trên áo [1, 4, 6].
* **Lỗi biến dạng/văng lưới khi di chuyển (Stretchy / Floating Mesh)**:
  * *Nguyên nhân:* Quên chưa Apply Scale/Rotation trên Armature hoặc Mesh trước khi thực hiện liên kết [10, 11].
  * *Cách kiểm tra:* Kiểm tra bảng N-Panel (`Item -> Scale`). Nếu chỉ số Scale khác `(1.0, 1.0, 1.0)`, hãy bấm `Ctrl + A -> Apply All Transforms` [9].
* **Trang phục bị kéo giãn bất thường ở vùng ranh giới (Giữa nách, háng)**:
  * *Nguyên nhân:* Trọng số từ các xương đùi/cánh tay lan quá rộng sang các vùng lân cận [16].
  * *Cách xử lý:* Chuyển sang **Weight Paint Mode**, bật tính năng **Vertex Selection**, chọn vùng bị lỗi và truy cập menu `Weights -> Smooth` (đặt tùy chọn Subset thành `All Groups`) để làm mịn vùng chuyển tiếp trọng số [2, 17].
* **Sai thứ tự Stack Modifier**:
  * *Nguyên nhân:* Đặt **Armature Modifier** nằm trên **Data Transfer** hoặc **Surface Deform**.
  * *Cách kiểm tra:* Luôn đảm bảo **Data Transfer** hoặc **Surface Deform** nằm ở trên cùng của Modifier Stack (hoặc đã được Apply) trước khi tính toán biến dạng theo xương của **Armature Modifier** [13].

---
💡 **Gợi ý bước tiếp theo:** Nếu bạn muốn tối ưu hóa thêm chuyển động cho phần vạt áo rộng hoặc tóc dài, ta có thể kết hợp thêm các xương chuỗi linh hoạt (*Rigify Tentacle/Tail Chains*) hoặc thiết lập mô phỏng vật lý vải (*Cloth Physics*) kết hợp với lưới Proxy. Bạn có muốn tìm hiểu chi tiết cách thiết lập này không?
