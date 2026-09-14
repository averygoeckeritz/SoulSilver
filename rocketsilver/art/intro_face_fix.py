"""Hand pass on the Masked Man's intro face.

At roughly twenty pixels across, the downscale merges both eye slits into one
blob and washes the gold helmet toward cream. Both are corrected against the
sheet art: the helmet takes its real gold, and two angled slits are placed
symmetrically about the helmet's centre.
"""
import numpy as np
from PIL import Image

im  = Image.open("mm_intro_final.png")
pal = np.array(im.getpalette()[:48]).reshape(16, 3).astype(int)
idx = np.array(im)

GOLD, GOLD_DK = 5, 8
pal[GOLD]    = (214, 186, 116)      # helmet, warmer than the washed cream
pal[GOLD_DK] = (158, 130,  68)      # its shading
EYE = 1                              # the magenta already in the palette
DARK = 13

# helmet extent: the LARGEST connected gold region, so the pointing arm's
# gold cuff does not drag the measured centre sideways
from scipy import ndimage as ndi
helm_all = np.isin(idx, [GOLD, GOLD_DK])
band = helm_all.copy(); band[:27] = False; band[42:] = False
lab, n = ndi.label(band)
sizes = ndi.sum(band, lab, range(1, n + 1))
head = lab == (int(np.argmax(sizes)) + 1)
hy, hx = np.nonzero(head)
c0, c1 = int(hx.min()), int(hx.max())
mid = (c0 + c1) // 2

# clear the merged blob the downscale left, then place two slits
for r in range(31, 35):
    for c in range(c0, c1 + 1):
        if idx[r, c] in (7, 4):
            idx[r, c] = GOLD

eye_r = 32
for dx in (-6, -5, 2, 3):
    for dr in (0, 1):
        c = mid + dx
        if 0 <= c < idx.shape[1] and idx[eye_r + dr, c] != 0:
            idx[eye_r + dr, c] = EYE
for dx in (-7, -4, 1, 4):
    c = mid + dx
    if 0 <= c < idx.shape[1] and idx[eye_r, c] != 0:
        idx[eye_r, c] = DARK

out = Image.fromarray(idx, "P")
out.putpalette(pal.astype(np.uint8).reshape(-1).tolist())
out.save("mm_intro_fixed.png")
print(f"helmet cols {c0}-{c1}, centre {mid}; eyes placed at row {eye_r}")
