# [C11] Phân tích & Đóng gói kỹ thuật từ tài liệu: Create Custom Buildings in Blender - Lazy Tutorials

- **Chủ đề:** Bố cục Máy quay & Tiêu cự (Camera Blocking & Focal Length)
- **Sổ NotebookLM nguồn:** `Camera blocking, tiêu cự, lens matching, bố cục khung hình.`
- **Cấp độ:** Chuyên sâu theo Nguồn (Level 4)
- **Ngày trích xuất:** 2026-11-06

---

1. **Tóm tắt Bản chất (2-3 câu):**
Phương pháp tạo công trình kiến trúc tùy chỉnh trong tài liệu "Create Custom Buildings in Blender - Lazy Tutorials" dựa trên quy trình phác thảo khối (blocking) đơn giản, phủ chất liệu bằng kỹ thuật chiếu **Cube Projection**, sau đó cắt và đùn khối trực tiếp theo chi tiết ảnh texture [1]. Cách tiếp cận này giúp tạo ra nhiều tòa nhà 3D chân thực, mang dấu ấn thủ công độc đáo một cách nhanh chóng mà không bị cảm giác rập khuôn hay phụ thuộc vào các asset dựng sẵn [1, 2].

2. **Nguyên lý & Thông số Chuẩn:**
- **Quy tắc phác thảo khối (Blocking & Bố cục):** Bắt đầu bằng các khối hộp (boxes), sử dụng chủ yếu thao tác extrude (đùn khối) và thêm edge loops (vòng cạnh) để chốt bố cục toàn cảnh và thử nghiệm ánh sáng trước khi đi vào chi tiết [1].
- **Kỹ thuật chiếu UV (Cube Projection):** Gán Image Texture vào Material, mở **UV Editor**, chọn toàn bộ các mặt và thực hiện **Cube Projection** (phím `U`) để căn chỉnh texture nhanh chóng [1].
- **Cắt & đùn khối theo ảnh:** Sử dụng Knife tool (phím `K`) để đi nét trực tiếp theo chi tiết bức ảnh texture rồi extrude nhô ra hoặc thụt vào [1]. Dùng phím `I` (Inset) để lùi các ô cửa sổ vào trong [2].
- **Nguyên lý phá vỡ sự hoàn hảo (Imperfection):** Chủ động làm dịch chuyển/lệch ngẫu nhiên một số edge loops và vertices để công trình bớt quá thẳng và cứng nhắc, tạo cảm giác tự nhiên [2].
- **Thiết lập Shader cửa sổ:** Chọn riêng các mặt cửa sổ, gán Material mới sử dụng **Glossy** hoặc **Translucent Shader** và đặt thêm ánh sáng phía trong phòng [2].
- **Chuẩn hóa UV:** Kích hoạt add-on **UV Squares** để làm thẳng các lưới UV bị méo lệch chỉ với một cú nhấp chuột [2].
*(Lưu ý: Tài liệu gốc tập trung vào quy trình thao tác thực chiến và phím tắt, không cung cấp các con số kích thước hay tỷ lệ định lượng cụ thể).*

3. **Cách áp dụng trong Blender (Thao tác & Code Python `bpy`):**
- **Các bước thao tác chi tiết trong Blender:**
  1. **Dựng khối sơ bộ:** Tạo các khối hộp (Cube), dùng `Ctrl + R` (Edge Loop) và `E` (Extrude) để tạo dáng tòa nhà, canh góc máy và ánh sáng [1].
  2. **Gán Material & Trải UV:** Tạo Material mới với Image Texture phù hợp. Vào **UV Editor**, chọn tất cả các mặt (`A`), ấn `U` > **Cube Projection** và di chuyển các mảng UV cho khớp với hình ảnh [1].
  3. **Tạo chi tiết theo Texture:** Trong Edit Mode, dùng Knife tool (`K`) cắt theo khung chi tiết trên ảnh texture, extrude các phần nhô ra/móp vào. Chọn các mặt cửa sổ và bấm `I` (Inset) để thụt vào [1, 2].
  4. **Tạo độ lệch tự nhiên:** Chọn ngẫu nhiên một số cạnh hoặc đỉnh, kéo lệch nhẹ để công trình trông gồ ghề thủ công [2].
  5. **Tạo chất liệu cửa sổ:** Chọn các mặt cửa sổ, gán Material riêng với Glossy/Translucent Shader và thêm nguồn đèn phía trong [2].
  6. **Nắn thẳng UV:** Dùng add-on **UV Squares** để thẳng hóa lưới UV nếu bị cong méo [2].
- **Về tự động hóa bằng Python `bpy`:**
  - *Lưu ý về nguồn tài liệu:* Video hướng dẫn thực hiện hoàn toàn bằng phím tắt và thao tác giao diện (UI) trong Blender, **không chứa đoạn mã Python `bpy`**. Các thao tác UI chính trong video tương ứng với các lệnh Blender sau:
    - Chiếu UV Cube Projection: Phím `U` > `Cube Projection` [1].
    - Cắt Knife tool: Phím `K` [1].
    - Thụt lề Inset: Phím `I` [2].
    - Làm thẳng UV: Add-on `UV Squares` [2].

4. **Lỗi thường gặp & Cách kiểm tra:**
- **Texture bị kéo giãn (Stretching):** Xảy ra khi cắt hoặc đùn khối mới làm biến dạng UV.
  - *Cách khắc phục:* Chọn các mặt bị giãn texture, tiến hành reproject lại (`U`) và di chuyển/sắp xếp lại mảng UV đó [1].
- **Mô hình quá thẳng và mang tính "máy móc":** Do giữ nguyên hình học phẳng hoàn hảo.
  - *Cách khắc phục:* Kéo lệch ngẫu nhiên các vòng cạnh (edge loops) và đỉnh (vertices) để tạo độ không hoàn hảo tự nhiên [2].
- **Lưới UV bị cong méo:**
  - *Cách khắc phục:* Sử dụng add-on **UV Squares** để làm thẳng lưới UV [2].
- **Cửa sổ phẳng lì, thiếu độ sâu:**
  - *Cách khắc phục:* Dùng `I` (Inset) đẩy mặt cửa vào trong, gán Glossy/Translucent Shader và bật đèn bên trong [2].

💡 Bạn có muốn mở rộng phân tích sang kỹ thuật dựng cảnh môi trường quy mô lớn (World Building) hay kỹ thuật ánh sáng Cinematic trong các nguồn bài học khác có trong sổ không?
