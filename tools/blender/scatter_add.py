"""Scatter pass: grass tufts + rocks + far silhouette trees for outdoor scenes.
Usage: blender --background --python scatter_add.py
Re-renders + Draco re-exports each touched scene.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import principled, tree_at, tree_kit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')

SCENES = ['adi-01-naimisha', 'adi-06-births', 'adi-07-drona',
          'adi-09-hidimba', 'adi-11-division', 'adi-12-indraprastha']

for sid in SCENES:
    rnd = random.Random(hash(sid) % (2 ** 31))
    bpy.ops.wm.open_mainfile(filepath=os.path.join(CH, 'blend', sid + '.blend'))
    tuft_mat = principled(f'MAT-{sid}-tuft', base=(0.10, 0.26, 0.10, 1.0), roughness=1.0)
    rock_mat = principled(f'MAT-{sid}-srock', base=(0.32, 0.31, 0.29, 1.0), roughness=0.95)
    dark_leaf = principled(f'MAT-{sid}-darkleaf', base=(0.05, 0.12, 0.08, 1.0), roughness=1.0)
    dark_trunk = principled(f'MAT-{sid}-darktrunk', base=(0.12, 0.08, 0.06, 1.0), roughness=1.0)

    for i in range(44):  # grass tufts
        a = rnd.random() * 2 * math.pi
        d = 6 + rnd.random() * 54
        x, y = math.cos(a) * d, math.sin(a) * d
        bpy.ops.mesh.primitive_cone_add(radius1=0.10 + rnd.random() * 0.10, depth=0.45 + rnd.random() * 0.4,
                                        vertices=5, location=(x, y, 0.25))
        t = bpy.context.active_object
        t.name = f'GEO-tuft{i}'
        t.rotation_euler = (0, 0, rnd.random() * 3)
        t.data.materials.append(tuft_mat)
    for i in range(8):  # rocks
        a = rnd.random() * 2 * math.pi
        d = 10 + rnd.random() * 48
        s = 0.3 + rnd.random() * 0.9
        bpy.ops.mesh.primitive_ico_sphere_add(radius=s, subdivisions=1,
                                              location=(math.cos(a) * d, math.sin(a) * d, s * 0.45))
        rk = bpy.context.active_object
        rk.name = f'GEO-srock{i}'
        rk.scale = (1.0 + rnd.random() * 0.6, 0.8 + rnd.random() * 0.5, 0.55)
        rk.data.materials.append(rock_mat)

    trunk_me, canopy_me = tree_kit()  # far silhouettes
    for i in range(14):
        a = (i / 14) * 2 * math.pi + rnd.random() * 0.3
        d = 72 + rnd.random() * 18
        tree_at(trunk_me, canopy_me, dark_trunk, dark_leaf,
                math.cos(a) * d, math.sin(a) * d, 1.6 + rnd.random() * 1.2)

    scene = bpy.context.scene
    scene.render.filepath = os.path.join(CH, 'renders', sid + '.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', sid + '.blend'))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(CH, 'models', sid + '.glb'),
        export_format='GLB', export_apply=True, export_yup=True,
        export_cameras=False, export_lights=False,
        export_image_format='JPEG', export_jpeg_quality=80,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12)
    print('SCATTER-DONE', sid)
