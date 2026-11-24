# [G08] Tạo chi tiết mặt tiền nhà phố (Procedural Building Facades) từ khối hộp OSM thô

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Nâng cao (Level 3)
- **Ngày trích xuất:** 2026-11-05

---

### 1. Tóm tắt Bản chất (2-3 câu)

Chuyển đổi khối hộp OSM (Massing blocks) thành công trình kiến trúc procedural là quy trình kết hợp dữ liệu Hệ thống Thông tin Địa lý (GIS) với các công cụ dựng hình thủ tục (Geometry Nodes) trong Blender [1, 2]. Phương pháp này giúp tự động hóa việc biến các hình khối 2D/3D thô sơ từ OpenStreetMap thành mô hình đô thị sinh động, tối ưu hóa thời gian dựng hình thủ công và duy trì độ chính xác không gian [1, 3]. Đây là giải pháp nền tảng cho trực quan hóa đô thị, quy hoạch kiến trúc và tái thiết môi trường thực tế [1, 3].

---

### 2. Nguyên lý & Thông số Chuẩn

*   **Xử lý xung đột tọa độ & Độ chính xác (Precision Conflict)**: Dữ liệu GIS gốc sử dụng số thực 64-bit (double precision), trong khi Blender sử dụng đồ họa số thực 32-bit (single precision) [4]. Vì \\(1^\circ\\) vĩ độ tương đương khoảng \\(111,320\,\text{m}\\), số thực 32-bit không thể phân giải khoảng cách dưới \\(\approx 1.11\,\text{m}\\) ở quy mô toàn cầu [5]. Do đó, bắt buộc phải đưa dữ liệu về hệ mét địa phương và thực hiện dịch chuyển gốc tọa độ theo công thức:
    \\[\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\]
    Thao tác này giúp đưa mô hình về gần gốc Cartesian \\((0,0,0)\\) nhằm triệt tiêu hiện tượng rung lắc đỉnh (vertex jitter) và lỗi bóng đổ [6].
*   **Trích xuất thuộc tính & Chiều cao từ OSM**: Quá trình nhập truy vấn các thẻ thuộc tính `building:levels` (tính số tầng tương quan) hoặc `height` (kích thước chiều cao trực tiếp) [2]. Khi dữ liệu OSM thiếu thuộc tính chiều cao, một giá trị mặc định kèm độ biến thiên ngẫu nhiên (ví dụ: \\(12.0\,\text{m} \pm 3.5\,\text{m}\\)) được áp dụng để tạo độ nhấp nhô tự nhiên cho tuyến phố [2, 7].
*   **Khớp độ cao địa hình (Terrain Conformance)**: Kích hoạt tham số `Elevation from object` để chiếu chân móng 2D của công trình trực tiếp lên mặt lưới địa hình (DEM/SRTM) [2, 7, 8].
*   **Quy tắc phân bố & Tỷ lệ chi tiết**: Khi rải các chi tiết phụ trợ trên bề mặt, áp dụng thuật toán **Poisson Disk** trong nút `Distribute Points on Faces` với tham số `Distance Min` để tạo khoảng không gian loại trừ tối thiểu, tránh hiện tượng các chi tiết bị đè lên nhau [9-11]. Kèm theo đó, nút `Random Value` giúp tạo biến thiên tỷ lệ (ví dụ: khoảng \\(0.8\\) đến \\(1.3\\)) [11].
*   **Tính toán độ dốc mái (Roof Pitch)**: Độ dốc mái được xác định dựa trên tỷ lệ giữa chiều cao nâng (Rise) và độ rộng mặt bằng (Run), tương ứng với hàm tang (\\(\text{Slope} = \text{Rise} / \text{Run} = \tan(\theta)\\)) [12-14].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Quy trình thao tác bằng giao diện & Geometry Nodes:

1.  **Nhập khối OSM**: Trong Viewport 3D, chọn mặt phẳng địa hình, mở menu BlenderGIS chọn `Web Geodata > Get OSM` [8, 15]. Chọn thẻ `Buildings`, bật `Elevation from object`, thiết lập `default height` và giá trị ngẫu nhiên [2, 8, 16].
2.  **Tạo tầng & Chia vỏ tường (`Extrude Mesh`)**: Đưa khối OSM vào Geometry Nodes modifier, sử dụng nút `Extrude Mesh` để đùn các mặt khối hộp tạo khối ban công, máng tường hoặc độ dốc mái [17, 18].
3.  **Cắt ô cửa & Rải ban công, biển hiệu**:
    *   Dùng nút `Mesh Boolean` (chế độ *Difference*) với các hình khối phụ để cắt ô cửa sổ/cửa đi vào mặt đứng tòa nhà [19].
    *   Dùng nút `Distribute Points on Faces` (Poisson Disk) kết hợp `Instance on Points` để rải các mô hình mẫu (instances) cửa sổ, ban công, biển hiệu lên mặt đứng [9, 20, 21].
4.  **Tạo vật liệu tường rêu phong (`Texture Nodes` & `Set Material`)**:
    *   Sử dụng nút `Noise Texture` kết hợp `Brick Texture` để điều khiển độ gồ ghề và độ rêu bám trên bề mặt tường [22, 23].
    *   Sử dụng nút `Set Material` để gán các slot vật liệu riêng biệt cho mặt đỉnh (Top) và mặt bên (Side) sau khi đùn khối [18].

#### Đoạn mã Python (`bpy`) thiết lập môi trường và gán Modifier:

```python
import bpy

# 1. Tạo vật liệu mẫu cho tường rêu phong
wall_mat = bpy.data.materials.new(name="Old_Mossy_Wall")
wall_mat.use_nodes = True
nodes = wall_mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")

# Thêm Noise Texture mô phỏng rêu
noise = nodes.new(type='ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 15.0

color_ramp = nodes.new(type='ShaderNodeValToRGB')
wall_mat.node_tree.links.new(noise.outputs['Color'], color_ramp.inputs['Fac'])
wall_mat.node_tree.links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

# 2. Chọn đối tượng khối nhà OSM đang active
obj = bpy.context.active_object

if obj and obj.type == 'MESH':
    # Gán vật liệu vào đối tượng
    if obj.data.materials:
        obj.data.materials = wall_mat
    else:
        obj.data.materials.append(wall_mat)
        
    # 3. Thêm Geometry Nodes Modifier để xử lý hình khối
    gn_mod = obj.modifiers.new(name="Building_Procedural_Pipeline", type='NODES')
    
    # Tạo Node Group mới nếu chưa có
    node_group = bpy.data.node_groups.new(name="Shophouse_GN_Setup", type='GeometryNodeTree')
    gn_mod.node_group = node_group
    
    # Thiết lập cổng vào/ra cơ bản
    in_node = node_group.nodes.new('NodeGroupInput')
    out_node = node_group.nodes.new('NodeGroupOutput')
    node_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    node_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # Nối thẳng đường truyền hình học cơ bản
    node_group.links.new(in_node.outputs, out_node.inputs)
    print("Đã khởi tạo thành công thiết lập Geometry Nodes cho khối nhà OSM.")
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1.  **Hiện tượng méo lưới và rung hình (Vertex Jittering)**:
    *   *Nguyên nhân*: Nhập dữ liệu tọa độ địa lý thực mà không thiết lập lại gốc tọa độ Scene (Scene Origin Re-centering), dẫn đến tràn giới hạn số thực 32-bit của Blender [4-6].
    *   *Cách kiểm tra*: Kiểm tra vị trí tâm công trình xem có bị đẩy ra xa mốc \\((0,0,0)\\) hàng ngàn mét hay không; áp dụng phép trừ vị trí \\(\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\) để đưa về gốc tọa độ [6].
2.  **Mất vật liệu sau khi biến đổi hình học**:
    *   *Nguyên nhân*: Một số nút như `Extrude Mesh` hay các nút thay đổi cấu trúc lưới có thể loại bỏ thiết lập vật liệu đã gán trước đó [24].
    *   *Cách kiểm tra*: Luôn đặt nút `Set Material` ở bước cuối cùng trong luồng Geometry Nodes (sau các nút xử lý hình học và trước nút đầu ra Output) [24].
3.  **Chồng lấp vật thể chi tiết (Balcony/Sign Overlap)**:
    *   *Nguyên nhân*: Sử dụng phân bố ngẫu nhiên thuần túy làm các điểm rải ban công/biển hiệu trùng vị trí [9].
    *   *Cách kiểm tra*: Chuyển `Distribute Points on Faces` sang chế độ `Poisson Disk` và điều chỉnh tham số `Distance Min` vừa đủ lớn hơn bán kính của mô hình chi tiết [9-11].

---

> ⚠️ **Lưu ý về phạm vi tài liệu trong sổ:** Tài liệu cung cấp quy trình kỹ thuật nền tảng về nhập dữ liệu OSM [8, 15, 25], xử lý độ chính xác tọa độ GIS [4-6], và các công cụ Geometry Nodes (Extrude, Boolean, Instancing, Textures, Poisson Disk) [9, 17-23, 26-83]. **Trong sổ KHÔNG có các bộ preset kiến trúc thiết lập sẵn hay mã nguồn dành riêng cho kiểu nhà ống/nhà phố Việt Nam, mẫu mái tôn corrugated, kiểu dáng ban công, biển hiệu hay shader rêu phong cụ thể.**

---

Thao tác nhập khối OSM và áp dụng Geometry Nodes đã sẵn sàng. Bạn có muốn tìm hiểu thêm về cách thiết lập hệ thống culling theo tầm nhìn camera (Frustum Culling) để tối ưu dung lượng bộ nhớ khi xử lý toàn bộ khu phố không?
