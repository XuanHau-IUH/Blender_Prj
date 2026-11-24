# G84 ACTION PRODUCTION ARCHITECTURE (Chuẩn Biên Đạo Võ Thuật 3D → AI Video / Seedance)

> **Nguyên lý cốt lõi của Showrunner Gate 84:**
> - **Blender nắm 100% quyền quyết định về không gian và biên đạo chuyển động** (vị trí nhân vật, hướng di chuyển, thời điểm tiếp xúc đòn đánh, phá hủy môi trường có điều kiện, góc máy).
> - **AI Video (Seedance / LTX-2.5 / Wan / MiniMax H3) KHÔNG ĐƯỢC tự sáng tác lại** vị trí nhân vật, hướng di chuyển hay diễn biến trận đánh; AI chỉ chịu trách nhiệm phủ ngoại hình, chất liệu, ánh sáng, khí quyển và độ chi tiết thực tế lên bộ khung previs của Blender.
> - **Chiến lược Chia Để Trị (8 Clip × 4 Giây = 30 Giây):** Dựng liền mạch 30 giây (`720 frames @ 24fps`) trong 1 file Blender duy nhất để khóa chặt tính liên tục không gian (World Lock), nhưng **xuất thành 8 đoạn clip ngắn theo từng Beat** kèm Start/End Frame và trạng thái nối tiếp để AI Video không bị trôi nhân vật hay biến dạng bối cảnh.

---

## 1. Luật Biên Đạo Động Tác Thực Chiến Trong Blender 5.2

1. **Đầy đủ 5 pha mỗi đòn đánh:**
   - **Pha 1 — Chuyển trọng tâm & Chuẩn bị (Preparation / Weight Transfer):** Hạ hông (`pelvis`/`torso` Z giảm 5–12cm), xoay vai/hông lấy đà trước khi ra đòn (tối thiểu 4–6 frames).
   - **Pha 2 — Quỹ đạo đòn đánh (Trajectory):** Đường cong vòng cung rõ ràng (kiểm tra bằng `bx_anim.onion_skin` và `motion_path`), không đi đường thẳng băng máy móc.
   - **Pha 3 — Điểm tiếp xúc (Contact Frame & Hit-Stop):** Khoảng cách giữa chân/tay người đánh và ngực/cổ tay người trúng đòn tại `Contact Frame` phải `<= 0.35m`; giữ `Moving Hold` 2–3 frames tại điểm va chạm để tạo lực (`Hit-Stop`).
   - **Pha 4 — Phản ứng trúng đòn (Opponent Reaction):** Ngay sau frame tiếp xúc, đối thủ gập ngực/ngửa cổ và văng lùi theo đúng vector lực của đòn đánh (ví dụ: A văng về cột đá Đông `P1 (4.7, 1, 0)`; C văng về bàn thờ Tây `Altar (-4.4, 1, 0)`).
   - **Pha 5 — Điểm dừng vật lý (Physical Endpoint & Ground Lock):** Đối thủ bị hạ phải nằm yên tại tọa độ rơi cho đến hết frame 720 (`holds` khóa chặt `AUTO_CLAMPED`), tuyệt đối không trôi hay tự đứng dậy.
2. **Khinh công có kiểm soát (Controlled Wire-Fu):**
   - Nhún chân lấy đà rõ ràng (`knee bend` + hạ trọng tâm 6 frames) → quỹ đạo parabol hợp lý (`bx_anim.ballistic_fit`) + xoay thân 180° trên không → tiếp đất chùng gối hấp thụ xung lực (`landing compression` 5–8 frames).
3. **Vũ khí gắn liền tay (Continuous Weapon Ownership):**
   - Kiếm của A, B, C phải gắn chặt vào xương tay phải (`hand.R` / `hand_ik.R`) qua `Child Of` hoặc `Bone Parent`, mũi kiếm hướng theo đòn chém ngang/chém thấp/chém đôi liên hoàn.
