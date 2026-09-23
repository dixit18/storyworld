"""Convert Quaternius FBX cast to GLB (rigs + animations + textures preserved, no Draco on skins).
Usage: blender --background --python convert_quaternius.py
"""
import glob
import os

import bpy

SRC = r'C:\Users\Dell\AppData\Local\Temp\opencode\rpg\RPG Characters - Nov 2020\FBX'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DEST = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets',
                    'models', 'cast')
os.makedirs(DEST, exist_ok=True)

MAP = {'Wizard': 'sage', 'Warrior': 'warrior', 'Cleric': 'king',
       'Monk': 'strongman', 'Ranger': 'ranger', 'Rogue': 'rogue'}

for fbx in sorted(glob.glob(os.path.join(SRC, '*.fbx'))):
    base = os.path.splitext(os.path.basename(fbx))[0]
    arch = MAP.get(base, base.lower())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx)
    # report animations
    clips = set()
    for a in bpy.data.actions:
        clips.add(a.name)
    out = os.path.join(DEST, arch + '.glb')
    bpy.ops.export_scene.gltf(
        filepath=out, export_format='GLB', export_apply=False, export_yup=True,
        export_skins=True, export_animations=True, export_cameras=False, export_lights=False,
        export_image_format='AUTO')
    tris = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH' and o.data)
    print(f'{arch}: {os.path.getsize(out) // 1024}KB tris={tris} clips={sorted(clips)[:8]}')
