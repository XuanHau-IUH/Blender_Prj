import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler
import sys
import os

def build_perfect_chest():
    # -------------------------------------------------------------
    # 1. SCENE CLEANUP & SETUP (blender-scene-setup)
    # -------------------------------------------------------------
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
            
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'
    
    col_chest = bpy.data.collections.get("ASSET_Chest")
    if not col_chest:
        col_chest = bpy.data.collections.new("ASSET_Chest")
        scene.collection.children.link(col_chest)
        
    col_ld = bpy.data.collections.get("LD_Lookdev")
    if not col_ld:
        col_ld = bpy.data.collections.new("LD_Lookdev")
        scene.collection.children.link(col_ld)

    # -------------------------------------------------------------
    # 2. SHADERS (blender-pbr-materials)
    # -------------------------------------------------------------
    # Material 1: Stylized Honey-Caramel Oak Wood
    mat_wood = bpy.data.materials.new(name="M_Chest_Wood")
    mat_wood.use_nodes = True
    nw = mat_wood.node_tree.nodes
    lw = mat_wood.node_tree.links
    nw.clear()
    
    out_w = nw.new("ShaderNodeOutputMaterial")
    bsdf_w = nw.new("ShaderNodeBsdfPrincipled")
    lw.new(bsdf_w.outputs["BSDF"], out_w.inputs["Surface"])
    
    tc_w = nw.new("ShaderNodeTexCoord")
    map_w = nw.new("ShaderNodeMapping")
    map_w.inputs["Scale"].default_value = (4.5, 1.2, 1.0)
    lw.new(tc_w.outputs["UV"], map_w.inputs["Vector"])
    
    wave_w = nw.new("ShaderNodeTexWave")
    wave_w.wave_type = 'BANDS'
    wave_w.bands_direction = 'Y'
    wave_w.inputs["Scale"].default_value = 3.2
    wave_w.inputs["Distortion"].default_value = 1.5
    wave_w.inputs["Detail"].default_value = 2.0
    lw.new(map_w.outputs["Vector"], wave_w.inputs["Vector"])
    
    ramp_w = nw.new("ShaderNodeValToRGB")
    ramp_w.color_ramp.elements[0].position = 0.12
    ramp_w.color_ramp.elements[0].color = (0.52, 0.19, 0.03, 1.0) # Rich warm grain
    ramp_w.color_ramp.elements[1].position = 0.85
    ramp_w.color_ramp.elements[1].color = (0.86, 0.46, 0.10, 1.0) # Golden amber oak
    lw.new(wave_w.outputs["Fac"], ramp_w.inputs["Fac"])
    lw.new(ramp_w.outputs["Color"], bsdf_w.inputs["Base Color"])
    
    bsdf_w.inputs["Roughness"].default_value = 0.52
    bsdf_w.inputs["Specular IOR Level"].default_value = 0.45
    
    bump_w = nw.new("ShaderNodeBump")
    bump_w.inputs["Strength"].default_value = 0.04
    bump_w.inputs["Distance"].default_value = 0.02
    lw.new(wave_w.outputs["Fac"], bump_w.inputs["Height"])
    lw.new(bump_w.outputs["Normal"], bsdf_w.inputs["Normal"])
    
    # Material 2: Stylized Slate Iron Metal
    mat_metal = bpy.data.materials.new(name="M_Chest_Metal")
    mat_metal.use_nodes = True
    nm = mat_metal.node_tree.nodes
    lm = mat_metal.node_tree.links
    nm.clear()
    
    out_m = nm.new("ShaderNodeOutputMaterial")
    bsdf_m = nm.new("ShaderNodeBsdfPrincipled")
    lm.new(bsdf_m.outputs["BSDF"], out_m.inputs["Surface"])
    
    tc_m = nm.new("ShaderNodeTexCoord")
    noise_m = nm.new("ShaderNodeTexNoise")
    noise_m.inputs["Scale"].default_value = 22.0
    lm.new(tc_m.outputs["Object"], noise_m.inputs["Vector"])
    
    ramp_m = nw.new("ShaderNodeValToRGB")
    ramp_m.color_ramp.elements[0].position = 0.1
    ramp_m.color_ramp.elements[0].color = (0.17, 0.20, 0.24, 1.0) # Slate gunmetal
    ramp_m.color_ramp.elements[1].position = 0.9
    ramp_m.color_ramp.elements[1].color = (0.28, 0.32, 0.38, 1.0) # Edge highlight
    lm.new(noise_m.outputs["Fac"], ramp_m.inputs["Fac"])
    lm.new(ramp_m.outputs["Color"], bsdf_m.inputs["Base Color"])
    
    bsdf_m.inputs["Metallic"].default_value = 0.94
    bsdf_m.inputs["Roughness"].default_value = 0.38
    bsdf_m.inputs["Specular IOR Level"].default_value = 0.5
    
    # Material 3: Hex Bolt Metal
    mat_bolt = bpy.data.materials.new(name="M_Chest_Bolt")
    mat_bolt.use_nodes = True
    nb = mat_bolt.node_tree.nodes
    lb = mat_bolt.node_tree.links
    nb.clear()
    out_b = nb.new("ShaderNodeOutputMaterial")
    bsdf_b = nb.new("ShaderNodeBsdfPrincipled")
    lb.new(bsdf_b.outputs["BSDF"], out_b.inputs["Surface"])
    bsdf_b.inputs["Base Color"].default_value = (0.26, 0.30, 0.36, 1.0)
    bsdf_b.inputs["Metallic"].default_value = 0.98
    bsdf_b.inputs["Roughness"].default_value = 0.30

    # Material 4: Dark Keyhole Cavity
    mat_kh = bpy.data.materials.new(name="M_Chest_Keyhole")
    mat_kh.use_nodes = True
    nkh = mat_kh.node_tree.nodes
    lkh = mat_kh.node_tree.links
    nkh.clear()
    out_kh = nkh.new("ShaderNodeOutputMaterial")
    bsdf_kh = nkh.new("ShaderNodeBsdfPrincipled")
    lkh.new(bsdf_kh.outputs["BSDF"], out_kh.inputs["Surface"])
    bsdf_kh.inputs["Base Color"].default_value = (0.015, 0.015, 0.018, 1.0)
    bsdf_kh.inputs["Roughness"].default_value = 0.90
    bsdf_kh.inputs["Specular IOR Level"].default_value = 0.1

    # -------------------------------------------------------------
    # 3. GEOMETRIC MODELING
    # -------------------------------------------------------------
    W = 1.40
    D = 0.88
    Z_ground = 0.03
    Z_seam = 0.48
    R = D / 2.0

    def finalize_obj(name, bm, mats):
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        
        obj = bpy.data.objects.new(name, me)
        col_chest.objects.link(obj)
        for m in mats:
            obj.data.materials.append(m)
            
        for p in obj.data.polygons:
            p.use_smooth = True
            
        mod_wn = obj.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
        mod_wn.mode = 'FACE_AREA'
        mod_wn.keep_sharp = True
            
        # Smart UV Unwrap (blender-retopology-uv)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)
        return obj

    # =============================================================
    # 1. WOOD MESH (SM_Chest_Wood)
    # =============================================================
    bm_wood = bmesh.new()
    W_w = W - 0.02
    D_w = D - 0.02
    
    # 3 Lower Body Planks
    plank_h = (Z_seam - Z_ground) / 3.0
    groove_w = 0.006
    for i in range(3):
        z_min = Z_ground + i * plank_h + (groove_w / 2.0 if i > 0 else 0)
        z_max = Z_ground + (i + 1) * plank_h - (groove_w / 2.0 if i < 2 else 0)
        zc = (z_min + z_max) / 2.0
        zh = (z_max - z_min)
        bmesh.ops.create_cube(
            bm_wood, size=1.0,
            matrix=Matrix.Translation((0, 0, zc)) @ Matrix.Diagonal((W_w, D_w, zh, 1.0))
        )
        
    # 5 Arched Lid Planks
    num_lid_planks = 5
    d_th = math.pi / num_lid_planks
    wood_thick = 0.038
    for p_idx in range(num_lid_planks):
        th_start = p_idx * d_th + 0.012
        th_end = (p_idx + 1) * d_th - 0.012
        sub_steps = 4
        verts_p = []
        for s in range(sub_steps + 1):
            t = th_start + (th_end - th_start) * (s / sub_steps)
            yo = -R * math.cos(t)
            zo = Z_seam + R * math.sin(t)
            yi = -(R - wood_thick) * math.cos(t)
            zi = Z_seam + (R - wood_thick) * math.sin(t)
            verts_p.append((yo, zo, yi, zi))
            
        x_min = -W_w / 2.0
        x_max = W_w / 2.0
        
        for s in range(sub_steps):
            yo1, zo1, yi1, zi1 = verts_p[s]
            yo2, zo2, yi2, zi2 = verts_p[s+1]
            
            v_o1_l = bm_wood.verts.new((x_min, yo1, zo1))
            v_o1_r = bm_wood.verts.new((x_max, yo1, zo1))
            v_o2_l = bm_wood.verts.new((x_min, yo2, zo2))
            v_o2_r = bm_wood.verts.new((x_max, yo2, zo2))
            
            v_i1_l = bm_wood.verts.new((x_min, yi1, zi1))
            v_i1_r = bm_wood.verts.new((x_max, yi1, zi1))
            v_i2_l = bm_wood.verts.new((x_min, yi2, zi2))
            v_i2_r = bm_wood.verts.new((x_max, yi2, zi2))
            
            bm_wood.faces.new((v_o1_l, v_o1_r, v_o2_r, v_o2_l))
            bm_wood.faces.new((v_i1_l, v_i2_l, v_i2_r, v_i1_r))
            if s == 0:
                bm_wood.faces.new((v_o1_l, v_i1_l, v_i1_r, v_o1_r))
            if s == sub_steps - 1:
                bm_wood.faces.new((v_o2_l, v_o2_r, v_i2_r, v_i2_l))
            bm_wood.faces.new((v_o1_l, v_o2_l, v_i2_l, v_i1_l))
            bm_wood.faces.new((v_o1_r, v_i1_r, v_i2_r, v_o2_r))

    # Lid Side Semicircular End Caps (proper triangle at apex to avoid 0-length edge)
    for sign in [-1, 1]:
        x_pos = sign * (W_w / 2.0 - 0.002)
        # Tier 0 (lower half: quad)
        z0 = Z_seam
        z1 = Z_seam + R / 2.0
        y_lim0 = R
        y_lim1 = math.sqrt(R*R - (R/2.0)*(R/2.0))
        
        v1 = bm_wood.verts.new((x_pos, -y_lim0, z0))
        v2 = bm_wood.verts.new((x_pos, y_lim0, z0))
        v3 = bm_wood.verts.new((x_pos, y_lim1, z1))
        v4 = bm_wood.verts.new((x_pos, -y_lim1, z1))
        if sign == 1:
            bm_wood.faces.new((v1, v2, v3, v4))
        else:
            bm_wood.faces.new((v4, v3, v2, v1))
            
        # Tier 1 (upper half: triangle meeting at apex)
        v_apex = bm_wood.verts.new((x_pos, 0.0, Z_seam + R))
        if sign == 1:
            bm_wood.faces.new((v4, v3, v_apex))
        else:
            bm_wood.faces.new((v_apex, v3, v4))

    obj_wood = finalize_obj("SM_Chest_Wood", bm_wood, [mat_wood])

    # =============================================================
    # 2. METAL MESH (SM_Chest_Metal)
    # =============================================================
    bm_metal = bmesh.new()
    metal_thick = 0.026
    
    # A) Main Horizontal Rim Belt (at Z_seam)
    belt_w = 0.08
    ow = W + metal_thick * 2
    od = D + metal_thick * 2
    
    # Front strip
    bmesh.ops.create_cube(
        bm_metal, size=1.0,
        matrix=Matrix.Translation((0, -D/2.0 - metal_thick/2.0, Z_seam)) @ Matrix.Diagonal((ow, metal_thick, belt_w, 1.0))
    )
    # Back strip
    bmesh.ops.create_cube(
        bm_metal, size=1.0,
        matrix=Matrix.Translation((0, D/2.0 + metal_thick/2.0, Z_seam)) @ Matrix.Diagonal((ow, metal_thick, belt_w, 1.0))
    )
    # Left strip (inset slightly in Y so ends don't fight with front/back strips)
    bmesh.ops.create_cube(
        bm_metal, size=1.0,
        matrix=Matrix.Translation((-W/2.0 - metal_thick/2.0, 0, Z_seam)) @ Matrix.Diagonal((metal_thick, D - 0.004, belt_w, 1.0))
    )
    # Right strip
    bmesh.ops.create_cube(
        bm_metal, size=1.0,
        matrix=Matrix.Translation((W/2.0 + metal_thick/2.0, 0, Z_seam)) @ Matrix.Diagonal((metal_thick, D - 0.004, belt_w, 1.0))
    )

    # B) 4 Bottom Corner Feet (Single Solid L-shaped Brackets -> 0 coplanar overlapping faces!)
    foot_h = 0.13
    foot_arm = 0.16
    foot_t = 0.038
    
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            # Origin of corner
            cx = sx * (W / 2.0 + metal_thick)
            cy = sy * (D / 2.0 + metal_thick)
            
            # 6 points of the L-bracket in X-Y
            p0 = Vector((cx, cy, 0.0))
            p1 = Vector((cx - sx * foot_arm, cy, 0.0))
            p2 = Vector((cx - sx * foot_arm, cy - sy * foot_t, 0.0))
            p3 = Vector((cx - sx * foot_t, cy - sy * foot_t, 0.0))
            p4 = Vector((cx - sx * foot_t, cy - sy * foot_arm, 0.0))
            p5 = Vector((cx, cy - sy * foot_arm, 0.0))
            
            pts = [p0, p1, p2, p3, p4, p5]
            if (sx * sy) < 0:
                pts.reverse()
                
            v_base = [bm_metal.verts.new(p) for p in pts]
            f_base = bm_metal.faces.new(v_base)
            res_ext = bmesh.ops.extrude_face_region(bm_metal, geom=[f_base])
            ext_verts = [v for v in res_ext['geom'] if isinstance(v, bmesh.types.BMVert)]
            bmesh.ops.translate(bm_metal, vec=Vector((0, 0, foot_h)), verts=ext_verts)
            f_base.normal_flip()

    # C) 4 Vertical Corner Angle Pillars
    # Slightly penetrate foot and rim to avoid coplanar boundary faces
    pillar_z_bot = foot_h - 0.005
    pillar_z_top = Z_seam - belt_w / 2.0 + 0.005
    pillar_h = pillar_z_top - pillar_z_bot
    pillar_zc = (pillar_z_bot + pillar_z_top) / 2.0
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            cx = sx * (W / 2.0)
            cy = sy * (D / 2.0)
            bmesh.ops.create_cube(
                bm_metal, size=1.0,
                matrix=Matrix.Translation((cx + sx * (metal_thick/2.0), cy + sy * (metal_thick/2.0), pillar_zc)) @
                       Matrix.Diagonal((0.074, 0.074, pillar_h, 1.0))
            )

    # D) 2 Arched Side Metal Rims (closed manifold quad ribbons)
    arch_width = 0.075
    num_arch_segs = 24
    dth = math.pi / num_arch_segs
    r_in = R - arch_width
    r_out = R + metal_thick
    
    for sx in [-1, 1]:
        x_base = sx * (W / 2.0 + 0.002) if sx == 1 else sx * (W / 2.0 + 0.002) - metal_thick
        v_in = []
        v_out = []
        for i in range(num_arch_segs + 1):
            th = i * dth
            yi = -r_in * math.cos(th)
            zi = Z_seam + r_in * math.sin(th)
            yo = -r_out * math.cos(th)
            zo = Z_seam + r_out * math.sin(th)
            v_in.append(bm_metal.verts.new((x_base, yi, zi)))
            v_out.append(bm_metal.verts.new((x_base, yo, zo)))
            
        faces_arch = []
        for i in range(num_arch_segs):
            f = bm_metal.faces.new((v_in[i], v_out[i], v_out[i+1], v_in[i+1]))
            faces_arch.append(f)
            
        res_ext = bmesh.ops.extrude_face_region(bm_metal, geom=faces_arch)
        ext_verts = [v for v in res_ext['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm_metal, vec=Vector((sx * metal_thick, 0, 0)), verts=ext_verts)
        for f in faces_arch:
            f.normal_flip()

    # E) Two Vertical Lid Metal Straps
    strap_w = 0.125
    strap_thick = 0.024
    num_strap_segs = 24
    dsth = math.pi / num_strap_segs
    rs_in = R - 0.004
    rs_out = R + strap_thick
    
    for sx in [-0.38, 0.38]:
        x_start = sx - strap_w / 2.0
        v_in = []
        v_out = []
        for i in range(num_strap_segs + 1):
            th = i * dsth
            yi = -rs_in * math.cos(th)
            zi = Z_seam + rs_in * math.sin(th)
            yo = -rs_out * math.cos(th)
            zo = Z_seam + rs_out * math.sin(th)
            v_in.append(bm_metal.verts.new((x_start, yi, zi)))
            v_out.append(bm_metal.verts.new((x_start, yo, zo)))
            
        faces_strap = []
        for i in range(num_strap_segs):
            f = bm_metal.faces.new((v_in[i], v_out[i], v_out[i+1], v_in[i+1]))
            faces_strap.append(f)
            
        res_ext = bmesh.ops.extrude_face_region(bm_metal, geom=faces_strap)
        ext_verts = [v for v in res_ext['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm_metal, vec=Vector((strap_w, 0, 0)), verts=ext_verts)
        for f in faces_strap:
            f.normal_flip()

    # F) Stylized Shield Lock Plate with True Keyhole Cavity
    lock_w = 0.20
    lock_h = 0.23
    lock_t = 0.026
    lock_y = -D / 2.0 - metal_thick - lock_t / 2.0
    c = 0.05
    hw = lock_w / 2.0
    hh = lock_h / 2.0
    poly_pts = [
        (-hw + c, hh),
        (hw - c, hh),
        (hw, hh - c),
        (hw, -hh + c),
        (hw - c, -hh),
        (-hw + c, -hh),
        (-hw, -hh + c),
        (-hw, hh - c)
    ]
    
    v_front = []
    for px, pz in poly_pts:
        v_front.append(bm_metal.verts.new((px, lock_y - lock_t/2.0, Z_seam + pz)))
    f_plate = bm_metal.faces.new(v_front)
    res_ext = bmesh.ops.extrude_face_region(bm_metal, geom=[f_plate])
    ext_verts = [v for v in res_ext['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm_metal, vec=Vector((0, lock_t, 0)), verts=ext_verts)
    f_plate.normal_flip()
    
    # Lower Latch Lip
    bmesh.ops.create_cube(
        bm_metal, size=1.0,
        matrix=Matrix.Translation((0, lock_y, Z_seam - hh - 0.02)) @ Matrix.Diagonal((0.09, lock_t * 0.95, 0.04, 1.0))
    )
    
    # Keyhole Cavity (Material Index 1: M_Chest_Keyhole)
    kh_y = lock_y - lock_t / 2.0 - 0.002
    kh_verts = []
    kh_r = 0.016
    kh_zc = Z_seam + 0.016
    for i in range(12):
        ang = i * (2 * math.pi / 12.0)
        kx = kh_r * math.cos(ang)
        kz = kh_zc + kh_r * math.sin(ang)
        kh_verts.append(bm_metal.verts.new((kx, kh_y, kz)))
    f_kh_circ = bm_metal.faces.new(kh_verts)
    f_kh_circ.material_index = 1
    
    slot_w_top = 0.010
    slot_w_bot = 0.016
    slot_h = 0.036
    s1 = bm_metal.verts.new((-slot_w_top/2.0, kh_y, kh_zc))
    s2 = bm_metal.verts.new((slot_w_top/2.0, kh_y, kh_zc))
    s3 = bm_metal.verts.new((slot_w_bot/2.0, kh_y, kh_zc - slot_h))
    s4 = bm_metal.verts.new((-slot_w_bot/2.0, kh_y, kh_zc - slot_h))
    f_kh_slot = bm_metal.faces.new((s1, s2, s3, s4))
    f_kh_slot.material_index = 1

    obj_metal = finalize_obj("SM_Chest_Metal", bm_metal, [mat_metal, mat_kh])

    # =============================================================
    # 3. HEXAGONAL BOLTS (SM_Chest_Bolts)
    # =============================================================
    bm_bolts = bmesh.new()
    
    def add_hex_bolt(pos, normal, radius=0.022, height=0.018):
        embed_offset = 0.001
        z_axis = Vector(normal).normalized()
        ref = Vector((0, 0, 1)) if abs(z_axis.z) < 0.9 else Vector((0, 1, 0))
        x_axis = z_axis.cross(ref).normalized()
        y_axis = z_axis.cross(x_axis).normalized()
        rot_mat = Matrix((x_axis, y_axis, z_axis)).transposed().to_4x4()
        
        base_origin = pos - z_axis * embed_offset
        total_h = height + embed_offset
        
        v_base = []
        v_mid = []
        v_top = []
        for i in range(6):
            ang = i * (math.pi / 3.0) + (math.pi / 6.0)
            hx = radius * math.cos(ang)
            hy = radius * math.sin(ang)
            p_b = base_origin + rot_mat @ Vector((hx, hy, 0.0))
            p_m = base_origin + rot_mat @ Vector((hx, hy, total_h * 0.7))
            p_t = base_origin + rot_mat @ Vector((hx * 0.7, hy * 0.7, total_h))
            v_base.append(bm_bolts.verts.new(p_b))
            v_mid.append(bm_bolts.verts.new(p_m))
            v_top.append(bm_bolts.verts.new(p_t))
            
        for i in range(6):
            i_nxt = (i + 1) % 6
            bm_bolts.faces.new((v_base[i], v_base[i_nxt], v_mid[i_nxt], v_mid[i]))
            bm_bolts.faces.new((v_mid[i], v_mid[i_nxt], v_top[i_nxt], v_top[i]))
        bm_bolts.faces.new(v_top)
        bm_bolts.faces.new(reversed(v_base))

    # BOLT POSITIONS:
    # 1. Front Horizontal Rim
    y_front_surf = -D / 2.0 - metal_thick
    add_hex_bolt(Vector((-0.60, y_front_surf, Z_seam)), Vector((0, -1, 0)))
    add_hex_bolt(Vector((-0.38, y_front_surf, Z_seam)), Vector((0, -1, 0)))
    add_hex_bolt(Vector((0.38, y_front_surf, Z_seam)), Vector((0, -1, 0)))
    add_hex_bolt(Vector((0.60, y_front_surf, Z_seam)), Vector((0, -1, 0)))
    
    # 2. Front Straps on Lid (at theta = 18 deg)
    rad_f = math.radians(18.0)
    y_str_f = -(R + strap_thick) * math.cos(rad_f)
    z_str_f = Z_seam + (R + strap_thick) * math.sin(rad_f)
    norm_f = Vector((0, -math.cos(rad_f), math.sin(rad_f)))
    add_hex_bolt(Vector((-0.38, y_str_f, z_str_f)), norm_f)
    add_hex_bolt(Vector((0.38, y_str_f, z_str_f)), norm_f)

    # 3. Rear Horizontal Rim
    y_rear_surf = D / 2.0 + metal_thick
    add_hex_bolt(Vector((-0.60, y_rear_surf, Z_seam)), Vector((0, 1, 0)))
    add_hex_bolt(Vector((-0.38, y_rear_surf, Z_seam)), Vector((0, 1, 0)))
    add_hex_bolt(Vector((0.38, y_rear_surf, Z_seam)), Vector((0, 1, 0)))
    add_hex_bolt(Vector((0.60, y_rear_surf, Z_seam)), Vector((0, 1, 0)))
    
    # 4. Rear Straps on Lid (at theta = 162 deg)
    rad_r = math.radians(162.0)
    y_str_r = -(R + strap_thick) * math.cos(rad_r)
    z_str_r = Z_seam + (R + strap_thick) * math.sin(rad_r)
    norm_r = Vector((0, -math.cos(rad_r), math.sin(rad_r)))
    add_hex_bolt(Vector((-0.38, y_str_r, z_str_r)), norm_r)
    add_hex_bolt(Vector((0.38, y_str_r, z_str_r)), norm_r)

    # 5. Over the Curved Lid Straps
    for sx in [-0.38, 0.38]:
        for ang_deg in [45.0, 90.0, 135.0]:
            rad = math.radians(ang_deg)
            y_b = -(R + strap_thick) * math.cos(rad)
            z_b = Z_seam + (R + strap_thick) * math.sin(rad)
            norm = Vector((0, -math.cos(rad), math.sin(rad)))
            add_hex_bolt(Vector((sx, y_b, z_b)), norm)

    # 6. Side Views: surface is at X = +/- (W/2 + metal_thick) = +/- 0.726
    x_left_surf = -W / 2.0 - metal_thick
    x_right_surf = W / 2.0 + metal_thick
    add_hex_bolt(Vector((x_left_surf, -0.28, Z_seam)), Vector((-1, 0, 0)))
    add_hex_bolt(Vector((x_left_surf, 0.28, Z_seam)), Vector((-1, 0, 0)))
    add_hex_bolt(Vector((x_right_surf, -0.28, Z_seam)), Vector((1, 0, 0)))
    add_hex_bolt(Vector((x_right_surf, 0.28, Z_seam)), Vector((1, 0, 0)))

    bmesh.ops.recalc_face_normals(bm_bolts, faces=bm_bolts.faces)
    me_bolts = bpy.data.meshes.new("SM_Chest_Bolts")
    bm_bolts.to_mesh(me_bolts)
    bm_bolts.free()
    
    obj_bolts = bpy.data.objects.new("SM_Chest_Bolts", me_bolts)
    col_chest.objects.link(obj_bolts)
    obj_bolts.data.materials.append(mat_bolt)
    
    bpy.context.view_layer.objects.active = obj_bolts
    obj_bolts.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj_bolts.select_set(False)

    # -------------------------------------------------------------
    # 4. LIGHTING & CAMERA (blender-lighting-lookdev)
    # -------------------------------------------------------------
    l_key = bpy.data.lights.new("Light_Key", 'AREA')
    l_key.energy = 450.0
    l_key.size = 2.0
    l_key.color = (1.0, 0.95, 0.90)
    o_key = bpy.data.objects.new("Light_Key", l_key)
    o_key.location = (2.2, -2.8, 2.4)
    o_key.rotation_euler = (math.radians(52), math.radians(10), math.radians(38))
    col_ld.objects.link(o_key)
    
    l_fill = bpy.data.lights.new("Light_Fill", 'AREA')
    l_fill.energy = 160.0
    l_fill.size = 2.4
    l_fill.color = (0.86, 0.92, 1.0)
    o_fill = bpy.data.objects.new("Light_Fill", l_fill)
    o_fill.location = (-2.6, -2.0, 1.8)
    o_fill.rotation_euler = (math.radians(55), math.radians(-10), math.radians(-50))
    col_ld.objects.link(o_fill)
    
    l_rim = bpy.data.lights.new("Light_Rim", 'AREA')
    l_rim.energy = 380.0
    l_rim.size = 2.0
    l_rim.color = (0.95, 0.98, 1.0)
    o_rim = bpy.data.objects.new("Light_Rim", l_rim)
    o_rim.location = (0.6, 2.8, 2.5)
    o_rim.rotation_euler = (math.radians(-45), 0, math.radians(170))
    col_ld.objects.link(o_rim)
    
    bm_g = bmesh.new()
    bmesh.ops.create_grid(bm_g, x_segments=1, y_segments=1, size=8.0)
    me_g = bpy.data.meshes.new("Studio_Backdrop")
    bm_g.to_mesh(me_g)
    bm_g.free()
    o_g = bpy.data.objects.new("Studio_Backdrop", me_g)
    col_ld.objects.link(o_g)
    mat_g = bpy.data.materials.new("M_Studio_Backdrop")
    mat_g.use_nodes = True
    bsdf_g = mat_g.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs["Base Color"].default_value = (0.84, 0.86, 0.88, 1.0)
        bsdf_g.inputs["Roughness"].default_value = 0.8
    o_g.data.materials.append(mat_g)
    
    cam = bpy.data.cameras.new("Camera_Chest")
    cam.lens = 75
    o_cam = bpy.data.objects.new("Camera_Chest", cam)
    o_cam.location = (2.5, -3.2, 2.1)
    target = Vector((0, 0, 0.48))
    direction = target - o_cam.location
    o_cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    col_ld.objects.link(o_cam)
    scene.camera = o_cam
    
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.view_settings.view_transform = 'Khronos PBR Neutral'
    
    # Save blend file for user
    blend_path = r"D:\Blender\AI\Stylized_Chest_Production.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"SUCCESS: Production chest saved to {blend_path}")

build_perfect_chest()
