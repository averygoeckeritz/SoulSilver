"""Final cleanup: absorb leftover specks and drop unused palette slots."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

im  = Image.open("marauder5.png")
pal = np.array(im.getpalette()[:48]).reshape(16, 3)
idx = np.array(im).astype(np.int16)
fig = idx != 0

# absorb every remaining region of two pixels or fewer into its surroundings,
# but never touch the outline, which is meant to be thin
OUTLINE = 15
for _ in range(6):
    changed = 0
    for c in range(1, 16):
        if c == OUTLINE: continue
        m = idx == c
        if not m.any(): continue
        lab, n = ndi.label(m)
        if not n: continue
        sizes = ndi.sum(m, lab, range(1, n + 1))
        for k in np.nonzero(sizes <= 2)[0] + 1:
            comp = lab == k
            ring = ndi.binary_dilation(comp, np.ones((3, 3), bool)) & fig & ~comp
            vals = idx[ring]; vals = vals[(vals != 0)]
            if vals.size:
                idx[comp] = np.bincount(vals).argmax(); changed += 1
    if not changed: break

# rebuild the palette so no slot is wasted
used = [c for c in range(1, 16) if (idx == c).any()]
remap = {old: new + 1 for new, old in enumerate(used)}
new_idx = np.zeros_like(idx)
for old, new in remap.items():
    new_idx[idx == old] = new
new_pal = np.vstack([pal[0]] + [pal[o] for o in used]).astype(np.uint8)
while len(new_pal) < 16:
    new_pal = np.vstack([new_pal, np.zeros((1, 3), np.uint8)])

out = Image.fromarray(new_idx.astype(np.uint8), "P")
out.putpalette(new_pal.reshape(-1).tolist())
out.save("marauder_final.png")

specks = 0
for c in range(1, 16):
    m = new_idx == c
    if not m.any(): continue
    lab, n = ndi.label(m)
    specks += int((ndi.sum(m, lab, range(1, n + 1)) <= 2).sum())
f = new_idx != 0
bo = f & ~ndi.binary_erosion(f, np.ones((3, 3), bool))
lum = new_pal[new_idx].mean(-1)
print(f"colours used   : {len(used)}")
print(f"specks (<=2px) : {specks}")
print(f"outline dark   : {100*int((bo & (lum<60)).sum())/int(bo.sum()):.0f}%")
print(f"interior holes : {int((ndi.binary_fill_holes(f) & ~f).sum())}")
