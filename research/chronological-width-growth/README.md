# A quasipolynomial upper bound for chronological batch widths

**Result:** for every fixed integer rule in #4436's default-height flow,
the chronological gcd/LCM widths constructed in #4507 satisfy

\[
\log B_N=O((1+\log N)^{d+2}),\qquad
B_N=\exp(O((1+\log N)^{d+2})),
\]

where `d` is the number of distinct primes dividing the target or paid
**ranks**, and the hidden constant depends on the fixed rule. This answers
the all-rank upper-bound part of [#4507's handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4503).
It improves the inherited `exp(O(N log N))` upper bound for that already
constructed width sequence. It does not assert a matching lower bound,
polynomial width, or a finite-rank improvement beyond #4507.

For the retained raw p7 rule, `d=7`, so this gives
`B_N = exp(O((1+log N)^9))`. The normalized leaf recurrence and all paid
operations are unchanged. **No new kappa or native admission is claimed.**

## 1. Exact scope and predecessor result

Fix positive integer multiplicities `W_k` on target ranks and `P_r` on paid
ranks, with `2 <= k_min <= m=max(k)` and `1 <= r_max < m`. The paid positions
retain their chronological order. At rank `n>=m`, use precisely #4436's
height `G(n)=floor(log_(k_min)(floor(n/m)))` and its source census `S_s(n)`.
Write `S(n)=sum_s S_s(n)`. The base widths are `B_e=1` for `0<=e<m`.

Keep #4507's batching policy: source complements are batched before the
flow; unmatched exits finish separately at their actual parent-round cut.
If `J_n` is this finite list of `(e,q)` rank/count constraints, its formula is

\[
B_n=S(n)\mathop{\mathrm{lcm}}_{(e,q)\in J_n}
       \frac{B_e}{\gcd(B_e,q)}. \tag{1}
\]

Separate occurrences must not multiply the per-cut `q`. #4507 already
proves (1) admissible and locally minimal for its prescribed smaller
library, and proves that normalized leaf cost is unchanged. Those are
predecessor results. This package proves an all-rank bound on (1).

The source hypotheses still include an all-column arbitrary-input native
word, disjoint splitting, priced whole-job adapters, and finite-program
closure with owned initialization/erasure. We use the source's counting
construction; we do not supply or re-audit those physical contracts.

## 2. A depth envelope for every prime valuation

Put `a=(m-1)/m`. Define the integer function

```text
D(n)=0                         if 0<=n<m,
D(n)=1+D(floor(a*n))            if n>=m.
```

Every recursive rank in `J_n` is at most `floor(a*n)`. Indeed, source
complements have `e=n-s` with `s>n/m`, and actual exits have
`e<=r_max*n/m< n`. Since `r_max<=m-1`, both bounds imply the claim.
This uses the actual source and exit inequalities of #4436 section 2,
including its premature exits. Mere strict descent `e<n` would not suffice
for the logarithmic-depth conclusion.

The map `n -> floor(a*n)` is increasing. Its hitting time `D` is therefore
nondecreasing, and each recursive edge satisfies `D(e)<=D(n)-1`.
Also, iteration is at most `a^j*n`; hence for `n>=m`,

\[
D(n)\le 1+\left\lfloor
  \frac{\log(n/m)}{\log(m/(m-1))}\right\rfloor=O(1+\log n). \tag{2}
\]

For fixed `N>=m`, let `L_N=lcm{S(j): m<=j<=N}`. For **any prime** `ell`,
the exact valuation of (1) is

\[
v_\ell(B_n)=v_\ell(S(n))+
 \max_{(e,q)\in J_n}\max(0,v_\ell(B_e)-v_\ell(q)). \tag{3}
\]

Strong induction, starting with zero valuations of the base widths, gives

\[
v_\ell(B_n)\le D(n)v_\ell(L_N),\quad
B_n\mid L_N^{D(n)}\quad(0\le n\le N). \tag{4}
\]

The induction step bounds every child valuation by
`(D(n)-1)*v_ell(L_N)` and the added source valuation by `v_ell(L_N)`.
Taking maxima never adds sibling valuations. This is the benefit of the
LCM recurrence. No monotonicity or nesting of `B_n` is assumed.

## 3. Only polynomially many logarithmic-scale source states

Let `Pi` contain every prime dividing a rank in either fixed alphabet,
and put `d=|Pi|`, `M=floor(N/m)`. A positive integer is called
`Pi-smooth` here if all its prime divisors lie in `Pi`; 1 is included.
Let `H(M)` be the set of such integers at most `M`.

**Source-state lemma.** For any `n>=m`, put `c=floor(n/m)` and let `t`
be the largest `Pi-smooth` integer at most `c`. The complete unreplicated
flow, and in particular `S(n)`, agrees with the flow at ambient rank `m*t`.
This statement concerns the flow before adding the rank-`n-s` complements;
those complement ranks can still change as `n` changes.

**Proof.** The flow's predicates use the cutoff `c` and height `G` only.
Height changes at powers `k_min^j`, all in `H`. Within one height, each
class has an ordered paid path with product `rho`, and each target point
has product `c(b)`. Presence is the predicate
`rho*c(b)<=c`. Child presence has the same form, with one more paid factor
and one fewer target factor. Every threshold is thus an integer product of
target and paid ranks, hence is `Pi-smooth`. Target multiplicities,
ordered-path multiplicities and Pascal matching counts are fixed between
these thresholds. The root sources, absent-parent sources, matched jobs,
unmatched exits and their counts are consequently unchanged. Pruning an
empty class introduces no new threshold. There is no threshold between
`t` and `c`, and height agrees too. This proves the lemma. QED.

We use a superset of the actual thresholds: not every smooth number must
occur as a flow threshold. In particular,

\[
\{S(j):m\le j\le N\}=\{S(mt):t\in H(M)\},\qquad
|H(M)|\le\prod_{p\in\Pi}(1+\lfloor\log_p M\rfloor). \tag{5}
\]

The cardinality bound simply counts nonnegative prime-exponent vectors
and drops their joint product constraint. It needs no prime-distribution
estimate. **Rank primes are not width primes.** Source counts can have new
prime factors; (3)-(4) apply to all of them through `L_N`.

## 4. Explicit all-rank bound

Let `W=sum W_k`, `P=sum P_r`, `h=G(N)`, and

```text
C_N = W*(W+P+1)^(h+1),
K_N = product_(p in Pi) (1+floor(log_p(floor(N/m)))).
```

The source's untruncated unit census gives
`U(n)<=sum_(j=0..G(n)) P^j W^(G(n)-j)` and `S(n)<=W*U(n)`.
Therefore `1<=S(n)<=C_N` for `m<=n<=N`. Combining (4)-(5),

\[
B_N\mid L_N^{D(N)},\qquad
L_N\le\prod_{t\in H(M)}S(mt)\le C_N^{|H(M)|}\le C_N^{K_N},
\]
\[
\boxed{B_N\le C_N^{D(N)K_N}
       \le 2^{D(N)K_N\lceil\log_2 C_N\rceil}.} \tag{6}
\]

For a **fixed** rule, `D(N)=O(1+log N)`, `log C_N=O(1+log N)` and
`K_N=O((1+log N)^d)`. Equation (6) proves the announced bound. The
constants and `d` are not uniform over rules whose ranks or multiplicities
grow with `N`. The theorem is a sharper asymptotic upper bound, not a proof
that the actual width has this growth order.

For raw p7, the rank primes are `{2,3,5,7,11,19,41}`. At `N=1000`,
the conservative binary exponent in (6) is 303,840; the actual width has
2,524 bits, as already reported by #4507. The new bound is deliberately
loose and does not improve that finite witness. Its value is its all-rank
growth guarantee. Base ranks below `m` have width 1 separately.

## 5. Exact evidence and controls

The written argument proves the universal conclusion. Finite checks test
its source binding and failure modes; they do not extrapolate a theorem.

`verify.py` executes the authenticated, unmodified #4507 `batches.py` to
obtain the actual source flows and width sequence. It does not call that
reuse an independent flow implementation. The new `growth.py` separately
computes prime valuations, prime-product intervals and the depth envelope.
All comparisons use integers; every retained RESULT.json field is compared.

| Fixed flow | Maximum compiled rank | Rank primes | Actual width bits | All-rank conclusion |
| --- | ---: | --- | ---: | --- |
| `{2:1,5:1} <- {1:2,4:1}` | 100 | 2, 5 | 42 | `log B_N=O((1+log N)^4)` |
| `{2:4,3:1} <- {1:6,2:2}` | 100 | 2, 3 | 88 | `log B_N=O((1+log N)^4)` |
| Raw p7 | 1,000 | 2, 3, 5, 7, 11, 19, 41 | 2,524 | `log B_N=O((1+log N)^9)` |

The replay covers 1,074 nonbase ranks and 49,474 actual batch constraints:
the valuation recurrence equals the existing width at every rank; all
children satisfy the stronger fractional rank descent; every valuation is
within (4); and sampling the prime products gives exactly the source LCM
obtained from all ranks. Final width hashes reproduce the pinned receipt.

There are 832 cutoff cases: both toys and p7 through cutoff 256, and a
paid-prime fixture through 64. Complete flow records agree at the first
and last ambient rank of each floor-cutoff interval and with the previous
smooth representative. Of these, 642 compare a cutoff with a **strictly
smaller** smooth representative, so the check is not only identity cases.

Ten rejection controls include these concrete failures:

- Omitting paid prime 3 for targets `{2:1,5:1}`, paid `{1:2,3:1}` wrongly
  identifies cutoffs 2 and 3. Their source counts are 4 and 5 respectively.
- Restricting width primes to rank primes fails immediately: the `{2,3}`
  target fixture has `B_3=5`.
- Dropping depth from (4) fails at `n=7` in the first toy: `B_7=4` but
  the source LCM through rank 7 is 2.
- Omitting gcd cancellation changes that toy's exact `B_22` from 896 to
  1,792. This would remain a looser upper bound, but is not equation (3).

Other controls reject noncontracting child ranks, zero batch counts,
out-of-contract rules, a composite claimed prime, and omission of the
source multiplier. No input-validator control is a substitute for the proof.

## 6. Reproduction and provenance

Python 3.12, standard library only, from the repository root:

```sh
python -B scripts/research_package.py --package research/chronological-width-growth
python -I -O -B research/chronological-width-growth/verify.py
python -B scripts/check_research_commit.py --package research/chronological-width-growth --check-source-history
```

Normal and optimized registered replays are declared in VERIFY.json.
Direct replay is self-contained and needs no Git or network. `--write` is
an authoring command only; registered replay never rewrites the receipt.
The five exported predecessor files are authenticated by Git blob and
SHA256 before execution. VENDOR.json binds them to canonical main
`f626db5c3a3d781d8f7695038776c621651f75e1`; SOURCES.json pins that main's
catalogue, selected record and original files as historical provenance.
No frozen predecessor is changed.

This takes the explicit #4507 handoff, changing the `independent-moment`
card from invoice audit to all-rank compiler width. The scope is recorded
in TASK.json. #4519 already independently recounts the finite widths;
#4476 checks the older nested construction, and #4521 its expanded counts.
#4483 changes the height and convergence policy. None is represented here
as missing finite coverage or as a premise establishing this new bound.
Canonical coordination is the [claim in #4503](https://github.com/CrocSwap/integer-mult-bounds/discussions/4503#discussioncomment-19117802).

Initial overlap covered all 5,860 tracked top-level note paths after sparse
materialization, 355 open PRs, and 3,470 Discussion records, with reported
complete remote pagination at 07:48-07:50 UTC on October 22, 2026.
Closed PRs were covered only by local notes/ledger and targeted GitHub
search. This is bounded text coverage, not every historical diff or proof
of novelty. Submission freshness is recorded in TASK.json.

The orientation-only baseline stopped on sparse-omitted
`research/kappa-rebuild/CLAIM.json`; no baseline PASS is claimed. Package
validation is separate. On CPython 3.12.0 / Windows, the registered ordinary
and optimized replays pass (about 12 seconds together). An isolated copy
passes with `-I -O -B`, Git absent from PATH and socket creation disabled;
its files remain unchanged. Separate source-byte and receipt corruptions
reject, as do mutations omitting paid breakpoint primes or collapsing the
depth factor. The committed 14-file export also passes integrity checking
and an isolated optimized replay with Git unavailable, socket creation
disabled and unchanged bytes. Committed-byte preflight passes. The optional
source-history preflight requires full Git history and did not run in this
shallow checkout; all source pins are at this branch's canonical-main base.
These are author-side tests, not an independent reviewer. No full selected
cold replay, formal proof kernel, independent human review or
native/physical/outer admission is claimed.

## Open next questions

1. **Can actual source valuations improve the exponent `d+2` or the finite
   constants?** This would improve resource estimates beyond a loose
   existence bound. Start with `v_ell(S(mt))` on actual transition points,
   retaining repeated visits along contraction paths. A uniform argument
   and a matching lower bound remain absent; merely extending finite
   plots cannot establish the answer.
2. **Does a comparable source-state argument apply to #4483's changed-height
   compiler?** That would connect the width estimate to its stronger leaf
   theorem. First pin its height rule and inventory and identify every
   rank-dependent predicate. This package does not verify that different
   policy, so it supplies no transferred bound for it.

Neither question authorizes an automatic search campaign. Stop at the
bounded source-state/valuation obligation. A width bound is not a bound on
the time to generate every smaller program; native realization, complete
storage, precision and tape costs still require their own evidence.

## Credit

Jacob Alan Sussman supplied the integer lockstep compiler. zxv supplied
#4436's overlapping direct flow, rank bounds, source-count ceiling and
original LCM freedom. Mihir Srivastava's #4507 supplied the chronological
gcd/LCM policy and smaller finite width construction. Cinna Davis /
1337isnot1337 supplied the raw p7 rule. Ryanson Jonathan / pinterbanget
supplied #4456, #4476 and #4519's independent checks; the retained native
and outer lineage remains credited in the exported source notes.

Prepared for **Mihir Srivastava / mihir-s-05 with substantial OpenAI Codex
assistance** in proof development, implementation, verification and writing.
No subagents or independently launched reviewer were used. New work is
Apache-2.0; exported sources retain their original notices.
