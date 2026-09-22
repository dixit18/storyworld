"""Shared helpers for Storyworld Blender environment builds (Blender 5.x, background mode)."""
import math
import random

import bpy


def use_gpu():
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type in ('OPTIX', 'CUDA')
    return [d.name for d in prefs.devices if d.use]


def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for x in list(coll):
            coll.remove(x)


def principled(name, base=(0.8, 0.8, 0.8, 1.0), roughness=0.85, metallic=0.0,
               emission=None, emission_strength=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = base
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if transmission:
        bsdf.inputs['Transmission Weight'].default_value = transmission
    if emission is not None:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat


def mesh_obj(name, verts, faces, mat, location=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name + '_mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.location = location
    if mat:
        me.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def box(name, sx, sy, sz, mat, location=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (sx, sy, sz)
    if mat:
        ob.data.materials.append(mat)
    return ob


def bevel_subsurf(ob, bevel_width=0.03, levels=1):
    b = ob.modifiers.new('Bevel', type='BEVEL')
    b.width = bevel_width
    b.segments = 2
    b.limit_method = 'ANGLE'
    s = ob.modifiers.new('SubSurf', type='SUBSURF')
    s.levels = levels
    s.render_levels = levels + 1
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth()
    return ob


def aim_camera(cam, target):
    d = (mathutils_Vector(target) - cam.location)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def frame_check(cam, points):
    """Print normalized camera-space coords for landmarks. Inside frustum iff 0<=x,y<=1 and z>0."""
    from bpy_extras.object_utils import world_to_camera_view
    scene = bpy.context.scene
    for name, co in points:
        x, y, z = world_to_camera_view(scene, cam, mathutils_Vector(co))
        inside = (0.0 <= x <= 1.0) and (0.0 <= y <= 1.0)
        print(f'FRAME {name}: x={x:.2f} y={y:.2f} depth={z:.1f} inside={inside}')


def mathutils_Vector(v):
    from mathutils import Vector
    return Vector(v)


def setup_cycles(gpu=True, samples=96):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU' if gpu else 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX' if gpu else 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 6
    scene.cycles.transparent_max_bounces = 4
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False


def sky_world(sun_elevation=0.35, sun_rotation=1.2, turbidity=3.0):
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputWorld')
    bg = nodes.new('ShaderNodeBackground')
    sky = nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'PREETHAM'
    sky.turbidity = turbidity
    sky.sun_elevation = sun_elevation
    sky.sun_rotation = sun_rotation
    # warm dawn tint on the horizon via a hue shift on background strength
    bg.inputs['Strength'].default_value = 1.0
    links.new(sky.outputs[0], bg.inputs['Color'])
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    return world


def setup_view(transform='Filmic', look='Medium High Contrast', exposure=0.2):
    vs = bpy.context.scene.view_settings
    vs.view_transform = transform
    try:
        vs.look = look
    except TypeError:
        pass
    vs.exposure = exposure


def sky_gradient(horizon=(1.0, 0.52, 0.26), mid=(0.62, 0.45, 0.46),
                 zenith=(0.20, 0.36, 0.58), below=(0.13, 0.15, 0.17)):
    """Art-directable dawn gradient. Warm horizon -> mauve -> blue zenith."""
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputWorld')
    bg = nodes.new('ShaderNodeBackground')
    texco = nodes.new('ShaderNodeTexCoord')
    sep = nodes.new('ShaderNodeSeparateXYZ')
    ramp_in = nodes.new('ShaderNodeMapRange')
    ramp_in.inputs['From Min'].default_value = -0.06
    ramp_in.inputs['From Max'].default_value = 0.55
    ramp_in.inputs['To Min'].default_value = 0.0
    ramp_in.inputs['To Max'].default_value = 1.0
    ramp_in.clamp = True
    ramp = nodes.new('ShaderNodeValToRGB')
    els = ramp.color_ramp.elements
    els[0].position = 0.0
    els[0].color = (*below, 1.0)
    els[1].position = 1.0
    els[1].color = (*zenith, 1.0)
    e = els.new(0.10)
    e.color = (*horizon, 1.0)
    e = els.new(0.42)
    e.color = (*mid, 1.0)
    bg.inputs['Strength'].default_value = 1.0
    links.new(texco.outputs['Generated'], sep.inputs['Vector'])
    links.new(sep.outputs['Z'], ramp_in.inputs['Value'])
    links.new(ramp_in.outputs['Result'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    return world


def sun_light(name, energy=6.0, angle=0.5, location=(30, -20, 40)):
    bpy.ops.object.light_add(type='SUN', location=location)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.energy = energy
    ob.data.angle = angle
    return ob


def fire_light(name, location, energy=220.0, color=(1.0, 0.45, 0.15)):
    bpy.ops.object.light_add(type='POINT', location=location)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.energy = energy
    ob.data.color = color
    ob.data.shadow_soft_size = 0.6
    return ob


def set_input(node, name, value):
    """Blender 5.x: some BSDF inputs are enabled=False; iterate instead of key lookup."""
    for inp in node.inputs:
        if inp.name == name:
            inp.default_value = value
            return True
    return False


def load_hdri(path, strength=1.0, rotation_z=0.0):
    """Replace world with an HDRI environment."""
    import os
    assert os.path.exists(path), path
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputWorld')
    bg = nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = strength
    env = nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(path)
    links.new(env.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    return world


def pbr_from_maps(name, vendor_dir, slug, scale=2.0, normal_strength=0.6):
    """Principled PBR from Poly Haven 1K maps (diffuse sRGB, normal/rough Non-Color)."""
    import os
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    texco = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    set_input(mapping, 'Scale', (scale, scale, scale))
    nt.links.new(texco.outputs['Generated'], mapping.inputs['Vector'])
    set_input(bsdf, 'Metallic', 0.0)

    def img_node(fname, colorspace):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(os.path.join(vendor_dir, fname))
        n.image.colorspace_settings.name = colorspace
        nt.links.new(mapping.outputs['Vector'], n.inputs['Vector'])
        return n

    diff = img_node(f'{slug}_diffuse_1k.jpg', 'sRGB')
    nt.links.new(diff.outputs['Color'], bsdf.inputs['Base Color'])
    try:
        nor = img_node(f'{slug}_nor_gl_1k.jpg', 'Non-Color')
        nmap = nt.nodes.new('ShaderNodeNormalMap')
        nmap.inputs['Strength'].default_value = normal_strength
        nt.links.new(nor.outputs['Color'], nmap.inputs['Color'])
        nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    except Exception as e:
        print('no normal map:', e)
    try:
        rgh = img_node(f'{slug}_rough_1k.jpg', 'Non-Color')
        nt.links.new(rgh.outputs['Color'], bsdf.inputs['Roughness'])
    except Exception as e:
        print('no roughness map:', e)
    return mat


def beautify(ob, bevel_width=0.025, subsurf_levels=0):
    """Bevel (+optional Subsurf, bevel-first) + smooth shade. Idempotent."""
    if ob.type != 'MESH':
        return False
    if any(m.type == 'BEVEL' for m in ob.modifiers):
        return False
    try:
        b = ob.modifiers.new('BeautifyBevel', type='BEVEL')
        b.width = bevel_width
        b.segments = 2
        b.limit_method = 'ANGLE'
        if subsurf_levels:
            s = ob.modifiers.new('BeautifySubsurf', type='SUBSURF')
            s.levels = 0
            s.render_levels = subsurf_levels
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.shade_smooth()
        return True
    except Exception as e:
        print(f'beautify skip {ob.name}: {e}')
        return False


def tree_kit():
    """Create shared trunk/canopy meshes once; returns (trunk_me, canopy_me)."""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=2.6, location=(0, 0, -100))
    tob = bpy.context.active_object
    trunk_me = tob.data
    bpy.ops.mesh.primitive_cone_add(radius1=1.9, depth=3.6, vertices=8, location=(0, 0, -100))
    cob = bpy.context.active_object
    canopy_me = cob.data
    bpy.data.objects.remove(tob, do_unlink=True)
    bpy.data.objects.remove(cob, do_unlink=True)
    return trunk_me, canopy_me


def tree_at(trunk_me, canopy_me, trunk_mat, leaf_mat, x, d, s, leaf_tint=None):
    t = bpy.data.objects.new('GEO-tree-trunk', trunk_me)
    bpy.context.collection.objects.link(t)
    t.location = (x, d, 1.3 * s)
    t.scale = (s, s, s)
    t.data.materials.append(trunk_mat)
    lm = leaf_tint if leaf_tint is not None else leaf_mat
    for i, dy in enumerate((3.6, 5.4)):
        c = bpy.data.objects.new('GEO-tree-canopy', canopy_me)
        bpy.context.collection.objects.link(c)
        c.location = (x, d, dy * s)
        k = 1.0 - i * 0.28
        c.scale = (s * k, s * k, s * (1.0 - i * 0.2))
        if not c.data.materials:
            c.data.materials.append(lm)


def figure(name, color_mat, skin_mat, x, d, s=1.0, ry=0.0, h=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32 * s, depth=1.5 * s, location=(x, d, h + 0.75 * s))
    body = bpy.context.active_object
    body.name = name + '-body'
    body.rotation_euler = (0, 0, ry)
    body.data.materials.append(color_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24 * s, location=(x, d, h + 1.7 * s))
    head = bpy.context.active_object
    head.name = name + '-head'
    head.data.materials.append(skin_mat)
    return body


def flame_cone(name, x, d, z, rad, height, core_mat, inner_mat=None):
    bpy.ops.mesh.primitive_cone_add(radius1=rad, depth=height, vertices=8, location=(x, d, z))
    f = bpy.context.active_object
    f.name = name
    f.data.materials.append(core_mat)
    if inner_mat:
        bpy.ops.mesh.primitive_cone_add(radius1=rad * 0.55, depth=height * 0.7,
                                        vertices=8, location=(x, d, z - height * 0.1))
        f2 = bpy.context.active_object
        f2.name = name + '-core'
        f2.data.materials.append(inner_mat)
    return f


def fire_pit(name, x, d, s, stone_mat, wood_mat, flame_mat, core_mat, light_energy=220.0):
    for i in range(8):
        a = (i / 8) * 2 * math.pi
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.32 * s,
                                              location=(x + math.cos(a) * 1.3 * s, d + math.sin(a) * 1.3 * s, 0.2))
        st = bpy.context.active_object
        st.name = name + f'-stone{i}'
        st.data.materials.append(stone_mat)
    for i in range(4):
        a = (i / 4) * 2 * math.pi + 0.4
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16 * s, depth=2.2 * s,
                                            location=(x + math.cos(a) * 0.5 * s, d + math.sin(a) * 0.5 * s, 0.35 * s))
        log = bpy.context.active_object
        log.name = name + f'-log{i}'
        log.rotation_euler = (0, math.pi / 2, -a)
        log.data.materials.append(wood_mat)
    flame_cone(name + '-flame', x, d, 1.4 * s, 0.75 * s, 2.4 * s, flame_mat, core_mat)
    return fire_light(name + '-light', (x, d, 2.4 * s), energy=light_energy)


def star_spheres(n, seed, r_min=90, r_max=160, z_min=40):
    rnd = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.7, subdivisions=1, location=(0, 0, -200))
    base = bpy.context.active_object
    star_me = base.data
    star_mat = principled('MAT-star', base=(1, 1, 1, 1), emission=(0.95, 0.95, 1.0),
                          emission_strength=3.0)
    for i in range(n):
        a = rnd.random() * 2 * math.pi
        rr = r_min + rnd.random() * (r_max - r_min)
        st = bpy.data.objects.new('GEO-star', star_me)
        bpy.context.collection.objects.link(st)
        st.location = (math.cos(a) * rr, math.sin(a) * rr, z_min + rnd.random() * 60)
        if not st.data.materials:
            st.data.materials.append(star_mat)
    bpy.data.objects.remove(base, do_unlink=True)


def pillar(name, x, d, z_base, h, rad, mat, trim_mat):
    box(name + '-base', rad * 3, rad * 3, 0.5, trim_mat, location=(x, d, z_base + 0.25))
    bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=h, location=(x, d, z_base + 0.5 + h / 2))
    p = bpy.context.active_object
    p.name = name
    p.data.materials.append(mat)
    box(name + '-cap', rad * 3.2, rad * 3.2, 0.6, trim_mat, location=(x, d, z_base + 0.8 + h))
    return p
