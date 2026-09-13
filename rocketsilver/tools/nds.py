"""Nintendo DS ROM access: header, filesystem (FAT/FNT), file extraction.

Companion to the GBA project's `gba.py`. Scope is deliberately small —
enough to open a .nds and pull named files out of it. Archive (NARC) and
graphics (NCGR/NCLR/NSCR) decoding is added once verified against the
actual ROM.

Formats here follow the documented DS cartridge layout (GBATEK). Every
offset this module reads comes from the ROM header rather than being
hardcoded, so it is self-verifying: `header()` sanity-checks the values
before anything else uses them.
"""
import struct
from dataclasses import dataclass


def load(path):
    with open(path, "rb") as f:
        return bytearray(f.read())


# ---------------------------------------------------------------- header

@dataclass
class Header:
    title: str
    gamecode: str
    makercode: str
    arm9_off: int
    arm9_size: int
    arm7_off: int
    arm7_size: int
    fnt_off: int
    fnt_size: int
    fat_off: int
    fat_size: int
    ov9_off: int
    ov9_size: int
    ov7_off: int
    ov7_size: int
    rom_size: int

    @property
    def file_count(self):
        return self.fat_size // 8


def header(rom):
    """Parse and sanity-check the 0x200-byte cartridge header."""
    title = rom[0x00:0x0C].split(b"\x00")[0].decode("ascii", "replace")
    gamecode = rom[0x0C:0x10].decode("ascii", "replace")
    makercode = rom[0x10:0x12].decode("ascii", "replace")
    (arm9_off, _a9e, _a9r, arm9_size,
     arm7_off, _a7e, _a7r, arm7_size,
     fnt_off, fnt_size, fat_off, fat_size,
     ov9_off, ov9_size, ov7_off, ov7_size) = struct.unpack_from("<16I", rom, 0x20)
    used = struct.unpack_from("<I", rom, 0x80)[0]

    h = Header(title, gamecode, makercode, arm9_off, arm9_size,
               arm7_off, arm7_size, fnt_off, fnt_size, fat_off, fat_size,
               ov9_off, ov9_size, ov7_off, ov7_size, used)

    for name, off, size in (("FNT", fnt_off, fnt_size),
                            ("FAT", fat_off, fat_size),
                            ("ARM9", arm9_off, arm9_size),
                            ("ARM7", arm7_off, arm7_size)):
        if off == 0 or off + size > len(rom):
            raise ValueError(f"{name} table out of range: {off:#x}+{size:#x} "
                             f"(rom {len(rom):#x}) — not a valid .nds?")
    if fat_size % 8:
        raise ValueError(f"FAT size {fat_size:#x} is not a multiple of 8")
    return h


# ------------------------------------------------------------ filesystem

def fat(rom, h):
    """[(start, end)] per file id."""
    return [struct.unpack_from("<II", rom, h.fat_off + i * 8)
            for i in range(h.file_count)]


def fnt(rom, h):
    """Walk the filename table. Returns {path: file_id} and {file_id: path}."""
    base = h.fnt_off
    paths, by_id = {}, {}

    def read_dir(dir_id, prefix):
        entry = base + (dir_id & 0xFFF) * 8
        sub_off, first_id, _parent = struct.unpack_from("<IHH", rom, entry)
        p = base + sub_off
        fid = first_id
        while True:
            t = rom[p]
            p += 1
            if t == 0:
                break
            is_dir = bool(t & 0x80)
            n = t & 0x7F
            name = rom[p:p + n].decode("ascii", "replace")
            p += n
            if is_dir:
                child = struct.unpack_from("<H", rom, p)[0]
                p += 2
                read_dir(child, f"{prefix}{name}/")
            else:
                full = f"{prefix}{name}"
                paths[full] = fid
                by_id[fid] = full
                fid += 1

    read_dir(0, "")
    return paths, by_id


class Rom:
    """Convenience wrapper: `r = Rom(path); data = r.read('a/0/0/2')`."""

    def __init__(self, path):
        self.path = path
        self.data = load(path)
        self.h = header(self.data)
        self.fat = fat(self.data, self.h)
        self.paths, self.by_id = fnt(self.data, self.h)

    def __len__(self):
        return len(self.data)

    def file_id(self, path):
        if path not in self.paths:
            raise KeyError(f"no such file in ROM: {path}")
        return self.paths[path]

    def span(self, path_or_id):
        fid = path_or_id if isinstance(path_or_id, int) else self.file_id(path_or_id)
        return self.fat[fid]

    def read(self, path_or_id):
        start, end = self.span(path_or_id)
        return bytes(self.data[start:end])

    def listdir(self, prefix=""):
        return sorted(p for p in self.paths if p.startswith(prefix))

    def summary(self):
        h = self.h
        return (f"{h.title} [{h.gamecode}] maker {h.makercode}\n"
                f"  rom {len(self.data):#x} ({len(self.data)/2**20:.1f} MB), "
                f"used {h.rom_size:#x}\n"
                f"  arm9 {h.arm9_off:#x}+{h.arm9_size:#x}  "
                f"arm7 {h.arm7_off:#x}+{h.arm7_size:#x}\n"
                f"  fnt  {h.fnt_off:#x}+{h.fnt_size:#x}  "
                f"fat {h.fat_off:#x}+{h.fat_size:#x}\n"
                f"  files {h.file_count}")


if __name__ == "__main__":
    import sys
    r = Rom(sys.argv[1])
    print(r.summary())
    print("\nfirst 30 paths:")
    for p in r.listdir()[:30]:
        s, e = r.span(p)
        print(f"  {p:40s} {e - s:>9,} bytes")
