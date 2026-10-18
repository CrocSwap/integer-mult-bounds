# QQ16 coordinate decoding with two retained cuts

**Scoped ordered proof; no supplier or new kappa.** For the unchanged conserved
`F0/B_1_2` pair, 88 ordinary coordinate arrays suffice to recover **all original
pair-0 inputs**, provided the selected fields and completed-X block listed below
are available at the two specified cuts. The inputs may be arbitrary, not just
members of the eight local-axis families tested by
[PR2432](https://github.com/CrocSwap/integer-mult-bounds/pull/2432).

This answers a restricted version of PR2432's next question. It does **not**
show that the final controller exposes these cut values, that retaining them
is free, or that 88 reads are a favorable physical implementation. It supplies
an explicit decoder once those observations are granted.

## Exact observation contract

Write `(x1,y1)=F0(x,y)` and `(x2,y2)=B_1_2(x1,y1)`, with no intervening
modification. Use the retained disjoint selected sets

```text
A = [0,7,20,27,36,46,57,111]
T = [21,37,47,76,81,87,92,110]
U = {0,...,111} \ (A union T)
J = [1,2,3,4,5,6,8,12]
S = U \ J
```

The decoder receives only:

- `x1_A`, `x1_T`, `y1_A`, `y1_T`, retained immediately after complete F0;
- `y2_A` and the completed-X ordinary block `C=x2_U`, immediately after B1;
- `x1_S`, the 88 ordinary arrays read after F0.

An array includes its complete owner and payload coordinates. Reads are
side-effect-free. No original selected input, initial dense ordinary query,
`y2_U`, or former-Y final endpoint is an observation. This is a two-cut
information contract, not a bound of 88 total stored arrays: the selected
records and the complete `C` block are additional granted observations.
Other bank pairs can have arbitrary initial values; they do not participate
in these first two events. No recovery claim for those other pairs is made.

## Ordered proof

All equations are over rational-valued owner/payload arrays. Let `D_(s,p)` be
the actual invertible cover map for port p in chart s. The scalar centre matrix
is R. For a port set V, write

```text
B_(s,V) z = sum_(p in V) r_p D_(s,p) z_p
B_s = B_(s,U)
ell_(s,V) = B_(s,V), for V=A or T
P_(s,V) q = D_(s,V)^(-1) R_V^(-1) q, for V=A or T.
```

Here `D_(s,V)` is block diagonal in ports; its entries are operators, not
commuting scalar coefficients. The actual selected Grams are
`R_A R_A^T = R_T R_T^T = 4I`, so `R_V^(-1)=R_V^T/4`.
The source normalization is `K=R^T/4`; its routed restriction to U is `K_(s,U)`.
These are the conserved maps in the retained
[ordered contract](../joint-query/evidence/JOINT-QUERY-TRANSFER.md), sections
“A variant that preserves both selected pair sums” and
“A forward map with the same conserved inputs.”

### Recover the missing post-F0 ordinary arrays

The forward equations give

```text
f = R_0 x
x1_U = x_U - K_(0,U) f
y1_U = y_U + x1_U
x1_A = P_(0,A) ell_(0,T) x_T
x1_T = P_(0,T) f.
```

The backward U target is an exact subtraction. Its future logger changes
only A, and its source output at A is that logger's output. Consequently,

```text
C = x2_U = x1_U - y1_U = -y_U
q = ell_(2,A) (y2_A - y1_A)
  = B_2 y1_U + ell_(2,T) y1_T
v = q - ell_(2,T) y1_T + B_2 C
  = B_2 x1_U.
```

Every expression on the left is determined by the allowed observations.
Subtract the known coordinates:

```text
w = v - B_(2,S) x1_S
  = R_J D_(2,J) x1_J.
```

The actual rational `R_J` is invertible. The checker derives its inverse
from the pinned R, verifies both inverse orders, and records the matrices in
[RESULT.json](RESULT.json). Thus

```text
x1_J = D_(2,J)^(-1) (R_J^(-1) w).
```

The order is essential: first apply the scalar inverse, then undo each
port's cover map. Moving the different port maps through `R_J^(-1)` is not
valid. This step recovers all of `x1_U`, with no hypothesis on how its
owner or payload values were generated.

### Recover the original inputs

Use the selected sections and the recovered ordinary block:

```text
f   = ell_(0,T) x1_T
t   = P_(0,T) ell_(0,A) x1_A
x_U = x1_U + K_(0,U) f
x_T = t
x_A = P_(0,A) (f - B_0 x_U - ell_(0,T) t)
y_U = -C
y_V = x1_V + y1_V - x_V,                 V=A,T.
```

The first two formulas invert the two selected forward records. The third
inverts its ordinary update. The fourth and fifth recover the selected
components of `R_0 x=f`. Finally, the unchanged selected pair sums recover
the original Y values. Therefore this decoder composed with the stated
observation map is the identity on all 224 original port arrays.

This is an ordered algebraic argument for arbitrary arrays under the inherited
local contract. The finite fixtures below check its source-specific premises
and implementation; they are not the proof of the arbitrary-array statement.

## Evidence and reproduction

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/qq16-coordinate-cut-decoder
```

The registered commands run the direct check and the optimized replay and
source-corruption controls. Direct entry point:

```sh
python3.12 -I -B research/qq16-coordinate-cut-decoder/verify.py
```

Expected status: `PASS_QQ16_COORDINATE_CUT_DECODER`.

The check binds the actual packet, two archive members, the first F0/B1 events,
selected Grams, `K=R^T/4`, the two-sided unread-minor inverse, and 224 registered
port-route/inverse pairs, including their payload-translation inverse equations.
It implements the conserved logical maps directly, rather than executing the
native words or importing a predecessor verifier.

Finite execution covers each of the 224 input-port placements using nonconstant
owner bit-functions and one dense signed/dyadic fixture with every field dirty.
All five incorrect decoders have explicit nonzero residuals: wrong C sign,
missing future-T subtraction, missing old-A subtraction, missing forward K
correction, and reversed route/scalar inverse order. Each of the five external
source-file corruptions is rejected. Checks remain active under `-O`, and the
optimized replay must match the committed result without modifying package files.

The finite functions are constant in payload. The universal proof uses the
inherited invertibility of the full cover maps, not an extrapolation from these
functions. Native kernels, the remaining 17 schedule events, a proof assistant,
and the selected full cold replay were not run.

## Relation to earlier work and limits

- Gareth Davidson's [PR2432](https://github.com/CrocSwap/integer-mult-bounds/pull/2432),
  pinned at `cbede349fc764aa38379aa533befe3215916cfcd`, supplies the unread basis
  and the eight-family threshold. This package adds arbitrary-input sufficiency
  under the explicit two-cut contract. It does not reprove the threshold or
  claim a new unrestricted read minimum.
- commdata2338's [PR2174](https://github.com/CrocSwap/integer-mult-bounds/pull/2174),
  pinned at `f79470a7931f3943360c10d15b428e0e4e479c22`, uses two initial dense
  queries and a post-B1 selected cut to recover pair-0 selected inputs. It
  reconstructs a transient F0 record which this package explicitly retains.
  The observation and retention contracts differ; neither cost nor controller
  superiority follows from this comparison.
- commdata2338's PR2384 exact `Model.forward/backward` implementation, as
  retained by PR2432, was consulted. Its owner-function representation informed
  the finite checker; no predecessor executable is imported or vendored.
- Ali Romman / PR1969 supplies the conserved maps, native contract and cover
  semantics. Adam Gall / PR2093, kyzer1023 / PR2354, PR2389 and its PR2419 audit
  supply the hidden-family and coordinate-read lineage. The retained Rohan Arun,
  Jeremy Kothe, DreamingOfClouds and supplier contributors retain their credit.

No read, storage, chart-map, cleanup, hosting, precision, tape or recursive-child
cost is certified here. In particular, the `B_2 C` read must be legal at the
completed-X type; an algebraic formula alone does not establish that access.
The selected frontier and frozen predecessors are unchanged.

Base and exact input pins are in [SOURCES.json](SOURCES.json); scope and overlap
are in [TASK.json](TASK.json). Coordination:
[Discussion 2424](https://github.com/CrocSwap/integer-mult-bounds/discussions/2424#discussioncomment-18946004).
New work is Apache-2.0, submitted by `starship-s` with substantial assistance from
Hermes Agent (`gpt-6-astra-900k`: derivation and proof) and Codex
(`gpt-6-astra`, max effort: implementation and review). No independent human or
proof-assistant verification is claimed.

## Open next questions

1. **Can an actual controller retain or reconstruct these two-cut records?**
   This is necessary to turn the information lemma into a usable decoder.
   First trace `x1_A/T`, `y1_A/T`, `y2_A` and `C` through the remaining schedule,
   with their native endpoint types. The blocker is legal retention and access,
   not the local inverse.
2. **Does a fully charged implementation have a favorable budget?**
   First price the 88 reads, `B_2 C`, scalar minor inversion, per-port chart
   maps, storage and cleanup together. No physical implementation or favorable
   complete bill has been supplied; stop this route if even its optimistic bill
   misses the declared supplier target.
