"""Fast re-export: same .blends, JPEG-70 embedded textures + Draco (no re-render)."""
import glob
import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BLEND = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets', 'blend')
MODELS = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets', 'models')

total = 0
for bf in sorted(glob.glob(os.path.join(BLEND, 'adi-*.blend'))):
    name = os.path.splitext(os.path.basename(bf))[0]
    out = os.path.join(MODELS, name + '.glb')
    bpy.ops.wm.open_mainfile(filepath=bf)
    bpy.ops.export_scene.gltf(
        filepath=out,
        export_format='GLB', export_apply=True, export_yup=True,
        export_cameras=False, export_lights=False,
        export_image_format='JPEG', export_jpeg_quality=70,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12)
    kb = os.path.getsize(out) // 1024
    total += kb
    print(f'{name}: {kb}KB')
print(f'TOTAL: {total // 1024}MB')
