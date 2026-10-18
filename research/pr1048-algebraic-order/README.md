# Exact algebraic root ordering for a three-rank profile class

**Independent verification and scoped arithmetic lemma; no new kappa.**

This package independently corroborates Douglas Colkitt's retained PR1048
counterexample and gives a complete algebraic comparator for **unsurcharged**
profiles of width 8, proper child ranks `{1,2,4}`, equal role count and equal
rank mass, with roots strictly inside `0<a<1`. It adds the exact crossing of
the retained example and a distinct-profile, exactly equal-root fixture.
Neither logarithm nor exponential approximations enter the comparator.

The base is `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`; assignment seed **78**
was drawn once from OS randomness. [TASK.json](TASK.json) records the three
candidates, local claim, scope and overlap check. The selected reviewed
conditional kappa at this base is `0.001672660197076918`; it is unchanged.
[SOURCES.json](SOURCES.json) pins the original counterexample, review and
PR1048 disposition, including Git blobs and SHA256 digests. PR1048's reviewed
head is `07730cd8302c378607259a9ad0efb73e0b57a2f2`.

## Statement and proof

Write a profile as `C=(n1,n2,n4; W)`, with nonnegative integer counts and
positive integer `W`. Its normalized moment is

`M_C(a) = [n1 (1/8)^(1-a) + n2 (2/8)^(1-a) + n4 (4/8)^(1-a)] / W`.

Set `t=2^a`. Then `8W(M_C(a)-1)` is the polynomial

`P_C(t) = n1 t^3 + 2 n2 t^2 + 4 n4 t - 8W`.

Require `n1+2n2+4n4 < 8W` and `n1+n2+n4 > W`. Thus `P_C(1)<0<P_C(2)`.
Its derivative is strictly positive for `t>0`, since at least one count is
positive. There is exactly one root `t_C` in `(1,2)` and one moment root
`a_C=log2(t_C)` in `(0,1)`. Ordering these roots is equivalent.

For two profiles A and B with the same W and rank mass, put
`u=n1_A-n1_B` and `v=n4_A-n4_B`. Equal mass gives
`2(n2_A-n2_B)=-u-4v`, hence the identity

`P_A(t)-P_B(t) = t(t-1)(u t-4v)`.

This is a coefficient identity for every such pair, not an inference from
the finite replay. For `1<t<2`, the sign of the moment difference is exactly
the sign of `u t-4v`. Distinct curves cross in that interval precisely when
`u!=0` and `1<c=4v/u<2`, and that crossing is unique.

The exact root comparator returns `sign(a_A-a_B)` as follows:

| Condition | Root-order sign |
| --- | --- |
| `u=0` | `sign(v)` |
| `u!=0`, `c<=1` | `-sign(u)` |
| `u!=0`, `c>=2` | `sign(u)` |
| `u!=0`, `1<c<2` | `sign(u) sign(P_A(c))` |

To prove the last row, evaluate the difference at `t_A`, where `P_A=0`.
Then `sign(P_B(t_A))=-sign(u) sign(t_A-c)`. Strict monotonicity gives
`sign(t_A-c)=-sign(P_A(c))` and
`sign(t_A-t_B)=sign(P_B(t_A))`. The boundary rows follow because `t_A` lies
strictly between 1 and 2. When `u=v=0`, equal mass also fixes `n2`, so the
profiles are identical. A zero in the interior row certifies an exact tie
between possibly distinct profiles.

## Exact fixtures and independent checks

For the retained `A=(0,15,0;4)` and `B=(14,0,4;4)`, both rank masses are 30.
Their polynomial difference is `2t(t-1)(8-7t)`, so the sole interior crossing
is **`t=8/7`**, equivalently `a=log2(8/7)`. The exact rational separator
`t=31/30` gives `P_A=1/30>0` and `P_B=-263/13500<0`. Therefore `a_A<a_B`.
At `a=1/2`, the original unnormalized scores have the opposite preference:
`G_A=15 sqrt(2)<22=G_B`, certified by `450<484`. This corroborates the
existing counterexample; no priority for finding it is claimed.

The additional profiles **`A=(64,0,4;30)` and `B=(56,10,1;30)`** both have
rank mass 80 and vanish exactly at **`t=3/2`**. They have different count
vectors and different total call counts, but the same root `log2(3/2)`.
An interval overlap or an identical-profile special case alone cannot
establish this equality. This is a regression fixture for the stated
unsurcharged contract, not a claim about ties in a production supplier.

[compare.py](compare.py) implements the formula. A separately written
[oracle.py](oracle.py) constructs the moment polynomials directly from ranks,
isolates roots by exact rational bisection and detects shared roots by the
Euclidean polynomial GCD. It imports no comparator or predecessor code and
does not use the factored-difference rule. All decisions use integer/rational
arithmetic; unresolved isolation fails explicitly.

[RESULT.json](RESULT.json) records **24,338** comparisons among **3,099**
profiles, exhaustively covering `W=1..8`, each count `0..8`, the stated strict
root conditions, and every distinct equal-mass pair. This includes 201
interior crossings, with both strict root-order outcomes. The separate tie
fixture exercises exact equality. Seed 78 orders the transcript by SHA256;
it does not sample or reduce the domain. The sweep checks the implementation;
the general statement rests on the proof above, not finite enumeration.

Fifteen rejection controls cover malformed/out-of-domain profiles, unequal
roles or mass, fixed-score substitution, false equality/strictness, a
reciprocal crossing and an omitted rank weight. The last corruption still
has a valid root bracket, demonstrating why bracket existence alone is
insufficient. Three positive controls include refinement of deliberately
coarse overlapping brackets. Four end-to-end tests cover relocation without
Git, changed source bytes, forged root order and incomplete coverage receipts.

## Reproduce and scope

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/pr1048-algebraic-order
```

Expected: `PASS_DYADIC_ROOT_ORDER: 24338 pair comparisons; 15 rejection controls; exact crossing and distinct-profile tie`,
four passing integrity tests, then `PASS_REGISTERED_RESEARCH_PACKAGE`.
The standalone `python3 -B research/pr1048-algebraic-order/verify.py` also
checks live source hashes and exactly recomputes the committed receipt.
The registered wrapper additionally authenticates Git provenance; its full
history requirement is separate from the standalone source-export check.

There is no circuit, frame/owner admission, source-access/restoration charge,
surcharge, arbitrary rank set, unequal-mass comparator, search-optimality
claim, supplier adoption, full cold replay or proof-assistant theorem here.
In particular, adding a count-dependent surcharge can break the tie fixture
and the factored identity. The selected construction's all-size/compiler,
realization, whole-call hosting, precision/tape, analytic and bit H1-H5
obligations remain inherited and unchecked by this contribution.

Nearest related work: Brian Ross's [PR1392](https://github.com/CrocSwap/integer-mult-bounds/pull/1392)
compares at a reference-root interval with surcharge and audits a frozen
transport domain; woklerx's [PR1182](https://github.com/CrocSwap/integer-mult-bounds/pull/1182)
repairs false numerical root brackets; mightyOil's
[PR1254](https://github.com/CrocSwap/integer-mult-bounds/pull/1254) orders twelve
actual T16 packing profiles. Those remain distinct scopes. No pending code
is imported, changed or treated as accepted.

## Open next questions

Can a reference-root comparator recognize exact ties between distinct
profiles under its actual surcharge contract? This matters because a finite
interval can remain unresolved at an equality. A first step is to derive
that contract's residual and adapt the rational-root fixture before testing
an optional equality path. General rank spectra and count-dependent
surcharges block applying this width-eight factorization directly; no
change to PR1392 or its accepted domain is implied. The structured question
is in [TASK.json](TASK.json).

## Credit

Prepared by Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance
in derivation, implementation, verification and writing. No subagents or
independent human review were used. Douglas Colkitt and the maintainers
supplied the original counterexample and its review; flemhhh supplied
PR1048's pricing/search direction. Brian Ross, woklerx and mightyOil receive
credit for the complementary checks above. The retained construction lineage
is credited in the pinned review; no construction result is attributed to
this package. New work is Apache-2.0 under the repository license.
