# Exact direction optimum for two QQ16 scratch sweeps

**Scoped physical-access cost lemma and construction; no new kappa.**
Allowing each scalar instruction to traverse its aligned sites in either
increasing or decreasing order improves Nick Petalas's [PR2722](https://github.com/CrocSwap/integer-mult-bounds/pull/2722)
fixed-forward bank-major streaming tariff as follows, for **every positive
integer N**. All tapes start and return at address zero separately for each
window.

| Window | Credited fixed-forward tariff | Minimum with chosen sweep directions |
|---|---:|---:|
| L2 | `3564N - 896` | `3518N - 850` |
| F0 inverse | `8302N - 1944` | `8222N - 1864` |
| Total | `11866N - 2840` | **`11740N - 2714`** |

The saving is **`126(N-1)` word-address head steps**, strictly positive for
N >= 2. For N=2 the bills are 20,892 and 20,766. This is a modest local
movement improvement, approximately 1.06% of the leading coefficient.
It is not a runtime or recursive-exponent improvement. PR2722's tariff is
correct for its stated fixed-forward protocol.

## Exact contract and inherited charges

Pin PR2722 at `a9ec1a4f45f36d4ec131e43cf8528ea0e40ea4e8` and its source,
ywz65's PR2709, at `d7749c49e967b214537c0bd832e435e177e21d4f`.
[Source pins](SOURCES.json) identify the original word by commit, path, Git
blob and decompressed SHA256. The retained compressed word is input data,
not imported executable code. The verifier was written after consulting
PR2722's proof and implementation; it does not import or execute that code.

There are two independently movable tapes, Z and W, each containing 112 banks
of N scalar sites at `address(bank,site)=bank*N+site`. Keep the same two
scalar-only windows, same instruction order, same alignment, same scalar
source register, in-place target arithmetic and PR2722's eight restored
dirty-Z0 bridges. A CLEAR touches one tape; every rewritten ADD touches one
bank on each tape, reading its source before updating the destination.

The **only changed premise** is that each entire instruction sweep may choose
site order `0..N-1` or `N-1..0`. For an ADD both tapes use the same site order.
The next instruction starts after the previous instruction finishes at every
site. The minimum is over precisely these choices, not instruction reordering,
partial sweeps, caching, scalar resynthesis, different layouts or endpoints.

Whole-window exclusive W ownership and temporarily modified Z0 remain required.
No extra payload array or scalar arithmetic is added relative to PR2722.
The complete local scalar counts remain 864 unit ADDs, 832 quarter ADDs and
288 CLEARs, with inherited allowance **17,472**. Its 448 native events,
rank mass 352, 480 wrappers, 208 cover maps, 224 owned output banks and sixteen
early retained values are inherited, not freshly admitted here. The checker
recounts the scalar invoice, not those native/compiler obligations.
Direction choices form a fixed compiled control string (432 and 976 bits),
recorded in [RESULT.json](RESULT.json); direction dispatch, instruction storage,
precision-dependent staging, bit arithmetic, retention, layout production,
output consumption and surrounding native placement remain additional costs.

## Proof of the minimum for all N

Write a sweep direction as its start endpoint bit `s` (0 or 1). Its end
endpoint bit is `1-s`. After any fixed instruction prefix, the last bank
visited on each tape is independent of direction choices. Only the two last
endpoint bits vary, so at most **four states** suffice.

Let one touched tape's previous bank and endpoint bit be `(b,e)`, and its new
bank be `c`. Moving to the sweep start and traversing its N sites costs

```
abs((c-b)*N + (s-e)*(N-1)) + (N-1).
```

Sum this over the instruction's touched tapes, update their endpoint bits to
`1-s`, and keep untouched heads unchanged. The initial state is two heads at
bank 0, bit 0, with cost zero. At the end add each head's actual return distance
`b*N + e*(N-1)`. Induction on prefixes proves the Bellman recurrence includes
every allowed schedule and retains the least cost for each state. It gives
both a lower bound and an attaining schedule, not a heuristic search.

For a **fixed** direction string every edge cost is affine for all integer
N >= 1. To see this, put the integer `d=c-b` and `h=s-e` in `{-1,0,1}`. If d=0, the
absolute value is `abs(h)*(N-1)`. If d>0, `d*N+h*(N-1)` is positive, since its
minimum over h is `(d-1)*N+1 >= 1`; d<0 is analogous. Return and within-bank
costs are also affine.

At N=1 both endpoint bits represent the same physical cell. **Every direction
string has the same total closed cost C**, the bank-number walk. Thus every
schedule has cost `C + L*(N-1)` for some integer L. Minimizing at N=2 minimizes
L and therefore minimizes simultaneously at every N >= 1. No interpolation
from empirical sample values or assumed stabilization is involved.

The exact DP at N=2 gives 6,186 and 14,580. The common N=1 costs are 2,668 and
6,358. Hence the two minimum polynomials in the table follow. The committed
direction strings attain them. The receipt also records digests of every
N=2 Bellman cost layer for reproducibility.

## Scalar correctness and restoration

Changing the site order of one pointwise instruction only permutes operations
on disjoint cells. Because instruction order is unchanged at each site, the
entire scalar map is unchanged for arbitrary inputs and dirty outputs, over
any coefficient module supporting the original operations. The two tapes
must stay aligned: reversing only a source's site order is not this operation.

For clarity, the credited bridge is
`Z0+=g; f-=Z0; Z0-=g; f+=Z0`. From arbitrary `(z,f,g)` it returns
`(z,f-g,g)`. Reversing individual whole-site sweeps preserves that identity
at each site, even though intermediate Z0 values at many sites coexist.
The original final scratch clears remain. This proof covers these scalar
windows; the predecessor's native semantics, frame compatibility and full
QQ16 decoder are inherited assumptions.

## Reproduce and controls

Standard-library Python 3.12 or later, from the repository root:

```sh
python3 scripts/research_package.py --package research/qq16-oriented-scratch-sweeps
```

Expected primary output:

```
PASS_QQ16_ORIENTED_SCRATCH_SWEEPS travel=11740*N-2714 saving=126*(N-1) orientation_only no_new_kappa
```

The registered hook runs normal and optimized primary checks and five behavioral
test groups. Direct verification also works in a Git-free export. It checks:

- Exact source length, SHA256, Git blob, scalar windows and source scalar bill;
  reproducible directions and type-sensitive committed receipts.
- Literal cell-by-cell address walks and DP agreement at N=1..16,32,64;
  large-integer endpoint arithmetic at N=10^30.
- A separately written physical-address frontier oracle for both full windows
  at N=1,2,3,7. It uses actual head addresses and literal accesses rather than
  the primary endpoint-bit recurrence or cost formulas.
- All 340 words of lengths 1..4 over four tiny CLEAR/ADD choices, all their
  direction strings, at N=1,2,3; the N=2 attaining schedule also passes N=7.
- Exact rational dirty-state equality on every Z/W cell at N=2,3,5, including
  the unchanged original scalar bodies and the credited bridge rewrite.
- Changed source bytes, missing/changed/boolean-typed receipts, same-tape ADDs,
  borrowed or inactive fields, non-scalar events, aliases, wrong-site reads,
  wrong bridge-restoration sign and missing head returns. Equivalent gzip
  recompression and all-reversed scalar execution are positive controls.

These are finite checks supporting the written quantified proof. They are not
an independent human review, formal-kernel proof, full native replay or selected
supplier cold replay. Source pins do not establish the pending predecessors'
complete claims. No selected record or frozen predecessor is changed.

## Task, scope and next question

[Task metadata](TASK.json) records recursive-interface selection nonce
`19bf211be599d9fc291f47cf30e0a121`, priority revision 5, base canonical main
`c22e42de697334df85337e005864773cdc2bc98b`, overlap checks and their limits.
The standard overlap helper could search local notes but could not refresh
remotes because gh is absent. Connector scoped all-state PR searches and
public HTML of Discussions 1163,1166,2617 supplemented it; those HTML pages
may omit hidden or paginated comments. A scoped claim comment on PR2722 was
rejected with HTTP 403, so no public advance claim is asserted.

The family decision is **narrow**: finish this single physical-cost lemma and
stop. The favorable orientation bill does not price unknown costs as zero or
justify another supplier construction round.

### Open next questions

Does a complete physical QQ16 caller satisfy whole-window exclusive W ownership
and preserve a favorable complete cost after retention, bit-level staging,
instruction control and native entry/exit placement? Pin one actual caller,
verify its W/Z lifetimes, and price those obligations under the same model
before interpreting this saving as a complete improvement. The absent caller
ledger is the blocker; this note does not propose a larger orientation census.

## Credit and license

Prepared for David Sanders with substantial OpenAI Codex assistance in task
selection, derivation, implementation, testing and writing. Apache-2.0.
Credit **Nick Petalas / PR2722** for the source-bound fixed-forward tariff,
two-tape access model, dirty bridge and streaming construction; **ywz65 /
PR2709 and PR2540** for scratch reuse and the complete local decoder;
**commdata2338 / PR2651** for early output-bank retention; and the retained
Ali Romman, starship-s, Sagar Thakrar, Ross Richardson and native/geometry
lineage. This result only adds the direction optimization and its scoped
optimality argument/checkers.
