"""Toon character kit: Bheem-bar archetypes (big head ~1:1 torso, bold eyes, solid colors).
Usage: blender --background --python chars_kit.py -- [sage|warrior|princess|king|preview]
Preview builds all four side-by-side and renders cast_preview.png (no export).
Coords: Blender-native (X right, Y forward, Z up). Characters face +Y.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import beautify, clean_scene, principled, setup_cycles, setup_view, use_gpu

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')

ARCHS = {
    'sage': dict(skin=(0.72, 0.52, 0.36, 1.0), cloth=(0.85, 0.78, 0.60, 1.0),
                 trim=(0.85, 0.35, 0.10, 1.0), beard=True, mukut=False, crown=False,
                 skirt='dhoti', staff=True, jewel=False, tripundra=True, rudraksha=True),
    'warrior': dict(skin=(0.62, 0.42, 0.30, 1.0), cloth=(0.55, 0.12, 0.10, 1.0),
                    trim=(0.75, 0.58, 0.18, 1.0), beard=False, mukut=True, crown=False,
                    skirt='dhoti', staff=False, jewel=True, bow=True),
    'princess': dict(skin=(0.55, 0.36, 0.26, 1.0), cloth=(0.60, 0.10, 0.12, 1.0),
                     trim=(0.78, 0.60, 0.20, 1.0), beard=False, mukut=False, crown=True,
                     skirt='saree', staff=False, jewel=True, bindi=True,
                     jhumkas=True, tikka=True, braid=True),
    'king': dict(skin=(0.66, 0.46, 0.32, 1.0), cloth=(0.45, 0.10, 0.35, 1.0),
                 trim=(0.78, 0.60, 0.20, 1.0), beard='short', mukut='big', crown=False,
                 skirt='robe', staff=False, jewel=True, shoulderpads=True, scepter=True),
    'strongman': dict(skin=(0.60, 0.40, 0.28, 1.0), cloth=(1.0, 0.48, 0.06, 1.0),
                      trim=(0.78, 0.60, 0.20, 1.0), beard=False, moustache=True, crop=True,
                      mukut=False, crown=False, skirt='dhoti', staff=False, jewel=False,
                      belly=True, gada=True),
}

SKIN = {}
CLOTH = {}
TRIM = {}
DARK = None


def mats(cfg, tag):
    global DARK
    skin = principled(f'MAT-{tag}-skin', base=cfg['skin'], roughness=0.6)
    cloth = principled(f'MAT-{tag}-cloth', base=cfg['cloth'], roughness=0.8)
    trim = principled(f'MAT-{tag}-trim', base=cfg['trim'], roughness=0.4, metallic=0.6)
    white = principled(f'MAT-{tag}-eye', base=(1, 1, 1, 1), roughness=0.4)
    pupil = principled(f'MAT-{tag}-pupil', base=(0.08, 0.06, 0.05, 1.0), roughness=0.4)
    hair = principled(f'MAT-{tag}-hair', base=(0.10, 0.08, 0.07, 1.0), roughness=0.9)
    catch = principled(f'MAT-{tag}-catch', base=(1, 1, 1, 1),
                       emission=(1.0, 1.0, 1.0), emission_strength=3.0)
    if DARK is None:
        DARK = principled('MAT-dark', base=(0.12, 0.10, 0.09, 1.0), roughness=0.8)
    return skin, cloth, trim, white, pupil, hair, catch


def ball(name, r, loc, mat, scale=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=20, ring_count=12, location=loc)
    o = bpy.context.active_object
    o.name = name
    if scale:
        o.scale = scale
    o.data.materials.append(mat)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    return o


def tube(name, r1, r2, h, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r1, depth=h, vertices=16, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = rot
    if r1 != r2:
        # taper via scale trick on top verts is overkill; use cone when very different
        pass
    o.data.materials.append(mat)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    return o


def boxp(name, sx, sy, sz, loc, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    o.data.materials.append(mat)
    return o


def build_person(arch, tag, ox=0.0):
    """Build one archetype at origin offset ox. Faces +Y. ~2.2 units tall."""
    cfg = ARCHS[arch]
    skin, cloth, trim, white, pupil, hair, catch = mats(cfg, tag)
    X = lambda v: v + ox

    # head + hair + face (the Bheem read: head nearly as big as torso)
    head = ball(f'GEO-{tag}-head', 0.55, (ox, 0, 1.55), skin, scale=(1.0, 0.92, 1.05))
    ball(f'GEO-{tag}-hair', 0.57, (ox, -0.06, 1.66), hair, scale=(1.0, 0.92, 0.82))
    for sx in (-0.20, 0.20):
        ball(f'GEO-{tag}-eye', 0.13, (X(sx), 0.44, 1.62), white)
        ball(f'GEO-{tag}-pupil', 0.06, (X(sx), 0.545, 1.62), pupil)
        ball(f'GEO-{tag}-catch', 0.025, (X(sx) - 0.035, 0.585, 1.66), catch)
        boxp(f'GEO-{tag}-brow', 0.20, 0.05, 0.06, (X(sx * 1.05), 0.47, 1.82), hair)
        ball(f'GEO-{tag}-ear', 0.11, (X(sx * 2.6), -0.02, 1.55), skin)
    boxp(f'GEO-{tag}-mouth', 0.22, 0.04, 0.06, (ox, 0.50, 1.40), DARK)
    boxp(f'GEO-{tag}-teeth', 0.16, 0.045, 0.05, (ox, 0.50, 1.44), white)
    if cfg.get('moustache'):
        for s in (-1, 1):
            mo = boxp(f'GEO-{tag}-moustache', 0.26, 0.09, 0.08, (ox + s * 0.15, 0.47, 1.50), hair)
            mo.rotation_euler = (0, 0, s * -0.25)
    if cfg.get('crop'):
        ball(f'GEO-{tag}-crop', 0.58, (ox, -0.10, 1.78), hair, scale=(1.0, 0.95, 0.62))
    if cfg.get('tripundra'):
        for i, dy in enumerate((0.0, 0.09, 0.18)):
            boxp(f'GEO-{tag}-tripundra', 0.30, 0.02, 0.035, (ox, 0.53, 1.86 + dy), white)
        ball(f'GEO-{tag}-tilakdot', 0.04, (ox, 0.535, 1.80), cloth)
    if cfg.get('bindi'):
        ball(f'GEO-{tag}-bindi', 0.045, (ox, 0.52, 1.72), cloth)
    if cfg.get('beard') is True:
        bpy.ops.mesh.primitive_cone_add(radius1=0.34, depth=0.75, vertices=12, location=(ox, 0.18, 1.12))
        b = bpy.context.active_object
        b.name = f'GEO-{tag}-beard'
        b.rotation_euler = (math.pi, 0, 0)
        b.data.materials.append(hair)
        # topknot
        ball(f'GEO-{tag}-knot', 0.14, (ox, -0.10, 2.16), hair)
    elif cfg.get('beard') == 'short':
        boxp(f'GEO-{tag}-beard', 0.4, 0.18, 0.3, (ox, 0.30, 1.28), hair)

    # neck + torso (+ belly for the strongman read)
    tube(f'GEO-{tag}-neck', 0.14, 0.14, 0.25, (ox, 0, 1.05), skin)
    tube(f'GEO-{tag}-torso', 0.34, 0.42, 0.70, (ox, 0, 0.72), cloth)
    if cfg.get('belly'):
        ball(f'GEO-{tag}-belly', 0.5, (ox, 0.12, 0.62), cloth, scale=(1.25, 1.0, 1.05))
        for s in (-1, 1):  # bigger arms
            ball(f'GEO-{tag}-bicep', 0.17, (X(s * 0.48), 0.02, 0.88), skin)

    # lower garment
    skirt = cfg['skirt']
    if skirt == 'dhoti':
        bpy.ops.mesh.primitive_cone_add(radius1=0.55, depth=0.62, vertices=14, location=(ox, 0, 0.28))
        d = bpy.context.active_object
        d.name = f'GEO-{tag}-dhoti'
        d.data.materials.append(cloth)
    elif skirt == 'saree':
        bpy.ops.mesh.primitive_cone_add(radius1=0.62, depth=1.05, vertices=16, location=(ox, 0, 0.10))
        d = bpy.context.active_object
        d.name = f'GEO-{tag}-saree'
        d.data.materials.append(cloth)
    else:  # robe
        bpy.ops.mesh.primitive_cone_add(radius1=0.60, depth=1.15, vertices=16, location=(ox, 0, 0.05))
        d = bpy.context.active_object
        d.name = f'GEO-{tag}-robe'
        d.data.materials.append(cloth)
    bpy.context.view_layer.objects.active = d
    bpy.ops.object.shade_smooth()
    # dhoti pleat fan + gold hem border (the read-from-3m trick)
    if skirt == 'dhoti':
        for i in range(5):
            pl = boxp(f'GEO-{tag}-pleat', 0.09, 0.05, 0.40, (ox - 0.18 + i * 0.09, 0.40, 0.28), cloth)
            pl.rotation_euler = (0, 0, (i - 2) * 0.12)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.035, location=(ox, 0, 0.02))
        hb = bpy.context.active_object
        hb.name = f'GEO-{tag}-hem'
        hb.data.materials.append(trim)
    else:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.60, minor_radius=0.035, location=(ox, 0, -0.36))
        hb = bpy.context.active_object
        hb.name = f'GEO-{tag}-hem'
        hb.data.materials.append(trim)

    # arms: shoulder balls + angled cylinders + hands
    for s in (-1, 1):
        ball(f'GEO-{tag}-shoulder', 0.15, (X(s * 0.42), 0, 0.98), cloth)
        arm = tube(f'GEO-{tag}-arm', 0.11, 0.10, 0.62, (X(s * 0.55), 0.02, 0.66), skin, rot=(0, s * 0.35, 0))
        ball(f'GEO-{tag}-hand', 0.13, (X(s * 0.66), 0.03, 0.36), skin)
        # legs + shoes
        tube(f'GEO-{tag}-leg', 0.12, 0.11, 0.42, (X(s * 0.20), 0, -0.05), skin)
        ball(f'GEO-{tag}-shoe', 0.15, (X(s * 0.20), 0.10, -0.24), scale=(1.0, 1.5, 0.7), mat=DARK)

    # headgear
    if cfg.get('mukut'):
        big = 1.25 if cfg['mukut'] == 'big' else 1.0
        tube(f'GEO-{tag}-mukut', 0.34 * big, 0.40 * big, 0.34, (ox, -0.02, 2.12), trim)
        for i in range(5):
            a = (i / 5) * math.pi
            bpy.ops.mesh.primitive_cone_add(radius1=0.07, depth=0.30, vertices=8,
                                            location=(ox + math.cos(a) * 0.30 * big, -0.02 + math.sin(a) * 0.10, 2.38))
            sp = bpy.context.active_object
            sp.name = f'GEO-{tag}-spike'
            sp.data.materials.append(trim)
        ball(f'GEO-{tag}-jewel', 0.09, (ox, 0.36, 2.14), trim)
    if cfg.get('crown'):
        tube(f'GEO-{tag}-crown', 0.30, 0.36, 0.26, (ox, -0.02, 2.08), trim)
        ball(f'GEO-{tag}-jewel', 0.08, (ox, 0.33, 2.10), trim)
    if cfg.get('jewel'):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.20, minor_radius=0.06, location=(ox, 0.30, 0.92))
        nl = bpy.context.active_object
        nl.name = f'GEO-{tag}-necklace'
        nl.data.materials.append(trim)
    if cfg.get('jhumkas'):
        for s in (-1, 1):
            ball(f'GEO-{tag}-jhumka', 0.07, (X(s * 0.62), -0.02, 1.42), trim)
            bpy.ops.mesh.primitive_cone_add(radius1=0.09, depth=0.14, vertices=10,
                                            location=(X(s * 0.62), -0.02, 1.32))
            jb = bpy.context.active_object
            jb.name = f'GEO-{tag}-jhumkbell'
            jb.rotation_euler = (math.pi, 0, 0)
            jb.data.materials.append(trim)
    if cfg.get('tikka'):
        boxp(f'GEO-{tag}-tikkachain', 0.03, 0.02, 0.22, (ox, 0.50, 1.90), trim)
        ball(f'GEO-{tag}-tikka', 0.05, (ox, 0.51, 1.78), trim)
    if cfg.get('braid'):
        for i in range(4):
            ball(f'GEO-{tag}-braid', 0.13 - i * 0.02, (ox, -0.55 - i * 0.03, 1.30 - i * 0.30), hair)
    if cfg.get('rudraksha'):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.045, location=(ox, 0.28, 0.88))
        rm = bpy.context.active_object
        rm.name = f'GEO-{tag}-rudraksha'
        rm.data.materials.append(hair)
    if cfg.get('shoulderpads'):
        for s in (-1, 1):
            ball(f'GEO-{tag}-pad', 0.20, (X(s * 0.48), 0, 1.02), cloth, scale=(1.0, 1.0, 0.7))
    if cfg.get('scepter'):
        tube(f'GEO-{tag}-scepter', 0.05, 0.05, 1.9, (ox - 0.85, 0.1, 0.75), trim)
        ball(f'GEO-{tag}-sceptertop', 0.11, (ox - 0.85, 0.1, 1.75), trim)
    if cfg.get('gada'):
        tube(f'GEO-{tag}-gada', 0.09, 0.11, 2.6, (ox + 0.95, 0.15, 0.9), trim)
        ball(f'GEO-{tag}-gadahead', 0.30, (ox + 0.95, 0.15, 2.30), trim)
    if cfg.get('staff'):
        tube(f'GEO-{tag}-staff', 0.05, 0.05, 2.6, (ox + 0.85, 0.1, 0.9), trim)
        ball(f'GEO-{tag}-stafftop', 0.11, (ox + 0.85, 0.1, 2.25), trim)
    if cfg.get('bow'):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.85, minor_radius=0.06, location=(ox + 0.80, 0.10, 1.0))
        bw = bpy.context.active_object
        bw.name = f'GEO-{tag}-bow'
        bw.rotation_euler = (0, math.pi / 2, 0.15)
        bw.data.materials.append(trim)

    # gentle bevel on hard parts for the cartoon-soft read
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name.startswith(f'GEO-{tag}-'):
            lname = ob.name.lower()
            if any(k in lname for k in ('eye', 'pupil', 'hair', 'beard', 'flame', 'star')):
                continue
            beautify(ob, 0.02, 0)


def main():
    argv = sys.argv
    arg = argv[argv.index('--') + 1] if '--' in argv else 'preview'
    print('GPU:', use_gpu())
    clean_scene()
    if arg == 'preview':
        from lib import setup_cycles, setup_view, sky_gradient, sun_light
        setup_cycles(gpu=True, samples=96)
        setup_view()
        sky_gradient(horizon=(0.55, 0.50, 0.55), mid=(0.30, 0.30, 0.38), zenith=(0.12, 0.14, 0.22),
                     below=(0.08, 0.08, 0.09))
        sun_light('GEO-key', energy=3.0, location=(20, 20, 30))
        import bpy as _b
        _b.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.45))
        fl = _b.context.active_object
        fl.name = 'GEO-floor'
        fl.scale = (30, 30, 1)
        from lib import principled
        fl.data.materials.append(principled('MAT-floor', base=(0.35, 0.33, 0.30, 1.0), roughness=0.9))
        for i, a in enumerate(['sage', 'warrior', 'princess', 'king', 'strongman']):
            build_person(a, a, ox=(i - 2) * 3.8)
        _b.ops.object.camera_add(location=(0, 18, 3.0))
        cam = _b.context.active_object
        cam.name = 'CAM-cast'
        cam.data.lens = 35
        from lib import aim_camera
        aim_camera(cam, (0, 0, 1.2))
        _b.context.scene.camera = cam
        _b.context.scene.render.filepath = os.path.join(CH, 'renders', 'cast_preview.png')
        _b.context.scene.render.image_settings.file_format = 'PNG'
        _b.ops.render.render(write_still=True)
        print('CAST-PREVIEW rendered')
    else:
        build_person(arg, arg, ox=0.0)
        out = os.path.join(CH, 'models', 'characters', arg + '.glb')
        bpy.ops.export_scene.gltf(
            filepath=out, export_format='GLB', export_apply=True, export_yup=True,
            export_cameras=False, export_lights=False,
            export_image_format='JPEG', export_jpeg_quality=80,
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14,
            export_draco_normal_quantization=10,
            export_draco_texcoord_quantization=12)
        print('EXPORTED', out)


main()
