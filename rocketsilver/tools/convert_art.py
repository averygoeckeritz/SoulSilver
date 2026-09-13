"""Convert official character artwork into a 64x128, 16-colour DS intro figure.

Same pipeline used for the FireRed Dark set: edge-extend under the alpha mask
so the downscale does not drag background into the outline, resize with a
high-quality filter, then pick an exact-colour palette by weighted frequency
rather than averaging, which is what washes colours out.
"""
import sys
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
BG = (115, 197, 164)              # the intro's transparent colour, index 0
W, H = 64, 128
FOOT = 126                        # bottom row the figure should stand on

im = Image.open(SRC).convert("RGBA")
a = np.array(im)
rgb, alpha = a[..., :3].astype(np.float64), a[..., 3]
mask = alpha > 128

ys, xs = np.nonzero(mask)
rgb  = rgb[ys.min():ys.max()+1, xs.min():xs.max()+1]
mask = mask[ys.min():ys.max()+1, xs.min():xs.max()+1]

def edge_extend(rgb, mask, iters=8):
    rgb, filled = rgb.copy(), mask.copy()
    for _ in range(iters):
        if filled.all(): break
        acc = np.zeros_like(rgb); cnt = np.zeros(mask.shape)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == dx == 0: continue
                acc += np.roll(np.roll(rgb * filled[..., None], dy, 0), dx, 1)
                cnt += np.roll(np.roll(filled.astype(float), dy, 0), dx, 1)
        new = ~filled & (cnt > 0)
        rgb[new] = acc[new] / cnt[new][:, None]
        filled |= new
    return rgb

h, w = mask.shape
scale = min((FOOT - 2) / h, (W - 4) / w)
nh, nw = max(1, round(h * scale)), max(1, round(w * scale))
ext = edge_extend(rgb, mask)
small  = np.array(Image.fromarray(ext.astype(np.uint8)).resize((nw, nh), Image.LANCZOS))
smallm = np.array(Image.fromarray((mask * 255).astype(np.uint8)).resize((nw, nh), Image.LANCZOS)) >= 128

def gba_round(p):                 # DS colour is 5 bits per channel
    return ((np.round(p.astype(float) * 31 / 255)).astype(int) * 255 // 31).astype(np.uint8)

from collections import Counter
cnt = Counter(map(tuple, gba_round(small[smallm]).reshape(-1, 3)))
sel, THR = [], 300
for c, _ in cnt.most_common():
    if len(sel) >= 15: break
    if all(sum((int(x) - int(y)) ** 2 for x, y in zip(c, s)) > THR for s in sel):
        sel.append(c)
pal = np.array(sel, np.uint8)

flat = small[smallm].astype(int)
d = ((flat[:, None, :] - pal[None, :, :].astype(int)) ** 2).sum(-1)
idx_small = np.zeros(smallm.shape, np.uint8)
idx_small[smallm] = 1 + np.argmin(d, axis=1)

canvas = np.zeros((H, W), np.uint8)
y0 = FOOT - nh
x0 = (W - nw) // 2
canvas[y0:y0+nh, x0:x0+nw] = idx_small

out = Image.fromarray(canvas, "P")
out.putpalette(np.vstack([np.array(BG, np.uint8), pal]).reshape(-1).tolist())
out.save(OUT)
print(f"{OUT}: figure {nw}x{nh} placed at ({x0},{y0}), {len(pal)} colours")
