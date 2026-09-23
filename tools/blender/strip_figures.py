"""Remove baked capsule crowds (replaced by Quaternius heroes at runtime).
Re-renders posters + Draco re-exports env GLBs.
Usage: blender --background --python strip_figures.py
"""
import glob
import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')

PATS = ('sage', 'priest', 'vyasa', 'drona', 'arjuna', 'guest', 'kaurava', 'pandava')

for bf in sorted(glob.glob(os.path.join(CH, 'blend', 'adi-*.blend'))):
    name = os.path.splitext(os.path.basename(bf))[0]
    only = os.environ.get('ONLY')
    if only and name != only:
        continue
    bpy.ops.wm.open_mainfile(filepath=bf)
    doomed = [o for o in bpy.data.objects
              if o.name.startswith('GEO-') and any(p in o.name.lower() for p in PATS)]
    for o in doomed:
        bpy.data.objects.remove(o, do_unlink=True)
    print(f'{name}: removed {len(doomed)} baked figures')
    scene = bpy.context.scene
    scene.render.filepath = os.path.join(CH, 'renders', name + '.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=bf)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(CH, 'models', name + '.glb'),
        export_format='GLB', export_apply=True, export_yup=True,
        export_cameras=False, export_lights=False,
        export_image_format='JPEG', export_jpeg_quality=80,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12)
    print('STRIP-DONE', name)
