# Independent adjoint audit of bridge-aware centre sources

**Independent finite audit; no new supplier or kappa.** Two separately written
algorithms reproduce the selected controller's **1,152-dimensional source-history
rank**, already reported in [PR2622](https://github.com/CrocSwap/integer-mult-bounds/pull/2622).
The new verification uses a backward local adjoint and dense controller matrices
to check every source coefficient against a forward rational calculation.

A concrete failure control explains the need for that coefficient check:
reversing **every bridge sign** retains rank **1,152** and the identity endpoint
on **14,336 owners**, yet changes **930 source rows**. One unit-input cut changes
from **+1 to -1**. Endpoint identity plus full source rank does not identify the
correct intermediate source map. This is a checker control, not a defect report
against PR2622, which authenticates its inputs and also audits the output response.

The scope is the common-frame scalar projection. Native owner/address routing
remains open; idle sweeps are explicitly identity here. This does not independently
verify PR2622's distinct final error-response map or claim priority for its rank.

## Exact boundary and result

The inputs are the selected PR1094 replay archive, bound by the selected assembly,
from main `c3c94c2ea2ebcd5d69d1e51b5fe8a36bf79819f5`. The archive contains the
actual **480-helper**, 704-role local word. No 492-helper ancestor is substituted.
[SOURCES.json](SOURCES.json) pins every external input. The selected conditional
kappa remains `836330098538459/500000000000000000`.

As in Adam Gall's PR1918 and thakrarsagar's PR2199, each physical owner starts
with an independent formal scalar over Q. Local `clear`, `copy`, `scale` and
`add` operations retain their exact coefficients. A `center` event records the
private C register at its rank-eight child. Local climbs, adapters, residual
adapters and the centre child itself act as identity in this declared projection.
The checker derives both local endpoint maps from **every scalar event** on all
704 formal columns and checks private clearing:

- forward: `Y_p += X_p` for all 112 ports;
- backward: `X_p -= Y_p` for all 112 ports;
- all other ordinary roles are restored.

The audit executes each bridge in the actual asynchronous event order. For
an event with destination pair d, source pair s and coefficient c, it applies

```text
X_d,p += c X_s,p
Y_s,p -= c Y_d,p
```

for every port p. The signed terminal is `(X,Y) <- (Y,-X)` simultaneously on
each pair. These formulas come from the pinned inherited complex geometry
proof, section “Four-pair scalar chain and idle children”. The complete
per-replica recipe and data-owner indexing are checked against the selected
template. In particular,
`owner(replica,pair,side,port) = 896*replica + 112*(2*pair+side) + port` is checked
against all local data-role maps, rather than assumed for arbitrary helper roles.

| Quantity | Calls-only predecessor projection | Projection with bridges and terminal |
|---|---:|---:|
| Local cover calls / centre rows | 144 / 1,152 | 144 / 1,152 |
| Rational rank of all centre rows | 1,152 | 1,152 |
| Changed centre rows relative to predecessor | — | 930 |
| Identity endpoint owners | 0 | 14,336 |

The calls-only comparison reproduces PR2199's call table, local cut support
sizes, complete centre-row support histogram and rational rank. It is a control,
not a defect claim against a predecessor that explicitly omitted these events.

A small exact witness shows that the added bridges matter. Set initial physical
owner **224** (replica 0, pair 1, X side, port 0) to one and every other initial
owner to zero. At call **time 10 / stage 2 / replica 0 / centre 0**, the calls-only
cut is zero and the bridge-aware cut is one. This witness is derived from the
complete symbolic rows, not from a sampled floating-point calculation.

Because all 1,152 rows are linearly independent, every subset is independent;
in particular, every two distinct calls supply 16 independent formal cut rows
in this model. This is **not** a 16-scalar output-transcript lower bound: that
would additionally need the fixed-dirt output-increment map, its consumer and
panel boundary. Full cut rank cannot replace those obligations.

## Two implementations and controls

`verify.py` propagates exact sparse rational forms forward through each local
program, composes them with a 14,336-owner state, and performs rational row
elimination. It checks the complete projected endpoint and emits [RESULT.json](RESULT.json).

`check_adjoint.py` imports neither that checker nor supplier code. It pulls each
cut backwards through the local scalar operations, then reconstructs the
chronological owner state using 16 dense integer 8-by-8 controller matrices.
Every coefficient of all 1,152 rows agrees with the first implementation through
the canonical row digest. Rows follow chronological call order, then centre
index 0 through 7. Each row is its ascending-column list of `[index, str(Fraction)]`
pairs; the digest is SHA-256 of compact JSON with separators `(',', ':')`.
A separate reverse-row, largest-column
elimination gives rank 1,152 modulo `2147483647`. All denominators are invertible
modulo that prime, so a nonzero maximal minor is also nonzero over Q; the row
count supplies the upper bound. The primary result does not rely on this modular
check: it also computes rank directly over Q.

Controls include all 18 individually omitted half-bridges, all bridges removed,
all bridge signs reversed, and dependent duplicate rows. Each individual
half-bridge omission breaks the 8-by-8 endpoint. Removing all bridges changes
both cuts and endpoint. Reversing **all** bridge signs changes the cuts but
**preserves** the endpoint: it conjugates the controller by the alternating-pair
sign matrix `diag(1,1,-1,-1,1,1,-1,-1)`. Every selected bridge joins opposite pair
parities, whereas each local call and terminal acts within one pair. Thus the
sign matrix negates all bridge shears and commutes with those other operations;
conjugation preserves the full controller's identity endpoint.

Both algorithms separately check that this wrong-sign controller also retains
rank 1,152, but changes 930 rows. For the owner-224 input above, its first changed
cut is -1 instead of +1. The receipt binds its full row digest and exact witness.
This finite counterexample establishes that **endpoint identity and source rank
together are insufficient** to certify the intermediate centre coefficients.

The checks remain active under Python `-O`. Both checkers authenticate inputs
before computing; normal primary execution compares every receipt field.

## Reproduce

Python 3.11 or later, standard library only, from the repository root:

```sh
python3 -I -B research/selected-centre-bridge-projection/verify.py
python3 -I -O -B research/selected-centre-bridge-projection/check_adjoint.py
python3.12 scripts/research_package.py --package research/selected-centre-bridge-projection
```

Expected markers:

```text
PASS_SELECTED_CENTRE_BRIDGE_PROJECTION rank=1152 changed_rows=930 endpoint_owners=14336
PASS_SELECTED_CENTRE_BRIDGE_ADJOINT rows=1152 rank_mod_2147483647=1152 controls=3
```

`verify.py --write` regenerates the receipt. The registered runner uses Python
3.12 and bounds each command by the replay manifest. Local
interpreter versions and actual runs are recorded in TASK.json. A local pass is
not a claim that upstream CI ran.

## Cost, limits and expansion decision

The unchanged 144 calls retain 1,152 rank-eight centre children, total rank mass
9,216, or 64 per call. There is no eliminated work and no changed cost profile.
No sharing construction is proposed. This result narrows a verification gap;
it does not pass the task card's construction or 10-percent improvement gate.

The 160 idle sweeps, 16 terminal Y translations, one bank-padding sweep and one
final every-family translation are explicitly assigned identity in this model.
Likewise, the exact complex phases and native address charts are not modeled.
This formal projection is **not proved to be a representation or specialization
of the native supplier**. Its rank need not be a native rank lower bound.
The identity endpoint also does not establish native correctness.

Full selected cold replay (`make frontier1094-verify`), native 512-address
operators, whole-cover owner routing, physical hosting, precision/tape costs,
all-size/compiler interfaces, analytic transfer and a multiplication theorem
remain outside scope. The selected record and frozen predecessors are unchanged.
The family decision is **narrow**: retain this scalar evidence and require an
explicit native boundary before any sharing implementation or larger search.

## Open next questions

Can the first changed cut (time 10, stage 2, replica 0, centre 0) be reconstructed
with the actual routed native bridge and idle operators? This would test whether
the scalar witness has a native counterpart. Start from the pinned owner 224
unit input and the exact route/phase maps through that cut, including both
bridge shears. The blocker is the cover/address action: treating it as identity
again would repeat this projection, not close the native question. A mismatch
would be a scoped counterexample, not a failure of the selected supplier.

## Credit and overlap

- Adam Gall, PR1918: original scalar projection and the separate output-rank lemma.
- thakrarsagar, PR2199 at `30ec048eedcaca970f94bbec0fdd3c52eacf9fdc`:
  calls-only census and the explicit bridge/idle handoff.
- ywz65, PR2564 at `64f940a8ee305a1b69f7db329f1ffa232e53c2ad`:
  terminal residual of two ablated calls, with bridge/idle events explicitly
  omitted. This package neither redoes nor extends its ablation calculation.
- ywz65, [PR2622](https://github.com/CrocSwap/integer-mult-bounds/pull/2622)
  at `4ffb893a08e8868057a30a065642d0b5f647f742`: already includes the complete
  bridge-aware source-history rank and identity endpoint, as context for its
  distinct output-error injectivity result. This package deliberately audits
  the source-history claim with an independent local adjoint, coefficient
  agreement and an endpoint/rank-preserving wrong-sign control. Neither checker
  imports its code or the PR2199 verifier. The existing rank is not a new result.
- Rohan Arun, Jeremy Kothe, Hao Yan, Douglas Colkitt and the retained selected
  construction/geometry lineage: exact scientific inputs and controller rules.

[TASK.json](TASK.json) records the task selection, overlap coverage, scope and
freshness. The contribution uses two separately written algorithms by the same
AI-assisted author; no independent human or theorem-kernel review is claimed.
Prepared for BigCactusLabs with substantial OpenAI Codex assistance in research,
implementation, verification and exposition. New work is Apache-2.0.
