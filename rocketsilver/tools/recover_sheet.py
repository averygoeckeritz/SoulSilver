"""Recover an upscaled sprite sheet: invert the resize, then snap to palette."""
import sys
import numpy as np
from PIL import Image
import deconv

SRC, OUT, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
im = Image.open(SRC).convert("RGB")
rec = deconv.deconvolve(im, W, H, Image.BICUBIC).round().astype(np.uint8)

fg = ~(rec > 235).all(-1)
cols, cnt = np.unique(rec[fg].reshape(-1, 3), axis=0, return_counts=True)
sel = []
for i in np.argsort(-cnt):
    c = cols[i].astype(int)
    if all(((c - s) ** 2).sum() > 120 for s in sel):
        sel.append(c)
    if len(sel) >= 110:
        break
pal = np.array(sel, int)

out = np.full((H, W, 3), 255, np.uint8)
flat = rec[fg].astype(int)
d = ((flat[:, None, :] - pal[None]) ** 2).sum(-1)
out[fg] = pal[d.argmin(1)].astype(np.uint8)
Image.fromarray(out).save(OUT)
print(f"{OUT}: {W}x{H}, palette {len(pal)}, foreground {100*fg.mean():.0f}%")
