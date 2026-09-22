"""Re-export every chapter .blend as Draco-compressed GLB (no re-render).
Run: blender --background --python reexport_draco.py
"""
import glob
import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BLEND = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets', 'blend')
MODELS = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets', 'models')

total_before = total_after = 0
for bf in sorted(glob.glob(os.path.join(BLEND, 'adi-*.blend'))):
    name = os.path.splitext(os.path.basename(bf))[0]
    out = os.path.join(MODELS, name + '.glb')
    before = os.path.getsize(out) if os.path.exists(out) else 0
    bpy.ops.wm.open_mainfile(filepath=bf)
    bpy.ops.export_scene.gltf(
        filepath=out,
        export_format='GLB', export_apply=True, export_yup=True,
        export_cameras=False, export_lights=False,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12,
    )
    after = os.path.getsize(out)
    total_before += before
    total_after += after
    print(f'{name}: {before / 1024:.0f}KB -> {after / 1024:.0f}KB')
print(f'TOTAL: {total_before / 1024:.0f}KB -> {total_after / 1024:.0f}KB')
