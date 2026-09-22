"""adi-12 A city from ashes: white sunrise palace, gardens, charred Khandava edge.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, fire_pit, flame_cone, frame_check,
                 principled, setup_cycles, setup_view, sky_gradient, sun_light, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 121212
rnd = random.Random(SEED)
SID = 'adi-12-indraprastha'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=112)
setup_view()
sky_gradient(horizon=(1.0, 0.62, 0.32), mid=(0.72, 0.55, 0.50), zenith=(0.30, 0.45, 0.65),
             below=(0.18, 0.16, 0.14))
sun_light('GEO-sunrise', energy=4.5, location=(-50, -40, 18))

MAT = {
    'ground': principled('MAT-ground', base=(0.24, 0.36, 0.18, 1.0), roughness=1.0),
    'marble': principled('MAT-marble', base=(0.92, 0.89, 0.78, 1.0), roughness=0.55),
    'gold': principled('MAT-gold', base=(0.75, 0.58, 0.18, 1.0), roughness=0.3, metallic=0.7),
    'glow': principled('MAT-glow', base=(1, 1, 1, 1), emission=(1.0, 0.88, 0.60), emission_strength=2.0),
    'char': principled('MAT-char', base=(0.06, 0.05, 0.04, 1.0), roughness=1.0),
    'stone': principled('MAT-stone', base=(0.32, 0.30, 0.28, 1.0), roughness=0.9),
    'wood': principled('MAT-wood', base=(0.28, 0.18, 0.10, 1.0), roughness=0.9),
    'flame': principled('MAT-flame', base=(1, 1, 1, 1), emission=(1.0, 0.50, 0.12), emission_strength=4.0),
    'core': principled('MAT-core', base=(1, 1, 1, 1), emission=(1.0, 0.82, 0.40), emission_strength=4.0),
    'bird': principled('MAT-bird', base=(0.12, 0.12, 0.14, 1.0), roughness=1.0),
}
blooms = [principled(f'MAT-bloom{i}', base=c, roughness=0.7, emission=c[:3], emission_strength=0.3)
          for i, c in enumerate([(0.95, 0.80, 0.25, 1.0), (0.92, 0.88, 0.78, 1.0)])]

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
gr = bpy.context.active_object
gr.name = 'GEO-ground'
gr.scale = (170, 170, 1)
gr.data.materials.append(MAT['ground'])

# white palace complex
box('GEO-platform', 44, 36, 2, MAT['marble'], location=(0, -14, 1))
for tx, tz, th, rad in ((0, -18, 22, 4.4), (-14, -12, 14, 3.0), (14, -12, 14, 3.0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=th, vertices=12, location=(tx, tz, 2 + th / 2))
    tw = bpy.context.active_object
    tw.name = 'GEO-tower'
    tw.data.materials.append(MAT['marble'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rad * 1.02, location=(tx, tz, 2 + th))
    dm = bpy.context.active_object
    dm.name = 'GEO-dome'
    dm.data.materials.append(MAT['gold'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=rad * 0.2, location=(tx, tz, 2 + th + rad * 1.15))
    fn = bpy.context.active_object
    fn.name = 'GEO-finial'
    fn.data.materials.append(MAT['glow'])
box('GEO-greathall', 30, 10, 8, MAT['marble'], location=(0, -14, 6))
box('GEO-goldband', 34, 12, 1.0, MAT['gold'], location=(0, -14, 10.4))
for i in range(7):
    box(f'GEO-step{i}', 16 - i * 1.6, 4, 0.6, MAT['marble'], location=(0, 6 - i * 1.1, 0.6 + i * 0.6))

# gardens
for i in range(24):
    x = -30 + (i % 12) * 5.5
    y = 12 + (i // 12) * 6
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.9, location=(x, y, 0.45))
    st = bpy.context.active_object
    st.name = 'GEO-stem'
    st.data.materials.append(MAT['ground'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(x, y, 1.0))
    fl = bpy.context.active_object
    fl.name = 'GEO-bloom'
    fl.data.materials.append(blooms[i % 2])

# charred Khandava edge + last ember
for i in range(16):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3 + rnd.random() * 0.2, depth=4 + rnd.random() * 4,
                                        location=(8 + rnd.random() * 20, -60 + rnd.random() * 20, 2.5))
    ch = bpy.context.active_object
    ch.name = 'GEO-char'
    ch.data.materials.append(MAT['char'])
fire_pit('GEO-ember', 18, -48, 0.9, MAT['stone'], MAT['wood'], MAT['flame'], MAT['core'], light_energy=150.0)

# rising sun disc + circling birds
bpy.ops.mesh.primitive_uv_sphere_add(radius=7, location=(-90, -120, 26))
sn = bpy.context.active_object
sn.name = 'GEO-sun'
sn.data.materials.append(MAT['glow'])
for i in range(7):
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, depth=1.4, vertices=4,
                                    location=((rnd.random() - 0.5) * 40, -40 + (rnd.random() - 0.5) * 40, 24 + rnd.random() * 10))
    b = bpy.context.active_object
    b.name = 'GEO-bird'
    b.rotation_euler = (0, 0, 1.5708)
    b.data.materials.append(MAT['bird'])

bpy.ops.object.camera_add(location=(38, 48, 14.0))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (4, -12, 9.0))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('palace', (0, -14, 8.0)), ('dome', (0, -18, 26.0)),
                  ('charred', (18, -50, 3.0)), ('sun', (-90, -120, 26.0))])

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
