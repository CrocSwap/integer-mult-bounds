# Borrowed source rows can tour several parity masks

**Exact local bit-circuit construction; no new kappa.** Three arbitrary
source rows and nine arbitrary target rows require 21 independent row ADDs
to apply three different source parities to three targets each. A borrowed
source row can walk through the three parity masks in one closed Gray tour,
fan each mask out once, and return to its arbitrary initial value in 13
ADDs. The eight-ADD saving includes the complete source restoration.

## Boundary map

For any row width `L >= 1`, let `A`, `B`, `C` and all target rows be
arbitrary elements of `F2^L`. The boundary must preserve `A`, `B`, and `C`
and make

```
X_i' = X_i + A + B
Y_i' = Y_i + A + B + C
Z_i' = Z_i + A + C       (i = 1, 2, 3).
```

The three target classes are independent. No source or target starts clean.
The source row `A` is an internal borrowed helper, and its exact restoration
is part of the output contract.

## Construction and complete invoice

Use `A` as the anchor and visit these masks of `(B,C)`:

| Anchor contents | Operation | Fanout |
|---|---|---:|
| `A` | `A ^= B` | — |
| `A+B` | add `A` to each `X_i` | 3 |
| `A+B+C` | `A ^= C` | — |
| `A+B+C` | add `A` to each `Y_i` | 3 |
| `A+C` | `A ^= B` | — |
| `A+C` | add `A` to each `Z_i` | 3 |
| `A` | `A ^= C` | — |

The anchor itinerary is `00 -> 10 -> 11 -> 01 -> 00`. Four charged source
transitions and nine charged target writes give **13 row ADDs**. At width
`L`, the bill is `13L` bit XORs, 13 source-row reads, and 13 destination-row
writes.

The independent baseline applies the sources separately to each target:
six ADDs for the `X` rows, nine for the `Y` rows, and six for the `Z` rows,
for **21 row ADDs** (`21L` bit XORs, 21 reads and 21 writes). Thus this local
construction saves 8 ADDs, or 8L bit XORs. Preparation and final restoration
are both included. Neither circuit uses copies, a clean helper, an extra
recursive child, a frame change, or a precision operation. Both use the
same aligned row frame. Head movement and hosting are not resources in this
row-register model; no claim about a hosted supplier or the selected
recursive profile is made.

Separately preparing and restoring each mask costs 17 ADDs: each target is
updated once, and the three independent anchor round trips cost 2, 4, and 2
ADDs. Sharing transitions along the four-state Gray cycle reduces that
invoice to 13. Within the declared one-anchor schedule class, the four
transitions are minimal: the closed walk must visit all four vertices of the
two-dimensional mask square, and a four-edge cycle attains the lower bound.
This is not a global minimum claim over arbitrary CNOT circuits.

## Relation to the selected bound and prior work

The originating task is `bit-helper-contract`; its scope is changed from
the inherited R439 H2/K helper-star word to this exact borrowed-source
boundary. The replacement is local: a temporary helper write is permitted
only when the arbitrary source row is restored exactly and every target has
its specified boundary value. This package does not assert a new general
H2/K criterion for R439.

Nearby work includes open PR [#2241](https://github.com/CrocSwap/integer-mult-bounds/pull/2241),
which shears one of two retained outputs to hold one fixed sum before fanout;
merged PR [#1968](https://github.com/CrocSwap/integer-mult-bounds/pull/1968),
which accumulates shared product terms before a two-wave dirty-output fanout;
and open PR [#2259](https://github.com/CrocSwap/integer-mult-bounds/pull/2259),
which fuses a four-source update into one aligned target stream. Open PR
[#2045](https://github.com/CrocSwap/integer-mult-bounds/pull/2045) and
[Discussion #2036](https://github.com/CrocSwap/integer-mult-bounds/discussions/2036)
use a newly allocated clean coded helper to send one three-source sum to two
outputs and restore it. Open PR [#1937](https://github.com/CrocSwap/integer-mult-bounds/pull/1937)
works inside the R439 helper-star donor interface. Earlier Discussion
[#1167 comment 18920388](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18920388)
prices a fixed four-source parity through one arbitrary dirty helper and
corrects helper contamination. Here one existing arbitrary source row walks
through three distinct parities; transition reuse across mask classes is the
mechanism under study. These comparisons are scope distinctions, not a
novelty certificate.

The construction is an exact local XOR-network result. No source-word
occurrence, selected supplier admission, recursive billing, or `kappa`
improvement is established. Source and selected-record pins are in
[`SOURCES.json`](SOURCES.json); the changed task scope and claim are in
[`TASK.json`](TASK.json).

## Reproduction

```sh
python3 -I -B research/borrowed-source-gray-mask-fanout-seed9b2fe133/verify.py
python3 -I -O -B research/borrowed-source-gray-mask-fanout-seed9b2fe133/verify.py
python3 scripts/research_package.py --package research/borrowed-source-gray-mask-fanout-seed9b2fe133 --check-only
```

The replay checks the exact 12-row linear map, all `2^12` one-bit dirty
states, inverse execution, the 21-versus-13 invoice, the minimum four-edge
one-anchor tour, and four controls for a leaked anchor, a missing parity
transition, a missing target update, and a wrong return transition.

## Open next questions

1. **Find an actual caller.** Search one source-pinned bit word for three
   target classes that need these shared parity masks at a common aligned
   frame. Charge the actual source references, frame schedule, host and
   recursive calls before claiming supplier relevance.
2. **More mask classes.** For a specified higher-dimensional source-mask
   family, find the shortest closed Hamming tour through the required masks
   and compare its charged transition count with independent mask preparation.

Prepared by Cinna Davis with substantial OpenAI Codex assistance. No
independent human review or proof-kernel verification is claimed. Apache-2.0.

Maintainer integration note: the originating task catalogue is pinned as
historical assignment provenance. The scientific verifier consumes its local
EXPECTED.json and constructs the complete circuit internally; it does not
read the live catalogue or depend on subsequent priority changes.
