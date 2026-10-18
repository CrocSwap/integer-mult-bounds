# P104 arrival helpers can have rank steps 1,7,1

A finite counterexample to the arrival-shape premise in Philippe Van Velzen's
[relay-v2 cost screen](https://github.com/philippeVV/integer-mult-bounds/blob/fac9e821d31bc199b49e8ed463074a50d1264311/research/p104-correction-screen/relay-v2/README.md).
The published argument excludes `{1,1,7}` for arrival lifetimes and applies
`{1,1,1,6}` to obtain a uniform 463-lifetime limit. The excluded shape is legal
in the stated X-only, monotone-helper model, including in a complete correction.
This result corrects that premise. It does **not** disprove the numerical limit
by constructing a feasible design with more than 463 helpers.

The new construction is deliberately expensive and fails the fixed-template
rank budget. No supplier, improved moment or new kappa is claimed. The
predecessor's 1,031-lifetime construction and its unfavorable measured invoice
are unaffected.

## One literal carrier

Write `C = I-G/2`. For a nonzero entry `c=C[t,s]`, let `q_s` be the source's
initial line and `H_t` the target's final eight-dimensional frame. Direct
reconstruction of the pinned root fixture and original witness establishes
`q_s` is contained in `H_t` for all 4,992 nonzero entries. Sources end in FULL;
targets start in ZERO. A fresh helper starts with an arbitrary logical value `d`.

| Cut | Operation | Helper logical value | Paid rank |
|---|---|---|---|
| 0 | `Y_t -= h` in ZERO | `d` | 0 |
| 0 | Move `h` from ZERO to `q_s` | `d` | 1 |
| 0 | `h += c X_s` in `q_s` | `d+c X_s` | 0 |
| 0 | Move `h` from `q_s` to `H_t` | `d+c X_s` | 7 |
| 4058 | `Y_t += h` in `H_t` | `d+c X_s` | 0 |
| 4058 | Move `h` from `H_t` to FULL | `d+c X_s` | 1 |
| 4058 | `h -= c X_s` in FULL | `d` | 0 |

The line-to-`H_t` move occurs after the source read and before the retained
core. The core changes the original source frames to FULL while this
new helper waits at `H_t`. Both target writes and both source reads have common
frames. The target gains `c X_s`; the helper returns its original logical dirt
in FULL. Its dimensions are `0 -> 1 -> 8 -> 9`, with rank histogram `{1:2,7:1}`.
The need to visit `H_t` and FULL does not force a fourth positive step.
The per-call profile price depends on the histogram, so the order `1,7,1`
has the same local price as the multiset `{1,1,7}`.

The first concrete pair is `t=0,s=2,c=-1/2`, with source basis `[228]` and target
basis `[243,499,23,32,112,3,4,1]`. All values here are logical coefficients;
compressed binary labels are used only for subspace membership, never as
ordinary Euclidean pairing coordinates.

## Complete arbitrary-input check

Use an independent helper for every nonzero entry of `C`. Batch the initial
four operations of every carrier, run the unchanged 4,058-event PR1972 core,
then batch the final three operations. The replay checks common frames at the
actual execution time, every nested transport and its rank, and every endpoint.

The verifier reconstructs the E8 root lines from doubled integer coordinates
and removes the pinned P104 puncture. It first independently verifies the core
map `Y += G X/2` and restoration of its 72 dirty helpers. It then executes the
combined word over all 5,272 independent original and new dirty inputs. Every
source and helper is restored logically; each target ends at `Y_t + X_t`.
Sparse exact row equality checks absent coefficients as zero as well.

Measured receipt:

- 4,992 correction carriers, all with steps `1,7,1`;
- 39,002 combined events, including 22,592 scalar additions;
- added profile `9984 H1 + 4992 H7`, rank mass 44,928;
- original eight owned private COPY lifetimes retained unchanged.

The original core's owned private copy/discard contract remains an assumption
of its interpretation. The new carriers use no private copy, initialization to
zero, discard, original-helper reads or target reads.

## What price limit survives

Under the **conditional** 832-family, nine-stage, width-73 template with centre
charge 56, paid mass per call is

`72*(832/9)+56 = 6712`.

The retained channel already costs 2,368 rank units. Thus at most 4,344 remain.
If each new monotone helper starts in ZERO and ends in FULL, its transport rank
mass is nine. Any construction admitted by this unchanged coverage budget must
therefore satisfy

`9L <= 4344`, hence **`L <= 482`**.

This is a necessary mass condition only. It gives no positive-saving moment,
chronological owner allocation or feasible design near 482. In particular,
substituting a uniform four-step profile for every helper requires a separate
lemma. This package does not reprice PR2559's pending target or prove that its
numerical 463 limit is false. It shows that the cited arrival argument does
not establish that universal limit.

The counterexample uses 4,992 helpers and 44,928 added ranks, so it is far above
the 4,344-rank allowance. Its purpose is to test the forbidden shape, not to
compete with relay-v2. No search or local optimum is claimed.

## Reproduce

Standard-library Python 3.12 or later, read-only, no network or predecessor
executable imports:

```sh
python3.12 -I -O -Werror -B research/p104-arrival-shape-audit/verify.py
python3.12 -Werror -B research/p104-arrival-shape-audit/test_verify.py
python3.12 -Werror -B scripts/research_package.py --package research/p104-arrival-shape-audit
```

`--out PATH` writes the receipt exclusively to a new file. `EXPECTED.json`
records the complete receipt. `SOURCES.json` pins the original geometry, core
word and audited claim; the claim README is retained byte for byte. `TASK.json`
records the bounded question, overlap coverage and verification environment.
The canonical [Discussion claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18952536)
tracks this investigation.

Controls reject lost initial dirty compensation, altered coefficients, lost
delivery or cleanup, wrong transport frame/rank, an early cleanup, capacity
exhaustion and source drift. Equivalent binary bases and optimized replay pass.

The construction also passes the predecessor's unmodified
[relay checker](https://github.com/philippeVV/integer-mult-bounds/blob/fac9e821d31bc199b49e8ed463074a50d1264311/research/p104-correction-screen/relay-construction/check_p104_relay_construction.py).
For this additional check, export the correction using
`verify.py --relay-word /tmp/p104-arrival-word.json`, download that pinned
checker, then run it with the repository root and exported word as arguments.
Its SHA256 is
`b808e70129fc2c01fbead974c770e0a39245f3a3968c53bcd1f49fb1972e865d`.
The observed output is
`PASS_P104_RELAY_CONSTRUCTION lifetimes=4992 per_target=48.00 line_floor=208 idle_cap=482`.
That checker deliberately expects this construction to exceed 482; its PASS
is an endpoint/grammar check, not budget admission. This optional external
corroboration is separate from the self-contained registered replay.

## Verification limits and implementation

This is an exact logical scalar/frame grammar result. Native Gaussian recipes,
phases, physical precision, scalar/address lowering, global hosting/idle pricing,
all-size admission and the selected cold replay are unrun. No human or formal
proof-kernel review is claimed.

The Python verifier uses bounded nonrecursive loops: at most 39,002 events,
5,272 persistent registers plus one owned private register, nine frame pivots
and 104 squared root pairs. Fractions and sparse dictionaries allocate during
replay, a managed-runtime deviation from fixed-allocation execution. Their keys
come only from the 5,272 independent inputs and their number of rows is bounded
by the register capacity. Exact arithmetic avoids rounding; the pinned grammar
and finite word bound the calculation. A streaming implementation would be
needed before accepting unbounded user programs. No such input is accepted.

## Open next questions

Can a valid stronger relay price bound replace the unsupported uniform profile?
A feasible first step is to classify useful helper lifetimes by their actual
contact dimensions and derive a joint profile constraint, then price the whole
histogram. The blocker is proving that constraint for arbitrary same-frame
mixing, retained dirt and chronological reuse. The current counterexample must
remain a positive case. This matters because an unjustified per-helper penalty
can prematurely exclude a route that is still open.

Alternatively, reduce relay-v2's actual merge loss and replay its complete bill.
The present result supplies no cheaper complete relay network. Structured next
questions and exclusions are in `TASK.json`.

## Credit

Philippe Van Velzen supplies relay-v2, its cost question and the predecessor
checker. This contribution audits one pricing implication, not that construction.
Retain the X-only relay model of kumagi / PR2353, Gonzalo Mier / PR2393 and Ross
Richardson / PR2445. Rohan Arun / PR1972 supplies the original scalar/frame
channel, Chafik Boukhalfa / PR1991 its native binding, Adam Gall / PR1940 the
schedule, and Josie Elliston / PR1071 and Ali Romman / PR1125 the fixture lineage.
Nick Petalas / PR2594 independently audited relay-v2's endpoints and logical
growth; this package addresses a different claim. Existing notices and frozen
source inputs are unchanged. Apache-2.0.
