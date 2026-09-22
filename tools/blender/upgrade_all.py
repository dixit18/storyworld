"""Batch production upgrade: HDRI + PBR retarget + metallic fixes + beautify + final + Draco GLB.
Usage: blender --background --python upgrade_all.py -- [sid ...]  (default: all 12)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import beautify, load_hdri, pbr_from_maps, set_input, sky_gradient

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
VENDOR = os.path.join(HERE, 'vendor')
TX = os.path.join(VENDOR, 'textures')
HD = os.path.join(VENDOR, 'hdris')

# swaps: (old mat name, texture slug, mapping scale)
CONFIG = {
    'adi-01-naimisha': dict(hdri=('gradient', dict(horizon=(0.10, 0.20, 0.24), mid=(0.07, 0.13, 0.20), zenith=(0.02, 0.04, 0.10), below=(0.01, 0.02, 0.03))),
        swaps=[('MAT-trunk', 'bark_brown_01', 3), ('MAT-ground', 'forest_ground_04', 30)], samples=160),
    'adi-02-snake-sacrifice': dict(hdri=('gradient', dict(horizon=(0.30, 0.10, 0.08), mid=(0.12, 0.06, 0.08), zenith=(0.03, 0.02, 0.04), below=(0.02, 0.01, 0.01))),
        swaps=[('MAT-pillar', 'stone_wall_05', 2), ('MAT-floor', 'stone_wall_05', 8)],
        retune=[('MAT-trim', dict(Metallic=1.0, Roughness=0.35)), ('MAT-bowl', dict(Metallic=1.0, Roughness=0.3))],
        samples=160),
    'adi-03-ganga': dict(hdri=('bloem_field_sunrise.hdr', 0.9),
        swaps=[('MAT-bank', 'forest_ground_04', 30), ('MAT-stone', 'stone_wall_05', 3),
               ('MAT-wood', 'oak_wood_planks', 2), ('MAT-trunk', 'bark_brown_01', 3)],
        retune=[('MAT-gold', dict(Metallic=1.0, Roughness=0.3))], samples=160),
    'adi-04-bhishma-vow': dict(hdri=('brown_photostudio_02.hdr', 0.5),
        swaps=[('MAT-marble', 'marble_01', 6), ('MAT-pillar', 'marble_01', 2),
               ('MAT-darkwood', 'oak_wood_planks', 3)],
        retune=[('MAT-gold', dict(Metallic=1.0, Roughness=0.3))], samples=160),
    'adi-05-vyasa-line': dict(hdri=('brown_photostudio_02.hdr', 0.35),
        swaps=[('MAT-wood', 'oak_wood_planks', 2)], samples=160),
    'adi-06-births': dict(hdri=('kloppenheim_06_puresky.hdr', 1.0),
        swaps=[('MAT-grass', 'forest_ground_04', 40), ('MAT-wall', 'stone_wall_05', 6),
               ('MAT-wood', 'oak_wood_planks', 2), ('MAT-trunk', 'bark_brown_01', 3)], samples=160),
    'adi-07-drona': dict(hdri=('kloppenheim_06_puresky.hdr', 1.0),
        swaps=[('MAT-wood', 'oak_wood_planks', 2), ('MAT-stone', 'stone_wall_05', 2)], samples=160),
    'adi-08-lakshagriha': dict(hdri=('gradient', dict(horizon=(0.35, 0.12, 0.08), mid=(0.10, 0.05, 0.08), zenith=(0.02, 0.02, 0.04), below=(0.02, 0.01, 0.01))),
        swaps=[('MAT-wood', 'oak_wood_planks', 2), ('MAT-stone', 'stone_wall_05', 2)],
        coat=['MAT-wall'], samples=192),
    'adi-09-hidimba': dict(hdri=('gradient', dict(horizon=(0.06, 0.12, 0.11), mid=(0.03, 0.07, 0.08), zenith=(0.01, 0.02, 0.04), below=(0.01, 0.01, 0.01))),
        swaps=[('MAT-ground', 'forest_ground_04', 40), ('MAT-trunk', 'bark_brown_01', 3)], samples=192),
    'adi-10-swayamvara': dict(hdri=('kloppenheim_06_puresky.hdr', 0.9),
        swaps=[('MAT-floor', 'marble_01', 8), ('MAT-pillar', 'marble_01', 2),
               ('MAT-darkwood', 'oak_wood_planks', 3)],
        retune=[('MAT-gold', dict(Metallic=1.0, Roughness=0.3))], samples=160),
    'adi-11-division': dict(hdri=('kiara_9_dusk.hdr', 0.9),
        swaps=[('MAT-west', 'forest_ground_04', 8), ('MAT-wood', 'oak_wood_planks', 2),
               ('MAT-stone', 'stone_wall_05', 3)],
        retune=[('MAT-gold', dict(Metallic=1.0, Roughness=0.3))], samples=160),
    'adi-12-indraprastha': dict(hdri=('bloem_field_sunrise.hdr', 1.0),
        swaps=[('MAT-marble', 'marble_01', 4), ('MAT-ground', 'forest_ground_04', 40)],
        retune=[('MAT-gold', dict(Metallic=1.0, Roughness=0.3))], samples=192),
}

SKIP = ('ground', 'river', 'riverbed', 'bank', 'mist', 'smoke', 'flame', 'star',
        'firefly', 'eye', 'reed', 'bed', 'water', 'pool', 'rift', 'core', 'moon', 'glow', 'window')
SUBSURF = ('throne', 'palace', 'pillar', 'cradle', 'dais', 'shrine')

argv = sys.argv
argv = argv[argv.index('--') + 1:] if '--' in argv else []
sids = argv or list(CONFIG.keys())

for sid in sids:
    t0 = time.time()
    cfg = CONFIG[sid]
    bpy.ops.wm.open_mainfile(filepath=os.path.join(CH, 'blend', sid + '.blend'))
    hd = cfg['hdri']
    if hd[0] == 'gradient':
        sky_gradient(**hd[1])
        print(f'{sid}: gradient sky')
    else:
        load_hdri(os.path.join(HD, hd[0]), strength=hd[1])

    for old_name, slug, scale in cfg.get('swaps', []):
        old = bpy.data.materials.get(old_name)
        if old is None:
            print(f'{sid}: material {old_name} NOT FOUND, skip');
            continue
        new = pbr_from_maps(old_name + '_PBR', TX, slug, scale=scale)
        for ob in bpy.data.objects:
            if ob.type != 'MESH' or not ob.data.materials:
                continue
            for i, slot in enumerate(ob.data.materials):
                if slot == old:
                    ob.data.materials[i] = new
        if old.users == 0:
            bpy.data.materials.remove(old)
        print(f'{sid}: {old_name} -> {slug} x{scale}')

    for mat_name, props in cfg.get('retune', []):
        m = bpy.data.materials.get(mat_name)
        if m and m.use_nodes:
            bsdf = m.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                for k, v in props.items():
                    set_input(bsdf, k, v)
                print(f'{sid}: retuned {mat_name}')

    for mat_name in cfg.get('coat', []):
        m = bpy.data.materials.get(mat_name)
        if m and m.use_nodes:
            bsdf = m.node_tree.nodes.get('Principled BSDF')
            if bsdf:
                set_input(bsdf, 'Coat Weight', 0.8)
                set_input(bsdf, 'Coat Roughness', 0.08)
                print(f'{sid}: lacquer coat on {mat_name}')

    n_b = n_s = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or not ob.name.startswith('GEO-'):
            continue
        lname = ob.name.lower()
        if any(k in lname for k in SKIP):
            continue
        sub = 1 if any(k in lname for k in SUBSURF) else 0
        if beautify(ob, 0.025, sub):
            n_b += 1
            n_s += sub
    print(f'{sid}: beautified {n_b} meshes (+{n_s} subsurf)')

    scene = bpy.context.scene
    scene.cycles.samples = cfg.get('samples', 160)
    scene.render.filepath = os.path.join(CH, 'renders', sid + '.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', sid + '.blend'))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(CH, 'models', sid + '.glb'),
        export_format='GLB', export_apply=True, export_yup=True,
        export_cameras=False, export_lights=False,
        export_image_format='JPEG', export_jpeg_quality=85,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12)
    tris = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH' and o.data)
    print(f'{sid}: DONE tris={tris} in {time.time() - t0:.0f}s')
