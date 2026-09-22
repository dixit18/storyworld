"""adi-02 Snake sacrifice: night stone hall, great fire, rising serpents, priests.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
from lib import (aim_camera, box, clean_scene, figure, fire_pit, flame_cone,
                 frame_check, pillar, principled, setup_cycles, setup_view,
                 sky_gradient, star_spheres, sun_light, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 20202
rnd = random.Random(SEED)
SID = 'adi-02-snake-sacrifice'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.30, 0.10, 0.08), mid=(0.12, 0.06, 0.08), zenith=(0.03, 0.02, 0.04),
             below=(0.02, 0.01, 0.01))
sun_light('GEO-moonlight', energy=0.4, location=(20, -30, 40))

MAT = {
    'floor': principled('MAT-floor', base=(0.22, 0.16, 0.13, 1.0), roughness=0.85),
    'pillar': principled('MAT-pillar', base=(0.30, 0.20, 0.16, 1.0), roughness=0.85),
    'trim': principled('MAT-trim', base=(0.65, 0.48, 0.18, 1.0), roughness=0.5, metallic=0.5),
    'serpent': principled('MAT-serpent', base=(0.30, 0.08, 0.05, 1.0), roughness=0.5,
                          emission=(0.75, 0.18, 0.05), emission_strength=0.7),
    'eye': principled('MAT-eye', base=(1, 1, 1, 1), emission=(1.0, 0.45, 0.10), emission_strength=4.0),
    'robe': principled('MAT-robe', base=(0.25, 0.10, 0.08, 1.0), roughness=0.95),
    'skin': principled('MAT-skin', base=(0.55, 0.40, 0.30, 1.0), roughness=0.8),
    'stone': principled('MAT-stone', base=(0.30, 0.28, 0.26, 1.0), roughness=0.9),
    'wood': principled('MAT-wood', base=(0.25, 0.16, 0.10, 1.0), roughness=0.9),
    'flame': principled('MAT-flame', base=(1, 1, 1, 1), emission=(1.0, 0.40, 0.08), emission_strength=5.0),
    'core': principled('MAT-core', base=(1, 1, 1, 1), emission=(1.0, 0.78, 0.30), emission_strength=5.0),
    'bowl': principled('MAT-bowl', base=(0.55, 0.42, 0.15, 1.0), roughness=0.4, metallic=0.6),
}

# floor + rear wall
box('GEO-floor', 46, 46, 0.6, MAT['floor'], location=(0, 0, 0.3))
box('GEO-rearwall', 46, 1.5, 12, MAT['pillar'], location=(0, -22.5, 6))
for i in range(12):  # colonnade ring
    a = (i / 12) * 2 * math.pi
    pillar('GEO-col', math.cos(a) * 19, math.sin(a) * 19, 0.6, 9, 0.7, MAT['pillar'], MAT['trim'])

# great fire
fire_pit('GEO-rite-fire', 0, 0, 1.9, MAT['stone'], MAT['wood'], MAT['flame'], MAT['core'],
         light_energy=500.0)

# serpents rising (bezier curves with bevel = TubeGeometry equivalent)
for i in range(7):
    a = (i / 7) * 2 * math.pi + rnd.random() * 0.5
    cd = bpy.data.curves.new(f'GEO-serpent{i}-curve', type='CURVE')
    cd.dimensions = '3D'
    spline = cd.splines.new('BEZIER')
    spline.bezier_points.add(3)
    pts = [(math.cos(a) * 2, math.sin(a) * 2, 0.5),
           (math.cos(a + 0.7) * 2.6, math.sin(a + 0.7) * 2.6, 3.4),
           (math.cos(a + 1.4) * 1.8, math.sin(a + 1.4) * 1.8, 6.4),
           (math.cos(a + 2.0) * 2.4, math.sin(a + 2.0) * 2.4, 9.2)]
    for bp, p in zip(spline.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(f'GEO-serpent{i}', cd)
    bpy.context.collection.objects.link(ob)
    cd.bevel_depth = 0.34
    cd.bevel_resolution = 3
    cd.materials.append(MAT['serpent'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(pts[3][0], pts[3][1], pts[3][2] + 0.3))
    head = bpy.context.active_object
    head.name = f'GEO-serpent{i}-head'
    head.data.materials.append(MAT['eye'])

# priests + braziers
for i in range(6):
    a = (i / 6) * 2 * math.pi + 0.5
    figure(f'GEO-priest{i}', MAT['robe'], MAT['skin'], math.cos(a) * 8.5, math.sin(a) * 8.5,
           s=1.15, ry=-a + math.pi / 2)
for bx, by in ((12, 12), (-12, 12), (12, -12), (-12, -12)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=1.2, location=(bx, by, 0.6))
    b = bpy.context.active_object
    b.name = 'GEO-brazier'
    b.data.materials.append(MAT['bowl'])
    flame_cone('GEO-brazier-flame', bx, by, 1.7, 0.4, 1.2, MAT['flame'], MAT['core'])

# camera
bpy.ops.object.camera_add(location=(13, 17, 4.5))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -2, 3.0))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('fire', (0, 0, 2.0)), ('serpent-top', (2.4, 0.5, 9.2)),
                  ('priest', (7.4, 4.2, 1.2)), ('colonnade', (-19, 0, 5))])

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
