import argparse
import json
import os
import struct
import sys
import time
from pathlib import Path

import bmesh
import bpy


BASE = Path(r'D:\Blender\AI')
OUT = BASE / 'One_Eyed_Monster'
WORK = BASE / '.monster_work'
scene = bpy.context.scene
character = bpy.data.collections.get('01 • CHARACTER')


def gpu_setup():
    if os.environ.get('MONSTER_CPU'):
        scene.cycles.device = 'CPU'
        return
    prefs = bpy.context.preferences.addons['cycles'].preferences
    device_type = os.environ.get('MONSTER_GPU', 'OPTIX')
    prefs.compute_device_type = device_type
    prefs.refresh_devices()
    enabled = [d for d in prefs.devices if d.type == device_type]
    for device in prefs.devices:
        device.use = device in enabled
    scene.cycles.device = 'GPU' if enabled else 'CPU'
    scene.cycles.denoising_use_gpu = bool(enabled) and not os.environ.get('MONSTER_DENOISE_CPU')
    print('RENDER DEVICE', [(d.name,d.type) for d in enabled], flush=True)


def flat_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (*color,1)
    shader.inputs['Roughness'].default_value = .49
    return mat


def clay_style():
    mat = flat_material('Clay | neutral plaster', (.47,.46,.445))
    for obj in character.all_objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                slot.material = mat


def wire_style():
    clay = flat_material('Wireframe | clay', (.55,.57,.59))
    wire = flat_material('Wireframe | slate ink', (.028,.061,.084))
    for obj in character.all_objects:
        if obj.type != 'MESH':
            continue
        for mod in list(obj.modifiers):
            if mod.type == 'SUBSURF':
                obj.modifiers.remove(mod)
        obj.data.materials.clear()
        obj.data.materials.append(clay)
        obj.data.materials.append(wire)
        for face in obj.data.polygons:
            face.material_index = 0
        mod = obj.modifiers.new('Control cage lines', 'WIREFRAME')
        mod.thickness = .0045
        mod.offset = 1
        mod.use_replace = False
        mod.use_boundary = True
        mod.material_offset = 1


def render_png(name, camera, folder, frame=1, style=None):
    scene.camera = bpy.data.objects[camera]
    scene.frame_set(frame)
    scene.render.filepath = str(folder / (name + '.png'))
    if style:
        style()
    t0 = time.monotonic()
    bpy.ops.render.render(write_still=True)
    print('RENDERED', name, round(time.monotonic()-t0,2), 'seconds', flush=True)


def render_video(name, camera, start, end):
    scene.camera = bpy.data.objects[camera]
    scene.frame_start, scene.frame_end = start, end
    directory = Path(os.environ.get('MONSTER_VIDEO_DIR', str(OUT)))
    scene.render.filepath = str(directory / name)
    scene.render.image_settings.media_type = 'VIDEO'
    ffmpeg = scene.render.ffmpeg
    ffmpeg.format = 'MPEG4'
    ffmpeg.codec = 'H264'
    ffmpeg.constant_rate_factor = 'HIGH'
    ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.use_file_extension = True
    scene.render.use_persistent_data = name != 'Idle'
    if name == 'Idle':
        scene.cycles.denoising_use_gpu = False
    bpy.ops.render.render(animation=True)
    for file in directory.glob(name + '*.mp4'):
        expected = directory / (name + '.mp4')
        if file != expected:
            file.replace(expected)


def fast_integrator():
    scene.cycles.adaptive_threshold = .18
    scene.cycles.adaptive_min_samples = 2
    scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    scene.cycles.denoising_prefilter = 'FAST'
    scene.cycles.glossy_bounces = 1
    scene.cycles.max_bounces = 3
    scene.cycles.sample_clamp_indirect = 3
    scene.cycles.use_animated_seed = False
    for mat in bpy.data.materials:
        if mat.node_tree is None:
            continue
        shader = mat.node_tree.nodes.get('Principled BSDF')
        if shader is None:
            continue
        shader.inputs['Subsurface Weight'].default_value = 0
        for link in list(shader.inputs['Normal'].links):
            mat.node_tree.links.remove(link)


def animation_quality(camera):
    scene.camera = bpy.data.objects[camera]
    scene.cycles.samples = int(os.environ.get('MONSTER_ANIM_SAMPLES', '4'))
    fast_integrator()
    scene.cycles.use_adaptive_sampling = False
    for obj in character.all_objects:
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF':
                mod.render_levels = min(mod.render_levels, 1)


def animation_crop(camera, tag):
    # Render the empty studio once at full native resolution and reuse its outer portion.
    render = scene.render
    scene.camera = bpy.data.objects[camera]
    path = WORK / f'{tag}_studio.exr'
    if not path.exists():
        actor_objects = list(character.all_objects)
        for obj in actor_objects:
            obj.hide_render = True
        old_samples = scene.cycles.samples
        scene.cycles.samples = 12
        render.image_settings.file_format = 'OPEN_EXR'
        render.image_settings.color_depth = '16'
        render.image_settings.color_mode = 'RGB'
        render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        for obj in actor_objects:
            obj.hide_render = False
        scene.cycles.samples = old_samples
    render.use_border = True
    render.use_crop_to_border = False
    render.border_min_x, render.border_max_x = .246, .754
    render.border_min_y, render.border_max_y = .0, 1.0
    render.film_transparent = True
    tree = bpy.data.node_groups.new('Animation | full UHD composite', 'CompositorNodeTree')
    scene.compositing_node_group = tree
    tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    out = tree.nodes.new('NodeGroupOutput')
    over = tree.nodes.new('CompositorNodeAlphaOver')
    layers = tree.nodes.new('CompositorNodeRLayers')
    image = tree.nodes.new('CompositorNodeImage')
    image.image = bpy.data.images.load(str(path), check_existing=True)
    print('COMPOSITOR INPUTS', [i.name for i in over.inputs], flush=True)
    tree.links.new(image.outputs['Image'], over.inputs['Background'])
    tree.links.new(layers.outputs['Image'], over.inputs['Foreground'])
    tree.links.new(over.outputs['Image'], out.inputs['Image'])
    render.image_settings.file_format = 'PNG'
    render.image_settings.color_depth = '8'
    render.image_settings.color_mode = 'RGB'


def retime(name, rate):
    rig = bpy.data.objects['Monster Rig']
    owners = [rig] + [ob.data.shape_keys for ob in character.all_objects
                        if ob.type == 'MESH' and ob.data.shape_keys]
    for owner in owners:
        track = owner.animation_data.nla_tracks.get(name)
        if track:
            track.strips[0].scale = rate / 24
    scene.render.fps = rate


def export_glb():
    scene.frame_set(1)
    for obj in bpy.context.view_layer.objects:
        obj.select_set(obj.name in character.all_objects)
    bpy.context.view_layer.objects.active = bpy.data.objects['Monster Rig']
    path = OUT / 'One_Eyed_Monster.glb'
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True,
                              export_apply=True, export_animation_mode='NLA_TRACKS',
                              export_anim_slide_to_zero=True, export_optimize_animation_size=True,
                              export_morph=True, export_morph_animation=True)
    with path.open('rb') as glb:
        _, version, total = struct.unpack('<4sII', glb.read(12))
        size, kind = struct.unpack('<I4s', glb.read(8))
        assert version == 2 and total == path.stat().st_size and kind == b'JSON'
        content = json.loads(glb.read(size))
    print('GLB', len(content['meshes']), 'meshes', len(content['skins']), 'skins',
          [(anim.get('name'), len(anim['channels'])) for anim in content['animations']], flush=True)


def inspect():
    summary = []
    for obj in character.all_objects:
        if obj.type != 'MESH':
            continue
        mesh = bmesh.new()
        mesh.from_mesh(obj.data)
        summary.append(dict(name=obj.name, faces=len(mesh.faces),
                            quads=sum(len(face.verts)==4 for face in mesh.faces),
                            boundary=sum(edge.is_boundary for edge in mesh.edges),
                            non_manifold=sum(not edge.is_manifold and not edge.is_boundary for edge in mesh.edges),
                            loose=sum(edge.is_wire for edge in mesh.edges),
                            degenerate=sum(face.calc_area() < 1e-10 for face in mesh.faces)))
        mesh.free()
    rig = bpy.data.objects['Monster Rig']
    poses = []
    for frame in [1,15,23,60,73,97,133,169,205,241]:
        scene.frame_set(frame)
        poses.append(dict(frame=frame, rise=round(rig.pose.bones['Body'].location.y,3),
                          yaw=round(rig.pose.bones['Root'].rotation_euler.y,3),
                          blink=[round(key.value,3) for key in bpy.data.objects['Eyelid | upper'].data.shape_keys.key_blocks[1:]]))
    print('VALIDATION', json.dumps(dict(meshes=summary, poses=poses), ensure_ascii=True), flush=True)


parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['preview','quick','stagecheck','bench','regiontest','beauty','clay','wire','idle','turntable','export','inspect'])
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
if args.mode == 'export':
    export_glb()
    raise SystemExit
if args.mode == 'inspect':
    inspect()
    raise SystemExit
gpu_setup()
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.compression = 15
if args.mode in {'beauty','clay','wire'}:
    fast_integrator()
    scene.cycles.samples = int(os.environ.get('MONSTER_STILL_SAMPLES', '8'))
    scene.cycles.adaptive_threshold = .075
if args.mode == 'preview':
    scene.render.resolution_percentage = 29
    scene.cycles.samples = 14
    scene.render.use_persistent_data = True
    for name in ['Front','Side','Back','Perspective 3-4']:
        render_png('preview_' + name.replace(' ', '_'), name, WORK)
    render_png('preview_blink', 'Front', WORK, 23)
elif args.mode == 'quick':
    scene.render.resolution_percentage = 28
    scene.cycles.samples = 9
    render_png('quick_hero', 'Perspective 3-4', WORK)
    render_png('quick_blink', 'Front', WORK, 23)
elif args.mode == 'stagecheck':
    fast_integrator()
    scene.render.resolution_percentage = 18
    scene.cycles.samples = 5
    render_png('seamless_stage', 'Front', WORK)
elif args.mode == 'bench':
    animation_quality('Perspective 3-4')
    scene.render.use_persistent_data = True
    for frame in (1,2):
        render_png(f'benchmark_{frame}', 'Perspective 3-4', WORK, frame)
elif args.mode == 'regiontest':
    animation_quality('Perspective 3-4')
    animation_crop('Perspective 3-4', 'Idle')
    scene.render.use_persistent_data = True
    render_png('regiontest', 'Perspective 3-4', WORK, 16)
elif args.mode == 'beauty':
    scene.render.use_persistent_data = True
    names = set(os.environ.get('MONSTER_STILL_VIEWS', '').split(',')) - {''}
    directory = Path(os.environ.get('MONSTER_STILL_DIR', str(OUT)))
    for name, camera in [('Front','Front'),('Side','Side'),('Back','Back'),
                         ('Perspective_3-4','Perspective 3-4'),('Side_Opposite','Opposite side')]:
        if not names or name in names:
            render_png(name, camera, directory)
elif args.mode == 'clay':
    render_png('Clay', 'Perspective 3-4', OUT, style=clay_style)
elif args.mode == 'wire':
    render_png('Wireframe', 'Perspective 3-4', OUT, style=wire_style)
else:
    rate = int(os.environ.get('MONSTER_ANIM_FPS', '12'))
    scene.render.resolution_percentage = int(os.environ.get('MONSTER_VIDEO_PERCENT', '100'))
    if args.mode == 'idle':
        camera = 'Idle Camera' if bpy.data.objects.get('Idle Camera') else 'Perspective 3-4'
        animation_quality(camera)
        if os.environ.get('MONSTER_CROP'):
            animation_crop(camera, 'Idle')
        retime('Idle', rate)
        job_name = os.environ.get('MONSTER_VIDEO_NAME', 'Idle')
        render_video(job_name, camera, 1, int(os.environ.get('MONSTER_VIDEO_END', 3*rate)))
    else:
        animation_quality('Turntable Camera')
        if os.environ.get('MONSTER_CROP'):
            animation_crop('Turntable Camera', 'Turntable')
        retime('Turntable', rate)
        job_name = os.environ.get('MONSTER_VIDEO_NAME', 'Turntable')
        render_video(job_name, 'Turntable Camera', 97, int(os.environ.get('MONSTER_VIDEO_END', 97+6*rate)))
