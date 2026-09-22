"""Pilot: adi-03 Ganga riverbank at dawn. Builds, renders keyframe, saves .blend, exports .glb.
Run: blender --background --python scene_adi_03_ganga.py

NOTE (Blender coords): X right, Y forward(depth), Z up.
Use P(x, h, d) -> (x, d, h) to author in story coords (x right, h height, d depth).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import (aim_camera, bevel_subsurf, box, clean_scene, frame_check,
                 principled, setup_cycles, setup_view, sky_gradient, sun_light, use_gpu)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # storyworld/
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')
SEED = 30303
rnd = random.Random(SEED)


def P(x, h, d):
    """Story coords (right, height, depth) -> Blender coords (X, Y, Z)."""
    return (x, d, h)


print('GPU:', use_gpu())
clean_scene()
setup_cycles(gpu=True, samples=96)
setup_view()
sky_gradient()
sun_light('GEO-sun', energy=3.2, location=(30, -48, 22))


# ---------- materials ----------
def mat_water():
    mat = principled('MAT-river', base=(0.04, 0.12, 0.20, 1.0), roughness=0.30,
                     metallic=0.05, transmission=0.0)
    nt = mat.node_tree
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 6.0
    noise.inputs['Detail'].default_value = 3.0
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bsdf = nt.nodes.get('Principled BSDF')
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


MAT = {
    'water': mat_water(),
    'bank': principled('MAT-bank', base=(0.10, 0.22, 0.12, 1.0), roughness=1.0),
    'stone': principled('MAT-stone', base=(0.40, 0.36, 0.28, 1.0), roughness=0.85),
    'wood': principled('MAT-wood', base=(0.30, 0.20, 0.12, 1.0), roughness=0.85),
    'leaf': principled('MAT-leaf', base=(0.10, 0.30, 0.14, 1.0), roughness=0.95),
    'trunk': principled('MAT-trunk', base=(0.25, 0.17, 0.11, 1.0), roughness=0.95),
    'plaster': principled('MAT-plaster', base=(0.82, 0.78, 0.66, 1.0), roughness=0.8),
    'gold': principled('MAT-gold', base=(0.79, 0.64, 0.15, 1.0), roughness=0.35, metallic=0.8),
    'darkpal': principled('MAT-darkpal', base=(0.10, 0.13, 0.18, 1.0), roughness=1.0),
    'saffron': principled('MAT-saffron', base=(0.85, 0.35, 0.08, 1.0), roughness=0.85),
    'skin': principled('MAT-skin', base=(0.78, 0.58, 0.44, 1.0), roughness=0.7),
    'reed': principled('MAT-reed', base=(0.20, 0.33, 0.16, 1.0), roughness=0.95),
}


def vnoise(x, z):
    def h(ix, iz):
        n = math.sin(ix * 127.1 + iz * 311.7) * 43758.5453
        return n - math.floor(n)

    ix, iz = math.floor(x), math.floor(z)
    fx, fz = x - ix, z - iz
    sx, sz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    return (h(ix, iz) * (1 - sx) + h(ix + 1, iz) * sx) * (1 - sz) + \
           (h(ix, iz + 1) * (1 - sx) + h(ix + 1, iz + 1) * sx) * sz


# ---------- river: plane 170 wide (X) x 90 deep (Y), water at Z=0 ----------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -10, 0))
river = bpy.context.active_object
river.name = 'GEO-river'
river.scale = (170, 90, 1)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=40)
bpy.ops.object.mode_set(mode='OBJECT')
river.data.materials.append(MAT['water'])

# dark riverbed so the water reads deep blue, not sky mirror
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -10, -0.8))
bed = bpy.context.active_object
bed.name = 'GEO-riverbed'
bed.scale = (170, 90, 1)
bed.data.materials.append(principled('MAT-riverbed', base=(0.03, 0.10, 0.14, 1.0), roughness=1.0))

# ---------- banks (near: depth 15..45, far: depth -67..-37, tops ~Z=1) ----------
def bank(name, cx, cd, w, d):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cd, 1.0))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (w, d, 1)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=24)
    bpy.ops.object.mode_set(mode='OBJECT')
    me = ob.data
    for v in me.vertices:
        wx = v.co.x * w + cx
        wy = v.co.y * d + cd
        v.co.z += (vnoise(wx * 0.25, wy * 0.25) - 0.5) * 1.6
    me.materials.append(MAT['bank'])
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth()
    return ob


bank('GEO-bank-near', 0, 30, 170, 30)
bank('GEO-bank-far', 0, -52, 170, 30)

# ---------- ghat steps descending into the river (moved near center) ----------
bpy.ops.mesh.primitive_cube_add(size=1, location=P(-10, 1.2, 14))
step = bpy.context.active_object
step.name = 'GEO-ghat-step'
step.scale = (9, 1.7, 0.5)
step.data.materials.append(MAT['stone'])
arr = step.modifiers.new('Array', type='ARRAY')
arr.fit_type = 'FIXED_COUNT'
arr.count = 6
arr.relative_offset_displace = (0, -1.02, -0.7)
bevel_subsurf(step, bevel_width=0.04, levels=0)

# ---------- shrine on the near bank (moved near center) ----------
box('GEO-shrine-base', 10, 8, 1.2, MAT['stone'], location=P(6, 2.0, 27))
for dx, side in ((-3.4, 'L'), (3.4, 'R')):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=6.4, location=P(6 + dx, 4.4, 27))
    pil = bpy.context.active_object
    pil.name = f'GEO-shrine-pillar{side}'
    pil.data.materials.append(MAT['plaster'])
    bevel_subsurf(pil, bevel_width=0.06, levels=1)
box('GEO-shrine-beam', 9.4, 1.2, 1.0, MAT['wood'], location=P(6, 8.0, 27))
bpy.ops.mesh.primitive_cone_add(radius1=5.4, depth=3.0, vertices=4, location=P(6, 9.4, 27))
roof = bpy.context.active_object
roof.name = 'GEO-shrine-roof'
roof.rotation_euler = (0, 0, math.pi / 4)
roof.data.materials.append(MAT['saffron'])
box('GEO-shrine-pole', 0.12, 0.12, 2.6, MAT['wood'], location=P(6, 12.0, 27))
box('GEO-shrine-cloth', 1.6, 0.06, 1.0, MAT['saffron'], location=P(6.9, 12.6, 27))

# ---------- trees (shared trunk/canopy meshes, linked duplicates) ----------
bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=2.6, location=(0, 0, -50))
trunk_ob = bpy.context.active_object
trunk_me = trunk_ob.data
bpy.ops.mesh.primitive_cone_add(radius1=1.9, depth=3.6, vertices=8, location=(0, 0, -50))
canopy_ob = bpy.context.active_object
canopy_me = canopy_ob.data
# remove ONLY the two template objects (keep their meshes for linking)
bpy.data.objects.remove(trunk_ob, do_unlink=True)
bpy.data.objects.remove(canopy_ob, do_unlink=True)


def tree_at(x, d, s):
    t = bpy.data.objects.new('GEO-tree-trunk', trunk_me)
    bpy.context.collection.objects.link(t)
    t.location = (x, d, 1.3 * s)
    t.scale = (s, s, s)
    t.data.materials.append(MAT['trunk'])
    for i, dy in enumerate((3.6, 5.4)):
        c = bpy.data.objects.new('GEO-tree-canopy', canopy_me)
        bpy.context.collection.objects.link(c)
        c.location = (x, d, dy * s)
        k = 1.0 - i * 0.28
        c.scale = (s * k, s * k, s * (1.0 - i * 0.2))
        if not c.data.materials:
            c.data.materials.append(MAT['leaf'])


for _ in range(16):
    x = -80 + rnd.random() * 160
    d = 34 + rnd.random() * 10
    if abs(x - 2) < 9:  # keep the camera corridor + shrine sightline clear
        continue
    tree_at(x, d, 0.8 + rnd.random() * 1.1)
for _ in range(14):
    tree_at(-80 + rnd.random() * 160, -62 + rnd.random() * 18, 0.9 + rnd.random() * 1.2)

# ---------- palace silhouette on the far bank (small, off-axis) ----------
box('GEO-palace-main', 22, 7, 10, MAT['darkpal'], location=P(-48, 5, -72))
box('GEO-palace-tower', 10, 7, 16, MAT['darkpal'], location=P(-32, 8, -72))
bpy.ops.mesh.primitive_cone_add(radius1=4.2, depth=4.6, vertices=4, location=P(-32, 18.5, -72))
dome = bpy.context.active_object
dome.name = 'GEO-palace-dome'
dome.rotation_euler = (0, 0, math.pi / 4)
dome.data.materials.append(MAT['gold'])
for i, lx in enumerate((-56, -48, -40)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=P(lx, 5 + (i % 2), -68.4))
    win = bpy.context.active_object
    win.name = f'GEO-palace-window{i}'
    win.data.materials.append(
        principled(f'MAT-win{i}', base=(1, 1, 1, 1), emission=(1.0, 0.72, 0.3), emission_strength=4.0))

# ---------- basket with the kept child, floating ----------
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=0.7, location=P(6, 0.25, -8))
basket = bpy.context.active_object
basket.name = 'GEO-basket'
basket.data.materials.append(MAT['wood'])
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=P(6, 0.68, -8))
baby = bpy.context.active_object
baby.name = 'GEO-baby'
baby.data.materials.append(MAT['skin'])

# ---------- reeds along both waterlines ----------
for _ in range(46):
    x = -80 + rnd.random() * 160
    d = 13.5 + rnd.random() * 2.5 if rnd.random() > 0.45 else -36.5 - rnd.random() * 2.5
    h = 1.6 + rnd.random() * 1.6
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=h, location=(x, d, 0.2 + h / 2))
    rd = bpy.context.active_object
    rd.name = 'GEO-reed'
    rd.data.materials.append(MAT['reed'])

# ---------- low mist billboards over the water ----------
mist_mat = principled('MAT-mist', base=(0.85, 0.88, 0.92, 1.0), roughness=1.0)
mist_mat.blend_method = 'BLEND'
mist_mat.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value = 0.05
for i in range(3):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-40 + i * 40, -26 - (i % 2) * 6, 1.0))
    mp = bpy.context.active_object
    mp.name = f'GEO-mist{i}'
    mp.scale = (34, 16, 1)
    mp.rotation_euler = (math.pi / 2 - 0.12, 0, 0.06 * (i - 2))
    mp.data.materials.append(mist_mat)

# ---------- hero camera on the near bank ----------
bpy.ops.object.camera_add(location=(-4, 52, 14.0))
cam = bpy.context.active_object
cam.name = 'CAM-hero'
cam.data.lens = 40
aim_camera(cam, (4, -16, 1.0))
bpy.context.scene.camera = cam
bpy.context.view_layer.update()
frame_check(cam, [
    ('ghats', (-10, 10, 1.0)),
    ('shrine', (6, 27, 5.0)),
    ('basket', (6, -8, 0.5)),
    ('palace', (-40, -72, 8.0)),
    ('water-mid', (0, -20, 0.0)),
])

# ---------- outputs ----------
scene = bpy.context.scene
scene.render.filepath = os.path.join(CH, 'renders', 'adi-03-ganga.png')
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print('RENDERED:', scene.render.filepath)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CH, 'blend', 'adi-03-ganga.blend'))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(CH, 'models', 'adi-03-ganga.glb'),
    export_format='GLB', export_apply=True, export_yup=True,
    export_cameras=False, export_lights=False,
)
print('EXPORTED GLB')
print('TRIS:', sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH' and o.data))
