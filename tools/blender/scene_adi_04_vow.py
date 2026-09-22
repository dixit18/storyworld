"""adi-04 Bhishma's vow: golden throne room, empty throne, oath sword, banners.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, flame_cone, frame_check, pillar,
                 principled, setup_cycles, setup_view, sky_gradient, sun_light, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SID = 'adi-04-bhishma-vow'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.45, 0.28, 0.15), mid=(0.20, 0.13, 0.10), zenith=(0.06, 0.05, 0.05),
             below=(0.03, 0.02, 0.02))
sun_light('GEO-warm', energy=2.2, location=(10, 10, 30))

MAT = {
    'marble': principled('MAT-marble', base=(0.80, 0.75, 0.62, 1.0), roughness=0.4, metallic=0.1),
    'pillar': principled('MAT-pillar', base=(0.85, 0.79, 0.65, 1.0), roughness=0.6),
    'gold': principled('MAT-gold', base=(0.72, 0.55, 0.18, 1.0), roughness=0.35, metallic=0.7),
    'darkwood': principled('MAT-darkwood', base=(0.20, 0.12, 0.08, 1.0), roughness=0.8),
    'banner': principled('MAT-banner', base=(0.45, 0.10, 0.08, 1.0), roughness=0.9),
    'steel': principled('MAT-steel', base=(0.75, 0.77, 0.82, 1.0), roughness=0.2, metallic=0.9),
    'flame': principled('MAT-flame', base=(1, 1, 1, 1), emission=(1.0, 0.55, 0.15), emission_strength=5.0),
    'core': principled('MAT-core', base=(1, 1, 1, 1), emission=(1.0, 0.85, 0.45), emission_strength=5.0),
    'beam': principled('MAT-beam', base=(1, 1, 1, 1), emission=(1.0, 0.88, 0.60), emission_strength=2.0),
    'window': principled('MAT-window', base=(1, 1, 1, 1), emission=(1.0, 0.90, 0.70), emission_strength=1.2),
}

box('GEO-floor', 52, 52, 0.6, MAT['marble'], location=(0, 0, 0.3))
for x, y in ((-18, -18), (18, -18), (-18, 18), (18, 18), (-18, 0), (18, 0), (0, -18)):
    pillar('GEO-col', x, y, 0.6, 11, 0.8, MAT['pillar'], MAT['gold'])
box('GEO-rearwall', 52, 1.5, 14, MAT['darkwood'], location=(0, -25, 7))
box('GEO-roof', 52, 54, 3, MAT['darkwood'], location=(0, 0, 15.5))

# dais + empty throne + oath sword on its stand
for i in range(3):
    box(f'GEO-dais{i}', 10 - i * 2, 8 - i * 1.4, 0.5, MAT['gold'], location=(0, -14, 0.85 + i * 0.5))
box('GEO-throne-back', 3.4, 1.2, 3.2, MAT['gold'], location=(0, -14.5, 4.0))
box('GEO-throne-seat', 4.2, 1.6, 1.1, MAT['gold'], location=(0, -14.5, 5.6))
box('GEO-throne-cushion', 3.0, 1.1, 0.35, MAT['banner'], location=(0, -14.5, 6.3))
blade = box('GEO-oath-blade', 0.16, 0.4, 3.4, MAT['steel'], location=(2.8, -12.5, 3.4))
blade.rotation_euler = (0, 0.5, 0)
box('GEO-oath-stand', 0.5, 0.5, 0.9, MAT['darkwood'], location=(2.1, -12.5, 1.6))
bpy.ops.object.light_add(type='SPOT', location=(0, -14, 13.5))
spot = bpy.context.active_object
spot.name = 'GEO-oath-spot'
spot.data.energy = 900.0
spot.data.color = (1.0, 0.88, 0.66)
spot.data.spot_size = 0.5
spot.data.spot_blend = 0.4
spot.rotation_euler = (0, 0, 0)

# banners + torches
for bx in (-14, 14):
    box(f'GEO-bannerpole{bx}', 0.18, 0.18, 11.0, MAT['darkwood'], location=(bx, -24, 6.0))
    box(f'GEO-banner{bx}', 3.4, 0.1, 7.5, MAT['banner'], location=(bx + 1.85, -24, 8.6))
for tx, ty in ((-8, 2), (8, 2), (-8, -8), (8, -8)):
    box(f'GEO-torchpole{tx}{ty}', 0.14, 0.14, 2.6, MAT['darkwood'], location=(tx, ty, 1.6))
    flame_cone(f'GEO-torch{tx}{ty}', tx, ty, 3.3, 0.28, 0.9, MAT['flame'], MAT['core'])

# glowing high windows on the rear wall
for i, wx in enumerate((-14, -7, 7, 14)):
    box(f'GEO-window{i}', 2.4, 0.3, 3.6, MAT['window'], location=(wx, -24.2, 9.5))
    box(f'GEO-windowframeV{i}', 0.18, 0.34, 3.6, MAT['darkwood'], location=(wx, -24.2, 9.5))
    box(f'GEO-windowframeH{i}', 2.4, 0.34, 0.18, MAT['darkwood'], location=(wx, -24.2, 9.5))

bpy.ops.object.camera_add(location=(11, 12, 3.4))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -13, 3.5))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('throne', (0, -14.5, 4.5)), ('sword', (2.8, -12.5, 3.4)),
                  ('banner', (-14, -24, 8.6)), ('window', (7, -24.2, 9.5))])

scene = bpy.context.scene
scene.render.filepath = os.path.join(CH, 'renders', f'{SID}.png')
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print('RENDERED:', scene.render.filepath)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', f'{SID}.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(CH, 'models', f'{SID}.glb'),
                           export_format='GLB', export_apply=True, export_yup=True,
                           export_cameras=False, export_lights=False)
print('EXPORTED GLB')
print('TRIS:', sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH' and o.data))
