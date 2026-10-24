# Positive correlation for overlapping ternary rank-two full guards

This package was produced by Nick Petalas. Apache-2.0.

**Claim type: exact finite certificate with a written counting reduction.**
For the fixed commuting projectors over F3

```text
P = diag(0,1,0,1),   Q = diag(0,0,1,1),
```
exactly **2,409,984 of 24,261,120** complete headers in GL4(F3) pass
both requests' full guards. Their joint fraction is **523/5265**.
Each marginal is **361/1170**, so their covariance is strictly positive:

```text
523/5265 - (361/1170)^2 = 5659/1368900 > 0.
```

A request passes G when the leading principal minors of GPG^-1 or GQG^-1
of orders one and two are both nonzero. This is a fixed, uniform complete
header cover and a fixed pair chosen before the header. The result applies
to every commuting ternary projector pair with joint-sector dimensions
(00,10,01,11) = (1,1,1,1), by simultaneous conjugation.

This supplies an explicit positive-correlation example beyond the orthogonal
and corank-one families. It answers one bounded part of the nonlaminar
full-guard question and gives a new residual-state fixture for state-aware
recursion. No new kappa, supplier admission or multiplication theorem follows.

## Exact residual distribution

After a passing first pivot, each Schur complement is a rank-one idempotent
on F3^3. In the following table S and T are ordered. The middle count is the
number of first split pairs reaching that type. The next column counts
second split pairs passing both terminal guards, out of 234. Multiplication
by 48 gives the passing complete GL3 continuation headers per first split.

| Residual type | First splits | Passing second splits | Full GL4 headers |
|---|---:|---:|---:|
| S = T | 44 | 114 | 240,768 |
| Same image, different kernels | 88 | 78 | 329,472 |
| Same kernel, different images | 88 | 78 | 329,472 |
| ST = TS = 0 | 294 | 44 | 620,928 |
| ST = 0, TS != 0 | 168 | 50 | 403,200 |
| TS = 0, ST != 0 | 168 | 50 | 403,200 |
| Different images/kernels, tr(ST) = 1 | 32 | 54 | 82,944 |
| Different images/kernels, tr(ST) not in {0,1} | 0 | 56 | 0 |
| Total | 882 | | 2,409,984 |

The table's terminal counts are the specialization of Nick Petalas's
[#4240 rank-one pair law](../projector-pair-header-law/README.md).
The new quantities are the initial residual distribution, its weighted
full-guard count and the positive covariance. The verifier computes the
second-split count separately for **every** initial split; its total does
not assume that a residual type is a sufficient invariant or use the
predecessor formula to generate successful events. In particular, generic
residuals occur zero times in this enumerated domain only.

## Counting reduction

1. Write x=e1^T G and y=G^-1 e1. Then xy=1. There are
   (3^4-1)3^3=2160 such pairs. For each, choose W=[y,B], where B is the
   explicit ordered basis of ker x in the verifier. Thus xW=e1^T and
   G0=W^-1 has first row x. Every header with this same split pair has
   the unique form diag(1,K)G0 for K in GL3(F3). This proves the common
   completion factor |GL3(F3)|=11232 and total denominator 24,261,120.

2. For either conjugated request R=G0 P G0^-1 or G0 Q G0^-1, write
   R=[[p,b],[c,D]]. When p is nonzero its Schur complement is
   S=D-cb/p. The leading two-by-two determinant after the remaining
   change K is p times (K S K^-1)[0,0]. Therefore the two full guards
   are equivalent to both initial pivots being nonzero and both
   residual first pivots being nonzero. Standard idempotent Schur
   deletion gives rank one; the verifier also checks nonzero rank and
   S^2=S at every applicable split. This scalar deletion is credited
   to the retained #4228/#4278 lineage.

3. Put a=e1^T K and b=K^-1 e1 in dimension three. There are
   (3^3-1)3^2=234 split pairs ab=1, each with exactly |GL2(F3)|=48
   completions by the same basis argument. Count the terminal events
   by directly evaluating aSb and aTb. The verifier visits all
   2160*234=505440 two-stage split paths. The successful totals before
   the final completion multiplier are 155952 for either marginal
   and 50208 for their intersection. Consequently the full counts
   are 7,485,696 for either marginal and 2,409,984 jointly.

4. All idempotent commuting pairs with the stated four sector dimensions
   are simultaneously conjugate to P,Q. Multiplication of G by a fixed
   conjugating matrix permutes the complete GL4 cover. Thus the count
   depends on that sector profile, rather than the chosen axis labels.

This proof reduces an exact finite enumeration to its explicitly enumerated
finite domain; it does not assert a formula uniform in field size or rank.

## Reproduction and evidence

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/ranktwo-overlap-ternary/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/ranktwo-overlap-ternary/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ranktwo-overlap-ternary
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ranktwo-overlap-ternary --check-source-history
```

The verifier prints `PASS_RANKTWO_OVERLAP_TERNARY` in a generated JSON receipt
binding every package file's SHA256. It writes no files. The registered
normal and optimized runs use explicit exceptions, so -O retains every check.

Besides the complete two-stage split enumeration, the verifier scans all
19,683 ternary three-by-three matrices to obtain GL3. For one original split
in each of the seven occupied residual types, it checks all 11,232 literal
complete headers in the continuation fibre. These **78,624** direct header
checks evaluate the original requests' one-by-one and two-by-two minors
without Schur complements. They corroborate each class's continuation count;
this is not a raw scan of all 24,261,120 GL4 headers.

Reversing the completion kernel basis preserves the residual type for every
one of the 882 jointly admitted first splits. Eight controls cover a singular
matrix, two invalid split pairs, a zero pivot, loss of continuation information
under commutator-only state identification, first-pivot/full-guard confusion,
a missing completion multiplier and the complete denominator.

Power of Ten scope is this standalone verifier. Its dimension is fixed at
four, its field at three, functions are below 60 lines, and it uses no recursion,
subprocesses or runtime-generated code. Every loop is bounded by these fixed
domains; the largest raw scan is 19,683 matrices. Python's managed allocation
requires a rule 3 deviation: the live GL3 list is bounded at 11,232 matrix/inverse
pairs, first splits at 2160 and terminal splits at 234; there is no user-selected
size. A fixed-capacity implementation is a follow-up only if these bounds change.
Warning-strict execution and the repository's package checks provide available
Python diagnostics; no new repository-wide analyzer configuration is introduced.

## Scope, predecessor credit and limitations

This takes the nonlaminar question of Nick Petalas #4240/#4259 and the
state-aware continuation question of **ssafwann #4678**, **Mihir Srivastava
#4689**, and **codyw912 #4735**. Their one-block, binary rank-three profile and
binary transition results retain their credit. **MatShep #4762** supplies the
related all-field factor-invariant framework. None of those results is the
deliverable being rechecked here, and none of their executable code is imported.

Credit Nick Petalas's #4240 terminal law and #4228/#4278 scalar completion/Schur
lineage; **Ryanson Jonathan** for the separate-family full-guard census and
sharpness work; **lee-phys** for dimension work; **Cinna Davis** for the BIT
request context; and **source527**, **commdata2338**, and **Jose Manuel** for
the normalizer lineage. Exact main-source blobs are historical provenance in
[SOURCES.json](SOURCES.json). Their original credit lines remain unchanged.

Canonical base is 624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7.
[TASK.json](TASK.json) marks formal-interface-lemma as changed to this algebraic
side result. The card's old balanced-transfer baseline fails on the current
certificate with KeyError 'bit_lower'; its documented replacement
`research_selected_baseline.py` passes source-binding orientation. Neither
baseline is scientific evidence for this count.

Finite exactness is the claim. Other fields, sector profiles, restricted or
weighted header covers and adaptive requests remain outside scope. Ternary
rank two is within the odd-field algebraic model, but no actual producer,
header selection/emission, physical reads, dirty restoration, stock, dispatch
or complete consumer bill is provided. No selected scientific cold replay,
Lean or Docker run is required or claimed. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

1. Determine an exact field-uniform law for this same four-sector pair.
   This would identify when its positive correlation persists. Start by
   counting the residual-type multiplicities symbolically from sector dot
   products; the missing ingredient is that distribution, rather than the
   already known terminal rank-one laws.
2. Extend a state-aware recursion to one larger nonlaminar profile using
   #4762's factor invariant. First retain actual transition multiplicities
   and compare them with a literal finite sample. A complete higher-rank
   transition law and its cost remain missing.
