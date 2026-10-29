# From a connector word to the certified finite formula

Alexander Richard Towell, with substantial OpenAI Codex assistance.

## Claim and dependencies

Let w be a word of length 30 on six symbols, each appearing five times.
Let q_t(j) count occurrences of symbol j before boundary t, 0 <= t <= 30.
There is no such word for which every binary vector of weight two or six
is congruent to q_s+q_t modulo five for some boundaries s,t. Consequently
there is no depth-two block realizing all 63 nonzero binary vectors in
the PR4231/4248 interface. No other connector interface or characteristic
is covered; no supplier admission or multiplication exponent follows.

The finite formula is Josie Elliston's PR6141 generator, pinned at
d192172f57b10647ddcff9410c69d48ac06862c1, with python-sat 1.9.dev15,
k=6, c=5, weight pruning enabled and mask weights {2,6}.
The certificate checker establishes only UNSAT of the exact recorded formula.
The following written implication connects it to the claim. It is not a
Lean/kernel formalization. Tool, compiler and hardware correctness remain
part of the computational trust base.

The LRAT checker used for the final replay includes the exact existing PR43
correction (head 0ca925b4f5b4ed04d02d830807cfd614483e7320) by haskiindahouse.
The uncorrected checker at 2e3b2dc falsely accepts a fake refutation of a SAT
formula (known issue42); its successful output is not evidence relied on here.
This correction is not a complete audit of either C checker. The separate
DRAT checker verifies the full pinned trace as well.

## Symmetry, boundaries and weight pruning

Relabel the six symbols in order of first occurrence. This preserves the
word counts and permutes the full sets of weight-two and weight-six masks.
Thus it suffices to consider words whose first occurrences are increasing.
For any boundary equal to 30, replace it by zero, since q_30=(5,...,5)
is zero modulo five. Reorder the two boundaries to obtain 0 <= s <= t < 30.
Repeated boundaries s=t remain allowed. For every realizing pair,
sum_j(q_s(j)+q_t(j))=s+t, so s+t is congruent to the mask's weight modulo
five. Thus pruning other pairs never discards a possible realization.

## Assigning the non-cardinality variables

Set x[p,j] true exactly when w[p]=j. Each position has exactly one symbol.
Set e[t,j,v] true exactly when q_t(j) is congruent to v modulo five.
This satisfies all one-hot residue clauses, initial residues and transitions.
Set f[p,j] true exactly when j has occurred in positions 0 through p.
The defining recurrence is f[p,j] iff x[p,j] or f[p-1,j], with a false
predecessor at p=0. Increasing first occurrences satisfy the symmetry clauses.

For each mask of weight two or six, select a realizing boundary pair after
the preceding reductions. Set its y[mask,s,t] true and every other selector
false (alternatively, set all realizing selectors true). The mask disjunction
is satisfied. If e[s,j,v] is true, realization forces
e[t,j,(mask_j-v) mod 5], exactly as required by each selector implication.
All other selector implications have false antecedents.

## Constructive cardinality extension

For each source, PySAT encodes at-most-five true x-literals and at-most-25
true negated x-literals. Together these say exactly five occurrences. The
generator's sequential-counter clauses are compared, in order and with actual
variable IDs, against the following independent construction by checks.py.
Every target cardinality clause must match; no unnamed counter is ignored.

For literals u_0,...,u_(n-1) with total at most r, the interior counter has
variables y[k,j] for 0 <= k < r and 0 <= j < n-r. Assign y[k,j] true iff
at least k+1 of u_0,...,u_(j+k) are true. The clauses are:

1. u_j implies y[0,j].
2. y[k,j] implies y[k,j+1], whenever the latter index exists.
3. u_(j+k+1) and y[k,j] imply y[k+1,j], for k < r-1.
4. u_(j+r) and y[r-1,j] cannot both be true.

The first three follow by counting prefixes. The fourth would require at
least r+1 true input literals, contradicting the assumed bound. This gives
a satisfying extension for each counter. The target uses (n,r)=(30,5)
and (30,25); both are interior cases covered by this construction.
The anonymous variable ranges for different counters are disjoint, and
separate from x/e/f/y. Therefore the extensions combine with the assignments
above to satisfy every clause of the target CNF.

## Conclusion and evidence levels

If a word with the claimed realizations existed, the preceding assignments
would satisfy the recorded CNF. A successful checked refutation of that exact
CNF contradicts this. UNSAT for the sixteen selected masks also excludes a
word realizing all 63 masks, since the latter is a stronger requirement.

The counter interpretation and word-to-CNF bridge are written proofs, supported
by executable clause comparison and finite exhaustive controls. The DRAT/LRAT
replay is a checked finite refutation using C checkers, not a Lean proof or a
formal proof of the full integer-multiplication theorem. AI review is separate
from human peer review and repository acceptance. PR6141's reported characteristic
six exclusion and the open characteristic seven case are not checked here.
