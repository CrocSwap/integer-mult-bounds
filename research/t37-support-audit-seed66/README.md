# Uniform rational audit of the T37 supporting lemma

**Mathematical audit / independent verification; no new kappa.** PR942's
[ALL-T-PROOF](references/research__complex-t37-owners__ALL-T-PROOF.md) certifies
its signed-dual supporting inequality at one exact complex endpoint. This
package gives a different, elementary proof valid throughout **0 < z <= 1/500**.
Its main arithmetic certificate uses only rational numbers; it imports neither
retained moment engine. The selected endpoint
`0.001664727258740678855773` lies inside this interval. This corroborates the
supporting lemma; it finds no counterexample to the accepted statement.

For all 42 applicable attainable ranks, the normalized strict margin is at
least **24274/28675 > 4/5**. This is a conservative lower bound, not the actual
margin. A separately written fixed-point enclosure gives a lower bound above
3 for every rank, using an exact-fill dynamic program, direct atanh sums and
geometric repeated squaring. Neither implementation computes a new moment
root, replays the outer map or admits a supplier.

## Reproduce

From any working directory, with standard-library Python **3.9+**:

```sh
python3 -I -O -B research/t37-support-audit-seed66/verify.py
```

Expected final line:

```text
PASS_T37_UNIFORM_SUPPORT_AUDIT bins=1163 ranks=42 z=(0,1/500] minimum_margin=24274/28675 no_new_kappa
```

The relative command above assumes the repository root. The package can also
be copied by itself and invoked by absolute path. The default check writes
nothing, checks all four retained source SHA256/Git-blob bindings, compares all
certificate fields with type-sensitive canonical JSON, and runs the separate
implementation. All checks remain active under `-O`. Additional controls:

```sh
python3 -I -O -B research/t37-support-audit-seed66/test_package.py
```

Expected: `PASS_T37_SUPPORT_PACKAGE relocation=1 certificate_regeneration=1 on_disk_corruptions=12 independent_mutations=2`.
`verify.py --json` prints the full audit, controls and independent receipt;
`--write NEW_PATH` regenerates the certificate and refuses existing output.

## Exact statement and dependencies

Use the fixed U8 whole-helper widths `(4,5,7,8,9)`, signed prices
`(-1,-20,-8,-2,4)` and capacity bonuses `(2,4,8,-13)` at capacities
`(8,16,32,48)`. Let `u(r)` be the largest bonus plus helper price among legal
bin count vectors leaving rank `r`, and `v(r)=48*u(r)+13*r`. Define

```
phi_z(r) = r*(73/r)^z,
c_z(r) = 48*phi_z(r) - r*phi_z(48),
lambda_z = c_z(1)/925.
```

The audited obligation is `c_z(r) > lambda_z*v(r)` for attainable
`0 < r < 48`, `r != 1`; rank one is equality. The recursive enumeration visits
all **1,163** legal count vectors across the four capacities, and records a
maximizing witness at every attainable rank. The exact-fill DP independently
reconstructs all 45 values of `u`. The attainable ranks are
`0..41,43,44,48`; ranks `42,45,46,47` are absent. Among the 42 strict obligations,
26 have positive credit and 16 have nonpositive credit.

These are the prices and relaxed family inherited from PR795 and PR890, not
an optimized new inventory. Actual time windows, bin counts, geometry and
physical ownership are relaxed in this lemma. Source constants are extracted
as literals from the retained source using `ast.literal_eval`; its code is
never executed. [SOURCES.json](SOURCES.json) binds every consumed predecessor
file to the exact experimental base and its Git blob.

## Elementary uniform proof

Put `a=log(48/r)`, `b=log(48)` and `K=(73/48)^z`. Both `a,b` are positive.
Then the normalized difference is exactly

```
(c_z(r) - v(r)*c_z(1)/925)/(48*z*K)
 = r*(exp(z*a)-1)/z - (v(r)/925)*(exp(z*b)-1)/z.
```

Integrating `exp(t)` gives
`(exp(z*a)-1)/z >= a` and
`b <= (exp(z*b)-1)/z <= b*exp(z*b)`.
A positive `v` therefore needs an upper bound for the latter expression; a
nonpositive `v` contributes favorably and can be dropped. This is the
sign-sensitive step of the audit.

For `x>=1`, `log(x)>=2*(x-1)/(x+1)`: subtract the right side from the left;
the derivative is `(x-1)^2/(x*(x+1)^2)>=0` and the difference at one is zero.
Moreover,

```
sum_(k=0)^6 4^k/k! = 437/9 > 48,
log(48) < 4,
48^z < exp(1/125) < 1/(1-1/125) = 125/124,
log(48)*48^z < 125/31,        0 < z <= 1/500.
```

The exponential bounds follow from its convergent positive Taylor series:
`exp(4)` exceeds the displayed partial sum; for `0<t<1`,
`exp(t)<sum t^k=1/(1-t)` because the terms from degree two are strictly smaller.
The nonstrict endpoint `z=1/500` retains the strict logarithm bound.

Consequently a valid rational lower bound for each normalized difference is

```
delta_r = 2*r*(48-r)/(48+r) - max(v(r),0)*125/(925*31).
```

[CERTIFICATE.json](CERTIFICATE.json) contains all 42 exact comparisons.
Every `delta_r > 4/5`; its unique minimum is `24274/28675` at `r=2`, where
`u(2)=13` and `v(2)=650`. Thus the stated supporting inequality holds throughout
the entire real interval, rather than at only sampled exponents. This is an
analytic argument supported by exhaustive rational bin arithmetic, not a
proof-assistant theorem or a finite replay claimed as a full theorem proof.

## Transfer to the all-replica relaxation

The fixed inventory independently gives rank mass `14382*T` and signed price
`-3892*T`. Summing the upper bin prices gives the necessary direction
`sum u(r)*n_r >= -3892*T`. Eliminating rank 48, using `u(0)=0` and
`u(48)=-13`, yields

```
sum_(0<r<48) v(r)*n_r >= 150*T.
```

Because `lambda_z>0`, the uniform support inequality implies

```
sum_(0<r<48) c_z(r)*n_r >= (6*T/37)*c_z(1).
```

This holds for nonnegative **real** count vectors satisfying the two necessary
constraints, for every real `T>0`. Equality requires
`n_1=6*T/37`, `n_48=11086*T/37` and no other positive-rank residuals; `n_0` is
unrestricted by this relaxation. For **integer** counts and positive integer
replica counts, equality requires `37 | T`. It does not imply that a bin
assignment, time window or physical execution exists. PR942's separate owner
construction supplies its witness; that construction is not replayed here.

## Concrete negative and boundary evidence

The verifier checks seven mathematical mutations, including an inflated
rank-two credit, wrong rank-one/zero/rank-48 prices, an omitted rank, and
unsupported exponent endpoints. Four exact boundary controls distinguish a
scoped counterexample from failure of the accepted theorem:

- At `z=0`, all `c_z(r)` vanish. Strictness needs `z>0`.
- Reversing the credit inequality admits the integer profile `T=8`,
  `n_48=2397`, all other positive-rank counts zero. It has correct rank mass
  and zero excess cost, contradicting the positive lower bound. Its signed
  total `-31161` is below the required `-31136`, so the correct inequality
  excludes it.
- Replacing negative credit by its absolute value fails the sign-aware bound
  at rank 38. This is a defect in that altered accounting rule.
- Extending the supporting statement to `z=2` is concretely false:
  `c_2(2)-(650/925)*c_2(1) = -1923769/37 < 0`.
  This lies outside the certified interval and is not a counterexample to PR942.

The package controls test seven actual certificate corruptions (including
Boolean/float substitutions and duplicate fields), each of four corrupted
source files, and altered source literals with recomputed content hashes.
They also check an isolated optimized relocation, exact regeneration, existing
output preservation and two mutations in the independent arithmetic.

## Provenance, attribution and limits

Exact base: **407d52ff15b2217b6e22bce44728b4c3907b6515**.
OS assignment seed **66**, adversarial audit track. Three candidates and the
scope/overlap decision are recorded in [CLAIM.json](CLAIM.json). This is a finite
inventory audit, not a randomized search; enumeration stops after every legal
bin vector and every attainable rank is checked. No supplier search is reopened.

At this base the selected conditional kappa is
`1661960547713947/1000000000000000000`, from Jonathan Capalbo's **PR942**
(source head `1960cfa919a0945d0ca4cb14ea96237000037903`), with PR890's U8 and
unchanged PR589/555 bit supplier. The actual construction, selected certificate
and maintainer batch952 review were inspected. Chafik Boukhalfa's **PR795/890**
provide the signed-dual prices and fixed-family equations. PR890 predecessor
head: `4b3bd8cbe8e3e81c44161017c9b72c905a8040a8`. Hao Yan's T16 lineage and Jeremy
Kothe's U8 word remain credited by the retained notices. Concurrent **PR962**
corroborates the T37 construction and retains the moment engines; this adds a
different uniform analytic proof. **PR974** concerns interface/bit-binding budgets
and is a separate obligation. No claim of priority over those results is made.

Final overlap refresh found **[PR995](https://github.com/CrocSwap/integer-mult-bounds/pull/995)**,
published first at head `93a8127b990f9755d0c80e729b40c969d6c611e4`.
Its monotone-quotient proof and two integer cube-root formulations cover the
wider interval `0 < b <= 1/3`. It is stronger in exponent range and is credited
for that concurrent result. This package adds a distinct elementary integral
proof whose main checker evaluates only rational inequalities, without a
cube-root algorithm or retained transcendental engine. Its standalone
fixed-point companion supplies another arithmetic method. No superiority in
range or priority for uniform support is claimed; PR995 code is not consumed.
Concurrent **PR992** quantifies integrality penalties, which this audit does
not reproduce. At refresh main is
`8bddbee377e2f3ce1f1247196c4b290d55767d20`; all four pinned inputs are unchanged.

Prepared by **Eva Ayala / ToikY with substantial OpenAI Codex assistance** in
mathematics, implementation, separate proof review/checking, and writing.
Separate AI implementations are not independent human peer review. New work
is Apache-2.0; retained predecessor text/code keeps its original attribution.
See [NOTICE.md](NOTICE.md) and [VALIDATION.md](VALIDATION.md).

The moment root, all 47 outer constraints, complete supplier/controller,
finite precision invoice, selected cold replay and hosted CI are outside this
audit. All-size/compiler, common-label/mutable-source realization, whole-call
hosting, precision/tape, analytic transfer and bit H1-H5 assumptions remain.
Only this package is added; `upstream/` and the selected frontier are unchanged.
