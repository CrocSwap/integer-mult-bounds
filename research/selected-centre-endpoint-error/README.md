# Centre errors remain visible at the complete projected endpoint

In the selected 144-call **common-frame scalar projection**, the linear map
from the 1,152 centre-transport output errors to the final 14,336 ordinary-owner
errors is injective. Every scalar instruction, all 144 paired bridges, and all
16 signed terminal exchanges are included. Consequently, nonzero centre errors
cannot compensate each other at the complete final endpoint in this model.

This answers a bounded version of PR2199's final-output-quotient handoff. Its
calls-only source-history rank did not imply a final-output bound because scatter
panels overlap and later calls can change them. The new calculation directly
propagates independently injected errors through the remaining program. It does
not identify history rank with output rank or infer a native recursive tariff.

## Model and result

The local 24,767-event words, selected owner maps and execution schedule are
unchanged and source-pinned. As in PR1918/PR2199, frame climbs, frame/endpoint and
residual adapters are replaced by identity. Here idle factors, padding and address
translations are explicitly identity as well. This is an algebraic projection;
it is not a specialization asserted to preserve the native operator rank.

At each literal rank-eight `center` event, add an independent scalar e_(call,k)
to that private centre **after** its projected transport. Preserve every later
instruction, including all gathers, scatters, cleanup, helper restoration and
private clears. Start the two compared runs with identical arbitrary ordinary
inputs. The vector e has 144*8=1,152 coordinates. Let R be the resulting map from
e to the final ordinary-owner difference.

The independently reproduced exact results are:

| Quantity | Value |
|---|---:|
| Complete ordinary endpoint with e=0 | Identity on 14,336 inputs |
| Centre sites | 1,152 |
| rank_Q R | 1,152 |
| rank R modulo 2^31-1, different pivot order | 1,152 |
| Explicit square output minor | 1,152 selected owners |
| Complete bridge-aware source-history rank modulo 2^31-1 | 1,152 |

The last row is context, not the argument for the endpoint result. The receipt
records every pivot output owner, a canonical digest of the complete response,
the local response support and the complete chronological call list. Every
response coefficient is recomputed on replay.

A forward centre perturbation has 112 potentially affected ordinary roles at
local exit. A backward perturbation has **227**, including helper roles. Thus a
calculation that keeps only the immediate scatter panel silently discards part
of the restoration obligation. Hosted helpers remain the actual shared physical
families; they are never cloned or reset between calls.

## Why the computation proves the scoped assertion

All retained operations are linear over Q. A complete local call therefore has
an ordinary endpoint matrix A and an additive error-response matrix B. The source
replay checks A is the declared forward or backward transvection on all 704
ordinary inputs. The new local interpreter computes B by injecting eight formal
basis errors at the literal transport events and executing the complete word.
Private centre rows must clear for every error coordinate.

The chronological recurrence is

    state_next = A state + B e_call

at local calls. Each bridge executes X_dst += c X_src and Y_src -= c Y_dst on
every port of its replica. The signed terminal exchange is (X,Y) -> (Y,-X).
The owner numbering of these operations is checked against every call's first
224 data roles. Call hashes bind each invocation to its actual oriented word.
Composing these linear maps gives final difference R e. This recurrence remains
valid when individual errors depend on earlier values: after evaluating a run,
their realized values still form the vector e in the same identity.

R has 1,152 columns. Independent elimination modulo the prime 2^31-1, with the
opposite pivot order, verifies full column rank, including the explicitly listed
square output minor. All denominators are invertible modulo that prime; a
nonzero reduced determinant certifies a nonzero rational determinant. Therefore
R is injective over Q and over any characteristic-zero extension, including C.
The separate rational elimination agrees. Hence R e=0 if and only if e=0.

This is an error-cancellation statement for the fixed internal schedule. It
neither lower-bounds the cost of computing the exact centres nor excludes
redesigning the word, additional observations, different final readouts, changed
helper contracts, or physically nonidentity frame effects. In particular it
cannot be promoted to a 1,152-scalar transcript lower bound for an arbitrary
feedback implementation merely by citing the history rank.

## Reproduction and independent checks

```
python3.12 -I -O -B research/selected-centre-endpoint-error/endpoint.py
python3.12 -B scripts/research_package.py --package research/selected-centre-endpoint-error
```

Default replay is read-only. `--out NEW.json` exclusively creates a regenerated
receipt. No third-party dependency is needed. Set TEMP/TMP to a writable location
for export tests on a restricted Windows host.

The primary path composes exact sparse local endpoint/error maps. A separate
numeric interpreter executes every scalar instruction of every actual local
word on two complete error vectors, rather than using those maps or endpoint
formulas. It independently executes bridges and signed terminals and compares
every final owner. One vector is dense; the other injects a single backward-call
centre error. Private zero at each local exit is checked in both paths.

Controls omit a paired bridge (the no-error endpoint ceases to be identity),
duplicate two error columns (rank drops to 1,151), and require a nonzero single
error to remain observable. Export tests check Git-free unchanged replay,
source-pin rejection before imported code, wrong-typed receipt rejection and
existing-output refusal. These tests support the finite claim; there is no
proof-assistant or complete supplier replay claim.

## Sources and attribution

Sagar Thakrar (`thakrarsagar`) supplied PR2199, exact head
`30ec048eedcaca970f94bbec0fdd3c52eacf9fdc`, including the local scalar replay and
calls-only census. Its unchanged verifier is retained under `vendor/`, with its
original authorship, AI disclosure and Apache-2.0 notice. It supplies the local
endpoint and rational elimination routines, not the new final-error recurrence,
modular checker or literal numeric replay. Adam Gall's PR1918 established the
composed scalar source-map setting. PR2048 by `commdata2338` proves a separate
native two-forward-call lift; PR2391 by Aaron Wang / `navinor` gives a native
counterexample to the D-only quarter-factor. Neither is reproduced or superseded.

The selected PR1094 archive, complete members, owner maps and local program hashes
are checked before use. Rohan Arun, Jeremy Kothe, Hao Yan, icekylinx and the
retained construction/compiler contributors keep their attribution. Main base
is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected/frozen files are unchanged.
Prepared by ywz65 with Codex assistance, Apache-2.0. No new supplier or kappa.

## Open next questions

* Does this exact endpoint-error injectivity survive the native frame/owner
  action? First transport the displayed output minor through actual native
  continuations, idle factors and cover charts. PR2391 shows that scalar
  identities cannot simply be assumed to lift; this is the main blocker.
* Which deliberately weakened final readout admits a nonzero error kernel, and
  does that readout still satisfy a useful data/helper contract? Start with a
  precisely named subset or quotient of ordinary outputs. A smaller readout is
  not automatically a legal restoration contract or a cost improvement.
