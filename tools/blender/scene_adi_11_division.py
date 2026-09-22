"""adi-11 The kingdom splits: two land halves divided by water, broken bridge, half crown.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, figure, frame_check, principled,
                 setup_cycles, setup_view, sky_gradient, sun_light, tree_at,
                 tree_kit, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 111111
rnd = random.Random(SEED)
SID = 'adi-11-division'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.85, 0.52, 0.38), mid=(0.42, 0.30, 0.42), zenith=(0.16, 0.16, 0.30),
             below=(0.10, 0.09, 0.12))
sun_light('GEO-sun', energy=3.0, location=(-30, -10, 22))

MAT = {
    'west': principled('MAT-west', base=(0.20, 0.26, 0.16, 1.0), roughness=1.0),
    'east': principled('MAT-east', base=(0.26, 0.20, 0.14, 1.0), roughness=1.0),
    'water': principled('MAT-water', base=(0.12, 0.18, 0.30, 1.0), roughness=0.25),
    'wood': principled('MAT-wood', base=(0.28, 0.19, 0.11, 1.0), roughness=0.9),
    'stone': principled('MAT-stone', base=(0.48, 0.46, 0.40, 1.0), roughness=0.85),
    'gold': principled('MAT-gold', base=(0.72, 0.55, 0.18, 1.0), roughness=0.35, metallic=0.7),
    'red': principled('MAT-red', base=(0.45, 0.10, 0.08, 1.0), roughness=0.9),
    'blue': principled('MAT-blue', base=(0.10, 0.26, 0.42, 1.0), roughness=0.9),
    'skin': principled('MAT-skin', base=(0.60, 0.44, 0.32, 1.0), roughness=0.8),
    'leaf': principled('MAT-leaf', base=(0.14, 0.28, 0.12, 1.0), roughness=1.0),
    'trunk': principled('MAT-trunk', base=(0.26, 0.17, 0.10, 1.0), roughness=1.0),
}

box('GEO-west', 34, 60, 3, MAT['west'], location=(-19, 0, 0.5))
box('GEO-east', 34, 60, 3, MAT['east'], location=(19, 0, 0.5))
box('GEO-rift-water', 8, 70, 0.4, MAT['water'], location=(0, 0, 0.4))

# broken bridge planks sagging into the rift
for i in range(6):
    x = -2.5 + (5 + rnd.random() * 2 if i >= 3 else 0)
    pl = box(f'GEO-plank{i}', 3.4, 1.4, 0.3, MAT['wood'], location=(x, -12 + i * 4.4, 2.1 - abs(i - 2.5) * 0.35))
    pl.rotation_euler = ((rnd.random() - 0.5) * 0.4, 0, (rnd.random() - 0.5) * 0.5)

# half crown on western pedestal, empty eastern pedestal
box('GEO-pedW', 3, 3, 2, MAT['stone'], location=(-9, -2, 3.0))
bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=1.1, vertices=12, location=(-9, -2, 4.6))
hc = bpy.context.active_object
hc.name = 'GEO-halfcrown'
hc.data.materials.append(MAT['gold'])
for i in range(4):
    a = (i / 4) * 3.14159
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, depth=0.9, vertices=6,
                                    location=(-9 + __import__('math').cos(a) * 1.3, -2 + __import__('math').sin(a) * 1.3, 5.5))
    sp = bpy.context.active_object
    sp.name = f'GEO-spike{i}'
    sp.data.materials.append(MAT['gold'])
box('GEO-pedE', 3, 3, 2, MAT['stone'], location=(19, -10, 3.0))

# rival banners + two figures facing off across the rift
box('GEO-poleW', 0.18, 0.18, 11.0, MAT['wood'], location=(-14, -4, 7.0))
box('GEO-bannerW', 3.4, 0.1, 6.5, MAT['red'], location=(-12.2, -4, 8.0))
box('GEO-poleE', 0.18, 0.18, 11.0, MAT['wood'], location=(14, -4, 7.0))
box('GEO-bannerE', 3.4, 0.1, 6.5, MAT['blue'], location=(12.2, -4, 8.0))
figure('GEO-kaurava', MAT['red'], MAT['skin'], -8, 6, s=1.1, ry=1.8)
figure('GEO-pandava', MAT['blue'], MAT['skin'], 8, 6, s=1.1, ry=-1.8)

trunk_me, canopy_me = tree_kit()
for _ in range(16):
    a = rnd.random() * 6.283
    d = 34 + rnd.random() * 26
    x, y = __import__('math').cos(a) * d, __import__('math').sin(a) * d
    if abs(x) < 8:
        continue
    tree_at(trunk_me, canopy_me, MAT['trunk'], MAT['leaf'], x, y, 0.8 + rnd.random() * 0.6)

bpy.ops.object.camera_add(location=(0, 28, 6.0))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -6, 2.5))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('crown', (-9, -2, 4.8)), ('bridge', (0, 0, 2.0)),
                  ('bannerW', (-12.2, -4, 8.0)), ('bannerE', (12.2, -4, 8.0))])

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
