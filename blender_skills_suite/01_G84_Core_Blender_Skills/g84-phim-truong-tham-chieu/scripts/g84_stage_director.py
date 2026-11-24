"""
g84_stage_director.py — Bộ máy Dựng Phim Trường Nhỏ, Diễn Xuất Nhân Vật Rig & Xuất Video Tham Chiếu Đa Kênh (Blender 5.1 / 5.2+)
Dành riêng cho Showrunner Gate 84 (Cúc vận hành).

Cách chạy Headless từ dòng lệnh:
    blender -b -P g84_stage_director.py -- --spec path/to/stage_spec.json --out path/to/output_dir
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

# Nạp các thư viện chuyên sâu Blender 5.2 đã tích hợp
try:
    import bx_previs as P
    import bx_blockout as B
    import bx_kits as K
    import bx_anim as A
    import bx_rig as R
except ImportError as exc:
    print(f"[G84 Stage Director] Cảnh báo nạp thư viện bx_*: {exc}")
    P = B = K = A = R = None


# ==============================================================================
# 1. CẤU HÌNH ACTION SLOTTED BLENDER 5.0 - 5.2+ & CHUYỂN ĐỘNG MỀM CHUẨN KỸ THUẬT
# ==============================================================================

def get_or_create_fcurve_52(id_block, data_path: str, index: int = 0, action_name: str = None):
    """Tương thích cả Blender 5.2 (Slotted Actions / channelbag) và Blender 4.x/5.0."""
    if not id_block.animation_data:
        id_block.animation_data_create()
    act = id_block.animation_data.action
    if not act:
        act = bpy.data.actions.new(name=action_name or f"ACT_{id_block.name}")
        id_block.animation_data.action = act

    # Blender 5.2+ Slotted Action API
    if A is not None and hasattr(A, "channelbag"):
        cb = A.channelbag(id_block, create=True)
        if cb is not None:
            fc = cb.fcurves.find(data_path, index=index)
            if fc is None:
                fc = cb.fcurves.new(data_path, index=index)
            return fc

    # Fallback cho API cũ hoặc truy cập trực tiếp
    if hasattr(act, "fcurves"):
        fc = act.fcurves.find(data_path, index=index)
        if fc is None:
            fc = act.fcurves.new(data_path, index=index)
        return fc
    raise RuntimeError(f"Không thể tạo FCurve cho {id_block.name}:{data_path}[{index}]")


def apply_smooth_bezier_clamped(id_block, bones=None):
    """
    Ép toàn bộ keyframe sang nội suy BEZIER với tay nắm AUTO_CLAMPED
    để tạo gia tốc Ease-In / Ease-Out mềm mại, chống trượt lố (overshoot) và chống giật robot.
    """
    if A is not None:
        A.set_interpolation(id_block, interpolation="BEZIER", handle="AUTO_CLAMPED", bones=bones)
        return

    if not id_block.animation_data or not id_block.animation_data.action:
        return
    act = id_block.animation_data.action
    fcurves = getattr(act, "fcurves", [])
    for fc in fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()


def add_breathing_and_idle_micro_motion(rig_obj, frame_start: int, frame_end: int, fps: int = 24,
                                        breath_period_sec: float = 3.6, amp_deg: float = 1.4):
    """
    Thêm nhịp thở sinh học (ngực/vai nhấp nhô nhẹ + lắc trọng tâm cực nhỏ) cho nhân vật
    để khi nhân vật đứng nghe hoặc thoại không bị đơ cứng như tượng gỗ.
    """
    if not rig_obj or rig_obj.type != 'ARMATURE':
        return
    pbones = rig_obj.pose.bones
    # Hỗ trợ cả tên xương Rigify (spine_fk.002 / chest / torso) và Mannequin
    chest_candidates = ["chest", "spine_fk.002", "spine_fk.001", "spine.002", "spine.001", "upper_body"]
    chest_bone = next((pbones[n] for n in chest_candidates if n in pbones), None)
    if not chest_bone:
        return

    chest_bone.rotation_mode = 'XYZ'
    step = max(4, int(round(fps * breath_period_sec / 4.0)))
    for f in range(frame_start, frame_end + 1, step):
        phase = ((f - frame_start) / float(fps * breath_period_sec)) * (2.0 * math.pi)
        pitch_rad = math.radians(amp_deg * math.sin(phase))
        roll_rad = math.radians(amp_deg * 0.35 * math.cos(phase * 0.5))
        chest_bone.rotation_euler[0] += pitch_rad
        chest_bone.rotation_euler[2] += roll_rad
        chest_bone.keyframe_insert(data_path="rotation_euler", frame=f)

    apply_smooth_bezier_clamped(rig_obj, bones=[chest_bone.name])


def add_head_look_at_constraint(rig_obj, target_obj, head_influence: float = 0.65, neck_influence: float = 0.35):
    """
    Gắn Damped Track cho cổ (35%) và đầu (65%) nhìn về phía đối tượng (nhân vật khác hoặc đạo cụ)
    giúp ánh nhìn tự nhiên, không bị gãy cổ.
    """
    if not rig_obj or rig_obj.type != 'ARMATURE' or not target_obj:
        return
    pbones = rig_obj.pose.bones
    neck_bone = next((pbones[n] for n in ["neck", "spine.004", "spine_fk.003"] if n in pbones), None)
    head_bone = next((pbones[n] for n in ["head", "spine.006", "head_fk"] if n in pbones), None)

    for pbone, inf in [(neck_bone, neck_influence), (head_bone, head_influence)]:
        if pbone is None:
            continue
        con = pbone.constraints.new(type='DAMPED_TRACK')
        con.name = f"G84_LookAt_{target_obj.name}"
        con.target = target_obj
        con.track_axis = 'TRACK_NEGATIVE_Y'
        con.influence = inf


# ==============================================================================
# 2. DỰNG PHIM TRƯỜNG NHỎ (WORLD & PROPS) & SNAP MẶT ĐẤT
# ==============================================================================

def snap_to_ground_raycast(obj, ground_obj, sink_offset: float = -0.005):
    """Bắn tia Raycast đặt chân đạo cụ/nhân vật bám khít mặt sàn."""
    if not obj or not ground_obj:
        return
    depsgraph = bpy.context.evaluated_depsgraph_get()
    ground_eval = ground_obj.evaluated_get(depsgraph)
    inv_mat = ground_eval.matrix_world.inverted()

    world_origin = mathutils.Vector((obj.location.x, obj.location.y, 500.0))
    local_origin = inv_mat @ world_origin
    local_dir = (inv_mat.to_3x3() @ mathutils.Vector((0.0, 0.0, -1.0))).normalized()
    hit, loc, _, _ = ground_eval.ray_cast(local_origin, local_dir)
    if hit:
        world_hit = ground_eval.matrix_world @ loc
        obj.location.z = world_hit.z + sink_offset


def build_stage_shell(sc, world_spec: dict):
    """
    Tạo khung phim trường nhỏ (Sàn + Tường L/U-shape hoặc Hẻm 2 vách)
    với tường có thể ẩn đối với tia Camera (Camera Ray Visibility) khi quay góc hẹp.
    """
    width = float(world_spec.get("width_m", 8.0))
    depth = float(world_spec.get("depth_m", 10.0))
    height = float(world_spec.get("height_m", 3.6))
    stage_type = world_spec.get("stage_type", "room_l_shape")  # room_l_shape | alley | open_floor
    floor_color = tuple(world_spec.get("floor_color", (0.22, 0.22, 0.24)))
    wall_color = tuple(world_spec.get("wall_color", (0.45, 0.43, 0.40)))

    floor = P.prop(
        sc,
        name="STAGE_Floor",
        dims=(width, depth, 0.15),
        loc=(0.0, 0.0, -0.15),
        color=floor_color,
        kind="box",
        collection="SET",
    )

    walls = []
    if stage_type in ("room_l_shape", "room_u_shape"):
        # Tường hậu (Back wall ở +Y)
        w_back = P.prop(
            sc, "STAGE_Wall_Back",
            dims=(width, 0.2, height),
            loc=(0.0, depth * 0.5, 0.0),
            color=wall_color, kind="box", collection="SET"
        )
        # Tường trái (Left wall ở -X)
        w_left = P.prop(
            sc, "STAGE_Wall_Left",
            dims=(0.2, depth, height),
            loc=(-width * 0.5, 0.0, 0.0),
            color=wall_color, kind="box", collection="SET"
        )
        walls.extend([w_back, w_left])
        if stage_type == "room_u_shape":
            w_right = P.prop(
                sc, "STAGE_Wall_Right",
                dims=(0.2, depth, height),
                loc=(width * 0.5, 0.0, 0.0),
                color=wall_color, kind="box", collection="SET"
            )
            walls.append(w_right)
    elif stage_type == "alley":
        # Hẻm 2 vách trái/phải chạy dọc trục Y
        w_left = P.prop(
            sc, "STAGE_Alley_Left",
            dims=(0.3, depth, height),
            loc=(-width * 0.5, 0.0, 0.0),
            color=wall_color, kind="box", collection="SET"
        )
        w_right = P.prop(
            sc, "STAGE_Alley_Right",
            dims=(0.3, depth, height),
            loc=(width * 0.5, 0.0, 0.0),
            color=wall_color, kind="box", collection="SET"
        )
        walls.extend([w_left, w_right])

    return floor, walls


def setup_stage_lighting(sc, lighting_spec: dict):
    """Đánh sáng chuẩn điện ảnh Gate 84 theo preset hoặc thông số tùy chỉnh."""
    preset = lighting_spec.get("preset", "studio_3point")
    target_loc = mathutils.Vector(lighting_spec.get("target_loc", (0.0, 0.0, 1.5)))
    key_energy = float(lighting_spec.get("key_energy", 300.0))

    if preset == "saigon_noon":
        specs = [
            ("LGT_Sun_Key", target_loc + mathutils.Vector((3.0, -2.5, 6.0)), key_energy * 1.5, (1.0, 0.96, 0.88), 0.8),
            ("LGT_Sky_Fill", target_loc + mathutils.Vector((-3.0, -2.0, 4.0)), key_energy * 0.4, (0.78, 0.88, 1.0), 4.0),
            ("LGT_Bounce", target_loc + mathutils.Vector((0.0, -1.5, 0.4)), key_energy * 0.25, (0.95, 0.88, 0.78), 2.5),
        ]
    elif preset == "golden_hour":
        specs = [
            ("LGT_Golden_Key", target_loc + mathutils.Vector((4.0, -1.5, 1.8)), key_energy * 1.3, (1.0, 0.72, 0.42), 1.2),
            ("LGT_Cool_Fill", target_loc + mathutils.Vector((-3.0, -2.0, 2.5)), key_energy * 0.25, (0.65, 0.78, 1.0), 3.5),
            ("LGT_Warm_Rim", target_loc + mathutils.Vector((-1.5, 2.5, 2.2)), key_energy * 0.9, (1.0, 0.82, 0.55), 0.8),
        ]
    elif preset == "night_alley":
        specs = [
            ("LGT_StreetLamp_Key", target_loc + mathutils.Vector((1.2, -1.0, 3.2)), key_energy * 0.8, (1.0, 0.76, 0.45), 0.5),
            ("LGT_NightSky_Fill", target_loc + mathutils.Vector((-2.0, -2.0, 4.0)), key_energy * 0.15, (0.45, 0.62, 0.95), 5.0),
            ("LGT_Neon_Rim", target_loc + mathutils.Vector((-1.2, 2.2, 1.8)), key_energy * 0.6, (0.35, 0.85, 1.0), 0.6),
        ]
    else:  # studio_3point
        specs = [
            ("LGT_Key", target_loc + mathutils.Vector((2.2, -2.2, 2.3)), key_energy, (1.0, 0.94, 0.86), 1.2),
            ("LGT_Fill", target_loc + mathutils.Vector((-2.5, -1.8, 1.7)), key_energy * 0.28, (0.82, 0.90, 1.0), 2.5),
            ("LGT_Rim", target_loc + mathutils.Vector((-0.8, 2.2, 2.4)), key_energy * 0.75, (1.0, 0.98, 0.92), 0.7),
        ]

    light_coll = P.coll(sc, "LIGHTS")
    created = []
    for name, loc, energy, color, size in specs:
        ldata = bpy.data.lights.new(name=name, type='AREA')
        ldata.energy = energy
        ldata.color = color
        ldata.size = size
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        light_coll.objects.link(lobj)
        lobj.location = loc
        direction = target_loc - loc
        lobj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        created.append(lobj)
    return created


# ==============================================================================
# 3. XUẤT PASS DEPTH & COLOR ID MASK CHO AI VIDEO (CONTROLNET / VACE / LTX / WAN)
# ==============================================================================

def render_depth_and_id_frames(sc, shot_id: str, frames: list, out_dir: Path):
    """
    Xuất nhanh ảnh First/Mid/Last kèm bản đồ Màu Định Danh (Material ID)
    bằng Workbench phẳng (FLAT) để làm Mask chuẩn tuyệt đối cho AI Video.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    prev_engine = sc.render.engine
    prev_light = sc.display.shading.light
    prev_color = sc.display.shading.color_type

    try:
        sc.render.engine = 'BLENDER_WORKBENCH'
        # 1. Color ID Mask (Flat Material Color - Không bóng đổ, tách biệt từng nhân vật/đạo cụ)
        sc.display.shading.light = 'FLAT'
        sc.display.shading.color_type = 'MATERIAL'
        for f in frames:
            sc.frame_set(f)
            sc.render.filepath = str(out_dir / f"{shot_id}_IDMask_f{f:04d}.png")
            bpy.ops.render.render(write_still=True)

        # 2. Shaded Previs Still (Studio + Material + Cavity + Shadow)
        sc.display.shading.light = 'STUDIO'
        sc.display.shading.color_type = 'MATERIAL'
        sc.display.shading.show_shadows = True
        sc.display.shading.show_cavity = True
        for f in frames:
            sc.frame_set(f)
            sc.render.filepath = str(out_dir / f"{shot_id}_Shaded_f{f:04d}.png")
            bpy.ops.render.render(write_still=True)
    finally:
        sc.render.engine = prev_engine
        sc.display.shading.light = prev_light
        sc.display.shading.color_type = prev_color


# ==============================================================================
# 4. HÀM CHÍNH: DỰNG TOÀN BỘ PHIM TRƯỜNG TỪ FILE SPEC JSON
# ==============================================================================

def build_from_spec(spec_path: Path, out_dir: Path):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)

    fps = int(spec.get("fps", 24))
    res = tuple(spec.get("resolution", [1920, 1080]))
    res_pct = int(spec.get("resolution_pct", 100))
    scene_name = spec.get("scene_name", "G84_Stage")

    sc = P.setup_scene(scene_name, res=res, fps=fps, pct=res_pct)
    sc.frame_start = int(spec.get("frame_start", 1))
    sc.frame_end = int(spec.get("frame_end", 121))  # Mặc định 121 frames (8*15 + 1 chuẩn LTX/Wan 5s @ 24fps)

    # 1. Dựng khung Phim trường & Ánh sáng
    floor, walls = build_stage_shell(sc, spec.get("world", {}))
    setup_stage_lighting(sc, spec.get("lighting", {}))

    # 2. Đặt Đạo cụ (Props) & Snap xuống sàn
    props_dict = {}
    for p_spec in spec.get("props", []):
        p_name = p_spec["name"]
        p_kind = p_spec.get("kind", "box")
        p_dims = tuple(p_spec.get("dims", [1.0, 1.0, 1.0]))
        p_loc = tuple(p_spec.get("location", [0.0, 0.0, 0.0]))
        p_color = tuple(p_spec.get("color", [0.55, 0.42, 0.30]))
        p_rot = float(p_spec.get("rot_z_deg", 0.0))

        p_obj = P.prop(sc, p_name, dims=p_dims, loc=p_loc, color=p_color, kind=p_kind, collection="SET", rot_z=p_rot)
        if p_spec.get("snap_to_ground", True):
            snap_to_ground_raycast(p_obj, floor, sink_offset=0.0)
        props_dict[p_name] = p_obj

    # 3. Đặt Nhân vật sẵn Rig / Mannequin có khớp & Tạo chuyển động mềm chuẩn kỹ thuật
    chars_dict = {}
    for c_spec in spec.get("characters", []):
        c_name = c_spec["name"]
        c_height = float(c_spec.get("height_m", 1.72))
        c_loc = tuple(c_spec.get("location", [0.0, 0.0, 0.0]))
        c_facing = float(c_spec.get("facing_deg", 0.0))
        c_color = tuple(c_spec.get("color_id", [0.85, 0.25, 0.22]))
        use_rigify = bool(c_spec.get("use_rigify", False))

        if use_rigify:
            c_root = P.rigify_proxy(sc, c_name, height=c_height, loc=c_loc, facing=c_facing, color=c_color)
        else:
            c_root = P.mannequin(sc, c_name, height=c_height, loc=c_loc, facing=c_facing, color=c_color)

        chars_dict[c_name] = c_root

        # Diễn xuất theo danh sách Keyframes (Blocking -> Smooth Bezier Auto-Clamped)
        keyframes = c_spec.get("keyframes", [])
        for kf in keyframes:
            frame = int(kf["frame"])
            sc.frame_set(frame)
            P.pose(
                c_root,
                loc=tuple(kf["location"]) if "location" in kf else None,
                facing=float(kf["facing_deg"]) if "facing_deg" in kf else None,
                bones=kf.get("bones"),
                **kf.get("parts", {})
            )
            P.key_block(P.movables(c_root), frame=frame)

        # Chuyển toàn bộ quỹ đạo nhân vật sang đường cong Bezier AUTO_CLAMPED mượt mà
        for m_obj in P.movables(c_root):
            apply_smooth_bezier_clamped(m_obj)

        # Thêm nhịp thở sinh học nếu là Armature
        if c_root.type == 'ARMATURE':
            add_breathing_and_idle_micro_motion(c_root, sc.frame_start, sc.frame_end, fps=fps)

    # Thiết lập Look-At tự nhiên sau khi đã tạo đủ nhân vật & đạo cụ
    all_targets = {**chars_dict, **props_dict}
    for c_spec in spec.get("characters", []):
        look_target_name = c_spec.get("look_at")
        if look_target_name and look_target_name in all_targets:
            c_root = chars_dict[c_spec["name"]]
            if c_root.type == 'ARMATURE':
                add_head_look_at_constraint(c_root, all_targets[look_target_name])

    # 4. Thiết lập Danh sách Cảnh quay & Máy quay (Multi-Camera Blocking + Timeline Markers)
    beats = spec.get("beats", ["Beat 1"])
    shots_spec = spec.get("shots", [])
    table = []
    for idx, sh in enumerate(shots_spec, start=1):
        entry = {
            "shot": int(sh.get("shot", idx * 10)),
            "beats": sh.get("beats", [1]),
            "start": int(sh.get("frame_start", sc.frame_start)),
            "end": int(sh.get("frame_end", sc.frame_end)),
            "size": sh.get("size", "MS"),
            "lens": float(sh.get("lens_mm", 35.0)),
            "subject": sh.get("subject", list(chars_dict.keys())[:1]),
            "look_at": sh.get("look_at", list(chars_dict.keys())[0] if chars_dict else None),
            "side": float(sh.get("side", 1.0)),
            "angle_deg": float(sh.get("angle_deg", 25.0)),
            "height": sh.get("height", "eye"),
            "why": sh.get("why", "Reference shot"),
        }
        if "cam_loc" in sh:
            entry["loc"] = tuple(sh["cam_loc"])
        if "move" in sh:
            entry["move"] = sh["move"]
        table.append(entry)

    cams = []
    if table and chars_dict:
        cams = P.build_shots(sc, table, chars_dict, prefix="CAM_")
        for cam, sh in zip(cams, shots_spec):
            # Phối cảnh 2 điểm tụ nếu có shift_y
            if "shift_y" in sh:
                cam.data.shift_y = float(sh["shift_y"])
            # Rung máy cầm tay tự nhiên (Handheld breathing)
            hh = float(sh.get("handheld_strength", 0.006))
            if hh > 0:
                P.handheld(cam, strength=hh, scale=24.0)
            apply_smooth_bezier_clamped(cam)

    # 5. Lưu file .blend gốc của Phim trường
    blend_out = out_dir / f"{scene_name}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))

    # 6. Xuất Bản vẽ Mặt bằng (Top-Down Floor Plan), Contact Sheet & Video Tham Chiếu
    report = {
        "scene_name": scene_name,
        "blend_file": str(blend_out),
        "fps": fps,
        "frame_range": [sc.frame_start, sc.frame_end],
        "shots_rendered": [],
    }

    if table and chars_dict:
        floor_plan_path = out_dir / "01_TopDown_FloorPlan.png"
        P.floor_plan(sc, table, chars_dict, str(floor_plan_path))
        stills = P.render_stills(sc, table, str(out_dir / "stills"), stamp=True, live_ends=True, chars=chars_dict)
        cs_path = P.contact_sheet(sc, table, str(out_dir), cols=3, name="02_ContactSheet_Shots", chars=chars_dict)
        audit_res = P.audit(sc, table, chars_dict)
        report["floor_plan"] = str(floor_plan_path)
        report["contact_sheet"] = str(cs_path)
        report["previs_audit"] = audit_res

        # Xuất First/Mid/Last Shaded + Color ID Mask cho từng Shot
        for sh_entry in table:
            sh_id = f"Shot_{sh_entry['shot']:03d}"
            f_start, f_end = sh_entry["start"], sh_entry["end"]
            f_mid = (f_start + f_end) // 2
            render_depth_and_id_frames(sc, sh_id, [f_start, f_mid, f_end], out_dir / "passes")
            report["shots_rendered"].append({
                "shot_id": sh_id,
                "lens_mm": sh_entry["lens"],
                "size": sh_entry["size"],
                "frames": [f_start, f_end],
                "total_frames": f_end - f_start + 1,
                "why": sh_entry["why"],
            })

        # Xuất Video Tham Chiếu MP4 (Playblast mượt toàn cảnh)
        if B is not None and hasattr(P, "animatic"):
            mp4_out = out_dir / f"{scene_name}_Reference_Playblast.mp4"
            try:
                from bx_review import playblast
                sc.frame_set(sc.frame_start)
                playblast(str(mp4_out), scene=sc, res_pct=res_pct, color_type="MATERIAL")
                report["reference_video_mp4"] = str(mp4_out)
            except Exception as exc:
                report["playblast_warning"] = str(exc)

    report_path = out_dir / "STAGE_HANDOFF_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[G84 Stage Director] HOÀN TẤT! Báo cáo: {report_path}")
    return report


def _cli():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    import argparse
    parser = argparse.ArgumentParser(description="Gate 84 3D Reference Stage Director")
    parser.add_argument("--spec", required=True, help="Đường dẫn tới file stage_spec.json")
    parser.add_argument("--out", required=True, help="Thư mục xuất kết quả")
    args = parser.parse_args(argv)
    build_from_spec(Path(args.spec), Path(args.out))


if __name__ == "__main__":
    _cli()
