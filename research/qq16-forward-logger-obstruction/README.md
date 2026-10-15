# Changing the first QQ16 A logger is insufficient

**Scoped negative result; no new supplier or κ.** Changing the first forward
QQ16 source encoder cannot restore the initial selected inputs if it preserves
the full-query T output, the ordinary response and selected pair sums, while
B1, the ordinary tail and the allowed final observations stay fixed. The A
logger may change arbitrarily, including reads of ordinary inputs within F0.
The obstruction survives even if the entire changed encoder is granted for free.

This is a changed-first-forward theorem, not a repetition of the fixed-F0
witness and not an obstruction to every changed first pair. The proof below
quantifies over every invertible homogeneous source encoder with the displayed
outputs; the finite fixtures do not establish that quantifier.

## Exact interface and predecessors

Ali Romman's [PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969),
head `a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`, supplies the
[ordered QQ16 maps](../joint-query/evidence/JOINT-QUERY-TRANSFER.md), native
local words and the [fixed-pair witness](../joint-query/evidence/QQ16-SELECTED-WITNESS.md).
Its [independent observation review](../joint-query/evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.md)
proves eight missing B2 directions for fixed F0/B1. Those results are credited
inputs, not new claims here.

Retain its disjoint sets

```
A = [0,7,20,27,36,46,57,111]
T = [21,37,47,76,81,87,92,110]
U = {0,...,111} minus (A union T).
```

Use the actual routed centre queries R_s, their ordinary restrictions B_s,
and the two-sided selected sections P_(s,A), P_(s,T). For the first source
write z=X_U, a=ell_(0,A)X, c=ell_(0,T)X, and f=B0 z+a+c.
Let **G be any invertible homogeneous linear source map** satisfying

```
X'_U = z - K_(0,U) f,
X'_T = P_(0,T) f.
```

There is no further restriction on X'_A. In particular, G may read ordinary
inputs to compute its A output. Complete the pair by

```
Y'_U = Y_U + X'_U,
Y'_S = X_S + Y_S - X'_S,       S=A union T.
```

G acts on X alone. No input-dependent transcript, extra output or unrestored
helper is retained. Its full pair extension is invertible: invert G, then use
the last two equations to recover Y. Arbitrary initial Y is allowed, not cleared.

After this first call, retain **the original B_1_2**, the original ordinary
bank schedule and its terminal types. Later homogeneous selected-only linear
controls may change arbitrarily but may not read ordinary fields. Allowed
observations are all selected endpoints, all completed-X descendants and all
five forward query histories. The final named X0 ordinary field has the old-Y
native type, so it is not one of the completed-X descendants. This distinction
is essential, exactly as in the predecessor witness.

## 1. An actual B0/B1 witness

Let * transpose the real coefficient matrix and invert the cover route.
The source columns r_p satisfy

```
||r_p||^2 = 4,        sum_(p in U) r_p r_p^T = 48 I.
```

Stage zero has identity routes. The 96 actual stage-one ordinary routes g_p
are distinct involutions. Consequently B0 B0*=B1 B1*=48I. For e_k supported
at the identity cover element, define

```
h_k = (48 I - B1* B1) B0* e_k.                  (1)
```

Then B1 h_k=0. Since g_p^-1 g_q is identity exactly when p=q, the identity
coefficient of B0 B1* B1 B0* is

```
sum_p (r_p r_p^T)^2 = 4 sum_p r_p r_p^T = 192 I.
```

Thus the identity coefficient of B0 h_k is

```
48^2 I - 192 I = 2112 I.                       (2)
```

The eight h_k are independent and have integer coefficients. The checker
reconstructs R from the selected scalar prefix, derives the 112 stage-one
routes from the actual phase recipes, constructs every group-ring coefficient
of all eight h_k, and checks the **entire** B1 h=0, not only its identity term.
The 17-coordinate route representation is faithful: stage one acts on the nine
local and eight first-stage coordinates and fixes the other 56 coordinates.
It is not an abelian or cover-invariant quotient.

These are valid witnesses at every positive tensor size: take the fields
constant in payload coordinates, while leaving cover values arbitrary. Payload
translations act trivially on this subspace. Exact logical frame conventions
and their native meaning remain inherited from the predecessor, not removed by
an approximation. No division by 3, 11 or 13 is used in (1).

## 2. Pull back the erased state through any changed logger

Fix one h=h_k and prescribe the state immediately after G:

```
X'_U=Y'_U=h,
X'_A=P_(2,A) B2 h,       Y'_A=-P_(2,A) B2 h,
X'_T=Y'_T=0.
```

All other banks are zero. Since G is surjective, this X' has a unique original
source X. The conserved sums determine Y_S=-X_S, and Y_U=0. The two fixed
source output equations imply, in order,

```
f=0,       z=h,       a+c=-B0 h.                (3)
```

Equation (2) makes (3) nonzero. Hence **at least one of the original selected
A or T inputs is nonzero**, regardless of what G writes into A. The proof does
not claim that the original T alone must be nonzero for every changed logger.

Now run the unchanged B_1_2. Its future query is
`q2=B2 h+ell_(2,A)Y'_A=0`; the future logger E2 makes its A source zero.
Its T source and old selected-X driver are zero. The remaining current query
is `b1=B1 h=0`. Substitution into the credited ordered backward equations
therefore leaves exactly

```
Y_0,U=h; all other ordinary and selected fields zero.
```

This is the same post-B1 state as the predecessor's witness, although the
preimage and its missing query are different. The inherited ordinary tail
therefore gives zero selected observations, zero completed-X descendants and
zero f2,f4,f6,f8; f0=0 was already established. Its only terminal ordinary
value is h in old-Y-typed X0. Homogeneous selected-only operations preserve
the all-zero selected state. The zero initial input has identical allowed
observations but different required selected data. No decoder from those
observations alone, even a nonlinear decoder, can restore both inputs.

**This is the new implication:** an arbitrary rewrite of the A logger cannot
help while the two other source outputs and the downstream interface are fixed.
The old proof with its fixed preimage did not itself quantify over these G.

### Ordered description of the whole linear logger family

In normalized coordinates write the remaining output as
`d=alpha a+beta c+L z`. Here alpha and beta are arbitrary query operators and
L may read every ordinary source coordinate. Put D=beta-alpha. If D has a
two-sided inverse, the exact source inverse is

```
z = w + K_(0,U) f,
sigma = f - B0 z,
c = D^-1 (d - alpha sigma - L z),
a = sigma - c.
```

Factors are not commuted. Eliminating z and sigma reduces source invertibility
to invertibility of D on the query space. This also shows the admitted family
is nonempty and substantially larger than the original logger `d=c`.
For the erased state, every member still has `a+c=-B0h`. The checker includes
all 500 invertible scalar loggers over F5 with two ordinary coordinates and a
rational two-coordinate example with noncommuting alpha and beta. These are
regressions of the ordered calculation, not a substitute for the proof.

## Complete favorable accounting and stop decision

The credited original local pair has native rank mass **11076**, real scalar
primitive bound **426196**, **528** added full-cover maps and **64** native
wrapper maps. Those local counts are read from the pinned native invoice;
map counts are not physical address costs. They are context, not a lower bound
on a resynthesized G and not a whole-controller bill.

Before synthesis, grant the changed G **zero total cost**, and grant zero costs
for every extra read internal to it, source/target adapters, owner/helper hosting,
precision, routing and restoration work. Keep the required endpoint and
observation contract. Even this favorable completion is impossible by (3).
Adding nonnegative charges cannot fix its information loss. Accordingly no
moment root, child profile improvement, native synthesis or supplier claim is
made. A separately retained observation changes the interface and is not
silently assigned zero cost here.

## Evidence and reproduction

Base `564148b82ae9df72163f22106f15e73efca8aff2`, priority revision 4;
selection seed `e86c305e59ee045687c6d1ab7d3956e0`, recursive-interfaces,
`joint-query-controller`. [SELECTION.json](SELECTION.json) is the unchanged
one-shot draw. [TASK.json](TASK.json) records the hypothesis, pre-computation
screen, overlap scope and next questions. [SOURCES.json](SOURCES.json) pins
live inputs and historical provenance. No predecessor executable is imported
and no source archive is copied or changed.
The submission checkpoint read main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`: guidance changed, but priority
revision, catalogue, selected record and scientific inputs did not. The original
scientific base and source pins are intentionally retained.

From the repository root, standard-library CPython 3.12:

```sh
uv run --python 3.12 --no-project python -I -B research/qq16-forward-logger-obstruction/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/qq16-forward-logger-obstruction
```

The registered replay also runs under `-O`; all checks use explicit exceptions.
It compares the complete canonical JSON result with [RESULT.json](RESULT.json).
To regenerate evidence without overwriting the committed receipt, use
`verify.py --emit /tmp/qq16-forward-logger-result.json` with a fresh path.

Observed on CPython 3.12.12: `PASS_QQ16_FORWARD_LOGGER_OBSTRUCTION` in the
scientific generation and both registered modes, followed by
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
The receipt records 4320 nonzero ordinary-field/group terms, complete B1h=0,
eight independent missing directions, 500 changed loggers, 8000 dirty pair-basis
inverse checks and the noncommuting rational fixture. An initial registration
attempt rejected a combined next-questions heading; the corrected heading passed.

Semantic controls remove the projector term, change 48 to 47, collapse all
routes, corrupt a query column and omit the first cancelling ordinary bridge.
An extra B0 observation detects the witness, delimiting the result. The finite
logger check tests both inverse orders on every dirty pair-state basis column.
The tail replay is only the restricted h-coefficient trajectory from the pinned
witness and independent review receipts; **it is not a replay of the absent
full controller program or the native supplier**.

## Overlap and limits

The final shared overlap snapshot covers 353 open PRs and 738 discussion records,
with complete pagination at 2026-10-14 19:00:33/19:02:09 UTC. The targeted offline
search at 19:03:45 also covered 1538 local records (including this package).
Targeted reading included merged PR1969, the exact local sources and
[PR2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079) at
`49df8190b158e3028e702b2c6b798117006f7249` (Cinna Davis), following
[discussion2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074).
That concurrent work separates the original eight-direction witness using a
separately retained pre-F0 B2 observation, and explicitly leaves full-controller
injectivity open. This result instead changes the first A logger without adding
an observation.
Cached searches and absence of a matching title are not novelty proofs.

This does not exclude changing B1, changing the full-query T output or ordinary
response, retaining an extra transcript, reading ordinary old-Y output later,
nonhomogeneous control, changing selected conservation or changing the ordinary
schedule. No physical lower bound, all-size supplier admission, stronger κ,
complete cold replay or formal proof-assistant verification is claimed.

## Open next questions

- **Change an actually necessary premise.** Specify one different first T
  record or ordinary response and apply the same post-F0 state first. A legal
  native realization and complete paid bill remain the blockers.
- **Price a separately retained observation.** Test restoration of both initial
  selected inputs, not only one old B2 witness. Read access, storage lifetime,
  native types, restoration and recursive pricing remain obligations.

## Attribution

Prepared for Adam Gall with substantial OpenAI Codex assistance. New material
uses Apache-2.0. Ali Romman and the credited centre-encoding contributors supply
QQ16, its source loader/reconstruction method, native routes and the original
witness and review. The gauge44/t16 geometry, compiler and selected-supplier
lineage retain their full [source notices](../joint-query/NOTICE.md). The new
contribution is the changed-logger pullback theorem, B0/B1 integer witness and
its checker, not those inherited constructions. No independent human or formal
kernel review is asserted.
