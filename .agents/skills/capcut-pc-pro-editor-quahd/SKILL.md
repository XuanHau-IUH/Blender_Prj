---
name: capcut-pc-pro-editor-quahd
description: Kỹ năng dựng video, xử lý hiệu ứng, trộn âm thanh, làm phụ đề, retouch da/dáng và tối ưu xuất file trên CapCut PC theo quy chuẩn Freelance Video Editor của Quạ HD.
---

# CapCut PC Freelance Video Editor Skill (Quạ HD Workflow)

Khi người dùng yêu cầu tư vấn kịch bản dựng phim, hướng dẫn thao tác hiệu ứng, tạo checklist hậu kỳ hoặc tự động hóa quy trình trên CapCut PC, hãy áp dụng nghiêm ngặt các quy tắc và thông số kỹ thuật dưới đây:

## 1. Quy trình 7 Bước Dựng Video Chuẩn (Standard Pipeline)
1. **Setup & Tổ chức File:** Đặt tên thư mục ngoài hệ thống đánh số `01_Footage`, `02_Audio`, `03_Graphics`, `04_Render`. Mở Project và khóa **Ratio** ngay lập tức (`16:9` YouTube, `9:16` TikTok/Reels/Shorts, `1:1` Ads).
2. **Import & Lọc Source:** Đưa toàn bộ media vào tab `Import`, kéo xuống Timeline.
3. **Rough Cut (Dựng thô):**
   - Tắt `Main Track Magnet` để tự do dịch chuyển layer; bật `Auto Snapping` để chống hở frame đen.
   - Bộ phím tắt tốc độ cao (Preset `Set 5` tùy biến):
     - `Q`: Delete Left (Cắt bỏ đầu clip bên trái Playhead).
     - `E`: Delete Right (Cắt bỏ đuôi clip bên phải Playhead).
     - `S`: Split (Cắt đôi tại Playhead).
     - `C` -> Click -> `V` -> `Backspace`: Cắt và xóa nhanh các layer dài vượt khung nhìn.
     - `Backspace` tại vết cắt giữa 2 đoạn liền nhau của cùng 1 clip gốc: Hàn liền lại vết cắt.
   - **Quy tắc cắt sạch Frame:** Dùng phím mũi tên `Trái/Phải` dò từng frame tại điểm chuyển cảnh, nhấn `S` ngay ở frame đầu tiên của cảnh mới.
4. **Transform, Masking & Visual Effects:**
   - **Transform:** Giữ `Ctrl` khi kéo trên màn hình Preview để tắt tự động bắt dính lề (snapping). Giữ `Middle Mouse` để pan khung nhìn khi zoom lớn.
   - **Masking (`Video -> Mask`):**
     - Dùng `Split` ghép bầu trời/chia đôi màn hình; `Rectangle` bo góc làm cam mặt (Facecam); `Pen` vẽ vùng cắt tự do.
     - Luôn tinh chỉnh `Feather` để làm mềm biên cắt và dùng `Invert` khi cần đục thủng vùng chọn nhìn xuyên xuống layer dưới.
   - **Effects & Transitions:**
     - Chồng nhiều lớp `Video Effects` (Layer Stacking) lên phía trên clip để kết hợp hiệu ứng (ví dụ: Shake + Edge Blur).
     - Sử dụng `Body Effects` cho hiệu ứng bám theo chuyển động cơ thể (viền neon, phát sáng mắt, phân thân).
     - `Transitions` chỉ hoạt động khi 2 clip hít sát nhau. Dùng `Animation -> In/Out` cho mở đầu và kết thúc của các clip đơn lẻ.
   - **Speed & Optical Flow:**
     - Khi tua nhanh (>1x) video có lời thoại: Bắt buộc **tắt `Keep pitch` / `Change audio pitch`** để giữ nguyên giọng thật.
     - Khi làm chậm (<1x / Slow-mo) bị giật khung hình: Bắt buộc tích **`Smooth slow-mo` -> `Optical flow`**.
5. **Chuẩn hóa Âm thanh (Audio Mixing Formula):**
   - Tách âm thanh khỏi video bằng `Right-click -> Extract Audio`.
   - **Định mức dB bắt buộc:**
     - **Voiceover / Lời thoại chính:** `-12 dB` đến `-6 dB` (Chuẩn đích: `-6 dB`, tuyệt đối không chạm ngưỡng đỏ 0 dB).
     - **Nhạc nền (khi có giọng nói):** `-30 dB` đến `-15 dB`.
     - **Nhạc chủ đạo (không lời thoại):** `-6 dB`.
     - **Sound Effects (SFX):** Cân chỉnh dưới mức giọng nói bằng cách kéo trực tiếp thanh âm lượng trên thân clip.
   - Luôn kéo 2 chấm `Fade In` và `Fade Out` ở đầu/cuối layer nhạc nền để âm thanh vào/ra mượt mà.
6. **Typography & Phụ đề AI (Auto Captions):**
   - **Text Styling:** Kết hợp `Stroke` + `Background` + `Glow` + `Shadow`. Nhấn `Save Preset` ngay khi tạo được style chuẩn để đồng bộ toàn dự án. Dùng `Animation -> Loop` để tạo chữ chuyển động lặp lại (rung, lắc).
   - **Quy tắc Phụ đề 1 Dòng:** Sau khi chạy `Auto Captions`, bật `Background` màu xám đen dịu (không dùng màu `#000000` đen tuyền). Với các câu dài bị nhảy thành 2 dòng, nhấn `S` cắt đôi layer phụ đề theo nhịp nói và xóa phần thừa để mọi phụ đề chỉ hiển thị **tối đa 1 dòng**.
7. **Retouch (Làm đẹp) & Export tối ưu nền tảng:**
   - **Công thức Retouch Da tự nhiên (`Retouch -> Face`):**
     - Chuyển chế độ sang **`Multiple faces`** (ngay cả khi chỉ có 1 người) để chống lỗi tuột filter khi nhân vật cử động nhanh.
     - Nam giới: `Smooth` = `10 - 20%`, `Sparkling skin` = `0%`, `Even` = `50%`, tăng nhẹ `Brighten` và `Dark circles`.
     - Nữ giới: `Smooth` = `40 - 70%`, `Even` = `50%`, tùy chỉnh `Skin tone` nếu quay ngoại cảnh bị ám màu cây cối/đèn.
   - **Công thức Kéo dài chân (`Retouch -> Body`):** Không dùng `Auto Long Legs` khi nhân vật di chuyển. Chuyển sang **`Manual`**, khoanh vùng từ đầu gối xuống cổ chân và tăng `Strength`.
   - **Công thức Export chống giảm chất lượng:**
     - Dùng phím `I` và `O` giới hạn vùng render trên timeline.
     - Đặt tên file: `YYYYMMDD_TenDuAn_V01.mp4` | Codec: `H.264` | Format: `MP4` | FPS: `30fps` (hoặc theo source).
     - **Quy tắc Độ phân giải:**
       - YouTube (16:9): Source 4K -> Xuất `4K`; Source 1080p -> Xuất `1080p`.
       - TikTok / Reels / Shorts (9:16): Dù source quay 4K dọc (`2160x3840`), **chỉ xuất ở `1080p (Full HD)`** để tránh bị thuật toán nền tảng nén ép gây mờ video.
