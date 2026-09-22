"""One-off fixes for adi-03: remove mist billboards, deepen water, calm HDRI."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import set_input

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SID = 'adi-03-ganga'

bpy.ops.wm.open_mainfile(filepath=os.path.join(CH, 'blend', SID + '.blend'))

removed = 0
for ob in list(bpy.data.objects):
    if 'mist' in ob.name.lower():
        bpy.data.objects.remove(ob, do_unlink=True)
        removed += 1
print('removed mist:', removed)

for mname in ('MAT-river',):
    m = bpy.data.materials.get(mname)
    if m and m.use_nodes:
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            set_input(bsdf, 'Base Color', (0.02, 0.09, 0.16, 1.0))
            set_input(bsdf, 'Roughness', 0.22)
            print('deepened', mname)

wt = bpy.context.scene.world.node_tree
for n in wt.nodes:
    if n.type == 'BACKGROUND':
        n.inputs['Strength'].default_value = 0.7
        print('hdri strength 0.7')

scene = bpy.context.scene
scene.render.filepath = os.path.join(CH, 'renders', SID + '.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', SID + '.blend'))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(CH, 'models', SID + '.glb'),
    export_format='GLB', export_apply=True, export_yup=True,
    export_cameras=False, export_lights=False,
    export_image_format='JPEG', export_jpeg_quality=85,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14,
    export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=12)
print('TWEAK-DONE', SID)
