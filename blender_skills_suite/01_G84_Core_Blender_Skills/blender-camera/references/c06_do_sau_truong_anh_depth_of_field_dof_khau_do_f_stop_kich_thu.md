# [C06] Độ sâu trường ảnh (Depth of Field - DOF): Khẩu độ f-stop, kích thước cảm biến (Sensor Width) và lấy nét theo Object

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Trung cấp (Level 2)
- **Ngày trích xuất:** 2026-11-04

---

Dưới đây là giải thích chi tiết về mối liên hệ giữa kích thước cảm biến (Sensor Size), tiêu cự (Focal Length), khẩu độ (f-stop) và khoảng cách lấy nét (Focus Distance) để kiểm soát độ xóa phông (Bokeh / Depth of Field) tự nhiên trong Blender dựa trên các tài liệu trong sổ tay của bạn:

---

### 1. **Tóm tắt Bản chất (2-3 câu)**
**Độ xóa phông (Depth of Field / Bokeh)** trong Blender là kỹ thuật mô phỏng cơ chế quang học của máy ảnh thực tế, giúp làm mờ tiền cảnh hoặc hậu cảnh để định hướng sự chú ý của người xem vào chủ thể chính và tạo cảm giác điện ảnh (cinematic) [1-3]. Việc làm chủ sự kết hợp giữa cảm biến, tiêu cự, khẩu độ và khoảng cách lấy nét giúp bạn chủ động kiểm soát trường ảnh mỏng hay dày, tái tạo hiệu ứng Bokeh tự nhiên thay vì làm mờ giả tạo hay bị out-focus cực đoan [4-6].

---

### 2. **Nguyên lý & Thông số Chuẩn**
Trong máy ảnh thực tế cũng như môi trường 3D của Blender, các thông số này có sự phân chia vai trò rõ ràng giữa **Thân máy (Camera Body)** và **Ống kính (Lens)** [4, 5]:

*   **Kích thước Cảm biến (Sensor Size - Thân máy):** [4, 5]
    *   **Full-frame (36mm):** Kích thước cảm biến tiêu chuẩn mặc định của camera trong Blender [4, 5].
    *   **Super35 (khoảng 24mm – 24.89mm):** Chuẩn cảm biến điện ảnh truyền thống [4].
    *   *Tác động:* Cảm biến càng lớn (như Full-frame 36mm) sẽ cung cấp góc nhìn rộng hơn so với Super35 ở cùng một tiêu cự. Để giữ nguyên bố cục khung hình (framing) của chủ thể, bạn bắt buộc phải di chuyển máy ảnh lại gần hơn hoặc tăng tiêu cự dài hơn — chính thao tác này gián tiếp làm giảm chiều sâu trường ảnh (DoF) và làm hậu cảnh bị xóa mờ (Bokeh) đậm hơn [4, 5].
*   **Tiêu cự (Focal Length - Ống kính):** Đo bằng đơn vị `mm` (vd: `35mm`, `50mm`, `85mm`) [4, 7]. Tiêu cự càng dài (ống kính tele) sẽ làm nén khoảng cách không gian hậu cảnh, thu hẹp góc nhìn (Field of View) và tạo ra độ xóa phông mạnh mẽ, mịn màng hơn so với ống kính góc rộng [4, 7].
*   **Khẩu độ (Aperture / f-stop - Ống kính):** Được biểu diễn bằng chỉ số f-stop [4, 5]. **Chỉ số f-stop càng nhỏ** (khẩu độ mở càng lớn, vd: `f/1.4`, `f/1.8`, `f/2.8`) thì **trường ảnh (Depth of Field) càng mỏng**, làm độ xóa phông / Bokeh càng mờ đậm [2, 3, 6].
*   **Khoảng cách lấy nét (Focus Distance / Focus Object):** Khoảng cách từ vị trí camera tới điểm lấy nét [2, 3, 6]. Máy ảnh đặt **càng gần chủ thể** thì trường ảnh càng mỏng và hậu cảnh phía sau **càng bị xóa mờ mạnh** [3, 6].
*   **Hình dáng Bokeh (Aperture Blades):** Số lượng lá khẩu trong ống kính quyết định hình dạng của các vệt sáng Bokeh [6]:
    *   `0`: Bokeh tròn tự nhiên (đường tròn hoàn hảo) [6].
    *   `3`: Ngũ giác / Đa giác 3 cạnh (Tam giác) [6].
    *   `4`: Hình vuông [6].
    *   `5`: Ngũ giác [6].
    *   `6`: Lục giác [6].

---

### 3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)**

#### **Thao tác thủ công trên giao diện Blender (GUI):**
1. Chọn Camera -> chuyển sang thẻ **Camera Properties** (biểu tượng máy ảnh màu xanh) [6, 8].
2. **Sensor Size:** Mở mục **Sensor**, chỉnh **Width** thành `36 mm` (Full-frame) hoặc `24 mm` / `24.89 mm` (Super35) [4, 5].
3. **Tiêu cự:** Tại mục **Lens**, nhập **Focal Length** mong muốn (vd: `50 mm` hoặc `85 mm`) [4, 7].
4. **Bật Depth of Field:** Tích chọn ô **Depth of Field** [3, 6, 9].
5. **Tiêu điểm lấy nét:** Tại mục **Focus Object**, chọn một đối tượng mục tiêu (ví dụ: một đối tượng **Empty** được liên kết parenting hoặc di chuyển để làm kỹ thuật *Rack Focus*) [2, 3, 10] hoặc kéo thanh **Focus Distance** [3, 6].
6. **Khẩu độ & Bokeh:** Mở rộng mục **Aperture**, hạ chỉ số **F-stop** xuống mức nhỏ (vd: `1.4`, `1.8`, `2.8`) [2, 3, 6]. Để thay đổi hình dạng hạt Bokeh sáng, điều chỉnh thông số **Blades** (`0` cho Bokeh tròn tự nhiên) [6].

#### **Đoạn mã Python `bpy` thiết lập tự động:**

```python
import bpy

# Lấy camera hiện tại đang active trong scene
cam_obj = bpy.context.scene.camera

if cam_obj and cam_obj.type == 'CAMERA':
    cam_data = cam_obj.data
    
    # 1. Cấu hình Kích thước Cảm biến (Sensor Size)
    cam_data.sensor_width = 36.0  # Full-frame: 36mm (hoặc 24.89mm cho Super35)
    
    # 2. Thiết lập Tiêu cự (Focal Length)
    cam_data.lens = 85.0  # Ống kính 85mm
    
    # 3. Kích hoạt tính năng Depth of Field
    cam_data.dof.use_dof = True
    
    # 4. Gán đối tượng mục tiêu lấy nét (Focus Object) hoặc Khoảng cách (Focus Distance)
    focus_target = bpy.data.objects.get("Empty")
    if focus_target:
        cam_data.dof.focus_object = focus_target  # Lấy nét vào đối tượng Empty
    else:
        cam_data.dof.focus_distance = 3.5  # Lấy nét cố định ở khoảng cách 3.5 mét
        
    # 5. Cấu hình Khẩu độ (f-stop) và Hình dạng Bokeh
    cam_data.dof.aperture_fstop = 1.8  # Khẩu độ mở lớn f/1.8 giúp xóa phông mịn
    cam_data.dof.aperture_blades = 0   # 0 = Bokeh hình tròn tự nhiên (5 = ngũ giác, 6 = lục giác)
```

---

### 4. **Lỗi thường gặp & Cách kiểm tra**

*   **Lỗi 1: Đặt f-stop quá nhỏ hoặc cực đoan không thực tế.** (Vd: lạm dụng f/0.1 làm cả chủ thể chính bị nhòe mờ, mất nét chi tiết). *Cách khắc phục:* Nên sử dụng các chỉ số f-stop chuẩn của ống kính máy ảnh thực tế (như `f/1.4`, `f/2.8`, `f/4.0`) để hình ảnh giữ được độ chân thực [2].
*   **Lỗi 2: Cố định khoảng cách lấy nét (Focus Distance) bằng số khi chủ thể di chuyển.** Khi nhân vật chuyển động trong hoạt cảnh animation, chủ thể dễ bị out-focus (mất nét). *Cách khắc phục:* Tạo một đối tượng **Empty**, gán parent hoặc di chuyển Empty theo nhân vật, sau đó chọn Empty này làm **Focus Object** [2, 3, 10].
*   **Lỗi 3: Quên bật tích Depth of Field trong thẻ Camera Properties.** Nếu chỉ hạ f-stop mà không bật tích **Depth of Field**, Blender sẽ không hiển thị hiệu ứng xóa phông khi render [3, 6].
*   **Cách kiểm tra trực quan:**
    *   Nhấn phím `Z` -> chọn **Rendered View** trong Viewport (dùng Engine Cycles/EEVEE) để quan sát hiệu ứng xóa phông theo thời gian thực [11, 12].
    *   Trong thẻ **Camera Properties** -> mở mục **Viewport Display** -> tích chọn **Limits**. Lúc này Blender sẽ hiển thị một dấu chữ thập `+` màu vàng chỉ rõ chính xác vị trí tiêu điểm lấy nét (Focus Point) trực quan trong môi trường 3D.

---

🎬 *Bạn có muốn tôi hướng dẫn chi tiết kỹ thuật tạo chuyển động chuyển nét (Rack Focus) mượt mà từ tiền cảnh sang hậu cảnh bằng keyframe kết hợp đối tượng Empty trong Blender không?*
