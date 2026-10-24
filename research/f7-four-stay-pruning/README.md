# Sharp high-weight excess at four labels and length ten

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Claim type: scoped combinatorial proof with exact finite corroboration.**
For every simple restored singleton-prefix walk of length ten on `F_2^4`,
each weight-three functional has within-class pair-sum excess at most **11**.
The bound is attained by a universal walk for each such functional. The
all-ones functional has excess exactly **6**. Thus the fixed substituted
budget **13** is sound throughout this domain.

This proves the `(4,10)` case explicitly left unproved in unpaidmoon's
[PR #4148](https://github.com/CrocSwap/integer-mult-bounds/pull/4148),
Open next question 3. Earlier work measured soundness on this domain. The new
contribution is a structural proof, the sharp cap and its equality condition.
No predecessor executable is imported or replayed.

## Definitions

A word `w` of length `L` moves by `q_(i+1)=q_i+e_(w_i)` over `F_2`.
Restoration means `q_L=q_0=0`. Simplicity means the `L` nonclosing prefix
states are distinct. For a nonzero label-basis functional `f`, let `E,O`
be its two classes in the prefix set, of sizes `s,t`. Put

```text
D(A) = {x+y : x,y in A, x != y}
excess(A) = C(|A|,2) - |D(A)|
X_f = excess(E) + excess(O)
base(4,10) = 2 C(5,2) - (2^3-1) = 13.
```

This is the separate-class excess used in #4148. A vector occurring in
both `D(E)` and `D(O)` is counted once in each support. Universality means
the entire prefix set has difference set `F_2^4`.
Every coordinate is active here: ten distinct states cannot fit inside a
proper coordinate subcube, which has at most eight states.

## Proof

**Matching balance lemma.** In any simple hypercube cycle of length at least
four, a functional
omitting exactly one coordinate has class sizes satisfying
`max(s,t) <= 2 min(s,t)`.

Only edges in the omitted coordinate preserve the functional. Those
hypercube edges form a matching, so their endpoints in the cycle are
disjoint. Let `a,b` count preserving edges inside the respective classes,
and let `c` count edges crossing between them. Counting cycle degrees gives

```text
2s = 2a+c,       2t = 2b+c,       s-t = a-b.
2a <= s,        2b <= t.
```

If `s>=t`, then `s-t=a-b<=a<=s/2`, hence `s<=2t`. Interchange the
classes for the other case. Simplicity is used when the preserving edges
are treated as a matching on distinct cycle vertices.

At `L=10`, this gives `s,t>=4`. The unordered split is therefore `(5,5)`
or `(6,4)`. This conclusion uses no universality assumption.

Translate either functional coset into its kernel `F_2^3`; translation
preserves pair sums. Every subset of this eight-point space having at
least five points realizes every nonzero difference. Otherwise, for a
missed nonzero `v`, it contains at most one point from each of the four
pairs `{x,x+v}`, a contradiction. Every four-point subset realizes at
least three differences, obtained by adding a fixed point to the other
three.

For split `(5,5)`, both supports have size seven, so
`X_f=2 C(5,2)-14=6`. For split `(6,4)`, their sizes are seven and at least
three, so `X_f<=C(6,2)+C(4,2)-7-3=11`.

Equality in the latter case holds exactly when the four-point class is
an affine two-dimensional plane. Indeed, translate a point to zero. If
there are only three nonzero differences, the three remaining points
`u,v,z` must obey `u+v=z`, and conversely such a plane has exactly three
nonzero differences. This also proves the equality characterization.

The all-ones functional flips on every edge. Its split is `(5,5)` and
its excess is exactly six by the same support argument.

**Sharpness.** The word `0102301023` and functional mask `0111` have split
`(6,4)`, excess eleven and a full sixteen-element difference set. The
verifier checks this literal witness. Permuting coordinates sends its
omitted coordinate to any chosen coordinate and preserves all properties,
so every weight-three functional attains eleven. The verifier also emits
one literal witness for each mask. This completes the proof.

## Reproduction and evidence

Use CPython 3.12 and its standard library from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/f7-four-stay-pruning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/f7-four-stay-pruning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/f7-four-stay-pruning/verify.py
```

The standalone verifier freshly enumerates all `4^9` labeled prefixes.
Restoration uniquely determines the tenth edge when the ninth endpoint
is a unit vector. Exactly **2,640** simple restored cycles survive, and
all **13,200** high-weight functional cases satisfy the theorem and the
degree/matching identities. No first-occurrence normalization is used.

A separate set-level calculation uses all `C(16,10)=8,008` ten-point
subsets and all five high-weight functionals. It checks the same envelope
on every split admitted by the matching lemma, using ordered differences
instead of the walk checker's unordered pairs. It also checks the
affine-plane equality characterization. This is corroboration of the
proof's set argument, not another implementation of a predecessor census.

Nine controls reject a nonsimple word, a nonrestoring word, an out-of-range
label, a Boolean label, three invalid functionals, cap ten, and removal of
the functional-weight restriction. The last control is the universal word
`0102131213` at mask `0001`, whose excess is **21 > 13**.

The verifier prints a fresh JSON receipt bound to SHA256 of all five
package files. `--output /absolute/external/new.json` creates it exclusively
outside the checkout. `--check-receipt /absolute/external/new.json`
recomputes and compares the full payload. No receipt is hand-written or
stored in the checkout. The verifier and registered checks write no files
by default and need no Git or network access.

## Scope and credit

The catalogue's `census-pruning-audit` card changes scope to a new theorem
answering #4148. The selected-source orientation command passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. The package changes no engine,
seven-label exclusion, supplier, selected record or kappa. The theorem's
cycle and weight hypotheses are explicit; its proof makes no claim for
other lengths or dimensions.

Credit unpaidmoon for #4148's open question, double-transversal theorem
and excess convention. Nick Petalas's #3699/#3733 supply the earlier
measured functional classifications. Nicholas Stone's #2973 supplies the
parity correction, James Reed's #3096 the bit-0 boundary work, and Ross
Richardson's #943 the singleton-prefix model. The source documents are
pinned as provenance in `SOURCES.json`; they are not runtime inputs.

Overlap checks covered live open PR titles and relevant bodies, recent
account submissions, the latest handoff claims and active discussions,
distinctive all-main README terms and merged-title searches. The cached
refresh covered 411 open PRs and 3,925 Discussion records; its local scan
covered 133 of 6,319 tracked notes. The omitted notes, arbitrary diffs and
unpublished work are coverage limits. Direct Git searches covered the
relevant omitted f7 README paths. Search coverage is not a novelty proof.

The verifier uses bounded Python collections and iterator allocations.
This is a managed-runtime deviation from Power of Ten rule 3. There are
at most ten live walk states, sixteen difference values per set and five
histogram rows; the `4^9` prefix and `8,008` subset domains are streamed.
Receipt files are limited to one MiB. Python runtime allocations are not
instrumented. A future expansion must retain explicit domain and memory
bounds. Functions stay below sixty lines, there is no recursion or dynamic
code execution, and explicit exceptions keep checks active under `-O`.
Registered commands enable warning errors. No separate static type checker
is configured for this standalone standard-library script.

## Open next questions

- Does a structural argument settle the `(5,12)` high-weight case in
  #4148 Open next question 3? It would extend a proved soundness boundary.
  Start by applying the matching balance lemma and analyzing the remaining
  `(8,4)` split. The three-dimensional support argument here does not
  settle the four-dimensional kernel case.
- Can a pruning engine profitably use the matching balance constraint at
  a partial chronological prefix? A stronger sound prune could reduce
  future searches. First specify remaining-edge capacities and prove that
  every possible completion satisfies the proposed bound. No engine change
  or performance measurement is supplied here.
