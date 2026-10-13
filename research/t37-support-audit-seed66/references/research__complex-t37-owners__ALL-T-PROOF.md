# A signed-dual upper bound for every replica count

This is the package's independent relaxation bound. The separate construction
in [PROOF.md](PROOF.md) attains its kappa grid value. For the unchanged U8 local profile, whole-helper widths,
idle-capacity inventory and seven-step outer recipe, every positive integer
replica count has a kappa grid upper bound of **0.001661960547713947**.
The maximum possible improvement over PR890 within this family is therefore
**0.000000002773066918**. This removes the T <= 22 restriction from the
*upper-bound* argument. Feasibility and finite precision remain separate.

`independent/all_t_bound.py` reproduces the calculation with Python 3.11+ and the standard
library. It pins all consumed code and claims by SHA256. Run from the repository
root, with a fresh output filename:

```sh
python -B research/complex-t37-owners/independent/all_t_bound.py --out /fresh/ALL-T-BOUND.json
```

The exploratory arithmetic passed on Windows / CPython 3.14.7; repeated
fresh-output executions reproduced its complete receipt exactly. Relocation
changes only path resolution, the fail-closed optimization guard and explanatory
scope text; the numerical inputs and arithmetic are unchanged. The receipt
uses both retained exact rational moment engines, independently structured bin
enumerations, and all 47 retained outer constraints. It does not reproduce the
full supplier, owner map, hosted invoice, compiler or multiplication theorem.

## Fixed family and necessary inequalities

The U8 local paid profile per call is

```
{1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}.
```

There are nine calls and 896 live wires per replica. The whole-helper widths
per call are `{4:80,5:32,7:54,8:122,9:216}`. The idle stock per replica contains
672 cap-8 bins and 448 bins of each capacity 16, 32 and 48. These are PR890's
unchanged data. All geometric and execution-window restrictions are relaxed.

Use the PR795 signed width prices `(-1,-20,-8,-2,4)` at widths `(4,5,7,8,9)`
and bonuses `(2,4,8,-13)` at capacities `(8,16,32,48)`, as retained by PR890.
For an attainable residual rank r, let u(r) be the maximum bonus plus price
over every legal count vector in one bin leaving r. Cartesian enumeration of
all 1,163 legal vectors and a separate unbounded-fill recurrence agree on u.
In particular, u(0)=0, u(1)=19 and u(48)=-13.

For T replicas, let n_r count the bins with residual rank r. Summing actual
rank and signed price gives the necessary inequalities

```
sum r*n_r = 14382*T,
sum u(r)*n_r >= -3892*T.
```

The second direction matters: u is an upper bound on each actual bin's signed
price, while the sum of actual bin prices is fixed. Eliminating n_48 yields

```
sum_(0<r<48) v(r)*n_r >= 150*T,
v(r) = 48*u(r)+13*r,
v(1) = 925.
```

Rank zero contributes neither rank, credit, nor moment, so it may be omitted.

## One supporting inequality replaces replica enumeration

At the exact endpoint

```
z = 0.001664727258740678855773,
phi(r) = r*(73/r)^z,
c(r) = 48*phi(r)-r*phi(48),
lambda = c(1)/925,
```

both pinned rational engines independently certify lambda > 0 and

```
c(r) > lambda*v(r)  for every attainable 0<r<48 with r != 1.
c(1) = lambda*v(1).
```

The smallest certified strict margin is approximately 0.2913731504478641;
the receipt retains exact rational lower bounds for every rank. The comparison
also covers zero and negative v(r), with interval multiplication performed in
the correct direction for negative coefficients. No floating-point rank or
sign decision is used.

Consequently every nonnegative count vector satisfying the necessary credit
inequality satisfies

```
(sum c(r)*n_r)/T >= 150*c(1)/925 = (6/37)*c(1).
```

This holds for **every positive integer T**, with no replica cutoff. The idle
moment numerator is

```
sum phi(r)*n_r
  = (14382*T/48)*phi(48) + (sum_(r<48) c(r)*n_r)/48.
```

All other normalized moment contributions are identical across T. Thus the
normalized formal remainder profile

```
n_1/T = 6/37,  n_48/T = 11086/37
```

is a lower bound on every feasible owner's moment at z. Its smallest integral
representative is T=37, with `{48:11086,1:6}`. Exact equality in this relaxation
requires all nonzero non-48 residuals to have rank one and credit equality;
therefore T must be a positive multiple of 37. This argument alone does not
establish realization by actual bin patterns, owner time windows, or a complete
controller. The separate T37 construction and checks supply those facts.

## Root and outer transfer

Adding nine copies per replica of the U8 local profile to the T37 residual
profile gives live stock 33,152 and rank deficit 11,840. Both exact rational
engines certify moment < 1 at

```
0.001664727258740678855772
```

and moment > 1 at its next 1e-24 tick z. At z every physically feasible profile
has moment at least this formal T37 profile, hence also rejects z. Every
proper-child moment is increasing in its saving exponent, so its admitted
complex saving must be below z.

The unchanged outer map is increasing in this range: each update is
`a_next=s*(1-s+a_old)`, whose two partial derivatives are positive when
0<s<0.002 and a_old>=0; the final rational map is increasing in a. The bit
endpoint 0.001733427039589844234749 remains above the complex endpoint.
Applying the retained seven-step map to either T37 endpoint produces the same
1e-18 grid value, **0.001661960547713947**. All 47 strict constraints pass for
the formal arithmetic, and the next-grid control is rejected. This makes the
stated grid value an all-T upper bound under the same outer recipe.

The upper-bound use of the retained 512-bit bootstrap *driver* does not admit
a larger-T physical supplier. It evaluates the same numerical outer map for
the upper relaxation. A construction using a different payload must separately
recompute its finite bootstrap cutoffs and complete invoice. This package's
construction does so with a charged 1024-bit complex allowance.

## Attribution and scope

The signed-dual method and integer prices are inherited from Chafik Boukhalfa's
(chafreaky) PR795 and PR890.
PR890's `complex-t21-owner-bound/PROOF.md` supplies the fixed-family equations;
this note adds the supporting ratio inequality and removes the replica cutoff
from the relaxation. The U8 construction and T16/T21 controller lineages remain
credited to their original contributors. Exact arithmetic engines and outer
driver are imported unchanged and credited through their retained notices.

Prepared for Jonathan with substantial OpenAI Codex assistance, including
separately performed arithmetic cross-checks. No independent human peer review
is claimed. The all-size/compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape, analytic transfer and bit H1-H5 assumptions
are unchanged. See [NOTICE.md](NOTICE.md) for retained attribution.
