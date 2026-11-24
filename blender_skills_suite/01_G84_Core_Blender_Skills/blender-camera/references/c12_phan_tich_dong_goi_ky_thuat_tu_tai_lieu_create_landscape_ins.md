# [C12] Phân tích & Đóng gói kỹ thuật từ tài liệu: Create Landscape Inside Blender 3D | Full Tutorial with project file

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Chuyên sâu theo Nguồn (Level 4)
- **Ngày trích xuất:** 2026-11-06

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
**Quy trình dựng cảnh quan đại cảnh 3D (Large-scale Environment) trong Blender tập trung vào việc làm chủ góc nhìn camera, phân lớp không gian (FG, MG, BG) và thiết lập môi trường ánh sáng - khí quyển đồng bộ.** Phương pháp này giúp tối ưu hóa hiệu suất làm việc bằng cách chỉ tập trung xử lý chi tiết trong tầm nhìn của ống kính mà không tốn tài nguyên cho các vùng thừa [1, 2]. Sự kết hợp giữa vật liệu nước tính toán (procedural water), rải lá/cỏ rác tự nhiên và sương mù khí quyển (volumetric fog) mang lại chiều sâu điện ảnh chân thực cho tác phẩm [3-5].

---

### 2. **Nguyên lý & Thông số Chuẩn**
Dưới đây là các thông số kỹ thuật chuẩn được trích xuất trực tiếp từ quy trình thực hiện trong bài học:

- **Khung hình & Camera:**
  - **Tiêu cự góc rộng (Focal Length):** **30mm – 35mm** [1].
  - **Bố cục:** Áp dụng quy tắc một phần ba (**Rule of Thirds**), đặt công trình chính lệch sang bên trái hoặc bên phải khung hình [6].
  - **Depth of Field (DoF):** Bật DoF trên camera, focus trực tiếp vào mô hình nhà chính với **F-stop = 1.0** để làm mờ mạnh khu vực tiền cảnh (FG) [7, 8].
- **Mặt nước & Vật liệu (Procedural Water):**
  - **Tỷ lệ Scale plane nước:** Phóng to mặt nước lên **50 lần (50x)** rồi nhân tiếp **10 lần** nữa (tổng cộng 500x) để phủ kín đường chân trời [9].
  - **Vật liệu nước (BlenderKit Procedural Water):** Thiết lập **Water Scale = 1.5 – 2.0** (tạo mặt nước tĩnh) và **Waves = 1.0** [4].
- **Ánh sáng (Lighting & HDRI):**
  - **Sky Texture:** Thiết lập **Sun Elevation = 15° – 45°**, **Sun Rotation = 19°**, **Sun Size = 5.0** (giúp bóng đổ mềm mại), **Sun Strength = 1.0 – 2.0** [10-12].
  - **HDRI Sunset:** Trộn nguồn sáng HDRI hoàng hôn với Sky Texture thông qua node **Add Shader** với **Strength = 1.5 – 2.0** để triệt tiêu các vùng bóng đen xì [13-15].
  - **Quy tắc hướng sáng:** Không đặt mặt trời chiếu thẳng từ hướng camera (Frontal light); luôn đặt ở góc nghiêng/ngược (Side/Backlight 45°) [11].
- **Khí quyển & Volumetric Fog (Principled Volume):**
  - **Density (Độ đặc sương mù):** **0.005** [5].
  - **Emission Strength:** **0.005** (hoặc 0.01) [5, 16].
  - **Anisotropy:** **1.0** (để sương mù gom ánh sáng về phía nguồn sáng) [5].
  - **Tối ưu hóa Light Paths:** Bật **Fast GI Approximation** trong bảng thiết lập Light Paths [5].
- **Cấu hình Render & Compositing (Cycles):**
  - **Cycles GPU Samples:** **84 samples** [10, 17].
  - **Volume Step Rate / Steps:** **6 steps** [17].
  - **Color Management:** Thiết lập **Medium High Contrast**, tinh chỉnh Gamma để tạo tông màu vàng hoàng hôn [17].
  - **Glare Node (Compositor):** Loại **Bloom**, **Mix = -1.0**, **Threshold = 1.5** [18].
  - **Lens Distortion Node:** **Distort = -0.04** (tạo hiệu ứng tán sắc Chromatic Aberration ở viền ảnh) [18].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### A. Các bước thao tác trên giao diện (GUI)
1. **Thiết lập Camera & Bố cục:** Import mô hình nhà (`.glb`), tạo Camera góc rộng (30-35mm), căn góc nhìn qua `Ctrl + Alt + Numpad 0`, xoay nhẹ nhà và nền đất để tạo góc nghiêng vừa mắt [1, 6].
2. **Mặt nước & Tiền cảnh:** Thêm Plane làm nước, scale 500x và đẩy nhẹ theo trục Z để ngập một phần chân công trình [9]. Bố trí các asset tiền cảnh (FG) như thuyền, nhánh cây nhô khỏi mặt nước [19].
3. **Phân tán Lá khô & Cỏ:** Tạo Collection "Leaves", dùng **GeoScatter** (hoặc Manual Scatter với Dot/Spray Brush) để rải lá khô rải rác trên nước [3, 20, 21]. Dùng **GeoScatter Biomes** (Spring Grass / Grass 4) phủ kín nền đất [22, 23].
4. **Cây Hậu cảnh (Background Trees):** Tạo Plane phía sau, dùng Sculpt mode đẩy nâng chiều cao địa hình, gán **Hair Particle System** (Render type: Collection, Rotation: None, Scale Randomization = 1.0) [24-26].
5. **Khí quyển & Compositing:** Thêm khối Cube bao phủ toàn bộ cảnh, gán shader **Principled Volume**, lùi khối Cube về phía sau xa camera [5, 8]. Bật **Compositing Nodes** kết nối Glare (Bloom) và Lens Distortion [18].

#### B. Đội mã tự động hóa Python `bpy`
Đoạn mã dưới đây giúp tự động hóa việc thiết lập Camera, Render Engine Cycles, Volumetric Fog và hệ thống Compositing Nodes đúng theo các thông số kỹ thuật bài học:

```python
import bpy

# 1. Thiet lap Camera goc rong & Depth of Field (DoF)
cam_data = bpy.data.cameras.new(name="Cinematic_Camera")
cam_data.lens = 30  # Tieu cu 30mm
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 1.0  # F-stop = 1.0

cam_obj = bpy.data.objects.new("Cinematic_Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (-12, -18, 4)
cam_obj.rotation_euler = (1.3, 0, -0.6)

# 2. Tao mat nuoc scale lon (Water Plane)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.2))
water_plane = bpy.context.active_object
water_plane.name = "Large_Water_Surface"
water_plane.scale = (500, 500, 1)  # Scale 500x phu kin duong chan troi

# 3. Thiet lap Cycles Render Engine & Fast GI
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 84
scene.cycles.volume_step_rate = 1.0
scene.cycles.use_fast_gi = True  # Fast GI Approximation

# 4. Tao khoi Volumetric Fog (Principled Volume)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 2))
fog_cube = bpy.context.active_object
fog_cube.name = "Volumetric_Fog_Cube"
fog_cube.scale = (100, 100, 20)

fog_mat = bpy.data.materials.new(name="Volumetric_Fog_Mat")
fog_mat.use_nodes = True
nodes = fog_mat.node_tree.nodes
nodes.clear()

node_volume = nodes.new(type='ShaderNodeVolumePrincipled')
node_volume.inputs['Density'].default_value = 0.005
node_volume.inputs['Emission Strength'].default_value = 0.005
node_volume.inputs['Anisotropy'].default_value = 1.0

node_output = nodes.new(type='ShaderNodeOutputMaterial')
fog_mat.node_tree.links.new(
    node_volume.outputs['Volume'], node_output.inputs['Volume']
)
fog_cube.data.materials.append(fog_mat)

# 5. Thiet lap Post-Processing Compositing Nodes
scene.use_nodes = True
comp_nodes = scene.node_tree.nodes
comp_links = scene.node_tree.links
comp_nodes.clear()

render_layers = comp_nodes.new(type='CompositorNodeRLayers')

# Glare Node (Bloom)
glare_node = comp_nodes.new(type='CompositorNodeGlare')
glare_node.glare_type = 'BLOOM'
glare_node.mix = -1.0
glare_node.threshold = 1.5

# Lens Distortion Node (Chromatic Aberration)
lens_dist = comp_nodes.new(type='CompositorNodeLensdist')
lens_dist.inputs['Distort'].default_value = -0.04
lens_dist.use_fit = True

comp_output = comp_nodes.new(type='CompositorNodeComposite')

# Ket noi cac Node
comp_links.new(render_layers.outputs['Image'], glare_node.inputs['Image'])
comp_links.new(glare_node.outputs['Image'], lens_dist.inputs['Image'])
comp_links.new(lens_dist.outputs['Image'], comp_output.inputs['Image'])
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

- **Lỗi 1: Đường chân trời nước bị đứt đoạn (Fake horizon cutoff).**
  - *Nguyên nhân:* Plane nước quá nhỏ, làm lộ ra vệt kết thúc của đường chân trời trong khung nhìn camera [9].
  - *Cách kiểm tra & Sửa:* Phóng to mặt nước lên từ 50x đến 500x để bao phủ hoàn toàn tầm nhìn xa của ống kính [9].
- **Lỗi 2: Khung hình bị bẹt, mất khối do chiếu ánh sáng trực diện.**
  - *Nguyên nhân:* Đặt Sun Light chiếu cùng hướng với góc nhìn của Camera [11].
  - *Cách kiểm tra & Sửa:* Đặt Sun Light lệch góc (Side/Backlight ~45°), đồng thời kết hợp HDRI Sunset qua nút `Add Shader` để làm dịu và lấp đầy các vùng bóng xám/đen xì [11, 13, 15].
- **Lỗi 3: Toàn bộ khung cảnh bị đục mờ, mất chi tiết tiền cảnh.**
  - *Nguyên nhân:* Để khối Volumetric Fog Cube trùm trực tiếp lên trước ống kính Camera [8].
  - *Cách kiểm tra & Sửa:* Đẩy khối Volume Cube lùi về phía sau trục Z/Y, giữ khoảng không giữa Camera và tiền cảnh trong trẻo [8].
- **Lỗi 4: Cây cối background trong Particle System bị mọc đâm ngược xuống dưới.**
  - *Nguyên nhân:* Mặt phẳng mesh bị lật ngược hướng Normal (Face Orientation) [25, 26].
  - *Cách kiểm tra & Sửa:* Bật *Face Orientation* trong Viewport Overlays (vùng màu đỏ là bị lật). Vào Edit Mode, nhấn `A` chọn tất cả mặt và bấm `Alt + N` > `Flip` [25, 26]. Trong bảng Particle System > Rotation, chọn `None` để cây mọc thẳng đứng [26].
- **Lỗi 5: Lag nặng viewport và thời gian render quá lâu.**
  - *Nguyên nhân:* Rải quá nhiều hạt Scatter hiển thị trực tiếp trong viewport hoặc đặt Max Samples/Volume Steps quá cao [17, 24].
  - *Cách kiểm tra & Sửa:* Tắt hiển thị Scatter trong viewport khi dựng hình; hạ Cycles Max Samples xuống **84**, Volume Steps xuống **6** và bật **Fast GI Approximation** [5, 17, 24].

💡 *Bạn có muốn tạo một báo cáo tóm tắt Markdown chi tiết hoặc bộ tài liệu minh họa quy trình dựng cảnh điện ảnh này lưu vào sổ không?*
