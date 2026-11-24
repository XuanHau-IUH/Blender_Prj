"""
build_temple_broken_silence.py — G84 Action Engine Previs Builder (Blender 5.1 / 5.2+)
Dự án: TEMPLE OF BROKEN SILENCE (30 giây / 720 frames @ 24 FPS)
Thực hiện toàn bộ yêu cầu:
  1. World Lock: Chùa đổ nát 14m (Đông-Tây) x 12m (Nam-Bắc) x 7m (Cao), gốc (0,0,0) giữa sàn.
     - Buddha Statue: (0, 5, 0)
     - South Entrance: (0, -6, 0)
     - East Collision Pillar P1: (4.7, 1, 0)
     - West Wooden Altar: (-4.4, 1, 0) -> Nguyên vẹn từ f001..f627, CHỈ VỠ từ f628 khi C va vào.
     - Ánh nắng chiều vàng xuyên mái thủng Đông-Bắc + lớp bụi lơ lửng.
  2. 4 Võ sĩ (W, A, B, C) — hỗ trợ nạp Rig từ 2XKO Characters Collection hoặc Rigify/Articulated Mannequin:
     - W (Nữ chính tay không): xuất phát (0, -2, 0), kết thúc ở trung tâm đối diện cửa Nam.
     - A (Kiếm thẳng): xuất phát (0, 1, 0), bị đánh văng vào cột P1 (4.3, 1.0, 0) ở Beat 2.
     - B (Đao cong): xuất phát (-2.6, -2, 0), bị quét ngã ở trung tâm (-0.9, -1.6, 0) ở Beat 3.
     - C (Kiếm thẳng): xuất phát (2.6, -2, 0), bị đá văng xuyên bàn thờ (-4.4, 1.0, 0) ở Beat 7.
  3. 4 Camera Rigs (CAM_A, CAM_B, CAM_C, CAM_D) khóa theo 8 Beat (35mm & 50mm).
  4. Xuất đủ bộ Deliverables:
     - temple_action_previs.blend
     - temple_action_previs.mp4 (+ 8 clip ngắn beat_01..beat_08.mp4)
     - choreography_timeline.json
     - camera_manifest.json
     - continuity_report.json
     - Reference frames tại toàn bộ 8 ranh giới Beat & các frame va chạm (Contact Events).
"""
import os
import sys
import json
import math
from pathlib import Path

import bpy
import mathutils

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import bx_previs as P
import bx_blockout as B
import bx_anim as A
from bx_review import playblast


# ==============================================================================
# 1. THÔNG SỐ KHÓA THẾ GIỚI (BLENDER WORLD LOCK)
# ==============================================================================

WORLD_LOCK = {
    "temple_size_m": [14.0, 12.0, 7.0],
    "fps": 24,
    "total_frames": 720,
    "duration_sec": 30.0,
    "key_locations_m": {
        "Warrior_W": [0.0, -2.0, 0.0],
        "Swordsman_A": [0.0, 1.0, 0.0],
        "Swordsman_B": [-2.6, -2.0, 0.0],
        "Swordsman_C": [2.6, -2.0, 0.0],
        "P1_Collision_Pillar": [4.7, 1.0, 0.0],
        "Wooden_Altar": [-4.4, 1.0, 0.0],
        "Buddha_Statue": [0.0, 5.0, 0.0],
        "South_Entrance": [0.0, -6.0, 0.0],
    },
}

BEATS_SPEC = [
    {"beat": 1, "name": "THE_STANDOFF",         "time_s": [0, 4],   "frames": [1, 96],    "cam": "CAM_A_Beat1", "lens": 35.0, "move": "push_in"},
    {"beat": 2, "name": "FIRST_CONTACT",        "time_s": [4, 8],   "frames": [97, 192],  "cam": "CAM_B_Beat2", "lens": 35.0, "move": "lateral_track"},
    {"beat": 3, "name": "THE_LOW_ATTACK",       "time_s": [8, 12],  "frames": [193, 288], "cam": "CAM_C_Beat3", "lens": 50.0, "move": "side_profile"},
    {"beat": 4, "name": "THE_FINAL_SWORDSMAN",  "time_s": [12, 16], "frames": [289, 384], "cam": "CAM_B_Beat4", "lens": 50.0, "move": "handheld_medium"},
    {"beat": 5, "name": "QINGGONG_COUNTER",     "time_s": [16, 20], "frames": [385, 480], "cam": "CAM_D_Beat5", "lens": 35.0, "move": "orbit_60deg"},
    {"beat": 6, "name": "REVERSAL",             "time_s": [20, 24], "frames": [481, 576], "cam": "CAM_C_Beat6", "lens": 35.0, "move": "lateral_track_altar"},
    {"beat": 7, "name": "FINAL_IMPACT",         "time_s": [24, 28], "frames": [577, 672], "cam": "CAM_A_Beat7", "lens": 35.0, "move": "low_angle_full_body"},
    {"beat": 8, "name": "THE_SILENCE",          "time_s": [28, 30], "frames": [673, 720], "cam": "CAM_A_Beat8", "lens": 50.0, "move": "slight_push_in"},
]

CONTACT_EVENTS = [
    {"frame": 124, "beat": 2, "event": "W_WRIST_LOCK_A",       "actors": ["W", "A"], "desc": "W khóa cổ tay cầm kiếm của A"},
    {"frame": 134, "beat": 2, "event": "W_PALM_STRIKE_A",      "actors": ["W", "A"], "desc": "W đánh chưởng trúng ngực A"},
    {"frame": 162, "beat": 2, "event": "A_IMPACT_PILLAR_P1",   "actors": ["A", "P1"], "desc": "A văng đập lưng vào cột đá Đông P1 (4.7, 1, 0)"},
    {"frame": 222, "beat": 3, "event": "W_JUMP_EVADE_B",       "actors": ["W", "B"], "desc": "W bật nhảy qua lưỡi đao quét thấp của B"},
    {"frame": 246, "beat": 3, "event": "W_SWEEP_KICK_B",       "actors": ["W", "B"], "desc": "W xoay hông quét trụ làm B ngã giữa sàn"},
    {"frame": 342, "beat": 4, "event": "W_FOREARM_PARRY_C",    "actors": ["W", "C"], "desc": "W gạt cẳng tay và khóa cổ tay kiếm của C ở nhát chém thứ 2"},
    {"frame": 425, "beat": 5, "event": "W_QINGGONG_APEX",      "actors": ["W", "C"], "desc": "W bật khinh công qua vai C, xoay 180 độ trên không"},
    {"frame": 524, "beat": 6, "event": "W_ELBOW_STRIKE_C",     "actors": ["W", "C"], "desc": "W thúc chỏ trúng ngực C đẩy C lùi về phía bàn thờ Tây"},
    {"frame": 604, "beat": 7, "event": "W_SPIN_BACK_KICK_C",   "actors": ["W", "C"], "desc": "W xoay 360 độ tung cú đá hậu trúng ngực C"},
    {"frame": 628, "beat": 7, "event": "C_CRASH_WOODEN_ALTAR", "actors": ["C", "Altar"], "desc": "C đập mạnh vào bàn thờ gỗ phía Tây (-4.4, 1, 0), bàn thờ bắt đầu vỡ"},
]


# ==============================================================================
# 2. DỰNG KIẾN TRÚC NGÔI CHÙA ĐỔ NÁT (14m x 12m x 7m) & BÀN THỜ VỠ CÓ ĐIỀU KIỆN
# ==============================================================================

def build_ruined_temple(sc):
    """Dựng đầy đủ hình học ngôi chùa theo đúng tọa độ khóa World Lock."""
    stone_dark = (0.24, 0.23, 0.21)
    stone_wall = (0.34, 0.32, 0.29)
    pillar_col = (0.42, 0.39, 0.35)
    buddha_gold = (0.62, 0.48, 0.24)
    wood_weathered = (0.38, 0.25, 0.15)
    pottery_col = (0.58, 0.34, 0.22)

    # Sàn đá 14m x 12m tại gốc (0, 0, 0)
    floor = P.prop(sc, "ENV_Temple_Floor", dims=(14.0, 12.0, 0.25), loc=(0.0, 0.0, -0.25), color=stone_dark, kind="box", collection="SET")

    # Tường Bắc (North Wall tại Y = +6.0)
    P.prop(sc, "ENV_Wall_North", dims=(14.0, 0.4, 7.0), loc=(0.0, 6.0, 0.0), color=stone_wall, kind="box", collection="SET")
    # Tường Tây (West Wall tại X = -7.0)
    P.prop(sc, "ENV_Wall_West", dims=(0.4, 12.0, 7.0), loc=(-7.0, 0.0, 0.0), color=stone_wall, kind="box", collection="SET")
    # Tường Đông (East Wall tại X = +7.0)
    P.prop(sc, "ENV_Wall_East", dims=(0.4, 12.0, 7.0), loc=(7.0, 0.0, 0.0), color=stone_wall, kind="box", collection="SET")

    # Cổng Nam (South Entrance tại (0, -6, 0) — mở khoảng trống 4.4m ở giữa)
    P.prop(sc, "ENV_Wall_South_WestWing", dims=(4.8, 0.4, 7.0), loc=(-4.6, -6.0, 0.0), color=stone_wall, kind="box", collection="SET")
    P.prop(sc, "ENV_Wall_South_EastWing", dims=(4.8, 0.4, 7.0), loc=(4.6, -6.0, 0.0), color=stone_wall, kind="box", collection="SET")
    P.prop(sc, "ENV_South_Lintel", dims=(4.6, 0.5, 1.2), loc=(0.0, -6.0, 5.8), color=stone_wall, kind="box", collection="SET")

    # Mái chùa (Cao 7m, thủng một mảng lớn ở góc Đông-Bắc để nắng vàng chiếu xiên xuống)
    P.prop(sc, "ENV_Roof_WestHalf", dims=(7.0, 12.0, 0.35), loc=(-3.5, 0.0, 7.0), color=wood_weathered, kind="box", collection="SET")
    P.prop(sc, "ENV_Roof_SouthEast", dims=(7.0, 5.5, 0.35), loc=(3.5, -3.25, 7.0), color=wood_weathered, kind="box", collection="SET")

    # Tượng Phật lớn phía Bắc tại (0, 5, 0)
    P.prop(sc, "ENV_Buddha_Pedestal", dims=(3.4, 2.2, 1.1), loc=(0.0, 5.0, 0.0), color=pillar_col, kind="box", collection="SET")
    P.prop(sc, "ENV_Buddha_Statue", dims=(2.4, 1.6, 4.2), loc=(0.0, 5.0, 1.1), color=buddha_gold, kind="cylinder", collection="SET")

    # Cột đá va chạm P1 ở phía Đông: (4.7, 1, 0) + các cột đối xứng
    p1 = P.prop(sc, "PROP_P1_East_Pillar", dims=(0.75, 0.75, 7.0), loc=(4.7, 1.0, 0.0), color=pillar_col, kind="cylinder", collection="SET")
    P.prop(sc, "ENV_Pillar_NE", dims=(0.75, 0.75, 7.0), loc=(4.7, 4.0, 0.0), color=pillar_col, kind="cylinder", collection="SET")
    P.prop(sc, "ENV_Pillar_NW", dims=(0.75, 0.75, 7.0), loc=(-4.7, 4.0, 0.0), color=pillar_col, kind="cylinder", collection="SET")
    P.prop(sc, "ENV_Pillar_SW", dims=(0.75, 0.75, 7.0), loc=(-4.7, -3.5, 0.0), color=pillar_col, kind="cylinder", collection="SET")
    P.prop(sc, "ENV_Pillar_SE", dims=(0.75, 0.75, 7.0), loc=(4.7, -3.5, 0.0), color=pillar_col, kind="cylinder", collection="SET")

    # Dầm gỗ rơi & gạch vỡ rải rác ở rìa (không cản đường đánh nhau)
    P.prop(sc, "ENV_Fallen_Beam_01", dims=(2.8, 0.28, 0.28), loc=(3.8, -4.5, 0.0), color=wood_weathered, kind="box", collection="SET", rot_z=28.0)
    P.prop(sc, "ENV_Fallen_Beam_02", dims=(2.4, 0.25, 0.25), loc=(-3.6, 3.6, 0.0), color=wood_weathered, kind="box", collection="SET", rot_z=-18.0)

    # BÀN THỜ GỖ PHÍA TÂY tại (-4.4, 1, 0) — Thiết kế gồm 6 mảnh để VỠ ĐÚNG FRAME 628!
    altar_pieces = []
    piece_specs = [
        # (name, dims, rest_loc, broken_loc, broken_rot_euler_deg)
        ("PROP_Altar_Base",      (1.1, 2.4, 0.55), (-4.4, 1.0, 0.0),   (-4.55, 1.0, 0.0),   (0, -8, 4)),
        ("PROP_Altar_TopSlab",   (1.2, 2.6, 0.14), (-4.4, 1.0, 0.95),  (-5.35, 1.25, 0.08), (65, -35, 28)),
        ("PROP_Altar_Panel_N",   (0.9, 1.1, 0.40), (-4.4, 1.6, 0.55),  (-5.10, 2.15, 0.05), (78, 22, -40)),
        ("PROP_Altar_Panel_S",   (0.9, 1.1, 0.40), (-4.4, 0.4, 0.55),  (-5.20, 0.10, 0.05), (-72, -18, 35)),
        ("PROP_Altar_Pottery_1", (0.28, 0.28, 0.42), (-4.3, 1.4, 1.09), (-5.60, 1.85, 0.02), (88, 45, 60)),
        ("PROP_Altar_Pottery_2", (0.24, 0.24, 0.35), (-4.3, 0.6, 1.09), (-5.50, 0.30, 0.02), (-85, 30, -55)),
    ]
    for pname, pdims, rloc, bloc, brot in piece_specs:
        col = pottery_col if "Pottery" in pname else wood_weathered
        kind = "cylinder" if "Pottery" in pname else "box"
        pobj = P.prop(sc, pname, dims=pdims, loc=rloc, color=col, kind=kind, collection="SET")
        # Khóa nguyên vẹn tuyệt đối từ frame 1 đến frame 627!
        for f in (1, 627):
            pobj.location = rloc
            pobj.rotation_euler = (0.0, 0.0, 0.0)
            pobj.keyframe_insert(data_path="location", frame=f)
            pobj.keyframe_insert(data_path="rotation_euler", frame=f)
        # Chỉ khi C đập vào ở frame 628 -> vỡ tung ra từ 628 đến 652 và nằm yên đến 720
        sc.frame_set(628)
        pobj.location = (rloc[0] - 0.08, rloc[1], rloc[2])
        pobj.keyframe_insert(data_path="location", frame=628)
        for f in (652, 720):
            pobj.location = bloc
            pobj.rotation_euler = tuple(math.radians(a) for a in brot)
            pobj.keyframe_insert(data_path="location", frame=f)
            pobj.keyframe_insert(data_path="rotation_euler", frame=f)
        A.set_interpolation(pobj, interpolation="BEZIER", handle="AUTO_CLAMPED")
        altar_pieces.append(pobj)

    return floor, p1, altar_pieces


def setup_temple_golden_lighting(sc):
    """Ánh nắng chiều vàng xuyên qua mái thủng Đông-Bắc + ánh sáng phản xạ trong chùa."""
    light_coll = P.coll(sc, "LIGHTS")
    target = mathutils.Vector((0.0, -0.5, 1.2))
    specs = [
        # Nắng vàng chiều tà chiếu xiên từ mái thủng Đông-Bắc (+X, +Y, +Z)
        ("LGT_NE_Golden_Shaft", mathutils.Vector((4.2, 3.2, 6.8)), 650.0, (1.0, 0.76, 0.42), 1.8),
        # Ánh sáng trời xanh dịu từ cổng Nam
        ("LGT_South_Door_Fill", mathutils.Vector((0.0, -5.8, 2.8)), 180.0, (0.72, 0.84, 1.0), 3.6),
        # Ánh sáng hắt lên từ mặt sàn đá
        ("LGT_Stone_Bounce",    mathutils.Vector((0.0, 0.0, 0.5)),  95.0,  (0.92, 0.80, 0.65), 5.0),
    ]
    for name, loc, energy, color, size in specs:
        ldata = bpy.data.lights.new(name=name, type='AREA')
        ldata.energy = energy
        ldata.color = color
        ldata.size = size
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        light_coll.objects.link(lobj)
        lobj.location = loc
        lobj.rotation_euler = (target - loc).to_track_quat('-Z', 'Y').to_euler()


# ==============================================================================
# 3. QUÉT KHO NHÂN VẬT 2XKO & TẠO 4 VÕ SĨ CÓ KHỚP (W, A, B, C) + VŨ KHÍ LIỀN TAY
# ==============================================================================

DEFAULT_2XKO_DIR = Path(r"d:\ĐỒ chơi Blender\2XKO Characters Collection\2XKO Characters Collection")

def scan_2xko_collection(collection_dir: Path = DEFAULT_2XKO_DIR):
    """Quét toàn bộ file .blend / .fbx / .gltf trong thư mục 2XKO Characters Collection."""
    if not collection_dir.exists():
        return {"exists": False, "path": str(collection_dir), "files": []}
    found = []
    for ext in ("*.blend", "*.fbx", "*.glb", "*.gltf"):
        for fpath in sorted(collection_dir.rglob(ext)):
            found.append({
                "name": fpath.stem,
                "ext": fpath.suffix.lower(),
                "rel_path": str(fpath.relative_to(collection_dir)),
                "abs_path": str(fpath),
                "size_mb": round(fpath.stat().st_size / (1024 * 1024), 2),
            })
    return {"exists": True, "path": str(collection_dir), "count": len(found), "files": found}


def attach_weapon(sc, fighter_root, weapon_name: str, kind: str = "straight_sword"):
    """Gắn kiếm thẳng hoặc đao cong trực tiếp vào xương cẳng tay/bàn tay phải của kiếm khách."""
    hand_loc = P.hand_point(fighter_root, side="R")
    steel_col = (0.78, 0.80, 0.84) if kind == "straight_sword" else (0.70, 0.72, 0.76)
    dims = (0.04, 0.88, 0.06) if kind == "straight_sword" else (0.05, 0.82, 0.09)
    wpn = P.prop(sc, weapon_name, dims=dims, loc=(0, 0, 0), color=steel_col, kind="box", collection="CAST")

    # Tìm cẳng tay phải của mannequin để parent cứng
    forearm_r = next((c for c in fighter_root.children_recursive if c.name.endswith("_forearm_R")), fighter_root)
    wpn.parent = forearm_r
    wpn.location = (0.0, -0.42, -0.22)
    wpn.rotation_euler = (math.radians(-75.0), 0.0, 0.0)
    return wpn


def create_fighters_and_choreography(sc):
    """Tạo 4 võ sĩ W, A, B, C và đặt toàn bộ Keyframes 8 Beat (720 frames)."""
    # Màu định danh tách biệt rõ ràng cho AI Video & mắt người
    W = P.mannequin(sc, "Warrior_W",   height=1.70, loc=(0.0, -2.0, 0.0), facing=0.0,    color=(0.88, 0.22, 0.20))  # Đỏ son / Trắng ngà
    A_f = P.mannequin(sc, "Swordsman_A", height=1.76, loc=(0.0, 1.0, 0.0),  facing=180.0,  color=(0.55, 0.36, 0.18))  # Nâu sẫm
    B_f = P.mannequin(sc, "Swordsman_B", height=1.74, loc=(-2.6, -2.0, 0.0), facing=90.0,  color=(0.35, 0.42, 0.48))  # Xám than
    C_f = P.mannequin(sc, "Swordsman_C", height=1.82, loc=(2.6, -2.0, 0.0), facing=-90.0,  color=(0.20, 0.52, 0.82))  # Đen xanh

    attach_weapon(sc, A_f, "WPN_Sword_A_Straight", kind="straight_sword")
    attach_weapon(sc, B_f, "WPN_Sword_B_Curved",   kind="curved_sword")
    attach_weapon(sc, C_f, "WPN_Sword_C_Straight", kind="straight_sword")

    chars = {"W": W, "A": A_f, "B": B_f, "C": C_f}

    def kf(actor_key, frame, loc=None, facing=None, **parts):
        sc.frame_set(frame)
        root = chars[actor_key]
        P.pose(root, loc=loc, facing=facing, **parts)
        P.key_block(P.movables(root), frame=frame)

    # ------------------------------------------------------------------
    # BEAT 1 (f001 - f096 | 00-04s): THE STANDOFF
    # ------------------------------------------------------------------
    kf("W", 1,  loc=(0.0, -2.0, 0.0), facing=0.0,   torso=(5, 0, 0), arm_L=(35, 0, -15), forearm_L=(45, 0, 0), arm_R=(25, 0, 15), forearm_R=(55, 0, 0))
    kf("A", 1,  loc=(0.0, 1.0, 0.0),  facing=180.0, arm_R=(40, 0, 10), forearm_R=(35, 0, 0))
    kf("B", 1,  loc=(-2.6, -2.0, 0.0), facing=90.0, arm_R=(30, 0, 15), forearm_R=(40, 0, 0))
    kf("C", 1,  loc=(2.6, -2.0, 0.0), facing=-90.0, arm_R=(35, 0, 10), forearm_R=(30, 0, 0))

    # W hạ trọng tâm, lùi nhẹ chân phải, dựng thủ thế võ thuật; 3 kiếm khách áp sát dần
    kf("W", 48, loc=(0.0, -2.05, -0.06), facing=0.0, torso=(12, 0, -18), thigh_L=(18, 0, 0), shin_L=(-18, 0, 0), thigh_R=(-16, 0, 0), arm_L=(55, 0, -20), forearm_L=(65, 0, 0), arm_R=(40, 0, 20), forearm_R=(70, 0, 0))
    kf("W", 96, loc=(0.0, -2.05, -0.06), facing=0.0, torso=(14, 0, -20), thigh_L=(20, 0, 0), shin_L=(-20, 0, 0), thigh_R=(-18, 0, 0), arm_L=(58, 0, -20), forearm_L=(68, 0, 0), arm_R=(42, 0, 20), forearm_R=(72, 0, 0))
    kf("A", 96, loc=(0.0, 0.2, 0.0),     facing=180.0, torso=(10, 0, 0), arm_R=(55, 0, 20), forearm_R=(40, 0, 0))
    kf("B", 96, loc=(-2.1, -2.0, 0.0),   facing=90.0,  torso=(12, 0, 0), arm_R=(35, 0, 20))
    kf("C", 96, loc=(2.1, -2.0, 0.0),    facing=-90.0, torso=(8, 0, 0),  arm_R=(40, 0, 15))

    # ------------------------------------------------------------------
    # BEAT 2 (f097 - f192 | 04-08s): FIRST CONTACT (A chém ngang -> W khóa cổ tay & đánh chưởng -> A đập vào P1)
    # ------------------------------------------------------------------
    # A lao vào chém ngang
    kf("A", 116, loc=(0.0, -1.15, 0.0), facing=180.0, torso=(18, 0, -35), arm_R=(85, 0, 65), forearm_R=(20, 0, 0), thigh_R=(25, 0, 0))
    # W né sang trái ngoài đường kiếm, khóa cổ tay A (f124)
    kf("W", 124, loc=(-0.38, -1.45, -0.04), facing=45.0, torso=(15, 0, 25), arm_L=(75, 0, -15), forearm_L=(35, 0, 0), arm_R=(30, 0, 25), forearm_R=(85, 0, 0))
    kf("A", 124, loc=(0.12, -1.25, 0.0),    facing=195.0, torso=(22, 0, 30), arm_R=(80, 0, -25), forearm_R=(15, 0, 0))
    # W tung chưởng phải trúng ngực A (f134 — CONTACT_A_PALM)
    kf("W", 134, loc=(-0.15, -1.20, -0.02), facing=65.0, torso=(22, 0, -35), arm_R=(92, 0, 0), forearm_R=(10, 0, 0), arm_L=(45, 0, -30), thigh_R=(28, 0, 0))
    kf("A", 134, loc=(0.35, -1.10, 0.0),    facing=240.0, torso=(-18, 0, 0), head=(-20, 0, 0), arm_R=(45, 0, 35))
    # Hit-stop 2 frames (f136)
    kf("W", 136, loc=(-0.12, -1.18, -0.02), facing=68.0, torso=(24, 0, -38), arm_R=(95, 0, 0), forearm_R=(5, 0, 0))
    kf("A", 136, loc=(0.48, -1.02, 0.05),   facing=245.0, torso=(-25, 0, 0), head=(-25, 0, 0))
    # A văng đập lưng vào cột đá Đông P1 (4.7, 1, 0) tại f162 (CONTACT_A_PILLAR)
    kf("A", 162, loc=(4.25, 0.95, 0.15),    facing=255.0, torso=(-38, 12, 0), head=(25, 0, 0), arm_L=(65, 0, -40), arm_R=(55, 0, 45), thigh_L=(35, 0, 0), thigh_R=(25, 0, 0))
    # A trượt xuống sàn dưới chân cột P1 và nằm bất động đến hết frame 720
    for f_hold in (188, 288, 384, 480, 576, 672, 720):
        kf("A", f_hold, loc=(4.05, 0.85, -0.55), facing=250.0, torso=(-72, 15, 10), head=(30, 0, 15), arm_L=(20, 0, -55), arm_R=(15, 0, 50), thigh_L=(45, 0, -15), shin_L=(-35, 0, 0), thigh_R=(30, 0, 15))
    kf("W", 192, loc=(-0.20, -1.55, -0.04), facing=-45.0, torso=(10, 0, 15), arm_L=(50, 0, -20), arm_R=(45, 0, 20))
    kf("B", 192, loc=(-1.75, -2.0, 0.0),    facing=85.0,  torso=(18, 0, -20), arm_R=(45, 0, 35))
    kf("C", 192, loc=(1.85, -2.0, 0.0),     facing=-90.0)

    # ------------------------------------------------------------------
    # BEAT 3 (f193 - f288 | 08-12s): THE LOW ATTACK (B chém thấp -> W nhảy tránh & quét trụ -> B ngã)
    # ------------------------------------------------------------------
    # B lao vào quét đao tầm thấp (f218)
    kf("B", 218, loc=(-0.75, -1.75, -0.18), facing=75.0, torso=(38, 0, -45), thigh_R=(45, 0, 0), shin_R=(-40, 0, 0), arm_R=(35, 0, -25), forearm_R=(15, 0, 0))
    # W bật nhảy vọt lên tránh lưỡi đao (f222 — CONTACT_EVADE)
    kf("W", 222, loc=(-0.15, -1.55, 0.58),  facing=-75.0, torso=(18, 0, 10), thigh_L=(65, 0, -15), shin_L=(-75, 0, 0), thigh_R=(55, 0, 15), shin_R=(-65, 0, 0), arm_L=(70, 0, -35), arm_R=(65, 0, 35))
    # W đáp chân phải xuống sàn (f234), xoay hông quét chân trái vào chân trụ B (f246 — CONTACT_B_SWEEP)
    kf("W", 234, loc=(-0.10, -1.55, -0.12), facing=-110.0, torso=(25, 0, 35), thigh_R=(35, 0, 0), shin_R=(-35, 0, 0))
    kf("W", 246, loc=(-0.18, -1.58, -0.22), facing=-155.0, torso=(-15, -20, -45), thigh_L=(82, 0, -25), shin_L=(-5, 0, 0), thigh_R=(45, 0, 0), shin_R=(-45, 0, 0), arm_L=(35, 0, -45), arm_R=(45, 0, 45))
    kf("B", 246, loc=(-0.72, -1.68, -0.10), facing=70.0,   torso=(25, -25, 20), thigh_R=(-35, 0, 25), thigh_L=(30, 0, -20))
    # B mất trụ ngã đập xuống sàn đá trung tâm tại f268 và nằm yên đến hết frame 720
    for f_hold in (268, 288, 384, 480, 576, 672, 720):
        kf("B", f_hold, loc=(-0.95, -1.45, -0.68), facing=55.0, torso=(82, 18, -12), head=(15, 0, -20), arm_L=(45, 0, -60), arm_R=(55, 0, 45), thigh_L=(-15, 0, -20), thigh_R=(20, 0, 25))
    kf("W", 288, loc=(-0.05, -1.65, -0.04), facing=90.0, torso=(8, 0, 0), arm_L=(48, 0, -18), forearm_L=(55, 0, 0), arm_R=(38, 0, 18), forearm_R=(60, 0, 0))
    kf("C", 288, loc=(1.55, -1.80, 0.0),    facing=-95.0, torso=(10, 0, 0), arm_R=(50, 0, 15))

    # ------------------------------------------------------------------
    # BEAT 4 (f289 - f384 | 12-16s): THE FINAL SWORDSMAN (C chém 2 nhát liên hoàn -> W lùi 1 bước & gạt cổ tay)
    # ------------------------------------------------------------------
    # C tiến vào chém nhát 1 (f316) -> W lùi 1 bước né
    kf("C", 316, loc=(0.75, -1.72, 0.0),    facing=-95.0, torso=(20, 0, -35), arm_R=(95, 0, 30), forearm_R=(15, 0, 0), thigh_R=(28, 0, 0))
    kf("W", 316, loc=(-0.45, -1.75, -0.05), facing=85.0,  torso=(-12, 0, 20), thigh_L=(-22, 0, 0), thigh_R=(22, 0, 0), arm_L=(60, 0, -25))
    # C bồi tiếp nhát chém 2 (f342 — CONTACT_C_PARRY) -> W áp sát khóa cẳng tay & cổ tay kiếm của C
    kf("C", 342, loc=(0.35, -1.65, 0.0),    facing=-100.0, torso=(22, 0, 28), arm_R=(78, 0, -20), forearm_R=(20, 0, 0), thigh_L=(25, 0, 0))
    kf("W", 342, loc=(-0.15, -1.62, -0.04), facing=82.0,   torso=(16, 0, -25), arm_L=(85, 0, 15), forearm_L=(35, 0, 0), arm_R=(78, 0, -10), forearm_R=(40, 0, 0))
    kf("W", 384, loc=(-0.10, -1.58, -0.08), facing=85.0,   torso=(18, 0, -15), thigh_L=(25, 0, 0), shin_L=(-25, 0, 0), thigh_R=(22, 0, 0), shin_R=(-22, 0, 0))
    kf("C", 384, loc=(0.42, -1.60, 0.0),    facing=-95.0,  torso=(14, 0, 10), arm_R=(65, 0, -10))

    # ------------------------------------------------------------------
    # BEAT 5 (f385 - f480 | 16-20s): QINGGONG COUNTERATTACK (W bật khinh công qua vai C, xoay 180° đáp sau lưng C)
    # ------------------------------------------------------------------
    # W nhún gối lấy đà (f398)
    kf("W", 398, loc=(-0.05, -1.55, -0.18), facing=85.0,  torso=(28, 0, 0), thigh_L=(45, 0, 0), shin_L=(-48, 0, 0), thigh_R=(42, 0, 0), shin_R=(-45, 0, 0), arm_L=(-25, 0, -20), arm_R=(-25, 0, 20))
    # Đỉnh vòm khinh công qua vai C + xoay thân (f425 — W_QINGGONG_APEX)
    kf("W", 425, loc=(0.55, -1.25, 1.38),   facing=0.0,   torso=(15, 12, 0), thigh_L=(55, 0, -10), shin_L=(-50, 0, 0), thigh_R=(25, 0, 10), shin_R=(-35, 0, 0), arm_L=(85, 0, -45), arm_R=(85, 0, 45))
    kf("C", 425, loc=(0.42, -1.55, 0.0),    facing=-75.0, head=(-35, 0, 25), torso=(-8, 0, 15))
    # W tiếp đất sau lưng C, chùng gối hấp thụ lực (f456) và xoay 180° nhìn về phía Tây (-90 deg)
    kf("W", 456, loc=(1.25, -1.15, -0.16),  facing=-95.0, torso=(22, 0, 0), thigh_L=(42, 0, 0), shin_L=(-42, 0, 0), thigh_R=(38, 0, 0), shin_R=(-38, 0, 0), arm_L=(55, 0, -25), arm_R=(45, 0, 25))
    kf("W", 480, loc=(1.20, -1.10, -0.04),  facing=-100.0, torso=(10, 0, 0), arm_L=(52, 0, -18), forearm_L=(55, 0, 0), arm_R=(42, 0, 18), forearm_R=(60, 0, 0))
    kf("C", 480, loc=(0.40, -1.35, 0.0),    facing=65.0,  torso=(12, 0, -20), arm_R=(60, 0, 20))

    # ------------------------------------------------------------------
    # BEAT 6 (f481 - f576 | 20-24s): REVERSAL (C quay lại -> W chặn cổ tay, thúc chỏ đẩy C lùi về phía bàn thờ Tây)
    # ------------------------------------------------------------------
    # C xoay người vung kiếm (f504) -> W bắt tay kiếm và thúc chỏ phải vào ngực C (f524 — CONTACT_C_ELBOW)
    kf("C", 504, loc=(0.35, -1.20, 0.0),    facing=80.0,   torso=(18, 0, -25), arm_R=(90, 0, 25), forearm_R=(25, 0, 0))
    kf("W", 512, loc=(0.75, -1.05, -0.04),  facing=-105.0, arm_L=(82, 0, -10), forearm_L=(25, 0, 0))
    kf("W", 524, loc=(0.45, -0.95, -0.05),  facing=-110.0, torso=(24, 0, -40), arm_R=(85, 0, -25), forearm_R=(110, 0, 0), thigh_R=(32, 0, 0))
    kf("C", 524, loc=(0.05, -0.85, 0.0),    facing=75.0,   torso=(-22, 0, 15), head=(-20, 0, 0), arm_R=(50, 0, 35))
    # C lảo đảo lùi 2 bước về phía bàn thờ Tây (-X, +Y) tới (-1.65, 0.25, 0) tại f568
    kf("C", 548, loc=(-0.85, -0.30, 0.0),   facing=105.0,  torso=(-15, 10, -15), thigh_L=(-25, 0, 0), thigh_R=(28, 0, 0))
    kf("C", 576, loc=(-1.65, 0.25, 0.0),    facing=110.0,  torso=(12, 0, 0), arm_R=(45, 0, 25), thigh_L=(18, 0, 0))
    kf("W", 576, loc=(-0.55, -0.15, -0.04), facing=-70.0,  torso=(12, 0, 15), arm_L=(50, 0, -20), arm_R=(45, 0, 20))

    # ------------------------------------------------------------------
    # BEAT 7 (f577 - f672 | 24-28s): FINAL IMPACT (W xoay người tung cú đá hậu -> C văng vỡ bàn thờ Tây tại f628)
    # ------------------------------------------------------------------
    # W bước trụ và xoay lưng lấy đà (f592)
    kf("W", 592, loc=(-0.95, 0.05, -0.08),  facing=110.0,  torso=(20, 0, 35), thigh_L=(28, 0, 0), shin_L=(-28, 0, 0), thigh_R=(45, 0, 0), shin_R=(-65, 0, 0))
    # W tung cú Spinning Back Kick thẳng vào ngực C (f604 — CONTACT_C_BACKKICK)
    kf("W", 604, loc=(-1.10, 0.12, -0.02),  facing=115.0,  torso=(-28, 15, 0), thigh_R=(-88, 0, 10), shin_R=(0, 0, 0), thigh_L=(18, 0, 0), arm_L=(65, 0, -35), arm_R=(60, 0, 35))
    kf("C", 604, loc=(-1.85, 0.35, 0.02),   facing=112.0,  torso=(-28, 0, 0), head=(-25, 0, 0), arm_L=(55, 0, -40), arm_R=(50, 0, 40))
    # Hit-stop 2 frames (f606)
    kf("W", 606, loc=(-1.10, 0.12, -0.02),  facing=115.0,  torso=(-30, 15, 0), thigh_R=(-90, 0, 10), shin_R=(0, 0, 0))
    kf("C", 606, loc=(-2.05, 0.42, 0.12),   facing=112.0,  torso=(-35, 0, 0))
    # C bay ngược về phía Tây và ĐẬP VÀO BÀN THỜ GỖ (-4.4, 1.0, 0) đúng frame 628 (CONTACT_C_ALTAR)!
    kf("C", 628, loc=(-4.15, 0.95, 0.35),   facing=115.0,  torso=(-48, -12, 10), head=(20, 0, 0), arm_L=(75, 0, -50), arm_R=(70, 0, 50), thigh_L=(40, 0, -15), thigh_R=(35, 0, 15))
    # C ngã gục giữa đống mảnh vỡ bàn thờ từ f656 đến f720
    for f_hold in (656, 672, 720):
        kf("C", f_hold, loc=(-4.55, 1.05, -0.58), facing=120.0, torso=(-78, -15, 12), head=(28, 0, -15), arm_L=(25, 0, -65), arm_R=(20, 0, 55), thigh_L=(35, 0, -20), thigh_R=(25, 0, 20))
    # W thu chân về và lùi nhẹ về chính giữa sàn
    kf("W", 648, loc=(-0.45, -0.45, -0.04), facing=-75.0,  torso=(10, 0, 0), arm_L=(45, 0, -20), arm_R=(40, 0, 20))
    kf("W", 672, loc=(0.0, -1.10, -0.02),   facing=-15.0,  torso=(6, 0, 0),  arm_L=(38, 0, -18), arm_R=(32, 0, 18))

    # ------------------------------------------------------------------
    # BEAT 8 (f673 - f720 | 28-30s): THE SILENCE (W thu thế đứng tĩnh lặng giữa sàn, đối diện cửa Nam)
    # ------------------------------------------------------------------
    kf("W", 696, loc=(0.0, -1.25, 0.0), facing=0.0, torso=(4, 0, 0), arm_L=(28, 0, -14), forearm_L=(35, 0, 0), arm_R=(24, 0, 14), forearm_R=(40, 0, 0))
    kf("W", 720, loc=(0.0, -1.25, 0.0), facing=0.0, torso=(2, 0, 0), arm_L=(22, 0, -12), forearm_L=(28, 0, 0), arm_R=(20, 0, 12), forearm_R=(30, 0, 0))

    # Chuyển toàn bộ keyframe của 4 nhân vật sang nội suy BEZIER AUTO_CLAMPED mượt chuẩn kỹ thuật
    for root in chars.values():
        for m_obj in P.movables(root):
            A.set_interpolation(m_obj, interpolation="BEZIER", handle="AUTO_CLAMPED")

    return chars


# ==============================================================================
# 4. THIẾT LẬP 4 CAMERA RIGS THEO 8 BEAT (35mm & 50mm + TIMELINE MARKERS)
# ==============================================================================

def setup_action_cameras(sc):
    """Dựng hệ thống Camera khóa vào từng Beat và gắn Timeline Markers."""
    cam_coll = P.coll(sc, "CAMERAS")
    sc.timeline_markers.clear()

    cam_specs = [
        # (beat, name, lens, f_start, f_end, loc_start, loc_end, target_start, target_end, handheld_amp)
        (1, "CAM_A_Beat1", 35.0, 1,   96,  (0.0, -5.8, 1.55),  (0.0, -4.4, 1.48),  (0.0, -0.8, 1.15), (0.0, -1.2, 1.10), 0.004),
        (2, "CAM_B_Beat2", 35.0, 97,  192, (-0.5, -4.2, 1.45), (2.4, -3.6, 1.45),  (0.0, -1.2, 1.15), (3.6, 0.6, 1.05),  0.007),
        (3, "CAM_C_Beat3", 50.0, 193, 288, (-0.4, -5.0, 1.25), (-0.4, -4.8, 1.20), (-0.6, -1.6, 1.05), (-0.5, -1.6, 0.90), 0.005),
        (4, "CAM_B_Beat4", 50.0, 289, 384, (0.2, -4.4, 1.45),  (0.1, -4.1, 1.45),  (0.2, -1.6, 1.20), (0.15, -1.6, 1.18), 0.009),
        (5, "CAM_D_Beat5", 35.0, 385, 480, (-1.8, -4.2, 1.50), (2.2, -3.8, 1.65),  (0.5, -1.4, 1.35), (0.8, -1.2, 1.15), 0.006),
        (6, "CAM_C_Beat6", 35.0, 481, 576, (1.2, -4.2, 1.40),  (-0.8, -3.6, 1.38), (0.4, -1.0, 1.15), (-1.8, 0.2, 1.10), 0.007),
        (7, "CAM_A_Beat7", 35.0, 577, 672, (-1.8, -3.5, 0.95), (-2.2, -3.2, 0.98), (-1.8, 0.4, 1.05), (-3.8, 0.9, 0.95), 0.008),
        (8, "CAM_A_Beat8", 50.0, 673, 720, (0.0, -4.4, 1.38),  (0.0, -3.6, 1.42),  (0.0, -1.2, 1.18), (0.0, -1.25, 1.22), 0.003),
    ]

    manifest = []
    for beat_idx, cname, lens, fs, fe, l0, l1, t0, t1, hh in cam_specs:
        cdata = bpy.data.cameras.new(name=cname)
        cdata.sensor_fit = 'HORIZONTAL'
        cdata.sensor_width = 36.0
        cdata.lens = lens
        cdata.passepartout_alpha = 0.9

        cobj = bpy.data.objects.new(name=cname, object_data=cdata)
        cam_coll.objects.link(cobj)

        for frame, loc, tgt in [(fs, l0, t0), (fe, l1, t1)]:
            sc.frame_set(frame)
            cobj.location = loc
            direction = mathutils.Vector(tgt) - mathutils.Vector(loc)
            cobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            cobj.keyframe_insert(data_path="location", frame=frame)
            cobj.keyframe_insert(data_path="rotation_euler", frame=frame)

        A.set_interpolation(cobj, interpolation="BEZIER", handle="AUTO_CLAMPED")
        if hh > 0:
            P.handheld(cobj, strength=hh, scale=22.0)

        # Bind Camera vào Timeline Marker tại đầu mỗi Beat
        m = sc.timeline_markers.new(name=f"B{beat_idx:02d}_{cname}", frame=fs)
        m.camera = cobj

        manifest.append({
            "beat": beat_idx,
            "camera_name": cname,
            "lens_mm": lens,
            "frame_start": fs,
            "frame_end": fe,
            "location_start_m": list(l0),
            "location_end_m": list(l1),
            "look_target_start_m": list(t0),
            "look_target_end_m": list(t1),
        })

    # Thêm các Event Markers cho 10 điểm va chạm (Contact Events)
    for ev in CONTACT_EVENTS:
        sc.timeline_markers.new(name=f"HIT_{ev['event']}", frame=ev["frame"])

    sc.camera = bpy.data.objects["CAM_A_Beat1"]
    return manifest


# ==============================================================================
# 5. KIỂM ĐỊNH TOÁN HỌC & XUẤT BỘ DELIVERABLES CHUẨN SEEDANCE / G84
# ==============================================================================

def run_continuity_validation(sc, chars: dict, p1_obj, altar_pieces: list):
    """Kiểm chứng không dịch chuyển tức thời, khoảng cách va chạm, bàn thờ vỡ đúng lúc."""
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # 1. Kiểm tra không dịch chuyển tức thời (Max step distance giữa 2 frame liên tiếp)
    max_step = {}
    prev_pos = {}
    for k in chars:
        max_step[k] = 0.0

    for f in range(1, 721):
        sc.frame_set(f)
        for k, obj in chars.items():
            pos = obj.matrix_world.translation.copy()
            if k in prev_pos:
                step_d = (pos - prev_pos[k]).length
                if step_d > max_step[k]:
                    max_step[k] = round(step_d, 4)
            prev_pos[k] = pos

    # 2. Kiểm tra khoảng cách thực tế tại 10 Contact Events
    contact_checks = []
    for ev in CONTACT_EVENTS:
        sc.frame_set(ev["frame"])
        a1_key, a2_key = ev["actors"]
        obj1 = chars[a1_key]
        if a2_key in chars:
            obj2 = chars[a2_key]
        elif a2_key == "P1":
            obj2 = p1_obj
        else:
            obj2 = altar_pieces[0]
        dist_xy = (mathutils.Vector(obj1.location[:2]) - mathutils.Vector(obj2.location[:2])).length
        contact_checks.append({
            "frame": ev["frame"],
            "event": ev["event"],
            "actors": ev["actors"],
            "xy_distance_m": round(dist_xy, 3),
            "valid_contact": dist_xy <= 1.35,
        })

    # 3. Kiểm tra bàn thờ gỗ giữ nguyên vẹn trước frame 628 và chỉ vỡ sau frame 628
    sc.frame_set(627)
    slab = altar_pieces[1]
    intact_before_628 = (mathutils.Vector(slab.location) - mathutils.Vector((-4.4, 1.0, 0.95))).length < 0.01
    sc.frame_set(660)
    broken_after_628 = (mathutils.Vector(slab.location) - mathutils.Vector((-4.4, 1.0, 0.95))).length > 0.5

    # 4. Trạng thái cuối ở frame 720
    sc.frame_set(720)
    final_states = {
        k: {
            "location_m": [round(v, 3) for v in obj.location],
            "facing_deg": round(math.degrees(obj.rotation_euler.z), 1),
        }
        for k, obj in chars.items()
    }

    return {
        "total_frames_checked": 720,
        "no_teleportation_passed": all(v < 0.45 for v in max_step.values()),
        "max_per_frame_step_m": max_step,
        "fighter_count_locked": len(chars) == 4,
        "altar_intact_until_frame_627": intact_before_628,
        "altar_shattered_after_frame_628": broken_after_628,
        "contact_events_verification": contact_checks,
        "final_frame_720_states": final_states,
    }


def render_reference_frames_and_videos(sc, out_dir: Path, render_video: bool = True):
    """Xuất ảnh Reference ở tất cả ranh giới 8 Beat + 10 Contact Frames + Video Playblast."""
    ref_dir = out_dir / "reference_frames"
    ref_dir.mkdir(parents=True, exist_ok=True)

    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'MATERIAL'
    sc.display.shading.show_shadows = True
    sc.display.shading.show_cavity = True

    rendered_frames = []
    # Xuất Start & End của cả 8 Beat
    for b in BEATS_SPEC:
        for tag, f in [("START", b["frames"][0]), ("END", b["frames"][1])]:
            sc.frame_set(f)
            fp = ref_dir / f"Beat{b['beat']:02d}_{b['name']}_{tag}_f{f:04d}.png"
            sc.render.filepath = str(fp)
            bpy.ops.render.render(write_still=True)
            rendered_frames.append(str(fp))

    # Xuất 10 Contact Frames
    for ev in CONTACT_EVENTS:
        f = ev["frame"]
        sc.frame_set(f)
        fp = ref_dir / f"Contact_f{f:04d}_{ev['event']}.png"
        sc.render.filepath = str(fp)
        bpy.ops.render.render(write_still=True)
        rendered_frames.append(str(fp))

    # Xuất Video Previs 30 giây (720 frames) + 8 đoạn clip ngắn theo từng Beat cho Seedance
    mp4_path = out_dir / "temple_action_previs.mp4"
    beat_clips = []
    if render_video:
        sc.frame_start = 1
        sc.frame_end = 720
        sc.frame_set(1)
        playblast(str(mp4_path), scene=sc, res_pct=100, color_type="MATERIAL")

        beats_dir = out_dir / "beat_clips"
        beats_dir.mkdir(parents=True, exist_ok=True)
        for b in BEATS_SPEC:
            b_start, b_end = b["frames"]
            sc.frame_start = b_start
            sc.frame_end = b_end
            sc.frame_set(b_start)
            b_mp4 = beats_dir / f"Beat{b['beat']:02d}_{b['name']}_f{b_start:04d}-{b_end:04d}.mp4"
            playblast(str(b_mp4), scene=sc, res_pct=100, color_type="MATERIAL")
            beat_clips.append(str(b_mp4))
        sc.frame_start = 1
        sc.frame_end = 720

    return rendered_frames, str(mp4_path), beat_clips


def build_temple_action_project(out_dir: Path, render_video: bool = True):
    out_dir.mkdir(parents=True, exist_ok=True)
    sc = P.setup_scene("Temple_Of_Broken_Silence", res=(1280, 720), fps=24, pct=100)
    sc.frame_start = 1
    sc.frame_end = 720

    floor, p1_obj, altar_pieces = build_ruined_temple(sc)
    setup_temple_golden_lighting(sc)
    chars = create_fighters_and_choreography(sc)
    cam_manifest = setup_action_cameras(sc)

    # Kiểm định tính liên tục hình học + Quét kho nhân vật 2XKO
    continuity_rep = run_continuity_validation(sc, chars, p1_obj, altar_pieces)
    continuity_rep["authorized_2xko_collection"] = scan_2xko_collection()

    # Lưu file .blend chính
    blend_path = out_dir / "temple_action_previs.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    # Ghi 3 file JSON chuẩn
    (out_dir / "choreography_timeline.json").write_text(
        json.dumps({"world_lock": WORLD_LOCK, "beats": BEATS_SPEC, "contact_events": CONTACT_EVENTS}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    (out_dir / "camera_manifest.json").write_text(
        json.dumps({"cameras": cam_manifest}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    (out_dir / "continuity_report.json").write_text(
        json.dumps(continuity_rep, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    ref_frames, mp4_path, beat_clips = render_reference_frames_and_videos(sc, out_dir, render_video=render_video)
    print(f"[G84 Action Engine] Hoàn tất tại: {out_dir}")
    return {
        "blend": str(blend_path),
        "mp4": mp4_path,
        "beat_clips": beat_clips,
        "reference_frames_count": len(ref_frames),
        "continuity_report": continuity_rep,
    }


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out_folder = Path(argv[0]) if argv else Path(r"E:\G84 - blender\TEMPLE_ACTION_PREVIS")
    build_temple_action_project(out_folder, render_video=True)
