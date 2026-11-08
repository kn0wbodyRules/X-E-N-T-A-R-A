# Tile a folder of stills (named <t>.jpg) into one labelled contact sheet, for frame-by-frame review.
# Usage: python3 contact_sheet.py <stills dir> <out.jpg> [--cols 4]
import sys, glob, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[sys.argv.index('--cols') + 1]) if '--cols' in sys.argv else 4
fs = sorted(glob.glob(os.path.join(d, '[0-9]*.jpg')), key=lambda f: float(os.path.basename(f)[:-4]))
W, H = 640, 360; im = Image.new('RGB', (W * cols, H * ((len(fs) + cols - 1) // cols)))
for i, f in enumerate(fs):
    t = Image.open(f).resize((W, H)); ImageDraw.Draw(t).text((10, 10), os.path.basename(f)[:-4] + 's', fill='white'); im.paste(t, ((i % cols) * W, (i // cols) * H))
im.save(out, quality=85); print(out, len(fs), 'frames')
