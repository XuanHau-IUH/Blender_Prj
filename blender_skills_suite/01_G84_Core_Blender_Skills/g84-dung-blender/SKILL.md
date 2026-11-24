---
name: g84-dung-blender
description: Dựng set Blender 5.2 MỘT CHIỀU từ bảng không gian mốc 000, đặt điểm người/máy, đi máy bằng Scenario, xuất sheet, take và depth. Dùng cho sequence dựng bằng Blender (mặc định cho phòng/nội cảnh, ví dụ DANH Seq B).
---
# g84-dung-blender

## Công cụ
- Blender `D:\Blender 5.2\`. Cổng 9876 = blender-mcp (dựng bằng Python). Cổng 9877 = Scenario addon v0.12.0: CHỈ dùng tính năng miễn phí, không dán key, ô "Allow agents to run Python" phải TẮT.
- File Seq B: `E:\G84 - blender\DANH\SeqB\DANH_T01_SEQB.blend` (gốc, chỉ đọc). Bản thử đặt trong `_THU_*`. Take ở `E:\G84\lenh_cuc\danh_seqb\takes\`.
- Gotcha: `transform_apply(scale=True)` sau khi đặt location sẽ reset location. Thứ tự đúng: thêm khối ở vị trí → đặt scale → apply → gán lại `obj.location`.
- Script đang có ở skill `g84-phim-truong-tham-chieu` và `blender-*`: CHƯA chạy thật. Chỉ được dùng hàm nào đã qua một lần chạy thử có nghiệm thu.

## Quy trình
0. Điều kiện: cổng `MAP2D_<LOC>` đã có dòng `TÚ DUYỆT`. Chưa có thì DỪNG.
1. Đọc bảng không gian (`g84-khong-gian`). CẤM sửa tay vị trí trong Blender. Muốn đổi thì sửa bảng rồi dựng lại.
2. Dựng khối đúng `w,d,h`, `xoay_do`, `loai`. Vật `anh_sang_hologram` dựng bằng đèn/emission, không làm khối đặc. Mỗi P_ đặt một Empty, mỗi V_ đặt một Camera.
3. Kiểm ngược: `world_to_camera_view` cho từng V_, đối chiếu vật trong khung với bảng. Kiểm không có vật lơ lửng hoặc xuyên sàn (≤0.05m).
4. Đi máy theo tiền kỳ 14 cột đã duyệt (bảng ánh xạ 14 cột → camera: tiêu cự, khoảng cách, độ cao, nghiêng, camera_path, số khung).
5. Xuất: mặt bằng nhìn từ trên (top-down) có P_/V_ và góc mở máy; sheet 4 khung/cú (Scenario capture_views); khung đầu/cuối + depth; video tham chiếu.
6. Soát bằng qwen3-vl (chạy sau khi nhả GPU), rồi Tú duyệt. Chỉ sau đó mới phủ vỏ (`g84-phu-vo-stablegen`) hoặc tạo ảnh/video.
