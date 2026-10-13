# Assessment of the bounded 2^-9 investigation

Douglas Colkitt, with OpenAI Codex assistance. October 8, 2026.
Apache-2.0. No priority claim for the combinatorial or representation arguments.

**No new kappa is established.** The investigation identifies target-capable
optimistic block-label budgets, but supplies no positive block geometry,
complete circuit or new all-size transfer. The main result is a set of exact
exclusions that materially changes where effort should go next.

## 1. What the existing construction can and cannot supply

PR82 has kappa=5203279888519/10^17. Reaching 1/512 requires about 37.54 times
that saving. The balanced assembly requires a_bit>1/511, and at beta=1/20,
a_complex>(20/19)/511. Hypothetical a_bit=0.0022 and a_complex=0.0025 pass
all 47 assembly inequalities with kappa slightly above 1/512 when the current
bridge is held fixed. These are prospective interface targets only.

The exact [budget](target-budget.json) and [derivation](README.md) show:

- Keeping the current rank mass and largest child 529 in dimension 575
  excludes the target, regardless of how those widths are regrouped.
- Arbitrary role compression with the retained data/boundary profile fails.
- Even ideal full-rank batching of each retained macro plus arbitrary role
  compression fails while its central loss is retained.
- Retaining the distinct auxiliary source ports forces at least one source
  role per label. With that floor, **even erasing central loss entirely and
  batching every retained macro ideally still fails**.

These are full-volume mixed-width recurrence screens. They do not exclude
new macros, different role obligations or new transfer theorems. A proposal
to give children smaller volume must implement that obligation; a favorable
weight assignment is not evidence of an algorithm. A larger child also
requires recomputing halving depth, row stock and the finite bridge.

## 2. Alternate-geometry feasibility comparison

We screened the explicit subset cores with q in {2,4,8,16,32}, k=2q-1,
center index j=q-1, and 2q<=h<=64. The scalar factor has r=C(h,j) and
n=C(h,k). Unlike a naive reuse of the triple ledger, a retained j-subset
center has dimension h-j: its label vectors obey equal coordinates on J
and sum(x)=k*x_J. The restricted rational form is the sum of squares of
the coordinates outside J, so this space is nondegenerate.

The screen grants those center dimensions, a hypothetical two-stage copied
schedule, ideal full-rank macro batching and zero auxiliary roles. It covers
all rectangular pairs of the specified axes. At each dimension, minimizing
r*(h-j)/n is an exact domination reduction because its coefficient in the
moment is positive. All covered pairs fail; the best relaxed score is
approximately 1.00001526035 at q=4,h=24 on both axes. The script records the
finite coverage and every reduced-case interval. This does not exclude
different central factors, induced subfamilies, block labels, changed
boundaries or dimensions outside the screen.

Ten signed-vector instances were also measured by complete binary elimination:
q=4,h=4..10 and q=8,h=8..10. This replaces a previously loose rank upper bound
with exact ranks for those small cores. It does not supply their frame/side
circuits. No unexpectedly low rank emerged as a target-capable construction.
The ordinary direct mod-2 reduction of these even-weight signed vectors is
isotropic; it is not a nondegenerate rank-one phase companion.

## 3. Why rank-two labels were selected

The rank-one geometry imposes a small gross deficit per pair. Increasing label
rank changes that quantity rather than optimizing its existing implementation.
For 560 triple labels on 16 points, binary factor size 16, rank-two rational
labels in dimension d, we evaluated a **hypothetical** two-stage block ledger:

    m=d^2, W/N=2+2R/n,
    data: 2 blocks of (d-2)^2 and one endpoint block of 4,
    growth: 4 blocks of 2(d-2),
    auxiliary per axis: blocks 2d and m-2d per role,
    fixed center mass per axis: 16*2(d-2)/560 per pair.

It grants full batching and preserves all these rank charges. At a=1/511:

| d | Roles per label, each axis | Optimistic moment |
|---|---:|---:|
| 14 | 5 | 0.999809335 |
| 15 | 5 | 0.999957094 |
| 16 | 3 | 0.999738468 |

These favorable budgets justified testing the necessary block geometry.
They are not achieved profiles. In particular, no unproved block copy,
ordered pivot or phase theorem was used to certify a bound.

## 4. Experiment 1: exact Fano saturation obstruction

Change: allow arbitrary rational rank-two idempotents instead of line labels;
do not assume a common form or vertex symmetry. Target dimension: 14.
Required compatibility is P_S P_T=P_T P_S=0 when triples intersect in one point.

Seven Fano lines form a clique in that relation. More generally, seven
mutually annihilating rank-l idempotents in dimension 7l must sum to I.
On nine ground points there are 84 triples and 1,080 embedded Fano cliques.
The [certificate](block-fano-obstruction.json) selects 84 clique-incidence
rows with a nonzero determinant modulo 101, proving full column rank over Q.
Every matrix entry in the clique equations therefore has the unique solution
P_T=I/7. But (I/7)^2-I/7=-6I/49, contradicting idempotence.

Thus dimension 7l is impossible on the full triple graph for every h>=9,
by restriction to nine points. For l=2 this closes d=14 completely, including
nonsymmetric matrices and all frame choices. The graph and dimension are
essential hypotheses; dimensions 15 or 16 are not excluded by this argument.
The determinant is independently replayed, with a duplicated-row negative
control. A rank-eight scalar fitting factor on nine points provides a
nontrivial positive geometry control (rank-two dimension 16 by direct sum).
That control is not a finite multiplication network.

## 5. Experiment 2: covariant rank-two labels in dimensions 15 and 16

Change: move to the next target-capable dimensions, allowing any rational
stabilizer-invariant idempotent under the standard/natural permutation action.
This is a specified block-label construction family, not unrestricted matrices.

For a triple T on h points, the sum-zero standard representation splits under
its stabilizer into the sum-zero vectors on T (dimension 2), the sum-zero
vectors outside T (dimension h-4), and one between-block line. Its commutant
has dimension three: direct six-orbit coordinate equations establish this
without assuming self-adjoint matrices. The three corresponding idempotents
span it. For h>=7, only the first component can be a rank-two idempotent.

That candidate is P_T=diag(1_T)-1_T*1_T^T/3. For T={0,1,2} and
U={0,3,4}, their product sends e_0-e_5 to
(4e_0-2e_1-2e_2)/9, which is nonzero. It fails the required annihilation.
In the full natural space, the extra possible rank-two choice is identity
on the two-dimensional trivial component. Every such choice fixes the global
constant line, so it also fails. [Exact certificate](covariant-block-test.json).

Stop this covariance family. The proof does not exclude noncovariant labels,
other group actions, induced subfamilies or other graphs. Neither experiment
reached a valid label geometry, so neither justifies constructing or claiming
a side circuit, scaling law or complex companion.

## 6. Ranked feasibility and next experiment

1. **Noncovariant block fitting geometry with an explicit side budget.**
   This is the most concrete remaining target-capable direction identified in
   this round, not a prediction of success. It changes gross rank deficit and
   evades both tested restrictions in dimension 15 or above. The first task is
   exact geometry, before expensive compilation. A rational geometry witness
   would still need a compatible compact side circuit and a phase counterpart.
2. **Cross-macro or restricted-child transfer with genuinely changed
   obligations.** It can evade the recurrence screens, but must remove an
   actual paid obligation or prove a different volume/child contract. Merely
   eliminating central loss, changing basis or compressing the old injection
   bank does not suffice under the retained ledger. No such primitive was
   discovered in this round.
3. **Different two-field graph/topology.** Potentially the largest departure,
   but currently the least specified. Require an explicit characteristic
   advantage and complete reversible/typed-workspace contract before treating
   it as a candidate. Do not recycle the closed balanced-Fano scalar graph or
   infer a transfer certificate from a coding or scalar identity alone.

The recommended next bounded experiment is **an unrestricted rational rank-two
representation on nine points in dimension 15**, as a necessary subinstance
for the 16-point target. Fix one Fano clique to seven coordinate two-planes
and a one-dimensional remainder; this is a legitimate change of basis for
any solution. For each other triple, annihilation forces its matrix to have
zero rows and columns on the neighboring clique blocks. Search the remaining
allowed blocks without imposing permutation covariance or retaining the old
rank-one line. All idempotence, rank and two-sided annihilation conditions
must be checked over Q. A finite-field or numerical candidate is discovery
evidence only.

A positive nine-point solution is not a scaling argument. It must extend to
the 16-point instance, admit a charged producer within the role budget, and
support actual ordered child profiles. A negative finite search only excludes
its specified kernel catalogue; it is not a dimension-15 impossibility proof.
This proposed continuation was **not executed** in this bounded two-experiment
round. The [unexecuted specification](next-experiment-spec.json) fixes the
gauge and lists allowed coordinates: 4,893 rational matrix entries and 1,890
unordered annihilation pairs remain, before exploiting the idempotence and
rank-two factorization constraints. This is a concrete search problem, not
an estimate that it will be easy to solve.

## 7. Complex interface and claim boundary

The retained complex saving is 717/10^7, far below the necessary approximately
0.00206 at the current beta. A bit-only block breakthrough therefore cannot
establish the headline. The subset family has a historical rational polynomial
companion, but its phase frames, scalar coefficients, copied schedule and
recursive profiles require their own certificate. A rational bit block
representation does not automatically transfer to characteristic-two phase
geometry. Changed maximum children or scalar charges require new row-stock
and precision constants even if the assembly formulas remain available.

The result of this round is a clearer research target and exact exclusions,
not an established credible complete route to 2^-9. The remaining bet is on
an asymmetric block primitive or a genuinely different transfer contract.
Published results and prior review artifacts are unchanged; nothing was
merged, pushed or publicly announced.
