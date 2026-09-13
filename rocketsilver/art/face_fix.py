"""Hand-authored face pass for the Iron-Masked Marauder.

At fourteen pixels across, a downscale cannot place eye slits or a forehead
notch; it smears them. The body converts well automatically, so only the head
is touched here, using the reference art as the guide:

  - a dark V notch under the crest, where the helmet dips toward the brow
  - two symmetrical eye slits, two pixels wide and two tall
  - stray highlights and the over-long dark bar from the downscale removed
"""
import numpy as np
from PIL import Image

im  = Image.open("marauder4.png")
pal = np.array(im.getpalette()[:48]).reshape(16, 3)
idx = np.array(im)

GOLD, DARK, SLIT, PALE = 4, 8, 15, 11

def put(rows, cols, val):
    for r in rows:
        for c in cols:
            if idx[r, c] != 0:            # never paint over transparency
                idx[r, c] = val

# 1. forehead notch: the stray pale blob below the crest becomes the V dip
put([10], [32], DARK)
put([11], [30, 31, 32], DARK)
put([12], [30, 31], DARK)

# 2. clear the downscale's over-long dark bar on the right of the helmet
put([16, 17, 18], [34, 35], GOLD)

# 3. remove stray dark and pale specks inside the helmet
put([17], [27], GOLD)
put([18], [27, 28], GOLD)
put([17, 18, 19], [38], GOLD)

# 4. eye slits, symmetric about the helmet centre (cols 25..38 -> centre 31.5)
put([14, 15], [28, 29], SLIT)
put([14, 15], [34, 35], SLIT)

out = Image.fromarray(idx, "P")
out.putpalette(pal.reshape(-1).tolist())
out.save("marauder5.png")
print("face pass written to marauder5.png")

for r in range(3, 24):
    line = "".join("." if idx[r,c]==0 else
                   "G" if idx[r,c] in (4,9,10) else
                   "P" if idx[r,c]==11 else
                   "O" if idx[r,c]==15 else "D" for c in range(24, 40))
    print(f"  r{r:2d} {line}")
