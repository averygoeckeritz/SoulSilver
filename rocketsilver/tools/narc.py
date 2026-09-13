"""NARC archive reader (Nintendo DS container format).

Layout: 'NARC' header, then three chunks whose magics are stored
byte-reversed on disk — BTAF (file allocation table), BTNF (filenames),
GMIF (the file image). Only BTAF and GMIF matter for reading.
"""
import struct


class Narc:
    def __init__(self, data):
        data = bytes(data)
        if data[:4] != b"NARC":
            raise ValueError(f"not a NARC (magic {data[:4]!r})")
        bom, filesize, hdrsize, nchunks = struct.unpack_from("<HxxIHH", data, 4)
        p = hdrsize
        self.files = []
        img_off = None
        fat = None
        for _ in range(nchunks):
            magic = data[p:p+4]
            size = struct.unpack_from("<I", data, p+4)[0]
            if magic == b"BTAF":
                n = struct.unpack_from("<I", data, p+8)[0]
                fat = [struct.unpack_from("<II", data, p+12+i*8) for i in range(n)]
            elif magic == b"GMIF":
                img_off = p + 8
            p += size
        if fat is None or img_off is None:
            raise ValueError("NARC missing BTAF or GMIF chunk")
        self.data = data
        self.img_off = img_off
        self.files = [(img_off + s, img_off + e) for s, e in fat]

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        s, e = self.files[i]
        return self.data[s:e]

    def sizes(self):
        return [e - s for s, e in self.files]
