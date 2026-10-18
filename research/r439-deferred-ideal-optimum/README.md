# The deferred R439 scatter has exact ideal optimum 94

**Independent verification / finite optimality result; no new supplier or kappa.**
For the pinned PR1062 word, every dependency ideal of its 306-gate target-basis undo has scatter cost at least 94 ADDs.
The known ideal {31,51,52} attains 94.
This closes PR2115's larger-ideal question for this word, with no bound on ideal size.

Sagar Thakrar's [PR2115](https://github.com/CrocSwap/integer-mult-bounds/pull/2115), head `b56dceffad83c88e8ad39ffd82a1bdd55c4130da`, supplies the construction and attaining split.
Its search checks ideals of size at most four and explicitly leaves larger ideals open.
The new result is a complete lower bound, not a new circuit or a repeated small census.

[PROOF.md](PROOF.md) gives the exact claim, constant-increment lemma, row inequalities, dependency argument, and attainment.
Only five rows can improve over the 97-ADD start.
Necessary dependencies charge three possible improvements back to two other rows.
The resulting disjoint row bounds sum to 94.
All 1,386 unrestricted row subsets certify the premises; the proof avoids enumeration of all ideals.

## Reproduce

Standard library only, from the repository root:

```sh
python3 -I -O -B research/r439-deferred-ideal-optimum/verify.py && python3 -I -O -B research/r439-deferred-ideal-optimum/independent.py
```

Expected:

```text
PASS_R439_DEFERRED_IDEAL_OPTIMUM minimum=94 gates=306 row_subsets=1386 dirty_columns=661 controls=5 no_new_kappa
PASS_INDEPENDENT_IDEAL_AUDIT backward_coefficients=417 row_subsets=1386 matrix_dependencies=850 minimum=94
```

The primary checker uses forward row states and complete arbitrary-dirty input columns.
The separate checker uses backward coefficient cones, Boolean truth tables, and literal small-matrix commutators.
It imports no primary or predecessor engine.
Five controls reject a cheaper nonideal subset, a missing dependency, a missing compensating cost, an old scatter, and an omitted undo.
Checks remain active under Python optimization.

The frozen certificate records every row minimum and all consumed coefficients.
An exact SMT model helped discover the bound; replay uses neither Z3 nor its answer.

## Accounting and scope

The complete attaining word costs 11,500-527+94=11,067 scalar ADDs, as already reported by PR2115.
All 306 undo gates remain charged, with nine COPY/ERASE pairs and all helpers restored.
The verifier independently checks all 661 dirty input columns in both directions through the literal stream.
The construction preserves the inherited frame paths and paid profile; this package does not regenerate their invoice.

The theorem concerns one fixed undo circuit, its nine-column scatter, and every commutation-closed split into D and B.
It does not cover new basis circuits, different frame paths, scatter interleavings, or extra workspace.
Native address action, stage hosting, precision/tape, all-size realization, and the multiplication theorem remain inherited or unverified here.
We claim neither independent human review nor a full selected-frontier replay.

## Open next questions

A different target-basis circuit could improve the deferred objective.
First price both basis directions and the resulting scatter, then verify the dirty boundary and full precision charge.
The present optimum applies only to the frozen 306-gate circuit; it supplies no global lower bound for that changed problem.
Structured scope and blockers appear in [TASK.json](TASK.json).

## Credit

Credit Sagar Thakrar for PR2115's deferred basis and PR1062's composed word.
Credit Gareth Davidson for the PR915 target basis, with commdata2338, Scott Woolsey Biggart, and Sagar Thakrar in its lineage.
The R439 word retains Sricharan Vagvala's helper stars, Aaron Wang's B circuits, Ross Richardson's frame circuit, and DreamingOfClouds' tuning.
The interface and exporter lineage includes eumemic, Zhihao Chen, woklerx, Arham Tahir, and Dylan Crow.
All predecessor source files remain unchanged.

Prepared for Charles Bethin with substantial OpenAI Codex assistance in the proof, implementation, checks, and writing.
The two implementations have the same AI author; their independence is algorithmic, not human.
New material is Apache-2.0.
