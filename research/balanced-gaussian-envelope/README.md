# Sharp fixed-parameter Gaussian envelope for the balanced arithmetic

**Research note / mathematical audit. No new multiplication bound.**

For the pinned historical `balanced_shared.py` formula, omit only the
`b_below_one_over32` row and assume valid supplier ordering and positive
abstract bridge gaps. A positive target at a fixed effective bit parameter
`a` is arithmetically feasible exactly when

$$
0<a<\tfrac12,\qquad 0<\kappa<M(a),\qquad
M(a)=\begin{cases}
 a/(1+a),&0<a\leq1/3,\\
 (1-2a)/(4a),&1/3<a<1/2.
\end{cases}
$$

Both branches are strict suprema. This completes the fixed-`a` arithmetic
picture beyond the sufficient interval `a<1/3` in
[PR #294](https://github.com/CrocSwap/integer-mult-bounds/pull/294).
It does not identify an error in that PR: its proof explicitly says that
its sufficient input interval is not necessary. The diagnostic cap `1/4`
and the balance `a/(1+a)` were already recorded in the repository's
[domain audit](../../docs/research/assembly-domain-audit.md).

| Fixed effective parameter `a` | Strict supremum `M(a)` |
|---:|---:|
| `1/64` | `1/65` |
| `1/3` | `1/4` |
| `2/5` | `1/8` |
| `49/100` | `1/98` |
| `a >= 1/2` | No positive feasible target in this formula |

Extending `a/(1+a)` past `a=1/3` overestimates what this parameterization
permits. A stronger **supplier** need not use its full saving as `a`: the
source permits a smaller effective parameter. The decreasing branch is not
an obstruction to stronger suppliers or other assembly equations.

## Exact object and assumptions

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected certificate at that base is #626 with #543,
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
It is recorded for orientation, not replaced or revalidated by this note.

The audited source is
[`research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py`](../coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py),
SHA-256 `c3204e1758057f5ef10724014f38b91b8a01f6d8a3562b054263fc74795bfd90`.
These bytes also match PR294's pinned assembly. The three negative-control
switches `original_prefix`, `old_guard`, and `old_exposures` are all **false**.
This is a claim about that formula, not every later outer engine.

All parameters below are rational. Fix `0<a<b`, `0<beta<1` and
`L=(1-beta)b-a>0`, retain the source's preconditions `0<h<1/2` and
`kappa>0`, and assume both bridge gaps are positive. For any `0<a<1/2`,
the ordering can be supplied abstractly by `b=(a+1)/2` and
`beta=(b-a)/(2b)`.

The actual `validate_shared_bridge` gate and the existence of a uniform bit
supplier admitting `a` are not established for these hypothetical rows.
No finite circuit, compiler, hosting, moment enclosure, recursion,
precision/recovery, tape or analytic interface is supplied. The production
cap and every existing file remain unchanged.

## Proof

Put `t=1-2h`, so `0<t<1`. The source equations become

$$
q=at,\quad \epsilon=\frac{1+t}{2(1+at)},\quad
G=\frac{at(1+t)}{2(1+at)},\quad
r=G+\frac{1-t}{4}.
$$

The decisive exact factorization is

$$
\frac14-r=\frac{t\,[1-a(2+t)]}{4(1+at)}.
$$

Thus `r<1/4` is equivalent to `a(2+t)<1`. It forces `a<1/2`.
For such `a`, the complete admissible interval is `0<t<T`, where
`T=min(1,1/a-2)`. Equality is excluded, including the double endpoint
at `a=1/3,t=1`.

**Sufficiency for the other rows.** In this interval,
`0<q<a<1/2`, `1/2<epsilon<1`, `0<h<1/2`,
`0<c=q+h/4<5/8`, `0<delta=h/8<1/16`, and `0<r<1/4`.
The potentially restrictive residuals reduce to

$$
\begin{aligned}
1-\epsilon-G&=h,&1-\epsilon-r&=h/2,\\
1-\epsilon(1+c)&=h(1-\epsilon/4),&\epsilon-a&>0,\\
\epsilon-(1-r)/2&>0,&8-\epsilon+r-\delta-G&=8-\epsilon+3h/8>7.
\end{aligned}
$$

Since `a<b`, the source's internal exponent is `tau=1-a`. Its remaining
nontrivial ordering slacks are `L`, `2ah`, `L+2ah`, `h/4`, `ah`, and
`b-a+ah`; all are positive. The elementary sign slacks follow from the
parameter bounds and the two assumed bridge gaps. The seven margins are

$$
(G+h,\ a,\ G,\ a,\ G+3h/8,\ G+7h/8,\ \epsilon).
$$

Their minimum is exactly `G`, since `G=epsilon*q<q<a` and `q<1`.
Consequently all 46 non-cap rows and the scalar preconditions hold
**if and only if** `a(2+t)<1` and `0<kappa<G`, under the stated ordering
and bridge assumptions. The verifier compares the factored value of each
of the 47 rows, including the diagnostic value of the cap, with execution
of the unchanged source function.

**Sharp supremum and explicit witnesses.** For `0<t<T<=1`, subtraction gives

$$
G(a,T)-G(a,t)=
\frac{a(T-t)(1+T+t+aTt)}{2(1+aT)(1+at)}>0.
$$

Hence `G` is strictly increasing in `t`. Its supremum is `G(a,T)`:
`a/(1+a)` if `a<=1/3`, and `T/4=(1-2a)/(4a)` otherwise.
These give the stated two branches of `M(a)`.

Every rational `0<kappa<M(a)` has an explicit rational witness. Set

$$
t=T-\frac{M(a)-\kappa}{2},\qquad h=\frac{1-t}{2}.
$$

Because `M(a)<aT<T/2`, this has `0<t<T`. In the subtraction formula,
the coefficient of `T-t` is at most `a(3+a)/2<7/8<1`.
Therefore `G(a,t)>M(a)-(T-t)=(M(a)+kappa)/2>kappa`.
The earlier sufficiency argument proves the witness meets every retained
inequality. No finite search or limiting uniformity assertion is needed.

**Original cap.** If `b<1/32` is retained, feasibility requires
`0<a<b<1/32`, and the same construction attains exactly
`0<kappa<a/(1+a)` for each admissible fixed `a` and leaf ordering.
For an existential choice of `b`, use `b=(a+1/32)/2`.
The overall supremum remains the known `1/33`, unattained.

## Reproduction and evidence

From the repository root, with standard-library Python 3.11 or later:

```sh
python3 -B research/balanced-gaussian-envelope/verify.py
```

Expected result:

```text
PASS_SCOPED_BALANCED_GAUSSIAN_ENVELOPE cases=7965 witnesses=288 controls=12
```

The command verifies the source pin, executes only its `assembly` function
body with an explicitly assumed bridge and an observing `require`, and
compares every exact slack against a separate `t`-coordinate calculation.
Observing a rejected source row is not production acceptance; the cap's
failure remains present in the receipt. Failures outside the slack dictionary,
including the positive-`h` and positive-`kappa` checks, remain visible too.

Seed 60 selects all proper fractions with denominators 59, 60 and 61 for
`a`; each is crossed with all proper reduced fractions of denominator at
most 12 for `t`. The complete finite domain has 7,965 pairs: 3,206 satisfy
the relaxed region and 4,759 do not. All 47 fractions per pair agree.
There is no early stopping or optimization search. Another 288 constructed
witnesses exercise both branches, original-cap acceptance where applicable,
and 60-decimal-place approaches to the thresholds and target supremum.

Twelve controls cover Gaussian equality/excess, `a=1/2`, target equality,
leaf equality, nonpositive bridge gaps, cap equality, zero backoff, zero
target, an omitted Gaussian row and source drift. The omission control
has **only** the Gaussian and cap rows failing; omitting the former would
admit an invalid point to the relaxed diagnostic. This is a concrete
control of the audit, not a claim that production omits that row.

[`EXPECTED.json`](EXPECTED.json) records exact examples, counts, controls,
and a deterministic SHA-256 of the entire 47-slack transcript.
`--write PATH` generates a receipt; default execution compares the
committed receipt without writing files. Finite checks support the written
proof and do not constitute formal verification of the universal statement
or the multiplication theorem.

The same receipt passes on Python 3.11 and 3.14 (and the default 3.15
interpreter). The pre-existing seven `test_assembly_domain.py` tests and
`make selected-record-check` also pass. The full `make verify` and selected
supplier cold replay are not run for this isolated research addition.

## Attribution and concurrent work

Contribution by **BigCactusLabs**, with substantial OpenAI Codex assistance
in the derivation, implementation, review and writing. No human peer review
or proof-assistant verification is claimed. Apache-2.0 under the repository
license; predecessor source and notices are unchanged.

Credit maximussthegreat's PR294 for the constructive sufficient interval
and slack factorizations, Douglas Colkitt's arithmetic-domain audit for the
independent Gaussian cap and source-observation method, and Romain Hedouin's
[PR183](https://github.com/CrocSwap/integer-mult-bounds/pull/183) for the
fixed-domain constraint reduction. The source credits PR141, PR34/RaD/PR23,
icekylinx, PR100/103, and the shared-bridge supplier lineage.

[PR657](https://github.com/CrocSwap/integer-mult-bounds/pull/657) concerns a
different, broader pass/accounting ceiling. This note instead proves a sharp
fixed-parameter region for one historical formula. It imports neither
PR294's implementation nor PR657's theorem. Reference heads and hashes are
in [`SOURCES.json`](SOURCES.json), along with the assignment, candidate
selection and coordination record.
