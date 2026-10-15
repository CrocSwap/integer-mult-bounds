# fstar-proof-lemmas-seed3096ed3f

**Proof-level work on open problem F-star (no kappa, no frontier change).** This
package moves the F-star question of `research/root-unit-decoder-lemmas`
(section 7, OPEN) from the witness-level census of
https://github.com/CrocSwap/integer-mult-bounds/pull/2335 toward proof level:
four structural lemmas with exact hypotheses and written proofs (PROVEN below),
an independent stdlib reproduction of the one-copy L8 certificates of
DreamingOfClouds' named instances `tied_min` (12 lines) and `cex_min_1` (19
lines) of https://github.com/CrocSwap/integer-mult-bounds/pull/2111, exact
`cert` values where exhaustive computation is possible, and a targeted falsifier
search beyond the censused domain. **F-star itself is not proved and not
refuted here.** Every claim below is labelled PROVEN or CHECKED; the residue is
spelled out in "What is demoted".

## The object

A `T = 3` exact decoder on `v` lines is `M = sum_{j=1..3} p_j q_j^T` over the
rationals with `M_tt != 0` on every line (`p_j, q_j` are the coordinate columns
over lines; `M_ts = p(t) . q(s)`). Row support `pi(t) = {j : p_j(t) != 0}`,
column support `sigma(t) = {j : q_j(t) != 0}`; both are nonempty and
`D(t) = pi(t) intersect sigma(t)` is nonempty because `M_tt != 0`. An *L8
labelling* is F2 vectors `a(t)` supported in `pi(t)` and `b(t)` supported in
`sigma(t)`, with `K_ts = a(t) . b(s) mod 2`; `cert(M)` is the largest `|S|`
admitting an order with `K_tt = 1` on `S` and `K_ts = 0` at every incidence
`M_ts = 0` with `t` before `s` (`t, s in S`). Definitions and the proven chain
`cost >= sum_j r_j >= cert(M)` are from `research/root-unit-decoder-lemmas`
(merged); this package does not restate their proofs.

**Remark (CHECKED on every instance, and immediate from the definition).**
`cert(M)` depends only on the zero pattern `Z` of `M` off the diagonal and the
supports `pi, sigma`, not on the coefficient values and not on any pairing `B`.
Write `H = {(t,s) : t != s, M_ts = 0, pi(t) intersect sigma(s) nonempty}` for
the *block-incidence digraph* of PR 2111's Lemma SCC, and `Z` for the full zero
digraph; `H` is the part of `Z` that lands inside some block `R_j x A_j`. For a
labelling `K` let `D_K = {(t,s) : M_ts = 0, K_ts = 1}` be its conflict digraph;
a set `S` is feasible with an order iff `K_tt = 1` on `S` and `D_K[S]` is
acyclic (then any order making every `D_K` edge point backward works).

## 1. Lemma SF (support-forced incidences vanish) — PROVEN

> **Lemma SF.** For every L8 labelling, `K_ts = 0` whenever
> `pi(t) intersect sigma(s)` is empty; hence `D_K` is a subdigraph of `H` for
> every labelling. Consequently: (i) `cert(M) >= MAS(H)`, the maximum size of an
> induced acyclic subset of `H`; (ii) `cert(M) = v` whenever `H` is acyclic;
> (iii) `cert(M) >= v - fvs(H)`, where `fvs` is a minimum feedback vertex set.

*Proof.* `K_ts = sum_j a_j(t) b_j(s)`, and `a_j(t) = 0` for `j` outside
`pi(t)`, `b_j(s) = 0` for `j` outside `sigma(s)`, so every nonzero summand
needs `j in pi(t) intersect sigma(s)`, an empty set by hypothesis. Thus `D_K`
is a subdigraph of
`H`. Take the matched-pivot labelling `a(t) = b(t) = e_{c(t)}` with any
`c(t) in D(t)` (nonempty, since `M_tt = sum_j p_j(t) q_j(t) != 0`); then
`K_tt = 1` on every line. For any `S` with `H[S]` acyclic, `D_K[S]` is acyclic;
order `S` with every `H[S]` edge pointing backward (repeatedly take sinks
first). Every `D_K` edge is an `H` edge and points backward, so no constraint
pair is forward with `K_ts = 1`; `S` is feasible. Maximizing over `S` gives
(i); (ii) is (i) with `S = [v]`; (iii) follows from `MAS(H) >= v - fvs(H)`.
`QED`

This is a named-family result: **F-star holds (with `cert = v`) for every
decoder whose block-incidence digraph `H` is acyclic**, and quantitatively for
every instance through `MAS(H)` and `fvs(H)`. CHECKED: on `tied_min` the exact
`MAS(H) = 4`, so the lemma alone is far from tight there (`cert = 11`); the
lemma is a floor, not a characterization.

## 2. Lemma MP (matched-pivot certificate) — PROVEN

> **Lemma MP.** For every map `c: [v] -> {1,2,3}` with `c(t) in D(t)`, let
> `C_i = c^{-1}(i)`. Then `cert(M) >= sum_i MAS(Z[C_i])`. Hence `cert(M) = v`
> whenever `Z` admits a partition into three acyclic classes with each line's
> pivot inside its `D(t)` (in particular when `Z` is 3-dichromatic and all
> `D(t)` are nonempty).

*Proof.* With matched pivots `a(t) = b(t) = e_{c(t)}` one gets `K_ts = 1` iff
`c(t) = c(s)`, so `D_K` is the disjoint union of the `Z[C_i]` over the three
classes. Acyclic subsets of disjoint vertex sets union to an acyclic subset, of
size `sum_i MAS(Z[C_i])`; apply Lemma SF's order argument. If each class is
acyclic the sum is `v`. `QED`

CHECKED on every instance in `CERTIFICATE.json` (the constructed pivot witness
is replayed by the checker on all instances with `v <= 12`).

## 3. Lemma RK (rank-3 structural facts) — PROVEN

> **Lemma RK.** For any `M` of rank at most 3 with nonzero diagonal (in
> particular every exact `T = 3` decoder): (a) the mutual-zero graph `G_0`
> (edges `{t,s}` with `M_ts = M_st = 0`) has no `K_4`; (b) `Z` contains no
> transitive 4-tournament; (c) an incidence with `|pi(t) intersect sigma(s)| = 1`
> is impossible, so every zero pair landing in a block has
> `|pi(t) intersect sigma(s)| >= 2`.

*Proof.* (a) A mutual-zero clique `S` makes `M[S,S]` diagonal with nonzero
diagonal, so `rank M >= |S|` and `|S| <= 3`. (b) If `M_{t_i t_j} = 0` for all
`i < j` in some ordering of four lines, `M[S,S]` is triangular with nonzero
diagonal and rank at least 4. (c) `M_ts = sum_j p_j(t) q_j(s)`; one nonzero
summand cannot vanish. `QED`

(c) is PR 2111's L5, restated for completeness. (a) and (b) restrict what a
falsifier's zero pattern can look like; CHECKED on every searched instance
(`v <= 16`).

## 4. Lemma AN (mod-2 anchor) — PROVEN

> **Lemma AN.** Suppose that after per-total powers of two the factorization is
> 2-integral: all entries of `p, q` lie in `Z_(2)`. Then `a(t) = p(t) mod 2`,
> `b(t) = q(t) mod 2` is an L8 labelling with `K_ts = M_ts mod 2`; in
> particular `K_ts = 0` at every incidence and `K_tt = M_tt mod 2`. Hence
> `S = {t : M_tt odd}` is feasible in any order and
> `cert(M) >= #{t : M_tt odd}`. Under the added hypothesis that at most
> `floor(v/3)` lines have `M_tt` even, `cert(M) >= ceil(2v/3)`, so **F-star
> holds for dyadic decoders with at most one-third even diagonals**.

*Proof.* Reducing `sum_j p_j(t) q_j(s) = M_ts` modulo 2 gives
`sum_j a_j(t) b_j(s) = M_ts mod 2` (all entries are 2-integers); supports
shrink under reduction so the support constraints hold. At an incidence
`M_ts = 0`, so `K_ts = 0`; on `S` all diagonals are 1, so every order works and
`|S| = v - #{t : M_tt even} >= v - floor(v/3) = ceil(2v/3)`. `QED`

The count `#{t : M_tt odd}` depends only on the diagonal of `M`, and the
identity holds for every 2-integral normalization of the factorization, so the
bound is normalization-robust. What Lemma AN does **not** do is classify which
lines can be made odd by changing the normalization: that is exactly the
*tied-minima* obstruction of `research/root-unit-decoder-lemmas` section 7
(lines whose minimal 2-adic valuations among the products `p_k(t) q_k(t)` tie,
where the reduction is isotropic and one-sided repairs are unavailable). This
package does not resolve that question; see "What is demoted".

## 5. Engine and controls — CHECKED

`verify.py` (stdlib only, deterministic). For fixed `a`-labels the completion
over `b`-labels, order and kept set is **exact** by subset DP: `b`-existence
for line `t` against blocker span `U` is a per-line table lookup
(`exists b in F2^{sigma(t)}: a(t).b = 1 and a(s).b = 0 for s in U`), and
`f[T] = OR over t in T of (f[T \ t] and b-exists(t, blockers of T \ t))` over
all subsets. Exact `cert` enumerates all `a`-labelings (`v <= 5`); the witness
search hill-climbs over `a`-labels with exact completion; every stored witness
is replayed by an independent checker (supports, `K_tt = 1`, and the order
constraints recomputed from scratch).

Controls (all in `verify.py`, all required to pass):

1. Three tiny instances (`v = 3`) are computed both by brute force over *all*
   labellings (the definition) and by the engine; the values must agree (3/3).
2. The hand-checkable diagonal decoder `p_j = q_j = e_j` gives `cert = 3`.
3. Corrupted witnesses (a zeroed `a(t)`, a zeroed `b(t)`) are rejected by the
   independent checker.
4. The chain engine is recomputed on PR 2111's stored pairing for `cex_min_1`
   and must reproduce their recorded cost 22 (`10 + 6 + 6`); this validates
   `sum_j rank_F2 B[R_j, A_j]` on real data.
5. The matched-pivot witness constructed from `MAS(H)` is replayed wherever
   `MAS(H)` is computed exactly (`v <= 12`).
6. The proven chain `witness <= cost(B)` is rechecked on every instance with
   both numbers available.

## 6. Named instances (PR 2111) — CHECKED

The one-copy L8 certificates of the named instances are reproduced here by a
different method (exact-completion engine + stored-witness replay), from
byte-identical copies of PR 2111's data files (`data/`, sha256 recorded in
TASK.json evidence):

| instance | v | PR 2111 recorded max one-copy L8 | this package | threshold `floor(2v/3)` |
|---|---:|---:|---|---:|
| `tied_min` | 12 | 11 (CHECKED, recorded: CP-SAT) | witness 11, machine-checked and re-found by the deterministic search | 8 |
| `cex_min_1` | 19 | 18 (CHECKED, recorded: CP-SAT) | stored witness 18, machine-checked replay | 12 |

On `tied_min` the deterministic hill-climb re-finds 11 within its bounded
budget, so the two independent methods agree at 11; combined with PR 2111's
recorded CP-SAT upper bound, `cert(tied_min) = 11` is pinned at both ends
(subject to their recorded, not here re-verified, optimality claim). The same
holds at 18 for `cex_min_1`. Both values are consistent with F-star
(`11 >= 8`, `18 >= 12`) and show `cert < v` is genuinely possible
(`cex_min_1`), which by Lemma MP forces its zero digraph to be non-3-dichromatic.

The chain engine is validated on real data: PR 2111's stored pairing for
`cex_min_1` (`data/cex_min_1.B22.json`) is recomputed here as exactly 22
(`10 + 6 + 6`, matching their record) and is confirmed admissible. The bounded
`B`-search itself finds 20 on `tied_min` and 30 on `cex_min_1`, weaker than the
recorded optima (12 and 22); those numbers are labelled upper bounds.

Exact `cert` values where exhaustive `a`-enumeration terminates: two `v = 5`
instances and one `v = 6` instance from the new-alphabet family have
`cert = v` exactly (engine upper and lower bounds coincide; these upgrade the
census's witness-level claims to exact values on their instances).

## 7. Beyond-census falsifier search — CHECKED (scoped negative)

The census of PR 2335 covers `v = 4..12`, factor entries in `{-2..2}`, three
families, 196 sampled instances. This search goes beyond that domain,
smallest falsifying instance first (`v` ascending). Falsifier criterion: an
explicit admissible pairing `B` (0/1, unit diagonal, ones only where `M`
vanishes) with `cost(B) = sum_j rank_F2 B[R_j, A_j] < floor(2v/3)`, which by
the proven chain would force `cert(M) < floor(2v/3)`. The `B`-search is a
bounded deterministic search (exhaustive only when the admissible-pair count
is at most 12), so the recorded chain numbers are upper bounds and can only
overstate `cert`; a missing low-cost `B` cannot create a false falsifier, but
the search is not an exhaustive non-falsification proof.

| family | domain | instances | falsifiers | min witness ratio |
|---|---|---:|---:|---:|
| entries3 | `v = 4..12`, entries `{-3..3}` | 27 | 0 | 1.000 |
| entries3-big | `v = 13..16`, entries `{-3..3}` | 8 | 0 | 0.867 |
| tied-heavy | `v = 13..16`, 2-adic weighted | 8 | 0 | 1.000 |

The worst witness ratio is 13/15 on an `entries3-big` instance at `v = 15`
(threshold 10), limited by the bounded search budget, not by an observed
certificate drop. The tied-heavy generator deliberately accumulates the named
obstruction: every product `p_j(t) q_j(t)` is even on half the lines (all tied
at level 1), so the mod-2 anchor is isotropic there and the labelling search
carries the full load; all eight tied-heavy instances are witnessed at
`cert = v`. Every instance is witnessed at or above `floor(2v/3)` and every
witness is replayed by the independent checker. Full per-instance records are
in `CERTIFICATE.json` (digest printed by `verify.py`).

## What is proved, what is witnessed, what is demoted

- **PROVEN:** Lemma SF, Lemma MP, Lemma RK, Lemma AN (each with its exact
  hypothesis above). Together with the source package's proven consequence
  (F-star closes every open `T = 3` window), Lemma AN closes the stated
  subfamily: dyadic decoders with at most `floor(v/3)` even diagonals; Lemma SF
  closes every decoder with acyclic `H`; Lemma MP closes every decoder whose
  zero digraph is 3-dichromatic.
- **CHECKED:** the engine controls, the named-instance certificate
  reproduction (`tied_min` 11/12, `cex_min_1` 18/19), the chain-engine
  cross-check at 22, exact `cert` at `v = 5..6`, the structural checks per
  instance, and the declared-domain search (no falsifier).
- **Demoted / OPEN:** F-star for general rational decoders is **not** proved
  here. The residue is exactly: (a) lines that no 2-integral normalization
  anchors odd (the tied-minima/isotropic lines) — Lemma AN handles only the
  even-diagonal count, not their repair or ordering; (b) zero digraphs that are
  not 3-dichromatic (Lemma MP then gives only `sum_i MAS(Z[C_i])`); (c) for
  non-dyadic entries (odd primes in denominators) the mod-2 anchor does not
  apply at all. No "exactly when" or necessity claim is made for any lemma's
  hypothesis: each is sufficient as stated and not shown necessary. The
  `B`-search values are bounded-search upper bounds, not exact minima.

## Open next questions

1. **Order the tied residue.** Can the unanchorable (tied-minimum) lines always
   be ordered, with one-sided repairs, keeping at least `floor(2v/3)` lines?
   Why it matters: Lemma AN reduces F-star to exactly this. First step:
   enumerate tied-heavy decoders at `v <= 8`, classify unanchorable lines by
   valuation-tie type, and test the anchorable count plus greedy ordering.
   Blocker: none structural; needs a dedicated enumeration session.
2. **Dichromatic number of rank-3 zero digraphs.** Is every such `Z`
   3-dichromatic (with pivots inside `D(t)`)? `cex_min_1` (cert 18 < 19) forces
   the answer no at the level of *certificates*; the open question is whether
   `Z` itself can be non-3-dichromatic. First step: compute dichromatic numbers
   of the zero digraphs of the stored instances. Blocker: needs an exact
   dichromatic-number routine beyond `v <= 12`.
3. **Exact chain minima on the named instances.** PR 2111 records
   `cost(tied_min) = 12` and a stored cost-22 `B` for `cex_min_1`; an exact
   minimizer here would pin `cert` between 11 and 12 (and 18 and 22). First
   step: branch-and-bound over admissible pairings seeded from the stored
   pairing. Blocker: longer exact run than one session allows.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -B research/fstar-proof-lemmas-seed3096ed3f/verify.py
python3 scripts/research_package.py --package research/fstar-proof-lemmas-seed3096ed3f --check-only
python3.12 scripts/research_package.py --package research/fstar-proof-lemmas-seed3096ed3f
```

Expected markers include `PASS_FSTAR_CONTROLS`, `PASS_FSTAR_NAMED`,
`PASS_FSTAR_CHAIN_ENGINE`, `PASS_FSTAR_EXACT`, `PASS_FSTAR_STRUCTURAL`,
`PASS_FSTAR_SEARCH` and `PASS_FSTAR_PROOF_LEMMAS`. The registered CPython 3.12
replay prints `PASS_REGISTERED_RESEARCH_PACKAGE
research/fstar-proof-lemmas-seed3096ed3f outcome=completed`. `make` is not
installed on the authoring host; the commands above are the underlying ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain
`cost >= sum_j r_j >= cert(M)` are from the merged package
`research/root-unit-decoder-lemmas` (Douglas Colkitt with OpenAI Codex
assistance lineage). The rank-3 configuration model, the named instances
`tied_min` and `cex_min_1`, their recorded one-copy certificate limits (11 and
18, CP-SAT, CHECKED (recorded)), the stored cost-22 pairing for `cex_min_1`
(`data/cex_min_1.B22.json`), Lemma SCC's block-incidence digraph and L5 are
DreamingOfClouds' work in
https://github.com/CrocSwap/integer-mult-bounds/pull/2111 and
https://github.com/CrocSwap/integer-mult-bounds/pull/2162; `data/tied_min.json`
and `data/cex_min_1.json` are byte-identical copies of their data files (sha256
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` and
`86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`). The
falsifier census this package builds on is Aaron Wang's
https://github.com/CrocSwap/integer-mult-bounds/pull/2335. This package does
not claim their results; the new content is Lemmas SF/MP/RK/AN with their
proofs, the exact-completion engine and its controls, the independent
certificate reproduction, and the beyond-census search.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no independent human review claimed). New work in this package is Apache-2.0.
