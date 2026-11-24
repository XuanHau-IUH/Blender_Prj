# [G07] Phân bố thảm thực vật & Chi tiết đô thị thông minh (Geometry Nodes Point Distribute, Weight/Slope Mask & Instancing)

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

Thao tác rải cây cối, cỏ dại, rác đô thị và đạo cụ hẻm phố bằng **Geometry Nodes** trong Blender được tổng hợp chi tiết từ tài liệu như sau:

---

### 1. Tóm tắt Bản chất (2-3 câu)
Kỹ thuật rải đối tượng bằng Geometry Nodes là một quy trình rải điểm và phân bổ mảng đối tượng procedural không phá hủy (non-destructive) trên bề mặt lưới 3D trong Blender [1-4]. Phương pháp này giúp tự động hóa việc sắp xếp hàng loạt chi tiết vi địa hình với diện mạo tự nhiên mà không tốn công dựng thủ công [2, 5]. Quan trọng nhất, việc sử dụng các bản sao tham chiếu (instances) thay vì nhân bản toàn bộ lưới hình học giúp tiết kiệm bộ nhớ VRAM vượt trội và duy trì hiệu năng mượt mà ngay cả khi hiển thị hàng triệu đối tượng [6-8].

---

### 2. Nguyên lý & Thông số Chuẩn

*   **Distribute Points on Faces & Poisson Disk (Phân bổ chống chồng lấn):**
    Việc rải ngẫu nhiên thuần túy (Random) dễ dẫn đến tình trạng các mô hình đè chồng lên nhau gây lỗi va chạm lưới (mesh collision) [4]. Chuyển phương thức phân bổ sang **Poisson Disk** sẽ kích hoạt thuật toán thiết lập vùng loại trừ tuyệt đối (exclusion zone) xung quanh mỗi điểm dựa trên thông số **Distance Min** (\\(r\\)) [9-13]. Thuật toán này bảo đảm không có hai đạo cụ hay cây cối nào nằm gần nhau hơn khoảng cách bán kính tối thiểu đã định, tạo ra phân bố tự né tránh tự nhiên [11-13]. Trong khi đó, thông số **Density Max** kiểm soát giới hạn bão hòa mật độ tối đa trên một đơn vị diện tích [10-13].
*   **Lọc theo độ dốc Normal Z (Normal Z Slope Filtering):**
    Để tránh việc cây cối hay rác đô thị xuất hiện bừa bãi trên các vách đá đứng hay bề mặt nghiêng bất hợp lý, vectơ pháp tuyến bề mặt (**Normal**) được trích xuất thành phần \\(Z\\) [14-17]. Bằng cách kết hợp phép so sánh ngưỡng (ví dụ: \\(\text{Normal Z} > 0.7\\), tương đương góc nghiêng dưới \\(45^\circ\\)), hệ thống chỉ cho phép rải điểm trên các bề mặt tương đối bằng phẳng thông qua cổng `Selection` [14, 16, 17].
*   **Tối ưu VRAM bằng Collection Instance:**
    Các tài sản như cây cối, rác đô thị hay đạo cụ được gom vào một Collection và nạp vào Node Tree qua node **Collection Info** [18-20]. Cơ chế instancing lưu trữ chung một khối dữ liệu hình học gốc (data block) và chỉ ghi nhận tọa độ vị trí, góc xoay và tỷ lệ của từng bản sao [6, 7]. Nhờ đó, GPU chỉ phải xử lý các lượt gọi vẽ (draw calls) tham chiếu nhẹ nhàng thay vì nhân bản hàng triệu đỉnh (vertices) vào VRAM [6-8].
*   **Biến thiên quy mô & Góc xoay (Randomization):**
    Nhằm xoá bỏ sự lặp lại cứng nhắc, node **Random Value** được nối vào các cổng `Rotation` (xoay ngẫu nhiên quanh trục Z) và `Scale` (ví dụ tỷ lệ biến thiên từ \\(0.8\\) đến \\(1.3\\)) của node **Instance on Points** để tạo độ đa dạng tự nhiên [8, 21-23].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Quy trình thiết lập trên Giao diện (GUI)
1.  **Gom nhóm Tài sản (Collection Setup):** Đưa toàn bộ các model cây, cỏ hoặc rác đô thị vào một Collection (đặt tên ví dụ: `PropsCollection`). Đảm bảo tâm gốc tọa độ (Pivot point) của mỗi đối tượng nằm ở đáy/chân model.
2.  **Tạo Geometry Nodes Tree:** Chọn mặt đất/địa hình target, thêm Modifier `Geometry Nodes`.
3.  **Xây dựng Node Graph:**
    *   Nối `Group Input` (Geometry) vào cổng `Mesh` của node **Distribute Points on Faces**.
    *   Đổi `Distribution Method` sang **Poisson Disk**. Đặt **Distance Min** (ví dụ: `1.5m` cho cây, `0.2m` cho rác) và điều chỉnh **Density Max**.
    *   Thêm node **Normal** nối vào **Separate XYZ**. Lấy đầu ra `Z` nối qua node **Compare** (chế độ Float, Greater Than, Threshold = `0.7`). Nối kết quả đầu ra vào cổng `Selection` của **Distribute Points on Faces**.
    *   Thêm node **Collection Info**, chọn `PropsCollection`, tích chọn **Separate Children** và **Reset Children**.
    *   Thêm node **Instance on Points**. Nối `Points` từ node rải điểm sang `Points` của node này. Nối `Instances` của **Collection Info** vào cổng `Instance`. Tích chọn **Pick Instance**.
    *   Tạo node **Random Value** (Float: Min `0.8`, Max `1.3`) cắm vào `Scale`. Tạo node **Random Value** (Vector: Z từ `0` đến `6.28` rad) cắm vào `Rotation`.
    *   Nối kết quả từ **Instance on Points** và địa hình gốc qua node **Join Geometry** trước khi đưa ra `Group Output`.

#### B. Đoạn mã Python (`bpy`) tự động hóa

```python
import bpy

def setup_procedural_scattering(target_obj_name, collection_name):
    # Lấy đối tượng địa hình và collection đạo cụ
    target_obj = bpy.data.objects.get(target_obj_name)
    props_coll = bpy.data.collections.get(collection_name)
    
    if not target_obj or not props_coll:
        print("Không tìm thấy Object hoặc Collection yêu cầu!")
        return

    # Thêm modifier Geometry Nodes
    gn_mod = target_obj.modifiers.new(name="Procedural_Scatter", type='NODES')
    node_group = bpy.data.node_groups.new(name="Scatter_Tree_Props_Tree", type='GeometryNodeTree')
    gn_mod.node_group = node_group

    nodes = node_group.nodes
    links = node_group.links
    nodes.clear()

    # Cấu hình cổng Input / Output (Blender 4.0+)
    node_group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    group_in = nodes.new(type='NodeGroupInput')
    group_out = nodes.new(type='NodeGroupOutput')

    # Node phân bổ điểm Poisson Disk
    distribute = nodes.new(type='GeometryNodeDistributePointsOnFaces')
    distribute.distribute_method = 'POISSON'
    distribute.inputs['Distance Min'].default_value = 1.2  # Khoảng cách tối thiểu chống chồng lấn
    distribute.inputs['Density Max'].default_value = 5.0   # Mật độ tối đa

    # Lọc độ dốc theo Normal Z
    normal_node = nodes.new(type='GeometryNodeInputNormal')
    sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    compare = nodes.new(type='FunctionNodeCompare')
    compare.data_type = 'FLOAT'
    compare.operation = 'GREATER_THAN'
    compare.inputs[24].default_value = 0.7  # Chỉ lấy mặt đất nghiêng < 45 độ

    # Nạp Collection đạo cụ
    coll_info = nodes.new(type='GeometryNodeCollectionInfo')
    coll_info.inputs['Collection'].default_value = props_coll
    coll_info.inputs['Separate Children'].default_value = True
    coll_info.inputs['Reset Children'].default_value = True

    # Node Instancing
    instance_on_pts = nodes.new(type='GeometryNodeInstanceOnPoints')
    instance_on_pts.inputs['Pick Instances'].default_value = True

    # Ngẫu nhiên hóa quy mô (Scale)
    rand_scale = nodes.new(type='FunctionNodeRandomValue')
    rand_scale.data_type = 'FLOAT'
    rand_scale.inputs['Min'].default_value = 0.8
    rand_scale.inputs['Max'].default_value = 1.3

    # Gộp Geometry địa hình gốc và các Instance
    join_geo = nodes.new(type='GeometryNodeJoinGeometry')

    # Liên kết các node
    links.new(normal_node.outputs['Normal'], sep_xyz.inputs['Vector'])
    links.new(sep_xyz.outputs['Z'], compare.inputs)
    links.new(compare.outputs['Result'], distribute.inputs['Selection'])

    links.new(group_in.outputs['Geometry'], distribute.inputs['Mesh'])
    links.new(distribute.outputs['Points'], instance_on_pts.inputs['Points'])
    links.new(coll_info.outputs['Instances'], instance_on_pts.inputs['Instance'])
    links.new(rand_scale.outputs['Value'], instance_on_pts.inputs['Scale'])

    links.new(group_in.outputs['Geometry'], join_geo.inputs['Geometry'])
    links.new(instance_on_pts.outputs['Instances'], join_geo.inputs['Geometry'])
    links.new(join_geo.outputs['Geometry'], group_out.inputs['Geometry'])

# Chạy thử nghiệm hàm
# setup_procedural_scattering("Terrain_Mesh", "PropsCollection")
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1.  **Thực hóa Instance quá sớm (`Realize Instances`):**
    Việc chèn node `Realize Instances` sau khi rải điểm sẽ ép Blender biến đổi toàn bộ các bản sao mỏng nhẹ thành lưới độc lập [14, 25]. Điều này làm bùng nổ dung lượng bộ nhớ và cạn kiệt VRAM nghiêm trọng [14, 25]. *Cách kiểm tra:* Kiểm tra chỉ số `Mem` trong Viewport Statistics; giữ nguyên dạng Instance trừ khi bắt buộc phải chỉnh sửa đỉnh chi tiết [25, 26].
2.  **Sử dụng chế độ Random thay vì Poisson Disk:**
    Khiến cây cối hoặc rác đô thị dính cụm và đè chéo vào nhau trông rất giả [4, 12]. *Cách kiểm tra:* Đảm bảo chuyển `Distribution Method` sang Poisson Disk và đặt `Distance Min` lớn hơn bán kính thực tế của model đạo cụ [11, 12].
3.  **Quên bật `Pick Instance` hoặc `Separate Children`:**
    Lỗi này làm cho tại mỗi điểm rải, toàn bộ Collection (tất cả các model) bị rải nguyên cụm lồng vào nhau thay vì chọn ngẫu nhiên 1 model [18-20, 27]. *Cách kiểm tra:* Tích chọn đầy đủ `Separate Children` trên **Collection Info** và `Pick Instance` trên **Instance on Points** [18, 20, 27].
4.  **Bỏ qua lọc Normal Z làm đạo cụ mọc ngang trên vách dốc:**
    Khiến cây cối hoặc rác bị đặt rải rác trên vách đá đứng hay vách tường, gây ra hiện tượng xuyên hình (clipping) hoặc lơ lửng [16, 17]. *Cách kiểm tra:* Kiểm tra kỹ đầu nối `Selection` của node rải điểm qua node so sánh thành phần `Normal Z` [14, 16, 17].
5.  **Thứ tự gán vật liệu `Set Material` sai:**
    Gán vật liệu trước các node thay đổi cấu trúc hình học có thể khiến thiết lập vật liệu bị xóa mất [28-30]. *Cách kiểm tra:* Luôn luôn vị trí node `Set Material` ở bước cuối cùng trước đầu ra `Group Output` [28-30].

---

🌿 **Gợi ý bước tiếp theo:** Bạn có muốn tìm hiểu thêm về kỹ thuật kết hợp **Frustum Culling** (xóa đối tượng ngoài tầm nhìn camera) và chuyển đổi **LOD (Level of Detail)** theo khoảng cách để tối ưu hóa hiệu năng render cho các cảnh đại cảnh lớn không?
