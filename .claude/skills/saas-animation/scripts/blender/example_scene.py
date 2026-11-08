# A tiny working scene: a white product turns and flies back on one light. Copy it and swap in the real object. Make the mesh first: python3 example_scene.py mesh
# Render: blender -b -P example_scene.py -- frames 1280 24 [flat] [times...]
import sys, os; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if len(sys.argv) > 1 and sys.argv[1] == 'mesh':
    import numpy as np, mesh_from_sdf as M
    def body(x, y, z): return M.smin(M.ellipsoid(x, y, z, 0.7, 0.56, 0.54), M.pill(x, y, z, -1.9, -0.25, 0.2, 0.15), 0.16)
    def slot(x, y, z): e = np.sqrt(np.maximum(np.abs(y + 0.1) - 0.2, 0) ** 2 + x ** 2) - 0.07; p = body(x, y, z); return np.maximum(np.maximum(p - 0.004, e), np.maximum(-(p + 0.012), -z))
    M.nets(body, (-0.9, -2.0, -0.7), (0.9, 0.7, 0.7), 0.01, 'body', os.path.join(HERE, 'example_mesh')); M.nets(slot, (-0.2, -0.5, 0), (0.2, 0.3, 0.7), 0.005, 'slot', os.path.join(HERE, 'example_mesh')); sys.exit()
import kit, tracks as T, math
from mathutils import Euler
OUT, WIDTH, SAMPLES, FLAT, TIMES = kit.args(); END, FPS = 4.0, 25
kit.fresh(); sc = kit.setup(WIDTH, SAMPLES, FPS)
white = kit.mat('white', (0.86, 0.86, 0.85), 0.2, coat=0.6, sss=0.12); black = kit.mat('black', (0.012, 0.012, 0.014), 0.5)
root = kit.empty('root'); root.rotation_quaternion = Euler((math.pi / 2, 0, 0)).to_quaternion()   # the meshes are y-up; Blender is z-up
g = kit.empty('product', root); M = os.path.join(HERE, 'example_mesh'); kit.load_npz(M + '/body.npz', white, g); kit.load_npz(M + '/slot.npz', black, g, smooth=0)
cam = kit.camera(); cam.data.lens = 70; kit.key_light((-10, -10, 11), target=(0, 0, 0))
if FLAT: kit.flat_mode(black_materials=('black',))
ry = T.mono([(0, -1.2), (2.0, 0.2), (END, 0.5)]); dist = T.mono([(0, 5), (1.2, 8), (END, 12)])   # the turn and the pull-back never reverse
def setf(t): g.rotation_quaternion = Euler((0.1, ry(t), -0.5), 'XYZ').to_quaternion(); kit.look_at(cam, (0, -dist(t), 0.3), (0, 0, -0.4))
kit.render(setf, [g, cam], END, FPS, OUT, TIMES)
