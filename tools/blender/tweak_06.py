"""One-off for adi-06: brighten mossy stone wall toward limestone."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SID = 'adi-06-births'

bpy.ops.wm.open_mainfile(filepath=os.path.join(CH, 'blend', SID + '.blend'))

m = bpy.data.materials.get('MAT-wall_PBR')
assert m is not None
nt = m.node_tree
bsdf = nt.nodes.get('Principled BSDF')
# find the diffuse image node feeding Base Color
src = None
for link in nt.links:
    if link.to_node == bsdf and link.to_socket.name == 'Base Color':
        src = link.from_node
        break
assert src is not None, 'diffuse source not found'
mix = nt.nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MIX'
mix.inputs[0].default_value = 0.55
mix.inputs[2].default_value = (0.78, 0.72, 0.58, 1.0)
nt.links.new(src.outputs['Color'], mix.inputs[1])
nt.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
for n in nt.nodes:
    if n.type == 'NORMAL_MAP':
        n.inputs['Strength'].default_value = 0.3
print('wall brightened')

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
