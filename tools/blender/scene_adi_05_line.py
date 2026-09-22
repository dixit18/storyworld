"""adi-05 The poet born of the river: dim chamber, three cradles, oil lamp, sage doorway.
Coords are Blender-native: X right, Y forward(depth), Z up.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, box, clean_scene, figure, fire_light, flame_cone,
                 frame_check, principled, setup_cycles, setup_view, sky_gradient,
                 sun_light, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SID = 'adi-05-vyasa-line'

print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient(horizon=(0.16, 0.12, 0.18), mid=(0.08, 0.07, 0.12), zenith=(0.03, 0.03, 0.06),
             below=(0.02, 0.02, 0.03))
sun_light('GEO-fill', energy=0.9, location=(0, 20, 20))

MAT = {
    'floor': principled('MAT-floor', base=(0.13, 0.12, 0.16, 1.0), roughness=0.9),
    'wall': principled('MAT-wall', base=(0.10, 0.10, 0.14, 1.0), roughness=0.95),
    'wood': principled('MAT-wood', base=(0.30, 0.20, 0.12, 1.0), roughness=0.85),
    'cover': principled('MAT-cover', base=(0.05, 0.05, 0.08, 1.0), roughness=1.0),
    'pale': principled('MAT-pale', base=(0.75, 0.68, 0.60, 1.0), roughness=0.7),
    'skin': principled('MAT-skin', base=(0.65, 0.48, 0.36, 1.0), roughness=0.8),
    'sage': principled('MAT-sage', base=(0.04, 0.04, 0.06, 1.0), roughness=1.0),
    'glow': principled('MAT-glow', base=(1, 1, 1, 1), emission=(0.45, 0.32, 0.55), emission_strength=1.6),
    'flame': principled('MAT-flame', base=(1, 1, 1, 1), emission=(1.0, 0.60, 0.18), emission_strength=5.0),
    'drape': principled('MAT-drape', base=(0.20, 0.12, 0.24, 1.0), roughness=0.95),
}

box('GEO-floor', 34, 34, 0.6, MAT['floor'], location=(0, 0, 0.3))
box('GEO-rearwall', 34, 1.2, 10, MAT['wall'], location=(0, -16.5, 5))
box('GEO-sidewall', 1.2, 34, 10, MAT['wall'], location=(-16.5, 0, 5))
box('GEO-doorway', 5.0, 0.5, 7.5, MAT['glow'], location=(0, -15.7, 4.1))

# three cradles: covered (blind), pale, plain
for i, cx in enumerate((-7, 0, 7)):
    box(f'GEO-cradle{i}', 2.6, 1.4, 1.0, MAT['wood'], location=(cx, -4, 1.1))
    for dx in (-0.8, 0.8):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.1, minor_radius=0.12, location=(cx + dx, -4, 0.6))
        rk = bpy.context.active_object
        rk.name = f'GEO-rocker{i}'
        rk.rotation_euler = (0, math.pi / 2, 0)
        rk.data.materials.append(MAT['wood'])
    if i == 0:
        box(f'GEO-cover{i}', 2.7, 1.5, 0.9, MAT['cover'], location=(cx, -4, 1.95))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(cx, -4, 1.75))
        baby = bpy.context.active_object
        baby.name = f'GEO-baby{i}'
        baby.data.materials.append(MAT['pale'] if i == 1 else MAT['skin'])

# Vyasa silhouette in the glowing doorway
figure('GEO-vyasa', MAT['sage'], MAT['sage'], 0, -12.8, s=1.7, ry=0.0)
# oil lamp + drape
bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.5, location=(5, 4, 0.9))
bowl = bpy.context.active_object
bowl.name = 'GEO-lampbowl'
bowl.data.materials.append(MAT['wood'])
flame_cone('GEO-lampflame', 5, 4, 1.5, 0.18, 0.6, MAT['flame'])
fire_light('GEO-lamplight', (5, 4, 2.2), energy=60.0, color=(1.0, 0.62, 0.25))
box('GEO-drape', 8.0, 0.3, 9.0, MAT['drape'], location=(-10, -15.8, 5.0))

bpy.ops.object.camera_add(location=(8, 11, 2.8))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (0, -6, 1.4))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('cradles', (0, -4, 1.4)), ('vyasa', (0, -12.8, 2.5)),
                  ('lamp', (5, 4, 1.4)), ('doorway', (0, -15.7, 4.1))])

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
