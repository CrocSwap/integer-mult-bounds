# A multi-role square-zero radical pencil obstruction

**Scoped proof, with finite corroboration. No new kappa.** Over any field K,
let R = K[x,y]/(x,y)^2. Paid factors on n roles are I + u v^T, where u is
in R^n and v is in K^n. Arbitrary GL_n(K) maps are free and may occur anywhere.
If A in M_n(K) has no left eigenvector over K, then

```text
M = xI + yA
```

is unreachable by any finite word. This is an arbitrary-length obstruction,
not a failed bounded search. Extra roles restored to the identity are outside
the statement.

An explicit three-role instance over F2 is

```text
    [0 0 1]
A = [1 0 1],       A^3 + A + I = 0.
    [0 1 0]
```

The polynomial t^3+t+1 has no binary root. The verifier also enumerates all
512 binary three-by-three matrices and finds 48 with no binary left
eigenvector. Each of the corresponding 48 pencils is unreachable by the
theorem. This is not a count of every unreachable pencil.

This package was produced by Nick Petalas. Apache-2.0.

## What changes and predecessor credit

[PR #4745](https://github.com/CrocSwap/integer-mult-bounds/pull/4745), exact
head `3edea13af13b755932852e9306a714b317630dda`, gives the complete two-role
square-zero radical criterion and introduces its first-zero scalar-prefix
argument. Its README limits that classification to two roles. This package
uses the same idea to obtain a necessary condition at arbitrary role count.
It does not audit or replay #4745 and does not assert a multi-role converse.

The free-map normal form is from Nick Petalas's
[PR #4243](https://github.com/CrocSwap/integer-mult-bounds/pull/4243).
The right-vector alphabet and column bound are Wentao Li's
[PR #4099](https://github.com/CrocSwap/integer-mult-bounds/pull/4099), following
[PR #2513](https://github.com/CrocSwap/integer-mult-bounds/pull/2513).
ToikY's #4334 and Nick Petalas's #4276/#4601/#4749 are the related two-role
general-target and invertible-target successors. No predecessor code or
finite enumeration is imported. The proof below is self-contained.

The `connector-alphabet-change` card is **changed** to an algebraic side
question in the existing alphabet. It is not a new legally priced connector.
The card's first working control passed with `pairings=945`, `queries=74`.
That control is orientation, not evidence for this theorem.

## Proof

Write a ring-valued matrix uniquely as P_0 + xP_x + yP_y, with all three
coefficient matrices over K. Products obey

```text
(TP)_0 = T_0 P_0
(TP)_x = T_0 P_x + T_x P_0
(TP)_y = T_0 P_y + T_y P_0.
```

### Normalize free maps

For G in GL_n(K), conjugation sends I+u v^T to
I+(Gu)(v^T G^-1), still a paid factor. Move every free map to the right.
An alleged word for M therefore has the form

```text
M = F_L ... F_1 G = P G.
```

Consequently P_0=0, P_x=G^-1 and P_y=A G^-1. In particular P_x is invertible.

### The first zero scalar prefix

Let k be the first index at which the scalar part of F_k ... F_1 is zero.
It exists since P_0=0. Immediately before it the scalar prefix H is nonzero.
Write

```text
F_k = I + (a + xb + yc) v^T,
T   = I + a v^T.
```

Here TH=0. A rank-one perturbation of I has nullity at most one. Since
H is nonzero, T is singular, rank(H)=1, v^T a=-1, and v^T T=0.
The kernel of T is K a, so H=a r^T for a nonzero row r^T. Thus
psi = v^T H = -r^T is nonzero.

Let C_x,C_y be the radical coefficient matrices before this step. Immediately
after the step they are

```text
D_x = T C_x + b v^T H,
D_y = T C_y + c v^T H.
```

Multiplication by v^T kills the first summands, giving

```text
v^T D_x = alpha psi,       alpha = v^T b,
v^T D_y = beta  psi,       beta  = v^T c.
```

This common-row identity is the essential restriction imposed by the
base-field right vector. No assumption on earlier radical coefficients was
made.

### Later factors cannot remove the restriction

After the first zero scalar prefix, the scalar prefix stays zero. Radical
parts of every later factor multiply a zero scalar prefix and contribute
nothing. If S is the product of their scalar parts, the final coefficients are

```text
P_x = S D_x = G^-1,
P_y = S D_y = A G^-1.
```

Invertibility of P_x forces both S and D_x to be invertible. Hence alpha is
nonzero, because v^T is nonzero and v^T D_x cannot vanish. Put
w^T = v^T S^-1 and lambda = beta/alpha. Then w^T is nonzero and

```text
w^T A G^-1 = w^T P_y
            = v^T D_y
            = lambda v^T D_x
            = lambda w^T P_x
            = lambda w^T G^-1.
```

Cancel G^-1 on the right. We obtain w^T A = lambda w^T, a left eigenvector
over K. Its absence excludes the alleged word, irrespective of its length.

For the displayed binary A, a left eigenvalue would be 0 or 1. Multiplying
A^3+A+I=0 by its nonzero left eigenvector would give
(lambda^3+lambda+1)w^T=w^T=0. This contradiction proves the explicit instance.

## Finite corroboration and controls

The standard-library verifier executes the following bounded checks. They
corroborate the proof; they are not an enumeration of arbitrary-length words.

- All 28 singular rank-two scalar factors on three binary roles and all
  seven nonzero compatible scalar prefixes per factor give 196 pairs.
  For each pair, the verifier checks all 512 preceding single-coefficient
  matrices and all eight radical columns. The common-row identity holds in
  all **802,816** cases. Exactly **150,528** have an invertible new coefficient;
  each has a nonzero common-row multiplier. The identity is checked for one
  arbitrary coefficient at a time, so it applies separately to x and y.
- Every one of the 512 possible A is tested against all seven nonzero binary
  rows and both scalar eigenvalues. There are **48** eigenvalue-free matrices.
  All 168 free conjugations of the displayed companion remain eigenvalue-free
  and give **24** distinct conjugates.
- Three literal reachable controls are each executed on all 512 dirty ring
  vectors, giving **1,536** chronological action comparisons. They are a rootful
  upper-triangular pencil, the single-coefficient target yA, and the collapsed
  target x(I+A) obtained if y is identified with x. The latter two show why an
  invertible first coefficient and independent radical variables matter.
- Two exact chronology controls reject reversing the first-zero product and
  omitting its radical contribution. The second error would miss a full-rank
  coefficient produced at a singular scalar step.

Every run prints a generated receipt bound to the SHA256 of all five package
files. No receipt is stored or hand-written. All checks use explicit exceptions
and remain active under `-O`.

## Reproduction

From the repository root, with CPython 3.12 and no third-party dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/multirole-radical-pencil/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/multirole-radical-pencil/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/multirole-radical-pencil
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/multirole-radical-pencil --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path. Each
registered command has a 120-second timeout and takes less than one second
locally. Expected final marker:

```text
PASS_MULTIROLE_RADICAL_PENCIL transitions=802816 full_rank=150528 excluded_pencils=48 no_new_kappa
```

## Limits and implementation bounds

This is a necessary condition only. A scalar eigenvalue is not proved
sufficient. The ring has two independent radical generators with all their
products zero. Right vectors and free maps must be over K. Arbitrary
ring-valued free maps, higher radical nilpotency, and restored auxiliary roles
are outside scope. No native supplier, recursive cost, precision, stock or
complete multiplication theorem is supplied. Independent human and formal
proof-kernel review are unclaimed. No Lean, Docker or selected operator replay
was run.

The code has no recursion, accepts no variable search sizes, and bounds every
loop by the displayed finite domains. Its largest table has 4,096 integers;
the receipt reads at most 128 KiB from each of five fixed paths. Python's
managed allocations depart from fixed steady-state allocation. Their domains
and lifetimes are bounded here. No shared code or interpreter configuration
changes are needed.

## Open next questions

1. Is a base-field eigenvalue sufficient when n>=3? Start with the direct sum
   of a scalar block and the binary companion of t^2+t+1. The proof gives one
   common row but no recursive criterion on its quotient.
2. Can an extra role restored to the identity make the displayed pencil
   reachable? Start with diag(xI_3+yA,I_1). Its nonzero scalar endpoint is the
   precise reason the present first-zero proof does not apply.

The structured questions, relevance, first steps and blockers are also in
[TASK.json](TASK.json). These follow-ups are not investigated here.

## Source and overlap scope

The originating card and selected record are pinned at
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. The clean branch was created from
the refreshed canonical main `1f87c3578ae546c8f903f7f4d83dc2e2fb99650b`; the
guidance and selected record are unchanged between those commits. Open
predecessor #4745 is a credited conceptual source, not an imported executable
or a required unmerged Git object. The theorem and verifier are self-contained.

Before claiming, live open PRs, this account's recent PRs, the latest handoffs,
active Discussions, local reservations, and distinctive merged/main
searches were checked. The overlap helper's cached remote pagination was
complete at approximately 19:22 UTC; its sparse local-note coverage was
incomplete and cannot certify novelty. The related two-role all-field count,
cube-zero example, rank-one-residue census and polynomial-ring cost claims
study different questions. The main two-role predecessor's twelve unreachable
radical targets are not rechecked or recounted here.

Claim: [handoff post](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19131197).
