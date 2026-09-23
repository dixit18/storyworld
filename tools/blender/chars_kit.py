"""Own-kit cast v1: king, warrior (bow+quiver), strongman (mace), princess.
Shared rig + face library + 72f Idle with bone-blink. Tiered subsurf, Draco GLBs.
Usage: blender --background --python tools/blender/chars_kit.py [-- arch]
  arch in {king, warrior, strongman, princess} (default: all four).
Coords: Blender-native X right, Y forward(depth), Z up. Faces +Y.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import aim_camera, clean_scene, frame_check, principled, setup_cycles, use_gpu  # noqa: F401
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')

PENDING: list = []
MAT = {}
amt = None


def part(name, mat, parent_bone=None):
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    if parent_bone:
        PENDING.append((o.name, parent_bone))
    return o


def bone_parent_all():
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj_name, bone_name in PENDING:
        ob = bpy.data.objects.get(obj_name)
        if ob is None:
            print('MISSING-OBJ:', obj_name, 'bone:', bone_name,
                  'have:', sorted(o.name for o in bpy.data.objects if o.name.startswith('GEO-'))[:8], '...')
            continue
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        amt.select_set(True)
        bpy.context.view_layer.objects.active = amt
        amt.data.bones.active = amt.data.bones[bone_name]
        bpy.ops.object.parent_set(type='BONE')
    PENDING.clear()


def ball(r, loc, sx=1, sy=1, sz=1, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=8, location=loc)
    o = bpy.context.active_object
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    return o


def cyl(r, depth, loc, rot=(0, 0, 0), vert=12):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=vert, location=loc)
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


def rod(p1, p2, r, seg=8):
    a, b = Vector(p1), Vector(p2)
    d = (b - a).length
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=seg, location=(a + b) / 2)
    o = bpy.context.active_object
    o.rotation_euler = (d.normalized() if False else (b - a).normalized()).to_track_quat('Z', 'Y').to_euler()
    bpy.ops.object.transform_apply(rotation=True)
    return o


def M(name, base, rough=0.9):
    m = principled(name, base=base, roughness=rough)
    MAT[name] = m
    return m


def build_rig():
    global amt
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    amt = bpy.context.active_object
    amt.name = 'RIG-char'
    eb = amt.data.edit_bones
    eb['Bone'].name = 'hips'
    eb['hips'].head = (0, 0, 0.95)
    eb['hips'].tail = (0, 0, 1.10)

    def add(name, head, tail, parent='hips'):
        b = eb.new(name)
        b.head = head
        b.tail = tail
        b.parent = eb[parent]
        return b

    add('spine', (0, 0, 1.10), (0, 0, 1.38))
    add('chest', (0, 0, 1.38), (0, 0, 1.50), parent='spine')
    add('head', (0, 0, 1.50), (0, 0, 1.86), parent='chest')
    add('lid.L', (0.085, 0.175, 1.79), (0.085, 0.20, 1.84), parent='head')
    add('lid.R', (-0.085, 0.175, 1.79), (-0.085, 0.20, 1.84), parent='head')
    for side, sx in (('L', 1), ('R', -1)):
        add(f'shoulder.{side}', (0.14 * sx, 0, 1.44), (0.26 * sx, 0, 1.44), parent='chest')
        add(f'upperarm.{side}', (0.26 * sx, 0, 1.44), (0.28 * sx, 0, 1.10), parent=f'shoulder.{side}')
        add(f'forearm.{side}', (0.28 * sx, 0, 1.10), (0.295 * sx, 0.02, 0.82), parent=f'upperarm.{side}')
        add(f'thigh.{side}', (0.11 * sx, 0, 0.95), (0.12 * sx, 0, 0.52))
        add(f'shin.{side}', (0.12 * sx, 0, 0.52), (0.12 * sx, 0.03, 0.10), parent=f'thigh.{side}')
    bpy.ops.object.mode_set(mode='OBJECT')


def build_face(spec):
    """spec: skin, brow (stern tilt), mustache ('big','royal','thin','none'),
    beard ('full', color) or None, hair ('topknot','crown','band','cap','long'),
    bindi bool."""
    skin = M('MAT-face-skin', spec['skin'], 0.8)
    hairm = M('MAT-face-hair', spec.get('hair_color', (0.16, 0.11, 0.09, 1.0)), 1.0)
    white = M('MAT-face-eye', (1, 1, 1, 1), 0.4)
    pupil = M('MAT-face-pupil', (0.08, 0.06, 0.05, 1.0), 0.4)
    mouthm = M('MAT-face-mouth', (0.30, 0.10, 0.08, 1.0), 0.8)
    ball(0.21, (0, 0, 1.68), seg=16)
    part('GEO-head', skin, 'head')
    for sx in (1, -1):
        ball(0.045, (0.20 * sx, 0, 1.68))
        part(f'GEO-ear{sx}', skin, 'head')
        ball(0.062, (0.085 * sx, 0.175, 1.70), sy=0.55)
        part(f'GEO-eye{sx}', white, 'head')
        ball(0.028, (0.085 * sx, 0.205, 1.70), sy=0.5)
        part(f'GEO-pupil{sx}', pupil, 'head')
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.056, segments=12, ring_count=6,
                                             location=(0.085 * sx, 0.175, 1.715))
        lid = part(f'GEO-lid{sx}', skin, f'lid.{"L" if sx == 1 else "R"}')
        lid.scale = (1, 0.55, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.085 * sx, 0.158, 1.79))
        br = part(f'GEO-brow{sx}', hairm, 'head')
        br.scale = (0.075, 0.03, 0.022)
        br.rotation_euler = (0, 0, spec.get('brow', -0.12) * sx)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.mesh.primitive_cone_add(radius1=0.028, depth=0.07, location=(0, 0.215, 1.65))
    nz = part('GEO-nose', skin, 'head')
    nz.rotation_euler = (math.pi / 2 + 0.25, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    ball(0.05, (0, 0.238, 1.585), sx=1.1, sy=0.36, sz=0.64)
    part('GEO-smile', mouthm, 'head')
    if spec.get('bindi'):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.012, vertices=10,
                                            location=(0, 0.198, 1.755))
        part('GEO-bindi', M('MAT-face-bindi', (0.75, 0.12, 0.08, 1.0), 0.7), 'head')
    else:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.20, 1.755))
        tk = part('GEO-tilak', M('MAT-face-tilak', (0.75, 0.15, 0.08, 1.0), 0.8), 'head')
        tk.scale = (0.035, 0.012, 0.07)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    beard = spec.get('beard')
    if beard:
        ball(0.16, (0, 0.10, 1.55), sx=1.05, sy=0.85, sz=1.25)
        part('GEO-beard', M('MAT-face-beard', beard, 1.0), 'head')
    mm = spec.get('mustache', 'none')
    if mm != 'none':
        sc = {'big': (1.4, 1.2, 1.1), 'royal': (1.2, 1.0, 0.9), 'thin': (0.62, 0.7, 0.6)}.get(mm, (1, 1, 1))
        mcol = spec.get('mustache_color', (0.16, 0.11, 0.09, 1.0))
        for sx in (1, -1):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0.055 * sx, 0.232, 1.615))
            ms = part(f'GEO-mustache{sx}', M('MAT-face-mustache', mcol, 1.0), 'head')
            ms.scale = (0.075 * sc[0], 0.035 * sc[1], 0.028 * sc[2])
            ms.rotation_euler = (0, 0, -0.25 * sx)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    hair = spec.get('hair', 'topknot')
    if hair == 'topknot':
        ball(0.075, (0, -0.06, 1.90))
        part('GEO-topknot', hairm, 'head')
        cyl(0.025, 0.06, (0, -0.06, 1.865))
        part('GEO-knot-tie', M('MAT-face-tie', (0.85, 0.45, 0.12, 1.0), 0.9), 'head')
    elif hair == 'crown':
        bpy.ops.mesh.primitive_torus_add(major_radius=0.185, minor_radius=0.035, location=(0, 0, 1.80))
        part('GEO-crown', M('MAT-face-gold', (0.85, 0.62, 0.20, 1.0), 0.5), 'head')
        for i in range(5):
            a = (i / 5) * 2 * math.pi
            bpy.ops.mesh.primitive_cone_add(radius1=0.028, depth=0.11,
                                            location=(math.cos(a) * 0.185, math.sin(a) * 0.185, 1.89))
            part(f'GEO-spike{i}', MAT['MAT-face-gold'], 'head')
        ball(0.032, (0, 0.185, 1.83), seg=8)
        part('GEO-jewel', M('MAT-face-jewel', (0.75, 0.12, 0.12, 1.0), 0.3), 'head')
        ball(0.20, (0, -0.04, 1.70), sx=1.0, sy=1.0, sz=0.72)
        part('GEO-haircap', hairm, 'head')
    elif hair == 'band':
        bpy.ops.mesh.primitive_torus_add(major_radius=0.20, minor_radius=0.025, location=(0, 0, 1.76))
        part('GEO-headband', M('MAT-face-band', spec.get('band_color', (0.75, 0.2, 0.1, 1.0)), 0.9), 'head')
        ball(0.06, (0, -0.05, 1.90))
        part('GEO-topknot', hairm, 'head')
    elif hair == 'cap':
        ball(0.205, (0, -0.03, 1.70), sx=1.0, sy=1.0, sz=0.78)
        part('GEO-haircap', hairm, 'head')
    elif hair == 'long':
        ball(0.20, (0, -0.10, 1.64), sx=0.95, sy=0.80, sz=1.10)
        part('GEO-hairback', hairm, 'head')
        ball(0.07, (0, -0.15, 1.86))
        part('GEO-bun', hairm, 'head')


def limbs(skin, arm_r=1.0, leg_r=1.0):
    for sx in (1, -1):
        side = 'L' if sx == 1 else 'R'
        cyl(0.072 * arm_r, 0.36, (0.26 * sx, 0, 1.27))
        part(f'GEO-upperarm{side}', skin, f'upperarm.{side}')
        cyl(0.060 * arm_r, 0.34, (0.285 * sx, 0.05, 0.98))
        part(f'GEO-forearm{side}', skin, f'forearm.{side}')
        ball(0.068 * arm_r, (0.295 * sx, 0.10, 0.83))
        part(f'GEO-hand{side}', skin, f'forearm.{side}')
        cyl(0.085 * leg_r, 0.45, (0.11 * sx, 0, 0.73))
        part(f'GEO-thigh{side}', skin, f'thigh.{side}')
        cyl(0.068 * leg_r, 0.44, (0.12 * sx, 0.015, 0.31))
        part(f'GEO-shin{side}', skin, f'shin.{side}')
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.12 * sx, 0.06, 0.05))
        ft = part(f'GEO-foot{side}', skin, f'shin.{side}')
        ft.scale = (0.11 * leg_r, 0.24, 0.09)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def idle_keys():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 72
    action = bpy.data.actions.new('Idle')
    amt.animation_data_create()
    amt.animation_data.action = action
    bpy.context.view_layer.objects.active = amt
    pb = amt.pose.bones

    def key(bone, prop, frame, value, index=0):
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
    for side in ('L', 'R'):
        for f, v in ((1, 0), (16, 0), (19, -1.15), (22, 0), (48, 0), (51, -1.15), (54, 0), (72, 0)):
            key(f'lid.{side}', 'rotation_euler', f, v)


HERO = ('head', 'beard', 'torso', 'dhoti', 'skirt', 'kurta', 'shawl', 'cape',
        'upperarm', 'forearm', 'thigh', 'shin', 'mustache', 'topknot', 'hair')


def studio_and_shoot(tag):
    setup_cycles(gpu=True, samples=64)
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.16, 0.14, 0.13, 1.0)
    bg.inputs['Strength'].default_value = 1.0
    bpy.ops.object.light_add(type='SUN', location=(4, -3, 6))
    bpy.context.active_object.data.energy = 3.0
    bpy.context.active_object.data.color = (1.0, 0.9, 0.78)
    bpy.ops.object.light_add(type='AREA', location=(-4, 2, 3))
    a = bpy.context.active_object
    a.data.energy = 60.0
    a.data.color = (0.65, 0.75, 1.0)
    a.data.size = 3.0
    bpy.ops.object.light_add(type='SUN', location=(-2, 4, 3))
    bpy.context.active_object.data.energy = 1.5
    bpy.context.active_object.data.color = (1.0, 0.75, 0.5)
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
    bpy.context.scene.render.filepath = os.path.join(CH, 'renders', f'cast_{tag}.png')
    bpy.ops.render.render(write_still=True)
    print('RENDERED cast_' + tag + '.png')
    return fl


def export_cast(tag):
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith('GEO-'):
            mod = o.modifiers.new('Smooth', type='SUBSURF')
            lv = 2 if o.name.startswith(tuple('GEO-' + h for h in HERO)) else 1
            mod.levels = lv
            mod.render_levels = lv
    skinm = MAT.get('MAT-face-skin')
    if skinm:
        bsdf = skinm.node_tree.nodes.get('Principled BSDF')
        if bsdf and 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = 0.35
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', f'cast_{tag}.blend'))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(CH, 'models', 'cast', f'{tag}.glb'),
        export_format='GLB', export_apply=True, export_yup=True,
        export_cameras=False, export_lights=False,
        export_animations=True, export_frame_range=True,
        export_image_format='JPEG', export_jpeg_quality=80,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12)
    print('EXPORTED cast/' + tag + '.glb')
    print('TRIS:', sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH' and o.data))


# ============================== KING ==============================
def build_king():
    skin = M('MAT-king-skin', (0.68, 0.48, 0.33, 1.0), 0.8)
    kurta = M('MAT-king-kurta', (0.55, 0.12, 0.14, 1.0), 0.9)
    dhoti = M('MAT-king-dhoti', (0.90, 0.84, 0.70, 1.0), 0.95)
    border = M('MAT-king-border', (0.85, 0.62, 0.20, 1.0), 0.9)
    cape = M('MAT-king-cape', (0.45, 0.08, 0.12, 1.0), 0.95)
    gold = M('MAT-king-gold', (0.85, 0.62, 0.20, 1.0), 0.5)
    build_face({'skin': (0.68, 0.48, 0.33, 1.0), 'brow': -0.2, 'mustache': 'royal',
                'hair': 'crown', 'hair_color': (0.12, 0.09, 0.07, 1.0)})
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.48, vertices=16, location=(0, 0, 1.24))
    part('GEO-kurta', kurta, 'spine')
    cyl(0.10, 0.26, (0, 0, 1.54))
    part('GEO-neck', skin, 'chest')
    bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.022, location=(0, 0.095, 1.36))
    nl = part('GEO-necklace', gold, 'chest')
    nl.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    ball(0.035, (0, 0.095, 1.26), seg=8)
    part('GEO-pendant', M('MAT-king-jewel', (0.75, 0.12, 0.12, 1.0), 0.3), 'chest')
    bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.85, vertices=18, location=(0, 0, 0.55))
    part('GEO-dhoti', dhoti, 'hips')
    bpy.ops.mesh.primitive_torus_add(major_radius=0.295, minor_radius=0.05, location=(0, 0, 0.93))
    part('GEO-dhoti-border', border, 'hips')
    bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.44, vertices=14, location=(0.17, -0.02, 1.22))
    cp = part('GEO-cape', cape, 'chest')
    cp.scale = (0.55, 1.25, 1.0)
    cp.rotation_euler = (0, 0, -0.12)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    limbs(skin)
    for sx in (1, -1):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.068, minor_radius=0.018,
                                         location=(0.26 * sx, 0, 1.36))
        part(f'GEO-armlet{sx}', gold, f'upperarm.{"L" if sx == 1 else "R"}')


# ============================== WARRIOR ==============================
def build_warrior():
    skin = M('MAT-warrior-skin', (0.62, 0.44, 0.30, 1.0), 0.8)
    armor = M('MAT-warrior-armor', (0.55, 0.38, 0.20, 1.0), 0.55)
    cloth = M('MAT-warrior-dhoti', (0.20, 0.35, 0.22, 1.0), 0.95)
    wood = M('MAT-warrior-wood', (0.35, 0.22, 0.12, 1.0), 0.9)
    build_face({'skin': (0.62, 0.44, 0.30, 1.0), 'brow': -0.28, 'mustache': 'thin',
                'hair': 'band', 'band_color': (0.75, 0.2, 0.1, 1.0)})
    bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.46, vertices=16, location=(0, 0, 1.26))
    part('GEO-armor', armor, 'spine')
    cyl(0.10, 0.26, (0, 0, 1.54))
    part('GEO-neck', skin, 'chest')
    for i, z in enumerate((1.16, 1.30)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.205, minor_radius=0.018, location=(0, 0, z))
        part(f'GEO-plate{i}', M('MAT-warrior-dark', (0.35, 0.24, 0.13, 1.0), 0.6), 'spine')
    bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.55, vertices=14, location=(0, 0, 0.68))
    part('GEO-dhoti', cloth, 'hips')
    limbs(skin)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.068, minor_radius=0.018, location=(0.26, 0, 1.36))
    part('GEO-armlet1', armor, 'upperarm.L')
    # bow in left hand + quiver on back (proud of the torso, arrows over shoulder)
    rod((0.35, 0.02, 1.40), (0.35, 0.02, 0.86), 0.028)
    part('GEO-bow-upper', wood, 'forearm.L')
    rod((0.35, 0.02, 0.86), (0.35, 0.02, 0.32), 0.028)
    part('GEO-bow-lower', wood, 'forearm.L')
    rod((0.35, 0.02, 1.40), (0.35, 0.02, 0.32), 0.010)
    part('GEO-string', M('MAT-warrior-string', (0.85, 0.82, 0.72, 1.0), 0.9), 'forearm.L')
    cyl(0.07, 0.50, (0.18, -0.30, 1.25), rot=(0.15, 0, 0))
    part('GEO-quiver', wood, 'chest')
    for i, dx in enumerate((0.145, 0.18, 0.215)):
        rod((dx, -0.30, 1.30), (dx, -0.32, 1.74), 0.011)
        part(f'GEO-arrow{i}', wood, 'chest')


# ============================== STRONGMAN ==============================
def build_strongman():
    skin = M('MAT-strong-skin', (0.66, 0.47, 0.32, 1.0), 0.8)
    band = M('MAT-strong-band', (0.70, 0.15, 0.10, 1.0), 0.9)
    wood = M('MAT-strong-wood', (0.35, 0.22, 0.12, 1.0), 0.9)
    build_face({'skin': (0.66, 0.47, 0.32, 1.0), 'brow': -0.24, 'mustache': 'big',
                'hair': 'cap', 'hair_color': (0.10, 0.08, 0.06, 1.0)})
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.48, vertices=16, location=(0, 0, 1.24))
    part('GEO-torso', skin, 'spine')
    cyl(0.11, 0.28, (0, 0, 1.54))
    part('GEO-neck', skin, 'chest')
    bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.30, vertices=14, location=(0, 0, 0.90))
    part('GEO-langot', band, 'hips')
    limbs(skin, arm_r=1.15, leg_r=1.18)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.075, minor_radius=0.02, location=(0.26, 0, 1.36))
    part('GEO-armlet1', band, 'upperarm.L')
    # gada mace in right hand
    rod((-0.325, 0.04, 0.60), (-0.325, 0.04, 1.30), 0.035)
    part('GEO-mace-handle', wood, 'forearm.R')
    ball(0.13, (-0.325, 0.04, 1.40), seg=12)
    part('GEO-mace-head', wood, 'forearm.R')
    bpy.ops.mesh.primitive_torus_add(major_radius=0.085, minor_radius=0.02, location=(-0.325, 0.04, 1.30))
    part('GEO-mace-collar', band, 'forearm.R')


# ============================== PRINCESS ==============================
def build_princess():
    skin = M('MAT-princess-skin', (0.78, 0.58, 0.42, 1.0), 0.75)
    blouse = M('MAT-princess-blouse', (0.75, 0.15, 0.22, 1.0), 0.9)
    saree = M('MAT-princess-saree', (0.85, 0.30, 0.18, 1.0), 0.9)
    gold = M('MAT-princess-gold', (0.88, 0.66, 0.25, 1.0), 0.45)
    build_face({'skin': (0.78, 0.58, 0.42, 1.0), 'brow': -0.06, 'mustache': 'none',
                'hair': 'long', 'hair_color': (0.08, 0.06, 0.05, 1.0), 'bindi': True})
    bpy.ops.mesh.primitive_cylinder_add(radius=0.185, depth=0.46, vertices=16, location=(0, 0, 1.26))
    part('GEO-blouse', blouse, 'spine')
    cyl(0.09, 0.24, (0, 0, 1.53))
    part('GEO-neck', skin, 'chest')
    bpy.ops.mesh.primitive_cone_add(radius1=0.34, radius2=0.24, depth=1.0, vertices=18,
                                    location=(0, 0, 0.50))
    part('GEO-skirt', saree, 'hips')
    bpy.ops.mesh.primitive_torus_add(major_radius=0.235, minor_radius=0.035, location=(0, 0, 0.98))
    part('GEO-skirt-border', gold, 'hips')
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.40, vertices=12, location=(0.16, -0.02, 1.22))
    dr = part('GEO-drape', saree, 'chest')
    dr.scale = (0.55, 1.25, 1.0)
    dr.rotation_euler = (0, 0, -0.12)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.02, location=(0, 0.095, 1.36))
    nl = part('GEO-necklace', gold, 'chest')
    nl.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    limbs(skin, arm_r=0.9, leg_r=0.9)
    for sx in (1, -1):
        for i, z in enumerate((0.92, 0.97)):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.055, minor_radius=0.012,
                                             location=(0.285 * sx, 0.01, z))
            part(f'GEO-bangle{sx}{i}', gold, f'forearm.{"L" if sx == 1 else "R"}')


BUILDERS = {'king': build_king, 'warrior': build_warrior,
            'strongman': build_strongman, 'princess': build_princess}

if __name__ == '__main__' or True:
    want = [a for a in sys.argv[sys.argv.index('--') + 1:] if a in BUILDERS] if '--' in sys.argv else []
    todo = want or list(BUILDERS)
    print('GPU:', use_gpu())
    for tag in todo:
        clean_scene()
        MAT.clear()
        PENDING.clear()
        build_rig()
        BUILDERS[tag]()
        bone_parent_all()
        idle_keys()
        fl = studio_and_shoot(tag)
        fl.hide_render = True
        export_cast(tag)
