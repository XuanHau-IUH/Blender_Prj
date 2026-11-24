---
name: g84-phu-vo-stablegen
description: Phủ texture cho set Blender bằng StableGen + ComfyUI local, chỉnh màu theo canon, có ngưỡng đo sáng tự kiểm. Dùng sau khi set dựng từ bảng đã được duyệt.
---
# g84-phu-vo-stablegen

- Script: `E:\G84\lenh_cuc\tools\chay_c4_stablegen_tang52.py --loc <LOC> | --config <json> --mode post_only|regen_shell_b1|full`, có README cùng thư mục. StableGen 0.4.0 nhánh Qwen 2.1, trỏ về ComfyUI 8188, KHÔNG chạy `installer.py`.
- Chỉ phủ vật có `nhan_texture=true`. Chạy 2 lượt: vỏ kiến trúc riêng, đạo cụ riêng. Làm trên bản sao `.blend`.
- NGUYÊN TẮC: KHÔNG nung độ tối vào texture. Texture phải đọc được chi tiết (bản UNLIT: trung vị độ sáng vùng vỏ khoảng 35–55/255). Không khí tối hay lạnh là việc của ánh sáng và bước chỉnh màu cuối (bản LIT: trung vị 15–30, có vùng sáng nhân vật/vật chính, có bóng đổ; sắc lạnh phải đo được qua chênh kênh B−R).
- Vùng phát sáng (đèn, hologram, vật toả sáng) không đi qua node làm tối.
- Script tự đo 12 ô (trung bình, trung vị, B−R) và đưa số vào báo cáo. Lệch ngưỡng thì báo, không tự kết luận "đạt".
- Giới hạn thời gian theo lệnh. Không đè file của vòng trước.
