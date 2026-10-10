# Ninety-one collective response-kernel families on PR #283's gen4 word

**Claim.** On PR #283's composed gen4 word (PR #276's bit word with sixteen sinks, 741 kernel pivots, PR #279's
retimings, 29 transported entrances, 440 early restorations and 220 target squares), adding 91 collective
response-kernel families (87 quadruples, 4 triples; entrance rank 456) on helpers disjoint from every helper PR #283
touches, at its global cut, gives a legal word of the same model with literal stock 2,549,300 (120 replicas) and
κ = 181572923056461298166587/(25·10²⁵) = 7.26291692225845·10⁻⁴ by PR #283's fixed-prime price, every stage of its
verifier passing with the receipts regenerated.

## 1. The mechanism (PR #254/#259/#272/#283, unchanged)

An untouched dirty helper acts on the targets only through its compensation reads, so its complete target response
R ∈ F₂^1760 is a column of the prefix map. A family (p; d₁..d_k) with R_p = R_{d₁} ⊕ … ⊕ R_{d_k} and a common
nondegenerate subspace E inside all members' first required frames admits the rewrite: p starts at E with its
compensation reads deleted; each donor is moved to E at the cut and absorbs p there (Q = I + Σ e_{d_j} e_pᵀ); the old
word resumes; Q⁻¹ is paid at the full frame; the omitted response of p cancels against the induced change. PR #283's
`kernel-transform` admits any such family whose entrance is nondegenerate under its exact chart audit, whose members
are untouched before the cut, and whose shared donors have nested entrance chains.

## 2. The families

On the gen4 word the 13,944 plain dirty helpers have 12,352 distinct responses with F₂ rank 1,760. Among the
low-weight F₂ circuits (1,616 twin pairs, 5,245 helper triples, 38,633 quadruples after twin expansion; quintuples are
never net-positive, a fourth donor always outweighing the pivot), those with a nondegenerate common entrance
(cleared Gram 9⟨x, y⟩ − Σx·Σy ≠ 0 on the intersection of first frames) number 616 pairs, 1,131 triples and 4,490
quadruples. Under the deficit-fixed ledger (φ(r) = r·ln(120/r); the pivot gains φ(r_p − e) − φ(r_p), each donor
costs φ(e) + φ(r_d − e) − φ(r_d), a shared donor's lift once along its chain) the net-positive ones are packed greedily
with disjoint pivots. On helpers outside PR #283's 1,612 kernel roles, 16 sinks and 60 transported candidates, 91
families remain net-positive: (3, 3, 3, 3) e = 2 × 49, (5, 5, 5, 5) e = 4 × 10, (10/11/12/14/16/17)⁴ with e = r − 1 or
r − 2, four triples; φ-gain −302.3 per invocation, 14 donors shared along nested chains. All 91 are legal at PR #283's
global cut 520,031 (every member's last compensation read before it, every first touch after it), so no per-family
cut was needed; their rows are appended to `inputs/kernel-original.json` in PR #283's schema and remapped through
its sink transform like every other row (none of our members is a sink).

The ledger predicted PR #283's price 7.26111340·10⁻⁴ → 7.26291688·10⁻⁴ before the fixed-prime refinement; the
package's pricers give exactly that (coarse 7.26819572·10⁻⁴, price κ 7.26291688·10⁻⁴, fixed-prime κ
7.26291692225845·10⁻⁴).

## 3. The bank allocator

A pivot of entrance rank e has residual width 24 − e. PR #283 tiles each residual group with four r-blocks and
(30 − r) rank-4 fillers per bank; with 17 new residual widths the fillers needed (30,060 copies) exceed what its
rank-4 pool leaves (10,380). The allocator now walks the new residual groups in descending r and, for a group that
would exhaust the pool, uses b = (30 − r) mod 3 rank-4 and 4·⌊(30 − r)/3⌋ rank-3 fillers per bank (4r + 4b + 12k =
120), reducing the 3⁴⁰ bank count accordingly; both remainders and the pool are asserted, every bank is width 120 and
full, and when the pool suffices the allocation is byte for byte PR #283's. In this word only PR #283's own rank-19
transported entrances (residual 6) switch, to [6 × 4, 3 × 32] in 870 banks; the 3⁴⁰ banks fall from 2,118 to 1,422,
the 4³⁰ count stays 40. Receipt fields `rank3_filler_residual_ranks` and `rank3_filler_copies` record it.

## 4. What is checked

Every stage of PR #283's verifier on the new word: the nine PR #276 stages on the vendored immutable package; sink
transform and audit; kernel transform (832 pivots, 13,136 reads removed, 3,462 Q/Q⁻¹ gates, all 19,914 columns
forward and inverse, omitted-operation controls non-vacuous); retiming (880 gates), transport (29), restoration
(440), target squares (220); independent legality (source owners, COPY lifetimes, nested chains, final frames) and
prefix (1,464,320 kernel equalities, 41.8·10⁶ identity bits on 1,956 helpers); global columns (23,434); bank review
with the new allocation (literal stock 2,549,300, 4,923,000 assignments, chart bound unchanged: max 312 factors);
price, fixed-prime price (47 constraints, adjacent grid rejected) and finite invoice. The families were also
replayed on the bare gen4 word by `discovery/replay_families.py` with per-family omitted-setup and omitted-restore
controls. Runtime 16 minutes (macOS/clang) for the whole verifier.

## 5. Not claimed

No Lean certificate; the public all-size interfaces retained by PR #276/#283 remain hypotheses; PR #283's own
correctness claims are inherited, not re-proved. Not composed: on the bare gen4 word the same census gives a
695-entry selection (416 pairs, 24 twin pairs entering on 16-dimensional intersections, 255 families; model κ
7.24029·10⁻⁴ before any retiming) whose helpers largely coincide with PR #283's; the 24 e = 16 pairs are inside its
helper set and were not re-derived on its word.
