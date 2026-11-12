# A fixed tape table for the current selected quadratic Gaussian phase

**Scoped enabling lemma; no new kappa.** This package lowers the diagonal
part of one actual current #7000 monomial to a fixed local tape program:
native MOVE index 24472, owner 415, frames 3→99, rank 1, right factor. It has a nonzero
constant, seven nonzero linear coefficients and fifteen quadratic pairs.
`RECIPE.json` records the exact source lowering.

The graph has **8,211 locations, 23 tapes and four symbols**. Runtime control
uses only scanned symbols, one-cell writes, unit moves, fixed jumps and
halt. It receives a supplied five-Gamma descriptor `(f,r,P,S,w)` and the
complete packed payload `[P] × [2^f]^9 × [S]`, with r signed Gaussian fields
per record. It applies the tensor phase, including the constant `i^f`, and
commits the exact result to the original owner. Successful calls restore
every head and private window. A signed range failure leaves the complete
public payload unchanged, without promising failure cleanup or reuse.

For `Q=2^(9f)`, `N=PQS r`, `V=2Nw` and descriptor length E, the complete
bound is `65536[E+10f+r+P+S+w+100PQ+V+1]`, hence **O(V)** for every positive
f on this supplied interface. It includes header acquisition, synchronized
counters, repetitions, signed staging, commit and erasure. The proof also
retains historical backing relative to prior history K0.

## Novelty and limits

[#5375](https://github.com/CrocSwap/integer-mult-bounds/pull/5375) already
proves the incremental multicounter phase algorithm and repeated constant.
The structured physical Gaussian monomial and selected record-list work
are predecessors. The new result is this current recipe's literal table,
complete original-owner contract and bill; see [PROOF.md](PROOF.md).

The native descriptor producer, bridge from a gapped/interleaved layout,
affine routing, source scalar arithmetic, recursive C call and caller
lifecycle remain open. This is not a complete monomial, all-column supplier,
selected layer or multiplier. All five foundational assumptions remain in
the complete theorem and its conditional kappa is unchanged.

## Evidence and reproduction

Python 3.11+ and standard library only, from the repository root:

```sh
python3 -I -W error -B research/literal-native-quadratic-phase/bind_selected.py
python3 -I -W error -O -B research/literal-native-quadratic-phase/bind_selected.py
python3 -I -W error -B research/literal-native-quadratic-phase/verify.py
python3 -I -W error -O -B research/literal-native-quadratic-phase/verify.py
```

Expected markers: `PASS_CURRENT_SELECTED_QUADRATIC_RECIPE_BINDING` and
`PASS_LITERAL_NATIVE_QUADRATIC_PHASE_NO_NEW_KAPPA`. Normal/optimized outputs
match the BINDING and RESULT receipts. These are standalone commands;
the package does not claim a registered research-package schema.
VERIFY.json records these direct commands and the two independent replays.

Source binding authenticates eight unchanged references, reconstructs the
actual recipe, checks its full kernel with the retained independent
signed-Pauli/Gaussian interpreter, and checks all 512 right-monomial basis
inputs against a separate parity formula. This is not a new catalogue review.

The packet replay covers **376 complete packets, 11,991,714 transitions and
all 336 width 1–3 Gaussian endpoint pairs**. It rejects 53 exact range cases
without a public write. Four complete packets use actual m=9,f=1, including
outer/spectator/coefficient repetitions and widths 1,2,5,17; smaller fixed
dimensions cover f=1,2,3. Its direct address/polynomial/integer oracle does
not use incremental phase updates. Four controls detect an omitted repeated
phase, deleted actual quadratic pair, wrong linear sign and corrupt commit.
No complete selected m=9,f=2 packet is claimed by this author replay.
Universal claims rest on the written invariant and scan proofs.

## Independent review

The lead's separate dense CPU and XOR/popcount oracle pass 16 cases and
6,428,358 transitions, including exact public preservation and successful
longer-to-shorter reuse. Its selected f=2,3,4 inputs deliberately stop after
300 coefficients: correct staged prefixes are checked, not full tensor
execution. All eight exact Git source bindings were independently verified.

A second reviewer accepts the universal phase/geometry, complete cost,
retirement and historical-storage proof. A separate interpreter checks
11 complete successes, 9,362 record entries and 6,786,145 transitions.
It derives and verifies an exact counter-movement census. One cost control
is functionally correct but unnecessarily scans the full counter width;
the census detects that error. Review, sources, receipts and portable
commands are in [independent/README.md](independent/README.md).

## Open next questions

1. Produce this descriptor and packed layout at a selected native occurrence,
   or lower the existing arbitrary-active-mask version with physical costs.
2. Join its affine route and rank-one child with complete source access,
   current-chart, private-lifetime and return accounting.
3. Establish the common grid and signed headroom at that joined caller.

## Credit

Prepared for **@CubeJerry (Jerry Chen)** with substantial OpenAI assistance
in mathematics, implementation, checking and prose. Apache-2.0. Credit
Ali Romman/#5375; #7000's DreamingOfClouds, Ali Romman, Cinna Davis, zxv,
unpaidmoon, icekylinx and earlier native/Gaussian authors; C2's
`literal-layer-phase` for Gamma and signed staging/return; B1's
`literal-layer-egress` for owner staging; and #7349 for the retained literal
machine. Exact pins are in [SOURCES.json](SOURCES.json). Independent AI
review is not human or proof-kernel acceptance.
