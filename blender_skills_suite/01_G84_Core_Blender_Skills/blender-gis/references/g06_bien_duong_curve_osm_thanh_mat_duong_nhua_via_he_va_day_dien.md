# [G06] Biến đường Curve OSM thành mặt đường nhựa, vỉa hè và dây điện võng bằng Geometry Nodes

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

Dưới đây là hướng dẫn chi tiết về cách tận dụng các đường Spline/Curve từ dữ liệu giao thông OpenStreetMap (OSM) để tạo tự động mặt đường, bó vỉa hè, hàng rào và đường dây điện võng bằng Geometry Nodes trong Blender.

---

### 1. Tóm tắt Bản chất (2-3 câu)
Tận dụng đường Spline/Curve từ dữ liệu giao thông OpenStreetMap (OSM) kết hợp **Geometry Nodes** trong Blender là phương pháp dựng hình không phá hủy (procedural, non-destructive), giúp tự động hóa quá trình sinh mô hình 3D cho mặt đường, bó vỉa hè, hàng rào và đường dây điện võng [cite: 34, 53, 58, 69]. Thay vì thao tác thủ công từng đỉnh lưới, quy trình hướng tới thiết kế dựa trên đường cong (curve-driven design) cho phép chuyển đổi dữ liệu vectơ địa lý thành hạ tầng đô thị 3D hoàn chỉnh chỉ bằng các tham số toán học [cite: 34, 64, 327]. Điều này vừa bảo đảm kích thước chuẩn theo tỷ lệ thực tế, vừa tối ưu hóa hiệu năng làm việc trên các khung cảnh GIS quy mô lớn [cite: 327, 336, 360].

---

### 2. Nguyên lý & Thông số Chuẩn

*   **Hệ tọa độ & Giới hạn số thực Float32:**
    *   Blender xử lý tọa độ dưới dạng số thực đơn Float32 với độ chính xác khoảng 7 chữ số có nghĩa [cite: 396, 638, 773, 863]. Khi nhập dữ liệu tọa độ địa lý thực tế (như hệ UTM với giá trị hàng triệu mét), sai số làm tròn \\(\epsilon \approx X \cdot 2^{-23}\\) sẽ đạt mức \\(0.536\,\text{m}\\) tại mốc \\(4,500,000\,\text{m}\\), dẫn đến hiện tượng vỡ lưới, rung giật (jittering) và hỏng bóng râm (shadow map breakdown) [cite: 396, 773, 774, 861].
    *   **Quy tắc:** Bắt buộc phải đưa tọa độ về hệ chiếu phẳng tuyến tính mét (EPSG/UTM) và dời tâm dữ liệu về gốc tọa độ local \\((0,0,0)\\) thông qua cơ chế **Geoscene Offset** [cite: 396, 775, 776, 777].
*   **Tái mẫu & Sinh mặt đường (Road Surface):**
    *   Spline nhập từ OSM cần đi qua node **Resample Curve** ở chế độ `Length` (ví dụ: khoảng cách \\(1.0\,\text{m} - 2.0\,\text{m}\\) giữa các điểm) để phân bổ đều các điểm kiểm soát, tránh méo lưới khi duỗi cong [cite: 56, 60, 70, 481, 483].
    *   Node **Curve to Mesh** quét một đường thẳng hai điểm (**Curve Line** hoặc **Quadrilateral**) dọc theo Spline để tạo dải mặt đường có chiều rộng tham số hóa (chiều rộng đường 2 làn chuẩn là \\(7.0\,\text{m}\\), tức mỗi bên \\(3.5\,\text{m}\\)) [cite: 57, 58, 60, 69, 478].
*   **Tạo bó vỉa hè (Curb):**
    *   Dựa trên mép ngoài của mặt đường vừa tạo, node **Extrude Mesh** ở chế độ `Edges` hoặc `Faces` được sử dụng để đẩy dải vỉa hè lên cao theo phương thẳng đứng (chiều cao chuẩn vỉa hè đô thị từ \\(0.15\,\text{m} - 0.20\,\text{m}\\)) [cite: 66, 77, 493, 494].
*   **Phân bổ hàng rào / Bó gờ (Guardrail / Fence):**
    *   Sử dụng node **Instance on Points** trên các điểm đã tái mẫu của Spline biên [cite: 56, 61, 461].
    *   Căn chỉnh hướng cọc/rào chắn theo tiếp tuyến (`Curve Tangent`) hoặc pháp tuyến mặt đất (`Normal`) bằng node **Align Rotation to Vector** [cite: 52, 54, 519, 520].
    *   Áp dụng thuật toán **Poisson Disk** (`Distance Min`) để khống chế khoảng cách tối thiểu giữa các cọc rào, tránh hiện tượng các phần tử chồng lấp [cite: 70, 788, 789, 843].
*   **Tạo đường dây điện võng (Catenary Curves):**
    *   Sử dụng node **Spline Parameter** để lấy giá trị nội suy \\(t \in [1]\\) dọc theo mỗi phân đoạn dây [cite: 55, 448].
    *   Tạo độ võng tự nhiên dạng Parabol/Catenary bằng cách tác động vào node **Set Position** với giá trị dịch chuyển trục Z: \\(\Delta Z = -4 \cdot h_{\text{sag}} \cdot t \cdot (1 - t)\\) (trong đó \\(h_{\text{sag}}\\) là độ võng tối đa tại trung điểm \\(t=0.5\\), thường đặt từ \\(0.5\,\text{m} - 1.2\,\text{m}\\)) [cite: 48, 55, 464, 465].
*   **Bám sát mặt đất (Terrain Conformance):**
    *   Chiếu các điểm Spline xuống lưới địa hình DEM/TIN bằng node **Raycast** (hướng ray \\((0, 0, -1)\\)) hoặc **Geometry Proximity** kết hợp **Sample Index** để lấy tọa độ độ cao (`Hit Position`) và góc nghiêng (`Hit Normal`) [cite: 47, 49, 333, 784, 786, 787, 814, 815].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### Thao tác trên giao diện:
1.  **Nhập dữ liệu OSM:** Vào menu `GIS > Web geodata > Get OSM`, chọn danh mục giao thông (Roads/Highways) và đánh dấu chọn `Elevation from object` để khớp dữ liệu lên bề mặt địa hình 3D [cite: 110, 113, 129, 332].
2.  **Khởi tạo Geometry Nodes:** Chọn đối tượng đường dạng Curve vừa nhập, thêm Modifier **Geometry Nodes**.
3.  **Xây dựng sơ đồ Node:**
    *   Thêm node `Resample Curve` để làm mịn và đều khoảng cách đỉnh [cite: 56, 70].
    *   Thêm node `Curve to Mesh` nối với `Curve Line` làm dải rộng mặt đường [cite: 57, 69].
    *   Thêm node `Extrude Mesh` nối vào mép cạnh để nâng lề đường/bó vỉa hè [cite: 66, 493].
    *   Thêm nhánh `Spline Parameter` \\(\rightarrow\\) `Math` (tính \\(t(1-t) \times -4 h_{\text{sag}}\\)) \\(\rightarrow\\) `Set Position` để làm võng dây điện [cite: 48, 55, 464].
    *   Thêm node `Instance on Points` nối với cọc hàng rào và điều hướng qua `Align Rotation to Vector` [cite: 52, 461, 519].
    *   Gộp tất cả bằng node `Join Geometry` và gán vật liệu qua `Set Material` [cite: 74, 460, 509].

#### Mã nguồn Python (`bpy`) thiết lập tự động:

```python
import bpy

def setup_procedural_osm_road_geometry_nodes():
    # Tạo Node Group mới cho Geometry Nodes
    node_group = bpy.data.node_groups.new(name="OSM_Procedural_Road_Nodes", type='GeometryNodeTree')
    
    # 1. Đặt Input và Output
    group_in = node_group.nodes.new('NodeGroupInput')
    group_in.location = (-800, 0)
    group_out = node_group.nodes.new('NodeGroupOutput')
    group_out.location = (1200, 0)
    
    # 2. Resample Curve (Phân bổ lại đỉnh Spline)
    resample = node_group.nodes.new('GeometryNodeResampleCurve')
    resample.mode = 'LENGTH'
    resample.inputs['Length'].default_value = 1.0  # Khoảng cách 1 mét
    resample.location = (-600, 0)
    
    # 3. Tạo mặt đường (Road Surface)
    curve_to_mesh = node_group.nodes.new('GeometryNodeCurveToMesh')
    curve_to_mesh.location = (-300, 200)
    
    profile_line = node_group.nodes.new('GeometryNodeCurvePrimitiveLine')
    profile_line.inputs['Start'].default_value = (-3.5, 0, 0)  # Chiều rộng 7m (mỗi bên 3.5m)
    profile_line.inputs['End'].default_value = (3.5, 0, 0)
    profile_line.location = (-500, 300)
    
    # 4. Extrude vỉa hè (Curb)
    extrude_curb = node_group.nodes.new('GeometryNodeExtrudeMesh')
    extrude_curb.mode = 'EDGES'
    extrude_curb.inputs['Offset Scale'].default_value = 0.2  # Cao vỉa hè 20cm
    extrude_curb.location = (0, 200)
    
    # 5. Tạo đường dây điện võng (Catenary Cable)
    spline_param = node_group.nodes.new('GeometryNodeSplineParameter')
    spline_param.location = (-600, -300)
    
    # Công thức toán học: -4.0 * Sag * Factor * (1 - Factor)
    math_sub = node_group.nodes.new('ShaderNodeMath')
    math_sub.operation = 'SUBTRACT'
    math_sub.inputs.default_value = 1.0
    math_sub.location = (-400, -300)
    
    math_mul1 = node_group.nodes.new('ShaderNodeMath')
    math_mul1.operation = 'MULTIPLY'
    math_mul1.location = (-250, -300)
    
    math_mul2 = node_group.nodes.new('ShaderNodeMath')
    math_mul2.operation = 'MULTIPLY'
    math_mul2.inputs[1].default_value = -0.8  # Độ võng tối đa h_sag = 0.8m
    math_mul2.location = (-100, -300)
    
    combine_xyz = node_group.nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.location = (50, -300)
    
    set_catenary_pos = node_group.nodes.new('GeometryNodeSetPosition')
    set_catenary_pos.location = (200, -200)
    
    # 6. Gộp kết quả (Join Geometry)
    join_geo = node_group.nodes.new('GeometryNodeJoinGeometry')
    join_geo.location = (800, 0)
    
    # Tạo các kết nối (Links)
    links = node_group.links
    links.new(group_in.outputs, resample.inputs['Geometry'])
    
    # Nhánh Mặt đường & Vỉa hè
    links.new(resample.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    links.new(profile_line.outputs['Curve'], curve_to_mesh.inputs['Profile Curve'])
    links.new(curve_to_mesh.outputs['Mesh'], extrude_curb.inputs['Mesh'])
    links.new(extrude_curb.outputs['Mesh'], join_geo.inputs['Geometry'])
    
    # Nhánh Dây điện võng
    links.new(spline_param.outputs['Factor'], math_sub.inputs[1])
    links.new(spline_param.outputs['Factor'], math_mul1.inputs)
    links.new(math_sub.outputs['Value'], math_mul1.inputs[1])
    links.new(math_mul1.outputs['Value'], math_mul2.inputs)
    links.new(math_mul2.outputs['Value'], combine_xyz.inputs['Z'])
    links.new(resample.outputs['Curve'], set_catenary_pos.inputs['Geometry'])
    links.new(combine_xyz.outputs['Vector'], set_catenary_pos.inputs['Offset'])
    links.new(set_catenary_pos.outputs['Geometry'], join_geo.inputs['Geometry'])
    
    # Kết nối ra Output
    links.new(join_geo.outputs['Geometry'], group_out.inputs)

# Thực thi hàm tạo Node Tree
setup_procedural_osm_road_geometry_nodes()
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1.  **Lỗi giật hình/vỡ lưới do tọa độ địa lý quá xa (Rounding / Floating-Point Error):**
    *   *Nguyên nhân:* Nhập trực tiếp dữ liệu tọa độ UTM hoặc độ kinh/vĩ mà không dời tâm về gốc local \\((0,0,0)\\) làm sai số làm tròn số thực Float32 tăng cao [cite: 396, 638, 773, 861].
    *   *Kiểm tra & Sửa lỗi:* Kiểm tra bảng thuộc tính Scene xem **Scene Origin Geolocation** đã được xác định chưa [cite: 640, 776]. Luôn bật tùy chọn re-centering/geoscene offset trong BlenderGIS khi import dữ liệu [cite: 776, 777].
2.  **Lỗi xoắn vặn mặt đường (Spline Tilt / Normal Distortion):**
    *   *Nguyên nhân:* Hướng Normal của Spline bị xoắn tại các góc cua gấp hoặc đoạn dốc [cite: 55].
    *   *Kiểm tra & Sửa lỗi:* Thêm node **Set Curve Normal** và chuyển chế độ tính Normal sang `Z-Up` để mặt đường luôn hướng lên trên theo chiều thẳng đứng [cite: 55].
3.  **Lỗi hở khoảng cách / chồng lấp mặt lưới (Mesh Overlap & Light Leaks):**
    *   *Nguyên nhân:* Các đoạn Spline OSM cắt nhau tạo ra vô số đỉnh nằm đè lên nhau [cite: 5, 334, 794].
    *   *Kiểm tra & Sửa lỗi:* Đặt node **Merge by Distance** ở cuối chuỗi dựng lưới để tự động hàn các đỉnh gần nhau [cite: 5, 334, 458, 795].
4.  **Lỗi hàng rào/cọc điện bị quay sai hướng:**
    *   *Nguyên nhân:* Chọn sai trục xoay hoặc truyền nhầm tiếp tuyến `Curve Tangent` thay vì `Normal` vào node `Align Rotation to Vector` [cite: 519, 520, 578].
    *   *Kiểm tra & Sửa lỗi:* Kiểm tra lại thuộc tính `Pivot Axis` (chọn trục Z là Up Vector) và dùng **Viewer Node** để xem hướng của Vector trước khi truyền vào node instance [cite: 455, 519, 578].

---

🌐 Bạn có muốn bổ sung thêm thuật toán Frustum Culling (ẩn các đoạn đường ngoài tầm nhìn camera) hoặc hệ thống LOD tự động giảm tải cho các khung cảnh đô thị diện rộng không?
