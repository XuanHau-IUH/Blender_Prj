import bpy
import bmesh

floor = bpy.data.objects['Studio ground']
wall = bpy.data.objects['Studio cyclorama']
old = wall.data
verts = [v.co.copy() for v in old.vertices]
faces = [tuple(range(128))] + [tuple(reversed(p.vertices[:])) for p in old.polygons]
stage = bpy.data.meshes.new('Studio cyclorama | seamless')
stage.from_pydata(verts, [], faces)
stage.materials.append(floor.data.materials[0])
for face in stage.polygons:
    face.use_smooth = True
recalc = bmesh.new()
recalc.from_mesh(stage)
bmesh.ops.recalc_face_normals(recalc, faces=list(recalc.faces))
recalc.to_mesh(stage)
recalc.free()
wall.data = stage
wall.visible_diffuse = True
wall.visible_glossy = True
wall.visible_shadow = True
bpy.data.objects.remove(floor, do_unlink=True)
if old.users == 0:
    bpy.data.meshes.remove(old)
bpy.context.preferences.filepaths.save_version = 0
try:
    bpy.ops.wm.save_mainfile()
finally:
    bpy.context.preferences.filepaths.save_version = 1
