"""adi-01 Naimisha forest at night: fire circle, listening sages, moon, dense ring.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, figure, fire_pit, flame_cone,
                 frame_check, principled, setup_cycles, setup_view, sky_gradient,
                 star_spheres, sun_light, tree_at, tree_kit, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 10101
rnd = random.Random(SEED)
SID = 'adi-01-naimisha'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.10, 0.20, 0.24), mid=(0.07, 0.13, 0.20), zenith=(0.02, 0.04, 0.10),
             below=(0.01, 0.02, 0.03))
sun_light('GEO-moonlight', energy=0.7, location=(-30, -40, 50))

MAT = {
    'ground': principled('MAT-ground', base=(0.05, 0.11, 0.08, 1.0), roughness=1.0),
    'stone': principled('MAT-stone', base=(0.35, 0.35, 0.34, 1.0), roughness=0.9),
    'wood': principled('MAT-wood', base=(0.25, 0.16, 0.10, 1.0), roughness=0.9),
    'leaf': principled('MAT-leaf', base=(0.04, 0.16, 0.10, 1.0), roughness=1.0),
    'trunk': principled('MAT-trunk', base=(0.20, 0.13, 0.09, 1.0), roughness=1.0),
    'flame': principled('MAT-flame', base=(1, 1, 1, 1), emission=(1.0, 0.42, 0.10), emission_strength=5.0),
    'core': principled('MAT-core', base=(1, 1, 1, 1), emission=(1.0, 0.80, 0.35), emission_strength=5.0),
    'moon': principled('MAT-moon', base=(1, 1, 1, 1), emission=(0.90, 0.93, 1.0), emission_strength=2.5),
    'firefly': principled('MAT-firefly', base=(1, 1, 1, 1), emission=(0.62, 0.90, 0.30), emission_strength=4.0),
    'skin': principled('MAT-skin', base=(0.55, 0.40, 0.30, 1.0), roughness=0.8),
}
robes = [principled(f'MAT-robe{i}', base=c, roughness=0.95)
         for i, c in enumerate([(0.75, 0.70, 0.55, 1.0), (0.55, 0.42, 0.20, 1.0), (0.45, 0.32, 0.22, 1.0)])]

# ground
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
gr = bpy.context.active_object
gr.name = 'GEO-ground'
gr.scale = (150, 150, 1)
gr.data.materials.append(MAT['ground'])

# tree ring (clear center + camera corridor around x=2..11, y=8..16)
trunk_me, canopy_me = tree_kit()
placed = 0
tries = 0
while placed < 64 and tries < 400:
    tries += 1
    a = rnd.random() * 2 * math.pi
    d = 11 + rnd.random() * 55
    x, y = math.cos(a) * d, math.sin(a) * d
    if 0 < x < 14 and 6 < y < 18:
        continue
    tree_at(trunk_me, canopy_me, MAT['trunk'], MAT['leaf'], x, y, 0.9 + rnd.random() * 1.1)
    placed += 1

# hero fire + sage circle
fire_pit('GEO-hero-fire', 0, 0, 1.1, MAT['stone'], MAT['wood'], MAT['flame'], MAT['core'], light_energy=300.0)
for i in range(8):
    a = (i / 8) * 2 * math.pi + 0.2
    sx, sy = math.cos(a) * 4.4, math.sin(a) * 4.4
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=2.2, location=(sx, sy, 0.35))
    seat = bpy.context.active_object
    seat.name = f'GEO-seat{i}'
    seat.rotation_euler = (0, math.pi / 2, -a)
    seat.data.materials.append(MAT['wood'])
    figure(f'GEO-sage{i}', robes[i % 3], MAT['skin'], sx * 1.02, sy * 1.02, s=1.0, ry=-a + math.pi / 2)

# moon + stars + fireflies
bpy.ops.mesh.primitive_uv_sphere_add(radius=5, location=(-70, -90, 80))
moon = bpy.context.active_object
moon.name = 'GEO-moon'
moon.data.materials.append(MAT['moon'])
star_spheres(160, SEED)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.09, subdivisions=1, location=(0, 0, -50))
ff = bpy.context.active_object.data
bpy.data.objects.remove(bpy.context.active_object, do_unlink=True)
for i in range(44):
    a = rnd.random() * 2 * math.pi
    d = 4 + rnd.random() * 26
    o = bpy.data.objects.new('GEO-firefly', ff)
    bpy.context.collection.objects.link(o)
    o.location = (math.cos(a) * d, math.sin(a) * d, 0.5 + rnd.random() * 4.5)
    if not o.data.materials:
        o.data.materials.append(MAT['firefly'])

# camera
bpy.ops.object.camera_add(location=(11, 15, 3.6))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -2, 1.6))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('fire', (0, 0, 1.2)), ('sage-far', (-4.4, -0.9, 1.2)),
                  ('moon', (-70, -90, 80)), ('trees-back', (0, -30, 4))])

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
