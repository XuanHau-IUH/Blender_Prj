import bpy
from mathutils import Vector

for name in ('Front', 'Side', 'Back', 'Opposite side'):
    obj = bpy.data.objects[name]
    obj.location.z = 2.49
    obj.rotation_euler = (Vector((0,0,1.93)) - obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_mainfile()
