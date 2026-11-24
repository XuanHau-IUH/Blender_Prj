# [R01] Nguyên lý Armature, hệ thống phân cấp xương (Bone Hierarchy: Root, Spine, Limbs) và chuẩn hóa Mesh trước khi Rig

- **Chủ đề:** Gắn xương & Điều khiển Nhân vật (Character Rigging & Rigify)
- **Sổ NotebookLM nguồn:** `NB_Character_Rigging`
- **Cấp độ:** Cơ bản (Level 1)
- **Ngày trích xuất:** 2026-10-30

---

### 1. Tóm tắt Bản chất (2-3 câu)

Chuẩn bị mô hình 3D (Mesh) và căn chỉnh khung xương (Armature/Metarig) trước khi gắn Rig (Rigging/Binding) là quy trình làm sạch hình học, chuẩn hóa tọa độ không gian và thiết lập phân cấp giải phẫu tiêu chuẩn cho nhân vật [1-3]. Bước chuẩn bị này đảm bảo các thuật toán gán trọng số tự động (như thuật toán khuếch tán nhiệt Laplacian) tính toán chính xác, ngăn ngừa tình trạng lỗi biến dạng lưới, lem trọng số hoặc thất bại khi liên kết xương với mô hình [3-5].

---

### 2. Nguyên lý & Thông số Chuẩn

#### A. Chuẩn hóa Tọa độ & Biến đổi (Transforms & Origin)
* **Vị trí gốc tọa độ (World Origin):** Cả mô hình 3D và khung xương phải được đặt chính xác tại gốc tọa độ thế giới \\((0, 0, 0)\\) [3, 5].
* **Áp dụng biến đổi (Apply Scale / Rotation):** Bắt buộc phải áp dụng hoàn toàn các thông số biến đổi (**Ctrl + A** \\(\rightarrow\\) **All Transforms**) [3]. Tỷ lệ (Scale) của Mesh và Armature phải chuẩn về \\((1.0, 1.0, 1.0)\\) và Góc xoay (Rotation) về \\((0^\circ, 0^\circ, 0^\circ)\\) [3]. Nếu không áp dụng, các thuật toán gán trọng số tự động và các ràng buộc (Constraints) sẽ hoạt động sai lệch hoặc thất bại hoàn toàn [5].

#### B. Hình học & Topology (Lưới nhân vật)
* **Tính khép kín (Manifold Geometry):** Lưới nhân vật phải kín, không chứa lỗ thủng, không có đỉnh rải rác hay các cạnh rác [4, 5]. 
* **Hạn chế dùng Decimation:** Tránh dùng *Decimation Modifier* để giảm lưới vì thao tác này làm mất tính đối xứng hai bên (bilateral symmetry), tạo các mặt tam giác (triangles) gây lỗi thuật toán gán trọng số [1]. Thay vào đó, nên áp dụng quy trình **Smooth Remeshing** với các cấp độ Octree phù hợp để giữ topology sạch và đối xứng [1, 2].
* **Làm sạch hình học:** Xóa bỏ các đỉnh trùng lặp (*Merge by Distance / Remove Doubles*) và tính toán lại hướng pháp tuyến hướng ra ngoài (*Recalculate Normals Outward* với **Shift + N**) [2, 5].

#### C. Góc gập khớp (Joint Bends) & Trục đối xứng (Symmetry)
* **Góc gập định hướng IK:** Trong chế độ **Edit Mode**, các vị trí khớp chính như khuỷu tay và đầu gối **bắt buộc phải có độ cong gập nhẹ về phía trước** theo đúng mặt phẳng giải phẫu [2, 6]. Điều này giúp các bộ giải động học ngược (IK Solvers) xác định chính xác hướng gập của chân/tay, tránh hiện tượng khớp bị gập ngược bất thường khi diễn họa [6].
* **Căn chỉnh chân:** Xương gót chân (heel bone) phải nằm ngang hàng theo phương ngang với xương ngón chân (toe bone) để thiết lập mặt phẳng tiếp đất phẳng [6].
* **Đối xứng hai bên:** Nhân vật phải quay mặt về hướng trước (Front View - Numpad 1), căn chỉnh đối xứng qua mặt phẳng dọc (sagittal plane) và bật tính năng **X-Axis Mirror** trong Edit Mode khi chỉnh xương [2, 3].

#### D. Quyết tắc phân cấp xương & Xương mặt (Metarig Rules)
* **Phân cấp cơ bản:** Xương gốc/xương sống (Spine) \\(\rightarrow\\) Xương vai/đòn (Shoulder/Clavicles) \\(\rightarrow\\) Xương cánh tay/đùi \\(\rightarrow\\) Cẳng tay/cẳng chân \\(\rightarrow\\) Bàn tay/bàn chân [2, 7]. Các chuyển động kế thừa truyền từ xương cha sang xương con [8].
* **Không xóa xương mặc định của Metarig:** Tuyệt đối không xóa bất kỳ xương mặc định nào từ Metarig (ví dụ: xương tai, xương đuôi nếu nhân vật không có) vì sẽ làm hỏng script khởi tạo Rig (Generate Rig) [3]. Với các xương không dùng đến, hãy ẩn chúng hoặc loại bỏ khỏi nhóm đỉnh biến dạng (deform vertex groups) [3].
* **Khoảng cách xương mặt:** 
  * Bản lề xương hàm (*jaw hinge*) đặt gần xương tai [9].
  * Tách biệt xương môi trên và môi dưới để tránh thuật toán gán trọng số hàn dính miệng [9].
  * Đặt xương cằm (*chin*) sâu bên trong thể tích lưới; nếu đặt quá sát bề mặt, trọng số sẽ bị lem sang giáp ngực hoặc xương đòn [9].
  * Đặt xương trán (*forehead*) cao trên đầu, xa khu vực lông mày để tránh xung đột trọng số [9].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Thao tác thủ công trên giao diện Blender UI:
1. **Đưa về gốc tọa độ:** Nhấn **Shift + S** \\(\rightarrow\\) chọn *Cursor to World Origin*, sau đó chọn Mesh/Armature và nhấn **Shift + S** \\(\rightarrow\\) *Selection to Cursor* [3].
2. **Apply All Transforms:** Chọn Mesh và Armature trong Object Mode \\(\rightarrow\\) Nhấn **Ctrl + A** \\(\rightarrow\\) chọn **All Transforms** [3].
3. **Làm sạch lưới trong Edit Mode (Mesh):** 
   * Nhấn **A** chọn toàn bộ đỉnh \\(\rightarrow\\) nhấn **M** \\(\rightarrow\\) chọn *By Distance* để gộp đỉnh trùng [2, 5].
   * Nhấn **Shift + N** để tính lại pháp tuyến quay ra ngoài (*Recalculate Normals Outward*) [2, 5].
4. **Căn chỉnh Metarig trong Edit Mode (Armature):**
   * Bật **X-Axis Mirror** tại bảng Sidebar/Tool Tab [2, 3].
   * Bật **In Front** trong mục *Viewport Display* của thuộc tính Armature để luôn nhìn thấy xương [2].
   * Kéo vị trí khớp gối và khuỷu tay hơi nhô về phía trước [2, 6].

#### Mã nguồn Python (`bpy`) tự động hóa quy trình chuẩn bị:

```python
import bpy

# 1. Xử lý và làm sạch Mesh nhân vật
mesh_obj = bpy.context.active_object

if mesh_obj and mesh_obj.type == 'MESH':
    # Đặt mô hình về gốc tọa độ World Origin (0,0,0)
    mesh_obj.location = (0.0, 0.0, 0.0)
    
    # Apply All Transforms (Location, Rotation, Scale)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Chuyển sang Edit Mode để làm sạch hình học
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Merge by distance (Xóa đỉnh trùng)
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    
    # Recalculate Normals Outward (Shift + N)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    
    # Trở về Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Xử lý Mesh hoàn tất!")

# 2. Xử lý và chuẩn hóa Armature (Metarig)
armature_obj = bpy.data.objects.get("metarig")  # Thay tên tương ứng với Metarig của bạn
if armature_obj and armature_obj.type == 'ARMATURE':
    armature_obj.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.objects.active = armature_obj
    
    # Apply All Transforms cho Armature
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Bật thuộc tính hiển thị In Front và Bật X-Axis Mirror
    armature_obj.show_in_front = True
    armature_obj.data.use_mirror_x = True
    print("Xử lý Armature hoàn tất!")
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

| Lỗi thường gặp | Nguyên nhân chính | Cách kiểm tra & Khắc phục |
| :--- | :--- | :--- |
| **"Bone heat weighting: failed to find solution for one or more bones"** [4, 5] | Lưới bị tự giao nhau (mắt, răng nằm bên trong đầu), có đỉnh trùng, lỗ thủng (non-manifold) hoặc độ phân giải thể tích Laplacian bị giới hạn trên mesh nhỏ/chi tiết [4, 5, 10]. | **Cách 1 (10x Scale Pipeline):** Phóng to Armature và Mesh lên 10 lần (`S` \\(\rightarrow\\) `10` \\(\rightarrow\\) `Enter`), gán *Automatic Weights*, sau đó thu nhỏ trở lại (`S` \\(\rightarrow\\) `0.1`) [10, 11].<br>**Cách 2 (Loose Parts Pipeline):** Trong Edit Mode của Mesh, nhấn `P` \\(\rightarrow\\) chọn *Separate by Loose Parts* để tách các phần rời (răng, tóc, phụ kiện). Gán *Automatic Weights* cho tất cả các phần rải rác cùng Rig, sau đó chọn lại lưới và gộp lại bằng `Ctrl + J` [10-12]. |
| **Khớp gối / khuỷu tay gập ngược khi chuyển sang IK** [6] | Xương gối hoặc khuỷu tay trong Edit Mode đặt quá thẳng hàng (\\(180^\circ\\)) hoặc bị lệch gập về phía sau [6]. | Trong Edit Mode của Metarig, kiểm tra từ góc nhìn nghiêng (Side View) và đảm bảo các khớp luôn có một góc gập nhẹ hướng ra phía trước trước khi nhấn *Generate Rig* [2, 6]. |
| **Hàn dính môi / Lem trọng số mặt sang ngực** [9] | Môi trên và dưới đặt quá dính nhau; xương cằm (*chin*) đặt quá sát bề mặt ngoài của Mesh [9]. | Mở rộng khoảng hở giữa xương môi trên và dưới. Dời vị trí xương cằm đặt sâu vào bên trong thể tích của khối đầu nhân vật [9]. |
| **Rigify Error khi nhấn Generate Rig** [13, 14] | Xóa bớt xương mặc định từ Metarig hoặc đứt kết nối cha-con của các xương glue [3, 13, 14]. | Không xóa xương thừa. Nếu gặp lỗi đứt kết nối xương glue (ví dụ: `ORG-cheek_glue`), dùng 3D Cursor để căn chỉnh khớp nối: Chọn khớp mục tiêu \\(\rightarrow\\) **Shift + S** \\(\rightarrow\\) *Cursor to Selected*; chọn đầu xương glue \\(\rightarrow\\) **Shift + S** \\(\rightarrow\\) *Selection to Cursor* để hàn dính lại [4, 13]. |

💡 **Bạn có muốn tôi hướng dẫn chi tiết các bước thiết lập hệ thống IK chân tiếp đất phẳng (Feet IK) hoặc cấu hình tự động thích ứng địa hình không?**
