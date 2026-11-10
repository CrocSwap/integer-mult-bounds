# Caller admissibility of the cut-9047 witnesses

**Scoped audit; no new κ.** The #5546 separators at forward cut 9047 still
work on the #5402 entrance that the #5413 caller runs. The selected record is
unchanged (`781451/250000000`).

#5546 proved that the native variations `(L300=u, L505=-4u)` and
`(L301=u, L226=u)` fix the three coframed rows and move the pure helper
coordinates. It left open whether those variations are legal inputs of the
caller. This package checks that entrance and does not rerun the word.

The entrance multiplies eight mode owners by 2, applies monomials `Km`, and
runs the 834-instruction input basis on 122 helpers. [PROOF.md](PROOF.md)
records two readings.

- If `Km` is collapsed to the scalar 2, the entrance has rank 122. The
  published L300 witness is the public input `(L300=u, L240=-u/2, L505=-4u)`.
  The published L301 witness is already public. Both transfer verbatim.
- If mode inputs are kept out of the empty-warp keys, the verbatim L300 pair
  moves coframed row L301 by `-3u/8`. The bare public correction
  `(L300=u, L505=-4u, L226=-3u/8)` fixes every coframed row and still moves
  native `L300` by `u`. The L301 witness is unchanged.

Either reading supplies a legal variation that preserves the cut rows and
moves the pure coordinate. No prefix, basis, or anchor change is nominated.
The checker prints `PASS_CUT9047_CALLER_WITNESS_DOMAIN`.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/cut9047-caller-witness-domain
python3 -B research/cut9047-caller-witness-domain/verify.py
```

The registered command has a 60-second timeout. It authenticates the compressed
word, the provider entrance and the #5546 row table, checks that all three
bind the same payload, and evaluates the rank, the warp-blind preimage, the
`-3/8` leak and the corrected separator. Three mutations must fail: a zero
scale, a dropped `L226` correction, and a wrong `L505` coefficient.

## Scope

The coframed rows are an input from #5546, not a new derivation. `Km` is not
replayed through the 9,047 native events. Mains stay fixed. This is not a
paid-profile change, a compiler or precision bill, or a multiplication theorem.

## Open next questions

- After each mode monomial `Km` is carried through forward events `0..9047`,
  does any `Km`-keyed term meet a coframed row on the empty warp word? The
  bare witnesses set every mode input to zero, so they do not use that replay.
  A term that returns to the empty word would need its own separator.
- If a later caller replaces the #5402 basis, the corrected witness has to be
  recomputed before any prefix credit. No replacement entrance is proposed here.

## Credit

Cao Yifan supplied the #4610 word. Dillon Amburgey supplied the #5402 provider
entrance. Chris R (Clear1nsight) supplied the #5546 cut and the #5413 caller
schedule that runs that entrance. The coded-native-caller and balanced-J
lineage supplied the main/helper split this audit uses only as classification.
Retain the source authors credited in those packages.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New material
is Apache-2.0. The pinned inputs are unchanged.
