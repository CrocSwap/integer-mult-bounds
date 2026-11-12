# Exact polynomial widths from chronological gcd cancellation

This scoped written proof was produced by Nick Petalas. For a symbolic native
rule with W distinguishable rank-m productive targets and P distinguishable
rank-one paid positions, the least chronological compiler widths have the
exact default-height formula

```text
B_n = W^floor(log_m n),  n>=m;       B_n=1, 0<=n<m.
```

At an arbitrary finite height G(n), put H=floor(log_m n), k=min(G(n)+1,H),
s=m^k and S=P^(G(n)+1-k) W^k. The complete cut inventory gives

```text
B_n = lcm(S,B_(n-s)).
```

Thus B_n is exactly the LCM of source totals along one decreasing rank chain.
At adaptive height G(n)=g floor(log_M floor(n/m)), for fixed M>=2 and g>=1,

```text
B_n divides W^floor(log_m n) P^(g floor(log_M floor(n/m))),
B_n <= n^(log_m W + g log_M P).
```

This is a polynomial bound, including parameter ranges where PR4638's general
adaptive envelope is subexponential. The new step retains actual gcd
cancellation. It supplies a concrete positive answer to that package's
gcd-savings opening, without improving its generic semigroup count.
[PROOF.md](PROOF.md) gives all quantifiers, the complete specialized cuts and
the comparison with a separately defined gcd-free recurrence.

At m=2,W=2,P=3,n=1023, the least width is 512. Omitting gcd cancellation in
that recurrence gives 2^45. At fixed height two, the actual rank-10 chain has
source totals 8 and 18 and needs width 72; replacing LCM by maximum fails.
These are compiler widths, not runtime measurements or a new kappa.

## Evidence and reproduction

The standalone checker imports no predecessor code and writes no files. It
enumerates 2,052 forests, including 1,422 empty-root cases, and 139,536 literal
leaf cuts. Distinguishable paid paths and ordered target words independently
recover the claimed source/cut and unit-column formula. Exact rank invoices
also agree. A separate literal-batch compiler checks 27 default width tables.
The recurrence and chain formula agree at 121,440 coordinates in 480 tables
across default, fixed and adaptive rules. Twelve domain rejections and seven
semantic control groups retain explicit checks under optimization.
Four capacity controls exercise the declared logarithm, closed-form, chain
and width-table limits. Three disposable optimized-code mutations reject an
omitted empty-root depth, omitted paid-path multiplicity and omitted gcd.

The finite domains corroborate the written proof. They do not establish its
unbounded quantifiers or certify a physical native supplier. The receipt is
generated on stdout and binds all six package files by SHA256; no receipt is
hand-written or committed.

From the worktree root, with the local CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/homogeneous-gcd-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/homogeneous-gcd-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/homogeneous-gcd-width
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/homogeneous-gcd-width --check-source-history
```

Other machines may substitute their CPython 3.12 path. Only the standard
library is required. Expected markers are PASS_HOMOGENEOUS_GCD_WIDTH,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES. Source pins
are provenance only, so the standalone six-file replay also works without Git.

## Scope, credit and overlap

The source question is codyw912 / [PR4638](https://github.com/CrocSwap/integer-mult-bounds/pull/4638),
Open next question 2 of research/adaptive-chronological-batching. Credit Mihir
Srivastava / [PR4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507)
for least chronological batching; zxv / PR4436 and PR4483 for the default and
arbitrary-height forests; Jacob Alan Sussman for integer compilation; and
Cinna Davis and Ryanson Jonathan for their retained native and flow lineage.
LCM arithmetic and positional notation are classical. No literature-wide
priority claim is made.

Nick Petalas / PR5962 improves semigroup counting, and JoyboyBrian / PR6086
improves adaptive shell counting. This proof uses a different mechanism,
retaining exact cancellation in source multiplicities. The source results
and their numbers are cited premises, not audit or replay deliverables.

Canonical base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8,
selected PR6030. The selected mixed-rank inventory is outside this theorem.
Live open PRs, active Discussions, recent account work, local reservations and
main/merged object and general-form searches were checked. Cached overlap
reported complete pagination for 555 open PRs and 6,599 discussion records;
sparse local notes, arbitrary historical diffs and unpublished work remain
coverage limits. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373389)
records the exact scope. Structured metadata is in [TASK.json](TASK.json).

No physical realization of the homogeneous rule, finite generation-time bound,
practical cutoff, storage extent, precision, stock, outer consumer, supplier
admission or complete multiplication theorem is supplied. All-column native
semantics, ownership/erasure, compiler realization, precision/tape and analytic
recovery remain conditional obligations. Independent human and formal
proof-kernel review are unclaimed. The selected cold replay, Lean and Docker
were not run. New work is Apache-2.0; frozen predecessor files are unchanged.

## Open next questions

- Bind one physically realized native word to this inventory and price its
  complete caller. A useful physical inventory is missing; polynomial width
  alone does not improve the selected exponent.
- Find a valuation invariant retaining gcd savings for one mixed-rank physical
  profile. The one-complement and rank-one-exit reduction fails there, so this
  proof supplies no mixed-rank polynomial width claim.

## Verifier constraints

All functions are at most 45 lines. Loops and iterator products have explicit
finite domains; there is no recursion, subprocess, network, dynamic code
execution, callback or output-file creation. Explicit guards remain active
under optimized Python. Registered replay uses warnings as errors.

Power-of-ten rule 3 deviation: CPython allocates managed integers, sets and
containers during checking. The literal oracle bounds m<=6, W,P<=3, n<=512
and height<=5. Each target-word set has at most 243 members and each paid-path
iterator has at most 243 members; a leaf sweep has at most 729 cuts. Width
tables have at most 1,025 entries. The closed formula caps height at 256 and
rank at 2^256. Package reads are bounded by two MiB per file. These controls
bound live memory in this one-shot verifier; they do not provide an
allocation-free runtime. An embedded fixed-allocation port would need a
separate implementation and capacity review.
