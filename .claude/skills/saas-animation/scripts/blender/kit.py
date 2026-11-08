# Helpers for a Blender + Cycles product ad, run with no window: blender -b -P your_scene.py -- <out dir> <width> <samples> [flat] [times...]
# Your scene imports this, builds objects, then calls render(setf, end, fps, ...). Finished frames are skipped, so a crashed render resumes where it stopped.
import bpy, sys, os, math, numpy as np
from mathutils import Vector, Quaternion, Euler
def args():
    a = sys.argv[sys.argv.index('--') + 1:]; flat = 'flat' in a; a = [x for x in a if x != 'flat']; return a[0], int(a[1]), int(a[2]), flat, [float(x) for x in a[3:]]
def fresh(): bpy.ops.wm.read_factory_settings(use_empty=True); return bpy.context.scene
def mat(name, base, rough=0.3, coat=0.0, metal=0.0, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value = (*base, 1); p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal; p.inputs['Coat Weight'].default_value = coat; p.inputs['Subsurface Weight'].default_value = sss; return m
def empty(name, parent=None): sc = bpy.context.scene; o = bpy.data.objects.new(name, None); sc.collection.objects.link(o); o.parent = parent; o.rotation_mode = 'QUATERNION'; return o
def load_npz(path, m, parent=None, smooth=20):   # a mesh made with mesh_from_sdf.py
    d = np.load(path); name = os.path.basename(path)[:-4]; me = bpy.data.meshes.new(name); V = d['v'].astype(np.float32); Q = d['f'].astype(np.int32); me.vertices.add(len(V)); me.vertices.foreach_set('co', V.ravel()); me.loops.add(len(Q) * 4); me.loops.foreach_set('vertex_index', Q.ravel()); me.polygons.add(len(Q)); me.polygons.foreach_set('loop_start', np.arange(len(Q), dtype=np.int32) * 4); me.polygons.foreach_set('loop_total', np.full(len(Q), 4, dtype=np.int32)); me.update(calc_edges=True); me.validate(); me.polygons.foreach_set('use_smooth', np.ones(len(Q), dtype=bool)); me.update(); me.materials.append(m); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.parent = parent
    if smooth: s = o.modifiers.new('sm', 'SMOOTH'); s.factor = 0.6; s.iterations = smooth
    return o
def load_model(path, parent=None):   # a real model: .glb, .gltf or .obj. Returns the new objects
    before = set(bpy.data.objects); e = path.lower().rsplit('.', 1)[-1]; (bpy.ops.import_scene.gltf(filepath=path) if e in ('glb', 'gltf') else bpy.ops.wm.obj_import(filepath=path)); new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if parent is not None and o.parent is None: o.parent = parent
    return new
def key_light(loc, size=(7, 9), power=4200, target=(0, 0, 0)):   # the one light source. One light is most of what makes it look cinematic
    d = bpy.data.lights.new('key', 'AREA'); d.shape = 'RECTANGLE'; d.size, d.size_y = size; d.energy = power; o = bpy.data.objects.new('key', d); bpy.context.scene.collection.objects.link(o); o.location = loc; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y'); return o
def camera(): sc = bpy.context.scene; c = bpy.data.cameras.new('cam'); o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); sc.camera = o; o.rotation_mode = 'QUATERNION'; return o
def setup(width, samples, fps, world=0.002):
    sc = bpy.context.scene; sc.world = bpy.data.worlds.new('w'); sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs[0].default_value = (world, world, world, 1); sc.render.engine = 'CYCLES'; pr = bpy.context.preferences.addons['cycles'].preferences; sc.cycles.device = 'CPU'
    for kind in ('METAL', 'OPTIX', 'CUDA', 'HIP', 'ONEAPI'):   # uses whichever GPU this computer has, or the CPU if none
        try:
            pr.compute_device_type = kind; pr.get_devices(); ds = [d for d in pr.devices if d.type == kind]
            if ds:
                for d in pr.devices: d.use = d.type == kind
                sc.cycles.device = 'GPU'; break
        except Exception: pass
    print('Rendering on', sc.cycles.device, flush=True); sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.04; sc.cycles.max_bounces = 4; sc.render.resolution_x = width; sc.render.resolution_y = width * 9 // 16; sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.file_format = 'PNG'; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5; sc.render.fps = fps; sc.render.use_persistent_data = True; sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; return sc
def flat_mode(black_materials=()):   # the silhouette look: pure white, with only the named materials staying black. No shading, lines or texture
    sc = bpy.context.scene
    def emit(name, v):
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (v, v, v, 1); o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0]); return m
    w, k = emit('flatwhite', 1), emit('flatblack', 0)
    for o in list(bpy.data.objects):
        if o.type == 'FONT': o.hide_render = True
        elif o.type == 'MESH' and o.data.materials: n = o.data.materials[0].name.split('.')[0]; o.data.materials[0] = k if n in black_materials else w
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.cycles.use_denoising = False; sc.cycles.use_adaptive_sampling = False; sc.render.dither_intensity = 0; sc.cycles.filter_width = 1.5
def look_at(cam_obj, eye, target, roll=0.0): cam_obj.location = eye; cam_obj.rotation_quaternion = (Vector(target) - Vector(eye)).to_track_quat('-Z', 'Y') @ Quaternion((0, 0, 1), roll)
def keyframe(animated, f):   # keys location, rotation and scale. Keeps quaternions on the short path so nothing spins the long way round
    for o in animated:
        q = o.rotation_quaternion.copy(); prev = o.get('_q')
        if prev is not None and Quaternion(prev).dot(q) < 0: o.rotation_quaternion = Quaternion((-q.w, -q.x, -q.y, -q.z))
        o['_q'] = list(o.rotation_quaternion); o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_quaternion', frame=f); o.keyframe_insert('scale', frame=f)
def render(setf, animated, end, fps, out, times=()):
    sc = bpy.context.scene; N = int(end * fps)
    for i in range(N + 1): setf(i / (N - 1) * end); keyframe(animated, i + 1)
    for o in animated:
        act = o.animation_data.action if o.animation_data else None
        for fc in (getattr(act, 'fcurves', None) or []):
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    frames = [round(t / end * (N - 1)) + 1 for t in times] if times else range(1, N + 1); os.makedirs(out, exist_ok=True)
    for f in frames:
        p = os.path.join(out, f'{f:04d}.png')
        if os.path.exists(p) and os.path.getsize(p) > 0: continue
        sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('FRAME', f, flush=True)
