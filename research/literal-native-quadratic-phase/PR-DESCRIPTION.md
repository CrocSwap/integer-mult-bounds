## Result and purpose

This package lowers the diagonal phase of an actual current #7000 native
monomial to a fixed local tape table. The source is MOVE index 24472, owner 415,
frames 3→99, rank 1, right factor, at main
`e54523517d0f03e58352e647c403a5af3e525a57`. Its nonzero constant, linear and
quadratic terms are retained, including the constant once per column.

The graph has **8,211 locations, 23 tapes and four symbols**, using only
local reads, one-cell writes, unit moves, fixed jumps and halt. For every
positive supplied five-Gamma `(f,r,P,S,w)` descriptor and complete packed
`[P] × [2^f]^9 × [S]` payload, it phases every Gaussian field and commits to
the original owner. Success restores every head and private window. Exact
signed range rejection preserves the public payload; failure cleanup and
reuse are not claimed.

With `Q=2^(9f)`, `N=PQS r`, `V=2Nw` and descriptor length E, the proved bill
is `65536[E+10f+r+P+S+w+100PQ+V+1]`, hence O(V) on this supplied interface.
A separate historical bound retains prior backing K0.

## Novelty and predecessors

#5375 already proves the multicounter update and repeated constant phase.
Structured physical Gaussian monomials and selected record lists remain
predecessors. The new contribution is the current recipe's literal table
and complete owner contract, not a phase identity or full monomial theorem.

The [outer phase package](https://github.com/CubeJerry/integer-mult-bounds/tree/8b549ca6557ccbb3017b104b27ea35051f990416/research/literal-layer-phase)
supplies Gamma and signed staging/return; the
[egress package](https://github.com/CubeJerry/integer-mult-bounds/tree/51ab0539059214fcfa044938c36a0b6017232be5/research/literal-layer-egress)
supplies whole-owner staging, and #7349 supplies the machine. Exact source
pins and copied original notices are retained.

## Reproduction and checks

Python 3.11+ and standard library only, from the repository root:

```sh
python3 -I -W error -B research/literal-native-quadratic-phase/bind_selected.py
python3 -I -W error -O -B research/literal-native-quadratic-phase/bind_selected.py
python3 -I -W error -B research/literal-native-quadratic-phase/verify.py
python3 -I -W error -O -B research/literal-native-quadratic-phase/verify.py
```

Normal/optimized receipts agree. Source binding checks the actual event,
exact lowering, retained independent kernel, all 512 monomial basis inputs
and a phase fault. The separate arithmetic/address oracle checks 376
complete packets, 11,991,714 transitions, all 336 width 1–3 endpoint pairs,
53 exact range rejections and four semantic controls. Four packets use
actual m=9,f=1; smaller fixed dimensions cover multiple columns. The author
replay does not claim a complete actual f=2 packet.

## Independent verification

The lead's separate dense CPU/XOR-popcount oracle passes 16 cases and
6,428,358 transitions, including explicitly incomplete selected f=2,3,4
prefixes; eight exact Git source bindings pass. A complementary reviewer
accepts the universal proof and complete bill. Their separate interpreter
checks 11 complete successes, 9,362 records and 6,786,145 transitions, plus
three mutations. A functionally correct full-width rewind is rejected by
an independently derived exact movement census. Copied sources, reviews
and receipts are in `independent/`; the relocated copies also pass.

## Limitations and kappa

**No new kappa.** Descriptor/layout production, gapped-layout conversion,
affine routing, exterior scalars, recursive C and joined lifetimes remain
open. No complete native word, selected layer or multiplier is admitted.
All five foundational assumptions remain in the full conditional theorem.
The next obligations are the actual descriptor/layout bridge, affine/child
composition, and complete caller grid/headroom admission.

Prepared for **@CubeJerry (Jerry Chen)** with substantial OpenAI assistance.
Credit Ali Romman/#5375, #7000's retained native/Gaussian authors and the
B1/C2/#7349 predecessors. Independent AI checks are not human or formal
kernel acceptance. Apache-2.0.
