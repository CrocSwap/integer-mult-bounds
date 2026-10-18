# One added pair-total at the selected centre cut: bounded cost rejection

**Completed exact finite experiment; no new supplier or kappa.** All **296** clean proportional pair-sharing replacements of the selected PR1094 centre cut fail the predeclared 5% improvement gate, even with additional preparation, frame adaptation, dirt repair, phase, precision and hosting costs granted free. They also fail the stronger comparison against the selected word's own packing relaxation.

This is an attempted changed decoder, not a repeat of the unchanged-tree audit. Four replacements shrink two original copy ranks from eight to seven, but add a rank-two copy. They tie total copied mass at 64 and fragment it into a more expensive profile. The experiment therefore stops before physical synthesis.

## Reproduce

Python 3.11+ and the standard library, from the repository root:

```sh
python3 -I -B research/centre-cut-pair-sharing/verify.py
python3 -I -O -B research/centre-cut-pair-sharing/verify.py
python3 -I -O -B research/centre-cut-pair-sharing/independent_check.py
```

Primary marker: `PASS_CENTRE_CUT_PAIR_SHARING_SCREEN candidates=296 best_centre_charge=64 gate=FAIL_SYNTHESIS_NOT_STARTED controls=8`.

Secondary marker: `PASS_CENTRE_CUT_PAIR_SHARING_INDEPENDENT cases=296 entries=265216 patterns=6 equal_mass=4 controls=3`.

Both checkers are read-only. Primary `--receipt` prints the recomputed evidence; ordinary verification compares every field with [RESULT.json](RESULT.json). The complete candidate table has a canonical SHA256 in that receipt, and the secondary checker independently reconstructs and binds it. The receipt keeps the full profile screens and a concrete best witness rather than duplicating every derivable candidate.

The registered Python 3.12 commands and all external inputs are explicit in [VERIFY.json](VERIFY.json):

```sh
python3 scripts/research_package.py --package research/centre-cut-pair-sharing --check-only
python3.12 -B scripts/research_package.py --package research/centre-cut-pair-sharing
```

## Exact changed mechanism and domain

The actual selected **480-helper** word comes from the provider inside `research/community-frontier1094-audit/selected-replay.tar.gz`. Its canonical payload is bound to the selected slot recipe, and its 176 nonzero quarter-coefficient scatter edges are compared to the emitted forward program. The 492-helper ancestor at stored `evidence/local/` paths is not substituted. Base main is `99aea7503041c2bd559e69bacb7ef12b4fa9a552`; selected PR1094 source head is `0fc329d0bec93ca7cd288eaea1295172e8789810`. [SOURCES.json](SOURCES.json) pins the archive, slot recipe and retained ceiling engine. The selected pointer and catalogue are historical provenance.

Write C_0,...,C_7 for the eight prepared carrier values, and d_tk for the selected cut's coefficient of C_k in target t. Choose i < j and a nonempty target subset S on which both coefficients are nonzero and `d_tj = lambda*d_ti`. Replace the two contributions on S by a ninth declared total:

```text
H = C_i + lambda*C_j
on t in S: d_ti*C_i + d_tj*C_j = d_ti*H
outside S: retain both original coefficients
```

All other six centre terms and all non-centre paid work are retained. The identity is checked over exact rationals on every target and every independent carrier basis input: **112 x 8 x 296 = 265,216** coefficient equalities. It holds for arbitrary carrier values; this is not a verification of the full native program.

The domain covers all 28 unordered pairs, every ratio class on their shared targets, and every nonempty subset of each class. There are 16 disjoint pairs, four pairs sharing six targets, and eight pairs sharing eight targets. The actual nonzero coefficients are +/-1/4, so the induced normalized mixing ratios are +/-1. Arbitrary common nonzero complex rescaling of H does not change these supports or costs. A different ratio cannot simultaneously delete both original contributions on a nonempty subset.

The new total is formed by common-frame addition of the **already prepared** carriers. Their two rank-eight frames join to the full rank-nine frame. Directly regathering H from earlier sources with cancellation is outside this mechanism. For each retained or new term, the favorable copied rank is the codimension, within its gather frame, of the common meet of its served targets' final frames. Those final frames are checked to be the kernels of the actual port functionals. The primary uses binary elimination and a separate vector-intersection computation. The secondary uses scaled-integer coefficients, combination-based subset enumeration and explicit frame vectors; it imports no primary or supplier module.

## Exact results

| Original residual copy ranks | Added rank | Cases | Total centre mass |
|---|---:|---:|---:|
| eight ranks of 8 | 1 | 88 | 65 |
| eight ranks of 8 | 2 | 116 | 66 |
| eight ranks of 8 | 3 | 68 | 67 |
| eight ranks of 8 | 4 | 16 | 68 |
| six ranks of 8 and two of 7 | 2 | 4 | 64 |
| six ranks of 8 and two of 7 | 3 | 4 | 65 |

A best witness shares centres **0 and 1** with `H=C_0+C_1` on zero-based targets **0 and 72**. It replaces their two rank-eight children by `(7,7,2)`; the other six rank-eight children stay. The favorable per-call local profile is

```text
{1:2412, 2:419, 3:432, 4:142, 5:82, 7:2, 8:6}
```

Local mass remains 5,586, idle mass 1,646, centre charge 64, and deficit 320/9. Exact retained-engine ceiling brackets are:

| Profile | Primitive saving a, lower bracket | Upper bracket |
|---|---:|---:|
| selected word | 0.001690054109088 | 0.001690054109089 |
| best sharing replacement | 0.001689680763861 | 0.001689680763862 |

The best upper end is already below the baseline lower end (about **0.0221% less**). These are **packing-relaxation ceilings**, not achieved savings, practical speedups or new kappa bounds. The original 5% gate was `candidate ceiling >= (21/20)*baseline ceiling`; every candidate fails even a zero-percent improvement comparison of these relaxed profiles. The primary imports Douglas Colkitt's source-pinned `ceiling.py` rather than claiming a new independent numerical engine. The secondary verifies the complete finite identities/ranks/profile classes, not those numerical root enclosures.

## Why equal mass still loses

This is a short written cost argument conditional on the complete finite classification above. For candidate saving `0<a<1`, put `f(r)=(r/73)^(1-a)`, with f(0)=0. The normalized recursive moment divides the sum by `w=896/9` and adds the idle contribution.

The non-centre paid mass is fixed at `5586-64=5522`. Under the explicitly retained nine-stage coverage model, total paid mass per call is `72*w+C`, where C is the complete centre charge. Thus every replacement has the same favorable idle mass `72*w-5522=1646`, including candidates whose C is greater than 64. There is no credit for omitting the ninth copy.

In 288 cases, all eight original ranks remain eight and a positive ninth child is added, so the moment increases. In the remaining eight cases the relevant old bill is `2*f(8)` and the new bill is `2*f(7)+f(2)` or `2*f(7)+f(3)`. Strict concavity gives

`f(1)-f(0) > f(8)-f(7)` and `f(2)-f(1) > f(8)-f(7)`.

Adding proves `2*f(7)+f(2) > 2*f(8)`; f(3)>f(2) handles the other four cases. Hence every enumerated replacement has a strictly larger favorable moment for `0<a<1`, despite four cases tying rank mass. The written argument is not a theorem-kernel or independent human proof review.

## Full cost boundary, controls and limits

The screen charges every residual and new copied rank, the entire retained non-centre profile, and ideal idle-remainder mass through the retained model (`m=73`, families 896, stages 9, halving cap 51, one unpaid coordinate per live family). All additional mixed-total preparation/source access, common-frame promotion, private-temporary initialization/erasure or dirty repair, phase/precision/scalar work, and physical stock/hosting costs are set to zero. Actual nonnegative costs cannot rescue this fixed-profile screen. This is a fully stated **optimistic rejection budget**, not a completed physical invoice.

Eight primary controls cover a wrong ratio, an empty sharing subset, a nonshared target, an invalid old-frame gather shortcut, failing to remove the second old scatter, omitting the shared scatter, omitting its COPY charge, and uncleared private dirt. The secondary supplies separate wrong-sign, dirt-leak and uncharged-copy witnesses. In particular, the equal-mass cases cost 64, not 62: forgetting the new rank-two copy fabricates a saving. Checks remain active under `-O`.

No full A/B/cleanup redesign, target waiting schedule, native phase, owner admission, precision invoice, exact global moment, outer composition or cold supplier replay is claimed. Source-bound selected replay is consumed as evidence. The comparison is against the selected word's **packing relaxation**, not proof that no better owner arrangement could improve its currently attained result. No decoder outside this proportional, both-contributions-deleted, prepared-carrier, fixed-non-centre-work family is excluded. One-sided cancellation, changed source gathering, multiple new totals, changed A/B work, interacting delivery and different coverage laws remain outside scope.

## Open next questions

A direct regather of a mixed total might exploit cancellation before the common-frame addition, or a different identity might remove non-centre work. That would change the tested hypotheses. A feasible first step is to specify one such exact identity, its legal source/target frames and its complete optimistic local profile. The blocker is a valid new gathering/dirty-state contract and fully charged costs; this result supplies no promising candidate. See the structured question and stopping rule in [TASK.json](TASK.json).

## Coordination and credit

The user explicitly chose a small changed-decoder experiment after [our centre-tree audit PR1643](https://github.com/CrocSwap/integer-mult-bounds/pull/1643). This experiment is coordinated in [Discussion1645](https://github.com/CrocSwap/integer-mult-bounds/discussions/1645). Entry overlap covered 591 open PRs and 285 Discussion records with complete pagination; a refresh before submission is recorded in TASK.json. Search coverage is metadata and local notes, not all private/historical code.

Credit ctoth's Discussion1516 and its disclosed reviewers; the PR446/595 pairing-cost and PR968/1077 decoder-bound lineage; Mihir Srivastava's PR845 and woklerx's complex single-lift continuation (full P112 Gram fixed-reader identities, not this sparse local cut); Hanson Sun's PR1633 excess-rank classification (also a different question); Douglas Colkitt's PR1240 ceiling engine; and Jeremy Kothe, Rohan Arun, Hao Yan, icekylinx and the selected construction's retained lineage.

Prepared for Dennis (@antunishdPursuit) with substantial OpenAI Codex assistance in design, code, proof exposition, execution and packaging. The two implementations are by the same assisted author; neither independent human review nor independent numerical repricing is claimed. New work is Apache-2.0. All predecessor inputs, notices and selected records are unchanged.
