# F-star family gap: the box floor FAILS, minimally at v = 3 - and its exact surviving tau >= 1 form (no kappa)

## Scope

Kappa-blocker **KB5k** (authorized explicit open request from the
[handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166);
scope changed from the drawn `portable-replay` card and recorded in
`TASK.json`): the **surviving box-floor route** to open problem **F-star**
(`cert(M) >= floor(2v/3)` for every exact 3-total rational decoder
`M = sum_{j<=3} p_j q_j^T` on `v` lines with `M_tt != 0`,
`research/root-unit-decoder-lemmas` section 7) - the recorded remainder of
[PR 2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978) (its
consequences section and open questions). PR 2978 proved `cert >= box` and
proposed the **box floor** `box(M) >= floor(2v/3)` as the surviving chain link
("a proof closes F-star directly"), scoped in its prose to the `tau >= 1`
domain.

**Answer: the box floor, read over all exact 3-total rational decoders, is
FALSE - minimally so.** The minimal falsifier is a rank-3 decoder at `v = 3`
with `tau = (0,0,0)`: `cert = 3 >= 2 = floor(2v/3) > 0 = box`, both sides
exact. F-star itself is **not** proved and **not** refuted (every falsifier
has `cert >= floor(2v/3)`). On the `tau >= 1` domain the floor is **PROVEN for
`v <= 4`** (Lemma LB2 below) and its first open case is `v = 5` (threshold 3),
where a bounded exact search of 240 realizable decoders found 0 violations.
Every claim is labelled PROVEN / CHECKED / DEMOTED.

## Verdict

1. **PROVEN: `box = 0` iff every line has `tau = 0`** (Lemma K: a kept line
   needs a tied bit). The box floor therefore fails at `v = 3` exactly when
   fewer than two lines have `tau(t) >= 1`; the minimal falsifier has
   `box = 0`, the minimum possible value.
2. **PROVEN: the minimal rank-3 falsifier is `v = 3`, `tau = (0,0,0)`.** Exact
   integer decoder (int-only arithmetic):

   ```text
   P = [[1, 1, 0],        Q = [[2, 2, 1],
        [1, 0, 1],             [2, 1, 2],
        [0, 1, 1]]             [1, 2, 2]]

   M = P Q^T = I + 3 J = [[4,3,3],[3,4,3],[3,3,4]]   det = 10, rank 3
   gamma = 0   c = (0,0,0)   r_box = 3   tau = (0, 0, 0)
   a0 = [3, 5, 6]  b0 = [4, 2, 1]     zero arcs: none
   ```

   Exact both sides: `cert = 3` (trivial upper bound `v`, attaining witness
   replayed) > `2 = floor(2v/3)` > `0 = box` (PROVEN upper bound Lemma K;
   independent definition-level enumeration over every in-box label
   assignment). Minimal: rank 3 forces `v >= 3`, and no value below `box = 0`
   exists.
3. **PROVEN: the whole failure gradient, exact both sides.** In the wide class
   (rank `<= 3`, three totals) a rank-2 falsifier exists already at `v = 2`
   (`tau = (0,0)`, `cert = 2 > 1 = floor(2v/3) > 0 = box`); at `v = 3` the
   pattern `tau = (1,0,0)` gives `cert = 3 > 2 > 1 = box`; at `v = 4`,
   `tau = (0,0,0,0)` gives `cert = 4 > 2 > 0 = box`. Each is a rank-checked
   exact decoder with `M_tt != 0`, all three totals used, and its `cert`/`box`
   recomputed by the vendored PR 2914 engine AND an independent enumeration
   written from the definitions.
4. **PROVEN (Lemma LB2, two-line repair): any two lines with `tau >= 1` are
   jointly box-keepable**, so `box >= min(2, #{t : tau(t) >= 1})`. Machine
   replay of the explicit construction on 16,761 canonical `v = 3` configs
   with at least two keepable lines (the full Lemma-SG-consistent
   `(a0, b0, Z)` space up to line/total relabeling, **including** `tau = 0`
   lines, which PR 2978 job B excluded) and on 160 random realizable decoders
   at `v = 4..6`, 0 failures.
5. **CHECKED: the `tau >= 1` box floor is exact at `v = 3` and `v = 4`**
   (threshold `<= 2`, Lemma LB2) and **bounded at `v = 5`** (threshold 3):
   240 realizable `tau >= 1` decoders (80 random valuation-tuned, 80
   extensions of PR 2978's counterexample core, 80 unit-role templates), 97
   of them with `r_box = 2`, every exact box `>= 3` (0 below threshold).
   Bounded - **not** a non-existence result.
6. **CHECKED: recomputation of PR 2978 job B** (the vendored receipt ships
   empty; everything recomputed from scratch): 3023 canonical `v = 3`
   configs, 27 gap candidates, every candidate at exact `box = 2 =
   floor(2v/3)` - so the `tau >= 1` minimum at `v = 3` is exactly the
   threshold, with no margin.
7. **DEMOTED: the box-floor route as stated.** `box >= floor(2v/3)` is dead on
   the full class and survives only on the `tau >= 1` domain, where it is
   proved for `v <= 4` and open for `v >= 5`. The replacement lower-bound
   picture is in "Consequences" below. F-star: **not proved, not refuted**
   (`cert = v >= floor(2v/3)` on every falsifier here).

## Lemma K (keepable lines) - PROVEN

> **Lemma K.** A line `t` can be kept inside the sub-anchor box iff
> `tau(t) = |a0(t) intersect b0(t)| >= 1`. Consequently `box(M)` is `0` iff
> every line has `tau(t) = 0`, and `box(M) <= #{t : tau(t) >= 1}` always.

*Proof.* A kept line needs in-box labels `a(t) subseteq a0(t)`,
`b(t) subseteq b0(t)` with `K_tt = a(t) dot b(t) = 1` mod 2, so
`a(t) intersect b(t)` is nonempty and contains a tied bit; conversely the tied
singleton `a(t) = b(t) = {j}` keeps `t` alone. QED

## Lemma LB2 (two-line repair) - PROVEN

> **Lemma LB2.** Any two lines `t, s` with `tau(t), tau(s) >= 1` are jointly
> box-keepable. Hence `box(M) >= min(2, #{t : tau(t) >= 1})`; in particular
> the box floor `box >= floor(2v/3)` holds at every `v` with
> `floor(2v/3) <= 2` as soon as two lines have `tau >= 1`.

*Proof.* Pick tied bits `j in a0(t) intersect b0(t)` and
`k in a0(s) intersect b0(s)`. If some ordered pair is a nonzero arc, order the
two lines so the nonzero pair is forward: there is no forward zero arc and the
tied singletons `a = b = {j}`, `a = b = {k}` keep both lines (only `K_tt = 1`
is required). If both ordered pairs are zero arcs, order `t` before `s`. For
`j != k` the singletons give `K_ts = [j = k] = 0`. For `j = k` the scope
identity (Lemma SG) makes `|a0(t) intersect b0(s)|` even and `j` lies in that
set, so there is `r != j` with `r in a0(t) intersect b0(s)`; take
`a(t) = {j, r}`, `b(t) = {j}`, `a(s) = {j}`, `b(s) = {j, r}`. Then
`K_tt = K_ss = 1` and `K_ts = |{j, r} intersect {j, r}| = 0` mod 2. All labels
are in-box (each bit lies in the required `a0`/`b0` mask) and the backward
entry is unconstrained. QED

The construction is machine-replayed from the definitions on every config and
instance named in verdict item 4 (a config where it fails is a refutation).

## What controls the box: tau pattern, shareable count, zero arcs

The shareable-class vocabulary of PR 2978 (Lemma RT + shareable-totals
corollary) supplies the matching upper bounds, and together with Lemmas K/LB2
fixes the box at small `v`:

- **tau pattern (lower side).** `box = 0` iff all `tau = 0` (Lemma K);
  `box >= min(2, #{tau >= 1})` (Lemma LB2). By Lemma CT (tie parity) the
  falsifiers are all-cancellation-line decoders (`tau` even everywhere,
  `v2(M_tt) > gamma`): the box dies exactly in PR 2901's cancellation residue,
  while `cert` there keeps its full value (`cert = v` on every falsifier here,
  since the matched-pivot construction (Lemma MP) attains `v` when the zero
  digraph is empty).
- **shareable count (upper side).** In the box only totals with `c_j = gamma`
  can enter `K`, and a kept set whose forward pairs are all zero arcs has size
  `<= r_box = |{j : c_j = gamma}|` (PR 2978 Lemma RT). So `r_box = 2` caps
  such kept sets at 2 - the shape a `v = 5` falsifier would need - while
  `r_box = 3` only admits rank-3 triangular obstructions.
- **tied totals (colour side).** The box version of Lemma MP: colour each line
  by a tied bit `c(t) in a0(t) intersect b0(t)` and keep acyclic subsets of
  each colour class (topological order kills same-colour forward zero arcs;
  cross-colour entries vanish automatically). **Lemma TB (PROVEN):**
  `box >= max_c sum_j MAS(Z[C_j])` over tied-bit colourings. This is exactly 0
  on `tau = 0` instances and recovers LB2 on two keepable lines.
- **zero arcs (shape of any remaining falsifier).** Lemma RT blocks one order
  of a kept set `S` only when every forward pair of that order is a zero arc;
  `S` is blocked in *every* order by rank only if `Z[S, S]` is complete (all
  six ordered pairs zero arcs), and then `M[S, S]` is diagonal, so
  `|S| <= rank(M) = 3`. Hence at `v = 5` a falsifier needs every 3-subset
  blocked in every order: Z-complete triples for the rank route (`r_box <= 2`
  necessary there) and bilinear infeasibility everywhere else. No such
  instance was realized in the bounded search; this is the recorded
  obstruction, not a proof of absence.

## The minimal falsifiers, in detail

Anchor data (canonical reduced normalization; engine-computed exactly):

| instance | v | rank M | gamma | c | r_box | tau | a0 | b0 | threshold | cert | box |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F2-wide | 2 | 2 | 0 | (0,0,0) | 3 | (0,0) | 3, 5 | 4, 2 | 1 | 2 | 0 |
| F3-tau0 | 3 | 3 | 0 | (0,0,0) | 3 | (0,0,0) | 3, 5, 6 | 4, 2, 1 | 2 | 3 | 0 |
| F3-tau1 | 3 | 3 | 0 | (0,0,1) | 2 | (1,0,0) | 3, 5, 6 | 1, 2, 1 | 2 | 3 | 1 |
| F4-tau0 | 4 | 3 | 0 | (0,0,0) | 3 | (0,0,0,0) | 3, 5, 6, 7 | 4, 2, 1, 0 | 2 | 4 | 0 |

(`a0`/`b0` are bit masks over the three totals; `c_j = m_j + n_j`;
`threshold = floor(2v/3)`.) `F3-tau0` has `M = I + 3 J` (all off-diagonal
pairs nonzero, so its `cert` witness keeps all three lines in any order with
unit pairs `a = b = e_j` on distinct totals); `F3-tau1` has
`M = [[3,3,3],[5,4,3],[6,3,4]]`, `det = -12`. Every instance passes the tie
parity and scope identities, `M_tt != 0` everywhere, all three totals used,
and each `cert`/`box` pair is reproduced three ways (vendored engine exact
enumeration; independent definition-level enumeration over all label
assignments for the box side and for `cert` at `v <= 3`; written bounds
`cert <= v`, `box = min(2, #keepable)`).

## What is proved, what is checked, what is demoted

- **PROVEN (written proofs in this README):** Lemma K; Lemma LB2; Lemma TB
  (tied-bit matched pivots inside the box); the four falsifiers with exact
  `cert`/`box`, ranks and identities; minimality (`v >= 3` forced by rank 3 in
  the exact-3-total class; `v = 2` minimal in the wide class; `box = 0` the
  minimum value).
- **CHECKED (machine, exhaustive on the declared domains or replayed):** the
  LB2 construction on 16,761 canonical `v = 3` configs and 160 random
  realizable decoders `v = 4..6`; the mixed-`tau` formula
  (`box = #keepable` for `#keepable <= 2`, `box >= min(2, #keepable)`) on 240
  realizable decoders `v = 3..4`; PR 2978 job B recomputed (3023 configs, 27
  candidates all exactly at `box = 2`); the `v = 5` `tau >= 1` pivot (240
  exact instances, 97 with `r_box = 2`, 0 below threshold - bounded);
  predecessor anchors reproduced unchanged (see `anchor_replay.py`).
- **DEMOTED / OPEN:** the box floor on the full class is **refuted**, not
  open; its `tau >= 1` form is open at `v >= 5` (first case `v = 5`,
  threshold 3). Shareable-class completeness (PR 2978's 21 unrealized `v = 3`
  patterns) is **unchanged and open** - this session spent its one bounded
  pivot on the box floor instead. F-star is **not** proved and **not**
  refuted.

## Consequences for the family-gap route

The chain `cert >= box` (PR 2914 Lemma LB) survives, but the floor rung is
dead on the full class: below two keepable lines the box can be `0` while
`cert = v`. The replacement lower bound that still links the rungs is the
**max** of the two certified rungs, not the box alone:

- the **named/box-free rung** (PR 2901's Lemma MP matched pivots, Lemma MX,
  Lemma TB's unrestricted original) carries the `tau = 0` cancellation
  region: on every falsifier here `MP = v` (empty zero digraph);
- the **box rung** carries the `tau >= 1` region: `box >= min(2, #keepable)`
  (Lemma LB2), the `v <= 4` floor, and PR 2978's `r_box` cap as its sharp
  upper companion.

So `cert >= max(named, box) >= floor(2v/3)` is the honest surviving statement
shape; the open work is either a `tau >= 1` box floor at `v >= 5` (which
together with the matched-pivot rung on the `tau = 0` side would still close
F-star) or a direct named-family floor in the shareable-class vocabulary.

## Open next questions

1. **The `tau >= 1` box floor at `v >= 5`** (threshold 3 at `v = 5`). Why it
   matters: it is the exact surviving form of PR 2978's box-floor route; a
   proof closes F-star on the `tau >= 1` domain. First step: either prove a
   three-line repair (generalizing Lemma LB2 under the rank-3 constraint of
   Lemma RT's shape analysis) or construct a `box = 2` instance with
   `r_box = 2` and the recorded obstruction shape. Blocker: bilinear
   infeasibility of three-line label systems has no characterization yet.
2. **PR 2978's 21 unrealized `v = 3` gap patterns (shareable-class
   completeness)** - unchanged. Why it matters: a realization refutes
   box-completeness in the shareable class at `v = 3`; unrealizability proves
   it there. First step: PR 2978's `realize_kj.py` with a valuation-level
   enumeration instead of seeded restarts. Blocker: no realizability
   characterization beyond Lemma SG + column attainment.
3. **The named-family floor in shareable-class terms.** Why it matters: with
   the box floor dead on the `tau = 0` side, `cert >= named` must carry that
   region; PR 2901's Lemma MP floor question (matched-pivot floor) is the
   same question in the older vocabulary. First step: express MP's MAS sums
   through the tied-bit colourings of Lemma TB and compare against
   `floor(2v/3)`.

## Reproduce

Standard library only, Python 3.10+ (registered replay: 3.12):

```sh
python3 -B research/fstar-boxfloor-minimal-seed758ae8fe/verify.py
python3 -B research/fstar-boxfloor-minimal-seed758ae8fe/anchor_replay.py
python3 scripts/research_package.py --package research/fstar-boxfloor-minimal-seed758ae8fe --check-only
```

`verify.py` recomputes everything from scratch (falsifiers, Lemma K/LB2
checks, the mixed-`tau` sweep, the job-B recomputation, the `v = 5` pivot) and
digests the receipts into `CERTIFICATE.json` (written with `newline="\n"`).
`anchor_replay.py` runs the vendored PR 2978 `verify.py` **unchanged** on a
byte-copy (its receipts cannot touch pinned bytes) and asserts every recorded
anchor marker, including `PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19
mp=9/16 chain=22 reach=0/12,8/19`, `PASS_KJ_COUNTEREXAMPLE v=3 tau=2/2/2
cert=3 box=2 r_box=2 independent=3/2`, `PASS_KJ_V2 configs=2842`,
`PASS_KJ_V3 configs=3023 box-equals-cert=2996 candidates=27` and the
certificate digest `0b5b55f84375b37c`.

## Exact heads and pins

- Base: `066f57ff795dbe6d0a0ecc11fe742eadcec00c39` (frozen assignment pin =
  canonical `origin/main` at worktree creation, 2026-10-16).
- [PR 2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978) head
  `12eb7b832de9239a314a7cddf6c6033d618cd8f2` (vendored tree under
  `predecessor/pr2978/`, byte-exact; its own pin sets
  `predecessor/pr2963/predecessor/PINS.json` (14 files) and
  `predecessor/PINS.json` (29 files) re-asserted at every replay).
- [PR 2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963) head
  `ee755e682b3b30d493e764d3be50003b13b69b4a`; [PR 2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936)
  head `f0ef06f13e4de3e50c211c880bdc6891c09620a1`; [PR 2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914)
  head `3f7781efccdf10fa61a1e0a6f11c191579b21280` (all through the vendored
  copies).

## Credit

F-star, `cert(M)`, L8 labellings and the proven chain `cost >= cert(M)`:
`research/root-unit-decoder-lemmas`,
[PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance).
Fixtures `tied_min`/`cex_min_1` and their recorded certificate limits 11/18:
DreamingOfClouds,
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111).
Lemmas SF/MP/RK/AN and the exact-completion engine design, Lemma MX, zero
digraph machinery, Lemmas SC/SG and the canonical reduced normalization,
chi(Z) machinery, the family-gap definition and Lemma CT, the sub-anchor box
and Lemmas SB/LB, Lemma BPP with the `tau >= 1` necessity pin, the 12
`tied_min` `v = 11` sub-decoders, and Lemma V2 / Lemma RT + shareable totals
with the minimal `box = cert` counterexample: Aaron Wang (navinor),
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717) /
[2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) /
[2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) /
[2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869) /
[2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890) /
[2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901) /
[2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914) /
[2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936) /
[2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963) /
[2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978).
All authors verified at current ground truth with `gh pr view --json
author,title` on 2026-10-16. New content here: Lemma K, Lemma LB2, Lemma TB's
box form, the four minimal falsifiers with their exact gradient, the
mixed-`tau` characterization, and the `v = 5` `tau >= 1` obstruction shape.

## Freshness and collision checks

Pair-collision checks (toolkit `disc-comments --grep`, discussions 1317 and
1166, nested replies) at entry found no live claim on the box floor or the
shareable class; the last family-gap activity is KB5j's FINDING/DONE/RELEASED
(PR 2978, 2026-10-16 15:56:55 UTC), whose recorded remainder this assignment
takes. The entry overlap survey (`find_overlap.py`, object proper names and
synonyms ("box floor", "shareable totals", "shareable class", "sub-anchor
box", "cert", "family gap", "F-star", "3-total decoder", "tied totals",
"box-completeness"), `--refresh`, complete pagination: 229 open PRs, 1682
discussion records at 16:04 UTC) found only the known F-star lineage and
unrelated traffic.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no model named; no independent human review claimed). No kappa, supplier,
word or moment claim.
