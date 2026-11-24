---
name: g84-khong-gian
description: Bảng không gian mốc 000 — khung dữ liệu DUY NHẤT cho địa điểm, vật, điểm người P_, điểm máy V_ mà cả Blender lẫn Unity 6 cùng đọc. Dùng khi tạo, sửa hoặc kiểm hồ sơ không gian của một địa điểm.
---
# g84-khong-gian — Một bảng, hai bên thi công

## Nguồn
- Khuôn gốc: Dify W-C nút B1/B2 (`g84_wc_extract_canon_dsl.yml`) + `E:\G84\lenh_cuc\QUY_TRINH_KHONG_GIAN_MOC000.md`. Bảng đã duyệt được lưu trong app (Canon Location qua Core API).
- `danh_khong_gian\*.json` chỉ là nguồn tạm của DANH. Khi DANH mở khoá thì chuyển vào app theo khuôn này, sau đó không sửa JSON tạm nữa.
- CẤM đẻ định dạng thứ ba (`WorldSpec.yaml`, `stage_spec.json`…). Thiếu trường thì thêm vào bảng này.

## Trường của mỗi địa điểm
`code LOC_…`, `dimensionsM {widthM, depthM, heightM}`, `quy_mo: phong | map_lon`, `anchoredObjectsLayout[]`, `viewInventories` (9 góc), `stateVariants`, `diem_nguoi[]`, `diem_may[]`.
- Mỗi vật: `propCode`, `loai: kien_truc | dao_cu | bay_tri | anh_sang_hologram | nhan_vat_diem`, `x,y,z` (tâm đáy), `w,d,h`, `xoay_do` (0 = mặt hướng Bắc), `nhan_texture`, `nguon` (`ho_so | giai_bang_code | CHUA_RO`).
- `diem_nguoi`: `P_<LOC>_<TÊN>`, x,y,z, `huong_mat_do`. `diem_may`: `V_<LOC>_<TÊN>`, x,y,z, `nhin_toi`, `tieu_cu_mm`. Mỗi địa điểm có ít nhất 1 GÓC ĐẶC BIỆT (qua khe cửa, bám sau lưng, rất thấp, trên cao).

## Hai quy mô (luật toạ độ, Tú duyệt 05/11)
- `phong` (Tầng 52, B3, Hẻm Vít…): số lấy từ hồ sơ đã đo. Văn bản không có số thì ghi `CHUA_RO`, rồi chuyển Tú điền hoặc cho bộ giải tính.
- `map_lon` (map Bễ…): LLM chỉ được ghi quan hệ (`relative_to`, `bearing`, `distance_m`, `along_path`, `snap`). Bộ giải bằng code tính ra x,y,z rồi ghi ngược lại vào bảng với `nguon: giai_bang_code`.

## Kiểm (script)
- Mọi số đều có `nguon`. Toạ độ nằm trong hộp của địa điểm. Mọi P_ và V_ thuộc một LOC có thật. Mỗi địa điểm có ≥1 góc đặc biệt. Không có từ quan hệ trong `description` của `phong`.
- Tiền kỳ 14 cột (L02) chỉ TRỎ tới điểm (`NV_X @ P_…`, máy `V_…`), không ghi toạ độ mới.

## CỔNG MAP 2D — BẮT BUỘC ĐẦU TIÊN (Tú chốt 06/11)
Chưa có map 2D được Tú duyệt thì KHÔNG dựng 2.5D hay 3D (Blender, Unity) và KHÔNG tạo ảnh không gian.
- Map do CODE vẽ thẳng từ bảng không gian (`E:\G84\lenh_cuc\tools\ve_map2d.py --loc <LOC> [--seq <SEQ>]`). KHÔNG dùng AI tạo ảnh. Muốn sửa map thì sửa bảng rồi vẽ lại.
- Trên map bắt buộc có:
  1. Lưới mét; mốc (0,0,0) ở góc Tây-Nam; mũi tên chỉ Bắc; thước tỉ lệ.
  2. Tường, cửa, lối vào/ra, cầu thang/thang máy.
  3. Vật cố định và đạo cụ kèm mã (`PROP_`/`DC_`) và kích thước.
  4. Điểm người `P_` có mũi tên hướng mặt.
  5. Điểm máy `V_` có hình nón góc nhìn theo tiêu cự; góc đặc biệt tô màu riêng.
  6. Đường di chuyển của nhân vật theo các cảnh của sequence (khi có `--seq`).
  7. Hướng ánh sáng chính.
  8. Mọi con số `CHUA_RO` (và `ho_so_tam`) in MÀU ĐỎ, kèm bảng liệt kê cạnh map.
- Xuất `map2d\<LOC>_MAP2D_vN.png` (+ `.svg`). Tạo cổng `MAP2D_<LOC>` (`g84-nghiem-thu`). Có duyệt rồi mới sang `g84-dung-blender` / `g84-dung-unity6`.
- Thứ tự: bảng → MAP 2D (Tú duyệt) → 2.5D/3D blockout → đi máy → phủ vỏ → ảnh/video.
