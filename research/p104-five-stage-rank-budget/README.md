# A 13q lower bound for five commuting full stages

This package proves a **scoped coefficient-space rank bound**. Five distinct
compatible, pairwise commuting full stages in a shortest coupled query root
have total rank at least `13q`. Attainment is unresolved. The contribution is
the five-stage aggregation and its equality conditions, using the credited
predecessor inequalities below. It supplies no new leakage lemma or query
normal form.

Averaging the five inherited four-stage bounds gives only `25q/2`.
The directed leakage rows raise this uniform floor to `13q`; for example,
they exclude total rank 25 at q=2 in every allowed even dimension.

## Contract and result

Let K be a commutative field with characteristic different from two, n >= 4
even, and q >= 1. On nq arbitrary independent coordinates let the rank-q
square-zero queries R_0,...,R_n satisfy

```text
(I - 2R_n) ... (I - 2R_0) = -I.
B_i = (I - 2R_i) ... (I - 2R_0).
```

At five distinct selected sites require idempotents P_i satisfying
`P_i R_i = R_i P_i = R_i`, `[P_i,B_i] = 0`, and pairwise commutation.
The prefix is the actual complete chronological prefix. Ordinary constant
changes of coefficient basis are allowed, including coupling of the q ports.
No assumption that internal coefficient blocks commute is added.

Write r_i = rank(P_i). Then

```text
sum r_i >= 13q.
```

If a selected site is even interior, the stronger bound is `14q`. If there
is no even interior and at most one endpoint is selected, it is `40q/3`.
Integer ranks permit rounding each bound upward.

Equality at `13q` therefore requires both endpoints and three odd interior
sites. Their ranks, in chronological order, must be
`(2q,3q,3q,3q,2q)`. These conditions are necessary, not a construction.

## Cited tools

All mathematical premises in this paragraph are predecessor results, not
reproved or independently certified here. The complete coupled normal form,
the compatible-stage floor `r_i >= 2q`, and the even-interior floor
`r_i >= 4q` are in thu-nmrc's [#6717 proof](../p104-coupled-three-stage-rank-budget/PROOF.md).
CubeJerry's [#6773 note](../p104-four-stage-rigidity/FOUR-STAGE-NOTE.md)
gives the four-stage floor `10q` and the directed inequalities

```text
2e_i + e_j >= 2q                   for distinct odd interior i,j,
2e_i + f_t >= 2q                   for a far endpoint t,
e_i = r_i - 2q,   f_t = r_t - 2q,   e_i,f_t >= 0.
```

The left endpoint 0 is far from odd i >= 3; the right endpoint n is far
from odd i <= n-3. The leakage argument originates in #6717, with ToikY's
#6721 and #6734 providing related verification and one-prefix extensions.
The normal form and image/row method retain Ali Romman's #6398 credit and
the preceding Cinna Davis query/controller lineage. Exact input blobs and
SHA256 pins are in [SOURCES.json](SOURCES.json).

## Proof of the new aggregation

If an even interior is selected, its rank is at least 4q and the remaining
four selected stages have total rank at least 10q. This gives 14q.

Otherwise each selected site is an endpoint or odd interior. Let t be the
number of selected endpoints. It is 0, 1 or 2. Every case starts with base
rank 10q, so it remains to bound the extra ranks.

For t = 0 there are five odd sites. Add both directed inequalities for
each pair to get `e_i + e_j >= 4q/3`. Summing the ten pairs counts each
extra rank four times, giving total extra rank at least 10q/3.

For t = 1 there are four odd sites. At most one can be near the selected
endpoint. Name its extra rank a if present, and otherwise choose any odd
site's extra rank as a. Name the other three extra ranks b,c,d, all far
from the endpoint, whose extra rank is f. One third of the sum of the
three odd-pair bounds involving a gives

```text
a + (b+c+d)/3 >= 4q/3.
```

One third of the sum of the three far-endpoint inequalities gives
`2(b+c+d)/3 + f >= 2q`. Adding proves total extra rank at least 10q/3.

For t = 2, write the three odd sites as i < j < k and their extra ranks
as a,b,c. Site i is far from n, site k is far from 0, and j is far from
both endpoints. The following is an exact nonnegative combination:

```text
(1/2)(2a + f_n >= 2q)
+ (1/2)(2c + f_0 >= 2q)
+ (1/4)(2b + f_0 >= 2q)
+ (1/4)(2b + f_n >= 2q)
---------------------------------
a+b+c + (3/4)(f_0+f_n) >= 3q.
```

Nonnegativity of the endpoint extras proves the 13q bound. For equality,
the unused quarter of each endpoint extra must vanish. Thus f_0=f_n=0.
Each odd site is far from an endpoint, so each of a,b,c is at least q.
Their sum is 3q, forcing a=b=c=q. This proves the stated necessity.

These are inequalities between integer dimensions, viewed in the real
numbers. Their rational multipliers do not divide by 3 inside K. The
argument therefore adds no characteristic restriction to the cited tools.

## What the linear relaxation does and does not settle

In normalized rank variables x_i = r_i/q, the directed rows are
`2x_i+x_j >= 8` and `2x_i+x_t >= 8`. The two-endpoint certificate uses
the four weights displayed above and weight 1/4 on each endpoint floor
`x_t >= 2`. Every rank coefficient becomes exactly one and the right side
is exactly 13. The zero-endpoint certificate weights every ordered odd
pair by 1/12. The one-endpoint certificate weights both directions of
each pair involving a by 1/9 and each of the three endpoint rows by 1/3.
These produce exactly 40/3.

For two endpoints and any three odd sites, the abstract assignment
`x_end = 2`, `x_odd = 3` satisfies all these inequalities, all three-stage
floors 7 and all four-stage floors 10. Thus their linear relaxation has
minimum 13. This assignment is **not** a tuple of projectors. A stronger
uniform floor needs an additional structural implication beyond this
listed system, or a stronger inequality not listed here.

Earlier [#6398](https://github.com/CrocSwap/integer-mult-bounds/pull/6398),
`mixed-projector-root-headroom/PROOF.md`, section 5, already gives total
rank at least 14 for five scalar stages on six fields in characteristic
zero. It excludes three rank-three interiors when both endpoints have
rank two. That stronger, narrower result is not claimed here. Likewise
[#6781](https://github.com/CrocSwap/integer-mult-bounds/pull/6781) gives
the sharp four-field four-stage value `ceil(21q/2)`. Together with the
even-site floor it already implies `4q+ceil(21q/2)` for all five sites
at n=4. The displayed 14q bound is deliberately weaker there. Neither
predecessor is replayed by this package.

## Reproduce and verification limits

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/p104-five-stage-rank-budget/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B research/p104-five-stage-rank-budget/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-five-stage-rank-budget
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-five-stage-rank-budget --check-source-history
```

The absolute path records the local interpreter. A reviewer's CPython 3.12
can replace it. The expected direct marker is `PASS_FIVE_STAGE_RANK_BUDGET`.
The receipt is generated by the verifier's explicit `--write-result` option;
ordinary replay is read-only and binds the package and cited proof hashes.

The verifier checks exact dual sums for every five-site placement at
n=4,6,8,10,12, checks feasible abstract rank assignments in the cases
without an even interior, and rejects six false-certificate controls.
The universal proof is the case analysis above, not this finite coverage.
The checks certify the new aggregation conditional on the cited lemmas;
they do not re-audit those lemmas or verify a physical query word.

All loops have fixed bounds from five sites and n <= 12. Files are capped
at 64 KiB. There is no recursion, dynamic code, subprocess, network or
solver in the verifier. Its checks remain enabled under `-O`. Python's
managed allocations are a Power of Ten rule-3 deviation, bounded here by
fixed fixture dimensions and file sizes; lower-level allocation control
would require a different runtime. Functions remain below 60 lines.
Validation uses warnings-as-errors and the registered normal/optimized
replays. Shared diagnostic configuration is outside this package.

No attainment proof, search exclusion, paid invoice, physical supplier,
new κ, selected-frontier change or complete multiplication theorem is
claimed. Native routing, ownership, compiler, precision/tape and analytic
recovery obligations are outside this coefficient-space result. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

- Is 13q attainable for any even n >= 8 and q >= 1? Start with the forced
  rank pattern above and impose compatibility and the actual prefixes
  exactly. The displayed relaxation cannot decide this. A floating-point
  residual alone would establish neither attainment nor exclusion.
- Can a structural argument improve the uniform lower bound above 13q?
  Start with the two-endpoint equality pattern and seek a coupled analogue
  of the credited scalar six-field obstruction. Arbitrary internal blocks
  must remain allowed. This is not settled by the finite certificates here.

## Credit

New five-stage aggregation and package produced by Nick Petalas.
Predecessor credit is retained above for Ali Romman, thu-nmrc, CubeJerry,
ToikY, Cinna Davis and their query/controller lineage. No predecessor
source text or notice is edited. New work is Apache-2.0.
