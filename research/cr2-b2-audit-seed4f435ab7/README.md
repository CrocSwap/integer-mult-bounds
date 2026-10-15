# CR2/B2 audit: an independent check of Lemma CR2 and Theorem B2, with the MAS term pinned down

**Scoped independent verification; no new bound and no kappa claim.** The selected
record, both suppliers and `upstream/` are unchanged.

This package answers **item 2** of the open independent-check request
[discussion comment 18934590](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590):
independent proofs, gaps or counterexamples for Lemma CR2 and Theorem B2 of
[PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162)
("Characteristic-2 shadows of rank-3 decoders", `research/char2-jets`).
The configuration, statements and license are DreamingOfClouds's; this package
imports no predecessor implementation.

## Source pins

| Item | Pin |
|---|---|
| PR 2162 head | `113a718265c62aec301c5695f4bfb9c421bef7ab` |
| Audited file | `research/char2-jets/README.md`, 25888 bytes, SHA-256 `60beed587a355b6b04e61053fc123fb8ebe5d0d75d9dbd065f24138c55a2e437` |
| PR 2111 head (model source) | `98da76c2839ba38538b510420dec54546ccabf0b` |
| Base main | `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` |

The model (PR 2162 section 1): a configuration is `v` lines with rational
points `p(t)` and lines `q(t)`, `p(t) . q(t) != 0`; an admissible pairing `B`
is a 0/1 matrix over `F2` with unit diagonal and `B_ts = 1` (`t != s`) only
where `p(t) . q(s) = 0`; and `cost(B) = sum_j rank_F2 B[R_j, A_j]` over the
three coordinate supports. `H` is the set of harmonic lines (`|D(t)| = 2` with
the two terms of `p(t) . q(t)` equal), `W` the wild incidences
(`|pi(t) intersect sigma(s)| = 3` with `p(t) . q(s) = 0`), and `F` the lines
with both supports full.

## Proof audit (written re-derivation, each implication checked)

1. **Lemma GR is sound, and its rank comparison holds with equality.** For a
   0/1 matrix `M` and any field `K` of characteristic 2, `rank_K(M) =
   rank_F2(M)`: the entries lie in the prime field `F2` of `K`, and Gaussian
   elimination over `F2` is valid in `K` (equivalently, a maximal nonzero
   minor over `F2` is an odd integer, hence nonzero in `K`). The printed chain
   `rank_K D(p~_j) B D(q~_j) <= rank_K B[R_j, A_j] <= rank_F2 B[R_j, A_j]`
   is therefore correct, with the last step an equality.
2. **Lemma CR2 is sound.** With `N = B ∘ P~Q~^T`, admissibility plus (ii) makes
   `N` diagonal and (iii) makes its diagonal nonzero, so `rank N = v` and
   `cost(B) >= v` follows from GR.
3. **Theorem B2's structural steps check out.** Binomial incidences are
   preserved by `phi` (`x + y = 0` over `Q` gives equal monomials, which cancel
   in characteristic 2); the `phi`-diagonal vanishes exactly on `H`
   (`p(t) . q(t) != 0` rules out the opposite-sign case); a wild edge forces
   the source point and target line to have full support, so every directed
   wild cycle lies inside `F`; and `N[X, X]` is triangular in a topological
   order of `W[X]` with nonzero diagonal for `X` a subset of the non-harmonic
   lines with no wild cycle.
4. **Statement/proof gap in the `MAS` term (the one substantive finding).**
   The triangular argument proves `cost(B) >= |X|` and hence, maximising `X`,
   `cost(B) >= v - |H| - |F| + masV`, where `masV` is the largest
   `A ⊆ F` with `W[A]` acyclic (a *vertex* count). The printed statement
   `cost(B) >= v - |H| - |F| + MAS(W[F])` glosses `MAS` as "maximum acyclic
   subset" of the wild-edge set `W[F]`, which read literally is an *edge*
   count `masE` and is strictly stronger whenever `masE > masV`. The printed
   proof does not imply the edge form. The verifier machine-checks the
   identity `Xbest = v - |H| - |F| + masV` on every instance, where `Xbest` is
   the best bound obtainable from the printed `X`-form argument.

## Machine evidence

`verify.py` re-implements the model independently (exact integers, F2 bitsets,
symbolic monomials for `phi`) and searches for falsifiers smallest-instance
first over a declared deterministic domain: `v` in `4..7`, entries in
`{-2,-1,1,2}`, per-bucket quotas for no-wild, wild-acyclic and wild-cycle
configurations (admissible-pair count `free <= 14`), plus targeted large-free
and dense-wild instances (`free <= 16..17`) in which `masE > masV`. Every
admissible pairing is enumerated exactly, so every reported minimum is exact.

```text
PASS_CR2_B2_AUDIT instances=58 buckets={"no-wild": 24, "wild-acyclic": 24, "wild-cycle": 10}
BOUND i: no violation in declared domain
BOUND ii: no violation in declared domain
BOUND iii_vertex: no violation in declared domain
BOUND iii_edge: no violation in declared domain
SUMMARY tight_iii_vertex=1 tight_iii_edge=2 masE_gt_masV=4
```

Facts machine-checked on all 58 instances: `phi` preserves every non-wild
incidence and no wild one; the `phi`-diagonal vanishes exactly on `H`; every
wild cycle lies inside `F`; the `Xbest` identity above. Controls (all pass): a
two-line fixture with analytically known minimum `2` (positive fixture and
sensitivity of the strengthened `+1` bound), a dense three-line fixture with
all six off-diagonal pairs wild (`masE = 3 > masV = 1`, exact minimum `3`,
tight for the edge form), a full-collapse (`phi0`) control showing where the
harmonic classification matters (48 domain disagreements), and a second
independent rank implementation cross-checked on sampled block ranks. The full
expected summary is frozen in `RECEIPT.json` and compared on every run.

**What this establishes.** In the declared domain, corollaries (i), (ii) and
both readings of (iii) have no falsifier; the vertex form is what the printed
proof gives, and the edge form survived exact testing, twice with equality.
**Not checked:** Lemma VCR2, Corollary J, Theorem T-prime, Lemma F, the split
min-max of PR 2162 section 3, configurations with `v > 7` or larger entries,
and target (A) itself. This is not a proof of (A) and not a theorem audit of
PR 2162 as a whole.

## Reproduce

From the repository root, standard library only:

```sh
python3 -B research/cr2-b2-audit-seed4f435ab7/verify.py
python3 scripts/research_package.py --package research/cr2-b2-audit-seed4f435ab7 --check-only
```

Expected verifier output begins `PASS_CR2_B2_AUDIT` and ends `RECEIPT_MATCH`
(about one to two minutes; the run above is the reference).

## Open next questions

1. **Does the edge form `cost(B) >= v - |H| - |F| + masE` hold in general?**
   It is strictly stronger than the printed proof and survived this domain
   (two tight instances). Why it matters: it would upgrade Theorem B2 (iii)
   without new machinery. First step: extend the dense cross-product family to
   near-dense wild cores at `v = 5, 6` with branch-and-bound over pairings.
   Blocked by the `2^free` exhaustive cost (a complete wild digraph on four
   full-support lines is impossible over `Q^3`, so density must come from
   partial cores).
2. **Is there a wild-cycle configuration violating the vertex form?** The
   vertex form equals the best `X`-form bound, so a violation would falsify
   Theorem B2 itself; none appeared in 10 wild-cycle instances. First step:
   a targeted search over `v = 8` structured cores. Blocked by exact
   enumeration cost past `free ~ 18` without a branch-and-bound or SAT oracle.

## Credit

Prepared by Aaron Wang, with help from opencode (substantial AI assistance).
Statements audited, the model and the configuration families are
DreamingOfClouds's work in PR 2162 / PR 2111 / PR 2125; thanks also to the
PR 2193 and PR 2176 audits that closed items 1 and 4 of the same request.
New work in this package is Apache-2.0.
