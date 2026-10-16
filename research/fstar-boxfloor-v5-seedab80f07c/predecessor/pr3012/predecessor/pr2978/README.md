# F-star family gap: Lemma BPP's without-loss question - box-completeness FAILS at tau >= 1, minimal counterexample v = 3 (no kappa)

## Scope

Kappa-blocker **KB5j** (authorized explicit open request from the
[handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166);
scope changed from the drawn `bit-new-register-model` card and recorded in
`TASK.json`): settle **Lemma BPP's without-loss question** of open problem
**F-star** (`cert(M) >= floor(2v/3)` for exact 3-total rational decoders,
`research/root-unit-decoder-lemmas` section 7) - the exact blocker
[PR 2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963) names for
box-completeness: may one assume, without loss at `tau >= 1`, that an attaining
L8 witness satisfies Lemma BPP conditions (i)+(ii), i.e. is
`box(M) = cert(M)` for every exact 3-total decoder with `tau(t) >= 1`
everywhere?

**Answer: NO.** A minimal exact counterexample exists at `v = 3` with
`tau = (2,2,2)`: `cert = 3 > 2 = box`, both sides exact. F-star itself is
**not** proved and **not** refuted here (the counterexample has
`cert = 3 >= 2 = floor(2v/3)`). Every claim is labelled PROVEN / CHECKED /
DEMOTED.

## Verdict

1. **PROVEN: box = cert = 2 at v = 2 for every tau >= 1 decoder** (written
   proof below; machine-checked on all 2842 scope-consistent anchor/zero
   patterns). So the minimal counterexample size is **exactly v = 3**.
2. **PROVEN: minimal tau >= 1 counterexample at v = 3.** Exact 3-total
   decoder (integers, all arithmetic exact):

   ```text
   P = [[-1, -3,  0],        Q = [[ 1, -3,  2],
        [ 1, -1, -2],             [ 3, -1, -2],
        [ 3,  3,  3]]             [ 3, -1,  2]]

   M = P Q^T = diag(8, 8, 12)          gamma = 0
   tau = (2, 2, 2)                     c = (0, 0, 1)
   a0 = [3, 3, 7]  b0 = [3, 3, 3]      (bit masks: 3 = {0,1}, 7 = {0,1,2})
   ```

   Exact both sides: `cert = 3` (replayed attaining witness below; independent
   enumeration), `box = 2` (PROVEN upper bound plus explicit box witness).
   `tau(t) >= 1` everywhere, the tie and scope identities (Lemmas CT/SG) hold
   machine-checked, and `M` has rank 3 (exact 3-total; all three totals used).
3. **PROVEN: the obstruction is a rank condition on the shareable totals.**
   Lemma RT (below): when every forward pair of a kept set is a zero arc,
   `K[S,S]` is unit triangular over F2, so `|S| = rank_F2(K[S,S])`, and
   `rank_F2(K) <= r(A,B)` = number of totals used on both label sides. In the
   box only the **shareable** totals (`c_j = gamma`) can enter `K` at all;
   here `c = (0,0,1)` gives `r_box = 2`, so `box <= 2 < 3 = cert`. Every
   attaining witness must certify line 2 through the **non-tied shared bit 2**
   (Lemma BPP condition (i) fails there; recorded projection drop 3 -> 2).
   So neither projection nor line-by-line re-pairing is without loss.
4. **CHECKED: escape classification (PR 2963's pool).** All 19 distinct
   escaping witnesses (21 events) of PR 2963's v = 3..5 fixture-sub-decoder
   pool are **cosmetic (E1)**: out-of-box bits that change no `K_tt` and no
   forward-arc parity; sub-anchor projection preserves them verbatim in value
   (0 drops, 0 box gaps). The escapes are labelling artefacts, not structure.
5. **REFUTED (bounded): projection is not without loss at tau >= 1.** On 360
   realizable tau >= 1 instances (v = 3..4: 320 random small-integer decoders
   with varied 2-adic valuations + 40 GL_3(Z) fixture transforms at v = 3),
   1788 replayed witnesses project to strictly lower value (E2 dominant:
   1768 certification escapes, E4 18, E3 6; E1 466). `box = cert` held on all
   360 (0 violations), so on that domain re-pairing exists although
   projection fails - until item 2 shows re-pairing can fail too.
6. **Narrowed surviving question (one stated condition).** Box-completeness
   on the **shareable class** (every total `j` has `c_j = gamma`, i.e. each
   total occurs in some `a0(t)` and some `b0(s)`): all earlier evidence lives
   there (fixtures, PR 2936/2963 sweeps, the 360 instances above). It is
   PROVEN at v = 2 and CHECKED at v = 3 on all 2996 non-candidate
   configurations; the exact remaining v = 3 question is the realizability of
   21 combinatorial gap patterns (below).

## The minimal counterexample, in detail

Anchor data (canonical reduced normalization; `m = (0,0,0)`, `n = (0,0,1)`,
`gamma = min(m+n) = 0`):

| t | p(t) | q(t) | a0(t) | b0(t) | tau(t) | v2(M_tt) |
|---|---|---|---|---|---|---|
| 0 | (-1, -3, 0) | (1, -3, 2) | 3 = {0,1} | 3 = {0,1} | 2 | 3 |
| 1 | (1, -1, -2) | (3, -1, -2) | 3 = {0,1} | 3 = {0,1} | 2 | 3 |
| 2 | (3, 3, 3) | (3, -1, 2) | 7 = {0,1,2} | 3 = {0,1} | 2 | 2 |

`M = diag(8, 8, 12)`: **every** off-diagonal pair is a zero arc. Tie parity
holds: all `tau(t) = 2` even and all `v2(M_tt) = 3, 3, 2 > 0 = gamma`
(cancellation lines). Scope identity holds machine-checked: `K0_ts = 0` on
every zero arc (`|a0(t) intersect b0(s)|` even everywhere) and `K0_tt = 0`
since every `tau` is even.

**cert = 3 (attaining witness, replayed).** Labels `a = b = [1, 2, 4]`
(unit pairs on totals 0, 1, 2 at lines 0, 1, 2), kept `[2, 1, 0]` in that
order. `K_tt = 1` on all three lines; the only forward pairs are
`(2,1), (2,0), (1,0)`, all zero arcs, and `K_21 = K_20 = K_10 = 0` (distinct
unit bits). Line 2 is certified through the non-tied shared bit 2
(`p_2(2) = 3` odd is in `a0(2)`, but `q_2(2) = 2` has `v2 = 1 > gamma`, so
bit 2 is **not** in `b0(2)`): Lemma BPP condition (i) fails exactly there,
and the witness's sub-anchor projection keeps only lines 0 and 1 (value 2).

**box = 2 (PROVEN).** In the box `b(t) subset of b0(t) = {0,1}` for every t,
so bit 2 never appears on a b-side and every box `K = A B^T` has
`rank_F2(K) <= 2`. Since every forward pair of any kept set is a zero arc,
Lemma RT gives `|S| = rank_F2(K[S,S]) <= 2` for every box witness. The bound
is attained: `a = b = [1, 2, 0]` on kept lines `{0, 1}` (order `0 < 1`) is a
valid box witness of value 2 (`K_00 = K_11 = 1`, `K_01 = 0`). Hence
`box = 2 < 3 = cert`. An independent enumeration (not the vendored engine)
recomputes both values from the definition; see `verify.py`.

## Lemma RT (triangular rank) - PROVEN

> **Lemma RT.** Let `(a, b)` be any L8 labelling and `S` a kept set in order
> `prec` (so `K_tt = 1` on `S` and `K_ts = 0` on every forward zero arc). If
> every forward pair `(t, s)`, `t prec s` in `S`, is a zero arc, then
> `det_F2(K[S,S]) = 1`; consequently `|S| = rank_F2(K[S,S])` and
> `|S| <= r(a, b)`, the number of totals `j` with some `a(t)` and some
> `b(s)` using `j`.

*Proof.* Under the hypothesis `K[S,S]` is unit lower triangular in the order
`prec`: the diagonal is 1 and every forward entry is 0 (zero arc). A
triangular matrix with unit diagonal has determinant 1 over any field, so it
is invertible and has rank `|S|` over F2. `K = A B^T` with `A, B` the
bit-matrices of the labels; `rank_F2(K) <= min(rank A, rank B)`, and both
ranks are at most the number of totals used on the respective sides, so
`rank_F2(K) <= r(a,b)`. QED

> **Corollary (shareable totals).** For box labels a total `j` contributes to
> `K` only if `j in a0(t)` for some `t` and `j in b0(s)` for some `s`; this
> holds exactly when `c_j = m_j + n_j = gamma`. So in the box
> `r(a,b) <= r_box := #{j : c_j = gamma}` and, when every forward pair of the
> kept set is a zero arc, `|S| <= r_box`.

*Proof.* `j in a0(t)` for some `t` iff `m_j` is attained (always true for a
nonzero p-column), and `j in b0(s)` for some `s` iff `min_s v2(q_j(s)) =
n_j = gamma - m_j`, i.e. `c_j = gamma`. QED

The hypothesis "every forward pair is a zero arc" is essential: when some
`M_ts != 0`, `K_ts` is unconstrained in the forward direction and `det` need
not be 1 (this is how `tied_min` reaches `box = 11 > 3 = r_box`). The
counterexample sits exactly where the hypothesis is strongest: `M` diagonal
forces rank `|S|` for every kept set in every order.

## Lemma (v = 2) - PROVEN: box = cert = 2 at tau >= 1

> **Lemma V2.** Every exact 3-total decoder on v = 2 lines with
> `tau(0), tau(1) >= 1` has `box = cert = 2`. Hence a box-completeness
> counterexample at `tau >= 1` needs `v >= 3`.

*Proof.* `cert <= 2` trivially, so it suffices to build a box witness keeping
both lines. Pick tied bits `p in a0(0) intersect b0(0)` and
`q in a0(1) intersect b0(1)` (nonempty by `tau >= 1`).
If `M_01 != 0` or `M_10 != 0`, order the lines so that the nonzero pair is
backward (or absent): no forward zero arc exists, any certifying box pairs
work (Lemma SB (ii)). If both arcs are zero and `p != q`, the unit pairs
`a = b = {p}` and `a = b = {q}` give `K_01 = 0` in the order `0 < 1`. If
both arcs are zero and `p = q = j`, the scope identity (Lemma SG) makes
`|a0(0) intersect b0(1)|` even, and `j` lies in that set, so there is
`x != j` with `x in a0(0) intersect b0(1)`; take
`a(0) = {j, x}, b(0) = {j}, a(1) = {j}, b(1) = {j, x}`: then
`K_00 = K_11 = 1` and `K_01 = |{j, x} intersect {j, x}| = 0` (mod 2). All
pairs are sub-anchor pairs and `tau >= 1` is used exactly once (Lemma SB
(ii)). QED

Machine corroboration: all 2842 scope-consistent `(a0, b0, Z)` patterns at
`v = 2` with `tau >= 1` give `box = cert = 2` (exhaustive, engine exact),
and PR 2936's `tau = 0` demonstration still reads `cert = 2 > box = 1`.

## Method (smallest instance first; exact arithmetic; no scan-and-trust)

| job | domain | result |
|---|---|---|
| A | v = 2 all `(a0,b0,Z)` with tau >= 1 and Lemma SG parity (2842 configs) | box = cert = 2 in all (PROVEN above) |
| B | v = 3 all `(a0,b0,Z)` up to line/total relabeling (7864 raw -> 3023 canonical) | 2996 with box = cert_max (box = 3 witnessed); 27 combinatorial gap candidates (cert_max = 3 > box = 2) |
| C | 360 realizable tau >= 1 decoders (320 random v = 3..4 with valuations in {0,1,2} bits + 40 GL_3(Z) fixture transforms at v = 3) | 0 box violations; 1788 strict projection drops (E2 1768, E1 466, E4 18, E3 6) |
| D | realization of the 27 candidates (odd/even valuation recipe; per-row exhaustive q, seeded P restarts; alphabets {+-1,+-3}/{+-2,0} then +-5,+-7/+-4,+-6) | 3 realized, all with `cert = 3 > box = 2` (the counterexample family, `M` diagonal); 3 unrealizable (a total enters some `b0` with no `a0` line attaining `m_j`); 21 not found in cap |

Certificate values are exact: `cert`/`box` by the vendored PR 2914 engine's
exhaustive enumerations (`cert_exact`, `box_exact_tolerant`), witnesses
replayed independently (`replay_witness`, `in_box`), and the delivered
counterexample is re-certified by an independent enumeration written from the
section-7 definition of `cert(M)` (not the engine), plus the PROVEN `box <= 2`
rank bound. All arithmetic is int-only.

**Escape classification (job 1).** E1 cosmetic (projection preserves value),
E2 certification escape (kept line certified through non-tied shared bits;
BPP condition (i) fails), E3 arc parity (condition (ii) fails), E4 both. PR
2963's pool is entirely E1; the broader witness pool is E2-dominated, and the
delivered counterexample's attaining witness is an E2 escape that **no**
box witness can replace (rank bound), which is precisely why it is a
counterexample and not a cosmetic escape.

## What is proved, what is checked, what is demoted

- **PROVEN (written proofs in this README):** Lemma V2 (box = cert = 2 at
  v = 2, tau >= 1); Lemma RT (triangular rank) and its shareable-totals
  corollary; the minimal tau >= 1 counterexample at v = 3 (`cert = 3 > 2 =
  box`, with `box <= 2` from the corollary and `cert = 3` from the replayed
  witness); Lemma BPP's conditions (i)+(ii) are **not** without loss at
  `tau >= 1` (the counterexample's every attaining witness violates (i) on
  line 2, since `b0(2)` excludes bit 2 while the only certifying bits for
  line 2 with rank 3 are the three distinct totals).
- **CHECKED (machine, exhaustive or replayed):** the 2842 v = 2 configs; the
  3023 v = 3 combinatorial configs (cert over-approximated by full-label
  `cert_max(Z)`, box exact); the 360 realizable instances and 1788
  projection drops; the 19 cosmetic escapes of PR 2963's pool; the three
  realizations with exact `cert`/`box` and identities; predecessor anchors
  reproduced from pristine copies (`PASS_FG_CALIBRATION tied_min=11/12
  cex_min_1=18/19 mp=9/16 chain=22 reach=0/12,8/19`, `PASS_KB5I_NAMED
  named=9x12`, `PASS_KB5I_BOXREPLAY in-box=12/12`, `PASS_BOX_SEARCH
  bpp-strict-tau0=yes`, PR 2936 tau = 0 demo `cert = 2 > box = 1`).
- **DEMOTED / OPEN:** box-completeness for `tau >= 1` at general v is
  **refuted**, not open; its surviving shareable-class form is open at
  `v >= 3` (21 combinatorial patterns not realized in cap - unrealized is
  not unrealizable). The without-loss reading of Lemma BPP is dead: neither
  projection nor re-pairing preserves the certificate value in general. The
  matched-pivot floor stays demoted. F-star is **not** proved and **not**
  refuted; the box-floor route is untouched (the counterexample has
  `box = 2 = floor(2v/3)`), but the completeness link of the PR 2914 chain is
  gone and any successor must carry the shareable-rank condition.

## Consequences for the family-gap route

PR 2914's route (b) required `cert = box-max` at `tau >= 1` plus a box floor.
Item 2 kills the equality: the certificate can gain exactly the rank that
non-tied shared bits add to `K` (here the third total at level
`c_2 = 1 > gamma`). What survives: `cert >= box` always, so a **box floor**
`box >= floor(2v/3)` on the `tau >= 1` domain would still close F-star there
without any completeness statement; and `cost >= cert` (PR 1590, PROVEN) is
untouched. This counterexample does not falsify F-star (`cert = 3 >= 2`).

## Open next questions

1. **Realizability of the 21 remaining v = 3 combinatorial gap patterns.**
   Why it matters: all 21 sit in the shareable class (`r_box = 3`), so a
   realization gives a shareable-class counterexample and kills
   box-completeness there too; a proof of unrealizability would prove
   box-completeness at v = 3 in the shareable class (the class all prior
   evidence lives in). First step: characterize the `(a0,b0,Z)` patterns
   forced by `M = P Q^T` rank-3 factorizations with prescribed odd/even
   valuations (the odd-term parity of every `M_ts`); the search so far is
   seeded enumeration over alphabets `{+-1,+-3}/{+-2,0}` and
   `{+-1..+-7}/{+-2..+-6,0}` with 10,000-14,000 P-restarts and exhaustive
   q-rows per candidate. Blocked by: no realizability characterization beyond
   Lemma SG + the column-attainment condition.
2. **The shareable-class box-completeness question at v >= 4** (the narrowed
   without-loss question): is `cert = box` when every total has `c_j = gamma`?
   First step: extend the job-B combinatorial enumeration to v = 4 with
   cert-side subset DP instead of full-label over-approximation. Blocker:
   `8^4` label enumeration per configuration times the zero-pattern lattice.

## Reproduce

Standard library only, Python 3.10+ (registered replay: 3.12):

```sh
python3 -B research/fstar-box-withoutloss-seed7f3a1c/verify.py
python3 scripts/research_package.py --package research/fstar-box-withoutloss-seed7f3a1c --check-only
```

`verify.py` recomputes everything from scratch (jobs A-D, the escape
classification, the independent counterexample enumeration, the predecessor
anchor reproduction) and prints `PASS_KJ_*` markers; receipts under `data/`
are digested into `CERTIFICATE.json` (written with `newline="\n"`).

## Exact heads and pins

- Base: `0614abaef427f123d9b844f85a759e64ee3ab29c` (frozen assignment pin =
  canonical `origin/main` at worktree creation, 2026-10-16).
- [PR 2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963) head
  `ee755e682b3b30d493e764d3be50003b13b69b4a` (vendored package tree,
  including its nested predecessor copies of PR 2936 and PR 2914 files).
- [PR 2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936) head
  `f0ef06f13e4de3e50c211c880bdc6891c09620a1`; [PR 2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914)
  head `3f7781efccdf10fa61a1e0a6f11c191579b21280` (through the vendored
  copies; SHA-256 pins in `predecessor/PINS.json`, PR 2963's own 14-file pin
  set re-asserted at every replay, fixture hashes `670ed9...`/`860647...`
  asserted).

## Credit

F-star, `cert(M)`, L8 labellings and the proven chain `cost >= cert(M)`:
`research/root-unit-decoder-lemmas`,
[PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance).
Fixtures `tied_min`/`cex_min_1` and their recorded certificate limits 11/18:
DreamingOfClouds, [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111).
Lemmas SF/MP/RK/AN and the exact-completion engine design: Aaron Wang,
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717). Lemma
MX: Aaron Wang,
[PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747). Zero
digraph machinery: Aaron Wang,
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774). Lemmas
SC/SG and the canonical reduced normalization: Aaron Wang,
[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869). chi(Z)
machinery: Aaron Wang,
[PR 2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890).
Family-gap definition and Lemma CT: Aaron Wang,
[PR 2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901).
Sub-anchor box, Lemmas SB/LB: Aaron Wang,
[PR 2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914). Lemma
BPP, the `tau = 0` demonstration and the `tau >= 1` necessity pin: Aaron
Wang, [PR 2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936).
The 12 tied_min v = 11 sub-decoders and the box weak-cell closure: Aaron
Wang, [PR 2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963).
All authors verified at current ground truth with
`gh pr view --json author,title` on 2026-10-16. New content here: Lemma V2,
Lemma RT and the shareable-totals corollary, the minimal v = 3
counterexample, the escape classification (E1-E4), and the v = 2/v = 3
combinatorial enumerations.

## Freshness and collision checks

Pair-collision checks (toolkit `disc-comments --grep`, discussions 1317 and
1166, nested replies) at entry found no live claim on this object; the last
family-gap activity is KB5i's FINDING/DONE/RELEASED (PR 2963,
2026-10-16 14:36:56 UTC), which this assignment extends. The entry overlap
survey (`find_overlap.py`, object proper names and synonyms, `--refresh`,
complete pagination: 240 open PRs, 1660 discussion records at 14:44-14:45
UTC) found only the known F-star lineage and unrelated traffic.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no model named; no independent human review claimed). No kappa, supplier,
word or moment claim.
