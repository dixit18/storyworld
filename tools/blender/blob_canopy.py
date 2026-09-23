"""Bheem foliage pass: swap cone canopies for displaced blob masses (shared mesh per blend).
Usage: blender --background --python blob_canopy.py
Re-renders posters + Draco re-exports env GLBs.
"""
import glob
import math
import os
import random

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CH = os.path.join(ROOT, 'content', 'stories', 'mahabharata', 'chapter-01-adi-parva', 'assets')


def make_blob(seed):
    rnd = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.9, subdivisions=2, location=(0, 0, -200))
    ob = bpy.context.active_object
    me = ob.data
    me.name = 'GEO-canopy-blob'
    j1, j2, j3 = rnd.random() * 10, rnd.random() * 10, rnd.random() * 10
    for v in me.vertices:
        n = (math.sin(v.co.x * 2.1 + j1) + math.sin(v.co.y * 1.7 + j2) + math.sin(v.co.z * 2.3 + j3)) / 3.0
        k = 1.0 + 0.20 * n
        v.co.x *= k
        v.co.y *= k
        v.co.z *= k
        if v.co.z < -0.9:  # flatten the underside a touch
            v.co.z = -0.9 + (v.co.z + 0.9) * 0.4
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth()
    bpy.data.objects.remove(ob, do_unlink=True)
    return me


for bf in sorted(glob.glob(os.path.join(CH, 'blend', 'adi-*.blend'))):
    name = os.path.splitext(os.path.basename(bf))[0]
    bpy.ops.wm.open_mainfile(filepath=bf)
    canopies = [o for o in bpy.data.objects if o.name.startswith('GEO-tree-canopy')]
    if not canopies:
        print(f'{name}: no cone canopies, skip')
        continue
    blob = make_blob(abs(hash(name)) % (2 ** 31))
    old_meshes = {o.data for o in canopies}
    leaf_mat = None
    for m in old_meshes:
        if m.materials:
            leaf_mat = m.materials[0]
            break
    if leaf_mat:
        blob.materials.append(leaf_mat)
    for o in canopies:
        o.data = blob
    for m in old_meshes:
        if m.users == 0:
            bpy.data.meshes.remove(m)
    print(f'{name}: {len(canopies)} canopies -> blob')
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
    print('BLOB-DONE', name)
