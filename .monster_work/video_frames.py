import sys
from pathlib import Path

import bpy


name = sys.argv[sys.argv.index('--')+1]
root = Path(r'D:\Blender\AI')
output = root / '.monster_work'
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 720
scene.render.resolution_y = 405
scene.render.resolution_percentage = 100
scene.render.fps = 12
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
editor = scene.sequence_editor_create()
strip = editor.strips.new_movie(name, str(root / 'One_Eyed_Monster' / f'{name}.mp4'), 1, 1)
strip.transform.scale_x = 720 / 1920
strip.transform.scale_y = 405 / 1080
scene.render.use_sequencer = True
for frame in ([1,8,12,15,23,30] if name == 'Idle' else [1,19,37,55,73]):
    scene.frame_set(frame)
    scene.render.filepath = str(output / f'movie_{name}_{frame:02}.png')
    bpy.ops.render.render(write_still=True)
