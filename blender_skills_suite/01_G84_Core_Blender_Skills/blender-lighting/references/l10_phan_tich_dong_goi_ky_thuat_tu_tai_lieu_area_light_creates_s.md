# [L10] Phân tích & Đóng gói kỹ thuật từ tài liệu: Area light creates shadow lines - Lighting and Rendering - Blender Artists Community

- **Chủ đề:** Ánh sáng & Khí quyển (Lighting & Atmosphere)
- **Sổ NotebookLM nguồn:** `NB_Lighting_Atmosphere: Three-point lightin`
- **Cấp độ:** Chuyên sâu theo Nguồn (Level 4)
- **Ngày trích xuất:** 2026-11-06

---

Dựa trên tài liệu **"Area light creates shadow lines - Lighting and Rendering - Blender Artists Community"**, dưới đây là bài học kỹ thuật chi tiết được đúc kết để xử lý hiện tượng vệt bóng đen bất thường khi sử dụng đèn Area trong Blender:

---

### 1. Tóm tắt Bản chất (2-3 câu)
Khi sử dụng đèn **Area** (hình vuông/chữ nhật) dạng dải mỏng để giả lập đèn LED sát trần, Blender có thể tạo ra một **vệt bóng đen/dải tối bất thường (shadow line)** chạy dọc trên tường dù không có vật thể nào cản sáng [1-3]. Hiện tượng này xuất phát từ sự kết hợp giữa góc phân tán ánh sáng (**Spread**) ở mức tối đa (180°) và sự thiếu chính xác trong lấy mẫu (sampling inaccuracy) ở các góc cực hạn khi dải đèn quá mỏng [4, 5]. Việc kiểm soát góc Spread, độ dày hình học hoặc chuyển sang dạng **Emission Geometry** là chìa khóa để xử lý lỗi này [5].

---

### 2. Nguyên lý & Thông số Chuẩn

*   **Thông số góc phân tán (Spread Angle):**
    *   **Mặc định (180°):** Ánh sáng tỏa ra ở góc tối đa nhưng dễ xuất hiện dải ranh giới/vệt bóng đen sắc nét "từ hư không" trên bề mặt tường tiếp giáp [2, 4].
    *   **Điều chỉnh (150° hoặc thấp hơn):** Giúp vệt bóng đen biến mất hoàn toàn [5]. Tuy nhiên, nếu giảm góc Spread quá nhiều, ánh sáng sẽ không chiếu tới phần đỉnh tường, tạo ra dải tối ở mép trần [5].
*   **Độ mỏng dải đèn & Sai số lấy mẫu (Sampling Inaccuracy):**
    *   Đèn Area dạng dải quá mỏng dễ phát sinh lỗi tính toán mẫu ở ranh giới phát sáng [5]. Việc tăng độ dày (width/thickness) của dải đèn giúp lấy mẫu ổn định hơn và triệt tiêu lỗi ranh giới [5].
*   **Giải pháp hình học phát sáng (Emission Geometry):**
    *   Sử dụng vật thể phát sáng (Emission Mesh) đặt âm trần (recessed lights) thay cho đèn Area [5]. Dù Emission Mesh có thể phát sinh nhiều nhiễu (noise) hơn, phương pháp này tránh được lỗi ranh giới vệt bóng của đèn Area [5].
*   **Cơ chế Light Linking & Shadow Linking (Blender 4.5+):**
    *   Cho phép liên kết hoặc loại trừ các vật thể cụ thể khỏi danh sách nhận ánh sáng hoặc đổ bóng của một nguồn sáng [3, 6].

---

### 3. Cách áp dụng trong Blender (Thao tác & Code Python `bpy`)

#### A. Thao tác thiết lập trên giao diện Blender (UI)
1.  **Hiệu chỉnh thông số Spread & Kích thước đèn Area:**
    *   Chọn đèn Area \\(\rightarrow\\) Mở tab **Light Properties** [4, 7].
    *   Giảm góc **Spread** từ 180° xuống mức thích hợp (khoảng 150°) để xóa dải bóng đen [4, 5].
    *   Tăng độ dày (Size/Width) của dải đèn Area thay vì để quá mỏng nhằm tránh sai số lấy mẫu [5].
2.  **Chuyển sang dải LED âm trần (Emission Geometry):**
    *   Tạo mô hình khối (Mesh) làm dải đèn LED âm trần, gán Shader **Emission** để phát sáng ổn định hơn [5].
3.  **Sử dụng Light Linking / Shadow Linking (Nếu cần loại trừ vật thể):**
    *   Chọn đèn Area \\(\rightarrow\\) Mở tab **Object Properties** \\(\rightarrow\\) Tìm mục **Shading** \\(\rightarrow\\) Mở **Light Linking** hoặc **Shadow Linking** \\(\rightarrow\\) Bấm **New** và kéo thả vật thể cần kiểm soát vào danh sách [3, 7].
    *   Hoặc tắt bỏ tùy chọn **Shadow** trong mục thuộc tính của đèn nếu không muốn đèn tạo bóng đổ [6, 7].

#### B. Kiểm soát bằng Python `bpy` / Nodes
> **Lưu ý về nguồn tài liệu:** *Tài liệu trong sổ không chứa các đoạn mã script Python `bpy` hay sơ đồ Shader Node cụ thể* [1-8]. Mọi thao tác được thảo luận trong tài liệu hoàn toàn dựa trên giao diện thiết lập trực quan (UI) của Blender.

---

### 4. Lỗi thường gặp & Cách kiểm tra

1.  **Nhầm lẫn nguồn gốc vệt bóng đen:**
    *   *Lỗi:* Cho rằng vệt bóng do vật thể ẩn hoặc vật thể khác tạo ra [2, 3, 6].
    *   *Cách kiểm tra:* Tắt lần lượt từng đèn trong cảnh (hoặc tắt hết và chỉ dùng HDRI) để xác định chính xác đèn gây lỗi [3, 8]. Tạo một mặt phẳng (Plane) thử nghiệm đặt sát tường để kiểm tra xem dải bóng có tiếp tục xuất hiện không [4].
2.  **Lỗi pháp tuyến bề mặt (Mesh Normals):**
    *   *Lỗi:* Bức tường có vẻ phẳng nhưng dữ liệu pháp tuyến bị sai (Custom Split Normals Data layer) gây ra sự cố phân bổ ánh sáng [4, 8].
    *   *Cách kiểm tra:* Bật hiển thị khung dây (**Wireframe**) và kiểm tra **Normals** của đối tượng tường [4, 8].
3.  **Lệ thuộc vào góc Spread 180° trên dải đèn quá mỏng:**
    *   *Lỗi:* Giữ nguyên Spread 180° trên đèn Area cực mỏng làm xuất hiện ranh giới tối [4, 5].
    *   *Khắc phục:* Tăng chiều rộng dải đèn hoặc đặt dải đèn dạng âm trần [5].
4.  **Lạm dụng Light Linking không đúng trường hợp:**
    *   *Lỗi:* Dùng Light Linking để loại trừ bức tường khỏi đèn Area, khiến tường bị mất hoàn toàn ánh sáng chiếu tới [2, 5].

💡 **Gợi ý tiếp theo:** Bạn có muốn tôi hỗ trợ tìm hiểu thêm các kỹ thuật tối ưu hóa ánh sáng EEVEE Next hoặc Cycles từ các tài liệu khác trong sổ không?
