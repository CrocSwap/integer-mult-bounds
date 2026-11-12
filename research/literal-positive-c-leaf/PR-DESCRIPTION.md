## Result and motivation

The physical positive Gaussian leaf already has exact arithmetic and a direct
O(fV) source proof, but its literal numerical-table export remains open.
This package implements one fixed 6,826-location, 29-tape graph for the
positive rank-one central factor of the actual selected #7000 MOVE24472,
`["MOVE",415,3,99,false]`.

Its exact kernel is `C=[[1+i,1-i],[1-i,1+i]]/2`, applied as `C^(tensor f)`
over all f columns. Rank one does not set f=1. The source binder recomputes
the actual lowering, both positive C columns and the complete local recipe,
including normalization and phase.

## Exact scope and full cost

The explicitly supplied packed field is `[P]x[2^f]^9x[S]`, with r Gaussian
coefficients per address on a common grid and w signed MSB bits per component.
Its six Gamma parameters are `f,r,P,S,w,cutoff`; the first five agree with the
published literal native phase ABI. The graph checks w>=2, f<=cutoff, every
Gaussian half, signed output range and exact complete cardinality.

All variable axis strides are generated on tapes. Full suffix splitting,
four-row finite-carry arithmetic, MSB restoration and full-array merging
execute for every f axis. A protected private field remains separate from
public DATA until all axes succeed. Successful commit uses the original owner
and returns every head, private body/guard and opaque exterior.

For `V=2PSr2^(9f)w` and header length E, the complete bill is
`T<=65536(fV+E+1)`, with private historical backing
`K_entry+64(V+E+1)`. Every helper, source return, copy, staging pass, install
and retirement is charged. Cutoff stays binary, so an arbitrarily large
threshold costs its encoded length. Shrinking clean calls do not rescan old
blank tails; histories are retained per actual owner/origin.

The accepting domain requires integral signed outputs at every executed
axis. Final-image fit alone is insufficient: `[1,0,0,1]` maps finally to
`[0,1,1,0]` under the two-axis tensor but fails the first exact half. Public
DATA is preserved on these named rejections. Private failure cleanup/retry
is not claimed and is weaker than the structured #6967 lifecycle.

## Novelty and predecessor credit

#3091 supplies the Gaussian rows, carry/parity/range proof, tensor reserve,
physical axis strategy and direct tariff; none is claimed new. #6967 binds
that structured kernel to the old coded interface. #6978/#6986/#6989 add
different source, cutoff and rounding wrappers while retaining the literal
numerical seam. This contribution supplies a fixed local graph and complete
ownership/history proof at the named packed boundary.

The packed ABI is credited to
[literal native quadratic phase](https://github.com/CubeJerry/integer-mult-bounds/tree/172f4535ce8dcff79f626410af845f757c1563be/research/literal-native-quadratic-phase).
Header/return patterns follow
[literal layer phase](https://github.com/CubeJerry/integer-mult-bounds/tree/8b549ca6557ccbb3017b104b27ea35051f990416/research/literal-layer-phase)
and its egress/#7349 lineage. All copied files have exact repository,
commit:path, blob and byte hashes in SOURCES.json. Frozen predecessors are
unchanged. No upstream PR number is invented for these review branches.

## Reproduction and verification

Tested base: `e54523517d0f03e58352e647c403a5af3e525a57`.

```sh
cd research/literal-positive-c-leaf
python -I -W error -B bind_source.py
python -I -W error -B check.py
python -I -W error -B check_big.py
```

Optimized-Python runs use `-O` and reproduce the same structured receipts.
The last command requires a C++17 compiler named `c++`; it compiles the
included dense local-table interpreter in a temporary folder. No external
library or network download is needed.

The author checks execute seven complete m=9,f=1 successes, six rejection
controls, a 2049-bit cutoff and three same-owner grow/shrink/regrow calls.
The actual unchanged m=9,f=2 graph executes all 262,144 addresses and
2,621,440 bits in 704,382,528 counted transitions, matching a direct tensor
polynomial oracle with all normal-retirement checks. A first-axis-only mutant
still retires correctly but fails that oracle; the endpoint-only witness
rejects without DATA writes. The local cutoff2 fixture is not a certified
global selected-producer packet.

Separate root execution and mutation checks, including smaller fixed-dimension
fixtures, are explicitly distinguished from that author's full actual f=2
trace. A separate peer independently authenticates sources, proves the
Gaussian spectral/geometry interface, checks 17,528 scalar components and
27 isolated axis cost cases, and derives exact scalar and whole-axis costs.
Unchanged reviews, portable commands and exact receipts are in independent/,
REVIEW.md and VERIFY.json. AI-assisted cross-review is not human or kernel
verification.

## Limitations and kappa status

**No new kappa; the complete multiplication bound remains conditional and
all five global assumptions remain.** This is a concrete direct-leaf
lowering, not an accelerated nonleaf or complete source caller.

The old 23-value/three-bit-coded LSB interface and strided native placements
require an explicitly supplied, paid format/packing/header bridge. The two
surrounding monomials, full MOVE/compiler composition, failure retirement,
global cutoff/stock/precision admission and analytic recovery remain open.
Matching the local source operator does not discharge those obligations.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Jose Manuel, Alejandro Zarzuelo Urdiales, Nick Petalas, James Chang,
AAAmirinu, the selected native/compiler authors and all retained predecessors
in NOTICE.md. New material is Apache-2.0.
