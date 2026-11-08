# Draw a labelled 100px grid over an image (on a loud red background where it's transparent), to read off
# coordinates for puppet pins, split regions and transition shapes. Usage: python3 grid.py <image.png> <out.jpg> [--step 100]
import sys
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]; step = int(sys.argv[sys.argv.index('--step') + 1]) if '--step' in sys.argv else 100
a = Image.open(src).convert('RGBA'); bg = Image.new('RGBA', a.size, (255, 60, 60, 255)); bg.alpha_composite(a); d = ImageDraw.Draw(bg)
for x in range(0, a.width, step): d.line([(x, 0), (x, a.height)], fill=(0, 0, 255, 255)); d.text((x + 2, 2), str(x), fill=(0, 0, 0, 255))
for y in range(0, a.height, step): d.line([(0, y), (a.width, y)], fill=(0, 0, 255, 255)); d.text((2, y + 2), str(y), fill=(0, 0, 0, 255))
bg.convert('RGB').save(out, quality=88); print(out, a.size)
