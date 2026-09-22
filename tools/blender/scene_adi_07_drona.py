"""adi-07 The school of arrows: dusty day range, ring targets, rack, Ekalavya shrine.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math
import bpy
from lib import (aim_camera, box, clean_scene, figure, frame_check, principled,
                 setup_cycles, setup_view, sky_gradient, sun_light, tree_at,
                 tree_kit, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 70707
rnd = random.Random(SEED)
SID = 'adi-07-drona'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.88, 0.72, 0.52), mid=(0.58, 0.68, 0.78), zenith=(0.30, 0.50, 0.75),
             below=(0.35, 0.28, 0.20))
sun_light('GEO-sun', energy=4.0, location=(30, 20, 50))

MAT = {
    'earth': principled('MAT-earth', base=(0.48, 0.36, 0.22, 1.0), roughness=1.0),
    'line': principled('MAT-line', base=(0.90, 0.86, 0.72, 1.0), roughness=1.0),
    'red': principled('MAT-red', base=(0.70, 0.18, 0.12, 1.0), roughness=0.8),
    'white': principled('MAT-white', base=(0.90, 0.87, 0.78, 1.0), roughness=0.8),
    'wood': principled('MAT-wood', base=(0.30, 0.20, 0.12, 1.0), roughness=0.9),
    'shaft': principled('MAT-shaft', base=(0.78, 0.68, 0.50, 1.0), roughness=0.8),
    'stone': principled('MAT-stone', base=(0.40, 0.39, 0.36, 1.0), roughness=0.9),
    'brass': principled('MAT-brass', base=(0.60, 0.45, 0.15, 1.0), roughness=0.4, metallic=0.6),
    'skin': principled('MAT-skin', base=(0.60, 0.44, 0.32, 1.0), roughness=0.8),
    'drona': principled('MAT-drona', base=(0.20, 0.32, 0.38, 1.0), roughness=0.9),
    'arjuna': principled('MAT-arjuna', base=(0.48, 0.12, 0.10, 1.0), roughness=0.9),
    'leaf': principled('MAT-leaf', base=(0.16, 0.34, 0.14, 1.0), roughness=1.0),
    'trunk': principled('MAT-trunk', base=(0.28, 0.18, 0.11, 1.0), roughness=1.0),
}

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
gr = bpy.context.active_object
gr.name = 'GEO-ground'
gr.scale = (160, 160, 1)
gr.data.materials.append(MAT['earth'])

# firing-line markers
for i in range(8):
    box(f'GEO-linemark{i}', 0.5, 30, 0.12, MAT['line'], location=(-21 + i * 6, -6, 0.06))

# ring targets at staggered ranges
for i, tz in enumerate((-14, -20, -26, -32, -38)):
    tx = -16 + i * 8
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=3.4, location=(tx, tz, 1.7))
    st = bpy.context.active_object
    st.name = f'GEO-tstand{i}'
    st.data.materials.append(MAT['wood'])
    for rad, c in ((1.5, MAT['red']), (1.05, MAT['white']), (0.6, MAT['red'])):
        bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=0.14, location=(tx, tz + 0.1, 4.4))
        rg = bpy.context.active_object
        rg.name = f'GEO-ring{i}'
        rg.rotation_euler = (math.pi / 2, 0, 0)
        rg.data.materials.append(c)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(tx, tz + 0.1, 4.4))
    hb = bpy.context.active_object
    hb.name = f'GEO-hub{i}'
    hb.data.materials.append(MAT['red'])

# arrow rack + loose arrows near the line
box('GEO-rack', 3.0, 1.0, 1.2, MAT['wood'], location=(-7, 4, 0.6))
for i in range(9):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.6,
                                        location=(-8 + (i % 3) * 0.9, 3.7 + (i // 3) * 0.35, 2.2))
    a = bpy.context.active_object
    a.name = f'GEO-arrow{i}'
    a.rotation_euler = (0.25, 0, 0)
    a.data.materials.append(MAT['shaft'])
for i in range(5):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.8,
                                        location=(-8 + rnd.random() * 16, 2 + rnd.random() * 5, 0.8))
    a = bpy.context.active_object
    a.name = f'GEO-loose{i}'
    a.rotation_euler = (0.5 + rnd.random() * 0.3, 0, 0)
    a.data.materials.append(MAT['shaft'])

# Ekalavya shrine: stone + brass offering bowl
bpy.ops.mesh.primitive_ico_sphere_add(radius=1.6, subdivisions=2, location=(7, 8, 1.0))
ek = bpy.context.active_object
ek.name = 'GEO-ekstone'
ek.data.materials.append(MAT['stone'])
bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=0.5, location=(7, 8, 2.6))
bw = bpy.context.active_object
bw.name = 'GEO-bowl'
bw.data.materials.append(MAT['brass'])

# Drona watching, Arjuna at the line
figure('GEO-drona', MAT['drona'], MAT['skin'], 6, -2, s=1.1, ry=2.6)
figure('GEO-arjuna', MAT['arjuna'], MAT['skin'], 2, 0, s=1.0, ry=2.6)

trunk_me, canopy_me = tree_kit()
for _ in range(18):
    a = rnd.random() * 6.283
    d = 45 + rnd.random() * 30
    import math
    tree_at(trunk_me, canopy_me, MAT['trunk'], MAT['leaf'],
            math.cos(a) * d, math.sin(a) * d, 0.9 + rnd.random() * 0.7)

bpy.ops.object.camera_add(location=(0, 24, 4.0))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -16, 2.5))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('target-mid', (0, -26, 4.4)), ('rack', (-7, 4, 1.5)),
                  ('shrine', (7, 8, 1.6)), ('archers', (4, -1, 1.2))])

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
