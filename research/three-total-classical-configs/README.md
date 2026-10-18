# Desargues 10_3 and Pappus 9_3 as three-total (T = 3) decoder atoms: char-2 (CR2) classification

**Status: research note / scoped result. No κ claim, no new bound on T(n).** This package answers OPEN ENDS item 4 of
the #2111 handoff ("untested: classical rich configurations (Pappus, Desargues, Reye, D4 line arrangements) as possible tight
atoms or counterexamples") for **Desargues and Pappus only**, in structured coordinates. It is conditional on
**Lemma CR2 of the open PR #2162**, which is inherited and not re-proved here.

Base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Predecessor pins: PR #2111 head
`98da76c2839ba38538b510420dec54546ccabf0b`, PR #2162 head `113a718265c62aec301c5695f4bfb9c421bef7ab` (vendored files and
hashes in [NOTICE.md](NOTICE.md)). The selected record (`certificates/selected-result.json`, κ = 0.001672660197076918,
#1094) is untouched and unaffected.

Terminology: "no CR2 realisation" below always means **none over GF(2), GF(4) or GF(8)** for a single instance, or **no
frame-universal certificate over GF(2^k), k ≤ 4** for a frame. Lemma CR2 allows any char-2 field, so these are bounded
failed searches, not proofs of non-realisability.

Links: the handoff this answers is
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18932893 and the sprint claim is
https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18936306.

**What is new relative to the predecessors.** In full-support (generic) coordinates the result already follows from
#2162 Lemma CR2 plus char-2 embeddability of the incidence pattern (compare #2111's X2 Hesse experiment). This package's
contribution is the structured, support-restricted frames, the special (zero-richer) Pappus realisations, and the one
coordinate system found where the certificate search fails.

## Question

Model (#2111 §1, from #446/#595): a T = 3 decoder configuration is a list of v pairs (p(t), q(t)) ∈ Z³ × Z³ with
p(t)·q(t) ≠ 0. R_j = {t : p_j(t) ≠ 0}, A_j = {s : q_j(s) ≠ 0}. An admissible B over F₂ has unit diagonal and B_ts = 1 (t ≠ s)
only where p(t)·q(s) = 0. cost(B) = Σ_j rank_F₂ B[R_j, A_j]. Statement **(A)**: cost(B) ≥ v for every admissible B. (A) is open at
T = 3 (#2111 §10). #2162 proves **Lemma CR2**: if there are P̃(t), Q̃(s) over a field of characteristic 2 with
supp P̃(t) ⊆ supp p(t), supp Q̃(s) ⊆ supp q(s), P̃(t)·Q̃(s) = 0 for every in-block incidence, and P̃(t)·Q̃(t) ≠ 0, then (A) holds
for that configuration, for every B.

Hypothesis tested (task card): coordinates in which configuration points or lines form the coordinate triangle are rich in
zeros. The support restriction might block a char-2 realisation, as the anti-Fano configuration `tied_min` does. Such
instances would be where (A) is genuinely open, and they could give new tight atoms or a counterexample.

## Result

1. **Every structured Desargues/Pappus decoder configuration satisfies (A), conditional on CR2** (Desargues: every exact
   realisation over Q; Pappus: the generic signature and the 12 grid-found special signatures, see item 2). The objects are:
   - Desargues 10_3 and Pappus 9_3 over Q. Each is an exact realisation, checked to have exactly the 30 / 27 incidences.
   - Every structured frame. A frame is three non-collinear configuration points sent to e₁, e₂, e₃, or three non-concurrent
     configuration lines sent to the coordinate lines. There are 110 + 110 Desargues frames and 75 + 75 Pappus frames, plus
     the identity coordinates.

   For each frame, `data/universal.json` stores a **frame-universal** char-2 realisation: X(point) and Y(line) over GF(16)
   for Desargues and over GF(4) for Pappus. The supports of X and Y lie inside the frame supports, and X·Y = 0 holds exactly
   when the point lies on the line. Lemma U below turns one such certificate into a CR2 realisation for **every** decoder
   configuration whose pairs are non-incident (configuration point, configuration line) pairs in that frame. This holds for
   any v and allows repeated points or lines. A sample of 740 configurations (v = 6..10, seed 22) is cross-checked:
   the vendored #2162 `cr2.py` DFS (GF(2)/GF(4)/GF(8)) or the a = 0 2-adic test certifies each instance independently.
2. **Which realisations are covered.**
   - **Desargues: every exact realisation over Q.** By Lemma Z, the frame zero pattern depends only on the incidences and
     on any extra collinear point triples or concurrent line triples. Desargues 10_3 cannot have extra triples, because any
     three points include two on a common configuration line (and dually; check 6).
   - **Pappus: realisations with each extra-triple signature found by the parameter grid.** The grid found the generic
     signature and 12 special ones. Each has a single A_iB_iC_i collinearity, a single concurrency ({l,m,pap},
     {A0B1,A1B2,A2B0} or {A0B2,A1B0,A2B1}), or one of each. For every structured frame of every one of these signatures,
     `data/special.json` holds a GF(4) universal certificate.
3. **Field size (side fact).**
   - Desargues frame-universal realisations are exhaustively excluded over GF(2), GF(4) and GF(8) in every frame.
   - A separately coded constructive count (a second method in the same verifier; a local-only pre-submission review, whose scripts are not in this package, reproduced the
     counts 0/0/1344 with its own code and normalisation) confirms this. Since a GF(4)/GF(8) frame certificate would itself
     be an exact 10_3 in PG(2,4)/PG(2,8), this covers every frame, not only the DFS-replayed subset. It fixes O, a₀, a₁ = e₁, e₂, e₃ and enumerates a₂ and μ_i. It finds
     **no exact Desargues 10_3 in PG(2,4) or PG(2,8)**, but finds 1344 in PG(2,16) with a₂ fixed.
   - In the frame (O, a₀, a₁), relaxing exactly one of the 10 "opposite" non-incidences (for example the centre O and the
     axis) makes GF(8) feasible, and relaxing any other single non-incidence does not. This was an exploratory run and is
     not part of the verifier.
   - On the sampled instances the per-instance DFS never needed more than GF(4) (740 Desargues/Pappus samples: 710 GF(2),
     10 GF(4), 20 by the 2-adic test). So GF(16) is a cost of universality only. We did not search the literature for this
     embedding fact; it is likely classical (every planar Desargues configuration is a plane section of the complete
     5-point in PG(3,q)), so it is not claimed as new.
4. **Where the CR2 certificate search fails (the hypothesis, confirmed once).** Of the 2,166 coordinate systems examined
   (every structured frame of the generic and the 12 special realisations, plus 13 identity frames that are all of one
   mixed type: e₁ = l∩m, e₃ = A₀, x = 0 the join A₀B₀), exactly one has no frame-universal certificate over GF(2..16).
   No other mixed frame type was tested.
   - The configuration is the special Pappus realisation `a=(0,1,-1), b=(0,-15,15)`. In it A₀B₀C₀ are collinear and l, m and
     pap are concurrent.
   - Its coordinates are the stored ones. The coordinate line x = 0 is the extra line A₀B₀C₀, e₁ is the concurrency point,
     and e₃ = A₀. This frame is mixed: it uses non-configuration elements.
   - No universal realisation exists there over GF(2..16) (exhaustive). The same realisation in full-support coordinates
     does have one over GF(4) (exploratory check with one integer change of coordinates; not in the verifier). So the obstruction comes from the support restriction.
   - We sampled 2000 decoder configurations in this frame (seed 22, v = 6..10). Of these, 1912 are CR2-certified and
     **88 have no CR2 realisation over GF(2), GF(4) or GF(8)** (written "non-CR2" below, with that meaning only).
   - 18 non-CR2 instances have f ≤ 26. For these, the exact minimum over all 2^f admissible B (vendored `enumall.c`;
     witnesses rechecked in pure Python, f ≤ 18 also exhausted in pure Python) gives **min(cost − v) = 1**. The default
     verifier re-derives the lower bounds only for the 3 instances with f ≤ 18; for the other 15 (f = 19..26) it checks the
     witness (an upper bound) and the lower bound is recorded enumall output, replayed by `--enumall` (which re-runs the same
     vendored C code, not an independent implementation). A local-only pre-submission review (scripts not included) re-enumerated all 18
     minima with its own C enumerator and found no B with cost < v.
     Distribution of (v, f, min): (7,16,11), (7,17,9), (7,18,10), (7,19,10), (8,20,11), (8,21,11), (8,22,11), (8,24,9), (8,24,11), (8,25,12), (8,26,10), (8,26,11), (9,19,13), (9,24,11), (9,24,12) ×2, (9,26,12), (9,26,14); the single cost − v = 1 instance is (v, f, min) = (8, 24, 9). The non-CR2 instances by v: 4 at v = 7, 9 at v = 8, 20 at v = 9, 55 at v = 10, none at v = 6. The skipped f range is 27..45.
   - 70 instances have f > 26 and were skipped (counted, not claimed).

   So, within this bounded search, no counterexample and no tight non-CR2 atom was found. This is a failed finite search,
   not a proof of (A) for this frame.

Counts printed (and asserted, check 8) by the verifier: CR2-certified 2652, no CR2 realisation over GF(2/4/8) with exact
minimum 18, skipped 70; min(cost − v) over the
non-CR2 exact set = 1.

### Lemma U (frame-universal certificate ⇒ CR2 for every pair list)

Let P[i] and L[k] be the frame coordinates of the configuration points and lines. Let X[i] and Y[k] be over GF(2^r) with
supp X[i] ⊆ supp P[i], supp Y[k] ⊆ supp L[k], and X[i]·Y[k] = 0 ⇔ P[i]·L[k] = 0. Take any decoder configuration
(p(t), q(t)) = (λ_t P[i_t], μ_t L[k_t]) with λ_t, μ_t ≠ 0 and P[i_t]·L[k_t] ≠ 0, and put P̃(t) = X[i_t], Q̃(t) = Y[k_t].
- Supports: they shrink as required.
- In-block incidences: if p(t)·q(s) = 0, then P[i_t]·L[k_s] = 0, so X·Y = 0.
- Diagonal: P[i_t]·L[k_t] ≠ 0, so X[i_t]·Y[k_t] ≠ 0.

This gives the hypotheses of Lemma CR2 (#2162), so cost(B) ≥ v for every admissible B. ∎ In full-support coordinates the
support condition is vacuous, so any certificate applies.

### Lemma Z (frame zero patterns are combinatorial)

Take a point frame (u₁, u₂, u₃) and the map p ↦ adj(U)p, where U is the matrix with columns u₁, u₂, u₃.
- Coordinate j of a point p vanishes iff p lies on the line u_k u_l.
- Coordinate j of a line ℓ (ℓ ↦ Uᵀℓ) vanishes iff u_j ∈ ℓ.

Line frames are dual. Consider two realisations with the same incidences and the same extra collinear point triples and
concurrent line triples. They have the same zero pattern and the same zero set of p·ℓ in every frame. So a certificate
checked on the stored realisation applies to the whole class. (Short proof here; the verifier checks the finite inputs.)

## Reproduce

From the repository root (standard library only; tested on CPython 3.14.4 only, syntax is 3.10-compatible; about 1–2 min
on a loaded 4-CPU machine):

```sh
python3 -I -B research/three-total-classical-configs/verify.py
```

Expected: every line `PASS`, then
`counts {'CR2_certified': 2652, 'noCR2_GF2to8_exact': 18, 'skipped': 70, ...}; min(cost - v) over the set with no CR2
realisation over GF(2/4/8) and f <= 26: 1` and `PASS_THREE_TOTAL_CLASSICAL_CONFIGS`. **Default mode certifies exact
minima (lower bounds) only for f ≤ 18 (3 instances); for f = 19..26 it checks witness upper bounds and asserts the
recorded minima.** To replay all 18 minima (including the headline (8, 24, 9) instance), run
`gcc -O2 -o /tmp/enumall research/three-total-classical-configs/c/enumall.c` and add `--enumall /tmp/enumall`
(about 3 min).

The verifier does the following:
- **Check 0:** hash pins.
- **Check 1:** exact configurations.
- **Check 2:** search-free check of all 372 frame certificates, with separately coded GF(2^k) arithmetic in `verify.py`.
- **Check 3:** exclusions. It replays the DFS on a frame subset and runs the separately coded constructive Desargues count with
  a positive control (the count also implies the Desargues exclusion in every frame).
- **Check 4:** the sampled instances.
- **Check 5:** controls.
  - `tied_min` (f = 72) must come out non-CR2 over GF(2/4/8).
  - The #2162 six-line atom must be non-CR2 with pure-Python exhaustive minimum 6 = v.
  - The stored #2162 GF(4) realisation of `cex_min_1` must pass the CR2 checker.
  - **Negative controls** must be rejected: a corrupted certificate entry, a certificate checked against another frame, a
    GF(4) certificate read over GF(8), a corrupted realisation, a zeroed realisation point, a Pappus certificate with two
    line vectors swapped (incidence-only corruption), and a constant assignment for `tied_min`. The zeroed-point and
    constant-assignment controls are rejected for trivial reasons (zero vector; zero diagonal), so they do not exercise
    the incidence logic; the swapped-lines and corrupted-entry controls do.
- **Check 6:** special realisations and the Desargues no-extra-triple lemma.
- **Check 7:** the instances with no CR2 realisation over GF(2/4/8). It re-runs the exhaustive DFS and rechecks every
  witness; lower bounds as described above.
- **Check 8:** asserts the summary counts and min(cost − v) = 1.

The task card asked for `tied_min` to come out "non-CR2 with exact minimum 12". Its f = 72 cannot be enumerated, so the
minimum 12 is inherited from #2111/#2162 (Theorem T′). The verifier checks non-CR2 and uses the six-line atom as the
enumerable tight control.

Regeneration (not needed for verification; deterministic; run under `nice`):
- `scripts/universal_sweep.py` takes about 35 s.
- `scripts/sweep.py 600 BIN 2` is the instance sample.
- `scripts/special_sweep.py` takes about 10 s.
- `scripts/special_instances.py 2000 BIN 900` has a 900 s budget. Recorded run: all 2000 requested samples completed in 168 s, inside the budget.

BIN is `c/enumall.c` compiled with `gcc -O2`.

## Scope, inherited assumptions, unresolved obligations

- **Inherited:** Lemma CR2 and the a = 0 2-adic corollary (#2162, open PR; its README reports a Lean check of the core
  lemma, not re-reviewed here). The model and `enumall.c` come from #2111 (open PR).
- **Covered:** pairs are configuration points with configuration lines. Coordinates are structured frames (or full-support
  coordinates). Realisations are as in item 2. Intersection points of non-configuration lines, mixed frames (only the identity
  frames of the one mixed type above were examined), Pappus realisations with signatures outside the grid, Reye 12_4 and D4 arrangements are **not** covered.
- **Finite certificate vs proof:** item 1 is a per-frame proof (Lemmas U and Z plus CR2) with stored, exactly checked
  certificates. The field-size exclusions are exhaustive finite computations. Item 4 is a **bounded failed search** for
  cost < v. It is not an impossibility theorem. The f > 26 non-CR2 instances are unresolved.
- Coverage of the Pappus special signatures depends on a parameter grid (a₂, b₁, b₂ ∈ [−15, 15]). The verifier checks the
  necessary condition (extra triples ⊆ the three A_iB_iC_i and three line triples). Whether two extra point triples can
  coexist over Q was not settled.

## Open next questions

1. **Do the f > 26 instances without a CR2 realisation over GF(2/4/8) of the special Pappus frame also satisfy cost ≥ v + 1?** This matters because they are
   the only open (A) instances from classical configurations found here. First step: run the #2162 Corollary J jet test, or
   SAT via #2111 `satlib`, on the skipped records in `data/special_instances.json`. Blocker: 2^f enumeration is infeasible,
   and jets can fail (jf0..2 of #2162).
2. **Mixed frames in general.** The single certificate-search failure uses a coordinate triangle built from a non-configuration line and
   point. Enumerate frames from the intersection points of the configuration's lines (and the joins of its points), then
   rerun `universal_sweep`. This matters because zero-rich supports from such frames are where CR2 can fail. Blocker: the
   frame count grows quickly; deduplicate by symmetry (S₅ for Desargues, order-108 group for Pappus).
3. **Reye 12_4 and the D4 arrangement** (the rest of OPEN ENDS item 4). The same frame-universal test applies. First step:
   build exact realisations with `check_config`, then run `universal_sweep.py`. No blocker beyond implementation time.
4. **Why GF(16) for Desargues?** Is "no exact Desargues 10_3 in PG(2,8)" known, and does the forced degeneracy (centre on
   axis) explain it? A sketch suggested by a pre-submission review (not verified here): a planar Desargues configuration is a
   section of the complete 5-point in PG(3,q); in characteristic 2 the 15 forbidden points form a PG(3,2) subgeometry, and
   a plane a·x = 0 avoids them iff a₁..a₄ are F₂-independent in GF(2^h), i.e. iff h ≥ 4. First step: a literature check, then a proof from the μ-parametrisation in `verify.py`. This matters
   only for the size of certificates, not for (A).

## Relation to the bottleneck

Side result on the complex-supplier decoder sub-line. (A) at T = 3 limits what rank-3 root-unit decoders can save (#2111,
#2125). This package removes structured Desargues/Pappus realisations as counterexample candidates. It also locates one
zero-rich coordinate system where the CR2 certificate search fails (up to GF(16)), and finds no counterexample there within a bounded search. κ is unchanged.

## Credit

DreamingOfClouds: #2111 (three-total model, `enumall.c`, `tied_min`, the Hesse X2 experiment, the OPEN ENDS handoff),
#2162 (Lemma CR2, `cr2.py`, CR2 realisations, the non-CR2 atoms) and #2125. #1590 (Lemma B). #446/#595 (cost model).
Adjacent audits: petalas #2193 (anti-Fano) and RossRichardson #2176 (jf0). Concurrent: petalas #2206 certifies the exact
pairing cost 21 of the 19-line configuration `cex_min_1`, a different question; this package uses `cex_min_1` only as a
stored-CR2 control and does not use #2206.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
