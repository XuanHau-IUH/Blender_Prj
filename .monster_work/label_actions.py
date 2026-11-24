import bpy

rig = bpy.data.objects['Monster Rig']
upper = bpy.data.objects['Eyelid | upper'].data.shape_keys
lower = bpy.data.objects['Eyelid | lower'].data.shape_keys
actions = {
    rig.animation_data.nla_tracks['Idle'].strips[0].action: 'Idle | body and arms',
    upper.animation_data.nla_tracks['Idle'].strips[0].action: 'Idle | upper eyelid',
    lower.animation_data.nla_tracks['Idle'].strips[0].action: 'Idle | lower eyelid',
    rig.animation_data.nla_tracks['Turntable'].strips[0].action: 'Turntable | 360 degrees',
}
for action in list(bpy.data.actions):
    if action in actions:
        action.name = actions[action]
    elif action.name.split('.')[0] in {'Idle', 'Turntable'} and action.users <= int(action.use_fake_user):
        bpy.data.actions.remove(action)

preferences = bpy.context.preferences.filepaths
save_version = preferences.save_version
try:
    preferences.save_version = 0
    bpy.ops.wm.save_mainfile()
finally:
    preferences.save_version = save_version

print('Actions:', [(action.name, action.users) for action in bpy.data.actions])
