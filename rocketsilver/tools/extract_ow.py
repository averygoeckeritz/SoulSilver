"""Pull a 4-direction walk cycle out of a recovered HGSS sprite sheet.

The sheet groups by facing: block 1 faces down, block 2 up, blocks 3 and 4 are
the two side views. Taking the first row of each gives the twelve frames the
game wants for an NPC.
"""
import sys
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
BLOCKS = {                      # facing -> the three animation columns
    "down":  [8, 31, 54],
    "up":    [133, 156, 179],
    "left":  [249, 273, 298],
    "right": [361, 386, 410],
}
ROW, CH, CW = 188, 32, 23
BG, FOOT = (139, 180, 131), 30

a = np.array(Image.open(SRC).convert("RGB"))
fg = ~(a > 235).all(-1)

order = ["down", "up", "left", "right"]
out = np.full((32 * 12, 32, 3), BG, np.uint8)
i = 0
for facing in order:
    for c in BLOCKS[facing]:
        cell, cellm = a[ROW:ROW+CH, c:c+CW], fg[ROW:ROW+CH, c:c+CW]
        ys, xs = np.nonzero(cellm)
        if ys.size == 0:
            i += 1; continue
        sub  = cell[ys.min():ys.max()+1, xs.min():xs.max()+1]
        subm = cellm[ys.min():ys.max()+1, xs.min():xs.max()+1]
        h, w = sub.shape[:2]
        h = min(h, FOOT); sub, subm = sub[-h:], subm[-h:]
        w = min(w, 32);   sub, subm = sub[:, :w], subm[:, :w]
        x0 = (32 - w) // 2
        tile = out[32*i:32*(i+1)]
        tile[FOOT-h:FOOT, x0:x0+w][subm] = sub[subm]
        i += 1

Image.fromarray(out).save(OUT)
print(f"{OUT}: 12 frames, order {' '.join(order)}")
