---
name: g84-kho-blender
description: Bản đồ chọn skill trong kho 224 skill Blender (D:\ĐỒ chơi Blender\KHO_SKILL_BLENDER) theo từng bước quy trình G84. Đọc skill này TRƯỚC mọi việc Blender; mỗi bước chỉ mở tối đa 2 skill được chỉ định, không lục cả kho.
---
# g84-kho-blender — Mỗi bước 1–2 skill, không lục cả kho

Kho gốc (chỉ đọc): `D:\ĐỒ chơi Blender\KHO_SKILL_BLENDER\` + `skill_catalog.json`. Ưu tiên bộ 01 (G84). Bộ khác chỉ đọc khi bảng dưới chỉ tới.
Luật chung: script nào CHƯA có lần chạy thử được nghiệm thu thì chạy trên bản sao `_THU_*`, ghi kết quả, không chạy trên file gốc.

| Bước G84 | Skill chính | Đọc thêm khi cần |
|---|---|---|
| 1. Bảng không gian mốc 000 (địa điểm, vật, P_, V_) | 01/g84-khong-gian | — |
| 2. Dựng set một chiều từ bảng | 01/g84-dung-blender | 03 EL4CTEO (API Blender 5.2), 05/blender-geometry-validation (soát hình) |
| 3. Đạo cụ canon từ sheet nhiều góc (trống đồng, đỉnh, sáo…) | 06 CC Reference (dựng khớp bản vẽ 4 góc) | 05/blender-reference-reconstruction |
| 4. Đại cảnh, rải quân đông, cây cối, phố | 05/blender-geometry-nodes-studio | 05/blender-procedural-systems, 01/blender-gis (đô thị/địa hình) |
| 5. Phủ vỏ texture | 01/g84-phu-vo-stablegen | 08/polyhaven-texture-apply (vật liệu CC0 khi không cần AI) |
| 6. Ánh sáng theo canon | 01/blender-lighting | 05/blender-lighting-analysis |
| 7. Đặt máy, đi máy, cỡ cảnh | 01/blender-camera | 02/motion-prompt (tên gọi chuyển động), 08 crane/dolly/slow-zoom (mẫu đường máy) |
| 8. Nhân vật có khớp, diễn | 01/blender-rigify | 01/blender-animation-52 |
| 9. Soát kết quả bằng mắt máy | 02/dream-loop (so render với ảnh mục tiêu) | 04 bx_review |
| 10. Xuất GLB cho Motion Previs Studio | 08/threejs-export | — |
| Phong cách, mood (tham khảo) | 10 Arjun988 — chỉ references, không nạp cả bộ | — |

KHÔNG dùng: phần gọi dịch vụ mây trả phí trong bộ 04 (Meshy, Rodin, Sparc3D, Patina, Video-to-Motion), 07 (ví dụ phim xe/drone — chỉ tham khảo), 09 (anime).
