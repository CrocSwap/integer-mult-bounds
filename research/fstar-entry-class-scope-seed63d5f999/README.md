# fstar-entry-class-scope-seed63d5f999

**Settling the statement of F-star residue class (iii) "non-dyadic entries" (no
kappa, no frontier change).** Open problem F-star of
`research/root-unit-decoder-lemmas` (section 7, OPEN) asks whether
`cert(M) >= floor(2v/3)` holds for every exact 3-total rational decoder
`M = sum_{j<=3} p_j q_j^T`. [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717)
proved Lemma AN (the mod-2 anchor) and demoted a three-part residue; its item
(c) reads: "for non-dyadic entries (odd primes in denominators) the mod-2
anchor does not apply at all".
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) recorded
this class as mathematically murky: odd-denominator rationals are 2-integral,
so the anchor may already cover them. This package determines the precise
scope of Lemma AN and Lemma MX with respect to entry denominators and
**collapses residue class (iii)**: it is mis-stated and empty as an
obstruction, and it merges into the cancellation residue that class (i)
already attacks. **F-star itself is not proved and not refuted here.** Every
claim below is labelled PROVEN, CHECKED or DEMOTED.

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
decoder. Write `v_2` for the 2-adic valuation of a nonzero rational
(`v_2(a/b) = v_2(a) - v_2(b)` in lowest terms; `Z_(2) = {x : v_2(x) >= 0}` is
the ring of odd-denominator rationals, and `Z[1/2]` is the ring of dyadic
rationals).

## 1. Lemma SC: the exact scope of Lemma AN's normalization hypothesis — PROVEN

Fix a factorization `M = sum_j p_j q_j^T`. For total `j` define

```
m_j = min { v_2(p_j(t)) : p_j(t) != 0 },   n_j = min { v_2(q_j(s)) : q_j(s) != 0 },
c_j = m_j + n_j.
```

Zero rank-one totals may be discarded: equivalently assign them content
`+infinity` and ignore them in the minimum defining `gamma`. Nonzero diagonal
entries ensure at least one nonzero total. The displayed finite minima below
refer to nonzero totals.

> **Lemma SC.** (a) `c_j = min { v_2(p_j(t) q_j(s)) : p_j(t) q_j(s) != 0 }`, the
> 2-adic content of the rank-1 matrix `p_j q_j^T`; `c_j` is invariant under
> every rescaling `(p_j, q_j) -> (lambda p_j, lambda^{-1} q_j)` of the total.
> (b) A per-total power-of-two rescaling makes both factors 2-integral (all
> entries in `Z_(2)`) if and only if `c_j >= 0` for every `j`. In particular
> Lemma AN's hypothesis ("after per-total powers of two the factorization is
> 2-integral") holds exactly on the factorizations with `c_j >= 0` for all
> totals.

*Proof.* (a) The nonzero entries of `p_j q_j^T` are exactly the products
`p_j(t) q_j(s)` with both factors nonzero, so the minimum valuation of the
nonzero entries is `min_t v_2(p_j(t)) + min_s v_2(q_j(s)) = m_j + n_j`. Under
`(p_j, q_j) -> (lambda p_j, lambda^{-1} q_j)` the two minima shift by
`v_2(lambda)` and `-v_2(lambda)`, so `c_j` is unchanged. (b) After the
rescaling `(2^alpha p_j, 2^{-alpha} q_j)` the two minima are `m_j + alpha` and
`n_j - alpha`; both are nonnegative for some integer `alpha` exactly when the
interval `[-m_j, n_j]` is nonempty, i.e. `c_j = m_j + n_j >= 0`. `QED`

**Entry-class coverage (PROVEN, immediate from Lemma SC).** If all entries lie
in `Z_(2)` (odd denominators, i.e. exactly the rationals whose denominators
contain odd primes but no factor of 2, and every integer), then
`m_j, n_j >= 0`, so `c_j >= 0` and Lemma AN applies verbatim, with no
rescaling at all. If entries lie in `Z[1/2]` (dyadic), Lemma AN applies exactly
when every total has `c_j >= 0`; dyadic entryhood alone does not imply this.
For general `Q` the same per-total criterion applies. This settles the
demoted claim (c) of PR 2717 as **mis-stated**: entries with odd denominators are 2-integral and the mod-2 anchor applies
without any change. Non-dyadic rationals with an even denominator, such as
`1/6`, instead fall under the general rational criterion; what can fail is not the denominator's
odd part but the total's 2-adic content.

## 2. Lemma SG: the scale-invariant anchor and its exact reach — PROVEN

Let `gamma = min_j c_j` for the given factorization.

> **Lemma SG.** (a) After the single global rescaling `M -> 2^{-gamma} M` the
> factorization admits a per-total 2-integral normalization, for every rational
> factorization of every entry class; Lemma AN applies to it verbatim. (b) With
> the reduced labels `K_ts = 2^{-gamma} M_ts mod 2`, so `K_ts = 0` at every
> incidence and `K_tt = 1` exactly on `S_gamma = {t : v_2(M_tt) = gamma}`;
> hence `cert(M) >= |S_gamma|`. (c) The reach is exact: every line satisfies
> `v_2(M_tt) >= gamma`, and no mod-2 anchor built from any power-of-two
> normalization of any per-total rescaling of this factorization anchors a line
> outside `S_gamma`. So the anchor family's reach on a fixed factorization is
> exactly `S_gamma`.

*Proof.* (a) The rescaled totals have contents `c_j - gamma >= 0`; apply Lemma
SC (b) per total. (b) The mod-2 reduction of a 2-integral factorization
satisfies `sum_j a_j(t) b_j(s) = 2^{-gamma} M_ts mod 2`; at an incidence
`M_ts = 0` this is 0, and on the diagonal it is 1 exactly when
`v_2(M_tt) - gamma = 0`. The set `S_gamma` is then feasible in any order.
(c) Each summand `p_j(t) q_j(t)` of `M_tt` has valuation at least `c_j >=
gamma`, so `v_2(M_tt) >= gamma`. A power-of-two normalization at global
exponent `s` needs `c_j + s >= 0` for every `j`, i.e. `s >= -gamma`, and its
anchor marks only lines with `v_2(M_tt) = -s`; combined with `v_2(M_tt) >=
gamma` this forces `v_2(M_tt) = gamma` and `s = -gamma`. `QED`

**Corollary (repaired form of Lemma AN's corollary).** `cert(M) >= v - #{t :
v_2(M_tt) > gamma}`, and F-star holds on `M` whenever at most `floor(v/3)`
lines have `v_2(M_tt) > gamma` (the *cancellation lines*). Lemma AN's count
`#{t : M_tt odd}` is the special case `gamma = 0` of `|S_gamma|`; when
`gamma != 0` the two counts differ (control SC2 below: `M = 2 I_3` has naive
count 0 and reach 3). PR 2717's corollary sentence ("F-star holds for dyadic
decoders with at most one-third even diagonals") is correct under Lemma AN's
stated hypothesis, but dyadic entries do not by themselves deliver that
hypothesis (control SC1: `p = q = (1/2)(1,1)` on two lines has `c_1 = -2`);
Lemma SG closes that normalization gap for all dyadic, and in fact all
rational, decoders.

## 3. Pattern invariance: F-star is entry-class-independent — PROVEN

> **Proposition.** For every `lambda` in `Q*`, `lambda M` has the same
> `(pi, sigma, Z)` as `M`, hence `cert(lambda M) = cert(M)`, and
> `cost_B(lambda M) = cost_B(M)` for every admissible pairing `B`. Moreover
> every rational decoder's `(pi, sigma, Z)` is realized by an integer-entry
> factorization.

*Proof.* Per-total scaling `(p_j, q_j) -> (a_j p_j, b_j q_j)` with `a_j b_j =
lambda` changes no support (`pi`, `sigma` are zero patterns of the factors)
and multiplies `M` by `lambda`, which changes no off-diagonal zero. The chain
cost uses only `R_j = supp p_j`, `A_j = supp q_j` and F2 ranks of submatrices
of `B`, all unchanged. For the integer realization, let `d` be the least
common multiple of the denominators of all entries of all `p_j` and `q_j`;
then `(d p_j)(d q_j)^T = d^2 p_j q_j^T`, the factorization `d^2 M = sum_j
(d p_j)(d q_j)^T` has integer factors with the same supports, and `d^2 M` has
the same zero pattern and nonzero diagonal. `QED`

Consequences: the set of realizable `(pi, sigma, Z)` is identical over `Z`,
`Z[1/2]`, `Z_(2)` and `Q`, and F-star holds for all rational decoders if and
only if it holds for integer-entry decoders. No residue of F-star can live in
entry denominators: **residue class (iii) is empty as an obstruction.** Entry
classes gate only coefficient-dependent proof tools (the anchors); the
combinatorial question is shared.

## 4. Scope of Lemma MX and the coefficient-free lemmas — PROVEN (corollary)

Lemma MX (PR 2747) mixes three line sets: `A` (anchor lines, labelled by the
mod-2 anchor `a0`, `b0`), `U` (one-sided repairs of the anchor labels) and `T`
(matched pivots `a(t) = b(t) = e_{c(t)}`, `c(t)` in `D(t)`), bounding
`cert(M) >= |A| + |U| + sum_i MAS(Z[C_i])`. Its `A` and `U` parts use the
anchor labels; by Lemma SG those exist for every rational decoder after one
global rescaling, with `A` a subset of `S_gamma`. Its `T` part uses only
supports and the zero digraph. Lemmas SF, MP and RK (PR 2717) are
coefficient-free entirely. So none of the four lemmas carries an
entry-denominator restriction; only the anchor count `|S_gamma|` varies with
the coefficients. No necessity or "exactly when" claim is made for any lemma
hypothesis; each remains sufficient as stated. The only iff statements in this
package are Lemma SC (b) and Lemma SG (c), both proved in both directions.

## 5. Fixture settlement — CHECKED

`verify.py`, stdlib, deterministic; certificate digest `39f5c167c495f457`.

| quantity | `tied_min` (12 lines) | `cex_min_1` (19 lines) |
|---|---|---|
| entry class of `p, q` | integer | integer |
| per-total contents `c_j` | 0, 0, 0 | 0, 0, 0 |
| `gamma` | 0 | 0 |
| `v_2(M_tt)` per line | 1 on all 12 lines | 0 on 8 lines, 1 on 11 lines |
| anchor reach `S_gamma` | 0 of 12 | 8 of 19 (lines 0, 4, 5, 6, 8, 11, 14, 15) |
| PR 2747 `anchor_good` | 0 | 8 |
| anchor-untouchable (`v_2(M_tt) > gamma`) | 12 of 12 | 11 of 19 |
| PR 2747 `tied_isotropic` | 12 | 11 |
| scope identity `K_ts = M_ts mod 2` | checked | checked |
| Lemma AN hypothesis (`c_j >= 0`) | holds | holds |

Both fixtures are integer-entry decoders (`Z`-entries), so class (iii) is
already empty on the canonical data, and on both fixtures the anchor reach
equals PR 2747's `anchor_good` count exactly while the anchor-untouchable set
equals its `tied_isotropic` count exactly (it records 0 `repairable_1s` on
both). The merge of class (iii) into the cancellation residue is therefore
exact on both canonical instances. On `tied_min` every diagonal sits at
`v_2(M_tt) = 1 > gamma = 0`: all 12 lines are cancellation lines, which is why
the anchor is vacuous there.

Calibration anchors, all reproduced:

| anchor | recorded by | recorded | here |
|---|---|---|---|
| `tied_min` one-copy L8 | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds (CP-SAT, CHECKED (recorded)) | 11 | 11 (hill-climb re-found, replayed; upper bound `v = 12`) |
| `cex_min_1` one-copy L8 | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds (CP-SAT, CHECKED (recorded)) | 18 | 18 (stored witness replayed) |
| chain on the stored pairing | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds | 22 (`10+6+6`) | 22 (admissibility re-checked) |
| Lemma MP on `tied_min` | [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) by Aaron Wang (navinor) | 9 (4096 pivot maps) | 9 (exhaustive) |
| Lemma MP on `cex_min_1` | [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) by Aaron Wang (navinor) | 16 (6144 pivot maps) | 16 (exhaustive) |
| Lemma MX on `tied_min` / `cex_min_1` | [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) by Aaron Wang (navinor) | 9 / 16 | 9 / 16 (all-T wins; 2048 mixed maps evaluated on `cex_min_1`, matching its recorded mixing obstruction) |
| `chi(Z)` unconstrained | [PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) by Aaron Wang (navinor) | 3 / 3 | 3 (exhaustive subset DP) / 3 (3-colouring decision plus a mutual-zero triangle forcing `>= 3`) |
| 3-dichromatic with allowed colours `D(t)` | [PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) by Aaron Wang (navinor) | no / no | no / no (matched-pivot value `9 < 12`, `16 < 19`) |

## 6. Smallest-first falsifier search in the entry-class domain — CHECKED (scoped negative)

Smallest falsifying instance first (`v` ascending from 3), three generator
families aimed at the statement under audit, deterministic seeds per instance
in `CERTIFICATE.json`. Falsifier criterion: an explicit admissible pairing `B`
with chain cost below `floor(2v/3)`, or exact `cert` below threshold where
exhaustive a-enumeration terminates. An instance is *certified* when a
machine-checked L8 witness of size at or above `floor(2v/3)` is replayed by
the independent checker, which rules a falsifier out on that instance.

| family | entries | instances | class | Lemma AN hypothesis | falsifiers | certified |
|---|---|---:|---|---|---:|---:|
| `evenden` | halves, quarters | 28 | dyadic | fails on 28 (`gamma < 0`) | 0 | 28 |
| `oddden` | thirds, fifths | 28 | 2-integral (odd denominators) | holds on 28 | 0 | 28 |
| `mixed` | halves and thirds | 28 | general `Q` | fails on 28 (`gamma < 0`) | 0 | 28 |

Totals: 84 instances, `v = 3..10`, 0 falsifiers, 84 of 84 certified at or
above `floor(2v/3)` (minimum best-known ratio 1.0; exact `cert = v` on all 36
instances where exhaustive a-enumeration terminates, `v = 3..5`). 56 instances
lie outside Lemma AN's literal hypothesis (negative total contents) and were
covered by Lemma SG's scaling; 66 of 84 have anchor reach below threshold, so
the certificate there was carried by the coefficient-free matched-pivot or
general-labelling witness, exactly as Sections 3-4 predict. The scope identity
`K_ts = M_ts mod 2` was machine-checked on every instance.

**Early kill and the exact obstruction (recorded).** By the pattern-invariance
proposition the entry-class axis cannot produce a falsifier beyond the shared
combinatorial `(pi, sigma, Z)` space, so the search was a regression test of
the scope machinery rather than a new domain; after 84 instances with zero
falsifiers and per-instance certificates the search was stopped at the
declared domain. The falsifier criterion (admissible-B chain cost) was armed
but never needed to fire. The true residual obstruction of the F-star residue
is exactly: (i-prime) the cancellation lines `{t : v_2(M_tt) > gamma}`, which
now contains PR 2747's tied-minimum/repair/ordering problem and the anchor-
count axis of Lemma AN; and (ii) the zero-digraph structure of PR 2774. Entry
denominators contribute nothing.

## 7. What is proved, what is checked, what is demoted (the merged residue)

- **PROVEN:** Lemma SC (the exact per-total criterion for Lemma AN's
  normalization hypothesis, with the entry-class coverage of `Z_(2)`, `Z[1/2]`
  and `Q`); Lemma SG (the scale-invariant anchor with exact reach
  `S_gamma = {t : v_2(M_tt) = gamma}`, subsuming Lemma AN's count); the
  pattern-invariance proposition (F-star is entry-class-independent; every
  rational pattern has an integer representative); the Lemma MX / SF / MP / RK
  scope remark (no entry-denominator restriction).
- **CHECKED (machine, `verify.py`, stdlib, deterministic, ~5 s):** controls
  (brute-force-over-all-labellings agreement 3/3 at `v = 3`, diagonal decoder
  `cert = 3`, corrupted-witness rejection 2/2, subset-DP MAS hand values 3/3,
  dichromatic hand values 4/4, `MP = 3` on the diagonal decoder) and four scope
  controls (SC1: the dyadic instance `p = q = (1/2)(1,1)` where Lemma AN's
  hypothesis fails with `c = -2` and the scale-invariant anchor still anchors
  both lines; SC2: `M = 2 I_3` where the naive odd-diagonal count is 0 and the
  reach is 3; SC3: an odd-denominator instance where the anchor applies
  verbatim; SC4: reach-witness replay 3/3); the fixture settlement and every
  calibration anchor of Section 5; and the 84-instance search of Section 6.
- **DEMOTED / OPEN:** residue class (iii) as stated is demoted: mis-stated
  (odd primes in denominators are 2-integral and anchor-covered verbatim) and
  empty as an obstruction (no residue can live in entry denominators because
  `cert(M)` and the chain are entry-class-invariant). The residue classification
  is renamed to two classes: (i-prime) the cancellation lines
  `{t : v_2(M_tt) > gamma}` (PR 2747's repair/ordering territory, now including
  the anchor-count axis), and (ii) the zero digraphs (PR 2774's territory).
  F-star for general rational decoders is neither proved nor refuted. No
  necessity claim is made beyond the proved directions of Lemmas SC and SG. The
  fixture limits 11/18 rest on PR 2111's recorded CP-SAT optimality, not
  re-verified here. `chi(Z) >= 4` above `v = 13` remains budget-limited.

## Open next questions

1. **Anchor plus repairs against the threshold.** Is
   `|S_gamma| + (PR 2747 repairable count) >= floor(2v/3)` for every rank-3
   decoder? Why it matters: it would prove F-star for every entry class through
   the anchor route alone, with no zero-digraph hypothesis; the fixtures show
   the bare anchor is short (0 of 12 on `tied_min`), so repairs or pivots must
   carry the residue. First step: enumerate tied-heavy decoders at `v <= 8`
   with controlled `gamma` (all diagonals above `gamma`, then one, then two
   lines at `gamma`) and test the anchor-plus-repair count. Blocker: nothing
   structural; needs a dedicated enumeration session.
2. **The best factorization for the anchor reach.** `gamma` and `S_gamma`
   depend on the chosen 3-total factorization; a `GL_3(Q)` re-split of the same
   `M` can change both. What is `max |S_gamma|` over factorizations of a fixed
   pattern? Why it matters: it would sharpen Lemma SG from "for every
   factorization" to a pattern-level bound. First step: sample `GL_3(Z)`
   re-splits of the fixtures' stored factorizations and track `gamma` and the
   reach, checking consistency with the recorded limits 11/18. Blocker: nothing
   structural; small linear algebra over `Z_(2)`.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -B research/fstar-entry-class-scope-seed63d5f999/verify.py
python3 scripts/research_package.py --package research/fstar-entry-class-scope-seed63d5f999 --check-only
python3.12 scripts/research_package.py --package research/fstar-entry-class-scope-seed63d5f999
```

Expected markers: `PASS_FSC_CONTROLS`, `PASS_FSC_FIXTURES`, `PASS_FSC_SEARCH`,
`PASS_FSTAR_ENTRY_CLASS_SCOPE`, and `CERTIFICATE.json` with digest
`39f5c167c495f457` (full digest printed by the run). The registered CPython
3.12 replay prints `PASS_REGISTERED_RESEARCH_PACKAGE
research/fstar-entry-class-scope-seed63d5f999 outcome=completed`. `make` is
not installed on the authoring host; the commands above are the underlying
ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain
`cost >= sum_j r_j >= cert(M)` are from the merged
`research/root-unit-decoder-lemmas` package
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds, with Claude Opus 5.5 (Anthropic) via Claude Code
assistance). The rank-3 configuration model, the named instances `tied_min`
and `cex_min_1`, their recorded one-copy certificate limits (11 and 18, CP-SAT,
CHECKED (recorded)) and the stored cost-22 pairing `data/cex_min_1.B22.json`
are DreamingOfClouds' work in
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) and
[PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162);
`data/tied_min.json` and `data/cex_min_1.json` are byte-identical copies of
their data files (sha256
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` and
`86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`). The
residue statement, Lemmas SF/MP/RK/AN and the exact-completion engine design
this package adapts are Aaron Wang's work in
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717); Lemma MX
and the class-(i) closure are Aaron Wang's
[PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747); the
class-(ii) machinery and the record that class (iii) is murky are Aaron Wang's
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774); the
falsifier census frontier is Aaron Wang's
[PR 2335](https://github.com/CrocSwap/integer-mult-bounds/pull/2335); the
exact cost 12 of `tied_min` is Aaron Wang's
[PR 2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379); the
exact cost 21 of `cex_min_1` is Nick Petalas'
[PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206). The
stored 18-witness `data/cex_min_1.witness.json` is from PR 2717's package.
[PR 2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613) by
thakrarsagar is a same-motif, different-object neighbor (a mod-2 2-integral
rank floor for a bit register model); it does not state the entry-class scope
of Lemma AN/MX. This package does not claim their results; the new content is
Lemmas SC and SG with their proofs, the pattern-invariance proposition, the
Lemma MX scope remark, the entry-class settlement of the two fixtures and the
smallest-first entry-class search.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no independent human review claimed). New work in this package is Apache-2.0.

## Maintainer integration correction

The three-colour decision helper now explores the remaining allowed colours
after a failed branch and propagates budget exhaustion as unknown. The original
helper rejected the bidirected eight-vertex crown graph despite its explicit
two-colouring. This is a regression of the helper, not a rational-decoder
counterexample or a refutation of F-star. The review retains that witness and
checks the corrected helper against exhaustive small-graph/list-colouring
controls before replaying the package. The table above now names the positive
`3-dichromatic with allowed colours` predicate that its stored false values
actually describe. No stronger F-star conclusion follows.
