# fstar-cancellation-lines-seed80d69336

**Residue (i-prime) of open problem F-star: the cancellation lines, and the
corrected dyadic corollary (no kappa, no frontier change).** Open problem
F-star of `research/root-unit-decoder-lemmas` (section 7, OPEN) asks whether
`cert(M) >= floor(2v/3)` holds for every exact 3-total rational decoder
`M = sum_{j<=3} p_j q_j^T`. [PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869)
collapsed the old entry-class residue and renamed what remains to
**(i-prime) the cancellation lines** `{t : v_2(M_tt) > gamma}` and (ii) the
zero digraphs. This package takes (i-prime), the last named residue thread:
the case where more than `floor(v/3)` lines are cancellation lines, so the
mod-2 anchor is short of the threshold and only structure can carry the rest.
It settles that case on both canonical fixtures, isolates the residual
obstruction precisely, and searches the full 1..v cancellation-line axis
smallest-first. It also repairs the normalization gap that PR 2869 found in
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717)'s dyadic
corollary sentence (the CORRECTIVE part; a corrective comment is posted on
PR 2717). **F-star itself is not proved and not refuted here.** Every claim
below is labelled PROVEN, CHECKED or DEMOTED.

## The object

A `T = 3` exact decoder on `v` lines is `M = sum_{j=1..3} p_j q_j^T` over the
rationals with `M_tt != 0` on every line. Row support `pi(t) = {j : p_j(t) != 0}`,
column support `sigma(t) = {j : q_j(t) != 0}`, `D(t) = pi(t) intersect sigma(t)`
(nonempty). An *L8 labelling* is F2 vectors `a(t)` supported in `pi(t)` and
`b(t)` supported in `sigma(t)`, with `K_ts = a(t) . b(s) mod 2`; `cert(M)` is
the largest `|S|` admitting an order with `K_tt = 1` on `S` and `K_ts = 0` at
every incidence `M_ts = 0` with `t` before `s` (`t, s` in `S`). The proven
chain `cost >= sum_j r_j >= cert(M)` is from the merged
`research/root-unit-decoder-lemmas` package; this package does not restate its
proof. **F-star** is `cert(M) >= floor(2v/3)` for every exact 3-total rational
decoder (the source states the stronger ceiling form `ceil(2v/3)`).

For a fixed factorization let `c_j = min_t v_2(p_j(t)) + min_s v_2(q_j(s))` be
the 2-adic content of total `j` (Lemma SC of PR 2869), `gamma = min_j c_j`,
`S_gamma = {t : v_2(M_tt) = gamma}` the anchor reach and `C = {t : v_2(M_tt)
> gamma}` the **cancellation lines** (Lemma SG of PR 2869: `cert(M) >= |S_gamma|`
after one global rescaling, and no mod-2 anchor of any normalization of this
factorization marks a line outside `S_gamma`). The anchor alone settles F-star
whenever `|C| <= v - floor(2v/3)`; this package is about the complement.

## 1. Lemma CT: what a cancellation line is, exactly — PROVEN

For line `t` define its **tie number** `tau(t) = #{j : v_2(p_j(t) q_j(t)) = gamma}`
(the number of totals attaining the global content floor at `t`; invariant
under every per-total rescaling, since `v_2(p_j(t) q_j(t))` and `c_j` both
are).

> **Lemma CT.** (a) `v_2(M_tt) = gamma` if and only if `tau(t)` is odd, and
> `v_2(M_tt) > gamma` if and only if `tau(t)` is even; so the cancellation
> lines are exactly the even-`tau` lines, with `tau(t)` in `{0, 2}`. (b) Every
> total counted by `tau(t)` lies in `D(t)`; hence `tau(t) <= |D(t)|`, a
> `tau(t) = 2` line has `|D(t)| >= 2` with both tied totals inside `D(t)`,
> and a `|D(t)| = 1` line has `tau(t) <= 1` and is never a two-tie line. (c)
> On a `|D(t)| = 1` line, `D(t) = {j}`, every L8 labelling with `K_tt = 1`
> has bit `j` set in both labels, and the matched pivot `a(t) = b(t) = e_j`
> attains `K_tt = 1`; such lines sit inside the Lemma MP family of
> [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717).

*Proof.* (a) Reduce the global rescaling `M' = 2^{-gamma} M` modulo 2 in the
normalized factorization: each term `p_j(t) q_j(t)` of `M'_tt` is a 2-unit
exactly when its valuation equals `gamma`, and every other term vanishes
mod 2; so `M'_tt mod 2 = tau(t) mod 2`, and `t` is anchored exactly when
`M'_tt` is odd. (b) A term with `v_2(p_j(t) q_j(t)) = gamma` has both factors
nonzero, so `j` is in `pi(t) intersect sigma(t) = D(t)`. (c) `K_tt = 1`
requires `sum_j a_j(t) b_j(t) = 1` mod 2, and every summand needs `j` in
`D(t) = {j}`; so bit `j` is set in both labels, and `e_j, e_j` qualifies.
`QED`

**Scope.** `tau(t) = 2` is exactly the tied-minima obstruction of
`research/root-unit-decoder-lemmas` section 7 ("minimal 2-adic valuations
attained twice"); `tau(t) = 0` lines carry no total at the content floor.
Lemma CT classifies the residue by parity but does not order it: the anchor
covers the odd-`tau` lines, and everything else is the repair/ordering/pivot
territory this package measures.

## 2. Lemma CL3: insertion-finite mixing — PROVEN

Lemma MX of [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747)
mixes anchor lines `A` (labels `a0, b0` of the normalized factorization,
`K0_ts = 2^{-gamma} M_ts mod 2`), one-sided repairs `U` and matched pivots
`T`, but only in two block orders (all of `A union U` before `T`, or after);
its open question 2 asks for the general order, where each anchor line
inserts at a valid **cut** of the pivot order. This is exactly the closure
obstruction on `cex_min_1` (6144/6144 mixed failures in both block orders,
recorded in PR 2747). The general case has a closed form.

Fix a pivot configuration: a map `c: T -> {1, 2, 3}` with `c(t)` in `D(t)`,
kept pivot subsets `S_i` of the classes `C_i = {t in T : c(t) = i}` with
`Z[S_i]` acyclic, and a pivot order that points every conflict backward. For
an anchor line `x` put `L(x) = {t in S_T : M_xt = 0 and bit c(t) of a0(x) is
set}` (these must precede `x`) and `R(x) = {t in S_T : M_tx = 0 and bit c(t)
of b0(x) is set}` (these must follow `x`), where `S_T = union_i S_i`.

> **Lemma CL3.** A set `A` of anchor lines is simultaneously insertable at
> valid cuts of one pivot order if and only if the joint demand digraph
> (pivot demands: `v` before `u` for every pivot conflict `u -> v`; plus, for
> each `x` in `A`, `t` before `x` for `t` in `L(x)` and `x` before `t` for
> `t` in `R(x)`) is acyclic. In that case
> `cert(M) >= |A| + sum_i |S_i|`. Anchor-to-anchor conflicts vanish always
> (the scope identity `K0 = M' mod 2 = 0` at incidences), so insertions do
> not interact except through the shared pivot order.

*Proof.* A kept set is feasible exactly when its conflict digraph points
backward in some order (PR 2717's Lemma SF order argument). Conflicts
between two pivot-kept lines are the pivot demands; conflicts between an
anchor line `x` and a pivot-kept line `t` are `x -> t` for `t` in `L(x)` and
`t -> x` for `t` in `R(x)`, each demanding the opposite order; conflicts
between two anchor lines are `K0_ts = M'_ts mod 2 = 0` at every incidence and
vanish. The combined conflict digraph on `A union S_T` is acyclic exactly
when the joint demand digraph is, and any order pointing every conflict
backward (a topological order of the demands) certifies `|A| + sum_i |S_i|`.
`QED`

**Scope.** Lemma CL3 subsumes Lemma MX's two block orders (the extreme
cut placements) on the anchor-plus-pivot part; one-sided repairs `U` compose
as in Lemma MX and are not re-derived. The machine evaluation below uses the
MX-compatible fixed labels (`a0, b0` on `A`, `e_{c(t)}` on `T`); the exact
completion engine of PR 2717 (free `b`-labels) is strictly stronger and is
computed separately.

## 3. The residual obstruction of residue (i-prime), precisely

Define `named(M)` as the largest certificate value carried by the union of
the named families: the Lemma SG anchor (`|S_gamma|`), Lemma MX one-sided
repairs, Lemma MP matched pivots (`MP = max_c sum_i MAS(Z[C_i])`), and the
Lemma CL3 insertion mixings of Section 2. Every family carries a replayed
L8 witness, so `named(M)` is a certified lower bound on `cert(M)`.

> **Definition (residual obstruction).** The residual obstruction of the
> cancellation-line residue is an instance with `named(M) < floor(2v/3) <=
> cert(M)`: every named family (anchor, repairs, pivots, insertion mixing) is
> short of the threshold while general L8 labels still certify. The strict
> form is an instance with `cert(M) < floor(2v/3)`, a falsifier to F-star.

Two levels are distinguished in the record below: the **threshold
obstruction** `named(M) < floor(2v/3)` (never realized in this search; the
falsifier criterion was armed on every instance) and the **family gap**
`named(M) < cert(M)` (realized on both canonical fixtures and on a re-split,
see Section 4). The family gap says the named families are strictly weaker
than `cert`; it is the label-landscape question of PR 2747's open question 3
("what labels do the attaining certificates actually use?").

## 4. Fixture settlement despite 12/12 and 11/19 cancellation lines — CHECKED

Both canonical fixtures of
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) (by
DreamingOfClouds) are settled by a **coefficient-free** certificate even
though the anchor is vacuous or short; every number below is recomputed by
`verify.py` in one run.

| quantity | `tied_min` (12 lines) | `cex_min_1` (19 lines) |
|---|---|---|
| cancellation lines (Lemma CT/SG) | 12 of 12 (all `tau` even) | 11 of 19 |
| anchor reach `S_gamma` | 0 of 12 | 8 of 19 (lines 0, 4, 5, 6, 8, 11, 14, 15) |
| threshold `floor(2v/3)` | 8 | 12 |
| Lemma MP (exhaustive pivot maps) | 9 (4096 maps) | 16 (6144 maps) |
| Lemma CL3 insertion mixing | 9 (no anchor lines exist) | 16 (up to 5 of 8 anchors placeable at the best config; 7 seen) |
| engine / stored witness | 11 (hill-climb re-found) | 18 (stored witness replayed) |
| family gap `cert - named` | 2 | 2 |
| chain engine (stored pairing) | cited 12 (PR 2379) | 22 (reproduced, 10+6+6) |

**Verdict for the residue.** On `tied_min` (12/12 cancellation lines, anchor
reach 0) and on `cex_min_1` (11/19 cancellation lines, anchor 8 short of 12)
F-star holds through Lemma MP alone: the matched-pivot certificate reaches
`9 >= 8` and `16 >= 12` with no anchor, no repairs and no search. Cancellation
lines in these instances do not obstruct the threshold; the coefficient-free
pivot structure carries it. The CL3 insertion analysis (bounded scan of
`2^20 = 1048576` mixing configurations: `A = S_gamma` with all maps on the
cancellation lines scanned exhaustively, 20000 configurations scanned in
descending `|A|`, exact joint insertion on the top 32) adds nothing over
pure pivots on `cex_min_1`: the best mixed value stays 16, with up to 5 of
the 8 anchor lines placeable at valid cuts (7 placeable in some
configuration). This answers PR 2747's open question 2 on the canonical
instance: the general order's insertion power is real (block orders fail
completely; cuts place up to 7 of 8 anchors) but does not beat the pure
matched-pivot certificate there. The remaining gap to the recorded 18 is
the family gap of Section 3: the attaining witnesses use labels outside
anchor/repair/pivot families.

## 5. CORRECTIVE: the dyadic corollary's normalization gap, reproduced and repaired — PROVEN

[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717) proved
Lemma AN under the hypothesis "after per-total powers of two the
factorization is 2-integral: all entries of `p, q` lie in `Z_(2)`", and
closed it with this corollary sentence:

> "Under the added hypothesis that at most `floor(v/3)` lines have `M_tt`
> even, `cert(M) >= ceil(2v/3)`, so **F-star holds for dyadic decoders with
> at most one-third even diagonals**."

[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869) found
the normalization gap: **dyadic entries do not imply Lemma AN's hypothesis.**
The gap is reproduced here as control SC1 (PR 2869's control, recomputed):
on two lines with `p = q = (1/2)(1, 1)` all entries are dyadic, but the total
content is `c_1 = -2`, the rescaling interval `[-m_1, n_1] = [1, -1]` for the
per-total power of two is empty, and no per-total rescaling makes both
factors 2-integral; the mod-2 reduction `p mod 2` that Lemma AN applies is
not even defined on `p(t) = 1/2`. The corrected anchor still anchors both
lines (`gamma = -2`, `S_gamma` = both). The count phrase has a second gap
(control SC2): `M = 2 I_3` has three even diagonals (naive count 0 anchored)
while the corrected reach is 3 (`gamma = 1`), so "even diagonals" is not the
anchor count when `gamma != 0`.

> **Corrected dyadic corollary (PROVEN, from Lemmas SC/SG of PR 2869).** For
> every exact 3-total rational decoder, in any entry class: `cert(M) >=
> |S_gamma| = v - #{t : v_2(M_tt) > gamma}` with `gamma = min_j c_j` and
> `c_j` the content of total `j`; hence F-star holds on `M` whenever at most
> `floor(v/3)` lines are cancellation lines (`v_2(M_tt) > gamma`). Lemma AN's
> literal hypothesis (2-integrality after per-total powers of two) holds
> exactly when `c_j >= 0` for every total (Lemma SC (b)), which for dyadic
> entries is a condition on the factorization, not a consequence of dyadic
> entryhood; when it fails, the single global rescaling `M -> 2^{-gamma} M`
> restores it (Lemma SG (a)). The anchored set is `S_gamma = {t : v_2(M_tt) =
> gamma}`, not the odd-diagonal set; the two coincide exactly when
> `gamma = 0`.

This package states the corrected corollary in its own claim text; a
corrective comment with the same content is posted on PR 2717 (the
authorized remedy; PR 2717's branch is not touched).

## 6. Smallest-first falsifier search across 1..v cancellation lines — CHECKED (scoped negative)

Smallest falsifying instance first (`v` ascending from 3), exact
cancellation counts `k = 1..v` (the residue axis), deterministic seeds in
`CERTIFICATE.json`. Falsifier criterion, armed on every instance: exact
`cert` below `floor(2v/3)` where exhaustive `a`-enumeration terminates
(`v <= 5`), or an explicit admissible pairing `B` with chain cost
`sum_j rank_F2 B[R_j, A_j]` below `floor(2v/3)` (the proven chain of
`research/root-unit-decoder-lemmas` forces `cert` below threshold then).
Every accepted value carries an L8 witness replayed by the independent
checker.

| family | domain | instances | named = cert | falsifiers | min named ratio |
|---|---|---|---|---|---|
| parity-engineered | `v = 3..12`, `k = 1..v` exact | 75 | all | 0 | 1.000 |
| structured (tied_min signature) | `v = 3..12`, `k = 1..v` exact | 34 | all | 0 | 1.000 |
| adversary (minimizing the pivot floor) | `k > floor(v/3)`, `v = 3..11` | 44 | all | 0 | 1.000 |
| GL_3(Z) re-splits of the fixtures | 24 re-splits, fixture-density `Z` | 24 + 1 | gap 1 on the hardest | 0 | 0.895 |

Totals: 153 search instances plus 25 re-split records, 0 falsifiers, the
criterion never fired. What the families show: (i) on every generated
instance with generic supports the named families reach `cert = v` (the
engine never exceeds them: max engine-over-named 0); (ii) hardness needs
the fixtures' dense zero digraphs (`MAS(Z) = 4` of 12 and `10` of 19), which
the generators cannot realize: arcs `M_ts = 0` require `|pi(t) intersect
sigma(s)| >= 2` (Lemma RK (c) of PR 2717), so random small-integer
factorizations give sparse `Z` and easy pivot floors — this is the exact
obstruction of the generator route, recorded, not an unrealizability claim;
(iii) `GL_3(Z)` re-splits keep the fixtures' dense `Z` (and their diagonal
valuations, so the cancellation counts seen are 11 and 12 only) while moving
`gamma`, the supports and `S_gamma`; there the named floor dips to `17/19 =
0.895 v` and the engine adds 1 on the hardest re-split, so the family gap of
Section 3 persists at fixture density.

**Early kill and the exact obstruction (recorded).** The threshold
obstruction `named < floor(2v/3)` was not realized on any of the 178 records;
the falsifier criterion was armed and never fired; the search stops at the
declared domain (`v <= 12`, exact `k`, the recorded generator budgets). The
true residual obstruction of residue (i-prime) as found here is the family
gap: on the canonical hard instances the named families (anchor, repairs,
pivots, insertion mixing) reach 9 and 16 while `cert` is 11 and 18, so a
proof of F-star through named families alone must either prove the
matched-pivot floor `max_c sum_i MAS(Z[C_i]) >= floor(2v/3)` for every
realizable pattern (PR 2747 open question 1; witnessed here on 178 records
and on the fixtures at 9/12 and 16/19) or master the two-bit labels the
attaining witnesses use (PR 2747 open question 3).

## 7. What is proved, what is checked, what is demoted

- **PROVEN (README, written proofs):** Lemma CT (tie parity: cancellation
  lines are exactly the even-`tau` lines, `tau` in `{0, 2}`; tied totals lie
  in `D(t)`; `|D(t)| = 1` lines are pivot-bit-forced and never two-tie);
  Lemma CL3 (insertion-finite mixing with the exact joint-demand criterion,
  strictly extending Lemma MX's two block orders on the anchor-plus-pivot
  part); the corrected dyadic corollary of Section 5 (following Lemmas SC/SG
  of PR 2869, whose proofs are cited, not restated).
- **CHECKED (machine, `verify.py`, stdlib, deterministic, about 67 s,
  certificate digest `7f27c1e761b34c98`):** controls 8/8 (brute-force-over-
  all-labellings agreement 3/3 at `v = 3`, diagonal decoder `cert = 3`,
  corrupted-witness rejection 2/2, Lemma CT hand values 2/2 with tie parity
  and the scope identity on every instance, pivot-bit forcing on 6 label
  pairs, Lemma CL3 vs exact completion on 40 tiny configurations with
  replayed witnesses, and the two normalization-gap exhibits SC1 and SC2);
  the full recorded-anchor calibration (PR 2717: `tied_min` 11/12,
  `cex_min_1` 18/19, chain 22; PR 2747: MP/MX 9 and 16 over 4096/6144 pivot
  maps; PR 2869: reach = anchor_good 0/12 and 8/19; PR 2890:
  PASS_FC4_CALIBRATION values reproduced); the fixture settlement of Section
  4 including the bounded CL3 insertion analysis; the re-split probe (25
  records) and the k-axis search (153 records) of Section 6, 0 falsifiers.
- **DEMOTED / OPEN:** F-star for general rational decoders is **not** proved
  here. The threshold obstruction is not realized in the searched domain;
  the family gap is realized (9 < 11, 16 < 18) and is the residual
  obstruction as defined in Section 3. The CL3 evaluation on `cex_min_1` is
  a bounded scan (20000 of 1048576 configurations; the `A = S_gamma` level
  exhaustive), not an exhaustive maximum; "up to 5 of 8 placeable at the
  best config" is not an "exactly when" claim. No necessity claim is made
  for any lemma hypothesis. The fixture certificates 11/18 rest on PR 2111's
  recorded CP-SAT optimality, not re-verified here. The generators do not
  realize fixture-density zero digraphs (Section 6 (ii)); the adversarial
  family is a bounded hill-climb, not an optimization proof. Cancellation
  counts at fixture density are limited to 11 and 12 by the invariant
  diagonal valuations of the re-split construction.

## Open next questions

1. **The matched-pivot floor (PR 2747 open question 1).** Is
   `max_c sum_i MAS(Z[C_i]) >= floor(2v/3)` for every realizable rank-3
   pattern? Why it matters: Lemma MP alone would prove F-star for every
   entry class and every cancellation count, with no anchor at all; this
   package witnesses it on 178 records and on both fixtures at 9/12 and
   16/19. First step: a SAT/CP construction of rank-3 patterns minimizing
   `max_c sum_i MAS(Z[C_i])` (the fixture-density zeros resist random
   construction; Lemma RK (c) forces `|pi(t) intersect sigma(s)| >= 2` at
   every arc). Blocker: needs a constraint solver, not random search.
2. **The two-bit labels of the attaining certificates (PR 2747 open
   question 3).** The witnesses 11 and 18 exceed every named family (9 and
   16) by exactly 2; classify their label patterns and either add a
   two-bit-label lemma with exact hypotheses or prove the named families
   complete below some `v`. Why it matters: it decides whether the family
   gap of Section 3 is closable by one more lemma. First step: diff the
   stored 18-witness and the re-found 11-witness against all matched pivots
   and anchor labels. Blocker: none; analysis of existing witnesses.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -B research/fstar-cancellation-lines-seed80d69336/verify.py
python3 scripts/research_package.py --package research/fstar-cancellation-lines-seed80d69336 --check-only
python3.12 scripts/research_package.py --package research/fstar-cancellation-lines-seed80d69336
```

Expected markers: `PASS_CL_CONTROLS`, `PASS_CL_CALIBRATION
tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22 reach=0/12,8/19`,
`PASS_CL_RESPLIT`, `PASS_CL_GAP dyadic-corollary-normalization-gap=reproduced
SC1 SC2`, `PASS_CL_SEARCH`, `PASS_FSTAR_CANCELLATION_LINES`, and
`CERTIFICATE.json` with digest `7f27c1e761b34c98` (full digest printed by the
run; observed about 67 s on the authoring host). The registered CPython 3.12
replay prints `PASS_REGISTERED_RESEARCH_PACKAGE
research/fstar-cancellation-lines-seed80d69336 outcome=completed`. `make` is
not installed on the authoring host; the commands above are the underlying
ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain
`cost >= sum_j r_j >= cert(M)` are from the merged
`research/root-unit-decoder-lemmas` package
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance)).
The rank-3 configuration model, the named instances `tied_min` and
`cex_min_1`, their recorded one-copy certificate limits (11 and 18, CP-SAT,
CHECKED (recorded)), the stored cost-22 pairing and the tied-minima
obstruction are DreamingOfClouds' work in
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) and
[PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162);
`data/tied_min.json` and `data/cex_min_1.json` are byte-identical copies of
their data files (sha256
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` and
`86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`); the
stored cost-22 pairing is `data/cex_min_1.B22.json` (sha256
`15f5039069a175831f92c4ffe023a23a6f6e6bd6665f0ca2c2734bbe672b51ef`) and the
stored 18-witness `data/cex_min_1.witness.json` (sha256
`153f4d2e8dc262f547a91f2daff9724cab88beb4d45c399497efc68a8ed2c933`) is from
PR 2717's package. The residue statement, Lemmas SF/MP/RK/AN and the
exact-completion engine design this package adapts are Aaron Wang's work in
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717); Lemma
MX and the tied-residue closure are Aaron Wang's
[PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747); the
zero-digraph machinery is Aaron Wang's
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774);
Lemmas SC/SG, the entry-class collapse and the residue rename to (i-prime)
are Aaron Wang's
[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869); the
chi(Z) machinery and the calibrated engine variant are Aaron Wang's
[PR 2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890). The
falsifier-census frontier is Aaron Wang's
[PR 2335](https://github.com/CrocSwap/integer-mult-bounds/pull/2335); the
exact cost 12 of `tied_min` is Aaron Wang's
[PR 2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379); the
exact cost 21 of `cex_min_1` is Nick Petalas'
[PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206). All
authors above were verified at current ground truth with `gh pr view --json
author,title` on 2026-10-16. This package does not claim their results; the
new content is Lemma CT, Lemma CL3 with its exact insertion criterion, the
fixture settlement of the insertion route, the family-gap definition and
record, the cancellation-line-axis falsifier search and the GL_3(Z) re-split
probe, and the corrected dyadic corollary with its reproduced normalization
gap.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no model named; no independent human review claimed). New work in this
package is Apache-2.0.
