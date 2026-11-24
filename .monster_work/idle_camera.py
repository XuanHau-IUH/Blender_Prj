import bpy

hero = bpy.data.objects['Perspective 3-4']
camera = hero.copy()
camera.data = hero.data.copy()
camera.name = camera.data.name = 'Idle Camera'
camera.data.lens = 47.5
hero.users_collection[0].objects.link(camera)
preferences = bpy.context.preferences.filepaths
save_version = preferences.save_version
try:
    preferences.save_version = 0
    bpy.ops.wm.save_mainfile()
finally:
    preferences.save_version = save_version
