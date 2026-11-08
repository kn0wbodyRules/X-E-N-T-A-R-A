# Build smooth meshes from distance functions when you have no 3D model of the product. Runs on plain Python + numpy + scipy, not inside Blender.
# Write your shape as f(x, y, z) -> distance (negative inside), then nets(f, lo, hi, step, 'name', out_dir). The result is name.npz, which kit.load_npz() reads.
import numpy as np, os
from scipy.ndimage import map_coordinates
def smin(a, b, k): h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1); return b * (1 - h) + a * h - k * h * (1 - h)   # smooth union
def smax(a, b, k): return -smin(-a, -b, k)   # smooth cut: smax(shape, -hole, k)
def ellipsoid(x, y, z, rx, ry, rz): k0 = np.sqrt((x / rx) ** 2 + (y / ry) ** 2 + (z / rz) ** 2); k1 = np.sqrt((x / rx ** 2) ** 2 + (y / ry ** 2) ** 2 + (z / rz ** 2) ** 2) + 1e-9; return k0 * (k0 - 1) / k1
def pill(x, y, z, y0, y1, a, b): qy = np.maximum(np.maximum(y0 - y, y - y1), 0); kx = np.abs(x) - a + b; d = np.sqrt(np.maximum(kx, 0) ** 2 + z ** 2) - b; return np.sqrt(np.maximum(d, 0) ** 2 + qy ** 2) + np.minimum(d, 0) * (qy <= 0)   # a vertical rounded bar
def rounded_pocket(x, y, z, a, b, ry, p=3.2): return (((np.abs(x / a) ** p + np.abs(z / b) ** p) ** (2 / p) + (y / ry) ** 2) ** 0.5 - 1) * min(a, ry) * 0.8   # a squarish scooped recess
def polygon_2d(u, v, P):
    u, v = np.broadcast_arrays(u, v); d = np.full(u.shape, 1e9); inside = np.zeros(u.shape, bool)
    for i in range(len(P)):
        a, b = P[i], P[i - 1]; e = b - a; wx, wy = u - a[0], v - a[1]; h = np.clip((wx * e[0] + wy * e[1]) / (e @ e), 0, 1); d = np.minimum(d, (wx - e[0] * h) ** 2 + (wy - e[1] * h) ** 2); c1 = v >= a[1]; c2 = v < b[1]; c3 = e[0] * wy > e[1] * wx; inside ^= (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
    return np.sqrt(d) * np.where(inside, -1, 1)
def chaikin(P, n=4):   # rounds a polygon profile so it has no facets; the first and last two points stay fixed
    for _ in range(n):
        Q = [P[0], P[1]]
        for i in range(1, len(P) - 3): Q += [0.75 * P[i] + 0.25 * P[i + 1], 0.25 * P[i] + 0.75 * P[i + 1]]
        P = np.array(Q + [P[-2], P[-1]])
    return P
def revolve(P, rmax=1.5, zmin=-1.5, zmax=1.5, res=600):   # returns f(x, y, z) for a profile of (radius, z) points spun round the z axis: bells, caps, buttons, bottles
    r = np.linspace(-rmax, rmax, res); zz = np.linspace(zmin, zmax, res); R, Z = np.meshgrid(r, zz, indexing='ij'); T = polygon_2d(R, Z, np.asarray(P, float))
    def f(x, y, z):
        Rr = np.sqrt(x ** 2 + y ** 2); Rr, Zb = np.broadcast_arrays(Rr, z); return map_coordinates(T, [((Rr + rmax) / (2 * rmax) * (res - 1)).ravel(), ((Zb - zmin) / (zmax - zmin) * (res - 1)).ravel()], order=1, mode='nearest').reshape(Rr.shape).astype(np.float32)
    return f
def nets(fn, lo, hi, st, name, out='mesh'):
    os.makedirs(out, exist_ok=True); xs = [np.arange(lo[i], hi[i] + st, st, dtype=np.float32) for i in range(3)]; X, Y, Z = np.meshgrid(*xs, indexing='ij', sparse=True); F = fn(X, Y, Z).astype(np.float32); nx, ny, nz = F.shape
    I = F < 0; c = I[:-1, :-1, :-1].astype(np.int8) + I[1:, :-1, :-1] + I[:-1, 1:, :-1] + I[1:, 1:, :-1] + I[:-1, :-1, 1:] + I[1:, :-1, 1:] + I[:-1, 1:, 1:] + I[1:, 1:, 1:]; act = np.argwhere((c > 0) & (c < 8)); i, j, k = act.T
    f000, f100, f010, f110, f001, f101, f011, f111 = F[i, j, k], F[i + 1, j, k], F[i, j + 1, k], F[i + 1, j + 1, k], F[i, j, k + 1], F[i + 1, j, k + 1], F[i, j + 1, k + 1], F[i + 1, j + 1, k + 1]
    fc = (f000 + f100 + f010 + f110 + f001 + f101 + f011 + f111) / 8; gx = (f100 + f110 + f101 + f111 - f000 - f010 - f001 - f011) / 4; gy = (f010 + f110 + f011 + f111 - f000 - f100 - f001 - f101) / 4; gz = (f001 + f101 + f011 + f111 - f000 - f100 - f010 - f110) / 4; g2 = gx * gx + gy * gy + gz * gz + 1e-9
    u = np.clip(0.5 - fc * gx / g2, 0, 1); v = np.clip(0.5 - fc * gy / g2, 0, 1); w = np.clip(0.5 - fc * gz / g2, 0, 1); P = np.stack([xs[0][i] + u * st, xs[1][j] + v * st, xs[2][k] + w * st], 1).astype(np.float32)
    ID = -np.ones((nx - 1, ny - 1, nz - 1), np.int32); ID[i, j, k] = np.arange(len(act)); Q = []
    def add(mask, a, b, cc, d):
        ix = np.argwhere(mask)
        if not len(ix): return
        ii, jj, kk = ix.T; fl = I[ii, jj, kk]; qa, qb, qc, qd = a(ii, jj, kk), b(ii, jj, kk), cc(ii, jj, kk), d(ii, jj, kk); ok = (qa >= 0) & (qb >= 0) & (qc >= 0) & (qd >= 0); q = np.stack([qa, qb, qc, qd], 1)[ok]; fl = fl[ok]; q[~fl] = q[~fl][:, ::-1]; Q.append(q)
    mx = np.zeros_like(I); mx[:-1, 1:-1, 1:-1] = I[:-1, 1:-1, 1:-1] != I[1:, 1:-1, 1:-1]; add(mx, lambda a, b, c: ID[a, b - 1, c - 1], lambda a, b, c: ID[a, b, c - 1], lambda a, b, c: ID[a, b, c], lambda a, b, c: ID[a, b - 1, c])
    my = np.zeros_like(I); my[1:-1, :-1, 1:-1] = I[1:-1, :-1, 1:-1] != I[1:-1, 1:, 1:-1]; add(my, lambda a, b, c: ID[a - 1, b, c - 1], lambda a, b, c: ID[a - 1, b, c], lambda a, b, c: ID[a, b, c], lambda a, b, c: ID[a, b, c - 1])
    mz = np.zeros_like(I); mz[1:-1, 1:-1, :-1] = I[1:-1, 1:-1, :-1] != I[1:-1, 1:-1, 1:]; add(mz, lambda a, b, c: ID[a - 1, b - 1, c], lambda a, b, c: ID[a, b - 1, c], lambda a, b, c: ID[a, b, c], lambda a, b, c: ID[a - 1, b, c])
    Qa = np.concatenate(Q); np.savez(os.path.join(out, name + '.npz'), v=P, f=Qa); print(name, len(P), 'verts')
