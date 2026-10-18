# Four-site phase rigidity closes the rank-changing swap/cycle question

**Scoped negative result, with a written proof and exact source checks. No new
kappa or admitted supplier.** Under the inherited completed-call contract,
every operator-preserving replacement of idle children **8, 10, 12, 13** in
the fixed schedule preserves **each child's rank separately**. This includes
arbitrary simultaneous independent-axis replacements, not just single moves,
paired transfers, matched swaps or short cycles.

The reason is structural. The interval between the two idle events preserves
the receiver's two-dimensional coordinate subspace, forcing all four phase
functions to remain unchanged. The binary polar form of an independent-axis
child's Z4 phase has rank equal to its number of axes. Equal phases therefore
force equal ranks. The [proof](PROOF.md) states the assumptions and derives
both steps; no enumeration of candidate assignments is needed.

This answers the four-position matched-swap/cycle question left open by
[Gonzalo-Mier's #3196](https://github.com/CrocSwap/integer-mult-bounds/pull/3196)
and the finite assignment experiment in
[#3199](https://github.com/CrocSwap/integer-mult-bounds/pull/3199), inspected at
`ba34486f40f558fe3ac57bdb1ec263daeaa3fb5b` (including its same-centre
star isolation argument).
It extends the physical-stream obstruction of Gareth Davidson/#1387 and
Nick Petalas/#3187; it does not replace or re-credit those discoveries.

## What this saves and what it does not establish

A packing optimizer confined to these four positions cannot achieve a
rank-changing improvement without changing the schedule or another premise.
For an unhosted baseline of four rank-48 children, this excludes the proposed
`[51,51,51,39]` profile and every other changed rank profile. The fixed rank
profile also fixes any recursive charge depending only on those four ranks;
the theorem does not exclude savings in frame costs from rank-preserving
basis changes.

There is also a compact equality representation: a child's entire phase on
`F_2^73` is determined by **2,701** linear/quadratic coefficients (equivalently,
its values on singleton and pair characters). This can reject incompatible
child phases before an expensive physical replay. Equal polar matrices alone
are insufficient; the linear residues modulo four must also match. This is
not a completeness bound for testing an arbitrary eight-stream circuit.

The source checker validates all **448 full recipe bases across 112 ports**,
their rank 48, the physical child mapping, and the unmixed coordinate cut.
It does not rebuild the T740 fill. Rank 48 therefore describes the full
recipe axes, not a newly verified claim about all hosted residuals. The
theorem also applies to residual subsets, preserving their own starting
ranks while hosted operations remain fixed. The actual unhosted witness and
helper chronology remain credited to #3187/#3196.

Changed interactions, additional changed child positions, dependent-axis
implementations and new local contracts are outside this result. It neither
certifies the baseline supplier nor audits native words, the all-size compiler,
precision, tape recovery or outer analytic assumptions. The selected record
and frozen predecessor packages are unchanged.

## Reproduce

From the repository root, Python 3.12 or later, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/idle-four-site-rigidity
```

Expected verifier markers:

```text
PASS_IDLE_FOUR_SITE_RIGIDITY ports=112 axesets=448 full_recipe_ranks=48,48,48,48 phase_tuples=8192
PASS_IDLE_FOUR_SITE_EXPORT optimized_runs=6 rejecting_controls=3
```

For a Git-free source export containing this package and the three live input
paths in [VERIFY.json](VERIFY.json), the direct command is
`python3 -I -B research/idle-four-site-rigidity/verify.py`.
`--emit-result` prints the deterministically recomputed receipt; normal replay
compares it with [RESULT.json](RESULT.json) and writes no generated artifacts.
The registered runner additionally checks historical Git provenance.

Controls cover all 1,447 independent axis sets in dimensions one through four
(22,584 full-character evaluations), all 256 four-phase tuples for each of
32 deterministic diagonal fixtures (seed 40), and five rejected source-schedule
mutations. Positive boundary controls include equal phases from different
bases, a translation repair, and a transfer after changing the interval to
cross the invariant cut. The export tests exercise optimized Python, missing
or changed source bytes, receipt type mutation, and formatting invariance.
These finite controls check the implementation and hypotheses; the unlimited
assignment statement rests on the written proof, not on their coverage.

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) pins input bytes, Git blobs and predecessor proof
provenance. [TASK.json](TASK.json) records OS assignment seed 40, the explicit
task-card scope change, candidate selection, coverage and stopping rule.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19001658).

## Open next questions

The structured handoffs are in [TASK.json](TASK.json). A changed interaction
crossing the invariant cut is a concrete escape: first price its complete
bridge, frame, copy, restoration and recursive-child costs. The verifier's
stream-swap control is only an algebraic example, with no supplier budget.

Other sets of idle positions need their own phase insertion equation and
source-derived invariant-subspace test. Ross Richardson's
[concurrent handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18999338),
updated at 17:25 UTC on 2026-10-17, reports a broader normalized twenty-slot
obstruction with local-only evidence. We credit that report without claiming
exclusive priority or auditing its unpublished argument. This package supplies
a separate, source-bound four-position proof, its phase-rank implication and
compact phase representation; no result from that handoff is used as a premise. The four-position theorem does not
rule out proposals involving additional hosted-remainder positions.

## Credit

Gareth Davidson (@bitplane), #1387, established the physical-stream obstruction
on selected #1094 inputs. Nick Petalas, #3187, bound a literal counterexample
to the current candidate and proved the single-receiver-line interval argument.
Gonzalo-Mier, #3196/#3199, supplied paired/single-transfer censuses and exposed
the simultaneous-assignment question. The axis rule and star lineage retain
Gonzalo-Mier/#1252, Guéorgui Maissouradze/#1276 and Jeremy Kothe/#1324's credit.

The current fill and word context retain Jeremy Diviney/#3148, dcharb78/#3133,
Marius-Paul Dumitrean/#2979, Rohan Arun/#3184 and the predecessor packages'
full selected-supplier lineage. No predecessor code is imported by this checker,
and no fill or native-word evidence is regenerated or claimed as new here.

The simultaneous four-site proof, phase-rank application and independent
checker are by Tekalign (@tekuuu), with substantial OpenAI Codex assistance
in research, code, checking and writing. Author-checked, without independent
human or proof-kernel review. New work is Apache-2.0.
