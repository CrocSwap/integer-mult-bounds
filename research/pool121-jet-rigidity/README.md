# First-order jet rigidity of the 121-line unit-world pool (#1166 OPEN ENDS item 5b)

**Status: research note / scoped negative result. No κ claim, no supplier or word change.**
(A) at T = 3 (cost ≥ v for every exact three-total decoder) is neither proved nor refuted here.

## What was asked

DreamingOfClouds' OPEN ENDS post on #1166 (item 5b) proposes the #2111 121-line T = 3 pool as a test for new
lower-bound techniques. Its best certificate is MCC 119 against v = 121. The pool consists of all (p, q) with p and q
among the 13 projective vectors of {-1,0,1}^3 and p·q ≠ 0. The definition used is that of #2111
`checks/mcc_cex.py`, with the same line order. This package applies the B-independent first-order jet certificate of
#2162 (Corollary J, built on Lemma VCR2 and Lemma F) to the whole pool and its sub-configurations.

## What was learned (all exact over F2; `verify.py` replays everything)

1. **Rigidity, so Corollary J fails on the pool.** The pool has 2646 incidences. All of them are binomial, so there
   are no wild incidences. It has 30 harmonic lines (|D(t)| = 2). In the unit world every homomorphism
   φ: Q* → K* into a field of characteristic 2 has φ(±1) = 1, because φ(−1)² = 1 forces φ(−1) = 1. So φP and φQ are
   the 0/1 support vectors for every admissible φ, and the system (J1) has the same F2 coefficients for every φ and
   every K. (J1) has **2646 rows, 510 unknowns and F2 rank 266**. The 2v + 3 = 245 explicit *trivial motions* are the
   per-object scalings X(t) = c·1_{π(t)} and Y(s) = d·1_{σ(s)}, plus the torus X_j = Y_j = a_j. They satisfy (J1) and
   span dimension **244 = 510 − 266**. So the first-order solution space is exactly gauge + torus: the pool is
   infinitesimally rigid at the Fano collapse. Every δ′_t with |D(t)| = 2 vanishes on gauge and torus. Hence
   **all 30 of the 30 harmonic lines are immovable, for every admissible φ and every field of characteristic 2**, and
   Corollary J cannot be applied to the pool as a whole (sub-pools: item 4).
   *Scope note (from review):* the pool's incidence digraph is not strongly connected. It has one 70-line strong
   component holding all 30 harmonic lines, plus 51 singleton components, which #2111 Lemma SCC/Peel strip. So the
   real test object is the 70-line core, and cost(pool) ≥ 51 + cost(core). The rigidity statement holds on the core
   (all 30 harmonic lines lie in it); the Q4 comparison below is stated for the whole pool.
2. **Dual witnesses.** `data/flows.json` gives one explicit Lemma F flow for each harmonic line. Each flow is a set
   of 10–14 incidence edges whose (J1) rows sum to δ′_t. As Lemma F predicts, every flow has an even number of edges.
   Checking the flows needs no elimination.
3. **Minimal immovable sub-configurations: exhaustive up to 5 lines, search beyond.**
   - **Exact minimum (exhaustive).** No sub-configuration of the pool with at most 3 lines is jet-immovable. The
     immovable 4-line sub-configurations form **exactly one orbit** under the order-48 signed-permutation group.
     - *Method:* `lib/small.py` tests all 842 520 four-line subsets that contain one representative of each of the
       3 orbits of harmonic lines. Immovability is upward closed and invariant under the group, so this covers all
       subsets with at most 4 lines.
     - *The orbit:* it has 12 members, `data/atoms.json` atom v = 4. The configuration has 8 free incidences, a
       single Lemma F flow using all 8 incidences, and is not CR2 over GF(2), GF(4), GF(8) or GF(16). Its exact
       minimum cost is **5 = v + 1**, with 4 minimisers:

     | t | p(t) | q(t) | p·q |
     |---|---|---|---|
     | 0 (harmonic, immovable) | (0,1,-1) | (0,1,-1) | 2 |
     | 1 | (1,-1,-1) | (1,1,1) | -1 |
     | 2 | (1,-1,0) | (1,0,1) | 1 |
     | 3 | (1,0,-1) | (1,1,0) | 1 |

     It is the smallest jet-immovable unit configuration in the pool. It is far smaller than jf0..2 of #2162
     (v = 9–11, non-unit).
   - **All inclusion-minimal immovable 5-line sub-configurations (exhaustive).**
     - *Method:* `scripts/size5.py` / `lib/small.py` tests all 24 643 710 five-line subsets through the
       harmonic-line orbit representatives. It drops those that contain an immovable 4-subset.
     - *Count:* this leaves 1424 inclusion-minimal immovable subsets, which form **353 orbits**
       (`data/size5.json`).
     - *CR2:* none of the 353 orbits is CR2 over GF(2), GF(4), GF(8) or GF(16).
     - *Exact minimum cost:* C `enumall.c` and the Python enumerator agree. The distribution of cost − v is
       {0: 4, 1: 103, 2: 184, 3: 55, 4: 7}. So **(A) holds on every minimal immovable sub-configuration with at most
       5 lines**, and **4 orbits are tight (cost = v = 5)**. On these four the B-independent jet (Corollary J)
       fails and CR2 is excluded over GF(2^k), k ≤ 4, yet cost = v exactly. Each has 9 free incidences and 2
       harmonic lines, both immovable. The B-dependent jet was checked only on their 6 minimisers (all pass); that
       is a consistency check, not a certificate.
     - **Correction after review (SCC/Peel reduction, not replayed by `verify.py`).** These four tight orbits are
       *not* uncertified. Each contains a unit line (|π| = 1 or |σ| = 1) and has a non-strongly-connected incidence
       digraph, so #2111's proven Lemma SCC / Lemma Peel reduce (A) on them to proper components, which are
       jet-movable by inclusion-minimality; Corollary J then gives cost ≥ v. An independent reviewer script reports
       that the same reduction covers 242 of the 353 five-line orbits and 39 of the 42 stored atoms, and that the
       **111 strongly connected** minimal 5-line orbits all have slack ≥ 1 ({1: 19, 2: 66, 3: 25, 4: 1}). Only
       3 of the 42 stored atoms (and the 4-line orbit) are strongly connected. These reduction counts are reviewer
       evidence, not part of the default replay.
     - *Minimiser counts* below and in the atom table are taken over in-block free entries only; off-diagonal
       entries at D-empty incidences never enter a block (#2111) and are fixed. With them free, each tight orbit
       has 4 minimisers.
     - *The 4 tight orbits*, with pool line indices of one representative each:

     | rep (pool lines) | lines (p ; q) | orbit size | minimisers |
     |---|---|---|---|
     | 3, 10, 86, 105, 113 | (0,0,1;1,-1,-1) (0,1,-1;0,1,-1) (1,0,1;1,-1,0) (1,1,0;1,0,-1) (1,1,1;0,1,1) | 24 | 2 |
     | 10, 38, 54, 73, 82 | (0,1,-1;0,1,-1) (1,-1,-1;0,1,1) (1,-1,0;1,0,1) (1,0,-1;1,1,0) (1,0,0;1,1,1) | 12 | 1 |
     | 10, 30, 86, 105, 111 | (0,1,-1;0,1,-1) (0,1,1;1,-1,-1) (1,0,1;1,-1,0) (1,1,0;1,0,-1) (1,1,1;0,0,1) | 24 | 2 |
     | 10, 30, 86, 105, 116 | (0,1,-1;0,1,-1) (0,1,1;1,-1,-1) (1,0,1;1,-1,0) (1,1,0;1,0,-1) (1,1,1;1,0,0) | 12 | 1 |

   - **Minimal atoms beyond size 4 (search).** The search runs seeded greedy single-pass deletion (seed 43). It
     starts from each flow's support with 40 orders per harmonic line, and from the whole pool with 8 orders.
     Immovability is upward closed, so each output is inclusion-minimal. Together with the exhaustive 4-line orbit,
     the search found **42 orbits** of inclusion-minimal sub-configurations on which Corollary J fails. The greedy
     passes alone did *not* reach the 4-line orbit; that gap is why the exhaustive check was added. The atoms have
     **v = 4 … 10** and 8–17 free incidences, and each has exactly one immovable harmonic line. Every one-line
     deletion of an atom is jet-certifiable.
   - **Properties of every one of the 42 stored atoms:**
     - It is **not CR2** over GF(2), GF(4), GF(8) or GF(16) (exhaustive DFS, vendored #2162 `cr2.py`), so neither
       char-2 certificate is found (CR2 excluded over GF(2^k), k ≤ 4 only).
     - Its exact minimum cost is **v + 1 to v + 5** for the 42 stored atoms. The tight 5-line orbits above were not
       reached by the greedy passes. Two independent enumerations agree on both the minimum and the
       number of minimisers: the vendored C `enumall.c` (generator) and a separate Python enumerator
       (`lib/indep.py`, replayed in `verify.py`). So (A) holds on each of them with slack ≥ 1, and **no counterexample
       to (A) was found**.
     - The **B-dependent** first-order jet (VCR2 with E = supp B, as in #2162 §5) passes on all **1305 of 1305**
       exact minimisers.

4. **Q4, a time-boxed failed search.** Restricting an admissible B of the pool to S gives an admissible B for S, and
   each block rank can only drop. So cost(pool) ≥ cost(S) ≥ |S| for any Corollary-J-certifiable S. Greedy insertion
   (16 seeded orders, replayed by `make_data.py`) found certifiable sub-pools of **103 lines** and nothing larger. A
   1-out/2-in swap pass from a 103-line set found no improvement. That swap pass was a scratch run, not included and
   not replayed: it is recorded evidence only. Two
   such sub-pools are checked:
   - the stored one, which is the pool minus the 17 lines whose point or line is (1,1,0), minus ((1,-1,0),(1,-1,0));
   - the pool minus the 18 lines whose point is (0,1,±1).

   This gives cost(pool) ≥ 103, which is weaker than Theorem U (106) and MCC (119) of #2111. **Exact side
   statement:** the 91 non-harmonic lines are certifiable, but adding any single harmonic line to them makes that line
   immovable.

5. **Higher orders.**
   - **Proposition R** (proved here, from G4): it rules out the uniform order-m version of Corollary J on the pool,
     for every m ≥ 1. See the statement and proof below.
   - The #2162 §5 order-2 test also fails on every one of the 42 stored atoms, including the 25 that are not rigid. For the one immovable
     line t of each atom, the order-2 diagonal Q_t(X1, Y1) = X1(t)·Y1(t) + Σ_{e∈Z_t} X1(t_e)·Y1(s_e) is
     **identically zero** as a polynomial on the first-order solution space V. So for every jet whose incidences
     vanish to order ≥ 3, the diagonal of t vanishes at order 2, over every field of characteristic 2, as for
     jf0..2.
   - 17 of the 42 atoms are rigid as well, including the 4-line one, so Proposition R covers them too.
   - Orders ≥ 3 on the 25 non-rigid atoms were not tested.

   **Proposition R.** Let a unit-world configuration be *rigid*: the (J1) solution space equals the span of the
   gauge + torus motions. The pool is rigid by G4. Let K be a field of characteristic 2, and let
   P~(t) = φP(t) + Σ_{k≥1} ε^k X_k(t) and Q~(s) = φQ(s) + Σ_{k≥1} ε^k Y_k(s) be support-compatible over K[[ε]].
   If every incidence product P~(t)·Q~(s) vanishes to order ≥ m + 1, then every harmonic diagonal P~(t)·Q~(t) also
   vanishes to order ≥ m + 1.

   In particular, no jet of any order m has all incidences of order ≥ m + 1 and all harmonic diagonals of order
   ≤ m. That is the uniform order-m form of Corollary J.

   *Proof.* Induct on k = 1, …, m, assuming X_i = Y_i = 0 for i < k. The order-k coefficient of every incidence is
   then A_e(X_k, Y_k), and it must vanish. So (X_k, Y_k) lies in the solution space over K, which is the K-span of
   the F2 solutions, which is gauge + torus. Write X_k(t) = c_t φP(t) + a∘φP(t) and Y_k(s) = d_s φQ(s) + a∘φQ(s).
   Now apply three changes:
   - replace P~(t) by (1 + ε^k c_t)^{-1} P~(t);
   - replace Q~(s) by (1 + ε^k d_s)^{-1} Q~(s);
   - replace each coordinate p_j by (1 + ε^k a_j)^{-1} p_j and q_j by (1 + ε^k a_j) q_j.

   The torus change preserves every product P~(t)·Q~(s) exactly. The scalings multiply each product by a unit. So
   all valuations are unchanged, as are the supports and the lower-order terms. In characteristic 2 the new
   order-k terms are zero. After step m, P~ = φP + O(ε^{m+1}) and Q~ = φQ + O(ε^{m+1}). Each harmonic diagonal is
   then φP(t)·φQ(t) + O(ε^{m+1}) = |D(t)| + O(ε^{m+1}) = O(ε^{m+1}). ∎

   Proposition R does **not** exclude non-uniform valued realisations around the collapse, as allowed by Lemma VCR2
   with different orders on different lines. It only implies that the minimum harmonic-diagonal order is at least
   the minimum incidence order.

**Reading.** On the pool, the first-order char-2 jet is blocked everywhere by small, local Lemma F flows on 4–10 lines.
It is not blocked by a global phenomenon. Every inclusion-minimal immovable sub-configuration with at most 5 lines, and every
stored atom, still satisfies (A); all but 4 orbits do so with slack, and those 4 are already certified by
#2111 Lemma SCC/Peel plus Corollary J on their components. So the failure belongs to the
certificate, not to (A). Jet failure is **not** evidence against (A).

## Reproduce

```sh
python3 -I -B research/pool121-jet-rigidity/verify.py      # stdlib only, about 60 s; no compiler needed; add --full for ~8 more min
```

`--full` additionally re-runs the 5-line enumeration and its CR2 DFS. This takes about 8 extra minutes. Without
`--full`, `verify.py` checks every stored 5-line orbit: immovability, minimality, distinctness, and exact cost. It
does not re-prove completeness or non-CR2 for those orbits.

Expected output: every line starts with `PASS`, followed by the atom table and the final line
`PASS pool121 jet rigidity: (J1) rank 266 / solution dim 244 (= gauge + torus) / 30 of 30 harmonic lines immovable with Lemma F flows; 42 minimal immovable atom orbits (v 4..10), all non-CR2 (GF(2..16)) with exact min cost >= v + 1, order-2 jets fail on all; minimum immovable size 4 (one orbit); 353 minimal 5-line orbits, all cost >= v, 4 tight (cost = v); Q4 search best certifiable S = 103 < 106 <= 119`.
The exit code is 0. Any failed check prints `FAIL` and exits 1.

To regenerate the data (needs `cc`; deterministic for seed 43):
- `TMPDIR=/some/tmp python3 -I -B research/pool121-jet-rigidity/scripts/make_data.py` takes about 30 s.
- `scripts/size5.py` takes about 9 min; `verify.py --full` took 534 s on a shared 4-CPU machine. All replays used Python 3.14 (VERIFY.json records 3.12 as the declared floor).

**Checks** (`verify.py`):
- V0: hashes of the vendored files.
- G1/G2: the pool, harmonic lines, no wild incidences, and the order-0 collapse.
- G3: (J1) rank, from two code-disjoint implementations. Implementation A (`lib/jet.py`) does bitmask elimination by
  leading bit. Implementation B (`lib/indep.py`) does sparse-set Markowitz elimination and does not import A.
- G4: the gauge + torus dimension identity and immovability.
- G5: the flows.
- G6: the atoms: minimality, CR2 DFS re-run (168 runs), and exact cost recomputed in Python.
- G9: B-dependent jets on the minimisers.
- G10: an explicit nullspace and rigidity. The pool is rigid, and 17 of the 42 atoms are rigid.
- G11: the order-2 test, with `lib/order2.py`. It is checked on all 42 atoms and on all 30 lines of the pool.
- G12: the exhaustive 4-line check.
- G13: the 5-line classification. The default run checks each stored orbit and its exact cost in Python; `--full`
  also checks completeness and non-CR2.
- G7: Q4 and the exact non-harmonic statement.
- G8: positive control. `tied_min` (#2111) consists of 12 pool lines, all of them movable, so Corollary J applies,
  as #2162 Theorem T′ states.

**Negative controls** (`verify.py` asserts that each is rejected):
- N1: a flow with one edge dropped.
- N2: a flow edge replaced by a non-incidence.
- N2: a corrupted pool line. This changes the (J1) rank from 266 to 265.
- N3: a non-homomorphic ψ(−1) = ω ∈ GF(4). It breaks all 2646 order-0 incidences.
- N4: an atom with one line deleted becomes jet-movable.
- N5: if the X1(t)·Y1(t) term is dropped, the order-2 test sees a nonzero form on all 42 atoms. This shows the
  test can detect a nonzero form.

## Scope, inherited assumptions and unresolved obligations

- **Inherited, not re-proved here:** the statements and proofs of #2162 Corollary J, Lemma VCR2, Lemma F, Lemma CR2
  and Theorem B2. #2293 audited CR2/B2 but lists Corollary J as not checked, and this package does not audit it
  either. The vendored model code for the cost function and admissibility is #2111/#2162's `enumall.c`, used as
  written. `lib/indep.py` re-implements the cost independently.
- The rigidity statement covers **Corollary J as stated**: first-order jets at the φ-collapse base point, for every
  homomorphism φ and every characteristic-2 field. Higher orders are covered only by Proposition R, which is the uniform
  order-m form at the same base point, and by the order-2 test on the atoms. Nothing here covers non-uniform VCR2
  realisations, jets around other characteristic-2 base points, or other certificates (MCC, Theorem U,
  B-dependent tests).
- Proposition R and the order-2 reading of G11 are proved in this README. They are not machine-checked; the scripts
  check their finite premises only.
- Minimal immovable sub-configurations are classified **exhaustively up to 5 lines**. Completeness and non-CR2 for
  5 lines are replayed by `--full`. Atoms with 6–10 lines come from a **search**. They are inclusion-minimal but not
  of minimum size, and atoms the greedy passes did not reach are not excluded. "Not CR2" means that the DFS was exhaustive over GF(2), GF(4), GF(8) and GF(16) only;
  larger fields were not tried.
- Q4 is a **failed search**, not an upper bound on what the jet method can certify on sub-pools.
- Finite exact replays are not formal proofs. The rigidity claim (item 1) is a complete finite certificate: a rank
  and an explicit spanning set, checked twice, plus explicit dual flows. It concerns this one configuration only.

## Open next questions

The structured versions are in `TASK.json`.

1. **A direct certificate for the strongly connected immovable atoms** (the 4-line orbit, the 111 strongly
   connected minimal 5-line orbits, and 3 of the 42 stored atoms; all have cost ≥ v + 1, and none is CR2 over
   GF(2^k), k ≤ 4). The 4 tight 5-line orbits are not targets: SCC/Peel plus Corollary J already certify them.
   *Why it matters:* these are the smallest unit-world cases that neither SCC/Peel nor first-order jets nor CR2
   (k ≤ 4) reduce. *First step:* add an SCC/Peel classification to `verify.py`, then try CR2 over GF(32)/GF(64) and
   the #2162 §3 split/perfect-split bound (under audit in #2330) on them. *Blocked by:* nothing; not run here.
2. **Jets around other char-2 base points**, such as partial GF(4) realisations with a different vanishing diagonal
   set. *Why it matters:* the rigidity here is specific to the φ-collapse. *First step:* enumerate the
   incidence-preserving GF(4) base points of the 4-line atom and run (J1)/(J2) around each. *Blocked by:* the order
   bookkeeping of VCR2 for such base points must be written out.
3. **The largest certifiable sub-pool.** *Why it matters:* reaching 106 would recover Theorem U by an independent
   route, though not 119. *First step:* exact search over unions of point-classes modulo symmetry. *Blocked by:* only
   greedy and 1-out/2-in swaps were tried.
4. **Orders ≥ 3, and non-uniform VCR2, on the 25 non-rigid atoms.** Order 2 fails on all atoms, and the 17 rigid
   ones fail at every uniform order by Proposition R. *First step:* extend `lib/order2.py` to order 3 on the
   smallest non-rigid atom. *Blocked by:* the order-3 system is quadratic in the order-1 jet; this needs a
   Gröbner-free formulation.

## Provenance and credit

- Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (priority revision 4; the selected record is unchanged).
- Sources are pinned in `SOURCES.json`:
  - #2162 head `113a718265c62aec301c5695f4bfb9c421bef7ab`: vendored `lib/cr2.py`, `c/enumall.c` and
    `data/tied_min.json`.
  - #2111 head `98da76c2839ba38538b510420dec54546ccabf0b`: the pool definition, re-implemented here.
  - Own iteration-2 PR #2274 `67294e7d`: the tooling pattern.
- Predecessors:
  - **DreamingOfClouds**: #2111 (the pool, MCC 119, Theorem U), #2162 (Corollary J, VCR2, Lemma F, CR2, jf0..2,
    `cr2.py`, `enumall.c`), #2125, and the #1166 OPEN ENDS post.
  - The #1590 / #446 / #595 model authors.
  - **navinor**: #2293 (CR2/B2 audit) and #2272.
  - **RossRichardson**: #2176 (jf0).
  - **petalas**: #2193 and #2206.
- Concurrent work: a sibling local session works on OPEN ENDS item 5a (`cex_min_1`), which is a different object.
  Related open PRs on the #2162 tools inherited here: #2330 (theon199, audit of the #2162 §3 split min-max),
  #2340 (navinor, MAS edge form of Theorem B2(iii) is false) and #2334 (ROTl24, counterexample to the B2
  acyclic-edge strengthening). None concerns the pool or the jet test.
- The SCC/Peel correction and the 70-line core decomposition came from an independent adversarial review in this
  sprint loop.
- Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
  See `NOTICE.md` for the vendored files.
