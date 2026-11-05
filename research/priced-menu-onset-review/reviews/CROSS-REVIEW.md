# Cross-review of the sealed code-boundary draft

Reviewed `CODE-BOUNDARY-DRAFT.md` (provided sealed SHA256 `98785e5be014d820e5675b106c05afbd35324205bf908e5f34a0b6bb57de4513`) against my already sealed `DERIVATION-DRAFT.md` (`d3d794a3ad175356ea49837a168dd05b1e9282a4ee69153523f79ed7f69c6a1e`). The source `inputs/pricing.py` was additionally read as inert text after the two draft seals. No source or scientific program was imported, compiled or executed; no sealed original was edited.

**Verdict: no material mathematical contradiction or implementation-blocking gap found.** The peer's implementation-domain qualification is explicit and belongs in the final conclusion. One written adversarial-control statement should be narrowed; it does not affect the healthy formula or the theorem.

## Agreement on the proof-relevant boundaries

- Both drafts retain positive integer widths/jobs, nonempty finite cuts/menus, exact rational additive prices, completed separated cuts, and nonnegative excesses. Multiple cheapest widths are retained in the subgroup argument. Neither substitutes a single cheapest anchor for the whole cheapest subgroup.
- The lexicographic second coordinate is the minimum actual amount attaining the minimum loss in that anchor residue. It is not an arbitrarily selected attaining path or a unique count vector. The peer correctly disclaims count-vector tie uniqueness.
- The anchor criterion is an all-n iff in a reachable residue, including n=0. Below the cutoff an amount can be an expensive fill or a hole. An unreachable residue remains a permanent hole. The peer does not collapse these cases.
- D divisibility means all sampled residues are reachable, not that every current amount is feasible. The common D filter makes all direct `refined[s]` accesses finite. On its complement, both total sequences equal infinity; no subtraction of two infinities is used.
- On D multiples, all predicted losses are finite and every actual deviation is nonnegative or infinite. Thus one cut's deviation cannot cancel. This justifies the union of exceptions after filtering, rather than an unfiltered maximum of the separate-cut onsets.
- The zero set of the predicted sequence proves that every eventual period is divisible by P. Mathematical floor, nonnegative remainder, u=0, modulus1 and the absence of any positive exception are explicitly treated.

The peer's §5 directly rules out an earlier onset for period P. For the final unqualified phrase “earliest positive onset of periodicity”, include the short stronger step from my §6: every eventual T is a multiple of P; at a last exception L>0, the value at L+T is already its periodic prediction, while E(L) differs. Hence no larger period can permit an earlier onset either. This supplies an explicit quantifier already supported by the peer's own least-period argument, rather than correcting a counterexample.

## Stable/reiterable input is an explicit API qualification

Peer §1 expressly restricts the reviewed code path to nonempty stable reiterable cut collections, ordinarily lists/tuples, containing valid Menu objects whose attributes remain unchanged. Static text confirms the reason: `validate_cuts` consumes `cuts` and the subsequent routines iterate it again. A one-shot generator is not certified. The theorem, however, quantifies over a fixed finite indexed family; it has no promise about the behavior of an arbitrary Python iterator or mutated object. The qualification therefore narrows the code assertion without creating a theorem gap.

The low-level `residue_table` domain is also stated separately: positive modulus/widths and aligned nonnegative exact losses. Valid constructed Menus establish these conditions. The note does not claim that the low-level helper validates arbitrary malformed input. Root's authenticated source `checks.py` list caller is additional caller-binding evidence; I did not execute that caller or independently repeat its acquisition here.

## Minor finding: a written control does not detect truncation alone

Peer §6.2 says that replacing floor by truncation, or clamping an intermediate value to a positive candidate, could manufacture an exception in the singleton/no-exception boundary. For that stated singleton, the sampled residue is zero and A0=0. Mathematical floor gives limit=-1; truncating (-1)/step toward zero instead gives limit=0 (when step>1). With u=0, the subsequent class formula yields last_t=0, which `max(0,...)` still discards. Thus **truncation alone does not manufacture a positive exception in this written example**. An independently introduced positive clamp can do so, but is a different fault.

Recommended publication correction: preserve floor as the exact meaning of the formula, and state that this example checks no spurious positive exception from the implemented expression; do not present it as a distinguishing control for truncation alone. This is a low-severity scope/precision correction to an unexecuted adversarial example, not a flaw in `first_periodic_replication` or in the proved onset.

The peer's other hand examples are consistent with the theorem's case distinctions: the widths4/6 example separates a finite early hole from permanent odd-residue impossibility; the widths4/7 with q=2 example uses the reduced sampling class count; and the multiple-cheapest masking example remains explicitly credited source material. No runtime outcome was independently observed in this review.

## Final scope

The written and static code arguments support the stated arithmetic conclusion on the explicitly qualified code input domain. They do not establish the full Pareto routine, a new census, source fixture replay, physical compatibility or prices, the rank-12 threshold, human/formal-kernel acceptance, or selected-framework admission. Source theorem credit remains SHIN09-git, with Nick Petalas6658, Mihir Srivastava4507, and classical residue/knapsack methods retained.
