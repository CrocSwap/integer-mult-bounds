# The QQ16 shear still loses selected inputs with a dense old-chart record

Grant the paired A-to-T shear between F0 and B1 and retain the complete
ordinary old-chart query `q0 = B0 X_U^initial`. These changes still do not
restore all original selected inputs. For a finite regular cover of size
`N`, at least `ceil(32N/7)` dimensions of selected-input differences remain
invisible under the observation contract below.

This is a scoped linear-algebra obstruction, not a new supplier or κ.
It answers the dense-observation handoff in [PR #2326](https://github.com/CrocSwap/integer-mult-bounds/pull/2326).
It does not claim that every dense query fails. The new step is a graph
intersection for the changed first pair; the three-query rank estimate
and ordinary-tail argument are credited predecessor results.

## Exact scope

Use the conserved F0 and B_1_2 maps from
[the retained QQ16 package](../joint-query/README.md), with its A, T and U
port sets, selected sections, owner action and ordinary tail. All arrays
are arbitrary over the rationals. Restrict the counterexamples to fields
constant in payload coordinates, but allow independent cover-owner values.
This preserves the actual owner action; it does not replace routes by a
nonfaithful quotient.

After the complete F0, insert the logical paired shear from
[PR #2216](https://github.com/CrocSwap/integer-mult-bounds/pull/2216):

```text
X_T <- X_T + C X_A
Y_T <- Y_T - C X_A.
```

Here `C` is the identity pairing from the eight ordered A fields to the
eight ordered T fields. No ordinary field changes. The proof also works
for any fixed invertible rational-linear `C` between those selected spaces.

The observations are:

- `q0 = B0 X_U^initial`, retained without loss;
- every selected output immediately after B1 and at all later cuts;
- all five forward-query histories;
- all final completed-X descendants under the retained endpoint typing.

A separately retained transient F0 A/T output, a later ordinary read and
the final former-Y hole are **not** observations. Later homogeneous
selected-only linear controls are allowed. The observation record does
not feed back into ordinary state. The final decoder may be nonlinear:
two identical observation tuples still cannot have different answers.

Grant the shear, read, storage, native frame conversions, address work,
cleanup, hosting and precision zero cost. Recovery fails even in this
favorable relaxation, so no construction or moment claim is made. In
particular, this does not adopt PR #2216's bare-scalar native pricing.

## Ordered kernel construction

Write `B_s = R_s iota_U` and `K_1 = K_(1,U)`, so `B1 K_1 = 12 I`.
Let `P0A = P_(0,A)`, `P0T = P_(0,T)` and `P1T = P_(1,T)`.
Every selected section and its selected query are two-sided inverses.
Define the following ordered maps from query coordinates:

```text
L = ell_(1,T) C P0A
M = (ell_(2,A) + ell_(2,T) C) P0A.
```

`L` is invertible. Take a query vector `c` and an ordinary vector `w`
satisfying

```text
B0 w = 0,
B1 w = -11 L c,
B2 w = M c.                                           (1)
```

Only pair 0 is initially nonzero:

```text
X_U = w,       Y_U = 0,
X_A = -P0A c,  Y_A = P0A c,
X_T = P0T c,   Y_T = -P0T c.                           (2)
```

The other pairs and borrowed helpers may be set to zero: this is an
allowed subspace of an arbitrary-dirty-input contract. Both selected pair
sums vanish. The initial selected defect is injective in `c`.

The F0 query is `f0 = B0 w - c + c = 0`. Its exact output is

```text
X_U = Y_U = w,
X_A = P0A c,  Y_A = -P0A c,
X_T = Y_T = 0.
```

After the shear, `X_T = C P0A c` and `Y_T = -C P0A c`.
Set `a = L c`. The future query at B1 is

```text
q2 = R2 Y = B2 w - M c = 0.
```

The systematic logger `E2` therefore gives `u_A = P_(2,A) q2 = 0`,
`u_U = w` and `u_T = -C P0A c = -P1T a`. Consequently

```text
b = R1 u = B1 w - a = -12a.
```

The conserved backward equations from the
[ordered QQ16 proof](../joint-query/evidence/JOINT-QUERY-TRANSFER.md) give

```text
Y'_U = w + K_1 a = h,
Y'_A = 0,
Y'_T = u_T - P1T b - 11 P1T a = 0,
X'_U = w - w = 0,
X'_A = X'_T = 0.                                     (3)
```

No operators have been commuted. The output (3) is exactly the
[retained witness's post-B1 form](../joint-query/evidence/QQ16-SELECTED-WITNESS.md),
with an arbitrary ordinary value `h`. That tail argument does not require
`B1 h = 0`: the first positive bridge puts `-h` in Y1, F2 has zero X
source, and the negative bridge removes `-h` before B3. Later active
pairs are zero. The terminal moves `h` to named final X0 with the
former-Y native type. Every selected output, forward history and
completed-X descendant is zero. Homogeneous selected-only controls keep
the selected state zero.

Finally `q0 = B0 w = 0`. Thus every solution of (1) gives the same
allowed observations as the zero input, despite the selected defect (2).

## Why nonzero solutions exist on the actual cover

Let `S = [B0; B1; B2]`, a map into a `24N`-dimensional query space,
and let

```text
H = { (0, -11 L c, M c) : c in Q^(8N) }.
```

Because `L` is invertible, `dim H = 8N`, and every vector of
`im S intersect H` determines a unique `c`. The elementary intersection
inequality gives

```text
dim(im S intersect H) >= rank(S) + 8N - 24N
                         = rank(S) - 16N.             (4)
```

Every vector in this intersection has a rational preimage `w`, so (4)
counts actual invisible selected defects, not just unconstrained query
values. The zero element is the only one with `c = 0`.

The second-moment argument in [PR #2104](https://github.com/CrocSwap/integer-mult-bounds/pull/2104),
rebound to the retained packet by [PR #2153](https://github.com/CrocSwap/integer-mult-bounds/pull/2153),
gives `rank(S) >= 144N/7`. Its finite premises are rechecked here:

```text
sum_(p in U) r_p r_p^T = 48 I_8,   ||r_p||^2 = 4,
R_A R_A^T = R_T R_T^T = 4 I_8,
g_(s,p) g_(t,p)^-1 distinct for all 96 p, each s<t in {0,1,2}.
```

A nonidentity regular permutation has trace zero. Hence, for `K=S* S`,

```text
tr K = 1152 N,
tr K^2 = 64512 N,
rank S >= (tr K)^2 / tr K^2 = 144N/7.
```

Combining this with (4) proves the stated `ceil(32N/7)` lower bound.
The dimension is across the full owner array, not a per-owner native
rank tariff. Clearing rational denominators and scaling yields dyadic
inputs of arbitrarily small nonzero magnitude. This proves existence;
it does not give a compact actual-cover vector or a precision bound.

## Reproduce and verification boundary

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/qq16-shear-old-chart-kernel
python3.12 -I -O -B research/qq16-shear-old-chart-kernel/verify.py
```

The checker binds the packet and proof inputs through [SOURCES.json](SOURCES.json),
checks the actual three-chart route distinctions and Gram identities,
and exercises (1)--(3) with exact rational noncommuting selected-section
fixtures. It also checks the retained formal-h tail and deliberate
failures. Finite fixtures do not prove the quantified intersection
argument; the proof is written above.

The registered normal and optimized replays passed on CPython 3.12.13:
three sets of 96 relative routes, four rational basis fixtures, 17 tail
events and six rejection-control groups. A Git-free relocated optimized
replay preserved all 11 copied files; corrupting a copied source was
rejected by its digest check. Separate Astra/max agent reviews found no
blocking mathematical/spec or verifier-quality issue. These are agent
reviews, not independent human review.

No pending executable is imported. The packet's reviewed scalar/native
binding is inherited, not cold-replayed. There is no full supplier replay,
proof-assistant check or independent human review. The stronger later
moment estimates are not needed or reverified here. The selected record
and all frozen sources remain unchanged.

## Open next questions

Can a changed first-pair interface make a *different* eight-coordinate
dense record sufficient? This matters because detecting a known witness
is weaker than closing the complete kernel. Start by writing its ordered
analogue of (1) and intersecting its query graph with `im S`. Actual
native access, retention and a favorable complete bill remain blockers
even if that algebra succeeds.

Can one recover the privileged post-B1 selected cut used by
[PR #2174](https://github.com/CrocSwap/integer-mult-bounds/pull/2174)
from legal final records? Its two-record theorem is a different positive
contract. The first step is an ordered reconstruction of that cut; the
current obstruction neither supplies nor contradicts it.

## Provenance and credit

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The accepted chooser nonce is `7dcbcbed93c608a2c89c3e8330a31a30`;
`joint-query-controller` is a refined scope on the recursive-interfaces track.
[Task metadata](TASK.json) records the claim, overlap and stopping rule.

- Ali Romman, PR #1969 and the [retained notices](../joint-query/NOTICE.md):
  local maps, selected sections, owner action and ordinary tail.
- Ross Richardson, PR #2104 `4bdc574da394a39f955e8cf4637075649c43a632`,
  and commdata2338, PR #2153 `5646398dcdc01769df83b939c6b3eb5ecb4d5ebd`:
  the three-query rank method and source-binding checks.
- Cinna Davis, PR #2216 `b80e9ba43367fb8b20877a97da1cb677c34f9264`:
  the paired shear and its bounded witness-separation result;
  PR #2122 `7045301a8c15eb4408e3e9d80969c9d50a914cde`: the mixed-helper
  obstruction for the unchanged first pair. The new graph argument here
  accounts for the intervening shear rather than reusing that trajectory.
- commdata2338, PR #2326 `fb7d64cd4a51c49bc56920305b0aca64011a420c`:
  the coordinate-access obstruction and dense-query handoff;
  PR #2174 `f79470a7931f3943360c10d15b428e0e4e479c22`: the adjacent
  two-record recovery theorem and recorded-cut boundary.
- Adam Gall, PR #2093 `8b21a900eb520e4f11ea177b310f66316f8e8983`:
  the common-axis witness family. The active coordinate-threshold and
  whole-owner separation investigations concern that different family.

Prepared by @starship-s with substantial Hermes and OpenAI Codex assistance.
New material is Apache-2.0. No predecessor result is claimed as new.
