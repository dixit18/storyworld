"""adi-06 A hundred and five plus one: day garden, palace wall, river, drifting basket.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
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
SEED = 60606
rnd = random.Random(SEED)
SID = 'adi-06-births'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.85, 0.75, 0.62), mid=(0.55, 0.68, 0.80), zenith=(0.25, 0.45, 0.75),
             below=(0.20, 0.22, 0.20))
sun_light('GEO-sun', energy=3.2, location=(40, 30, 50))

MAT = {
    'grass': principled('MAT-grass', base=(0.20, 0.38, 0.16, 1.0), roughness=1.0),
    'stem': principled('MAT-stem', base=(0.15, 0.32, 0.12, 1.0), roughness=1.0),
    'wall': principled('MAT-wall', base=(0.62, 0.56, 0.43, 1.0), roughness=0.9),
    'dome': principled('MAT-dome', base=(0.55, 0.15, 0.10, 1.0), roughness=0.7),
    'gold': principled('MAT-gold', base=(0.75, 0.60, 0.18, 1.0), roughness=0.4, metallic=0.6),
    'wood': principled('MAT-wood', base=(0.35, 0.22, 0.12, 1.0), roughness=0.85),
    'skin': principled('MAT-skin', base=(0.78, 0.58, 0.44, 1.0), roughness=0.7),
    'water': principled('MAT-water', base=(0.10, 0.28, 0.42, 1.0), roughness=0.25),
    'leaf': principled('MAT-leaf', base=(0.08, 0.24, 0.10, 1.0), roughness=1.0),
    'trunk': principled('MAT-trunk', base=(0.28, 0.18, 0.11, 1.0), roughness=1.0),
}
petals = [principled(f'MAT-petal{i}', base=c, roughness=0.7,
                     emission=c[:3], emission_strength=0.25)
          for i, c in enumerate([(0.80, 0.20, 0.30, 1.0), (0.95, 0.80, 0.25, 1.0), (0.92, 0.88, 0.80, 1.0)])]

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
gr = bpy.context.active_object
gr.name = 'GEO-ground'
gr.scale = (150, 150, 1)
gr.data.materials.append(MAT['grass'])

# flower rows
for row in range(5):
    for i in range(12):
        x = -22 + i * 4 + (rnd.random() - 0.5)
        y = 2 + row * 3 + (rnd.random() - 0.5)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.9, location=(x, y, 0.45))
        st = bpy.context.active_object
        st.name = 'GEO-stem'
        st.data.materials.append(MAT['stem'])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(x, y, 1.0))
        fl = bpy.context.active_object
        fl.name = 'GEO-flower'
        fl.data.materials.append(petals[(i + row) % 3])

# palace wall + towers behind the garden
box('GEO-pwall', 64, 3, 7, MAT['wall'], location=(0, 54, 3.5))
for i in range(-4, 5):
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=11, location=(i * 7, 54, 5.5))
    t = bpy.context.active_object
    t.name = 'GEO-ptower'
    t.data.materials.append(MAT['wall'])
    bpy.ops.mesh.primitive_cone_add(radius1=2.2, depth=3, vertices=10, location=(i * 7, 54, 12.5))
    dm = bpy.context.active_object
    dm.name = 'GEO-pdome'
    dm.data.materials.append(MAT['dome'])

# river strip + basket
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 22, 0.05))
rv = bpy.context.active_object
rv.name = 'GEO-river'
rv.scale = (150, 16, 1)
rv.data.materials.append(MAT['water'])
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=0.7, location=(-14, 20, 0.3))
bk = bpy.context.active_object
bk.name = 'GEO-basket'
bk.data.materials.append(MAT['wood'])
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(-14, 20, 0.75))
bb = bpy.context.active_object
bb.name = 'GEO-baby'
bb.data.materials.append(MAT['skin'])

# lamps along the path
for i in range(8):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=2.2, location=(-28 + i * 8, -8, 1.1))
    lp = bpy.context.active_object
    lp.name = 'GEO-lamp'
    lp.data.materials.append(MAT['wood'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(-28 + i * 8, -8, 2.4))
    gl = bpy.context.active_object
    gl.name = 'GEO-lampglow'
    gl.data.materials.append(petals[2])

# trees flanking
trunk_me, canopy_me = tree_kit()
for _ in range(12):
    tree_at(trunk_me, canopy_me, MAT['trunk'], MAT['leaf'],
            -70 + rnd.random() * 25, -10 + rnd.random() * 30, 0.9 + rnd.random() * 0.8)
for _ in range(12):
    tree_at(trunk_me, canopy_me, MAT['trunk'], MAT['leaf'],
            45 + rnd.random() * 25, -10 + rnd.random() * 30, 0.9 + rnd.random() * 0.8)

bpy.ops.object.camera_add(location=(2, -6, 3.5))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (-10, 18, 1.0))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('flowers', (-6, 8, 1.0)), ('wall', (0, 54, 6.0)),
                  ('basket', (-14, 20, 0.5)), ('river', (-20, 22, 0.2))])

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
