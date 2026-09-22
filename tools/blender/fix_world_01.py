"""Fix adi-01 world: clear sequencer, rebuild night gradient with verified links, render."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SID = 'adi-01-naimisha'

bpy.ops.wm.open_mainfile(filepath=os.path.join(CH, 'blend', SID + '.blend'))
scene = bpy.context.scene

print('strips:', [s.name for s in scene.sequence_editor.strips_all] if scene.sequence_editor else [])

world = scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()
out = nodes.new('ShaderNodeOutputWorld')
bg = nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 1.0
texco = nodes.new('ShaderNodeTexCoord')
sep = nodes.new('ShaderNodeSeparateXYZ')
mr = nodes.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = -0.06
mr.inputs['From Max'].default_value = 0.55
mr.inputs['To Min'].default_value = 0.0
mr.inputs['To Max'].default_value = 1.0
mr.clamp = True
ramp = nodes.new('ShaderNodeValToRGB')
els = ramp.color_ramp.elements
els[0].position = 0.0
els[0].color = (0.01, 0.02, 0.03, 1.0)
els[1].position = 1.0
els[1].color = (0.02, 0.04, 0.10, 1.0)
e = els.new(0.10)
e.color = (0.10, 0.20, 0.24, 1.0)
e = els.new(0.42)
e.color = (0.07, 0.13, 0.20, 1.0)
links.new(texco.outputs['Generated'], sep.inputs['Vector'])
links.new(sep.outputs['Z'], mr.inputs['Value'])
links.new(mr.outputs['Result'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], out.inputs['Surface'])
print('world links:', len(world.node_tree.links))
assert len(world.node_tree.links) == 5

scene.render.filepath = os.path.join(CH, 'renders', SID + '.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', SID + '.blend'))
print('WORLD-FIXED', SID)
