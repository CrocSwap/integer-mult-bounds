# Finite completed ordinary supplier for the modern outer

The effective ordinary rate used by the support router is obtained by an
explicit fixed-depth bootstrap, not by declaring the coarse bit endpoint to be
an ordinary algorithm. For the actual DIG8 ledger write
`C=.00168358`, `R=10^-88`, `b=C-R`, `q=C-2R` and
`a_eff=(q+b)/2=C-3R/2`. Choose

```
s=(a_eff+b)/2=C-5R/4,
beta_boot=(b-s)/(2b)=R/(8b),
a_0=384599/10^10,
a_j=(1-s)*s+s*a_(j-1),   j=1,...,31.
```

Then `0<a_0<a_eff<s<(1-beta_boot)*b<b<bit<1/32`.
The exact gap identity in `Recursion.bootstrap_gap` is
`s-a_j=s^j*(s-a_0)`. Exact rational evaluation certifies
`a_30<a_eff<a_31`, with `a_31-a_eff>8*10^-90`.
At every one of the31 stages the retained atom, borrowing, remainder and stock
gaps `s-a_j`, `1-a_j-s`, `1-a_j-s*(1-a_(j-1))`, and `1-s` are strictly positive.
Thus the stronger internal ledger point has a finite sufficient witness; seven
legacy stages alone would not justify it.

For each j construct the completed ordinary algorithm A_j by the retained
PR185/387 stopped-leaf construction at atom width `ceil(e^s)`. Every ordinary
leaf, routing call, peeled atom, bounded leaf and high-part exchange uses only
A_(j-1); coarse recursive children reduce active width. A_0 is the retained
original completed algorithm and never calls a new stage. This is an acyclic
31-level finite program. Its inherited stopped estimate gives the displayed
saving a_j. Complete arbitrary-width chunks, preceding/intervening spectators,
row restoration, and internal high-digit borrowing are preserved at every
return. Extra internal reserves are not asserted to fit the external252
allowance; that allowance remains unused slack under the retained completed
internal-borrowing contract. A fixed31-level composition still has a fixed
finite tape set, independently of input size.

At stage j choose a constant C_j dominating its already fixed primitive,
wrapper, setup and previous-stage constants, and an integer ell_j>=1 with
C_j<2^ell_j. If delta_j is the minimum of the four strictly positive stage
gaps, use
`L_j=ceil(max(1,36/delta_j^2,2*(4+ell_j)/delta_j))` and the preceding completed
algorithm below width `2^L_j`. The resulting next constant can be enlarged
sequentially, as in the retained finite-cutoff proof. No specific unknown
implementation constant is bounded by the example value512, and no infinite
bootstrap or practical cutoff is claimed.

This assembly uses the retained completed ordinary fixed-depth construction
proved in PR185 and extended to arbitrary fixed depth by the same induction in
PR387. Its exact gap, monotonicity and finite reachability algebra is separately
kernel-audited in `Recursion.lean`. The completed all-size computational
interfaces remain the same explicit inherited conditions as elsewhere.

## Exact replay and source binding

From this directory, run

```
python3 -I -O -B ordinary_bootstrap.py --out /absolute/external/ordinary-bootstrap.json
```

The standard-library replay reads the actual `outer/outer/LEDGER.json`, its
endpoint and specification, the owner table, the already checked supplier-price
receipt, and `Recursion.lean`. It checks their hashes, common primitive rate,
bit rate, paid profile, owner binding and DIG8 rate relations. It then recomputes
all31 exact rational stages, all four strict gaps at each stage, the closed
form, the strict stage30/stage31 crossing, and the stronger gap above target.
The complete result must equal `ORDINARY-BOOTSTRAP-EXPECTED.json`.
Output is allowed only outside this package. Default execution writes no files.
Nonprogressing input, seven insufficient stages and a target at the unattained
fixed point are rejected. Checks remain active under Python optimization.

The newly submitted headline is only `kappa=.00168357`. The modern ledger's
stronger internal point is supported by this finite ordinary construction;
seven earlier bootstrap levels must not be cited as its justification. The
31-level count is fixed independently of multiplication input size. No claim
is made that31 is globally optimal for other coarse choices or seeds.

## Supporting sources and credit

Rohan Arun's [PR185](https://github.com/CrocSwap/integer-mult-bounds/pull/185)
supplied the completed ordinary leaf replacement and acyclic bootstrap. Its
reviewed proof is retained in the exact
[PR387 source snapshot](https://github.com/rohanarun/integer-mult-bounds/blob/d9fb9410b1ae6f6ada376a1e7fd12bc176e476ea/research/e8-outer-slack-refinement/bootstrap-sources/research/community-round8-audit/pr185-proof-reviewed.md),
SHA256 `bbac6ec77f315dd76324f4595b8c7a9b0ec719f3903d0c56c61f23990326e8fa`.
The actual [PR185 head](https://github.com/rohanarun/integer-mult-bounds/commit/561d6ecbbeb94a11b67862ccedd32bfcbad2cae0)
is separately recorded for provenance; the reviewed copy just linked is the
supporting text inspected here.

Rohan Arun's [PR387](https://github.com/CrocSwap/integer-mult-bounds/pull/387)
extended the same mechanism to six fixed levels and supplied the explicit
sequential constant/cutoff argument. Its
[pinned proof](https://github.com/rohanarun/integer-mult-bounds/blob/d9fb9410b1ae6f6ada376a1e7fd12bc176e476ea/research/e8-outer-slack-refinement/PROOF.md)
has SHA256 `15997b908604d124d688482db46e58da3117ecf1c176597afb1556a767c073d8`.
The all-fixed-depth induction above is the same finite composition, now with an
explicit31-stage witness for the new supplier. It does not assert that either
earlier source had already audited31 levels or this new numerical point.
Predecessor credit includes Chafik Boukhalfa's coarse suppliers, eumemic's
retained outer engine, icekylinx's wrapper constraints, Zhihao Chen's framework,
and the RaD/hipotures balanced-prefix work, as retained by those source notices.

The new universal gap, interval, monotonicity and finite-reachability lemmas
are in `Recursion.lean` and are separately kernel/axiom audited. This replay
checks finite exact arithmetic and pins; it does not turn the inherited
completed ordinary fixed-tape construction into a Lean theorem. The original
all-size compiler, borrowing/restoration, recovery and analytic conditions
remain explicit. No new oracle or unverified ordinary algorithm is assumed.
