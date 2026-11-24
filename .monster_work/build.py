import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


OUT = Path(r'D:\Blender\AI\One_Eyed_Monster')
FINAL = OUT / 'One_Eyed_Monster.blend'
TAU = math.tau


def linear(hex_color):
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels) + (1,)


def material(name, color, roughness, coat=0, subsurface=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = linear(color)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    for key, value in {
        'Base Color': mat.diffuse_color, 'Roughness': roughness,
        'Coat Weight': coat, 'Coat Roughness': .18, 'IOR': 1.44,
        'Subsurface Weight': subsurface, 'Subsurface Radius': (.22, .115, .075),
        'Subsurface Scale': .09,
    }.items():
        shader.inputs[key].default_value = value
    return mat


def add_skin_grain(mat):
    tree = mat.node_tree
    noise = tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 115
    noise.inputs['Detail'].default_value = 2
    noise.location = (-570, -150)
    coords = tree.nodes.new('ShaderNodeTexCoord')
    coords.location = (-760, -150)
    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .19
    bump.inputs['Distance'].default_value = .014
    bump.location = (-300, -150)
    tree.links.new(coords.outputs['Object'], noise.inputs['Vector'])
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], tree.nodes['Principled BSDF'].inputs['Normal'])


def collection(scene, name):
    group = bpy.data.collections.new(name)
    scene.collection.children.link(group)
    return group


def mesh_obj(name, vertices, faces, group, materials, material_indices=None):
    data = bpy.data.meshes.new(name + ' | cage')
    data.from_pydata(vertices, [], faces)
    for mat in materials:
        data.materials.append(mat)
    for poly in data.polygons:
        poly.use_smooth = True
        if material_indices:
            poly.material_index = material_indices[poly.index]
    edit = bmesh.new()
    edit.from_mesh(data)
    bmesh.ops.recalc_face_normals(edit, faces=list(edit.faces))
    edit.to_mesh(data)
    edit.free()
    data.update()
    ob = bpy.data.objects.new(name, data)
    group.objects.link(ob)
    return ob


def subdiv(ob, levels=2, render_levels=None):
    mod = ob.modifiers.new('Subdivision surface', 'SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels if render_levels is not None else levels
    return mod


def make_loop(vertices, points):
    first = len(vertices)
    vertices.extend(map(Vector, points))
    return list(range(first, len(vertices)))


def bridge(faces, ring_a, ring_b):
    count = len(ring_a)
    faces.extend((ring_a[i], ring_a[(i + 1) % count], ring_b[(i + 1) % count], ring_b[i])
                 for i in range(count))


def rectangle_perimeter(cols, rows):
    return ([(i, 0) for i in range(cols)] + [(cols, j) for j in range(rows)] +
            [(i, rows) for i in range(cols, 0, -1)] + [(0, j) for j in range(rows, 0, -1)])


def quad_cap(vertices, faces, outline, cols, rows, offset=(0, 0, 0)):
    """Coons patch on an existing closed edge loop, with quad corners."""
    grid = dict(zip(rectangle_perimeter(cols, rows), outline))
    p00, p10, p01, p11 = (vertices[grid[key]] for key in [(0, 0), (cols, 0), (0, rows), (cols, rows)])
    for j in range(1, rows):
        for i in range(1, cols):
            u, v = i / cols, j / rows
            across = vertices[grid[0, j]].lerp(vertices[grid[cols, j]], u)
            along = vertices[grid[i, 0]].lerp(vertices[grid[i, rows]], v)
            bilinear = p00.lerp(p10, u).lerp(p01.lerp(p11, u), v)
            bulge = Vector(offset) * math.sin(math.pi * u) * math.sin(math.pi * v)
            grid[i, j] = len(vertices)
            vertices.append(across + along - bilinear + bulge)
    for j in range(rows):
        for i in range(cols):
            faces.append((grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]))


def swept(name, profiles, group, mat, cage=(6, 6), tilt=False, resolution=2):
    vertices, faces, rings = [], [], []
    count = 2 * sum(cage)
    for k, (center, rx, ry) in enumerate(profiles):
        center = Vector(center)
        if tilt:
            tangent = Vector(profiles[min(k + 1, len(profiles) - 1)][0]) - Vector(profiles[max(k - 1, 0)][0])
            tangent.normalize()
            axis_y = Vector((0, 1, 0))
            axis_x = axis_y.cross(tangent).normalized()
            axis_y = tangent.cross(axis_x).normalized()
        else:
            axis_x, axis_y = Vector((1, 0, 0)), Vector((0, 1, 0))
        ring = make_loop(vertices, (center + rx * math.cos(TAU*i/count) * axis_x +
                                    ry * math.sin(TAU*i/count) * axis_y for i in range(count)))
        if rings:
            bridge(faces, rings[-1], ring)
        rings.append(ring)
    quad_cap(vertices, faces, rings[0], *cage)
    quad_cap(vertices, faces, rings[-1], *cage)
    ob = mesh_obj(name, vertices, faces, group, [mat])
    subdiv(ob, resolution, max(resolution, 2))
    return ob


TORSO = [
    (.711,.235,.174,.105), (.728,.468,.350,.105), (.756,.667,.518,.100),
    (.806,.833,.654,.096), (.887,.969,.753,.085), (.990,1.075,.838,.066),
    (1.095,1.132,.894,.036), (1.216,1.169,.931,.018), (1.344,1.197,.951,.014),
    (1.472,1.216,.958,.017), (1.596,1.226,.959,.021), (1.723,1.228,.956,.029),
    (1.863,1.229,.953,.035), (2.024,1.222,.949,.045), (2.243,1.215,.948,.058),
    (2.470,1.204,.935,.068), (2.687,1.179,.911,.079), (2.873,1.140,.874,.084),
    (3.065,1.080,.815,.094), (3.248,.987,.741,.112), (3.416,.858,.647,.130),
    (3.552,.701,.537,.153), (3.648,.527,.418,.166), (3.715,.340,.288,.181),
    (3.749,.161,.141,.190),
]


def torso_y(x, z):
    for lower, upper in zip(TORSO, TORSO[1:]):
        if lower[0] <= z <= upper[0]:
            t = (z - lower[0]) / (upper[0] - lower[0])
            rx, depth, shift = [a + (b - a) * t for a, b in zip(lower[1:], upper[1:])]
            return shift - depth * math.sqrt(max(.0, 1 - (x / rx) ** 2)) ** .76
    raise ValueError(z)


def make_body(group, skin, mouthmat):
    count = 64
    half, bottom, top = 7, 5, 12
    outer_points, faces, rings = [], [], []
    for row, (z, rx, depth, shift) in enumerate(TORSO):
        ring = {}
        for i in range(-count//2, count//2):
            if bottom < row < top and -half < i < half:
                continue
            a = TAU * i / count
            c = math.cos(a)
            y = shift - depth * math.copysign(abs(c) ** (.76 if c >= 0 else .88), c)
            ring[i] = len(outer_points)
            outer_points.append(Vector((rx * math.sin(a), y, z)))
        rings.append(ring)
    for row in range(len(rings)-1):
        for i in range(-count//2, count//2):
            if bottom <= row < top and -half <= i < half:
                continue
            j = (i + 1 + count//2) % count - count//2
            faces.append((rings[row][i], rings[row][j], rings[row+1][j], rings[row+1][i]))
    quad_cap(outer_points, faces, list(rings[0].values()), 16, 16, (0,0,-.009))
    quad_cap(outer_points, faces, list(rings[-1].values()), 16, 16, (0,0,.015))
    cols, rows = half*2, top-bottom
    perimeter = rectangle_perimeter(cols, rows)
    rim = [rings[bottom + j][i - half] for i, j in perimeter]
    angles = [math.atan2(2*j/rows - 1, 2*i/cols - 1) for i, j in perimeter]
    center = 1.435

    def mouth_point(angle, size, depth):
        c, s = math.cos(angle), math.sin(angle)
        x = size * .650 * c
        z = center + size * ((.230 - .106 * s) * s + .194 * c*c)
        return x, torso_y(x, z) + depth, z

    for size, depth in [(1.13, .001), (1.055, -.014), (1.0, -.008), (.985, .026), (.976, .066)]:
        next_loop = make_loop(outer_points, (mouth_point(a, size, depth) for a in angles))
        bridge(faces, rim, next_loop)
        rim = next_loop

    # The lining meets the lip on an identical edge, then forms the actual recessed cavity.
    lining_points, lining_faces = [], []
    lining_rim = make_loop(lining_points, (outer_points[index] for index in rim))
    for size, depth in [(.974,.084), (.945,.13), (.84,.222), (.68,.302), (.43,.327)]:
        next_loop = make_loop(lining_points, (mouth_point(a, size, depth) for a in angles))
        bridge(lining_faces, lining_rim, next_loop)
        lining_rim = next_loop
    quad_cap(lining_points, lining_faces, lining_rim, cols, rows, (0,.024,0))
    # The sealed inner wall sits behind the independently editable mouth lining.
    for size, depth in [(.978,.107),(1.01,.210),(1.04,.344),(.87,.438),(.43,.471)]:
        rim_extra = make_loop(outer_points, (mouth_point(a, size, depth) for a in angles))
        bridge(faces, rim, rim_extra)
        rim = rim_extra
    quad_cap(outer_points, faces, rim, cols, rows, (0,.015,0))
    body = mesh_obj('Body', outer_points, faces, group, [skin, mouthmat])
    lining = mesh_obj('Mouth | cavity', lining_points, lining_faces, group, [mouthmat])
    subdiv(body, 2, 2)
    subdiv(lining, 2, 2)
    solid = lining.modifiers.new('Mouth lining thickness', 'SOLIDIFY')
    solid.thickness = .011
    solid.offset = 0
    body['Topology'] = '64-point cross-sections with five mouth support loops and quad grid caps.'
    return body, lining


EYE = (0, -.781, 2.526)
EX, EY, EZ = .814, .482, .818
IRIS_R = .485
IRIS_Z = 2.528


def eye_bias(z):
    h = (z - EYE[2]) / EZ
    return .047 + .075*h*h + .030*max(0,h)**2


def eyeball_surface(x, z):
    d = (x / EX) ** 2 + ((z - EYE[2]) / EZ) ** 2
    return EYE[1] - EY * math.sqrt(max(0, 1 - d)) + eye_bias(z)


def iris_surface(x, z):
    r = math.hypot(x, z - IRIS_Z) / IRIS_R
    return eyeball_surface(x, z) - .001 - .037 * max(0, 1 - r*r) ** .8


def eyeball(group, mat):
    vertices, faces = [], []
    last = None
    for i in range(1, 28):
        p = math.pi * i / 28
        z = EYE[2]+EZ*math.cos(p)
        loop = make_loop(vertices, ((EX*math.sin(p)*math.sin(t*TAU/48),
                                     EYE[1]-EY*math.sin(p)*math.cos(t*TAU/48)+eye_bias(z), z) for t in range(48)))
        if last is None:
            quad_cap(vertices, faces, loop, 12, 12, (0,0,.004))
        else:
            bridge(faces, last, loop)
        last = loop
    quad_cap(vertices, faces, last, 12, 12, (0,0,-.004))
    obj = mesh_obj('Eye | sclera', vertices, faces, group, [mat])
    subdiv(obj, 1, 2)
    return obj


def lens_disc(name, cx, cz, rx, rz, group, materials, surface, bands):
    vertices, faces, indices = [], [], []
    previous = None
    for r, material_id in bands:
        ring = []
        for i in range(48):
            angle = TAU*i/48
            x, z = cx + rx*r*math.cos(angle), cz + rz*r*math.sin(angle)
            ring.append((x, surface(x, z), z))
        current = make_loop(vertices, ring)
        first = len(faces)
        if previous is None:
            quad_cap(vertices, faces, current, 12, 12, (0,-.0005,0))
        else:
            bridge(faces, previous, current)
        indices.extend([material_id] * (len(faces) - first))
        previous = current
    back = make_loop(vertices, ((vertices[i].x, vertices[i].y+.014, vertices[i].z) for i in previous))
    bridge(faces, previous, back)
    indices.extend([bands[-1][1]] * 48)
    first = len(faces)
    quad_cap(vertices, faces, back, 12, 12, (0,-.040,0))
    indices.extend([bands[-1][1]] * (len(faces) - first))
    obj = mesh_obj(name, vertices, faces, group, materials, indices)
    subdiv(obj, 1, 1)
    return obj


def lids(name, group, mat, upper):
    side = 1 if upper else -1
    closed = -.108 if upper else -.099

    def samples(blink):
        end = ((1.493 if upper else -1.503) * (1 - blink) + closed * blink)
        points = []
        for j in range(11):
            v = j/10
            phi = side * 2.10 * (1-v) + end*v
            for i in range(41):
                angle = .017 + (math.pi-.034)*i/40
                sa = math.sin(angle)
                x = (EX - .020 + .032*blink) * math.cos(angle)
                z = EYE[2] + (EZ-.024+.042*blink) * sa * math.sin(phi)
                y = EYE[1] - (EY+.014) * sa * math.cos(phi) + eye_bias(z) + .067 * (1-blink)**2
                if math.cos(phi) > 0:
                    ratio = math.hypot(x, z-IRIS_Z) / (IRIS_R+.028)
                    y -= .052 * max(0, 1-ratio*ratio) ** 1.15
                points.append((x,y,z))
        return points

    faces = [(j*41+i, j*41+i+1, (j+1)*41+i+1, (j+1)*41+i)
             for j in range(10) for i in range(40)]
    if upper:
        faces = [tuple(reversed(face)) for face in faces]
    obj = mesh_obj(name, samples(0), faces, group, [mat])
    obj.shape_key_add(name='Basis')
    for step, amount in enumerate((.28,.53,.77,1), 1):
        shape = obj.shape_key_add(name=f'Blink {step}')
        shape.data.foreach_set('co', [c for p in samples(amount) for c in p])
    subdiv(obj, 1, 1)
    solid = obj.modifiers.new('Lid thickness', 'SOLIDIFY')
    solid.thickness = .018
    solid.offset = 0
    return obj


def anatomy(group, mats):
    skin, hornmat, mouthmat, toothmat, tongue_mat, white, iris, limbal, pupil = mats
    body, cavity = make_body(group, skin, mouthmat)
    horn = swept('Horns | mirrored pair', [
        ((.883,.031,3.134),.111,.110), ((.955,.036,3.171),.192,.168),
        ((1.047,.047,3.230),.248,.230), ((1.147,.058,3.331),.257,.255),
        ((1.205,.070,3.449),.244,.240), ((1.224,.079,3.558),.205,.207),
        ((1.208,.086,3.668),.155,.169), ((1.167,.089,3.755),.119,.135),
        ((1.110,.087,3.817),.081,.096), ((1.054,.081,3.842),.055,.065),
        ((1.018,.078,3.837),.030,.034), ((1.006,.078,3.822),.012,.015),
    ], group, hornmat, tilt=True)
    mirror = horn.modifiers.new('Bilateral horns', 'MIRROR')
    horn.modifiers.move(len(horn.modifiers) - 1, 0)
    arms, feet, teeth = [], [], []
    for flip, side in [(1,'L'),(-1,'R')]:
        arms.append(swept(f'Arm.{side}', [((flip*x,y,z),rx,ry) for x,y,z,rx,ry in [
            (1.358,.006,.531,.047,.058), (1.356,.005,.562,.105,.117),
            (1.359,.008,.622,.165,.174), (1.361,.009,.721,.222,.216),
            (1.355,.016,.845,.247,.236), (1.333,.029,.999,.250,.250),
            (1.290,.051,1.173,.235,.250), (1.245,.081,1.356,.217,.237),
            (1.194,.105,1.526,.201,.207), (1.138,.120,1.680,.178,.173),
            (1.099,.124,1.826,.145,.137), (1.070,.126,1.933,.098,.091),
            (1.057,.126,1.991,.043,.041), (1.052,.126,2.005,.019,.017),
        ]], group, skin, tilt=True))
        feet.append(swept(f'Foot.{side}', [((flip*x,y,z),rx,ry) for x,y,z,rx,ry in [
            (.502,-.083,.001,.257,.298), (.502,-.072,.013,.348,.391),
            (.502,-.067,.048,.392,.436), (.500,-.059,.087,.410,.448),
            (.496,-.045,.158,.401,.441), (.490,-.016,.268,.374,.415),
            (.485,.019,.414,.349,.374), (.478,.048,.581,.329,.340),
            (.474,.066,.759,.326,.328), (.473,.077,.902,.298,.284),
            (.470,.077,.940,.198,.204),
        ]], group, skin))
        teeth.append(swept(f'Tooth.{side}', [((flip*x,y,z),rx,ry) for x,y,z,rx,ry in [
            (.344,-.847,1.487,.033,.031), (.346,-.850,1.497,.065,.053),
            (.348,-.853,1.532,.109,.076), (.350,-.850,1.589,.133,.091),
            (.352,-.840,1.653,.133,.093), (.353,-.828,1.684,.115,.086),
            (.354,-.818,1.702,.068,.050),
        ]], group, toothmat, cage=(3,4), tilt=True))
        for vertex in teeth[-1].data.vertices:
            vertex.co.y += .046 + .51 * max(0, vertex.co.z-1.526)
        teeth[-1]['Topology'] = '3 x 4 quad grid on each end cap, with continuous supporting edge loops.'
    tongue = swept('Tongue', [((0,y,z),rx,ry) for y,z,rx,ry in [
        (-.724,1.076,.186,.071), (-.737,1.099,.292,.140),
        (-.733,1.143,.382,.192), (-.719,1.192,.369,.195),
        (-.710,1.242,.309,.161), (-.702,1.279,.208,.117),
        (-.696,1.293,.110,.068),
    ]], group, tongue_mat, cage=(8,8))
    for vertex in tongue.data.vertices:
        x,y,z = vertex.co
        vertex.co.z -= .025 * math.exp(-(x/.085)**2) * max(0, (z-1.202)/.095)
    eye = eyeball(group, white)
    iris_obj = lens_disc('Eye | iris', 0, IRIS_Z, IRIS_R, .499, group, [iris, limbal], iris_surface,
                         [(.12,0),(.26,0),(.43,0),(.62,0),(.78,0),(.88,0),(.934,0),(.974,1),(1.002,1)])
    pupil_obj = lens_disc('Eye | pupil', -.006, IRIS_Z+.072, .400, .401, group, [pupil],
                          lambda x,z: iris_surface(x,z)-.0044,
                          [(.13,0),(.27,0),(.44,0),(.61,0),(.76,0),(.88,0),(.96,0),(1,0)])
    eyelids = [lids('Eyelid | upper',group,skin,True), lids('Eyelid | lower',group,skin,False)]
    return body, cavity, horn, teeth, tongue, eye, iris_obj, pupil_obj, eyelids, arms, feet


def bind(obj, rig, bone, weight_field=None):
    obj.parent = rig
    mod = obj.modifiers.new('Character deformation', 'ARMATURE')
    mod.object = rig
    mod.use_deform_preserve_volume = True
    # Symmetry stays first so the mirrored horn inherits its vertex weights.
    obj.modifiers.move(len(obj.modifiers)-1, int(obj.modifiers[0].type == 'MIRROR'))
    vg = obj.vertex_groups.new(name=bone)
    if weight_field is None:
        vg.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
        return
    support = obj.vertex_groups.new(name='Body' if 'Arm.' in bone else 'Root')
    for v in obj.data.vertices:
        weight = weight_field(v.co)
        vg.add([v.index], weight, 'REPLACE')
        support.add([v.index], 1-weight, 'REPLACE')


def stash(owner, name, start):
    animation = owner.animation_data
    action, slot = animation.action, animation.action_slot
    action.name = name
    action.use_fake_user = True
    track = animation.nla_tracks.new()
    track.name = name
    strip = track.strips.new(name, start, action)
    strip.action_slot = slot
    strip.extrapolation = 'NOTHING'
    animation.action = None


def curves_of(owner):
    anim = owner.animation_data
    return anim.action.layers[0].strips[0].channelbag(anim.action_slot).fcurves


def rig_and_animate(scene, group, parts):
    body, cavity, horn, teeth, tongue, eye, iris, pupil, eyelids, arms, feet = parts
    data = bpy.data.armatures.new('Monster skeleton')
    rig = bpy.data.objects.new('Monster Rig', data)
    group.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    specs = [('Root', (0,0,0), (0,0,.40), None),
             ('Body', (0,0,.70), (0,0,2.32), 'Root'),
             ('Eye', EYE, (0,-1.38,EYE[2]), 'Body')]
    for sign, side in [(1,'L'), (-1,'R')]:
        specs.extend([(f'Arm.{side}', (sign*1.07,.12,1.91), (sign*1.35,.015,.65), 'Body'),
                      (f'Foot.{side}', (sign*.48,.04,.71), (sign*.50,-.08,.10), 'Root')])
    for name, head, tail, parent in specs:
        bone = data.edit_bones.new(name)
        bone.head, bone.tail = head, tail
        if parent:
            bone.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    data.display_type = 'STICK'
    for bone in rig.pose.bones:
        bone.rotation_mode = 'XYZ'
    for obj in [body, cavity, horn, *teeth, tongue, *eyelids]:
        bind(obj, rig, 'Body')
    for obj in [eye, iris, pupil]:
        bind(obj, rig, 'Eye')
    for suffix, arm, foot in zip(['L','R'], arms, feet):
        bind(arm, rig, f'Arm.{suffix}', lambda p: min(1,max(0,(1.94-p.z)/.50)))
        bind(foot, rig, f'Foot.{suffix}', lambda p: min(1,max(0,(p.z-.23)/.29)))
    root, torso = rig.pose.bones['Root'], rig.pose.bones['Body']
    # The bones point up in world Z, so local Y is elevation / turntable yaw.
    for f, rise, squeeze, arm_a, arm_b in [
        (1,0,1,0,0),(8,-.040,.975,-5,3),(15,.103,1.026,10,-6),
        (23,.028,1.01,5,-3),(30,0,1,-1,1),(38,-.036,.977,-3,5),
        (45,.093,1.022,7,-10),(53,.024,1.008,4,-5),(61,0,1,0,1),
        (68,-.024,.986,-2,2),(73,0,1,0,0),
    ]:
        torso.location.y = rise
        torso.scale = (1-(squeeze-1)*.56,squeeze,1-(squeeze-1)*.56)
        torso.keyframe_insert(data_path='location', frame=f, group='Body')
        torso.keyframe_insert(data_path='scale', frame=f, group='Body')
        for suffix, swing in [('L',arm_a),('R',arm_b)]:
            bone = rig.pose.bones[f'Arm.{suffix}']
            bone.rotation_euler.x = math.radians(swing*.55)
            bone.rotation_euler.z = math.radians(swing)
            bone.keyframe_insert(data_path='rotation_euler', frame=f, group=bone.name)
            foot = rig.pose.bones[f'Foot.{suffix}']
            foot.location.y = -rise*.55
            foot.keyframe_insert(data_path='location', frame=f, group=foot.name)
    stash(rig, 'Idle', 1)

    for lid in eyelids:
        keys = lid.data.shape_keys
        poses = {1:0, 19:0, 20:1, 21:2, 22:3, 23:4, 24:4, 25:3, 26:2, 27:1, 28:0,
                 53:0, 54:1, 55:2, 56:3, 57:4, 58:3, 59:2, 60:1, 61:0, 73:0}
        for frame, pose in poses.items():
            for index, key in enumerate(keys.key_blocks[1:], 1):
                key.value = int(index == pose)
                key.keyframe_insert(data_path='value', frame=frame)
        for curve in curves_of(keys):
            for point in curve.keyframe_points:
                point.interpolation = 'LINEAR'
        stash(keys, 'Idle', 1)

    for f, angle in [(97,0),(133,90),(169,180),(205,270),(241,360)]:
        root.rotation_euler.y = math.radians(angle)
        root.keyframe_insert(data_path='rotation_euler', frame=f, group='Root')
    for curve in curves_of(rig):
        for point in curve.keyframe_points:
            point.interpolation = 'LINEAR'
    stash(rig, 'Turntable', 97)
    root.rotation_euler.y = 0
    for frame, label in [(1,'IDLE'),(23,'Blink'),(73,'Idle ends'),(97,'TURNTABLE 0°'),
                         (133,'90°'),(169,'180°'),(205,'270°'),(241,'360°')]:
        scene.timeline_markers.new(label, frame=frame)
    scene.frame_start = 1
    scene.frame_end = 241
    scene.render.fps = 24
    scene.frame_set(1)
    return rig


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio(scene, group):
    stage = material('Studio | warm sand', 'F2D5C3', .87)
    stage.cycles.emission_sampling = 'NONE'
    shader = stage.node_tree.nodes['Principled BSDF']
    shader.inputs['Emission Color'].default_value = stage.diffuse_color
    shader.inputs['Emission Strength'].default_value = .19
    vertices, faces = [], []
    rings = []
    profile = [(12.4,0),(13.4,0)]
    for index in range(1, 15):
        angle = math.pi*index/28
        profile.append((13.4 + 6*math.sin(angle),6 - 6*math.cos(angle)))
    profile.extend([(19.4,8), (19.4,16)])
    for radius, height in profile:
        ring = make_loop(vertices, ((radius*math.cos(TAU*i/128), radius*math.sin(TAU*i/128), height)
                                    for i in range(128)))
        if rings:
            bridge(faces, rings[-1], ring)
        rings.append(ring)
    floor = [(13.401*math.cos(TAU*i/128),13.401*math.sin(TAU*i/128),0) for i in range(128)]
    mesh_obj('Studio ground', floor, [tuple(range(len(floor)))], group, [stage])
    wall = mesh_obj('Studio cyclorama', vertices, faces, group, [stage])
    wall.visible_diffuse = False
    wall.visible_glossy = False
    wall.visible_shadow = False
    scene.world = bpy.data.worlds.new('Studio ambience')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (.69,.77,.82,1)
    bg.inputs['Strength'].default_value = .18
    for name, position, power, color, shape, size, target in [
        ('Key Light',(-3.95,-4.55,6.05),595,(1,.95,.89),'DISK',3.45,(0,0,1.88)),
        ('Fill Light',(4.45,-3.05,3.75),202,(.83,.95,1),'DISK',5.0,(0,0,1.65)),
        ('Rim Light',(1.55,3.85,6.0),435,(1,.89,.80),'DISK',4.50,(0,0,2.1)),
    ]:
        light = bpy.data.lights.new(name,'AREA')
        light.energy, light.color, light.shape, light.size = power, color, shape, size
        ob = bpy.data.objects.new(name,light)
        group.objects.link(ob)
        ob.location = position
        point_at(ob,target)

    def camera(name, location, target, orthographic):
        camera_data = bpy.data.cameras.new(name)
        if orthographic:
            camera_data.type = 'ORTHO'
            camera_data.ortho_scale = 8.19
        else:
            camera_data.lens = 50.5
        ob = bpy.data.objects.new(name,camera_data)
        group.objects.link(ob)
        ob.location = location
        point_at(ob,target)
        return ob

    camera('Front',(0,-11,2.14),(0,0,1.93),True)
    camera('Side',(11,0,2.14),(0,0,1.93),True)
    camera('Back',(0,11,2.14),(0,0,1.93),True)
    camera('Opposite side',(-11,0,2.14),(0,0,1.93),True)
    scene.camera = camera('Perspective 3-4',(4.05,-10.26,3.05),(0,-.04,1.94),False)
    camera('Turntable Camera',(0,-10.40,3.04),(0,0,1.94),False)


def configure(scene):
    scene.unit_settings.system = 'METRIC'
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 32
    scene.cycles.adaptive_threshold = .034
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 5
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 3
    scene.cycles.transmission_bounces = 2
    scene.cycles.transparent_max_bounces = 4
    scene.render.resolution_x, scene.render.resolution_y = 3840,2160
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.filepath = '//Perspective_3-4.png'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = .27


def build():
    old_scene = bpy.context.scene
    factory_scene = old_scene.name == 'Scene' and set(old_scene.objects.keys()) == {'Cube','Camera','Light'}
    old_project = bpy.data.scenes.get('One-Eyed Monster')
    scene = bpy.data.scenes.new('One-Eyed Monster / build')
    bpy.context.window.scene = scene
    if old_project:
        old_objects = list(old_project.objects)
        old_collections = list(old_project.collection.children)
        previous_actions = set()
        for obj in old_objects:
            owners = [obj] + ([obj.data.shape_keys] if obj.type == 'MESH' and obj.data.shape_keys else [])
            for owner in owners:
                if owner.animation_data:
                    previous_actions.update(strip.action for track in owner.animation_data.nla_tracks for strip in track.strips)
        bpy.data.scenes.remove(old_project)
        for obj in old_objects:
            if all(group.users <= 1 for group in obj.users_collection):
                bpy.data.objects.remove(obj, do_unlink=True)
        for group in old_collections:
            if group.users == 0:
                bpy.data.collections.remove(group)
        for action in previous_actions:
            if action and action.users <= int(action.use_fake_user):
                action.use_fake_user = False
        # Earlier passes kept unused editorial copies of the same named project actions.
        for action in bpy.data.actions:
            if action.name.split('.')[0] in {'Idle', 'Turntable'} and action.users == int(action.use_fake_user):
                action.use_fake_user = False
        bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)
    elif factory_scene or len(old_scene.objects) == 0:
        bpy.data.scenes.remove(old_scene)
        bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)
    scene.name = 'One-Eyed Monster'
    char = collection(scene,'01 • CHARACTER')
    setup = collection(scene,'02 • STUDIO')
    skin = material('Skin | turquoise satin', '37B9BF', .48, .075, .035)
    add_skin_grain(skin)
    mats = (skin, material('Horns | warm coral','FC4A2E',.41,.12,.04),
            material('Mouth | oxblood','381009',.58,.04,.025),
            material('Teeth | ivory','FFF1D8',.32,.13,.07),
            material('Tongue | warm rose','FA514B',.37,.18,.075),
            material('Sclera | warm porcelain','FFF2E4',.31,.18,.045),
            material('Iris | umber','5B3C30',.19,.11),
            material('Iris | limbal edge','34231F',.22,.12),
            material('Pupil | obsidian','100A08',.17,.17))
    parts = anatomy(char,mats)
    rig = rig_and_animate(scene,char,parts)
    studio(scene,setup)
    configure(scene)
    scene.frame_set(1)
    rig.select_set(False)
    bpy.context.view_layer.objects.active = parts[0]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.shading.type = 'SOLID'
                space.shading.color_type = 'MATERIAL'
                space.shading.light = 'STUDIO'
                space.shading.show_cavity = True
                space.overlay.show_overlays = False
                space.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()
                space.region_3d.view_location = (0,-.08,1.93)
                space.region_3d.view_distance = 8.1
                space.region_3d.view_perspective = 'PERSP'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(FINAL))
    print('SAVED', FINAL, 'OBJECTS', len(scene.objects))


build()
