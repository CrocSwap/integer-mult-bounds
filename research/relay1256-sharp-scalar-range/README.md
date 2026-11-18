# Sharp ranges for the role-1256 scalar graph

This package proves the exact largest normalized scalar values in the
fixed graph from [PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704).
The sharp ordered-prefix bound is `53895757/256`, versus the source's
separate-product triangle bound `13819451/16`. The graph and donor order
stay fixed. No new kappa or selected-frontier change follows.

Read PROOF.md for the contract and RESULT.json for all attaining inputs.
The proof covers arbitrary real entrance values in the unit cube. The
finite check covers all 7644 rows, 172414 ordered prefixes and 9044092
nonzero basis products. Eight complete scalar replays verify the four
attaining corners both over the rationals and on an integer lattice.

The sharp completed-row, product and predivision-numerator bounds are
`2140811/96`, `4340699/24` and `36262265/32`. For signed W-bit integer
entrances that are multiples of 921600, the normalized arithmetic needs
at most `W+21` signed data bits. A reachable 32-bit entrance fixture
fails with `W+20`. The separate sharp growth counts for completed rows,
prefixes, products and numerators are 15, 18, 18 and 21 bits.

The source's physical `W+26` service uses a different W contract. Physical
chart norms, paid-child internal states, root scaling, tape costs and
compiler substitution remain open here. The five selected assumptions
remain. This is an author-checked source-bound arithmetic result, not a
full endpoint audit, supplier admission or formal multiplication proof.

## Reproduction

Use CPython 3.12 and the standard library. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/relay1256-sharp-scalar-range
```

For a standalone copy, run both commands:

```sh
python3 -I -W error -B research/relay1256-sharp-scalar-range/verify.py
python3 -I -W error -B -O research/relay1256-sharp-scalar-range/verify.py
```

Each prints:

```text
PASS_RELAY1256_SHARP_SCALAR_RANGE
7644 rows; 172414 prefixes; 9044092 basis products; 8 scalar oracle runs
Extra signed bits: snapshots 15; prefixes 18; products 18; numerators 21
```

The checker reads committed bytes and never rewrites the receipt. It
checks source hashes, chronology, donor charts, exact integer divisions,
all ranges, the source triangle bound, four attaining corners, four
scaled integer corners and four one-bit-smaller failure witnesses. It
also checks that the row with the largest prefix ends as entrance 1372.
This detects a bound that considers completed rows alone.

SOURCES.json binds the main-branch catalogue and selected record. The
unmerged graph is copied from an explicit public commit and checked by
both compressed and decompressed hashes. CREDITS.md records that source;
it is not an inferred ancestor of main. Its full predecessor suites,
selected cold replay, physical application, native operators, Lean,
Docker and independent human/formal-kernel review were not run here.

## Open next questions

1. Can a bound on `T_current * inverse(T_input)` promote the exact scalar
   cancellation to a physical chart-valued range bound? Start with the
   shared factor for each entrance column. Child interiors and the
   common-root precision recurrence must still be covered.
2. Can a fully charged physical service use the smaller normalized
   range? First specify its input word contract and division temporaries.
   The present arithmetic proof supplies no tape or compiler cost gain.

Prepared by Ali Romman with substantial OpenAI Codex assistance under
Apache-2.0. Clear1nsight supplied the graph and source amplitude bound;
SYLforge supplied the word. CREDITS.md and credits/ preserve their
contributions and the bank, caller and framework lineage.
