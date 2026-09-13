"""Quantise a 12-frame strip to 16 colours and write it into an NSBTX.

The container is cloned from a real NPC sprite so every header field, bounding
box and name stays valid; only the texture payload and palette are replaced.
"""
import struct, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC, TEMPLATE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
BG = (139, 180, 131)

a = np.array(Image.open(SRC).convert("RGB"))
H, W, _ = a.shape
bg = (np.abs(a.astype(int) - np.array(BG)).sum(-1) < 12)

# strip the pale fringe the recovery leaves around each figure
fig = ~bg
light = fig & (a.astype(int).min(-1) > 205)
border = fig & ~ndi.binary_erosion(fig, np.ones((3, 3), bool))
bg |= (light & border)
fig = ~bg

def ds(p):
    return (np.round(np.asarray(p, float) * 31 / 255).astype(int) * 255 // 31)

pix = ds(a[fig]).astype(float)
cols, counts = np.unique(pix, axis=0, return_counts=True)
sel = []
for c in cols[np.argsort(-counts)]:
    if len(sel) >= 15: break
    if all(((c - s) ** 2).sum() > 260 for s in sel): sel.append(c)
cent = np.array(sel, float)
for _ in range(10):
    lab = ((pix[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
    for k in range(len(cent)):
        m = lab == k
        if m.any(): cent[k] = pix[m].mean(0)
pal = ds(cent).astype(int)

idx = np.zeros((H, W), np.uint8)
d = ((ds(a[fig]).astype(float)[:, None, :] - pal[None].astype(float)) ** 2).sum(-1)
idx[fig] = 1 + d.argmin(1)

full_pal = np.vstack([np.array(BG, int), pal])[:16]
while len(full_pal) < 16:
    full_pal = np.vstack([full_pal, np.zeros((1, 3), int)])

d = bytearray(open(TEMPLATE, "rb").read())
tex = struct.unpack_from("<I", d, 16)[0]
texoff = struct.unpack_from("<I", d, tex + 0x14)[0]
texlen = struct.unpack_from("<H", d, tex + 0x0C)[0] * 8
paloff = struct.unpack_from("<I", d, tex + 0x38)[0]

flat = idx.reshape(-1)
assert len(flat) == texlen * 2, f"{len(flat)} pixels vs {texlen*2} expected"
packed = (flat[0::2] | (flat[1::2] << 4)).astype(np.uint8).tobytes()
d[tex+texoff: tex+texoff+texlen] = packed
for i, (r, g, b) in enumerate(full_pal):
    v = (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
    struct.pack_into("<H", d, tex + paloff + i*2, int(v))
open(OUT, "wb").write(bytes(d))
print(f"{OUT}: {len(d)} bytes, {len(pal)} colours + transparent")
