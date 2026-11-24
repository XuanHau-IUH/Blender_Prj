import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def create_stylized_chest():
    # 1. Clean Scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0: bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0: bpy.data.materials.remove(block)

    # 2. Materials
    # Stylized Wood
    mat_wood = bpy.data.materials.new(name="M_Chest_Wood")
    mat_wood.use_nodes = True
    nodes = mat_wood.node_tree.nodes
    links = mat_wood.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_ramp = nodes.new(type='ShaderNodeValToRGB')
    node_noise = nodes.new(type='ShaderNodeTexNoise')
    node_coord = nodes.new(type='ShaderNodeTexCoord')
    node_map = nodes.new(type='ShaderNodeMapping')

    # Stylized warm amber/orange wood matching reference
    node_ramp.color_ramp.elements[0].position = 0.15
    node_ramp.color_ramp.elements[0].color = (0.62, 0.28, 0.06, 1.0) # deep warm brown
    node_ramp.color_ramp.elements[1].position = 0.70
    node_ramp.color_ramp.elements[1].color = (0.86, 0.48, 0.14, 1.0) # rich orange amber
    e2 = node_ramp.color_ramp.elements.new(0.95)
    e2.color = (0.95, 0.62, 0.24, 1.0) # warm highlight

    node_noise.inputs['Scale'].default_value = 6.0
    node_noise.inputs['Detail'].default_value = 2.0
    node_noise.inputs['Roughness'].default_value = 0.4
    node_map.inputs['Scale'].default_value = (0.5, 3.0, 0.5)

    links.new(node_coord.outputs['Object'], node_map.inputs['Vector'])
    links.new(node_map.outputs['Vector'], node_noise.inputs['Vector'])
    links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
    links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    node_bsdf.inputs['Roughness'].default_value = 0.50
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

    # Stylized Slate Metal
    mat_metal = bpy.data.materials.new(name="M_Chest_Metal")
    mat_metal.use_nodes = True
    mn = mat_metal.node_tree.nodes
    ml = mat_metal.node_tree.links
    mn.clear()
    m_out = mn.new(type='ShaderNodeOutputMaterial')
    m_bsdf = mn.new(type='ShaderNodeBsdfPrincipled')
    m_bsdf.inputs['Base Color'].default_value = (0.40, 0.45, 0.51, 1.0) # slate bluish-gray
    m_bsdf.inputs['Metallic'].default_value = 0.80
    m_bsdf.inputs['Roughness'].default_value = 0.35
    ml.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])

    # Dark Keyhole
    mat_dark = bpy.data.materials.new(name="M_Keyhole_Dark")
    mat_dark.use_nodes = True
    mat_dark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
    mat_dark.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9

    # Bolts
    mat_bolt = bpy.data.materials.new(name="M_Chest_Bolts")
    mat_bolt.use_nodes = True
    mat_bolt.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.55, 0.60, 0.67, 1.0)
    mat_bolt.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 0.88
    mat_bolt.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.28

    coll = bpy.data.collections.new("Stylized_Chest")
    bpy.context.scene.collection.children.link(coll)

    # 3. Dimensions
    W = 1.64   # Width (X)
    D = 1.06   # Depth (Y)
    H_base = 0.50  # Height of base
    H_lid = 0.52   # Height of lid arch
    Z_base_bot = 0.06
    Z_split = Z_base_bot + H_base # 0.56
    Z_top = Z_split + H_lid       # 1.08

    hw = W / 2.0  # 0.82
    hd = D / 2.0  # 0.53

    # ========================================================
    # 4. BASE WOOD (Planks with clean Quad Grooves)
    # ========================================================
    # We construct the base with 4 planks on front/back/sides
    mesh_base = bpy.data.meshes.new("Chest_Base_Wood")
    bm_b = bmesh.new()

    z_plank_cuts = [Z_base_bot, 0.18, 0.30, 0.43, Z_split]
    # Build box with loop cuts along Z
    bmesh.ops.create_cube(bm_b, size=1.0)
    # Scale cube to base dimensions
    for v in bm_b.verts:
        v.co.x *= W
        v.co.y *= D
        v.co.z = Z_base_bot + (v.co.z + 0.5) * H_base

    # Subdivide vertical edges to create 4 planks
    # Subdivide X and Y edges
    edges_z = [e for e in bm_b.edges if abs(e.verts[0].co.x - e.verts[1].co.x) < 0.001 and abs(e.verts[0].co.y - e.verts[1].co.y) < 0.001]
    bmesh.ops.subdivide_edges(bm_b, edges=edges_z, cuts=3)

    # Align new loop cut vertices to exact plank heights
    for v in bm_b.verts:
        if 0.15 < v.co.z < 0.22:
            v.co.z = 0.185
        elif 0.28 < v.co.z < 0.35:
            v.co.z = 0.310
        elif 0.40 < v.co.z < 0.47:
            v.co.z = 0.435

    bm_b.to_mesh(mesh_base)
    bm_b.free()

    obj_base = bpy.data.objects.new("Chest_Base_Wood", mesh_base)
    coll.objects.link(obj_base)
    obj_base.data.materials.append(mat_wood)

    bev_b = obj_base.modifiers.new("Bevel", type='BEVEL')
    bev_b.width = 0.018
    bev_b.segments = 2
    bev_b.profile = 0.7
    obj_base.data.polygons.foreach_set('use_smooth', [True] * len(obj_base.data.polygons))

    # ========================================================
    # 5. LID WOOD (Arched Barrel Vault with End Caps)
    # ========================================================
    mesh_lid = bpy.data.meshes.new("Chest_Lid_Wood")
    bm_l = bmesh.new()

    n_arch = 16
    n_len = 10

    def get_arch_z(y_val):
        yn = max(-1.0, min(1.0, y_val / hd))
        # Arch profile (semi-ellipse with subtle flat crown)
        return Z_split + H_lid * ((1.0 - (yn ** 2)) ** 0.60)

    # Grid of vertices along arch (Y) and length (X)
    lid_verts = [] # [i_arch][i_len]
    for ia in range(n_arch + 1):
        t = ia / n_arch
        y = -hd + (2 * hd * t)
        z = get_arch_z(y)
        row = []
        for il in range(n_len + 1):
            tl = il / n_len
            x = -hw + (2 * hw * tl)
            row.append(bm_l.verts.new(Vector((x, y, z))))
        lid_verts.append(row)

    bm_l.verts.ensure_lookup_table()

    # Curved top faces
    for ia in range(n_arch):
        for il in range(n_len):
            v1 = lid_verts[ia][il]
            v2 = lid_verts[ia][il+1]
            v3 = lid_verts[ia+1][il+1]
            v4 = lid_verts[ia+1][il]
            bm_l.faces.new([v1, v2, v3, v4])

    # Left End Cap (il = 0)
    left_bot_verts = []
    for ia in range(n_arch + 1):
        y = -hd + (2 * hd * (ia / n_arch))
        left_bot_verts.append(bm_l.verts.new(Vector((-hw, y, Z_split))))

    for ia in range(n_arch):
        v1 = left_bot_verts[ia]
        v2 = left_bot_verts[ia+1]
        v3 = lid_verts[ia+1][0]
        v4 = lid_verts[ia][0]
        bm_l.faces.new([v1, v2, v3, v4])

    # Right End Cap (il = n_len)
    right_bot_verts = []
    for ia in range(n_arch + 1):
        y = -hd + (2 * hd * (ia / n_arch))
        right_bot_verts.append(bm_l.verts.new(Vector((hw, y, Z_split))))

    for ia in range(n_arch):
        v1 = right_bot_verts[ia]
        v2 = lid_verts[ia][n_len]
        v3 = lid_verts[ia+1][n_len]
        v4 = right_bot_verts[ia+1]
        bm_l.faces.new([v1, v2, v3, v4])

    # Bottom Split Face
    for ia in range(n_arch):
        v1 = left_bot_verts[ia]
        v2 = right_bot_verts[ia]
        v3 = right_bot_verts[ia+1]
        v4 = left_bot_verts[ia+1]
        bm_l.faces.new([v1, v2, v3, v4])

    bm_l.to_mesh(mesh_lid)
    bm_l.free()

    obj_lid = bpy.data.objects.new("Chest_Lid_Wood", mesh_lid)
    coll.objects.link(obj_lid)
    obj_lid.data.materials.append(mat_wood)

    bev_l = obj_lid.modifiers.new("Bevel", type='BEVEL')
    bev_l.width = 0.015
    bev_l.segments = 2
    bev_l.profile = 0.7
    obj_lid.data.polygons.foreach_set('use_smooth', [True] * len(obj_lid.data.polygons))

    # ========================================================
    # 6. HORIZONTAL METAL RIM (Between Base & Lid)
    # ========================================================
    mesh_rim = bpy.data.meshes.new("Chest_Metal_Rim")
    bm_r = bmesh.new()

    rim_h = 0.08
    rim_t = 0.025
    r_z1 = Z_split - (rim_h / 2.0)
    r_z2 = Z_split + (rim_h / 2.0)

    # 4 corners
    outer_rect = [
        (-hw - rim_t, -hd - rim_t),
        ( hw + rim_t, -hd - rim_t),
        ( hw + rim_t,  hd + rim_t),
        (-hw - rim_t,  hd + rim_t),
    ]
    inner_rect = [
        (-hw, -hd),
        ( hw, -hd),
        ( hw,  hd),
        (-hw,  hd),
    ]

    vo1 = [bm_r.verts.new(Vector((p[0], p[1], r_z1))) for p in outer_rect]
    vo2 = [bm_r.verts.new(Vector((p[0], p[1], r_z2))) for p in outer_rect]
    vi1 = [bm_r.verts.new(Vector((p[0], p[1], r_z1))) for p in inner_rect]
    vi2 = [bm_r.verts.new(Vector((p[0], p[1], r_z2))) for p in inner_rect]

    for i in range(4):
        i_next = (i + 1) % 4
        # Outer Face
        bm_r.faces.new([vo1[i], vo1[i_next], vo2[i_next], vo2[i]])
        # Top Face
        bm_r.faces.new([vo2[i], vo2[i_next], vi2[i_next], vi2[i]])
        # Bottom Face
        bm_r.faces.new([vo1[i], vi1[i], vi1[i_next], vo1[i_next]])
        # Inner Face
        bm_r.faces.new([vi1[i], vi2[i], vi2[i_next], vi1[i_next]])

    bm_r.to_mesh(mesh_rim)
    bm_r.free()

    obj_rim = bpy.data.objects.new("Chest_Metal_Rim", mesh_rim)
    coll.objects.link(obj_rim)
    obj_rim.data.materials.append(mat_metal)
    bev_r = obj_rim.modifiers.new("Bevel", type='BEVEL')
    bev_r.width = 0.012
    bev_r.segments = 2
    obj_rim.data.polygons.foreach_set('use_smooth', [True] * len(obj_rim.data.polygons))

    # ========================================================
    # 7. TWO VERTICAL METAL STRAPS
    # ========================================================
    strap_xs = [-0.42, 0.42]
    strap_w = 0.16
    shw = strap_w / 2.0
    strap_t = 0.022

    for s_idx, sx in enumerate(strap_xs):
        mesh_s = bpy.data.meshes.new(f"Chest_Metal_Strap_{s_idx+1}")
        bm_s = bmesh.new()

        # Follow path along Y: Front base vertical -> Lid arch -> Back base vertical
        pts = []
        # Front base vertical
        pts.append((Vector((sx, -hd, Z_base_bot)), Vector((0, -1, 0))))
        pts.append((Vector((sx, -hd, Z_split - 0.04)), Vector((0, -1, 0))))
        pts.append((Vector((sx, -hd - rim_t, Z_split - 0.04)), Vector((0, -1, 0))))
        pts.append((Vector((sx, -hd - rim_t, Z_split + 0.04)), Vector((0, -1, 0))))
        pts.append((Vector((sx, -hd, Z_split + 0.04)), Vector((0, -1, 0))))

        # Arch
        n_sa = 16
        for ia in range(n_sa + 1):
            t = ia / n_sa
            y = -hd + (2 * hd * t)
            z = get_arch_z(y)
            # outward normal along arch
            yn = y / hd
            normal = Vector((0, -2 * yn * 0.4, 1.0)).normalized()
            pts.append((Vector((sx, y, z)), normal))

        # Back base vertical
        pts.append((Vector((sx, hd, Z_split + 0.04)), Vector((0, 1, 0))))
        pts.append((Vector((sx, hd + rim_t, Z_split + 0.04)), Vector((0, 1, 0))))
        pts.append((Vector((sx, hd + rim_t, Z_split - 0.04)), Vector((0, 1, 0))))
        pts.append((Vector((sx, hd, Z_split - 0.04)), Vector((0, 1, 0))))
        pts.append((Vector((sx, hd, Z_base_bot)), Vector((0, 1, 0))))

        # Build ribbon with thickness
        in_verts = []
        out_verts = []
        for p, norm in pts:
            # Inner
            v_il = bm_s.verts.new(Vector((p.x - shw, p.y, p.z)))
            v_ir = bm_s.verts.new(Vector((p.x + shw, p.y, p.z)))
            # Outer
            v_ol = bm_s.verts.new(Vector((p.x - shw, p.y, p.z)) + norm * strap_t)
            v_or = bm_s.verts.new(Vector((p.x + shw, p.y, p.z)) + norm * strap_t)
            in_verts.append((v_il, v_ir))
            out_verts.append((v_ol, v_or))

        for step in range(len(pts) - 1):
            vil1, vir1 = in_verts[step]
            vil2, vir2 = in_verts[step+1]
            vol1, vor1 = out_verts[step]
            vol2, vor2 = out_verts[step+1]

            # Outer face
            bm_s.faces.new([vol1, vol2, vor2, vor1])
            # Left side
            bm_s.faces.new([vil1, vil2, vol2, vol1])
            # Right side
            bm_s.faces.new([vir1, vor1, vor2, vir2])

        # Bottom caps
        bm_s.faces.new([in_verts[0][0], out_verts[0][0], out_verts[0][1], in_verts[0][1]])
        last = len(pts) - 1
        bm_s.faces.new([in_verts[last][0], in_verts[last][1], out_verts[last][1], out_verts[last][0]])

        bm_s.to_mesh(mesh_s)
        bm_s.free()

        obj_s = bpy.data.objects.new(f"Chest_Metal_Strap_{s_idx+1}", mesh_s)
        coll.objects.link(obj_s)
        obj_s.data.materials.append(mat_metal)
        bev_s = obj_s.modifiers.new("Bevel", type='BEVEL')
        bev_s.width = 0.008
        bev_s.segments = 2
        obj_s.data.polygons.foreach_set('use_smooth', [True] * len(obj_s.data.polygons))

    # ========================================================
    # 8. SIDE ARCH METAL RIMS (Left & Right)
    # ========================================================
    for sign, s_name in [(-1, "Left"), (1, "Right")]:
        mesh_side = bpy.data.meshes.new(f"Chest_Metal_Side_{s_name}")
        bm_sd = bmesh.new()

        sx = sign * hw
        trim_thick = 0.028
        trim_w = 0.08

        # Curve points along side arch
        pts_arch = []
        n_side = 14
        for ia in range(n_side + 1):
            t = ia / n_side
            y = -hd + (2 * hd * t)
            z = get_arch_z(y)
            pts_arch.append((y, z))

        # Build an extruded curved border along side edge
        for i in range(len(pts_arch) - 1):
            y1, z1 = pts_arch[i]
            y2, z2 = pts_arch[i+1]

            # Inset inward radially
            y1_in = y1 * (1.0 - (trim_w / hd))
            z1_in = max(Z_split, z1 - trim_w)
            y2_in = y2 * (1.0 - (trim_w / hd))
            z2_in = max(Z_split, z2 - trim_w)

            # 4 outer, 4 inner vertices
            x_out = sx + sign * trim_thick
            x_in  = sx

            vo1 = bm_sd.verts.new(Vector((x_out, y1, z1)))
            vo2 = bm_sd.verts.new(Vector((x_out, y2, z2)))
            voi1 = bm_sd.verts.new(Vector((x_out, y1_in, z1_in)))
            voi2 = bm_sd.verts.new(Vector((x_out, y2_in, z2_in)))

            vi1 = bm_sd.verts.new(Vector((x_in, y1, z1)))
            vi2 = bm_sd.verts.new(Vector((x_in, y2, z2)))
            vii1 = bm_sd.verts.new(Vector((x_in, y1_in, z1_in)))
            vii2 = bm_sd.verts.new(Vector((x_in, y2_in, z2_in)))

            # Face on side
            if sign > 0:
                bm_sd.faces.new([vo1, vo2, voi2, voi1])
                bm_sd.faces.new([vo1, vi1, vi2, vo2])
                bm_sd.faces.new([voi1, voi2, vii2, vii1])
            else:
                bm_sd.faces.new([vo1, voi1, voi2, vo2])
                bm_sd.faces.new([vo1, vo2, vi2, vi1])
                bm_sd.faces.new([voi1, vii1, vii2, voi2])

        bm_sd.to_mesh(mesh_side)
        bm_sd.free()

        obj_side = bpy.data.objects.new(f"Chest_Metal_Side_{s_name}", mesh_side)
        coll.objects.link(obj_side)
        obj_side.data.materials.append(mat_metal)
        bev_sd = obj_side.modifiers.new("Bevel", type='BEVEL')
        bev_sd.width = 0.010
        bev_sd.segments = 2
        obj_side.data.polygons.foreach_set('use_smooth', [True] * len(obj_side.data.polygons))

    # ========================================================
    # 9. FOUR CORNER METAL FEET / BRACKETS
    # ========================================================
    f_size_x = 0.16
    f_size_y = 0.16
    f_height = 0.18
    f_t = 0.035

    for cx, cy, c_name in [
        (-1, -1, "Front_Left"), (1, -1, "Front_Right"),
        (-1,  1, "Back_Left"),  (1,  1, "Back_Right")
    ]:
        mesh_f = bpy.data.meshes.new(f"Chest_Corner_Foot_{c_name}")
        bm_f = bmesh.new()

        px = cx * hw
        py = cy * hd

        # Solid block at corner
        x1 = px - (f_size_x if cx > 0 else -f_t)
        x2 = px + (f_t if cx > 0 else f_size_x)
        y1 = py - (f_size_y if cy > 0 else -f_t)
        y2 = py + (f_t if cy > 0 else f_size_y)
        z1 = 0.0
        z2 = f_height

        bmesh.ops.create_cube(bm_f, size=1.0)
        for v in bm_f.verts:
            v.co.x = (x1 + x2)/2.0 + v.co.x * abs(x2 - x1)
            v.co.y = (y1 + y2)/2.0 + v.co.y * abs(y2 - y1)
            v.co.z = (z1 + z2)/2.0 + v.co.z * abs(z2 - z1)

        bm_f.to_mesh(mesh_f)
        bm_f.free()

        obj_f = bpy.data.objects.new(f"Chest_Corner_Foot_{c_name}", mesh_f)
        coll.objects.link(obj_f)
        obj_f.data.materials.append(mat_metal)
        bev_f = obj_f.modifiers.new("Bevel", type='BEVEL')
        bev_f.width = 0.018
        bev_f.segments = 2
        obj_f.data.polygons.foreach_set('use_smooth', [True] * len(obj_f.data.polygons))

    # ========================================================
    # 10. CENTRAL LOCK PLATE & KEYHOLE
    # ========================================================
    mesh_lock = bpy.data.meshes.new("Chest_Lock_Plate")
    bm_lk = bmesh.new()

    lw = 0.14
    lh = 0.16
    lc = 0.04
    ly = -hd - rim_t - 0.018
    lt = 0.035
    lz = Z_split

    oct_pts = [
        (-lw + lc, lz + lh),
        ( lw - lc, lz + lh),
        ( lw,      lz + lh - lc),
        ( lw,      lz - lh + lc),
        ( lw - lc, lz - lh),
        (-lw + lc, lz - lh),
        (-lw,      lz - lh + lc),
        (-lw,      lz + lh - lc),
    ]

    vf1 = [bm_lk.verts.new(Vector((p[0], ly - lt, p[1]))) for p in oct_pts]
    vf2 = [bm_lk.verts.new(Vector((p[0], ly,      p[1]))) for p in oct_pts]

    bm_lk.faces.new(vf1)
    bm_lk.faces.new(list(reversed(vf2)))
    for i in range(8):
        i2 = (i + 1) % 8
        bm_lk.faces.new([vf1[i], vf1[i2], vf2[i2], vf2[i]])

    bm_lk.to_mesh(mesh_lock)
    bm_lk.free()

    obj_lock = bpy.data.objects.new("Chest_Lock_Plate", mesh_lock)
    coll.objects.link(obj_lock)
    obj_lock.data.materials.append(mat_metal)
    bev_lk = obj_lock.modifiers.new("Bevel", type='BEVEL')
    bev_lk.width = 0.012
    bev_lk.segments = 2
    obj_lock.data.polygons.foreach_set('use_smooth', [True] * len(obj_lock.data.polygons))

    # Keyhole Inset
    mesh_kh = bpy.data.meshes.new("Chest_Keyhole")
    bm_kh = bmesh.new()
    kh_y = ly - lt - 0.005
    # circle top + slot
    r_k = 0.022
    zk = lz + 0.03
    kh_pts = []
    for i in range(8):
        ang = math.pi * i / 7.0
        kh_pts.append(Vector((r_k * math.cos(ang), kh_y, zk + r_k * math.sin(ang))))
    kh_pts.append(Vector((-r_k * 0.45, kh_y, lz - 0.05)))
    kh_pts.append(Vector(( r_k * 0.45, kh_y, lz - 0.05)))
    v_kh = [bm_kh.verts.new(p) for p in kh_pts]
    bm_kh.faces.new(v_kh)
    bm_kh.to_mesh(mesh_kh)
    bm_kh.free()

    obj_kh = bpy.data.objects.new("Chest_Keyhole", mesh_kh)
    coll.objects.link(obj_kh)
    obj_kh.data.materials.append(mat_dark)

    # ========================================================
    # 11. HEXAGONAL BOLTS
    # ========================================================
    mesh_bolt = bpy.data.meshes.new("Chest_Hex_Bolt")
    bm_bt = bmesh.new()
    b_rad = 0.026
    b_len = 0.022
    sides = 6

    b_top = []
    b_bot = []
    for i in range(sides):
        ang = 2.0 * math.pi * i / sides
        x = b_rad * math.cos(ang)
        y = b_rad * math.sin(ang)
        b_top.append(bm_bt.verts.new(Vector((x, y, b_len))))
        b_bot.append(bm_bt.verts.new(Vector((x, y, 0.0))))
    c_top = bm_bt.verts.new(Vector((0.0, 0.0, b_len + 0.007)))

    for i in range(sides):
        i2 = (i + 1) % sides
        bm_bt.faces.new([b_bot[i], b_bot[i2], b_top[i2], b_top[i]])
        bm_bt.faces.new([b_top[i], b_top[i2], c_top])
    bm_bt.faces.new(list(reversed(b_bot)))

    bm_bt.to_mesh(mesh_bolt)
    bm_bt.free()
    mesh_bolt.materials.append(mat_bolt)

    # Exact bolt coordinates from reference image
    bolts = [
        # Front Lid (2 on straps)
        ((-0.42, -hd - 0.02, 0.88), (math.radians(-65), 0, 0)),
        (( 0.42, -hd - 0.02, 0.88), (math.radians(-65), 0, 0)),
        # Front Rim (flanking straps & lock)
        ((-0.42, -hd - rim_t - 0.02, Z_split), (math.radians(-90), 0, 0)),
        (( 0.42, -hd - rim_t - 0.02, Z_split), (math.radians(-90), 0, 0)),
        ((-0.22, -hd - rim_t - 0.015, Z_split), (math.radians(-90), 0, 0)),
        (( 0.22, -hd - rim_t - 0.015, Z_split), (math.radians(-90), 0, 0)),
        ((-0.68, -hd - rim_t - 0.015, Z_split), (math.radians(-90), 0, 0)),
        (( 0.68, -hd - rim_t - 0.015, Z_split), (math.radians(-90), 0, 0)),
        # Front Base (2 on straps)
        ((-0.42, -hd - 0.02, 0.26), (math.radians(-90), 0, 0)),
        (( 0.42, -hd - 0.02, 0.26), (math.radians(-90), 0, 0)),
        # Front Feet (2)
        ((-hw + 0.03, -hd - f_t - 0.01, 0.12), (math.radians(-90), 0, 0)),
        (( hw - 0.03, -hd - f_t - 0.01, 0.12), (math.radians(-90), 0, 0)),

        # Top Arch Apex
        ((-0.42, 0.0, Z_top + 0.02), (0, 0, 0)),
        (( 0.42, 0.0, Z_top + 0.02), (0, 0, 0)),

        # Back Lid
        ((-0.42,  hd + 0.02, 0.88), (math.radians(65), 0, 0)),
        (( 0.42,  hd + 0.02, 0.88), (math.radians(65), 0, 0)),
        # Back Base
        ((-0.42,  hd + 0.02, 0.26), (math.radians(90), 0, 0)),
        (( 0.42,  hd + 0.02, 0.26), (math.radians(90), 0, 0)),

        # Right Side Arch & Rim
        ((hw + trim_thick + 0.01, 0.0, Z_top - 0.02), (0, math.radians(90), 0)),
        ((hw + trim_thick + 0.01, -hd + 0.08, Z_split), (0, math.radians(90), 0)),
        ((hw + trim_thick + 0.01,  hd - 0.08, Z_split), (0, math.radians(90), 0)),
    ]

    for ib, (b_pos, b_rot) in enumerate(bolts):
        ob = bpy.data.objects.new(f"Hex_Bolt_{ib+1}", mesh_bolt)
        ob.location = b_pos
        ob.rotation_euler = b_rot
        coll.objects.link(ob)

    # ========================================================
    # 12. CLEAN STUDIO BACKGROUND & LIGHTING
    # ========================================================
    # Simple flat floor at Z = 0
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0.0))
    obj_fl = bpy.context.active_object
    obj_fl.name = "Studio_Floor"
    mat_fl = bpy.data.materials.new(name="M_Studio_Floor")
    mat_fl.use_nodes = True
    mat_fl.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.92, 0.93, 0.94, 1.0)
    mat_fl.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.95
    obj_fl.data.materials.append(mat_fl)

    # Three-Point Studio Lighting
    # Key Light (Warm, Top-Front-Left)
    key_d = bpy.data.lights.new(name="Key_Light", type='AREA')
    key_d.energy = 450.0
    key_d.size = 2.5
    key_d.color = (1.0, 0.95, 0.88)
    key_o = bpy.data.objects.new("Key_Light", key_d)
    key_o.location = (3.0, -3.2, 3.6)
    key_o.rotation_euler = (math.radians(50), math.radians(10), math.radians(45))
    bpy.context.scene.collection.objects.link(key_o)

    # Fill Light (Cool, Right)
    fill_d = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill_d.energy = 160.0
    fill_d.size = 3.0
    fill_d.color = (0.86, 0.92, 1.0)
    fill_o = bpy.data.objects.new("Fill_Light", fill_d)
    fill_o.location = (-3.5, -2.5, 2.5)
    fill_o.rotation_euler = (math.radians(40), math.radians(-15), math.radians(-55))
    bpy.context.scene.collection.objects.link(fill_o)

    # Rim Light (Backlight for crisp silhouette)
    rim_d = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim_d.energy = 320.0
    rim_d.size = 2.0
    rim_d.color = (1.0, 0.98, 0.95)
    rim_o = bpy.data.objects.new("Rim_Light", rim_d)
    rim_o.location = (-1.5, 3.2, 3.0)
    rim_o.rotation_euler = (math.radians(135), math.radians(15), math.radians(-25))
    bpy.context.scene.collection.objects.link(rim_o)

    # ========================================================
    # 13. CAMERA (Hero 3/4 Perspective View)
    # ========================================================
    cam_d = bpy.data.cameras.new("Hero_Camera")
    cam_d.lens = 85.0
    cam_o = bpy.data.objects.new("Hero_Camera", cam_d)
    cam_o.location = (3.5, -4.2, 2.8)
    bpy.context.scene.collection.objects.link(cam_o)
    bpy.context.scene.camera = cam_o

    # Track to center of chest
    target = bpy.data.objects.new("Cam_Target", None)
    target.location = (0.0, 0.0, 0.55)
    bpy.context.scene.collection.objects.link(target)

    trk = cam_o.constraints.new(type='TRACK_TO')
    trk.target = target
    trk.track_axis = 'TRACK_NEGATIVE_Z'
    trk.up_axis = 'UP_Y'

    # 14. Render Settings
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = r"D:\Blender\AI\chest_render.png"
    scene.render.image_settings.file_format = 'PNG'
    scene.render.engine = 'BLENDER_EEVEE'

    print("CHEST_V2_BUILT_SUCCESS")

create_stylized_chest()
