# Selected BIT: a mixed good/fallback child-weight descriptor

This package implements the ancestor-weight descriptor for one fallback
diagonal-pair child after a good rank-42 ancestor, and passes that generated
descriptor into a further good child. It takes Open next question 1 of
[PR #2171](https://github.com/CrocSwap/integer-mult-bounds/pull/2171), whose
evaluator covers good ancestors. The claim is in
[discussion #2165](https://github.com/CrocSwap/integer-mult-bounds/discussions/2165).
This is a conditional interface result, with no supplier or exponent change.

If unweighted elimination ends at diagonal d and original-row permutation
pi, the weighted fallback diagonal at logical atom column j is

```
d_i(j) = d_i * b_pi(i)(j) / b_i(j),
b_i(j) = A[i*f+j] for a head field, and 1 for a tail field.
```

The child must also convert physical atom t to j according to its field's
orientation. This follows inherited diagonal covariance in source527 and
Ross Richardson's PR2159. We add explicit recursive indices, an executable
evaluator and mixed-path checks, not a new covariance or fallback theorem.

On a source-bound rank-42 GL-orbit example modulo 25, a head child needs
weights **[14,14,19]**, from two differently indexed ancestor weights. A
reversed tail child needs **[11,6,6]**. Low-only ancestors, a lost row
permutation and the good-only flat-index rule fail. The
[proof](PROOF.md) states the assumptions and preparation charge.

## Reproduction and evidence

From the repository root, using Python 3.12 and no third-party packages:

```sh
python3 -I -B scripts/research_package.py --package research/selected-bit-mixed-descriptor
```

Both normal and optimized replay must print:

```
PASS_SELECTED_BIT_MIXED_DESCRIPTOR covariance=46848 mixed_columns=11 controls=15 no_new_kappa
```

Replay compares [RESULT.json](RESULT.json), without regenerating a missing
or changed receipt. `--write-result NEW_PATH` writes a candidate exclusively
when explicitly requested. [SOURCES.json](SOURCES.json) binds the selected
template, receipt, assembly citation and source527 proof. No predecessor
executable is imported.

- 46,848 covariance cases cover every 2 by 2 determinant +/-1 matrix
  modulo 3 and 9 and every unit diagonal conjugator.
- All 127 diagonal pairs and both orientations are checked over 11 weighted
  columns in four 128-coordinate fixtures. Full operators reconstruct
  exactly; a separate forward-elimination oracle agrees.
- A good/fallback/good path has widths 6400 → 4200 → 65 → 42, with 40-atom
  and one-atom peeled remainders explicit. All 65 intermediate weights are
  checked by direct weighted elimination.
- 5,625 complete coordinate-pair/stock cases check the six-child
  same-orientation pair; six basis columns check the two-child opposite
  pair; 15 semantic controls reject.

The prior fallback allowance remains **98,682 children**, below the charged
131,072. The tested same-orientation pair pays six children, including four
reversals. No bill reduction is claimed. Preparation uses the retained
root-width stopping relation before complete fibers absorb its cost.

## Scope and credit

The selected object is PR589 idle child 6, unhosted copy 213, with axes
22 through 63. Constructed charts lie in its assumed GL64 implementation
domain, not asserted emitted orthogonal-cover invocations. Small primes
are arithmetic fixtures. The full domain bridge, other local-frame labels,
all fallback shear descriptors, completed weighted callees, physical tape
execution and hosting remain open. Address-map tests are not a complete
payload/tape implementation. Evidence is author-checked, without external
independent or formal review.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

This account's [PR #2160](https://github.com/CrocSwap/integer-mult-bounds/pull/2160)
supplies the selected good residual and normal-form binding. Ross Richardson's
[PR #2159](https://github.com/CrocSwap/integer-mult-bounds/pull/2159) supplies
the fallback schedule and covariance proof. Jose Manuel (@jmbarrancoml)
supplies PR2171's good-only evaluator, physical controlled ADDs and handoff.
The generic weighted/fallback and ordered-affine methods retain the
source527/eumemic and original compiler lineage. PR589's tuning is
DreamingOfClouds' work on eumemic's PR555, with the retained geometry and
hosting lineage. Adam Gall and Nick Petalas supply fresh-field, stock and
carry context. Rohan Arun and Jeremy Kothe supply the selected assembly
lineage. Apache-2.0.

## Open next questions

1. Can all fallback shear slots use equally explicit mixed descriptors?
   Begin with `(b_pi(i)/b_pi(k))*c_ik` at one clearing step, tracking the
   intermediate row permutation and both orientations. This is needed for
   the whole fallback. Paid ordered-shift and child-routing integration
   remain blockers; the final permutation here cannot replace an
   intermediate one.
2. Can a generated mixed descriptor drive the physical evaluator through a
   complete selected invocation? Substitute `FallbackPair` for one incoming
   weight source in PR2171 and account for preparation. The weighted callee,
   additional local frames, domain bridge and correlated hosting remain
   separate blockers. Active discussion #2179 addresses whole invocations.

The structured task and limits are in [TASK.json](TASK.json).
