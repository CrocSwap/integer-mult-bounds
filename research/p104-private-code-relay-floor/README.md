# P104 private-code access preserves the monotone relay floor

The P104 correction still requires **at least 208 monotone helper lifetimes**
in the model below, even if the entire eight-dimensional rational root code
is supplied for free at every frame. In particular, free read-only access to
the original eight private-descended signals does not lower this floor.

The number 208 and the no-private-read relay argument belong to Philippe
Van Velzen's [correction screen](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18939575)
and kumagi's [PR #2353](https://github.com/CrocSwap/integer-mult-bounds/pull/2353),
head `2704eadf6b5205d4b965e9c6fc6dce28b89783cf`. That audit exhibits a private
descent which violates ordinary support containment and explicitly asks whether
such retained information can beat its bound. This successor supplies a
replacement invariant modulo the root code and checks its additional premises.
The claim is in [Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245).

This is a **written scoped proof with exact finite certificates**, checked by
the author using AI assistance. It is not a simultaneous-storage lower bound,
an attaining construction, a complete paid invoice, a formal proof-assistant
result, or a new supplier or kappa. The selected frontier is unchanged.

## Model and changed premise

Retain the ordered X-source and Y-target frame paths of PR #1972's immutable
4,058-event word, as retained by PR #1991. Sources are 104 independent logical
arrays, never overwritten. Target writes are additive; targets cannot be read,
cleared or rescaled. Every operation has input-independent rational coefficients.
Frames are binary subspaces of F2^9, and a source read is permitted only at
its retained frame. The added correction must contribute `C x`, where
`C = I - G/2`, to the original channel's `G x/2` contribution.

Correction helpers may perform arbitrary equal-frame linear mixing, copies,
clears and relays. Each helper lifetime follows an increasing nested frame
path, with jumps allowed. Its initial source dependence may lie anywhere in
the code K defined below, in addition to arbitrary independent dirty inputs.
Discard/reinitialization starts a new lifetime. We relax dirty restoration and
chronology; restoring dirt or enforcing original event times can only restrict
this model. Lifetimes count even when physical storage is reused.

**New permission:** at any time and any frame, a helper or target can receive
any coefficient row in K, at no cost and without counting a helper entrance.
These are logical source forms with the receiving frame's chart. This grants
more access than read-only use of the actual original private C values: it
removes their dirt, timing and frame restrictions and grants all their linear
combinations. It does not constrain the arbitrary source inputs to lie in K.
The quotient below is on **coefficient rows**, not on the source data.

Other reads of original G/Q/D helpers are excluded unless their source row is
in K. In particular, unfinished captures outside K are not granted. The
original private word is unchanged and read-only: feeding new source
information into it and reusing a descending transport is outside the model.
New descending helpers, cross-frame mixing, target feedback and additional
source-dependent initial information outside K are also outside it. Native
operations outside the logical common-frame model need a separate analysis.

## Exact finite premises

Let R be the 8-by-104 matrix whose columns are the doubled integer P104 roots
in the frozen port order. Set K = row_Q(R). Direct reconstruction gives
`R R^T = 104 I`, `G = R^T R/4`, and `C = I - R^T R/8`.
For a binary frame V, define

```
S(V) = {s : the initial source label q_s lies in V},
U(V) = span_Q {e_s : s in S(V)}.
```

The new premises and the inherited finite geometry are reproduced without
importing any predecessor executable. [RESULT.json](RESULT.json) contains
the actual rows and small witnesses:

| Check | Exact result |
| --- | --- |
| Complete logical/frame replay | 4,058 events, all 280 independent inputs; original G/2 endpoint and all dirty restorations |
| Private source projections | All eight lie in K and together span K |
| Private dirt | The i-th descended C value has exactly the original Q_i dirt, with coefficient 1 |
| Distinct target endpoints H_t | 104 subspaces, each of binary dimension 8 |
| Correction support | supp(C_t) = S(H_t), of size 48, for every t |
| K intersect U(H_t) | Zero for every t, certified by eight outside-root columns with determinant +512 or -512 |
| Direct retained X frame equal to H_t | None, for every t |
| Required labels after granting all earlier Y-frame writes | Binary rank 8, for every t |

The last row uses `N_t = S(H_t) minus E_t`, where E_t contains every source
label lying in any proper earlier frame on Y_t's path. It grants all such
contributions without testing source-read timing. The cardinalities of N_t are
`36:12, 44:24, 45:8, 46:24, 47:24, 48:12` (size: number of targets).
Each target has eight explicit independent labels from N_t. These premises
agree with PR #2353; their numerical values are not new claims.

The **new injectivity certificate** takes eight indices outside S(H_t) whose
root columns are independent. Any row in K vanishing outside S(H_t) must have
zero code coefficients, so K intersect U(H_t) = {0}. For example, target 0's
outside indices are `0,1,3,6,8,14,22,33`, with determinant -512. Rational
elimination selects the witnesses; an integer Bareiss determinant separately
checks each witness.

Here are all private rows. A row with coefficient vector alpha has source
projection `alpha R`; its independent dirt is Q_i. Indices are zero-based.

| i | Descent event | Terminal line | alpha |
| --- | ---: | ---: | --- |
| 0 | 2463 | 243 | (0,0,0,0,0,-1,1,0) |
| 1 | 2472 | 95 | (0,0,0,1,-1,0,0,0) |
| 2 | 2479 | 447 | (0,0,-1,1,0,0,0,0) |
| 3 | 2487 | 502 | (0,0,0,0,-1,-1,0,0) |
| 4 | 2495 | 486 | (0,0,0,0,1,-1,0,0) |
| 5 | 2503 | 127 | (1,-1,-1,1,1,1,1,1)/2 |
| 6 | 2510 | 500 | (0,0,0,0,0,0,-1,-1) |
| 7 | 2518 | 383 | (1,1,1,-1,-1,1,1,1)/2 |

In particular the first private row has coefficient -2 on X8, whose label 408
is outside line 243. This reproduces PR #2353's support-invariant failure;
the row nevertheless lies in K. Its value is checked unchanged throughout
that private lifetime, not only immediately after the descent.

## Proof with the additional information

**Invariant.** At any helper frame V, its source coefficient row lies in
`K + U(V)`. This holds initially. A source X_s read at V adds e_s with q_s in
V because its retained path is increasing from its initial line. Equal-frame
mixing preserves the sum of subspaces, increasing transports preserve U(V)
containment, and every free code input lies in K. Independent dirt has zero
source projection. Thus induction proves the invariant for arbitrary finite
relay networks, including cancellations and arbitrary helper feedback.

**Unique local representative.** Fix a target endpoint H. The finite
injectivity certificate gives `K intersect U(H) = {0}`. Consequently every
row in K + U(H) has a unique U(H) part; the map taking this part is linear.
For V contained in H, a row in K + U(V) has its local part supported on S(V).
Free code inputs have local part zero, even if their ordinary support extends
outside H. This is the step that ordinary support containment cannot provide.

**Two entrances.** Consider target t. Its earlier writes have local parts
supported on E_t. There is no retained source X at frame H_t. A correction
helper born at H_t has initial source dependence only in K and hence local
part zero. New local information at H_t can therefore enter only when a
helper first transports there from a proper subspace V < H_t. Subsequent
mixing, copies and clears at H_t cannot create support absent from those
entrance rows. Helpers cannot leave H_t and return on an increasing path.

If at most one such lifetime entered, all writes to Y_t would belong to
`K + span{e_s : s in E_t} + U(V)` for one proper V (or no V for zero
entrances). Since C_t, the early contribution and U(V) are all in U(H_t),
injectivity forces the code part of the final equality to vanish. Every
nonzero C_t coordinate outside E_t must then lie in S(V): `N_t subset S(V)`.
The eight independent labels in N_t contradict `dim V <= 7`. Hence at least
two helper lifetimes enter every H_t.

**Sum.** Distinct eight-dimensional H_t are incomparable. One increasing
helper lifetime cannot enter two of them. Summing the 104 requirements gives
at least 208 correction-helper lifetimes. This is an all-length argument in
the stated model; finite checking certifies its geometry and source binding,
not an enumeration of all networks.

The bound also applies when the oracle is replaced by actual read-only private
values, because projecting those values onto the independent source inputs
gives only rows in K. Those restrictions supply no source information outside K, so the lower
bound proved in the favorable model transfers to the actual read-only signals.

## Validation and limits

The verifier checks source hashes, every logical event and endpoint, the eight
private rows, all 104 determinant/support certificates and twelve control
groups. Controls reject puncture, transport-rank, private-query, cleanup,
code-membership, dependent-witness and determinant-sign faults. An invertible
code-basis change preserves all 104 determinants. Two countermodels delimit
the proof: granting the outside-code row C_0 itself permits a zero-entrance
write to Y0; a code meeting an endpoint's coordinate space nontrivially lacks
unique local representatives. The original private support escape is a
positive control for the replacement invariant.

This package does not replay native Gaussian phases, construct a correction
network, prove that 208 is attainable, or lower-bound simultaneous physical
registers. An entrance has positive rank under dimension-gap transport pricing,
but this is **not 208 excess ranks**: coverage progress, other operations,
idle children and owners must be accounted for in a complete bill. No recursive
moment, precision/reserve, tape, all-size admission or selected cold replay is
claimed. It does not rule out new descents or changed source/target paths.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -O -B research/p104-private-code-relay-floor/verify.py
python3 -I -O -B research/p104-private-code-relay-floor/test_verify.py
python3 scripts/research_package.py --package research/p104-private-code-relay-floor --check-only
python3 scripts/research_package.py --package research/p104-private-code-relay-floor
```

Expected direct output begins
`PASS_P104_PRIVATE_CODE_RELAY_FLOOR targets=104 private=8 code_rank=8 lifetimes=208 controls=12 no_new_kappa`.
Default replay reads only the package and its two declared JSON inputs, needs
no Git/network and writes nothing. `--out NEW.json` additionally writes a
verified receipt exclusively to a fresh path. A source export preserving the
relative paths supports the direct command; the generic provenance check
separately needs Git history. Six public CLI tests also check a read-only, Git-free export, source/receipt
drift, JSON type and duplicate-key rejection, and exclusive output creation.
Full-field receipt comparison preserves JSON types.

## Open next questions

Can reads of **unfinished original G/Q/D captures outside K** change this
obstruction? That would grant information excluded here. Start by tracing one
such row at an actual target-compatible frame, enlarge the oracle by that row,
and test endpoint injectivity and its chronological availability before
attempting a full word. An information escape alone would still need dirty
restoration, transport and hosting costs. The structured question and stop
test are in [TASK.json](TASK.json).

Can changing a source/target path or allowing a new descent produce a favorable
completed side correction? First identify which N_t rank or quotient-invariant
premise changes, then price the changed operations with the rest of the
construction. Repeating code-valued private reads alone does not evade this
result. The existing retained-path and full-word P104 results remain relevant.

## Credit and provenance

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex (GPT-6 Astra) derived the quotient extension and implemented,
checked and wrote this package. No independent human review is claimed.
New work is Apache-2.0.

Philippe Van Velzen supplied the 208 geometric floor at fork commit
`7dfc7a176d7de4e7eabaf553a0b187c1bd647546`. kumagi / PR #2353 supplied the
precise monotone-relay model, its support proof and private-descent handoff.
Rohan Arun / PR #1972 (`fd82d172f46933fd253c2c6de4bd5eaff5429cfd`) supplied
the frozen word; Chafik Boukhalfa / PR #1991 its retained native realization;
Adam Gall / PR #1940 the schedule; Josie Elliston / PR #1071 the fixture;
Ali Romman / PR #1125 and their retained geometry/compiler lineage are credited.
No predecessor executable or new copy of a frozen package is included.

The pooled correction-space results of Gonzalo Mier / PR #2173 and Gareth
Davidson / PR #2251 concern a different model. This account's PR #2172 and
PR #2190 concern a single-cut price and fixed-room capture order respectively.
The concurrent one-target source-acquisition investigation in Discussion #2245
retains the no-private-read model and addresses attainability, a separate
question. Exact base, source pins, selection, scope and overlap are recorded
in [SOURCES.json](SOURCES.json) and [TASK.json](TASK.json).
