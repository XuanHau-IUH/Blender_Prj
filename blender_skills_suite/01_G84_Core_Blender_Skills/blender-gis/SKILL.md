---
name: blender-gis
description: Kỹ năng Tái tạo Môi trường Đô thị & Dữ liệu Địa lý (Environment & BlenderGIS) trong Blender 5.1 cho Gate 84. Bao gồm hệ tọa độ CRS/UTM, nhập địa hình DEM/SRTM, khối công trình & đường hẻm từ OpenStreetMap (OSM), Delaunay Triangulation, Drop to Ground và phân bố đạo cụ bằng Geometry Nodes. Được bồi đắp tự động mỗi 9h sáng từ sổ NotebookLM NB_Environment_GIS.
---

# Kỹ năng Blender: Môi trường Đô thị & Địa lý (`blender-gis`)

> **Nguồn tri thức gốc:** Sổ NotebookLM `NB_Environment_GIS` (94 nguồn tài liệu)  
> **Cập nhật tự động:** 09:00 sáng hàng ngày (3 bài học/ngày từ Cơ bản → Nâng cao)  
> **Công cụ MCP liên kết:** `execute_blender_code` (Blender MCP), `world_blender_gis`, `world_geometry_nodes_scatter`

---

## 1. Mục đích & Khi nào sử dụng
Kỹ năng này hướng dẫn cách dựng **bối cảnh đô thị thực tế, địa hình tự nhiên và khu phố/con hẻm Việt Nam** trong Blender 5.1 bằng `BlenderGIS` và `Geometry Nodes`:
- Nhập dữ liệu bản đồ thực tế (OpenStreetMap `OSM`, cao độ `DEM`, Shapefile, ảnh vệ tinh georeferenced).
- Chuyển đổi hệ tọa độ địa lý (`WGS84` / `UTM Zone 48N - EPSG:32648` cho miền Nam/Sài Gòn hoặc `EPSG:32648/32649`) về gốc `(0,0,0)` của Blender.
- Tự động thả công trình, cây cối, cột điện bám sát mặt đất dốc (`bpy.ops.object.drop` hoặc `Raycast` trong Geometry Nodes).
- Phân bố chi tiết môi trường (dây điện, cỏ dại, rác đô thị, mặt tiền nhà phố) tiết kiệm bộ nhớ VRAM.

---

## 2. Nguyên tắc Sống Còn khi làm việc với Dữ liệu GIS trong Blender

1. **Không bao giờ để đối tượng ở tọa độ thực hàng triệu mét (ví dụ `X = 682,000m`, `Y = 1,192,000m`):** Blender lưu tọa độ đỉnh bằng số thực dấu phẩy động 32-bit (`float32`). Nếu để xa gốc `(0,0,0)` quá 10km, màn hình Viewport sẽ bị nhấp nháy Z-fighting và lưới bị răng cưa khi di chuyển. Luôn để `BlenderGIS` lưu tâm quy chiếu vào thuộc tính Scene (`GeoScene`) và đặt hình học tại `(0,0,0)`.
2. **Thả vật thể bám mặt đất (`Drop to Ground`):** Sau khi nhập các khối nhà OSM hoặc đạo cụ đường phố lên trên địa hình DEM lồi lõm, luôn dùng `bpy.ops.object.drop()` hoặc `Geometry Nodes Raycast (0, 0, -1)` để chân công trình ăn khớp xuống mặt đất.
3. **Dùng Instance thay vì Realize Mesh cho cây cối/đạo cụ lặp lại:** Khi rải hàng nghìn viên gạch, bụi cỏ, cột đèn bằng Geometry Nodes, luôn giữ ở chế độ `Pick Instance` để không làm tràn RAM/VRAM.

---

## 3. Mẫu Code Python (`bpy`) Chuẩn Hóa

### 3.1. Kích hoạt BlenderGIS và Thả hàng loạt đạo cụ bám xuống mặt đất (Ground Mesh)
```python
import bpy
import mathutils

def snap_objects_to_ground(object_names, ground_name, sink_offset=-0.02):
    """
    Bắn tia Raycast từ trên cao xuống mặt đất (ground_name) để đặt toàn bộ đối tượng
    trong danh sách object_names bám khít lên bề mặt địa hình.
    sink_offset = -0.02 (nhấn chìm nhẹ 2cm xuống đất để tránh hở chân công trình).
    """
    ground = bpy.data.objects.get(ground_name)
    if not ground:
        raise ValueError(f"Không tìm thấy mặt đất: {ground_name}")

    depsgraph = bpy.context.evaluated_depsgraph_get()
    ground_eval = ground.evaluated_get(depsgraph)
    inv_mat = ground_eval.matrix_world.inverted()

    for name in object_names:
        obj = bpy.data.objects.get(name)
        if not obj:
            continue
        world_origin = mathutils.Vector((obj.location.x, obj.location.y, 1000.0))
        local_origin = inv_mat @ world_origin
        local_dir = (inv_mat.to_3x3() @ mathutils.Vector((0.0, 0.0, -1.0))).normalized()

        hit, loc, normal, _ = ground_eval.ray_cast(local_origin, local_dir)
        if hit:
            world_hit = ground_eval.matrix_world @ loc
            obj.location.z = world_hit.z + sink_offset
```

---

### 3.2. Bộ Script Thực Thi Tự Động Chuẩn Blender 5.2 (scripts/)
- [scripts/bx_kits.py](scripts/bx_kits.py) & [scripts/bx_blockout.py](scripts/bx_blockout.py): Dựng nhanh khối nhà phố (uilding), cây cối (	ree), xe cộ (ehicle), quầy hàng vỉa hè (stall), cột đèn (street_lamp), rải đạo cụ tránh va chạm (scatter_points) và tạo đám đông/xe chạy trên đường (crowd, drive, pedal).
- [scripts/terrain.py](scripts/terrain.py), [scripts/scatter.py](scripts/scatter.py), [scripts/kit_check.py](scripts/kit_check.py), [scripts/gn_builder.py](scripts/gn_builder.py): Tạo địa hình, phân bố đạo cụ bằng Geometry Nodes 5.2 và kiểm tra chuẩn mô-đun Kitbash.
- [scripts/validate_scene.py](scripts/validate_scene.py), [scripts/validate_part_graph.py](scripts/validate_part_graph.py), [scripts/snapshot_scene.py](scripts/snapshot_scene.py): Kiểm định va chạm hình học, khe hở lắp ghép và chụp trạng thái scene trước/sau khi chỉnh sửa.

---

## 4. Danh mục Bài học Trích xuất Hàng ngày từ NotebookLM
*(Mỗi sáng 9h00, 3 kiến thức mới từ cơ bản đến nâng cao sẽ được tự động trích xuất từ `NB_Environment_GIS`, lưu chi tiết vào thư mục `references/` và cập nhật mục lục dưới đây)*

<!-- DAILY_LESSONS_INDEX -->
- **[G01 — Cơ bản (Level 1)] Hệ tọa độ địa lý (CRS / EPSG, WGS84 vs UTM) và thiết lập GeoScene gốc tọa độ trong BlenderGIS** *(Ngày 2026-10-30)* → Chi tiết: [`references/g01_he_toa_do_dia_ly_crs_epsg_wgs84_vs_utm_va_thiet_lap_geoscene.md`](references/g01_he_toa_do_dia_ly_crs_epsg_wgs84_vs_utm_va_thiet_lap_geoscene.md)
- **[G02 — Cơ bản (Level 1)] Nhập bản đồ nền vệ tinh (Basemap) và dữ liệu độ cao địa hình (DEM / SRTM Elevation)** *(Ngày 2026-10-30)* → Chi tiết: [`references/g02_nhap_ban_do_nen_ve_tinh_basemap_va_du_lieu_do_cao_dia_hinh_d.md`](references/g02_nhap_ban_do_nen_ve_tinh_basemap_va_du_lieu_do_cao_dia_hinh_d.md)
- **[G03 — Cơ bản (Level 1)] Truy vấn dữ liệu OpenStreetMap (OSM): Tái tạo khối nhà (Buildings), đường giao thông và hẻm phố** *(Ngày 2026-10-30)* → Chi tiết: [`references/g03_truy_van_du_lieu_openstreetmap_osm_tai_tao_khoi_nha_building.md`](references/g03_truy_van_du_lieu_openstreetmap_osm_tai_tao_khoi_nha_building.md)
- **[G04 — Trung cấp (Level 2)] Nội suy lưới địa hình (Delaunay Triangulation & Voronoi) từ đường đồng mức hoặc đám mây điểm** *(Ngày 2026-11-04)* → Chi tiết: [`references/g04_noi_suy_luoi_dia_hinh_delaunay_triangulation_voronoi_tu_duon.md`](references/g04_noi_suy_luoi_dia_hinh_delaunay_triangulation_voronoi_tu_duon.md)
- **[G05 — Trung cấp (Level 2)] Khớp công trình & Đạo cụ bám sát mặt đất dốc (Drop Objects to Ground & Raycast Snapping)** *(Ngày 2026-11-04)* → Chi tiết: [`references/g05_khop_cong_trinh_dao_cu_bam_sat_mat_dat_doc_drop_objects_to_g.md`](references/g05_khop_cong_trinh_dao_cu_bam_sat_mat_dat_doc_drop_objects_to_g.md)
- **[G06 — Trung cấp (Level 2)] Biến đường Curve OSM thành mặt đường nhựa, vỉa hè và dây điện võng bằng Geometry Nodes** *(Ngày 2026-11-04)* → Chi tiết: [`references/g06_bien_duong_curve_osm_thanh_mat_duong_nhua_via_he_va_day_dien.md`](references/g06_bien_duong_curve_osm_thanh_mat_duong_nhua_via_he_va_day_dien.md)
- **[G07 — Nâng cao (Level 3)] Phân bố thảm thực vật & Chi tiết đô thị thông minh (Geometry Nodes Point Distribute, Weight/Slope Mask & Instancing)** *(Ngày 2026-11-05)* → Chi tiết: [`references/g07_phan_bo_tham_thuc_vat_chi_tiet_do_thi_thong_minh_geometry_no.md`](references/g07_phan_bo_tham_thuc_vat_chi_tiet_do_thi_thong_minh_geometry_no.md)
- **[G08 — Nâng cao (Level 3)] Tạo chi tiết mặt tiền nhà phố (Procedural Building Facades) từ khối hộp OSM thô** *(Ngày 2026-11-05)* → Chi tiết: [`references/g08_tao_chi_tiet_mat_tien_nha_pho_procedural_building_facades_tu.md`](references/g08_tao_chi_tiet_mat_tien_nha_pho_procedural_building_facades_tu.md)
- **[G09 — Nâng cao (Level 3)] Tối ưu hóa đại cảnh môi trường lớn (Camera Frustum Culling, LOD, Linked Collections & Memory Budget)** *(Ngày 2026-11-05)* → Chi tiết: [`references/g09_toi_uu_hoa_dai_canh_moi_truong_lon_camera_frustum_culling_lo.md`](references/g09_toi_uu_hoa_dai_canh_moi_truong_lon_camera_frustum_culling_lo.md)
- **[E10 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: 27x OSM import · domlysz/BlenderGIS Wiki - GitHub** *(Ngày 2026-11-06)* → Chi tiết: [`references/e10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_27x_osm_import_domly.md`](references/e10_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_27x_osm_import_domly.md)
- **[E11 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: 27x OSM import · domlysz/BlenderGIS Wiki - GitHub** *(Ngày 2026-11-06)* → Chi tiết: [`references/e11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_27x_osm_import_domly.md`](references/e11_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_27x_osm_import_domly.md)
- **[E12 — Chuyên sâu theo Nguồn (Level 4)] Phân tích & Đóng gói kỹ thuật từ tài liệu: 27x OSM import · domlysz/BlenderGIS Wiki - GitHub** *(Ngày 2026-11-06)* → Chi tiết: [`references/e12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_27x_osm_import_domly.md`](references/e12_phan_tich_dong_goi_ky_thuat_tu_tai_lieu_27x_osm_import_domly.md)
