# [L12] Phân tích & Đóng gói kỹ thuật từ tài liệu: Blackbody | Adobe Substance 3D Designer - Experience League

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Chuyên sâu theo Nguồn (Level 4)
- **Ngày trích xuất:** 2026-11-06

---

**1. Tóm tắt Bản chất (2-3 câu)**
Công cụ **Blackbody** là node chuyển đổi nhiệt độ màu từ đơn vị Kelvin sang giá trị màu RGB trong đồ họa 3D [1]. Tính năng này giúp tái tạo màu sắc ánh sáng dựa trên nguyên lý bức nhiệt thực tế, trong đó giá trị Kelvin thấp tạo ra tông màu ấm và giá trị Kelvin cao tạo ra tông màu lạnh [1]. Việc ứng dụng đúng nguyên lý này mang lại tính chân thực cho ánh sáng môi trường và HDRI thay vì chọn màu RGB thủ công [1].

---

**2. Nguyên lý & Thông số Chuẩn**
*   **Vị trí & Phân loại:** Nằm trong nhóm `3D View > HDRI Tools` [1].
*   **Cơ chế chuyển đổi:** Chuyển đổi định lượng nhiệt độ màu tính theo độ Kelvin thành không gian màu RGB [1].
*   **Quy tắc phối màu:**
    *   **Giá trị Kelvin thấp (Lower Kelvin):** Cho ra các gam màu **ấm** (*warmer colors*) như vàng, cam, đỏ [1].
    *   **Giá trị Kelvin cao (Higher Kelvin):** Cho ra các gam màu **lạnh** (*colder colors*) như trắng xanh, xanh dương [1].
*   **Dải thông số chuẩn (Temperature):** Giá trị nhiệt độ Kelvin nằm trong khoảng từ **1000.0 K đến 27000.0 K** [1].

---

**3. Cách áp dụng trong Blender**
> *Lưu ý về nguồn tài liệu:* Tài liệu được chọn cung cấp quy chuẩn thông số Kelvin và cơ chế chuyển đổi sang RGB, nhưng không chứa mã lệnh Python `bpy` hay giao diện riêng của Blender [1].

Dựa trên nguyên lý kỹ thuật từ tài liệu [1], cách đưa kiến thức này vào Blender như sau:

*   **Thiết lập Shader Node:** Trong Blender (Shader Editor hoặc World Nodes), cơ chế này tương ứng với node **Blackbody**. Bạn nối đầu ra *Color* của node Blackbody vào cổng *Color* hoặc *Emission* của nguồn sáng.
*   **Áp dụng Dải thông số Kelvin chuẩn [1]:**
    *   **1000 K – 3000 K (Tông ấm):** Ánh nến, đèn dây tóc, ánh lửa hoặc hoàng hôn [1].
    *   **5000 K – 6500 K (Trung tính):** Ánh sáng mặt trời giữa trưa, cân bằng trắng tiêu chuẩn [1].
    *   **7000 K – 27000 K (Tông lạnh):** Ánh sáng bầu trời trong, bóng râm hoặc môi trường ánh sáng xanh [1].

---

**4. Lỗi thường gặp & Cách kiểm tra**
*   **Hiểu ngược chiều nhiệt độ Kelvin:** Nhầm lẫn giữa Kelvin cao/thấp (luôn nhớ quy tắc: Kelvin thấp = sắc ấm đỏ/vàng; Kelvin cao = sắc lạnh xanh) [1].
*   **Vượt dải thông số tiêu chuẩn:** Nhập giá trị Kelvin nhỏ hơn **1000.0 K** hoặc vượt quá **27000.0 K**, dẫn đến kết quả màu biến dạng không đúng với quang phổ bức nhiệt thực tế [1].
*   **Chỉnh màu RGB cảm tính:** Tự chọn màu RGB bằng tay thay vì thông qua thông số Kelvin, khiến nguồn sáng thiếu tính nhất quán về mặt vật lý [1].

💡 *Bạn có muốn chọn thêm các tài liệu khác trong sổ (như tài liệu kỹ thuật Blender EEVEE/Cycles) để mở rộng hướng dẫn thiết lập node và code Python chi tiết trong Blender không?*
