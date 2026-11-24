import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


scene = bpy.context.scene
turntable = bpy.data.objects['Turntable Camera']
turntable.data.lens = 46.5
character = bpy.data.collections['01 • CHARACTER']
mesh_objects = [obj for obj in character.all_objects if obj.type == 'MESH']
for camera, interval in [(turntable, range(97,242,6)), (bpy.data.objects['Perspective 3-4'], range(1,74,4))]:
    min_y, max_y = 1, 0
    for frame in interval:
        scene.frame_set(frame)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for ob in mesh_objects:
            evaluated = ob.evaluated_get(depsgraph)
            matrix = evaluated.matrix_world
            for corner in evaluated.bound_box:
                y = world_to_camera_view(scene, camera, matrix @ Vector(corner)).y
                min_y, max_y = min(min_y,y), max(max_y,y)
    print(camera.name, 'projected bounds', round(min_y,3), round(max_y,3))
scene.frame_set(1)
preferences = bpy.context.preferences.filepaths
save_version = preferences.save_version
try:
    preferences.save_version = 0
    bpy.ops.wm.save_mainfile()
finally:
    preferences.save_version = save_version
