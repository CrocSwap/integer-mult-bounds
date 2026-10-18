# A cutoff-independent time bill for the selected bootstrap

This package proves a **conditional uniform lifting lemma** for the time
hypothesis (H2) in [Josie Elliston's PR1965](https://github.com/CrocSwap/integer-mult-bounds/pull/1965).
It separates the uniform recurrence and completed-wrapper premises from the
conclusion instead of promoting an asymptotic estimate to an all-width one.
For the **native first stage** of selected PR1094, the inherited paid moment
certificate gives an explicit bound

```
K = C * max(401501, 2*sigma)
```

when every named primitive coefficient below is at most C. This is a bound in
unknown implementation and stock constants, **not** their measurement. No
stock coefficient is supplied, no cutoff is changed, and no new supplier,
kappa, full all-size implementation or formal-kernel theorem is claimed.

PR1956 identified the carried-time-constant problem; PR1965 proved that time
constants can be absorbed after H2 is available; [ToikY's PR1990](https://github.com/CrocSwap/integer-mult-bounds/pull/1990)
explicitly retained both H2 uniformity and the unknown H3 stock coefficient.
The contribution here is the uniform implication with a complete bill and a
source-bound rational constant. It does not repeat their fourteen stock
headrooms or import the historical m=120 reserve coefficient.

## Precise premises

Fix q >= 2, 0 <= a <= s < 1 with s > 0, p = 1-a and tau = 1-s. All widths
are positive integers. The radix and primitive implementations are fixed
before widths and any bootstrap cutoff are chosen. Write a' = (1-s)s+s*a.

1. **Uniform stopped primitive.** For nonnegative coefficients c_r on integers
   1 <= r < m and m >= 2, normalized time T(n,w) satisfies, for every w >= 1,

   ```
   T(0,w) = 0
   T(n,w) <= Cleaf*w^p                         (1 <= n < m)
   T(n,w) <= sum_r c_r*T(r*floor(n/m),w)
             + Cadapt*n + Cpeel*w^p           (n >= m).
   ```

   The constants are nonnegative, independent of n, w and the cutoff, and
   uniform over the allowed complete spectators and generated prefix controls.
   The same normalized recurrence is stated in `notes/stopped-product-interface.tex`,
   lines 31-53. The uniform primitive implementation, especially the logical
   volume normalization, remains an inherited premise; the finite word does
   not prove it. Let g1 and gt be certified positive lower bounds on
   `1-sum c_r*(r/m)` and `1-sum c_r*(r/m)^tau`.
2. **Completed endpoints and wrapper tolls.** Each reversed call restores its
   row, preserves complete spectators, and has the stated endpoint. Each of
   the three ordinary-wrapper shifts costs at most Cshift*n per unit logical
   volume. One outer row padding/unpadding, including its scans and bookkeeping,
   costs at most Cpad*V, and the padded volume is less than 2V. The completed
   old algorithm exchanges residual digits for at most Crem*V*w^p and the
   high parts for at most Chi*V*k^p. These are actual charge hypotheses, not
   free operations. The constants include radix-to-binary conversions inside
   old leaves, their fixed multiplicities, and permitted spectator handling.
   PR185's reviewed contract and the retained `three-stage-cover-rows.tex`
   explain these calls and restore their rows before reuse.
3. **Fit and stock.** At the particular width e under consideration, set
   `w=ceil(e^s)`, take an integer `0 <= k < e/2`, and require
   `k <= ceil(sigma*w*(1+log2(e)))`, for fixed sigma >= 0. The actual borrowed
   width `ceil(log_q S(e,w))` satisfies this implication if H3 holds. We do not
   derive H3 or assume its historical 252 or 57604 constants. Put
   `n=floor((e-k)/w)`; the residual contains fewer than w digits.

These premises are stronger than an eventual big-O statement. A finite spike
in a leaf's cost can satisfy an eventual estimate while violating a proposed
all-width coefficient. The verifier includes such a counterexample. No
unknown spike is silently placed below the selected recorded cutoff.

## Uniform lifting lemma and proof

Define

```
A = Cadapt/g1
B = max(Cleaf, Cpeel/gt).
```

Strong induction on n proves `T(n,w) <= A*n+B*n^tau*w^p` for every w and n.
At a non-leaf, `r*floor(n/m) <= (r/m)*n < n`. The linear term leaves at
least `g1*A*n = Cadapt*n`. The stopped term leaves at least
`gt*B*n^tau*w^p >= Cpeel*w^p`. For 1 <= n < m, `n^tau >= 1` and B >= Cleaf;
n=0 is the empty body. This is the inherited weighted induction with its
constants and all-width quantifiers made explicit; it is not a new recurrence.

The complete normalized bill, before estimating powers, is

```
(4*A + 6*Cshift)*n + 4*B*n^tau*w^p
    + Cpad + Crem*w^p + Chi*k^p.                 (1)
```

The factor four pays **two** reversed calls on a row volume less than **twice**
the original volume. The factor six pays three shifts on that padded volume.
Padding occurs once outside the recursion. The residual and high-part calls
are completed ordinary calls after restriction to the genuine row range;
their internal borrowing is included in Crem and Chi. The five-operation
ordinary wrapper is chronological, not a raw reversed call substituted for
an ordinary one. Nothing in (1) changes recursive child multiplicities.

For every e >= 1, `e^s <= w <= 2*e^s`, `n <= e/w <= e^(1-s)`, and

```
n^tau*w^p <= e^tau*w^(s-a)
             <= 2^(s-a)*e^(tau+s*(s-a))
             <= 2*e^(1-a').
```

The nonnegative exponent s-a is a stated premise. For integer k >= 1,
`k^p <= k`; for k=0 both are zero. Thus

```
k^p <= 2*sigma*e^s*(1+log2(e)) + 1.
```

The ceiling's extra one and Cpad are absorbed by `e^(1-s) >= 1`, not omitted.
Consequently (1) is at most

```
K * [e^(1-s) + e^(1-a') + e^s*(1+log2(e)) + w^(1-a)],

K = max(4*A+6*Cshift+Cpad+Chi, 8*B, 2*sigma*Chi, Crem).    (2)
```

This is H2 on **every width where the named primitive contracts and stock fit
hold**, with no occurrence of a cutoff L or a carried factor `2^(L*Delta a)`.
The inequality is a mathematical implication, not a proof that all selected
primitive implementations meet its premises. It even handles an empty atom
body, which a purely large-width derivation need not discuss.

For a binary width E, numerical padding to `q^e`, where
`e=ceil(E/log2(q))`, increases logical volume by less than q^2 and has e <= E.
Thus the same conclusion follows with `q^2*K` and powers of E whenever the
radix-width premises hold; fixed conversion scans must be included in Cpad.
This does not assert that a cutoff stated for radix width e is automatically
the same cutoff for binary width E.

## Polynomial descriptor preparation without another cutoff

There is one common source of an implicit extra width threshold. The retained
bit proof, lines 136-145, amortizes polynomial generated-descriptor preparation
against a **complete** q^w target fiber. Suppose its work per prefix is bounded
uniformly by `Cdesc*e^d*w^b`, with fixed nonnegative integer d,b. Put
`D=b+ceil(d/s)`. Since e^s <= w,

```
Cdesc*e^d*w^b/q^w <= Cdesc*w^D/2^w <= Cdesc*2^D*D!       (3)
```

for every integer w >= 1. For D >= 1,
`w^D <= D!*binom(w+D-1,D)`, and the positive generating series gives
`sum_(w>=1) binom(w+D-1,D)/2^w = 2^D`; one summand is no larger than the sum.
For D=0 the bound is immediate. This exact factorial overcharge can be folded
into the relevant Cadapt, Cpeel or Cshift coefficient, multiplied by the number
of charged preparation sites. It adds no new cutoff or unit-cost arithmetic
assumption. A separate uniform bound on d,b,Cdesc and the number of sites is
still required. An incomplete fiber cannot use (3); that failure is an exact
negative control, not an assertion about the selected implementation.

## Native selected first-stage binding

All source pins are in [SOURCES.json](SOURCES.json), on main
`564148b82ae9df72163f22106f15e73efca8aff2`, priority revision 4. The chooser's
independent seed is `3c6ed534c7c882d069b0dc2c8cd99397` ([SELECTION.json](SELECTION.json)).
The selected record binds the assembly and its PR589 BIT supplier. The latter
has **m=64**, W=28416, maximum child 42 and the paid profile in `EXPECTED.json`.
The selected complex m=73 producer is not substituted for it.

The frozen PR1087 assembler specifies the surcharge
`10^-16 * 32*m^2*sum(H_r)/W` additional rank-one children and

```
s = min(bit_lower, (1-10^-24)*complex_lower) - 10^-27,
a = 384599/10^10.
```

The selected receipt certifies the surcharged moment at bit_lower; both
retained exact upper endpoints are strictly below one. **We authenticate and
reuse that certificate, not recalculate another moment root or claim an
independent supplier replay.** The first-stage exponent is checked against
its recorded value. Exact rational arithmetic gives

```
g1 = 16326904278023 / 2890625000000000,
gt = (11/32)*(bit_lower-s)
   = 25504319623965913202561177203577795565550087
     / 1280000000000000000000000000000000000000000000000.
```

Here gt is a new explicit **sufficient gap transfer**, not an estimated moment:
for x <= rho=42/64 and d=bit_lower-s in (0,1), concavity gives
`x^d <= 1-d*(1-x) <= 1-d*(1-rho)` (the tangent at one). Multiplying the inherited
moment terms at exponent `1-bit_lower` yields `mu_(1-s) < 1-gt`. All coefficients,
including the rank-one surcharge, are nonnegative. Hence `A <= C/g1` and
`B <= C/gt` if all seven coefficients in the premises are at most C. Exact
cross multiplication certifies

```
4/g1+8 < 717,
8/gt < 401501,
```

so (2) follows with `K=C*max(401501,2*sigma)`. This conservatively pays every
term in (1). It proves no bound on C or sigma and does not assert favorable
practical constants. For example, descriptor degree d=1,b=0 alone becomes
D=597 in (3); that remains a fixed finite time constant, not a stock charge.

## Reproduction and evidence boundary

```
uv run --python 3.12 --no-project python -I -B research/selected-bootstrap-uniform-time/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/selected-bootstrap-uniform-time
```

The registered replay runs the exact checker both normally and under `-O`.
Source hashes are checked before data are consumed; archived Python is read,
never executed. The checker compares the canonical regenerated JSON object
with [RESULT.json](RESULT.json). The finite evidence includes independent
recursion-tree sums versus dynamic programming, exact square comparisons for
rational specializations of the all-width bound, charged padding and complete
endpoint fixtures, factorial inequalities, and semantic/source controls. The
padding, incomplete-fiber and finite-spike fixtures are mathematical countermodels
to weakened hypotheses, not reports of bugs in the selected implementation.
The universal claim rests on the written induction and inequalities, not the
finite sample. No full selected cold replay or hosted CI success is claimed.

Observed with CPython 3.12: the scientific smoke and registered normal/optimized
replays pass. Each replay checks 6,156 recurrence cases, 539 complete wrapper
bills, 1,664 descriptor inequalities and 1,458 padded endpoints; all 16 controls
reject. The output includes `PASS_SELECTED_BOOTSTRAP_UNIFORM_TIME` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. This evidence does not measure C or sigma.

## Open next questions

- Bind each actual selected primitive implementation to the uniform constants
  and preparation-site counts in the premises. First inspect logical-volume
  normalization, fixed-tape parking and generated prefix work; the inherited
  all-size/compiler and tape contracts still block unconditional adoption.
- Derive the actual selected stock envelope sigma with a same-domain producer
  and depth argument. This is the separate H3 obligation and is not solved by
  a large coefficient cap or by the explicit time constant above.
- Apply the lemma at later stages only after their preceding completed ordinary
  contract is established; C may grow with the fixed stage, but must not hide
  a width- or cutoff-dependent premise. The result here binds native stage one.

[Task metadata](TASK.json) records the initial question, complete optimistic
bill, bounded overlap coverage and limits. Claims are confined to this package
and its PR; no discussion post is required.

## Credit

Josie Elliston supplied PR1956's carry audit and PR1965's time/space separation;
ToikY supplied PR1990's independent stock-fit audit and explicit H2/H3 limits.
Rohan Arun supplied the reviewed PR185 completed-leaf argument and selected
PR1094 assembly; Jeremy Kothe supplied PR1087's frozen selected producer.
The stopped recurrence and three-stage row/weighted-atom proofs retain their
original repository lineage; DreamingOfClouds's PR589 BIT supplier, on eumemic's
PR555 base, is used through its authenticated selected receipt. These constructions and the
weighted-induction method are not claimed as new.

Prepared by Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
