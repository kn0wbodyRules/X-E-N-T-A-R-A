# Split a cut-out PNG into same-size layer PNGs, so its parts can move on their own (a card, a cloud, ticks...).
# Regions are polygons in the image's pixels; whatever no region claims stays in <name>-base.png.
# Usage: python3 split.py <cutout.png> '<{"card": [[x,y],[x,y],...], "ticks": [...]}>'   (or a path to a .json file with that object)
import sys, json, os
from PIL import Image, ImageDraw
src, spec = sys.argv[1], sys.argv[2]
regions = json.load(open(spec)) if os.path.exists(spec) else json.loads(spec)
im = Image.open(src).convert('RGBA'); base = im.copy(); stem = os.path.splitext(src)[0]
for name, poly in regions.items():
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(im, (0, 0), m); out.save(f'{stem}-{name}.png')
    base.paste(Image.new('RGBA', im.size, (0, 0, 0, 0)), (0, 0), m)
base.save(f'{stem}-base.png'); print('layers:', ', '.join(['base'] + list(regions)))
