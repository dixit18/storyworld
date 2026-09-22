"""adi-08 The house that burns: night, ornate lacquer palace, fires, smoke, escape mound.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, fire_pit, flame_cone, frame_check,
                 principled, setup_cycles, setup_view, sky_gradient, star_spheres,
                 sun_light, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 80808
rnd = random.Random(SEED)
SID = 'adi-08-lakshagriha'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.35, 0.12, 0.08), mid=(0.10, 0.05, 0.08), zenith=(0.02, 0.02, 0.04),
             below=(0.02, 0.01, 0.01))
sun_light('GEO-moonlight', energy=0.35, location=(-20, -30, 40))

MAT = {
    'ground': principled('MAT-ground', base=(0.10, 0.08, 0.07, 1.0), roughness=1.0),
    'wall': principled('MAT-wall', base=(0.30, 0.12, 0.07, 1.0), roughness=0.7),
    'trim': principled('MAT-trim', base=(0.65, 0.48, 0.15, 1.0), roughness=0.5, metallic=0.4),
    'roof': principled('MAT-roof', base=(0.14, 0.07, 0.05, 1.0), roughness=0.9),
    'window': principled('MAT-window', base=(1, 1, 1, 1), emission=(1.0, 0.45, 0.10), emission_strength=4.0),
    'door': principled('MAT-door', base=(0.03, 0.02, 0.02, 1.0), roughness=1.0),
    'stone': principled('MAT-stone', base=(0.30, 0.28, 0.26, 1.0), roughness=0.9),
    'wood': principled('MAT-wood', base=(0.25, 0.16, 0.10, 1.0), roughness=0.9),
    'flame': principled('MAT-flame', base=(1, 1, 1, 1), emission=(1.0, 0.42, 0.08), emission_strength=5.0),
    'core': principled('MAT-core', base=(1, 1, 1, 1), emission=(1.0, 0.78, 0.30), emission_strength=5.0),
    'smoke': principled('MAT-smoke', base=(0.25, 0.24, 0.24, 1.0), roughness=1.0),
    'mound': principled('MAT-mound', base=(0.14, 0.10, 0.08, 1.0), roughness=1.0),
}
MAT['smoke'].blend_method = 'BLEND'
MAT['smoke'].node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value = 0.35

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
gr = bpy.context.active_object
gr.name = 'GEO-ground'
gr.scale = (140, 140, 1)
gr.data.materials.append(MAT['ground'])

# ornate lacquer palace
box('GEO-palace', 24, 16, 10, MAT['wall'], location=(0, -6, 5))
box('GEO-palace-trim', 26, 18, 1.0, MAT['trim'], location=(0, -6, 10.2))
bpy.ops.mesh.primitive_cone_add(radius1=17, depth=7, vertices=4, location=(0, -6, 14))
rf = bpy.context.active_object
rf.name = 'GEO-palace-roof'
rf.rotation_euler = (0, 0, math.pi / 4)
rf.data.materials.append(MAT['roof'])
for i in range(5):  # burning windows
    box(f'GEO-win{i}', 1.8, 0.3, 2.6, MAT['window'], location=(-9.6 + i * 4.8, 2.1, 5.4))
box('GEO-door', 3.0, 0.5, 5.0, MAT['door'], location=(0, 2.1, 2.5))

# fires around the base + escape mound + ramp behind
fire_pit('GEO-fireL', -9, 8, 1.2, MAT['stone'], MAT['wood'], MAT['flame'], MAT['core'], light_energy=350.0)
fire_pit('GEO-fireR', 9, 8, 1.0, MAT['stone'], MAT['wood'], MAT['flame'], MAT['core'], light_energy=300.0)
fire_pit('GEO-fireC', 0, 12, 0.8, MAT['stone'], MAT['wood'], MAT['flame'], MAT['core'], light_energy=220.0)
bpy.ops.mesh.primitive_uv_sphere_add(radius=4, location=(14, -24, 0.5))
md = bpy.context.active_object
md.name = 'GEO-mound'
md.scale = (1.4, 1.0, 0.55)
md.data.materials.append(MAT['mound'])
box('GEO-ramp', 4.0, 12, 0.5, MAT['door'], location=(12, -20, 0.4))

# smoke columns
for i in range(5):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-8 + i * 4 + rnd.random() * 2, -6 + rnd.random() * 3, 18))
    sm = bpy.context.active_object
    sm.name = f'GEO-smoke{i}'
    sm.scale = (6, 16, 1)
    sm.rotation_euler = (0.1, 0.2 * i, 0)
    sm.data.materials.append(MAT['smoke'])

star_spheres(140, SEED)

bpy.ops.object.camera_add(location=(26, 34, 10.0))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -8, 5.0))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('palace', (0, -6, 6.0)), ('fireL', (-9, 8, 1.5)),
                  ('mound', (14, -24, 1.5)), ('smoke', (0, -6, 18.0))])

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
