# Runs a transparent Blender render straight on into real footage, at 4K. The first clip frame is the target the ad lands on.
# python3 compose_into_clip.py <rgba frames folder> <clip> "<out.mp4>" --fade 6.2 7.5 --melt 7.45 7.95 --end 8 [--start 0] [--sfx ad.wav]
# --start: where in the clip the ad lands (seconds). --fade: black fades away to show the held clip frame. --melt: the rendered object melts onto the real one, so there's no pop on the cut.
import cv2, numpy as np, subprocess, argparse, glob, os
a = argparse.ArgumentParser(); a.add_argument('frames'); a.add_argument('clip'); a.add_argument('out'); a.add_argument('--fade', nargs=2, type=float, default=[6.2, 7.5]); a.add_argument('--melt', nargs=2, type=float, default=[7.45, 7.95]); a.add_argument('--end', type=float, default=8.0); a.add_argument('--start', type=float, default=0.0); a.add_argument('--sfx'); a.add_argument('--fps', type=int, default=25); a.add_argument('--w', type=int, default=3840); a.add_argument('--h', type=int, default=2160); A = a.parse_args()
def sm(k): k = max(0, min(1, k)); return k * k * (3 - 2 * k)
fs = sorted(glob.glob(os.path.join(A.frames, '*.png'))); N = len(fs); W, H = A.w, A.h
bg = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(A.start), '-i', A.clip, '-frames:v', '1', '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True, check=True).stdout; first = np.frombuffer(bg, np.uint8).reshape(H, W, 3).astype(np.float32)
fc = f'[1:v]fps={A.fps},scale={W}:{H},format=yuv420p,setsar=1[cl];[0:v]format=yuv420p,setsar=1[ad];[ad][cl]concat=n=2:v=1:a=0[v]'; inp = ['-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(A.fps), '-i', '-', '-ss', str(A.start), '-i', A.clip]; has = bool(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', A.clip], capture_output=True, text=True).stdout.strip()); d = int(A.end * 1000); amap = []
if A.sfx: inp += ['-i', A.sfx]; fc += (f';[1:a]adelay={d}|{d}[ca];[2:a][ca]amix=inputs=2:normalize=0:duration=longest[a]' if has else ';[2:a]anull[a]'); amap = ['-map', '[a]', '-c:a', 'aac', '-b:a', '320k']
elif has: fc += f';[1:a]adelay={d}|{d}[a]'; amap = ['-map', '[a]', '-c:a', 'aac', '-b:a', '320k']
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error'] + inp + ['-filter_complex', fc, '-map', '[v]'] + amap + ['-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', A.out], stdin=subprocess.PIPE)
for i, f in enumerate(fs):
    t = i / (N - 1) * A.end; im = cv2.resize(cv2.imread(f, -1), (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32); al = im[..., 3:] / 255 * (1 - sm((t - A.melt[0]) / (A.melt[1] - A.melt[0]))); under = first * sm((t - A.fade[0]) / (A.fade[1] - A.fade[0])); p.stdin.write(np.clip(under * (1 - al) + im[..., :3] * al, 0, 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print('Wrote', A.out)
