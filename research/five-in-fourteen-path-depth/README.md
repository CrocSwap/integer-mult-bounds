# The stated raw five-in-fourteen architecture has no fixed free completion

**A complete named-caller obstruction; no new kappa or general fourteen-call exclusion.**

Expand the retained PR4813 architecture literally: four fresh-input three-call
ports on `(x1,x2),...,(x4,x5)` and a two-call port on `(x5,x1)`. Give a decoder
all five original inputs, all ten raw port outputs, and any fixed number of
recording-only taps from the displayed implementation. Every path from x5
still contains at most **two paid calls**.

For one address basis input at tensor width f, put z=2^f. The exact complete
raw-state support polynomial is bounded by

`q(z)=1+z+3z^2`.

Any fixed finite decoder made of uniformly bounded-column free linear steps
can multiply that support by only a constant B independent of f. The target
`K_f x5` instead has 8^f nonzero coordinates. For `2^f>5B`, the required target
support exceeds `B q(2^f)`. No such decoder can finish even the fifth target.
[PROOF.md](PROOF.md) supplies the full all-width argument, exact input ownership,
literal paid chronology and the distinction from other fourteen-call programs.

This global obstruction remains within either swap sector: a plus witness
has input support 1 and target support 8^f; a minus witness has input support 2
and target support 8^f/2. It is independent of
[PR5004's local sector error](https://github.com/CrocSwap/integer-mult-bounds/pull/5004).
Correcting that local premise alone does not supply the missing free decoder.

Two changed-premise controls prevent a general exclusion:

- Upgrading the closing port to a three-call port gives 15 calls and fifth-input
  depth 3, removing this support obstruction without proving a full decoder.
- Feeding the updated fourth-port target into the closing port gives a different
  fourteen-call word with fifth-input depth 4 and different raw outputs. That
  changed chronology is not excluded here.

The source's valid raw ports, their authorship and all frozen files are
preserved. This is a result about the stated fresh-original caller; it is not
an impossibility theorem for every five-in-fourteen unit, a stronger selected
bound or a physical compiler admission.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -B research/five-in-fourteen-path-depth/verify.py
python3.12 -I -O -B research/five-in-fourteen-path-depth/verify.py
python3.12 -B scripts/research_package.py --package research/five-in-fourteen-path-depth
```

Expected:

```text
PASS_FIVE_IN_FOURTEEN_PATH_DEPTH paid_calls=14 fifth_depth=2 raw_support=1+z+3z^2 input_columns=360 no_new_kappa
```

Default replay compares [PROGRAM.json](PROGRAM.json) and [RESULT.json](RESULT.json)
without writing. `--write-result NEW_PATH` exclusively creates fresh program
and receipt files. The literal caller has fourteen paid calls, ten copies,
ten monomial-image ADDs and eight additional monomial blocks. Every prefix's
paid-depth vector and the complete support-polynomial state are retained.

The coordinate interpreter is checked against a separate oracle of the actual
raw port matrices: all 40 original input columns over Q(i) at width 1, and all 320
columns over F17 with i=4 at width 2. Every one of the 15 output banks is checked.
Each branch is tensorized separately; no sum is tensorized as a single letter.
The target and both sector witnesses are also checked against the ordinary
three-call implementation. Modular tests are finite corroboration; the written
support proof establishes the universal conclusion.

Only exact field arithmetic and coordinate monomial application are reused
from the pinned compensated-pair checker. Its scientific verifier and program
are not invoked. The source factory provides the separate raw-operator oracle.
All own guards are explicit and remain active under optimization.

## Assignment, sources and limits

Base: `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority revision 7. OS seed:
`04527c49d56f9e55956ed2ae2070e7ff`; the `uniform-transfer-audit` card was
retrieved for the concrete global-decoder continuation of PR5004. [TASK.json](TASK.json)
records the changed scope. [SOURCES.json](SOURCES.json) pins every input and
[OVERLAP.json](OVERLAP.json) records search coverage and limitations.

The decoder model permits fixed bank mixing, copying, erasure and monomial
address maps. Even width-dependent coefficients and address permutations cannot
remove the support exponent when column bounds and program size stay uniform.
A number of free operations/banks growing with f, a new paid query, a different
query chronology or another intermediate-tap contract is outside this proof.
No per-input depth condition is summed into a universal 3W call lower bound.

No full native, hook-rank, selected cold replay or Lean suite was run. No
independent human or proof-assistant verification is claimed.

## Open next questions

- Can the changed closing-feed word support an actual pure-target decoder?
  Start from its emitted raw operator with every independent input retained;
  depth 4 only removes this obstruction, and supplies no completed unit.
- Can another 14-call chronology give adequate paid depth to every input and
  pass an exact all-width endpoint test? Emit the actual word before evaluating
  a favorable moment or using a finite dense recovery as evidence.

## Credit

Pierre-Loic Doulcet / hexapode supplies PR4813's architecture under audit.
Dugongue / PR4743 supplies the valid raw-port constructions; Yiyang / PR4710
supplies phase and residual identities; lee-phys / PR4688 supplies the original
prefix. Jacob Alan Sussman / PR4628 supplies the small-unit framework and
related one-array support method, retaining eumemic and Swapnil Jain credit.
The elementary support method is not claimed as new. This package binds it to
all inputs, original ownership and paid paths of the named raw schedule.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in research,
proof explanation, implementation, verification and writing. Apache-2.0.
