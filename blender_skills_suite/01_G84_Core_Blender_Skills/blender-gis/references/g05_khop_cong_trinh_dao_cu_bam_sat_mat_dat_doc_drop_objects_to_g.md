# [G05] Khớp công trình & Đạo cụ bám sát mặt đất dốc (Drop Objects to Ground & Raycast Snapping)

- **Chủ đề:** Môi trường Đô thị & Địa lý (Environment & BlenderGIS)
- **Sổ NotebookLM nguồn:** `NB_Environment_GIS`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

Dưới đây là hướng dẫn chi tiết quy trình đặt hàng loạt tòa nhà, cột điện, xe cộ và cây cối bám sát xuống bề mặt địa hình lồi lõm trong Blender, kết hợp giữa addon **BlenderGIS** và hệ thống nút **Geometry Nodes**.

---

### 1. Tóm tắt Bản chất
Việc đặt hàng loạt công trình kiến trúc, hạ tầng và cảnh quan (tòa nhà, cột điện, xe cộ, cây cối) bám sát bề mặt địa hình lồi lõm là kỹ thuật tự động hóa và xử lý thủ tục (**procedural**) quan trọng trong tái tạo môi trường 3D GIS trên Blender [1-3]. Phương pháp này thay thế các thao tác căn chỉnh thủ công bằng cách tính toán tọa độ giao điểm thẳng đứng hoặc khoảng cách bề mặt gần nhất giữa các vật thể và lưới địa hình [2-5]. Điều này giúp triệt tiêu hoàn toàn hiện tượng vật thể bị trôi lơ lửng hay đâm xuyên lòng đất, đảm bảo tính chân thực và độ chính xác không gian tuyệt đối cho các dự án quy hoạch đô thị và mô phỏng địa lý [1, 6-8].

---

### 2. Nguyên lý & Thông số Chuẩn

#### A. Nguyên lý công cụ `Drop to terrain` & OSM Terrain Conformance (BlenderGIS)
* **Cơ chế thả vật thể tĩnh (`Drop to terrain`)**: Tự động tính toán giao điểm chiếu thẳng đứng xuống dưới (**downward vertical intersection**) từ gốc tọa độ (**origin**) của từng vật thể đến lưới địa hình mục tiêu, từ đó cập nhật vị trí trục Z để vật thể hít chính xác vào mặt đất [2, 3, 9, 10].
* **Bám địa hình OSM (`Elevation from object`)**: Khi nhập dữ liệu công trình từ OpenStreetMap, tùy chọn này chiếu chân móng 2D (**2D footprints**) lên lưới DEM mục tiêu và đùn khối (**extrude**) tòa nhà dựa trên điểm tiếp xúc mặt đất duy nhất của từng công trình [6, 7, 11]. Chiều cao mặc định khi thiếu thuộc tính OSM thường áp dụng biên độ biến thiên ngẫu nhiên (ví dụ: \\(12.0\text{ m} \pm 3.5\text{ m}\\)) để tránh bằng phẳng đơn điệu [6, 7, 11].

#### B. Nguyên lý Raycast Node System (Geometry Nodes)
* **Tia ngắm (Ray Direction)**: Thiết lập vectơ \\((0, 0, -1)\\) chiếu tia ngắm thẳng đứng từ trên xuống dưới dọc theo trục Z toàn cục [12-14].
* **Vị trí nguồn & Mục tiêu**: `Source Position` nhận dữ liệu từ các điểm phân bố (Scatter Points); `Target Geometry` là lưới địa hình 3D (DEM Mesh) [12-14].
* **Cập nhật vị trí (`Hit Position`)**: Nối cổng xuất `Hit Position` vào cổng `Position` của nút `Set Position` để dán chân vật thể vào bề mặt va chạm [15-17].
* **Căn chỉnh pháp tuyến (`Hit Normal`)**: Chuyển đổi vectơ pháp tuyến `Hit Normal` thành góc xoay Euler qua nút `Align Rotation to Vector` (hoặc `Align Euler to Vector`), đặt trục căn chỉnh `Axis: Z` để hướng local Z của vật thể khớp với pháp tuyến bề mặt địa hình [15-17].
* **Xác thực điểm đâm trúng (`Is Hit`)**: Đưa tín hiệu Boolean `Is Hit` vào đầu vào `Selection` của nút `Instance on Points` để ngăn tạo bản sao ở các điểm nằm ngoài ranh giới địa hình [15-17].

#### C. Giải pháp Proximity-Based Sampling cho vách đá dốc đứng
* Đối với địa hình dốc đứng hoặc vách núi nguy hiểm, việc chiếu tia dọc \\((0, 0, -1)\\) dễ bị hụt tia khiến vật thể bị trôi [4, 5, 18].
* Hệ thống chuyển sang dùng nút `Geometry Proximity` (phân tích mức mặt - Face level) kết hợp với `Sample Nearest` để tìm chỉ số mặt gần nhất, sau đó dùng `Sample Index` lấy chính xác tọa độ `Position` và pháp tuyến `Normal` của mặt đó [4, 5, 18].

#### D. Phân bố mật độ Poisson Disk (Poisson Disk Distribution)
* Khi rải cây cối, cột điện hay xe cộ bằng `Distribute Points on Faces`, thiết lập thuật toán `Poisson Disk` với bán kính loại trừ tối thiểu `Distance Min` (\\(r\\)) để tạo khoảng cách an toàn sinh học giữa các cây/cột, tránh lồng ghép hay va chạm mô hình [19-21].

#### E. Giới hạn độ chính xác không gian & Hệ tọa độ Geoscene
* **Giới hạn số thực Float32**: Blender sử dụng chuẩn `float32` với 7 chữ số có nghĩa [22-29]. Sai số phân giải không gian \\(\epsilon \approx X \cdot 2^{-23}\\) [30-32]: Tại tọa độ UTM \\(X = 4,500,000\text{ m}\\), sai số \\(\epsilon \approx 0.536\text{ m}\\), làm đỉnh lưới bị giật giật (**jitter**) và bóng đổ bị hư [30-34]. Nhập kinh/vĩ độ trực tiếp (\\(1^\circ \approx 111,320\text{ m}\\)) gây sai số \\(> 1.11\text{ m}\\) [22, 23, 26, 35-37].
* **Khái niệm Geoscene**: Nhập dữ liệu qua mô hình dịch tâm địa lý \\(\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\) với \\(\mathbf{T}_{\text{offset}} = (X_{\text{geo\_origin}}, Y_{\text{geo\_origin}}, Z_{\text{geo\_origin}})\\) để đưa tọa độ về sát gốc \\((0,0,0)\\) Cartesian cục bộ, bảo toàn độ chính xác dưới 1mm [38-43].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác thủ công trong giao diện

##### Cách 1: Sử dụng BlenderGIS `Drop to terrain` / OSM Import
1. **Gắn công trình OSM bám địa hình**: Đưa Viewport về Top Orthographic \\(\rightarrow\\) Chọn `GIS` > `Web Geodata` > `Get OSM` \\(\rightarrow\\) Chọn danh mục công trình \\(\rightarrow\\) Tích chọn **`Elevation from object`** và chọn mesh DEM địa hình \\(\rightarrow\\) Nhấn **`OK`** [6, 7, 11, 44-47].
2. **Thả vật thể tĩnh ngẫu nhiên**: Chọn tất cả các mô hình cây cối, xe cộ, cột điện cần thả \\(\rightarrow\\) Giữ `Shift` chọn mesh địa hình mục tiêu **sau cùng** \\(\rightarrow\\) Vào menu `Object` > chọn **`Drop to terrain`** (hoặc trong TAB tool GIS) [2, 3, 9, 10, 48, 49].

##### Cách 2: Thiết lập Geometry Nodes Raycast Snapping
1. Chọn mesh điểm phân bố (Scatter Object), thêm modifier **Geometry Nodes**.
2. Thêm nút `Distribute Points on Faces`: Đặt phương thức là **`Poisson Disk`**, điều chỉnh `Distance Min` (ví dụ: \\(3.0\text{ m}\\)) [19-21, 50, 51].
3. Thêm nút `Raycast`:
   * Nối `Object Info` (chọn Mesh địa hình, đặt mode `Relative`) vào `Target Geometry` [12-14, 52, 53].
   * Nối nút `Position` vào `Source Position` [12-14].
   * Đưa nút `Combine XYZ` (\\(Z = -1.0\\)) vào `Ray Direction` [12-14].
4. Thêm nút `Set Position`: Nối điểm từ `Distribute Points` qua `Geometry`. Nối `Hit Position` từ Raycast vào cổng `Position` của `Set Position` [15-17].
5. Thêm nút `Align Rotation to Vector`:
   * Nối `Hit Normal` từ Raycast vào cổng `Vector` [15-17].
   * Đặt `Axis` là `Z` [15-17].
6. Thêm nút `Instance on Points`: Nối `Geometry` từ `Set Position` vào `Points`, `Rotation` từ `Align Rotation` vào `Rotation`, `Selection` nối từ `Is Hit` của Raycast [15-17]. Nối Collection cây cối/cột điện vào cổng `Instance` [54, 55].

---

#### B. Mã Python `bpy` tự động hóa

##### 1. Kịch bản gọi lệnh Drop to Terrain của BlenderGIS
```python
import bpy

def drop_objects_to_terrain_gis(object_names, terrain_name):
    # Bỏ chọn tất cả các vật thể
    bpy.ops.object.select_all(action='DESELECT')
    
    # Chọn danh sách các vật thể cần thả (cây cối, cột điện, xe cộ)
    for name in object_names:
        if name in bpy.data.objects:
            bpy.data.objects[name].select_set(True)
            
    # Chọn mesh địa hình mục tiêu SAU CÙNG và đặt làm Active Object
    terrain_obj = bpy.data.objects.get(terrain_name)
    if terrain_obj:
        terrain_obj.select_set(True)
        bpy.context.view_layer.objects.active = terrain_obj
        
        # Gọi operator drop on terrain của BlenderGIS
        bpy.ops.gis.drop_on_terrain()
        print("Đã thả các vật thể bám sát bề mặt địa hình!")

# Ví dụ sử dụng:
# drop_objects_to_terrain_gis(['Tree_01', 'Pole_01', 'Car_01'], 'DEM_Terrain_Mesh')
```

##### 2. Kịch bản tự động dựng nút Raycast Snapping trong Geometry Nodes
```python
import bpy

def setup_raycast_snapping_nodes(obj_scatter_name, terrain_obj_name):
    scatter_obj = bpy.data.objects.get(obj_scatter_name)
    terrain_obj = bpy.data.objects.get(terrain_obj_name)
    
    if not scatter_obj or not terrain_obj:
        print("Không tìm thấy vật thể hợp lệ!")
        return
        
    # Tạo Modifier Geometry Nodes
    gn_mod = scatter_obj.modifiers.new(name="RaycastTerrainSnap", type='NODES')
    node_group = bpy.data.node_groups.new(name="RaycastSnapGroup", type='GeometryNodeTree')
    gn_mod.node_group = node_group
    
    nodes = node_group.nodes
    links = node_group.links
    nodes.clear() # Xóa nút mặc định
    
    # 1. Tạo các nút chức năng
    input_node = nodes.new('NodeGroupInput')
    output_node = nodes.new('NodeGroupOutput')
    
    distribute_node = nodes.new('GeometryNodeDistributePointsOnFaces')
    distribute_node.distribute_method = 'POISSON'
    
    obj_info = nodes.new('GeometryNodeObjectInfo')
    obj_info.inputs['Object'].default_value = terrain_obj
    obj_info.transform_space = 'RELATIVE'
    
    raycast_node = nodes.new('GeometryNodeRaycast')
    combine_xyz = nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.inputs['Z'].default_value = -1.0 # Hướng tia ngắm (0, 0, -1)
    
    set_pos = nodes.new('GeometryNodeSetPosition')
    align_rot = nodes.new('FunctionNodeAlignRotationToVector')
    align_rot.axis = 'Z'
    
    instance_node = nodes.new('GeometryNodeInstanceOnPoints')
    
    # 2. Tự động liên kết các cổng nút (Links)
    # Nối địa hình vào Raycast
    links.new(obj_info.outputs['Geometry'], raycast_node.inputs['Target Geometry'])
    links.new(combine_xyz.outputs['Vector'], raycast_node.inputs['Ray Direction'])
    
    # Nối điểm phân bố qua Raycast và Set Position
    links.new(raycast_node.outputs['Hit Position'], set_pos.inputs['Position'])
    links.new(raycast_node.outputs['Hit Normal'], align_rot.inputs['Vector'])
    
    # Nối dữ liệu vào Instance on Points
    links.new(raycast_node.outputs['Is Hit'], instance_node.inputs['Selection'])
    links.new(align_rot.outputs['Rotation'], instance_node.inputs['Rotation'])
    
    print("Đã khởi tạo hệ thống nút Raycast Snapping tự động thành công!")

# Ví dụ sử dụng:
# setup_raycast_snapping_nodes('Scatter_Plane', 'DEM_Terrain_Mesh')
```

---

### 4. Lỗi thường gặp & Cách kiểm tra

1. **Lỗi đặt sai gốc tọa độ vật thể (Incorrect Origin Point)**:
   * *Hiện tượng*: Cây cối, cột điện chìm một nửa dưới lòng đất hoặc bay lơ lửng trên không [2, 3, 9, 56, 57].
   * *Khắc phục*: Tâm gốc (**Origin Point**) của vật thể phải nằm chính xác ở chân đáy (**pivot at base**) [56, 57]. Mở Edit Mode, di chuyển mesh sao cho chân vật thể nằm đúng mốc local \\((0,0,0)\\), sau đó thực hiện `Set Origin to 3D Cursor` ở dưới đáy.
2. **Lỗi tia ngắm bị trượt trên vách đá dốc (Missed Rays on Steep Slopes)**:
   * *Hiện tượng*: Vật thể biến mất hoặc bị trôi khỏi vách núi dốc đứng [4, 5, 18].
   * *Khắc phục*: Lọc điểm phát sinh bằng cổng `Is Hit` của Raycast [15-17], hoặc chuyển sang quy trình `Geometry Proximity` + `Sample Nearest` & `Sample Index` để lấy pháp tuyến và vị trí mặt dốc gần nhất thay vì chiếu tia dọc thẳng đứng [4, 5, 18].
3. **Lỗi giật lắc, móp méo lưới do Tọa độ Đại địa Tuyệt đối (Float32 Drift & Jitter)**:
   * *Hiện tượng*: Lưới địa hình và công trình bị méo mó, giật giật (**jitter**) khi quan sát hoặc thu nhỏ [22, 23, 26, 30, 31, 33, 34, 58-60].
   * *Khắc phục*: Kiểm tra cài đặt Geoscene trong BlenderGIS, đảm bảo luôn dịch tâm địa hình về sát gốc tọa độ \\((0,0,0)\\) Cartesian bằng vectơ offset \\(\mathbf{T}_{\text{offset}}\\) (\\(\mathbf{P}_{\text{local}} = \mathbf{P}_{\text{geographic}} - \mathbf{T}_{\text{offset}}\\)) [38-43].
4. **Lỗi công trình/cột điện bị đổ nghiêng theo sườn dốc**:
   * *Hiện tượng*: Cột điện hay tòa nhà bị xoay xiên xẹo theo độ dốc địa hình.
   * *Khắc phục*: Với các công trình cần giữ phương thẳng đứng (Trục Z toàn cục), chỉ sử dụng `Hit Position` để đặt độ cao chân đế, tuyệt đối không dùng `Hit Normal` để quay trục Z trừ khi đó là cây cối mọc nghiêng tự nhiên [15-17].
5. **Lỗi mặt bị đen hoặc hư hỏng hiển thị Viewport (Black Faces & Camera Clipping)**:
   * *Hiện tượng*: Địa hình rộng lớn xuất hiện các mảng đen rác (**black artifacts**) hoặc mặt bị cắt hỏng trên Viewport/Render [61-68].
   * *Khắc phục*: Mở bảng điều khiển N-Panel của Viewport 3D, điều chỉnh khoảng cách `Clip Start` ngắn lại sát khung cảnh và tăng `Clip End` đủ bao phủ toàn bộ vùng địa hình [61-70].

---

🌲 Nếu bạn muốn tối ưu hóa hiệu năng hiển thị cho các khung cảnh địa hình quy mô lớn, mình có thể hướng dẫn thiết lập hệ thống **Level of Detail (LOD)** tự động chuyển đổi mô hình chi tiết cao/thấp dựa trên khoảng cách camera trong Geometry Nodes!
