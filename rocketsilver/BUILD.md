# Building Rocket Silver

Rocket Silver is built from the **pokeheartgold decompilation** (pret/pokeheartgold),
not by binary-patching a ROM. That means the game is real C source we edit and
recompile, which is what makes building new scenes from nothing possible.

## Base ROM

The decomp builds both HGSS games. We target **SoulSilver (USA)**.

| | SHA-1 |
|---|---|
| `pokesoulsilver.us.nds` | `f8dc38ea20c17541a43b58c5e6d18c1732c7e582` |
| `pokeheartgold.us.nds` | `4fcded0e2713dc03929845de631d0932ea2b5a37` |

Both hashes come from the decomp's own `README.md` and are the No-Intro
clean-dump hashes. Each target directory (`soulsilver.us/`, `heartgold.us/`)
carries an identical file set, and the Makefile exposes first-class
`soulsilver`, `compare_soulsilver`, and `clean_soulsilver` targets.

Verified: our base ROM hashes to the expected SoulSilver value exactly, matching
`soulsilver.us/rom.sha1`. It is the clean retail dump, not Storm Silver.
Distinguishing marks of the clean dump:

- File size is exactly 134,217,728 bytes (128 MiB cart size).
- The NDS header's used-size field reads 126,645,820, i.e. less than the file
  length, because the tail is padding.

A patched image such as Storm Silver reports a used size equal to its whole
file length and has a different size and hash.

## Toolchain

### Free prerequisites (installed from apt, no special access)

    apt-get install -y binutils-arm-none-eabi p7zip-full libpng-dev \
                       libpugixml-dev build-essential

Verified working: apt reaches its repositories through the agent proxy, and the
decomp's own C tools (`compstatic`, `elfcoder`, `csv2bin`, and the rest) all
compile cleanly with the system gcc.

### wine (needed to run the compiler, which ships as Windows .exe files)

On Ubuntu 24.04 the obvious command fails. Installing `wine32:i386` together
with the rest hits an unmet dependency, `libgphoto2-6t64:i386` wanting
`libgd3:i386`, and apt reports held broken packages. `libgd3:i386` is in the
archive and installs fine on its own, so the fix is simply to stage it first:

    dpkg --add-architecture i386 && apt-get update
    apt-get install -y wine64
    apt-get install -y libgd3:i386      # must precede wine32, or apt breaks
    apt-get install -y wine32:i386

Verify that a real 32-bit Windows binary runs, since that is what the compiler
is. A 64-bit-only wine is not sufficient:

    WINEPREFIX=/root/.wine32 WINEARCH=win32 wineboot -i
    WINEPREFIX=/root/.wine32 wine cmd /c "echo ok"

Confirmed on this setup: `drive_c/windows/system32/cmd.exe` reports as
`PE32 executable (console) Intel 80386` and executes correctly.

### Proprietary prerequisites (not redistributable)

Two pieces of original 2009 software are required and cannot be downloaded
normally. Both are distributed through the pret Discord (https://discord.gg/d5dubZ3),
in the pinned messages of the `#pokediamond` channel.

1. **`mwccarm.zip`** — Metrowerks CodeWarrior for ARM, plus its `license.dat`.
   Pinned in `#pokediamond`; the compiler is shared across the DS decomps.
   Extract to `tools/mwccarm/`, so that `tools/mwccarm/2.0/sp2p2/mwccarm.exe`
   and `tools/mwccarm/license.dat` exist. Run under wine.
   Required because a byte-identical ROM can only be produced by the exact
   compiler the original developers used; any modern compiler emits different
   machine code and the identity check fails.

   The full archive is about 49 MB, but the build references only three of its
   compiler sets. Keeping just these, plus `license.dat`, cuts it to roughly
   6 MB, which matters when the only upload path has a size cap:

   | Keep | Used for |
   |---|---|
   | `2.0/sp2p2` | most of the game |
   | `2.0/sp2p3` | `lib/NitroSDK`, `lib/MSL_C` |
   | `1.2/sp2p3` | a small set of older objects |

   Everything else, including the whole `dsi/` tree, is unused here.

2. **`NitroSDK-4_2-071210-jp.7z`** — Nintendo's official DS SDK. Pinned in
   `#pokeheartgold`, *not* `#pokediamond`. Copy its `tools/bin` directory into
   the decomp's `tools/`, so that `tools/bin/makelcf.exe` exists. Then copy the
   link-script templates: `include/nitro/specfiles/ARM7-TS.lcf.template` into
   `sub/`, and `ARM9-TS.lcf.template` plus `mwldarm.response.template` into the
   repo root. Note this archive extracts with no top-level folder, unlike 3.2.

   **Version 4.2 is required; 3.2 will not do.** `#pokediamond` pins 3.2 because
   Diamond and Pearl were built against it. The ARM9 linker template differs
   between the two versions, and that template governs ROM layout, so 3.2 would
   build but fail the byte-identical check.

Without these the build stops at exactly this point, which is the state we
reached during setup:

    No rule to make target 'tools/mwccarm/2.0/sp2p2/mwasmarm.exe', needed by 'tools'

Nothing else in the chain is missing.

## Build and verify

    make soulsilver            # builds build/soulsilver.us/pokesoulsilver.us.nds
    make compare_soulsilver    # builds and checks against soulsilver.us/rom.sha1

An unmodified source tree must reproduce the base ROM byte for byte before any
Rocket Silver work begins. That is the project's go/no-go gate: it proves the
toolchain is correct, so that later any difference in output is our change and
nothing else.

**Status: cleared.** A clean build of an unmodified tree produced

    build/soulsilver.us/pokesoulsilver.us.nds: OK

against `soulsilver.us/rom.sha1`, and `cmp` against the retail dump reports the
two files identical. The build completed with no compiler or make errors.

## Building a *modified* ROM

`COMPARE` defaults to `1`, so **even a plain `make soulsilver` verifies every
built file against the retail original** and aborts on the first mismatch. That
is correct for proving the toolchain, and wrong once we start changing things.
The first real edit fails like this:

    files/a/0/2/7: FAILED
    sha1sum: WARNING: 1 computed checksum did NOT match
    make[2]: *** [filesystem.mk:563: filesystem] Error 1

`files/a/0/2/7` is `files/msgdata/msg.narc`, the message archive, so that is
simply the build noticing that dialogue changed. Build Rocket Silver with the
check off:

    make soulsilver COMPARE=0        # modified ROM
    make compare_soulsilver          # unmodified tree, proves toolchain

Expect the resulting ROM to differ from retail across a very large byte range
even for a one-line text change. Editing a message bank resizes an archive,
which shifts the offset of every file packed after it. A large byte diff is
therefore normal and is not evidence of a problem; judge changes by running the
ROM, not by diff size.

## Emulator verification

DeSmuME runs headless for screenshots. The binary installs to `/usr/games`,
not onto `PATH`:

    apt-get install -y desmume xvfb x11-utils imagemagick xdotool openbox
    setsid nohup Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 < /dev/null &
    setsid nohup openbox --display :99 >/dev/null 2>&1 < /dev/null &
    setsid nohup env DISPLAY=:99 /usr/games/desmume-cli --load-type=1 ROM.nds &

Notes learned the hard way:

- Detach with `setsid nohup ... &`; a plain `&` dies when the shell call ends.
- The window is 256x384 (both DS screens stacked). Find its origin with
  `xdotool getwindowgeometry`; the touch screen is the lower half.
- Drive the game by **touch**, not keys: `mousemove`, `mousedown`, brief hold,
  `mouseup`. Avoid sending `Escape`, which quits the emulator.
- Screenshot with `xwd -root` piped through `convert`, cropped to the window.

### Driving the new-game sequence

Blind timed tapping at the screen centre does not work; most prompts have a
specific target and a centre tap either misses or picks the wrong menu entry.
Window-relative coordinates within the 256x384 window:

| Target | Coordinates |
|---|---|
| "Touch to Start" | anywhere on the lower screen |
| Bottom-right confirm ("Touch") | 225, 362 |
| Tutorial menu, third entry ("No Info Needed") | 128, 348 |

Symptoms worth recognising: repeating the same message box means the confirm
button is being missed, and cycling back to the topic list means a centre tap
is re-selecting a tutorial topic instead of dismissing the menu.

This approach remains fragile. Before doing much scene work, build a savestate
harness so any scene can be reached directly instead of replayed from boot.

### Verifying a change without the emulator

Preferred, because it is deterministic:

- **Text**: read the message archive back out of the built `.nds` with
  `tools/nds.py`, `tools/narc.py` and `tools/text.py`. Message banks live at
  `a/0/2/7`; bank *n* is `Narc[n]`, decoded with `text.decode_file`.
- **Code and data**: search the uncompressed `build/soulsilver.us/main.sbin`,
  not the `.nds`. The ARM9 binary is compressed when packed into the ROM, so
  compiled structures are not findable in the finished file.

## Conventions

- ROMs, patches, and the proprietary toolchain archives are never committed.
- Verify each milestone in an emulator, not only by a successful compile.
