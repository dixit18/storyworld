"""adi-10 The bow that chose: golden pavilion, pool with turning fish, great bow, crowd.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, figure, frame_check, pillar,
                 principled, setup_cycles, setup_view, sky_gradient, sun_light, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 101010
rnd = random.Random(SEED)
SID = 'adi-10-swayamvara'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.90, 0.70, 0.48), mid=(0.60, 0.62, 0.68), zenith=(0.30, 0.45, 0.68),
             below=(0.25, 0.20, 0.16))
sun_light('GEO-sun', energy=4.5, location=(30, 20, 50))

MAT = {
    'floor': principled('MAT-floor', base=(0.72, 0.60, 0.44, 1.0), roughness=0.6),
    'pillar': principled('MAT-pillar', base=(0.85, 0.79, 0.65, 1.0), roughness=0.6),
    'gold': principled('MAT-gold', base=(0.72, 0.55, 0.18, 1.0), roughness=0.35, metallic=0.7),
    'canopy': principled('MAT-canopy', base=(0.50, 0.12, 0.10, 1.0), roughness=0.9),
    'pool': principled('MAT-pool', base=(0.10, 0.26, 0.40, 1.0), roughness=0.15, metallic=0.3),
    'bow': principled('MAT-bow', base=(0.25, 0.14, 0.08, 1.0), roughness=0.7),
    'skin': principled('MAT-skin', base=(0.62, 0.45, 0.33, 1.0), roughness=0.8),
    'darkwood': principled('MAT-darkwood', base=(0.20, 0.12, 0.08, 1.0), roughness=0.85),
}
crowd = [principled(f'MAT-crowd{i}', base=c, roughness=0.9)
         for i, c in enumerate([(0.50, 0.12, 0.10, 1.0), (0.10, 0.26, 0.40, 1.0),
                                (0.72, 0.55, 0.18, 1.0), (0.25, 0.32, 0.20, 1.0), (0.35, 0.18, 0.30, 1.0)])]

box('GEO-floor', 64, 44, 0.6, MAT['floor'], location=(0, 0, 0.3))
for i in range(8):
    for z in (-19, 19):
        pillar('GEO-col', -28 + i * 8, z, 0.6, 12, 0.7, MAT['pillar'], MAT['gold'])
box('GEO-canopy', 66, 46, 1.2, MAT['canopy'], location=(0, 0, 13.4))

# pool with turning fish + target rings above
bpy.ops.mesh.primitive_cylinder_add(radius=5, depth=0.5, location=(0, -4, 0.7))
pl = bpy.context.active_object
pl.name = 'GEO-pool'
pl.data.materials.append(MAT['pool'])
for rad, c in ((3.4, MAT['pillar']), (2.2, MAT['gold']), (1.1, MAT['pillar'])):
    bpy.ops.mesh.primitive_torus_add(major_radius=rad, minor_radius=0.16, location=(0, -4, 7.5))
    rg = bpy.context.active_object
    rg.name = 'GEO-ring'
    rg.data.materials.append(c)
bpy.ops.mesh.primitive_cone_add(radius1=0.5, depth=1.6, vertices=8, location=(0, -4, 7.5))
fh = bpy.context.active_object
fh.name = 'GEO-fish'
fh.rotation_euler = (math.pi, 0, 0)
fh.data.materials.append(MAT['gold'])

# great bow on its stand
bpy.ops.mesh.primitive_torus_add(major_radius=2.6, minor_radius=0.22, major_segments=24,
                                 location=(-10, -4, 3.0))
bw = bpy.context.active_object
bw.name = 'GEO-bow'
bw.rotation_euler = (math.pi / 2, 0, math.pi * 0.15)
box('GEO-bowstring', 0.05, 0.05, 4.6, MAT['bow'], location=(-10, -4, 3.0))
bw.data.materials.append(MAT['bow'])
box('GEO-bowstand', 1.6, 1.6, 1.0, MAT['darkwood'], location=(-10, -4, 0.8))

# garland of five knots + thrones + crowd ring
for i in range(5):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.16, location=(8 + i * 1.3, -4, 2.2))
    k = bpy.context.active_object
    k.name = f'GEO-knot{i}'
    k.data.materials.append(crowd[i % 5])
for i in range(5):
    box(f'GEO-throne{i}', 2.0, 1.2, 2.4, MAT['gold'], location=(-8 + i * 4, 12, 1.5))
for i in range(22):
    a = (i / 22) * 2 * math.pi
    figure(f'GEO-guest{i}', crowd[i % 5], MAT['skin'],
           math.cos(a) * (13 + rnd.random() * 4), -4 + math.sin(a) * (9 + rnd.random() * 3),
           s=0.95, ry=-a + math.pi / 2)

bpy.ops.object.camera_add(location=(-16, 20, 5.0))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (2, -6, 2.5))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('pool', (0, -4, 1.0)), ('bow', (-10, -4, 3.0)),
                  ('fish', (0, -4, 7.5)), ('thrones', (0, 12, 1.8))])

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
