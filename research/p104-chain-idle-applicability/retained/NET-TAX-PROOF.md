# Net moment taxes for separated finite native units

This is a structural strengthening of the chronological product, paid
completion and disjoint splitting argument in
[`higher-moment-strictification`](../higher-moment-strictification/README.md),
especially its Sections 1--2 and its pinned
[`p7-TENSOR.md`](../higher-moment-strictification/vendor/p7-TENSOR.md).
The raw native profile used by the accompanying certificate is inherited from
[`native-lattice-retiming`](../native-lattice-retiming/README.md).
No raw native word, raw paid invoice, multiplication saving or selected result is
changed here. These are conditional finite-unit transformations, not a new
admission of the native or multiplication theorem.

The finite integer compiler is Jacob Alan Sussman's Theorem 1G, retained
through PR4268/PR4359. The chronological product and completion construction
comes through PR4414/PR4416, and the higher-moment estimate and logarithmic
compiler through PR4411 and `higher-moment-strictification`. The native
profile also retains the query-thinning and fresh-helper contributions of
Cinna Davis, PR4440/PR4441, and zxv's native retiming. Their attribution and
source pins remain those of the accompanying source manifest. This proof
contributes net tax accounting and the bounds below. Substantial OpenAI Codex
assistance, including delegated mathematical audit; Apache-2.0.

## 1. Notation and the exact gap identity

Fix a finite native unit with productive ranks `k_i>=1`, paid ranks `r_j>=1`,
ambient rank `m=max_i k_i` containing every paid job, and `B` independent
productive fields. Write

```
T_s = sum_i k_i^s,       P_s = sum_j r_j^s,
0<C<1,                  t=1-C,
u>=C,                   sigma=t+u>=1.
```

Choose integers `1<c<b<m` and `v>=1`, and set `J=c^v`, `L=b^v`.
The chronological native product has productive ranks `K`, paid ranks `R`,
`B^v` productive fields and moments `T_s^v`, `P_s^v`. Its ambient rank is
`m^v`. These assertions use the native product contract in Section 6 below;
they are not consequences of histogram arithmetic alone.

For an integer `D>=0`, define the exact disjoint splitting charge

```
S_t(D,J) = q J^t + r^t,   D=qJ+r,  0<=r<J,
```

where the zero remainder contributes zero. This definition also gives
`S_t(0,J)=0`. For `D<=J` it equals `D^t`.

Complete a productive rank `K<L` by a paid job of rank `L-K` on disjoint
axes of its actual owner. Its final productive rank is `L`. Split every
original paid job and every completion job at cutoff `J`. Define

```
tau(R) = S_t(R,J)-R^t,
E(K)   = K^t+S_t(L-K,J)-L^t       for K<L.
```

Both taxes are nonnegative: for `0<t<1`, splitting a nonnegative mass into
pieces increases its `t`-moment. Let `T'_t,P'_t` be the final moments.
Accounting separately for each original paid job and each completed owner
gives the exact identity

```
T'_t-P'_t = T_t^v-P_t^v - sum_R tau(R) - sum_(K<L) E(K).       (1)
```

Thus completion is charged for its net effect on the gap: its paid
`t`-moment minus the productive `t`-moment it adds. In particular, the
subtraction of `L^t` in `E(K)` is not new productive-field credit.

## 2. Stronger original-paid tax bounds

Put

```
h = C t^(t/C),
A(C,u) = max(C/u,h).
```

The elementary function `g(x)=x^t-x` on `x>=0` has its unique maximum at
`x=t^(1/C)`, with value `h`. In particular `0<h<C<1`.

For `R>J`, put `x=R/J>1` and `rho=frac(x)`. The exact charge gives

```
tau(R)/J^t = x-x^t+rho^t-rho <= x-x^t+h.                    (2)
```

For any `u>=C`, the right side is at most `A(C,u) x^(t+u)`.
Indeed, after dividing by `x^t`, the difference between this proposed upper
bound and (2) is

```
G(x) = A x^u-x^C+1-h x^(-t).
G(1) = A-h >= 0,
G'(x) = Au x^(u-1)-C x^(C-1)+ht x^(-t-1) >= 0.
```

The last inequality uses `Au>=C`, `u>=C` and `x>=1`. Hence

```
tau(R) <= A(C,u) R^(t+u) J^(-u).                            (3)
```

For the useful range `C<=u<=C/h`, this coefficient is simply `C/u`.
In particular this holds throughout `C<=u<=1`.

A different bound can be stronger. Let `n=ceil(R/J)` be the number of
nonzero split pieces. Concavity gives

```
S_t(R,J) <= n^C R^t,
tau(R) <= (n^C-1) R^t.                                     (4)
```

For `u>C`, the function `(y^C-1)y^(-u)` on `y>=1` has derivative

```
y^(-u-1) [u-(u-C)y^C].
```

It increases up to the unique point `y^C=u/(u-C)` and decreases afterwards.
Its maximum is

```
M(C,u) = (C/u)(1-C/u)^((u-C)/C).
```

Since `n<2R/J`, (4) therefore implies

```
tau(R) <= K(C,u) R^(t+u) J^(-u),
K(C,u) = 2^u (C/u)(1-C/u)^((u-C)/C),       u>C.              (5)
```

At `u=C`, the supremum of `(y^C-1)y^(-C)=1-y^(-C)` is one,
so the valid endpoint definition is `K(C,C)=2^C`. The strict inequalities
in intermediate estimates are not needed: the final certificate will be
strict. Define

```
Q(C,u) = min(A(C,u),K(C,u)).
```

Then `0<Q<=1`, and summing (3)/(5) over the original paid jobs gives

```
sum_R tau(R) <= Q(C,u) P_(t+u)^v / J^u.                    (6)
```

Unsplit jobs contribute zero tax; including their higher moments only
increases the right side. The older rough net bound
`(C/u)2^u R^(t+u)J^(-u)` is also valid: for `y>=1`,
`y^C-1 <= (C/u)(y^u-1) <= (C/u)y^u`, followed by `n<2R/J`.
For `u>C`, (5) improves its coefficient by the factor
`(1-C/u)^((u-C)/C)<1`; at `u=C`, (3) improves it from `2^C` to one.

When `C,u` are rational, `K` can be certified without floating point.
Choose a positive integer `d` clearing the denominators of `u` and
`(u-C)/C`. Then

```
K(C,u)^d = 2^(du) (C/u)^d (1-C/u)^(d(u-C)/C)
```

is rational. A rational upper bound `q` for `K` is equivalent to the exact
rational comparison `q^d >= K^d`. Directed rational log/exp enclosures are
another option, particularly when the clearing exponent is large.

## 3. Stronger completion net tax

For `D=L-K>0`, the exact division formula and the definition of `h` imply

```
S_t(D,J) <= D J^(-C)+hJ^t.
```

Consequently

```
E(K) <= LJ^(-C)-L^t + (K^t-KJ^(-C)) + hJ^t
     <= LJ^(-C)+2hJ^t-L^t =: H(L,J).                       (7)
```

The second step applies `x^t-x<=h` to `x=K/J`. It does not replace a
restricted sum over `K<L` by an unrestricted sum with possibly negative
terms. Since `L/J>1`,

```
H(L,J)/J^t = L/J-(L/J)^t+2h > 0.
```

There are at most `B^v` completed owners, so multiplying the nonnegative
upper bound in (7) by `B^v` is legal even when fewer owners are completed:

```
sum_(K<L) E(K) <= B^v [LJ^(-C)+2hJ^t-L^t].                (8)
```

This is strictly stronger than the rough completion bound
`[(3L/J)^C-1]L^t = 3^C LJ^(-C)-L^t`. For completeness, weighted
AM--GM applied with weights `t,C` to `t,1+t` gives

```
t^t(1+t)^C <= t*t+C*(1+t) = 1,
h <= C/(1+t) = C/(2-C).
```

Also `2 atanh(C/2) <= C log(3)`, by convexity of `atanh` between zero
and `1/2`. Exponentiating gives

```
2C/(2-C) <= 3^C-1.
```

Thus `2h<3^C-1`, and, since `J/L<1`,

```
LJ^(-C)+2hJ^t < 3^C LJ^(-C).
```

The rough bound itself follows by viewing `K` and all completion pieces as
at most `1+ceil((L-K)/J)<L/J+2<3L/J` positive pieces with total mass `L`,
then applying concavity. Equation (7) uses their actual capped partition.

## 4. A reusable normalized certificate

Define the raw ratios

```
alpha   = P_t/T_t,
gamma   = P_(t+u)/(c^u T_t),
delta   = B b/(c^C T_t),
epsilon = B c^t/T_t,
delta0  = B b^t/T_t.
```

Substitute (6) and (8) into (1) and divide by the positive `T_t^v`:

```
(T'_t-P'_t)/T_t^v
  >= 1-alpha^v-Q(C,u)gamma^v-delta^v-2h epsilon^v+delta0^v.
```

Therefore the exact strict inequality

```
alpha^v+Q(C,u)gamma^v+delta^v+2h epsilon^v-delta0^v < 1       (9)
```

certifies a strict final `t`-moment advantage. The negative term in (9)
belongs to the nonnegative per-owner bound (7), so it is not legitimate to
reuse it after independently discarding other parts of that bound.

If the h-bound is inconvenient, the valid weaker certificate is

```
alpha^v+Q(C,u)gamma^v+3^C delta^v-delta0^v < 1.               (10)
```

Both improve on charging the entire split/completion invoice on top of the
old moment. Equation (9) is uniformly stronger than (10). Neither requires
the ratios individually to be less than one if the displayed finite
inequality is certified directly.

For a certificate with interval bounds, all positive terms use upper
bounds and the subtracted `delta0^v` uses a lower bound. Any upper bounds
on `Q` and `h` suffice. Displayed decimals are not substitutes for this
directed exact comparison.

## 5. What the finite compiler receives

The transformed unit has all paid ranks at most `J`, all productive ranks
at least `L`, and ambient rank `m^v`; hence strict separation holds.
If (9) or (10) holds, it has `P'_t<T'_t`. Positive rank-one surplus then
follows even without assuming it separately for the raw profile:

```
P'_1 <= J^C P'_t < L^C T'_t <= T'_1.
```

The inherited integer lockstep flow and denominator-clearing construction
therefore receive a separated native unit with a strict `t`-superpotential.
Cancellation of its matched internal jobs gives the source/exit inequality
`sum_e x_e e^t <= sum_s w_s s^t`; equality at a balance root is unnecessary.
The logarithmic majorant from Section 4 of
[`higher-moment-strictification`](../higher-moment-strictification/README.md)
then applies with the new finite ranks and constants. In particular an exit
exponent can use

```
theta <= log(J)/log(L) = log(c)/log(b) < 1.
```

The resulting word is the finite algorithm specified by chronological
substitution, exact completion and division, lockstep scheduling and integer
batch clearing. A sufficient ambient rank does not bound its productive
width, denominator growth, scalar count or runtime. No materialized winning
word or practical implementation follows from this moment certificate.

## 6. Native and consumer hypotheses retained

The precise compiler premises are those in
[`FINITE-PRECOMPILATION.md`](../higher-moment-strictification/vendor/FINITE-PRECOMPILATION.md).
They include all-column arbitrary-input correctness, disjoint splitting with
complete spectators, priced permitted whole-job adapters at every positive
column multiplicity, and finite-program closure with owned storage fully
initialized, retained and erased. The present taxes do not prove any of
these premises.

In the chronological product, run separate copies of one native unit for
the productive roles of the other. At each common paid position, substitute
the second unit on the distinct actual physical owners, complete it and
restore every adapter before resuming the suspended copies. Correlated
values in distinct fields are allowed by arbitrary-input correctness; they
do not authorize copying an input to create productive credit. Different
paid positions of one suspended instance cannot be combined.

Completion acts only after the whole product has finished, on disjoint
unused axes of the same original productive owner. Canonicalization is a
permitted conjugation of the complete existing job, including its input
map; an output-only change is insufficient. Whole-job adapters stay around
the complete split replacement, rather than being omitted between abstract
rank numbers. At column multiplicity `f`, all these ranks and disjoint
blocks are multiplied by `f`, and the same finite native prescription must
remain valid.

Every nested raw instance retains its own allocated owned-center banks and
all movements, routes, scalars and phase normalizers remain charged. The
uniform compiler's batch denominators are cleared using actual integer
multiplicities. The final finite word's precision, storage, coefficient and
movement constants must be recomputed by the inherited full-word counting
prescription; the smaller ambient rank does not permit reusing numerical
constants from an old small template.

Analytic decomposition, native tensor realization, delayed BIT cover where
used, fine-prime exclusions, physical fixed-tape execution, stock, precision
and exact recovery remain inherited obligations. Applying the same consumer
at a smaller certified uniform rank requires its changed constants and its
strict endpoint hypotheses. The net tax theorem alone does not improve
the multiplication saving or update `certificates/selected-result.json`.
