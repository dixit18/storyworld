"""Night scenes: flat dark background colors (gradient mapping unreliable in 5.2).
Stars/moon meshes already in-scene carry the sky. Re-renders stills only (no geo change).
Usage: blender --background --python fix_night_sky.py
"""
import os
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')

NIGHT = {
    'adi-01-naimisha': (0.015, 0.030, 0.060),
    'adi-02-snake-sacrifice': (0.050, 0.015, 0.015),
    'adi-08-lakshagriha': (0.050, 0.020, 0.015),
    'adi-09-hidimba': (0.010, 0.030, 0.025),
}

for sid, color in NIGHT.items():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(CH, 'blend', sid + '.blend'))
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputWorld')
    bg = nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (*color, 1.0)
    bg.inputs['Strength'].default_value = 1.0
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    scene = bpy.context.scene
    scene.render.filepath = os.path.join(CH, 'renders', sid + '.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', sid + '.blend'))
    print('NIGHT-FIXED', sid)
