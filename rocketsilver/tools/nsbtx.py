"""Read and write the DS overworld sprite textures used by HGSS (NSBTX)."""
import struct
import numpy as np
from PIL import Image

def read(path):
    d = open(path, "rb").read()
    tex = struct.unpack_from("<I", d, 16)[0]
    texoff = struct.unpack_from("<I", d, tex + 0x14)[0]
    texlen = struct.unpack_from("<H", d, tex + 0x0C)[0] * 8
    paloff = struct.unpack_from("<I", d, tex + 0x38)[0]
    raw = d[tex + texoff: tex + texoff + texlen]
    pal_raw = d[tex + paloff: tex + paloff + 32]
    pal = []
    for i in range(16):
        v = struct.unpack_from("<H", pal_raw, i * 2)[0]
        r, g, b = (v & 31), (v >> 5) & 31, (v >> 10) & 31
        pal.append((r * 255 // 31, g * 255 // 31, b * 255 // 31))
    idx = np.zeros(len(raw) * 2, np.uint8)
    a = np.frombuffer(raw, np.uint8)
    idx[0::2] = a & 0xF
    idx[1::2] = a >> 4
    return idx, np.array(pal, np.uint8), d, tex, texoff, texlen, paloff

def to_image(idx, pal, width):
    h = len(idx) // width
    im = Image.fromarray(idx[:h*width].reshape(h, width), "P")
    im.putpalette(pal.reshape(-1).tolist())
    return im
