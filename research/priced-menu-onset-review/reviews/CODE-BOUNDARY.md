# Independent source-aware residue/onset code audit

## Status and evidence boundary

PASS, conditional on the stated finite separated-cut arithmetic contract and ordinary list/tuple API described below. I found no mathematical or implementation mismatch in `residue_table`, construction of `Menu.refined`, or `first_periodic_replication` against PROOF §§2–3. This is a written source-aware AI audit, not an executed replay, independent census, human review, proof-kernel check or physical billing admission.

Read as inert text only: the pinned source `PROOF.md`, `pricing.py` and `README.md`. No scientific source, constructor, census, Lean/proof kernel, test or numeric experiment was imported, compiled or executed. No peer draft was read before this note's seal. Hash/byte/time utilities are provenance operations only. Source fixtures and formulas remain credited to SHIN09-git/source PR6689; classical shortest paths, Apéry sets and knapsack periodicity are prior methods. Nick Petalas6658 supplies the compatible-menu question and Mihir Srivastava4507 the separated chronological-cut setting.

Scope excludes the complete Pareto proof/code, rank12 fixture or invoice, runtime complexity improvements, any full caller/native construction and selected-framework admission. In particular none of routing, storage, precision, owned lifetimes or setup-sharing semantics follows from this arithmetic audit.

## 1. Exact API domain and arithmetic

`Menu.__init__` (pricing.py54–79) materializes its program iterable, requires a nonempty menu, rejects nonpositive widths and non-integer widths including bool, requires positive exact int/Fraction prices and rejects bool/float prices, then rejects duplicate widths. Sorting supplies the smallest cheapest width as `anchor`. Prices are converted to Fraction before computing densities or losses: each loss is exactly nonnegative and at least one is exactly zero. Both gcds and every modulus are positive integers. Multiple cheapest widths are retained, not collapsed to the anchor alone.

The cut routines need a nonempty, stable reiterable collection of `(q, Menu)` pairs, with q a positive genuine integer and the Menu objects not modified after construction. `validate_cuts` rejects bool/nonpositive multiplicities and nonpositive/non-integer parent, but does not check the Menu type or freeze its attributes. It iterates `cuts`, so a one-shot generator is outside the certified caller domain: validation would consume it before later passes. This is an API qualification, not a source theorem counterexample. The proof's finite indexed family can and should be supplied as a list/tuple. Direct calls to the low-level `residue_table` also need positive modulus/widths, aligned lengths and nonnegative exact losses; that helper does not independently validate those hypotheses. Its actual Menu calls establish them.

The reviewed onset does not depend on the parent productive width. The parent only scales the normalized bill. Positive q and widths imply `step>0` and `classes>=1`, excluding division/modulo by zero in the reviewed path. Python integers/Fractions prevent rounding or overflow within the exact mathematical resource model; this is not a promise that arbitrary huge moduli fit a fixed machine or resource budget.

## 2. `residue_table`: least loss and then least attaining size

At lines20–22 the empty path labels residue0 by `(0,0)` and the all-zero count vector. Unreachable residues remain `None`; infinity is represented by absence rather than a large finite sentinel. Each relaxation appends one real menu invocation, changes residue by its positive width modulo d, adds its exact loss/width, and increments that invocation's count. Thus every stored label has actual nonnegative integer counts witnessing both its size and loss.

Weights `(e_w,w)` are strictly positive in lexicographic order even when e_w=0, since w>0. Removing a cycle strictly improves a path label, so a minimal label has a simple representative; there are finitely many candidates relevant to any minimum. Dijkstra ordering by exact `(loss,size,residue)` and the stale `(loss,size)` check preserve least lexicographic labels. The residue coordinate is merely a heap tie-break. Strict relaxation does not replace an equal `(loss,size)` by a different count vector: the contract is one attaining vector, not a uniquely or lexicographically minimal count vector. Therefore this choice is harmless and deterministic for the ordered menu; no proof should claim a stronger count-vector tie rule.

Nonnegative widths generate in the finite cyclic group the subgroup determined by their gcd with the modulus. Both actual moduli d=h and d=b are multiples of g=gcd(W), and g divides all widths, so the reachable residues are precisely multiples of g. The heap never contains an entry for a residue without a stored label, so the stale-entry `.loss/.size` access is safe. Finite rational costs, including equal-density ties, do not change this argument.

The proof's zero-loss fact is correct: a zero-loss path uses cheapest widths, all divisible by h. Thus modulo h only residue0 has finite zero loss. Conversely residue0 has the empty path, independently of other zero-loss cycles.

## 3. `Menu.refined`: why the anchor size is an exact cutoff

The normalized cheapest widths have gcd1, so all residues of the normalized anchor are reachable in `apery`; the unguarded `max(item.size...)` at line75 is justified. All their losses are zero, so its least lexicographic labels are precisely least representable normalized sizes. If the modulus is1, its sole entry is the empty path and the conductor is0, as required. `cheap_counts` appends the normalized anchor after the appropriate Apéry witness; its early `n<0`/h-divisibility checks correctly exclude impossible input.

At lines77–79, reusing `labels` when b=h is exact because the two residue problems coincide. Otherwise the new table has modulus b, not h. For s reachable modulo b, projection shows its minimum loss is at least delta_(s mod h). Starting with a minimum-loss path modulo h, append only cheapest widths: modulo b their nonnegative monoid is the full subgroup of multiples of h, so one can reach s without more loss. Hence the two losses are equal, without requiring a cheapest width equal to h.

The table's second coordinate A_s is the least size of a fill attaining this eventual loss in that b-residue. For n in that residue, a fill attaining the eventual loss exists exactly when n>=A_s: necessity is the least-size tie rule; sufficiency appends `(n-A_s)/b` actual anchor invocations. An inaccessible residue remains impossible at every size. Below A_s, feasible fills may still exist but must be more expensive, or there may be a hole. `optimum` lines99–108 preserves this distinction: a `None` anchor label means a permanent hole, while `n<label.size` invokes the exact amount recurrence instead of wrongly reporting infinity or the eventual minimum.

This is why the h-table alone would not give the earliest exact onset. It provides a sufficient conductor bound but loses the within-anchor-residue last exceptions. Multiple cheapest widths are needed to establish both the projection equality and the correct earlier/later cutoffs.

## 4. Least eventual excess period, including infinity

Let D=lcm_j(g_j/gcd(g_j,q_j)) and P=lcm_j(h_j/gcd(h_j,q_j)). Since g_j divides h_j, D divides P. At D not dividing a, one cut's amount is in a permanently unreachable residue, so actual E(a) and its prediction are both +infinity. At D dividing a all residues are reachable, although finite-size holes may still occur. The eventual finite prediction is the sum of the h-table minimum losses.

Each finite summand is nonnegative and vanishes exactly when h_j divides a*q_j. Therefore the prediction has zeros exactly at multiples of P; it is P-periodic including its infinity pattern. This proves not only that P works but that it is least: any positive eventual period T must send a sufficiently late zero at a multiple of P to another zero, forcing P|T. Arbitrarily early holes do not invalidate that late-zero argument. Neither the normalized bill G(a) nor its floor F is claimed P-periodic; only the total excess E(a) is.

The code in `period_and_floor` computes the same quotient-before-LCM P. It uses positive exact rational density and a parent scale; no floating comparison selects cheapest widths. I reviewed this period expression and the meanings of q, D and P, not the full frontier routine or rank12 invoice.

## 5. `first_periodic_replication`: all residue classes and exact earliest positive start

Lines143–149 compute the same D, then v=step=q*D and k=classes=b/gcd(b,v). In class `t=u mod k`, s=v*u mod b is constant. Since g divides v and b, this s is always a multiple of g. Consequently `menu.refined[s]` is not None: line150's direct `.size` access is justified even when many other b-residues are permanently unreachable. Using q instead of D*q here would destroy that guarantee and fail to model other-cut masking.

For a=D*t with t>0, this cut matches its finite prediction exactly when v*t>=A_s. Its mismatches are exactly t<=floor((A_s-1)/v). The minus1 makes equality at the attained cutoff a success. For positive k, Python `//` is floor and `%` returns a remainder in0..k-1, even for a negative dividend. Therefore

`last_t = limit - (limit-u) % classes`

is exactly the largest integer <=limit in the required u-class. The code may compute a nonpositive `last_t`; `last_bad` initialized0, and its maximum update, implicitly discard all such values. In particular u=0 has s=0 and A_0=0, giving limit=-1; the expression produces a negative multiple of classes, not a spurious positive exception. Modulus1 is the same safe case. A menu with no positive exception thus contributes nothing and the returned onset is1.

Taking the maximum over all cuts is exact rather than merely sufficient. At a multiple of D, every finite actual cut excess is at least its predicted value, and a hole contributes infinity; no positive deviations can cancel. Thus one cut's mismatch forces a mismatch of the total. Nonmultiples of D were already equal infinities. Let L be the resulting largest bad replication. `return last_bad+1` is the earliest positive point beyond every mismatch, including inaccessible points inside the tail. If L>0, L+P>L and is no longer bad, while the prediction repeats after P. Hence actual E(L) differs from E(L+P), proving that no start <=L works. If L=0 the least allowed positive start is1.

Noexception, inaccessible residue, negative limit, rational prices and multiple-cheapest cases are all handled within this argument. The algorithm need not enumerate the global P or every amount through L; it visits the declared sum of anchor residue-class counts. This is the source method, not a new algorithm claimed by this review.

## 6. Written adversarial controls — NOT EXECUTED

These are deductions about altered hypotheses/code, not observations from tests. Existing displayed source fixtures remain source evidence.

1. **Unreachable residues / global D.** Use one menu of widths4,6 with prices4,12 and q=1. Here g=2, h=b=4; odd residues remain None. At accessible a=2 the desired amount is a finite-size hole, whereas the same residue at6 has its attaining loss. Restricting the onset search to a=D*t is necessary. Hand substitution gives the last mismatch at2 and first periodic start3: an onset need not itself be feasible. No code run is asserted.
2. **Negative bounds / no exceptions / modulus1.** A singleton width b with a positive rational price has g=h=b and accessible step divisible by b. Its sampled anchor residue is0, A0=0, limit=-1 and no positive exception. Replacing floor by truncation or incorrectly clamping the intermediate value to a positive candidate could manufacture an exception. The source expression avoids that error. A width1 singleton is the modulus1 boundary.
3. **Attained equality.** Changing `(A_s-1)//v` to `A_s//v` would count an amount exactly at its least attaining witness as still bad whenever v divides A_s. The source's -1 is essential.
4. **Multiple cheapest widths.** The source menu `{1,4,7}` priced2,4,7 has h=1 and anchor4, so treating only anchor invocations as cheap would miss mixed fills. Its displayed anchor labels and last exception are source fixtures, not independently run here. Adding the separate width4-only cut is the source's masking example: joint onset can be1 although the first cut alone has later exceptions.
5. **q scaling and residue stride.** With widths4,7 both priced at density1 and q=2, the anchor4 classes are t mod2, not mod4; the residue2 cutoff is14. Hand substitution identifies t=5 as its last positive exception and6 as the onset. Omitting q, using q/D, or dividing after taking the LCM does not follow the formula. This arithmetic example was not run.
6. **Lexicographic second coordinate.** Comparing loss alone may retain an unnecessarily long zero-loss cycle or a larger attaining path and overstate the onset. Comparing width first can instead sacrifice minimum loss. The exact ordered pair and the strict update preserve the proof's objective.
7. **Infinity is not zero.** Treating a missing label as zero excess would add false late zeros and invalidate the least-period argument. `None` is retained for permanent holes, while early holes in reachable residues are found by exact amount recurrence.
8. **Pricing domain.** A negative loss or zero width supplied directly to the helper invalidates the cycle/shortest-path argument; an invocation-dependent discount or setup shared across cuts invalidates additivity. These are outside the validated Menu/arithmetic contract, not source counterexamples. Rational prices and several exact equal-density minimizers are inside the contract.

## Conclusion and remaining obligations

The audited code implements the proof's exact least excess period and earliest positive onset on the stated input domain. No correction to its mathematical formula or these three routines is requested. Keep the stable-list/tuple, valid-unmodified-Menu and nonnegative-helper-weight API assumptions explicit when publishing the external conclusion. Count-vector tie uniqueness is not established or needed.

Remaining work includes external execution/certificate checking if desired; full Pareto and physical rank12/invoice coverage; actual compatible native programs, complete costs and lifetime/setup constraints; and every selected framework obligation. This note does not change the frontier, claim a new theorem, or turn author-side source fixtures into external test results.
