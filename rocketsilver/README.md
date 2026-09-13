# Rocket Silver

A Team Rocket total conversion of Pokémon SoulSilver, built on the
pokeheartgold decompilation so that new scenes, events and mechanics can be
written as source rather than patched into a binary.

You play as Silver, an agent of a Team Rocket that has spent three years in
the shadows since Giovanni's disappearance.

- **`STORY.md`** — the campaign outline. Fourteen Johto missions, twelve Kanto
  missions, an interlude and an epilogue.
- **`BUILD.md`** — toolchain setup, base ROM identity, how to build a modified
  ROM, and how to verify a change.
- **`tools/`** — Python utilities for reading a finished `.nds` directly:
  filesystem, NARC archives, and Gen 4 text decryption. Used to verify changes
  without an emulator.

## Relationship to upstream

This is a fork of [pret/pokeheartgold](https://github.com/pret/pokeheartgold),
whose reconstruction of the original source makes the project possible.
Everything under `rocketsilver/` is ours; changes elsewhere are marked with a
`Rocket Silver:` comment.

## Build

    make soulsilver COMPARE=0

`COMPARE=0` is required once the source diverges from retail. See `BUILD.md`.
To check the toolchain itself is sound, `make compare_soulsilver` on an
unmodified tree must still reproduce the retail ROM byte for byte.

## Design decisions

- **Badges become Rocket rank insignia.** The engine gates field moves and
  Pokémon obedience on badge flags in 84 places. Silver earns those same flags
  on mission completion, relabelled, so every existing check keeps working.
- **New Pokémon forms come last.** They are the hardest work and block nothing.

## Progress

- [x] Toolchain verified: an unmodified tree rebuilds retail SoulSilver exactly
- [x] Opening narration replaced with the Masked Man's
- [x] Game opens inside Team Rocket's Mahogany base
- [ ] Mission 1: the New Bark Heist
- [ ] Mission progression backbone
