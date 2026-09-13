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
- [x] Masked Man in the intro, converted from canon artwork
- [x] Masked Man as an overworld NPC in the hideout, with his Mission 1 briefing
- [ ] Silver as the player character, Gold as the rival
- [ ] Mission 1: the New Bark Heist
- [ ] Mission progression backbone

## Overworld sprite slots

Sprite ids and model ids are separate numbering schemes paired by name. Of 832
names in both tables, 670 are unused by any map. `SPRITE_BRAINS1` (model 103)
now holds the Masked Man: a Battle Frontier Brain that appears nowhere in Johto
or Kanto, so nothing in the game loses a character.

Do not assume a sprite used in only one map is safe to take. `SPRITE_AJI_PERU`
looked ideal on that test and turns out to be the Persian statue in the Rocket
hideout, not a person. Read the script that references an object before
repurposing it.

## Writing dialogue

The character set has no ASCII apostrophe. Use the typographic one, as every
line of vanilla text does. The encoder rejects the file rather than producing
something broken, so a build failure here is the tool doing its job.

The player's name is `{STRVAR_1 3, 0, 0}`. Check how vanilla text writes a
variable before inventing one; several similar forms exist and they differ.
