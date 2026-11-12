## Result and motivation

The elementary stream proof already uses a two-stack method to reverse whole
records while preserving each record's bit order. This package supplies a
literal implementation at the actual fixed-count canonical binary-descriptor
interface: one 524-location, 13-tape program reads P,R,B, reverses the R
complete B-bit records within every prefix, stages the full result, and
commits it to the original DATA owner.

The graph contains only scanned-symbol branches, one-cell writes, unit moves,
fixed jumps and halt. Its executing controller receives no decoded shape,
computed address, host loop, or trusted permutation stream. Successful calls
restore descriptors, every head, all private bodies/guards, and opaque
exteriors. Invalid finite descriptor/cardinality packets reject before any
DATA write; failure cleanup is not claimed.

## Exact result

For V=PRB, E the sum of the three binary lengths, and s binary popcount, the
accepting instruction count is exactly:

`53V+23PR+71P+54R+54B+28E-30(s(P)+s(R)+s(B))-8`.

Thus the complete cost is at most `256(V+E+1)=O(V)`. Private historical
backing is at most `K_entry+8V+E+18`; erased cells remain charged. A clean
smaller call need not rescan old tails, and the same nine private owners
support grow/shrink/regrow calls. Fixed origins admit per-role maximum
extents; translated origins retain absolute history unions and caller
transport costs.

When R=2^f, the map is XOR by all ones on that entire contiguous f-bit block.
A fixed binary translation vector composes a fixed number of paid calls
with supplied collapsed descriptors. The retained `flip_digit` source map
is explicitly matched, without treating its old Python caller as literal.

## Novelty and predecessors

The reversal algorithm and high-level elementary linear scan theorem are
credited to canonical `upstream/build/sections/02-streams.tex`; neither is
claimed new. #3834 records controlled-block/XOR evidence following #3825.
#5188 supplies a different literal two-field interchange. The retained
serial monomial caller and #6992 still use a structured permutation service.
This contribution adds the scoped fixed graph, full same-owner bill and
history contract, not a new general affine theorem.

Helper patterns follow @CubeJerry's verified
[literal layer phase package](https://github.com/CubeJerry/integer-mult-bounds/tree/8b549ca6557ccbb3017b104b27ea35051f990416/research/literal-layer-phase),
which credits the
[literal egress package](https://github.com/CubeJerry/integer-mult-bounds/tree/51ab0539059214fcfa044938c36a0b6017232be5/research/literal-layer-egress).
Exact source files and hashes are in SOURCES.json. No upstream PR number is
invented for those review branches.

## Reproduction and checks

Tested base: `e54523517d0f03e58352e647c403a5af3e525a57`. Only
`research/literal-row-reversal/` is added; canonical sources and the selected
certificate are unchanged.

```sh
cd research/literal-row-reversal
python check.py
python -O check.py
```

The normal and optimized receipts match: 3,814 accepting packets, including
all payloads on all 38 positive shapes with V<=8, plus 64 seeded larger
cases; 4,053,639 accepting transitions. Every accepting run checks the exact
cost census, current visit caps, complete DATA-write count, owner identity,
headers, heads, private cleanup and opaque exteriors. Twelve malformed
packets preserve DATA, six actual graph mutants are detected, and two wrong
permutation alternatives separate bit reversal from record reversal and
cross-prefix leakage. Additional checks cover six same-bank reuse calls,
21 pinned-source map comparisons, and five fixed-vector examples using
15 literal calls. Full commands, expected receipts and independent review
artifacts are listed in VERIFY.json and REVIEW.md.

## Limitations and kappa status

**No new kappa. The selected multiplication bound remains conditional, and
all five global foundational assumptions remain unchanged.** This proves
one concrete payload-moving primitive at an existing source boundary.

Supplied collapsed descriptors, initial private blankness/ownership, and
entry heads are explicit premises. Their production and transport must be
charged by a caller. Strided selected-bit packing, arbitrary affine routing,
complete native caller composition, and failure retirement remain open.
Reversing a larger field to imitate selected stride-K bits is incorrect;
the package includes that scope counterexample. Finite checks are not
represented as a universal proof or proof-kernel audit.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Predecessor contributions and source licenses are retained in NOTICE.md;
independent AI-assisted reviews are distinguished from human acceptance.
