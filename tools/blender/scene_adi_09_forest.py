"""adi-09 Hunger in the forest: dense dark woods, watching eyes, Bhima's mace, fireflies.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, frame_check, principled,
                 setup_cycles, setup_view, sky_gradient, sun_light, tree_at,
                 tree_kit, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 90909
rnd = random.Random(SEED)
SID = 'adi-09-hidimba'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.06, 0.12, 0.11), mid=(0.03, 0.07, 0.08), zenith=(0.01, 0.02, 0.04),
             below=(0.01, 0.01, 0.01))
sun_light('GEO-moonlight', energy=0.45, location=(10, -20, 40))

MAT = {
    'ground': principled('MAT-ground', base=(0.03, 0.07, 0.05, 1.0), roughness=1.0),
    'leaf': principled('MAT-leaf', base=(0.02, 0.10, 0.07, 1.0), roughness=1.0),
    'trunk': principled('MAT-trunk', base=(0.10, 0.07, 0.05, 1.0), roughness=1.0),
    'eye': principled('MAT-eye', base=(1, 1, 1, 1), emission=(1.0, 0.78, 0.20), emission_strength=4.0),
    'rock': principled('MAT-rock', base=(0.18, 0.18, 0.18, 1.0), roughness=0.95),
    'iron': principled('MAT-iron', base=(0.35, 0.35, 0.38, 1.0), roughness=0.4, metallic=0.7),
    'firefly': principled('MAT-firefly', base=(1, 1, 1, 1), emission=(0.55, 0.90, 0.30), emission_strength=4.0),
}

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
gr = bpy.context.active_object
gr.name = 'GEO-ground'
gr.scale = (130, 130, 1)
gr.data.materials.append(MAT['ground'])

trunk_me, canopy_me = tree_kit()
placed = tries = 0
while placed < 95 and tries < 600:
    tries += 1
    a = rnd.random() * 2 * math.pi
    d = 8 + rnd.random() * 52
    x, y = math.cos(a) * d, math.sin(a) * d
    if -4 < x < 6 and 8 < y < 20:  # camera corridor
        continue
    tree_at(trunk_me, canopy_me, MAT['trunk'], MAT['leaf'], x, y, 1.1 + rnd.random() * 1.2)
    placed += 1

# fallen log
bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=9, location=(4, 6, 0.55))
lg = bpy.context.active_object
lg.name = 'GEO-fallenlog'
lg.rotation_euler = (0, math.pi / 2, 0.5)
lg.data.materials.append(MAT['trunk'])

# Bhima's mace leaning on a rock
bpy.ops.mesh.primitive_ico_sphere_add(radius=1.1, subdivisions=2, location=(-8, -4, 0.7))
rk = bpy.context.active_object
rk.name = 'GEO-rock'
rk.data.materials.append(MAT['rock'])
bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=4.2, location=(-7.2, -4, 2.2))
hd = bpy.context.active_object
hd.name = 'GEO-mace-handle'
hd.rotation_euler = (0, 0.5, 0)
hd.data.materials.append(MAT['trunk'])
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(-6.1, -4, 3.9))
mh = bpy.context.active_object
mh.name = 'GEO-mace-head'
mh.data.materials.append(MAT['iron'])

# watching eyes
for i, (ex, ey, ez) in enumerate([(-12, -14, 4.5), (10, -18, 3.4), (-4, -26, 6.0), (16, -8, 5.0), (-18, -4, 3.0)]):
    for dx in (-0.5, 0.5):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(ex + dx, ey, ez))
        e = bpy.context.active_object
        e.name = f'GEO-eye{i}'
        e.data.materials.append(MAT['eye'])

# faint green fill + fireflies
bpy.ops.object.light_add(type='POINT', location=(0, -10, 3))
gl = bpy.context.active_object
gl.name = 'GEO-forestglow'
gl.data.energy = 50.0
gl.data.color = (0.25, 0.55, 0.30)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.09, subdivisions=1, location=(0, 0, -50))
ff = bpy.context.active_object.data
bpy.data.objects.remove(bpy.context.active_object, do_unlink=True)
for i in range(60):
    a = rnd.random() * 2 * math.pi
    d = 3 + rnd.random() * 32
    o = bpy.data.objects.new('GEO-firefly', ff)
    bpy.context.collection.objects.link(o)
    o.location = (math.cos(a) * d, math.sin(a) * d, 0.5 + rnd.random() * 5)
    if not o.data.materials:
        o.data.materials.append(MAT['firefly'])

bpy.ops.object.camera_add(location=(0, 14, 2.8))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -12, 3.0))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('eyes-mid', (-4, -26, 6.0)), ('mace', (-6.6, -4, 2.6)),
                  ('eyes-left', (-12, -14, 4.5)), ('eyes-right', (16, -8, 5.0))])

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
