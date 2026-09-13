"""Convert official character artwork into a clean 64x128, 16-colour DS figure.

The key idea: quantise the artwork to its final palette at FULL resolution,
then shrink by taking the most common colour in each destination cell. Ordinary
filters blend neighbouring colours and invent in-between shades, which at this
size turns small features such as eye slits into mud. Majority sampling keeps
every boundary crisp because it never invents a colour that was not there.

Afterwards, tiny stray regions are absorbed into their neighbours and a solid
dark outline is drawn around the silhouette, which is what makes a sprite read
as a sprite.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC, OUT = sys.argv[1], sys.argv[2]
BG = (115, 197, 164)
W, H, FOOT = 64, 128, 126
N_COLORS = 15
OUTLINE = (17, 15, 20)

im = Image.open(SRC).convert("RGBA")
a = np.array(im)
rgb, alpha = a[..., :3].astype(float), a[..., 3]
mask = alpha > 128
ys, xs = np.nonzero(mask)
rgb  = rgb[ys.min():ys.max()+1, xs.min():xs.max()+1]
mask = mask[ys.min():ys.max()+1, xs.min():xs.max()+1]

def ds_round(p):
    return (np.round(np.asarray(p, float) * 31 / 255).astype(int) * 255 // 31)

# ---- palette from the full-resolution artwork ---------------------------
pix = ds_round(rgb[mask]).astype(float)
uniq, counts = np.unique(pix, axis=0, return_counts=True)
sel = []
for c in uniq[np.argsort(-counts)]:
    if len(sel) >= N_COLORS - 1: break
    if all(((c - s) ** 2).sum() > 700 for s in sel):
        sel.append(c)
cent = np.array(sel, float)
for _ in range(12):
    lab = ((pix[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
    for k in range(len(cent)):
        m = lab == k
        if m.any(): cent[k] = pix[m].mean(0)
pal = np.vstack([ds_round(cent), ds_round(OUTLINE)]).astype(np.uint8)
OUT_IDX = len(pal)

# quantise at full resolution: 0 = transparent, 1..n = palette
full = np.zeros(mask.shape, np.int16)
d = ((ds_round(rgb[mask]).astype(float)[:, None, :] - pal[None, :-1].astype(float)) ** 2).sum(-1)
full[mask] = 1 + d.argmin(1)

# ---- majority downscale -------------------------------------------------
h, w = mask.shape
scale = min((FOOT - 3) / h, (W - 6) / w)
nh, nw = max(1, round(h * scale)), max(1, round(w * scale))
small = np.zeros((nh, nw), np.uint8)
ymap = (np.arange(nh + 1) * h / nh).round().astype(int)
xmap = (np.arange(nw + 1) * w / nw).round().astype(int)
ncol = len(pal) + 1
for i in range(nh):
    for j in range(nw):
        blk = full[ymap[i]:max(ymap[i+1], ymap[i]+1),
                   xmap[j]:max(xmap[j+1], xmap[j]+1)].ravel()
        if blk.size == 0: continue
        bc = np.bincount(blk, minlength=ncol)
        # a cell counts as figure when at least a third of it is covered
        if bc[0] * 3 > blk.size * 2:
            small[i, j] = 0
        else:
            bc[0] = 0
            small[i, j] = bc.argmax()
smallm = small != 0
smallm = ndi.binary_fill_holes(smallm)
small[smallm & (small == 0)] = OUT_IDX

# ---- absorb tiny regions ------------------------------------------------
for _ in range(4):
    changed = 0
    for c in range(1, ncol):
        m = small == c
        if not m.any(): continue
        lab, n = ndi.label(m)
        if not n: continue
        sizes = ndi.sum(m, lab, range(1, n + 1))
        for k in np.nonzero(sizes <= 2)[0] + 1:
            comp = lab == k
            ring = ndi.binary_dilation(comp, np.ones((3, 3), bool)) & smallm & ~comp
            vals = small[ring]; vals = vals[vals != 0]
            if vals.size:
                small[comp] = np.bincount(vals).argmax(); changed += 1
    if not changed: break

# ---- outline ------------------------------------------------------------
border = smallm & ~ndi.binary_erosion(smallm, np.ones((3, 3), bool))
small[border] = OUT_IDX

canvas = np.zeros((H, W), np.uint8)
y0, x0 = FOOT - nh, (W - nw) // 2
canvas[y0:y0+nh, x0:x0+nw] = small
out = Image.fromarray(canvas, "P")
out.putpalette(np.vstack([np.array(BG, np.uint8), pal]).reshape(-1).tolist())
out.save(OUT)

fig = canvas != 0
specks = 0
for c in range(1, ncol):
    m = canvas == c
    if not m.any(): continue
    lab, n = ndi.label(m)
    specks += int((ndi.sum(m, lab, range(1, n + 1)) <= 2).sum())
bo = fig & ~ndi.binary_erosion(fig, np.ones((3, 3), bool))
print(f"{OUT}: {nw}x{nh} at ({x0},{y0}), {len(pal)} colours")
print(f"  isolated specks : {specks}")
print(f"  outlined border : {100*int((canvas[bo]==OUT_IDX).sum())/max(int(bo.sum()),1):.0f}%")
