# Joined one-target hole mask, reverse-word keys, and repair

**Scoped proof with an exhaustive finite component. No new κ.** The selected
conditional exponent is unchanged.

## Scope and evidence

Original card: `uniform-transfer-audit`, refined to one proposition. Cinna
Davis's PR #4100 restores bad CRT addresses by the key `T(S^{-1}(x))` and a
sparse repair (`CRT.md` §4). Three later audits each stop at their own output:

- #4208/#4201 produce the one-target hole mask and erase the scanner's counter;
- #4169's reverse word inverts the compact macro, including on dirty addresses;
- #4328 prices the repair, but reads a host-built mask and a host-built table of `S`.

#4328's first open question is to compose those pieces. Its stated blocker was
the full `E(p, ell)` evaluator. That evaluator now has a constant in #4377, and
it is a different machine from these reverse shears. The ownership join was
still open.

[PROOF.md](PROOF.md) counts the stencil for every admitted one-target geometry
`(G, H, K, Y, J, B)`. The scanner mask is the hole set of the pinned `good`
predicate. Keys at holes are the #4169 reverse shears followed by the ideal
map; the program does not invert a stored table of `S`. Because `S` and `T`
both permute the holes, sorting by `T(S^{-1}(x))` writes the record of `q` at
`T(q)`. The producer's eight private tapes, the scanner counter, the mask and
the repair scratch are erased.

The universal shear inversion and the scanner's flag machine stay cited from
#4169 and #4201. Both are rechecked on every address of the geometries below,
not re-proved for every larger size. The repair cell counts obey the #4328
bounds on this same schedule. They are not a new tariff.

`verify.py` exhausts every address of

```text
(G, H, K, Y, J, B) =
  (1, 1, 5, 5, 0, 0), (1, 1, 5, 5, 0, 1), (1, 2, 6, 7, 1, 0),
  (1, 3, 5, 6, 0, 2), (2, 2, 6, 8, 2, 0)
```

with source bit `J + 1`, and repeats the first geometry with source bit `2`:
**23,040** addresses and **19,392** holes. Three controls fail in the stated
way. Origin keys still satisfy "key equals the hole address" and misplace the
payload. A complemented mask does too, because `S = T` on the good set, and
the ideal image fails. A source that reads bit `J` is rejected before repair.

Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/crt-joined-hole-repair --check-only
python3.12 -B research/crt-joined-hole-repair/verify.py
```

The verifier prints `PASS_CRT_JOINED_HOLE_REPAIR`.

## Open next questions

1. Does a two-target stencil, with disjoint guards, produce the product hole
   set and restore payloads under the same reverse-word repair? CRT.md colors
   several targets in one layer. The first step is one extra digit block and
   one extra guard block at position `J + K`. It is blocked because the #4208
   producer emits one target only.
2. Is one reverse shear at most the #4377 budget
   `E(p, ell) = 2^{4 ell}(p+2)^{16}` at the actual control width `H`? This
   join does not identify the shears with that Beneš evaluator, so the `o(V)`
   absorption is not yet a bit-step price for these keys. The first step is to
   expand one `H`-bit modular addition in that bit-step model. It is blocked
   because the shears are not expressed as those rotation tables.

## Credit

Cinna Davis supplies the CRT construction and the compact macro in PR #4100.
ToikY's #4201 and #4208 supply the scanner and the unary producer. Hiroki
KUMAZAKI's #4169 supplies the reverse word. Ryanson Jonathan's #4328 supplies
the repair schedule, the cell bounds and the open composition question.
Douglas Colkitt supplies the compact-control and sparse-repair ancestry those
packages retain. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Apache-2.0. No independent human review or proof-assistant
acceptance is claimed.
