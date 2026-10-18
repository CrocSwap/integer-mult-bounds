# Independent audit of the P104 monotone-relay floor

Under the explicit correction-network model below, the P104 side correction
requires **at least 208 new monotone helper lifetimes**: at least two first
entries into each of the 104 distinct target endpoint frames. This counts
lifetimes, not simultaneous physical registers, and does not construct a
208-helper network or establish a recursive price.

The number 208 belongs to **Philippe Van Velzen's
[correction screen](https://github.com/philippeVV/integer-mult-bounds/tree/7dfc7a176d7de4e7eabaf553a0b187c1bd647546/research/p104-correction-screen)**,
reported in [Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18939575).
This independent audit supplies the missing explicit implication from its
finite support-cover calculation to arbitrary monotone linear relay networks.
It gives small rank-eight witnesses, a proof that permits cancellation and
helper-to-helper relays, and a concrete boundary example from the frozen word.
The predecessor's numerical floor and geometric cover are not claimed new.

Evidence status: exact finite checks plus a written scoped proof, with separate
AI-assisted mathematical review and premise reconstruction. No independent
human review or proof assistant. No supplier, new κ, or selected-frontier change.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18941961).

## Precise model

Keep the ordered source and target **frame paths** from PR #1972's 4,058-event
word, retained by PR #1991. The sources are `X0..X103`, with initial binary
labels `q_s`; target `Y_t` ends in an eight-dimensional subspace `H_t` of
`F2^9`. Frames are subspaces, not a particular choice of basis. The added
network must contribute `(I-G/2)x` to the targets for arbitrary source values
and independent dirty inputs. Here `G` is the ordinary rational root Gram
matrix in the pinned port order, reconstructed independently from the fixture.

The added network may:

- read the unchanged source `X_s` when it is in its retained frame;
- make arbitrary rational linear combinations, copies and clears of helpers
  **within an equal frame**, with coefficients independent of all input values;
- use arbitrarily many fresh helpers with source-independent initial values,
  including arbitrary dirty inputs, and mix those helpers freely;
- transport a helper without changing its logical coefficients along any
  nested path of subspaces, with jumps permitted;
- add corrections to `Y_t` in its current frame, and freely retime operations
  while preserving the ordered source/target paths.

Targets receive additive writes only: they are not cleared or rescaled.
The added network cannot read targets or the retained channel's `G/Q/D/C`
helpers, modify source values, preload source-dependent helper inputs, or use
any other operation to transfer source dependence. In particular, descending
transports and cross-chart operations are excluded whether free **or paid**.
No source reads may be hidden in coefficients, descriptors, or initialization.
The retained channel itself may continue its unchanged work; these restrictions
apply to the added correction network. The frozen word never writes an X value
and never reads a Y value, so added target corrections do not feed back through
that word.

A **helper lifetime** starts with source-independent contents and follows one
nested path. Discarding/reinitializing a physical register begins another
lifetime. A single physical register may therefore count more than once.
Restoration is relaxed for this lower bound: imposing valid dirty restoration
cannot reduce it. This is a linear logical/common-frame model, not native
operator or hosting admission.

## Exact finite premises

Write `supp_t = {s : (I-G/2)[t,s] != 0}`. Define

```
E_t = {s in supp_t : q_s occurs in an earlier frame of Y_t},
D_t = {s in supp_t : some retained X_s frame equals H_t},
N_t = supp_t minus (E_t union D_t).
```

The audit grants all earlier target contacts and all possible direct source
reads, without enforcing their chronological availability. This is a favorable
relaxation, so no source/target time-separation premise is needed.

The independent checker establishes:

| Finite premise | Result |
|---|---:|
| Distinct target endpoint subspaces `H_t` | 104, all dimension 8 |
| Nonzero correction entries per target | 48 |
| `supp_t = {s : q_s in H_t}` | all 104 targets |
| Direct source reads at an endpoint (`D_t`) | none |
| Binary span of `{q_s : s in N_t}` | exactly `H_t`, all 104 targets |
| Cover by two proper hyperplanes of `H_t` | all 104 targets |

The sizes of `N_t` are `{36:12, 44:24, 45:8, 46:24, 47:24, 48:12}`.
[RESULT.json](RESULT.json) supplies eight independent source labels and two
cover normals for each target. The rank-eight witness rules out any single
proper-subspace cover, without an exhaustive lower-bound search. The two
normals certify only the local geometric covering minimum of two; they do not
certify a chronological circuit, compatible coefficients, or dirty restoration.

The compressed labels need not use ordinary Euclidean binary pairing.
The checker binds membership directly to the recorded endpoint subspaces and
to the support of the root-derived correction matrix.

## Relay-safe proof

Project each helper's logical row onto the independent source inputs. At any
frame `V`, every source with a nonzero coefficient has its label in `V`.
Initially the projection is zero. A source read respects this invariant since
all frames on `X_s`'s path contain `q_s`. A same-frame linear operation can only
combine existing support; cancellation removes coefficients but creates no new
source dependence. A nested transport preserves coefficients and enlarges the
allowed subspace. This proves the invariant by induction, for arbitrary dirty
state and arbitrary relay depth.

Fix target `t`. For any `s in N_t`, the correction coefficient of `x_s` is
nonzero. It cannot be written to the target in an earlier frame, by the
invariant and the definition of `E_t`. Nor can it be supplied directly at `H_t`,
by the definition of `D_t`. It must arrive through a new helper's first entry
into `H_t` from a proper subspace. Helpers born at `H_t` have zero initial source
dependence; mixing them there adds no other source of information.

Suppose there were at most one such entering lifetime. Just before its entry,
its support lies in one proper subspace `V < H_t`, of dimension at most seven.
Subsequent mixing at `H_t`, including feedback among its helpers and arbitrary
cancellation, cannot create an `N_t` variable absent from that entrance.
Therefore every label in `N_t` would lie in `V`. The checked rank-eight witness
contradicts this. At least two lifetimes must enter each `H_t`.

Two different eight-dimensional subspaces are incomparable. One nested helper
lifetime cannot enter both. Summing the 104 target requirements proves the
**208-lifetime lower bound**. Any admitted proper-to-`H_t` transport has positive
dimension increment; a paid-rank floor of 208 follows only if that increment is
indeed the chosen billing rule. It is not a complete excess-cost invoice:
productive coverage, other operations, residual children and owners still need
an explicit accounting argument.

## Boundaries and controls

Counting target writers would give a false proof. As a local relay illustration,
in `H = F2^2`, two helpers
can enter from `<e1>` and `<e2>` with `x1+d` and `x2-d`. After adding the second
into the first at `H`, only the first writes `x1+x2` to the target. The checker
includes this positive relay/cancellation example: there are two entrances
but only one target writer. A helper's support can grow after its first entry.

Reusing the existing channel is a substantive change of premise. At zero-based
event **2463** (cut 2464), the original private register `C` descends to
`span(243)`. Its coefficient of `X8` is **−2**, while `q_8 = 408` is outside
`{0,243}`. The checker propagates this exact scalar derivative through the
frozen events. This is a concrete failure of the support invariant when those
existing descents/values are admitted, not an error in the native channel.

Five rejecting controls cover a wrong transport rank, removed puncture,
dependent rank witness, one-hyperplane claim, and wrong correction support.
The positive relay example and excluded-descent example complete seven control
groups. Acceptance uses integers, rational arithmetic and explicit binary
subspaces, with no Python assertions that disappear under optimization.

## Reproduce and coverage

Python standard library only. From the repository root:

```sh
python3 -I -O -B research/p104-monotone-relay-floor-audit/verify.py
python3 scripts/research_package.py --package research/p104-monotone-relay-floor-audit --check-only
python3.12 scripts/research_package.py --package research/p104-monotone-relay-floor-audit
```

Default replay authenticates the two source inputs, recomputes the complete
receipt and compares it with `RESULT.json`; it writes nothing. `--out NEW.json`
additionally writes the verified receipt exclusively to a fresh path. A source
export preserving these relative paths works without Git or network; the
registered metadata check separately requires Git provenance.

This replay checks every recorded frame transition, common-frame ADD/COPY,
source/target path, source/target read/write direction, all 104 support/rank
certificates, and one scalar derivative. It does **not** recertify all 280
channel columns, native phases, the original `G/2` identity, or the selected
cold replay. The mathematical lower-bound proof is written above; the finite
checker does not enumerate all possible networks. No simultaneous-stock bound,
208-helper construction, pricing interval, complete moment, global hosting,
precision/tape or all-size theorem is claimed.

## Open next questions

Can an explicitly scheduled relay network attain these geometric covers with
useful cost? Start with one target's two recorded hyperplanes, assign source
reads and helper lifetimes, then check arbitrary dirty restoration and price
all transports. The covers alone do not ensure compatible timing or values.

Can retained descending/private values beat this restricted floor? The cut-2464
example identifies a concrete excluded information source. First state which
retained lifetimes may be read and check their actual dirty coefficients;
then derive a replacement invariant or a full correction identity. Existing
P104 constructions and cut bounds must be checked for overlap before proceeding.

## Credit and provenance

Philippe Van Velzen / `philippeVV` supplied the 208 floor, the two-hyperplane
cover calculation and the broader correction/pricing screen at exact fork head
`7dfc7a176d7de4e7eabaf553a0b187c1bd647546`. This audit neither imports its code
nor rechecks its Smith form, no-relay floor, or pricing claims.

Rohan Arun / #1972 supplies the frozen scalar/frame word, Chafik Boukhalfa /
#1991 its native realization, Adam Gall / #1940 the schedule, and Josie Elliston
/ #1071 the fixture, with Ali Romman / #1125 and retained geometry/compiler
lineage. The adjacent 96-dimensional pooled-space result belongs to Gonzalo
Mier / #2173 and Gareth Davidson / #2251; it is not this lifetime count.

Base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision
4. Exact input hashes and Git blobs are in [SOURCES.json](SOURCES.json).
[TASK.json](TASK.json) preserves the single chooser draw, changed audit scope,
live overlap coverage and remaining questions. Frozen inputs remain unchanged.

Prepared by kumagi with substantial OpenAI Codex assistance in derivation,
implementation, independent AI-assisted checking and writing. Apache-2.0.
