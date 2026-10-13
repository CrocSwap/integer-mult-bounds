# Sharp uniform range for the T37 owner relaxation

**Status: mathematical research note. No new kappa.**

PR942 certifies the T37 supporting inequality at one saving endpoint.
Concurrent PR995 extends it through `b=1/3` and exhibits failure at `b=1`.
This note determines the exact first failure and proves the sharp uniform range.
The result applies to every positive replica count and any unchanged contribution per replica from a local supplier.
It does not assume the U8 paid profile or infer physical feasibility from a relaxed profile.

Let `b_star` be the unique positive solution of

```text
37*(3/2)^b - 48^b - 36 = 0.
```

We prove `16/25 < b_star < 13/20` with exact arithmetic.
Thus `0.64 < b_star < 0.65`.
An exploratory floating calculation suggests `b_star ≈ 0.64186556`; that decimal is not a certified root enclosure.

For every `0 < b <= b_star`, the normalized T37 remainder profile minimizes the signed-dual relaxation over all positive replica counts.
For every `b > b_star`, an explicit relaxed T16 profile has a strictly smaller normalized moment.
This latter statement is not a physical packing counterexample.
The selected saving endpoint near `0.001665` lies far inside the proved interval.

## Fixed inventory and precise relaxation

Retain the whole-helper widths, call count, and idle capacities of PR795/PR890/PR942.
Every replica has nine calls, with this helper inventory per call:

```text
width:       4   5   7    8    9
multiplicity:80  32  54  122  216
```

The bin inventory per replica is:

```text
capacity:       8   16   32   48
multiplicity: 672  448  448  448
```

A bin may contain only whole helpers, with total width at most its capacity.
The residual rank is the unused capacity.
Let `u(r)` be the largest capacity bonus plus helper price of any bin pattern with residual rank `r`.
Use the inherited integer prices and bonuses:

```text
helper prices at widths (4,5,7,8,9): (-1,-20,-8,-2,4)
capacity bonuses at (8,16,32,48):    (2,4,8,-13)
```

The complete enumeration contains 1,163 legal count vectors and 45 attainable residual ranks.
It gives `u(0)=0`, `u(1)=19`, `u(32)=8`, and `u(48)=-13`.
Define `v(r)=48*u(r)+13*r`, so `v(1)=925` and `v(32)=800`.

For each positive integer `T`, define `R_T` by nonnegative integer counts `n_r` on attainable ranks satisfying:

```text
sum n_r       = 2016*T,
sum r*n_r     = 14382*T,
sum v(r)*n_r >= 150*T.
```

Every whole-helper packing of the fixed inventory gives a point in `R_T`.
Indeed, total residual mass is `14382*T` and total actual signed price is `-3892*T`.
Since each actual bin price is at most `u(r)`, summing gives the stated credit inequality.

The underlying totals are `48384-9*3778=14382` for residual mass and `896+9*(-532)=-3892` for signed price.
The relation `48*(-3892)+13*14382=150` verifies its direction.
The relaxation omits capacity assignments, helper multiplicities within residual classes, chronology, charts, and physical execution.
We assume no sufficiency of these constraints.

Define

```text
phi_b(r) = r*(73/r)^b for r>0; phi_b(0)=0,
I_b(n)   = sum phi_b(r)*n_r,
L_b      = (6*phi_b(1)+11086*phi_b(48))/37.
```

**Theorem.** For every `T>=1`, `n in R_T`, and `0<b<=b_star`, `I_b(n)/T >= L_b`.
For `0<b<b_star`, equality requires `n_1=6*T/37`, `n_48=11086*T/37`, and no other positive residual ranks.
Thus equality requires a positive multiple of 37 replicas in that open interval.
At `b=b_star`, rank 32 also permits equality.
Both the T37 profile and the relaxed T16 profile below attain equality at that boundary.

This is a theorem about the entire relaxation, not a finite sweep of replica counts or exponents.
Adding any identical per-replica local contribution preserves the inequality.
A physical realization, complete invoice, and outer transfer require their own proofs.

## Uniform supporting inequality

Set

```text
c_b(r) = 48*phi_b(r)-r*phi_b(48),
F_r(b) = 925*r*((48/r)^b-1)-v(r)*(48^b-1).
```

The identity

```text
925*c_b(r)-v(r)*c_b(1) = 48*(73/48)^b * F_r(b)
```

reduces the supporting inequality to the sign of `F_r`.
Rank one gives equality identically.
Rank zero and rank 48 contribute zero excess and zero credit.

For each `1<r<48`, put `x=48^b` and `a=log(48/r)/log(48)`.
Then `0<a<1` and

```text
F_r(b) = G_r(x),
G_r(x) = 925*r*x^a - v(r)*x + v(r)-925*r.
```

Here `G_r(1)=0` and `G_r''(x)=925*r*a*(a-1)*x^(a-2)<0` for every `x>0`.
Thus `G_r` is strictly concave.
If `F_r(B)>0`, its chord from `x=1` to `x=48^B` proves `F_r(b)>0` for every `0<b<=B`.

Exact cube-root enclosures certify `F_r(2/3)>0` for every attainable `r` except `0,1,32,48`.
This covers every noncritical rank throughout `0<b<=2/3`, including ranks with negative credit.
No sample between zero and two thirds enters this argument.

For rank 32,

```text
F_32(b) = 800*(37*(3/2)^b - 48^b - 36).
```

Exact radical bounds certify `F_32(16/25)>0` and `F_32(13/20)<0`.
Strict concavity in `x` and `G_32(1)=0` give exactly one further zero for `x>1`.
For completeness, the secant slope `G_32(x)/(x-1)` strictly decreases for `x>1`.
Its signs at the two certified points therefore give uniqueness and the signs on each side.
Consequently `F_32(b)>0` for `0<b<b_star`, equals zero at `b_star`, and is negative thereafter.
Since `b_star<13/20<2/3`, all other noncritical ranks remain strictly positive at that boundary.

## Summation, equality, and sharpness

For `0<b<=b_star`, the supporting inequalities and `c_b(1)>0` give

```text
sum_(r<48) c_b(r)*n_r >= (c_b(1)/925)*sum_(r<48) v(r)*n_r
                           >= (150*T/925)*c_b(1).
```

Negative credits cause no sign reversal: the first inequality holds rank by rank, and its final multiplier is positive.
Using the fixed mass gives

```text
I_b(n)/T = (14382/48)*phi_b(48) + sum c_b(r)*n_r/(48*T)
         >= (14382/48)*phi_b(48) + (6/37)*c_b(1)/48
          = L_b.
```

Below `b_star`, equality forces all positive non-48 ranks to be one and forces credit equality.
The mass equation then gives the stated profile and divisibility by 37.
It belongs to `R_37`, with `n_0=63500`, `n_1=6`, and `n_48=11086`.
At the boundary, equality allows only ranks `1,32,48`, with `37*n_1+32*n_32=6*T` and the mass equation.

Now take the relaxed T16 profile

```text
n_0=27461, n_32=3, n_48=4792; all other n_r=0.
```

Its count is `32256=2016*16`, mass is `230112=14382*16`, and signed price is `-62272=-3892*16`.
It therefore lies in `R_16` and has exact credit equality.
Its difference from `L_b` has the sign of

```text
(3/16)*c_b(32) - (6/37)*c_b(1)
  = (3/16)*(c_b(32)-(800/925)*c_b(1)).
```

This sign is exactly the sign of `F_32(b)`.
It proves equality at the boundary and strict failure of the relaxed T37 optimum for every `b>b_star`.
We do not claim that this residual profile admits the required whole-helper packing or physical schedule.

## Independent validation

The primary checker enumerates Cartesian count vectors and bounds rational powers with integer roots.
It checks the root bracket, every noncritical inequality, mass, credit, and the relaxed countermodel.
Each root enclosure carries the integer inequality that proves its lower and upper bounds.

The independent checker imports neither the primary checker nor the repository's moment engines.
It derives the bin table by a maximum-score fill recurrence.
It bounds logarithms with a rational atanh series and exponentials with outward-rounded integer arithmetic and an explicit tail bound.
It verifies the normalized ratio inequalities rather than the primary radical expressions.
Both traversals cover their complete finite domains.
[Arithmetic and coverage arguments](METHODS.md) justify their enumeration and interval bounds.

A second analytic argument checks the continuum step.
For `0<A<L`, the ratio `(exp(A*b)-1)/(exp(L*b)-1)` strictly decreases for `b>0`.
Write it as the ratio of the integrals of `exp(b*t)` on `[0,A]` and `[0,L]`.
Its logarithmic derivative is the first interval's weighted mean of `t` minus the second interval's weighted mean.

The latter mean is strictly larger because the added interval `(A,L]` lies above every point of `[0,A]`.
Apply this with `A=log(48/r)` and `L=log(48)`.
The exact endpoint checks then certify the same uniform interval and unique critical crossing.

Re-running a receipt does not supply independent proof.
The distinct enumerations, arithmetic bounds, analytic arguments, and semantic controls address that requirement separately.
This package has no external human review or Lean proof.

## Reproduce and scope

```sh
python3 -B research/t37-support-interval/reproduce.py --out /absolute/new/output
```

Expected final line: `PASS_T37_SUPPORT_INTERVAL_REPRODUCTION`.
The command needs only the Python standard library.
Checks remain active under `-O`; the command preserves existing outputs.
The command does not run the native supplier, global controller, full invoice, or multiplication theorem.

The contribution locates the first failure left open by PR995 and supplies an explicit relaxed competitor on the entire remaining exponent range.
It completes the parameter-domain characterization of the inherited supporting line, independently of the fixed local paid profile.
The new equality case explains the boundary's mechanism: rank 32 joins ranks one and 48.
The practical owner-search exclusion near the selected endpoint already follows from PR995; we claim no additional improvement there.
We claim no kappa improvement, new physical construction, or altered selected frontier.

## Credit and provenance

Chafik Boukhalfa supplies the signed prices and capacity model in PR795/PR890.
Jonathan Capalbo supplies the all-positive-replica rank-one supporting argument and T37 construction in PR942.
Hao Yan supplies the T16 owner-lift lineage.
Jeremy Kothe supplies the PR799 and U8 lineage; the retained sources also credit NewBArch and ColdWitness/icekylinx.
Joel Pulikkan's concurrent PR962 supplies a separate T37 construction and endpoint cross-check.

Charles Bethin's PR850 proves a separate continuum theorem for the fixed T8 inventory.
It does not imply this all-replica theorem.

Concurrent [PR995](https://github.com/CrocSwap/integer-mult-bounds/pull/995) by woklerx publishes the uniform `0<b<=1/3` theorem first.
We inspected its exact proof at `93a8127b990f9755d0c80e729b40c969d6c611e4` before submission.
[PR1000](https://github.com/CrocSwap/integer-mult-bounds/pull/1000) by Eva Ayala / ToikY adds an elementary rational proof near the selected endpoint.
[PR992](https://github.com/CrocSwap/integer-mult-bounds/pull/992) studies integer penalties at the selected endpoint.
These contributions have separate scopes; this package consumes none of their code.

This note adds the sharp uniform interval, its equality boundary, and the explicit relaxed countermodel beyond it.
`SOURCES.json` pins the consumed predecessor records at base `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
All five consumed source hashes remain unchanged at refreshed main `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
The selected PR942 source head is `1960cfa919a0945d0ca4cb14ea96237000037903`.
Charles Bethin prepares this work with substantial OpenAI Codex assistance.
The new files use Apache-2.0; predecessor files and notices remain unchanged.
