"""Toon Rishi (sage) v1: modeled cartoon face, dhoti+shawl, beard, topknot,
rudraksha mala, danda staff. Bone-parented parts + 3s idle (bob, sway, blink).
Exports cast/sage.glb (Idle) + approval still.
Coords: Blender-native X right, Y forward(depth), Z up.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import aim_camera, clean_scene, frame_check, principled, setup_cycles, use_gpu  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')

print('GPU:', use_gpu())
clean_scene()

# ---------- materials ----------
MAT = {
    'skin': principled('MAT-sage-skin', base=(0.72, 0.52, 0.36, 1.0), roughness=0.8),
    'dhoti': principled('MAT-sage-dhoti', base=(0.93, 0.88, 0.76, 1.0), roughness=0.95),
    'border': principled('MAT-sage-border', base=(0.85, 0.45, 0.12, 1.0), roughness=0.9),
    'shawl': principled('MAT-sage-shawl', base=(0.78, 0.34, 0.12, 1.0), roughness=0.95),
    'beard': principled('MAT-sage-beard', base=(0.82, 0.82, 0.80, 1.0), roughness=1.0),
    'hair': principled('MAT-sage-hair', base=(0.16, 0.11, 0.09, 1.0), roughness=1.0),
    'rudra': principled('MAT-sage-rudra', base=(0.42, 0.24, 0.12, 1.0), roughness=0.9),
    'wood': principled('MAT-sage-wood', base=(0.35, 0.22, 0.12, 1.0), roughness=0.9),
    'white': principled('MAT-sage-eye', base=(1, 1, 1, 1), roughness=0.4),
    'pupil': principled('MAT-sage-pupil', base=(0.08, 0.06, 0.05, 1.0), roughness=0.4),
    'mouth': principled('MAT-sage-mouth', base=(0.30, 0.10, 0.08, 1.0), roughness=0.8),
    'tilak': principled('MAT-sage-tilak', base=(0.75, 0.15, 0.08, 1.0), roughness=0.8),
}


PENDING_PARENTS: list = []


def part(name, mat, parent_bone=None):
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    if parent_bone:
        PENDING_PARENTS.append((o.name, parent_bone))
    return o


def bone_parent_all():
    # Operator parenting computes the inverse correctly (direct parent_bone
    # assignment zeroes it and scatters parts). Run once, all parts exist.
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj_name, bone_name in PENDING_PARENTS:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[obj_name].select_set(True)
        amt.select_set(True)
        bpy.context.view_layer.objects.active = amt
        amt.data.bones.active = amt.data.bones[bone_name]
        bpy.ops.object.parent_set(type='BONE')


def ball(r, loc, sx=1, sy=1, sz=1, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=8, location=loc)
    o = bpy.context.active_object
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    return o


def cyl(r, depth, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=12, location=loc)
    o = bpy.context.active_object
    o.rotation_euler = rot
    bpy.ops.object.transform_apply(rotation=True)
    return o


def box(sx, sy, sz, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.scale = (sx, sy, sz)
    o.rotation_euler = rot
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return o


# ---------- armature ----------
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
amt = bpy.context.active_object
amt.name = 'RIG-sage'
eb = amt.data.edit_bones
eb['Bone'].name = 'hips'
hips = eb['hips']
hips.tail = (0, 0, 1.10)


def add_bone(name, head, tail, parent='hips'):
    b = eb.new(name)
    b.head = head
    b.tail = tail
    b.parent = eb[parent]
    return b


spine = add_bone('spine', (0, 0, 1.10), (0, 0, 1.38))
chest = add_bone('chest', (0, 0, 1.38), (0, 0, 1.50), parent='spine')
head = add_bone('head', (0, 0, 1.50), (0, 0, 1.86), parent='chest')
lidL = add_bone('lid.L', (0.085, 0.175, 1.79), (0.085, 0.20, 1.84), parent='head')
lidR = add_bone('lid.R', (-0.085, 0.175, 1.79), (-0.085, 0.20, 1.84), parent='head')
for side, sx in (('L', 1), ('R', -1)):
    sh = add_bone(f'shoulder.{side}', (0.14 * sx, 0, 1.44), (0.26 * sx, 0, 1.44), parent='chest')
    ua = add_bone(f'upperarm.{side}', (0.26 * sx, 0, 1.44), (0.28 * sx, 0, 1.10), parent=f'shoulder.{side}')
    fa = add_bone(f'forearm.{side}', (0.28 * sx, 0, 1.10), (0.295 * sx, 0.02, 0.82), parent=f'upperarm.{side}')
    add_bone(f'thigh.{side}', (0.11 * sx, 0, 0.95), (0.12 * sx, 0, 0.52))
    sn = add_bone(f'shin.{side}', (0.12 * sx, 0, 0.52), (0.12 * sx, 0.03, 0.10), parent=f'thigh.{side}')
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- body (heights in world Z; character faces +Y) ----------
# dhoti + border
part('dhoti', MAT['dhoti'], 'hips') if False else None
bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.85, vertices=18, location=(0, 0, 0.55))
dh = part('GEO-dhoti', MAT['dhoti'], 'hips')
bpy.ops.mesh.primitive_torus_add(major_radius=0.295, minor_radius=0.035, location=(0, 0, 0.93))
part('GEO-dhoti-border', MAT['border'], 'hips')
# torso (bare chest + sacred thread)
bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.48, vertices=16, location=(0, 0, 1.24))
part('GEO-torso', MAT['skin'], 'spine')
bpy.ops.mesh.primitive_torus_add(major_radius=0.195, minor_radius=0.018, location=(0, 0, 1.36))
th = part('GEO-thread', MAT['border'], 'spine')
th.rotation_euler = (0, 0, 0.5)
# shawl over left shoulder: flattened vertical roll, no hard box edges
bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.44, vertices=14, location=(-0.17, -0.02, 1.22))
sh = part('GEO-shawl', MAT['shawl'], 'chest')
sh.scale = (0.55, 1.25, 1.0)
sh.rotation_euler = (0, 0, 0.12)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
# rudraksha mala (hangs on the chest: ring plane faces forward)
bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.025, location=(0, 0.095, 1.36))
ml = part('GEO-mala', MAT['rudra'], 'chest')
ml.rotation_euler = (math.pi / 2, 0, 0)
bpy.ops.object.transform_apply(rotation=True)
for i, a in enumerate([0.5, 1.1, 2.0, 2.6, 3.6, 4.2, 5.1, 5.7]):
    bx = math.cos(a) * 0.12
    bz = 1.36 + math.sin(a) * 0.12
    part(f'b{i}', MAT['rudra']) if False else None
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.028, segments=8, ring_count=6,
                                         location=(bx, 0.095, bz))
    part(f'GEO-bead{i}', MAT['rudra'], 'chest')

# ---------- head + face (faces +Y) ----------
part('hx', MAT['skin']) if False else None
ball(0.21, (0, 0, 1.68), seg=16)
part('GEO-head', MAT['skin'], 'head')
# ears
for sx in (1, -1):
    ball(0.045, (0.20 * sx, 0, 1.68))
    part(f'GEO-ear{ sx}', MAT['skin'], 'head')
# eyes: white + pupil proud of the face, lids for blink
eyes = []
for sx in (1, -1):
    ball(0.052, (0.085 * sx, 0.175, 1.70), sy=0.55)
    part(f'GEO-eye{sx}', MAT['white'], 'head')
    ball(0.022, (0.085 * sx, 0.205, 1.70), sy=0.5)
    part(f'GEO-pupil{sx}', MAT['pupil'], 'head')
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.056, segments=12, ring_count=6,
                                         location=(0.085 * sx, 0.175, 1.715))
    lid = part(f'GEO-lid{sx}', MAT['skin'], f'lid.{"L" if sx == 1 else "R"}')
    lid.scale = (1, 0.55, 0.55)
    bpy.ops.object.transform_apply(scale=True)
    eyes.append(lid)
# brows sit on the skin above the eyes
for sx in (1, -1):
    part('bx', MAT['hair']) if False else None
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.085 * sx, 0.158, 1.79))
    br = part(f'GEO-brow{sx}', MAT['hair'], 'head')
    br.scale = (0.075, 0.03, 0.022)
    br.rotation_euler = (0, 0, -0.12 * sx)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
# nose + open smiling mouth + tilak
bpy.ops.mesh.primitive_cone_add(radius1=0.028, depth=0.07, location=(0, 0.215, 1.65))
nz = part('GEO-nose', MAT['skin'], 'head')
nz.rotation_euler = (math.pi / 2 + 0.25, 0, 0)
bpy.ops.object.transform_apply(rotation=True)
ball(0.05, (0, 0.238, 1.585), sx=1.1, sy=0.36, sz=0.64)
part('GEO-smile', MAT['mouth'], 'head')
part('tx', MAT['tilak']) if False else None
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.20, 1.755))
tk = part('GEO-tilak', MAT['tilak'], 'head')
tk.scale = (0.035, 0.012, 0.07)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
# beard + mustache + topknot
ball(0.16, (0, 0.10, 1.55), sx=1.05, sy=0.85, sz=1.25)
part('GEO-beard', MAT['beard'], 'head')
for sx in (1, -1):
    part('mx', MAT['beard']) if False else None
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.055 * sx, 0.232, 1.615))
    ms = part(f'GEO-mustache{sx}', MAT['beard'], 'head')
    ms.scale = (0.075, 0.035, 0.028)
    ms.rotation_euler = (0, 0, -0.25 * sx)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
ball(0.075, (0, -0.06, 1.90))
part('GEO-topknot', MAT['hair'], 'head')
cyl(0.025, 0.06, (0, -0.06, 1.865))
part('GEO-knot-tie', MAT['border'], 'head')

# ---------- limbs ----------
for sx in (1, -1):
    side = 'L' if sx == 1 else 'R'
    cyl(0.062, 0.36, (0.26 * sx, 0, 1.27))
    part(f'GEO-upperarm{side}', MAT['skin'], f'upperarm.{side}')
    # armlet on right upper arm
    if sx == -1:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.068, minor_radius=0.018,
                                         location=(0.26 * sx, 0, 1.36))
        part('GEO-armlet', MAT['border'], f'upperarm.{side}')
    cyl(0.052, 0.34, (0.285 * sx, 0.01, 0.98))
    part(f'GEO-forearm{side}', MAT['skin'], f'forearm.{side}')
    ball(0.06, (0.295 * sx, 0.02, 0.83))
    part(f'GEO-hand{side}', MAT['skin'], f'forearm.{side}')
    cyl(0.075, 0.45, (0.11 * sx, 0, 0.73))
    part(f'GEO-thigh{side}', MAT['skin'], f'thigh.{side}')
    cyl(0.06, 0.44, (0.12 * sx, 0.015, 0.31))
    part(f'GEO-shin{side}', MAT['skin'], f'shin.{side}')
    part('fx', MAT['skin']) if False else None
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.12 * sx, 0.06, 0.05))
    ft = part(f'GEO-foot{side}', MAT['skin'], f'shin.{side}')
    ft.scale = (0.11, 0.24, 0.09)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
# danda staff in right hand
cyl(0.028, 1.55, (-0.325, 0.04, 0.85))
part('GEO-staff', MAT['wood'], 'forearm.R')

bone_parent_all()

# ---------- idle animation (72f loop): bob, sway, head drift, blink ----------
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 72
action = bpy.data.actions.new('Idle')
amt.animation_data_create()
amt.animation_data.action = action
bpy.context.view_layer.objects.active = amt
pb = amt.pose.bones


def key(bone, prop, frame, value, index=0):
    # Set-then-insert works with Blender 5 layered actions; first and last
    # frames match so the exported clip loops seamlessly without modifiers.
    if prop == 'location':
        pb[bone].location[index] = value
    else:
        pb[bone].rotation_euler[index] = value
    pb[bone].keyframe_insert(prop, index=index, frame=frame)


for f, v in ((1, 0.0), (18, 0.03), (36, 0.0), (54, 0.03), (72, 0.0)):
    key('hips', 'location', f, v, index=2)
for f, v in ((1, 0), (18, 0.035), (36, 0), (54, -0.035), (72, 0)):
    key('spine', 'rotation_euler', f, v)
for f, v in ((1, 0), (18, -0.049), (36, 0.06), (54, 0.049), (72, 0)):
    key('head', 'rotation_euler', f, v)
for side in ('L', 'R'):
    for f, v in ((1, 0), (18, 0.05), (36, 0), (54, 0.05), (72, 0)):
        key(f'upperarm.{side}', 'rotation_euler', f, v if side == 'L' else -v)
# blink: lid bones swing down over the eyes twice per loop
for side in ('L', 'R'):
    for f, v in ((1, 0), (16, 0), (19, -1.15), (22, 0), (48, 0), (51, -1.15), (54, 0), (72, 0)):
        key(f'lid.{side}', 'rotation_euler', f, v)

# ---------- studio light + approval still ----------
setup_cycles(gpu=True, samples=64)
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.16, 0.14, 0.13, 1.0)
bg.inputs['Strength'].default_value = 1.0
bpy.ops.object.light_add(type='SUN', location=(4, -3, 6))
sun = bpy.context.active_object
sun.name = 'LGT-key'
sun.data.energy = 3.0
sun.data.color = (1.0, 0.9, 0.78)
bpy.ops.object.light_add(type='AREA', location=(-4, 2, 3))
fill = bpy.context.active_object
fill.name = 'LGT-fill'
fill.data.energy = 60.0
fill.data.color = (0.65, 0.75, 1.0)
fill.data.size = 3.0
bpy.ops.object.light_add(type='SUN', location=(-2, 4, 3))
rim = bpy.context.active_object
rim.name = 'LGT-rim'
rim.data.energy = 1.5
rim.data.color = (1.0, 0.75, 0.5)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -0.01))
fl = bpy.context.active_object
fl.name = 'GEO-floor'
fl.data.materials.append(principled('MAT-floor', base=(0.23, 0.20, 0.18, 1.0), roughness=1.0))
bpy.ops.object.camera_add(location=(2.0, 3.8, 1.6))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 50
aim_camera(cam, (0, 0, 0.95))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [('face', (0, 0, 1.68)), ('feet', (0, 0, 0.1))])
scene.render.filepath = os.path.join(CH, 'renders', 'cast_sage.png')
bpy.ops.render.render(write_still=True)
print('RENDERED cast_sage.png')

# ---------- export (subsurf baked: smooth clay-toon, not faceted primitives) ----------
bpy.ops.object.select_all(action='DESELECT')
fl.hide_render = True
skin_bsdf = MAT['skin'].node_tree.nodes.get('Principled BSDF')
if skin_bsdf and 'Subsurface Weight' in skin_bsdf.inputs:
    skin_bsdf.inputs['Subsurface Weight'].default_value = 0.35
if skin_bsdf and 'Subsurface Color' in skin_bsdf.inputs:
    skin_bsdf.inputs['Subsurface Color'].default_value = (0.72, 0.42, 0.28, 1.0)
HERO = ('head', 'beard', 'torso', 'dhoti', 'shawl', 'upperarm', 'forearm',
         'thigh', 'shin', 'mustache', 'topknot')
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith('GEO-'):
        mod = o.modifiers.new('Smooth', type='SUBSURF')
        lv = 2 if o.name.startswith(tuple('GEO-' + h for h in HERO)) else 1
        mod.levels = lv
        mod.render_levels = lv
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', 'cast_sage.blend'))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(CH, 'models', 'cast', 'sage.glb'),
    export_format='GLB', export_apply=True, export_yup=True,
    export_cameras=False, export_lights=False,
    export_animations=True, export_frame_range=True,
    export_image_format='JPEG', export_jpeg_quality=80,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14,
    export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=12)
print('EXPORTED cast/sage.glb')
print('TRIS:', sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH' and o.data))
