# Cut an illustration's subject out of its flat single-colour background: flood-fill the background from the edges, then soften the edge.
# bits inside the figure survive), soften the edge by a pixel, crop to the subject.
# Usage: key.py <src.png> <out.png> [--keep-pockets] [--no-bottom]
#   --keep-pockets  keep enclosed field-coloured areas (a yellow folder on a yellow field)
#   --no-bottom     don't flood in from the bottom edge (a figure cut off by the frame, light trousers)
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
KEEP_POCKETS, NO_BOTTOM = '--keep-pockets' in sys.argv, '--no-bottom' in sys.argv
im = Image.open(src).convert('RGB'); a = np.array(im).astype(int)
bg = np.median(np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3), a[:, :4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)]), axis=0)
near = np.sqrt(((a - bg) ** 2).sum(-1)) < 46
lab, n = ndimage.label(near)
edge = set(np.unique(np.concatenate([lab[0], lab[:, 0], lab[:, -1]] + ([] if NO_BOTTOM else [lab[-1]])))) - {0}
sizes = ndimage.sum(np.ones_like(lab), lab, index=np.arange(n + 1))
field = np.isin(lab, list(edge)) | (np.zeros_like(near) if KEEP_POCKETS else (near & (sizes[lab] > 400)))   # plus enclosed pockets of field colour (between an arm and the body)
keep = ~field; kl, kn = ndimage.label(keep); ks = ndimage.sum(np.ones_like(kl), kl, index=np.arange(kn + 1)); keep &= ks[kl] > 300   # drop specks
alpha = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
rgba = im.convert('RGBA'); rgba.putalpha(alpha)
bb = rgba.getbbox(); pad = 12
rgba = rgba.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)))
rgba.save(out); print(out, rgba.size, 'bg', bg)
