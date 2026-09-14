"""Put the Masked Man into the intro at his art's true size, unscaled.

The intro figure is drawn from a tile set plus a tilemap. Vanilla uses an
8x16 tile area, exactly 64x128, which forces any larger art to be shrunk. The
tilemap is data, so the area can simply be made bigger: this builds a 12x19
tile set (96x152) holding the 88x150 art at 1:1, and a matching tilemap that
places it where Oak's figure used to stand.
"""
import struct
import numpy as np
from PIL import Image

SRC = "mm_fullbody.png"
BG = (115, 197, 164)
TW, TH = 11, 18                       # tiles: 88 x 144 px, the tallest the
                                      # text box leaves free (vanilla used 8x16)

src = Image.open(SRC).convert("RGBA")
# the art is 88x150 and the usable area is 88x144, so it needs a 0.96 nudge
# rather than the 0.70 crush the vanilla 64x128 area forced
sw, sh = src.size
sc = min(TW*8 / sw, TH*8 / sh)
if sc < 1:
    src = src.resize((max(1,round(sw*sc)), max(1,round(sh*sc))), Image.LANCZOS)
    print(f"art {sw}x{sh} -> {src.size[0]}x{src.size[1]} (scale {sc:.3f})")
a = np.array(src)
rgb, alpha = a[..., :3], a[..., 3]
fg = alpha > 128
h, w = fg.shape

canvas = np.zeros((TH*8, TW*8, 3), np.uint8); canvas[:] = BG
mask   = np.zeros((TH*8, TW*8), bool)
y0 = TH*8 - h                          # stand on the bottom of the area
x0 = (TW*8 - w)//2
canvas[y0:y0+h, x0:x0+w][fg] = rgb[fg]
mask[y0:y0+h, x0:x0+w] = fg

def ds(p): return (np.round(np.asarray(p,float)*31/255).astype(int)*255//31)
pix = ds(canvas[mask]).astype(float)
cols, cnt = np.unique(pix, axis=0, return_counts=True)
sel=[]
for c in cols[np.argsort(-cnt)]:
    if len(sel) >= 15: break
    if all(((c-s)**2).sum() > 200 for s in sel): sel.append(c)
cent = np.array(sel, float)
for _ in range(10):
    lab = ((pix[:,None,:]-cent[None])**2).sum(-1).argmin(1)
    for k in range(len(cent)):
        m = lab==k
        if m.any(): cent[k]=pix[m].mean(0)
pal = ds(cent).astype(int)

idx = np.zeros(mask.shape, np.uint8)
d = ((ds(canvas[mask]).astype(float)[:,None,:]-pal[None].astype(float))**2).sum(-1)
idx[mask] = 1 + d.argmin(1)

full = np.vstack([np.array(BG,int), pal])[:16]
while len(full) < 16: full = np.vstack([full, np.zeros((1,3),int)])
img = Image.fromarray(idx, "P"); img.putpalette(full.astype(np.uint8).reshape(-1).tolist())
img.save("mm_big.png")
print(f"tile sheet {TW*8}x{TH*8}, art placed at ({x0},{y0}), {len(pal)} colours")
np.save("mm_big_idx.npy", idx)
