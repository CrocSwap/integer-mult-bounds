# Sharper retained backing for the selected coefficient continuation stacks

The unchanged PR2697 coefficient evaluator's value stack stores at most
`h+1` RETURN records. This gives a smaller all-depth retained-array allowance
than PR2758's conservative symmetric bound. For the known literal GL64
depth-two fixture, the certified allowance falls from 340 to 214 cells,
matching its already published observation. Execution and the selected
frontier are unchanged.

For ancestor depth h, index/residue digit lengths I,R, set

```text
A = 2I+4,  B = R+3,  T = max(A,B),  F(h) = (h+1)T+hB

                         pending main  pending reverse  values main  values reverse
h = 0                    A+1           A                B+1          B
h >= 1                   F(h)+1        T                (h+1)B+1     B
```

The new total for h>=1 is `F(h)+(h+1)B+T+B+2`, improving
`2F(h)+T+B+2` by `(h+1)T-B`. At depth zero it is exactly `2A+2B+2`,
including when B>A. For arbitrary erased warm entry arrays with lengths K_j,
use the sum of `max(K_j,c_j)` over the four listed limits c_j.
[PROOF.md](PROOF.md) gives the quantified successful-call contract, source
induction, statement interiors and exact warm-history qualification.

A successful complete binary real-child trace attains the bounds when A>=B.
This is conditional grammar sharpness. The general h>=1 bound is conservative
when B>A; no universal optimality claim is made for that regime.

## Sources and added evidence

Scientific source Jose Manuel/jmbarrancoml's
[PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697), exact
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, is authenticated through the
unchanged [PR2758 package](../selected-continuation-storage/README.md).
[SOURCES.json](SOURCES.json) pins the predecessor fixture, proof, snapshot,
four runtime modules and source notice. All nonstandard inputs are authenticated
before any module is executed, and loading compiles source bytes directly.
No predecessor export is copied or changed.

The new verifier reuses PR2758's fixture recipes and literal algorithms. It
adds a separate per-array length observer at every actual Tape.write, with
quotas checked before growth. Its census covers 524 level-homogeneous branch
histories: GOOD, two-real-child PAIR, either mixed PAIR, two-constant PAIR and
UNIT through depth three, plus binary stress through depth six. Those fixtures
replace only step/preparation with finite unit tables; they are control tests.
Three additional fixtures execute actual GL64 matrix preparation/fallback at
depths 0,1,2 and return the predecessor's literal expected coefficients.
The depth-two retained lengths are exactly 145,44,19,6, totaling 214.

[RESULT.json](RESULT.json) records 914240 synthetic tape writes, eight attaining
request-dominant binary/root fixtures, both scalar-dominant and request-dominant
stress cases, successful repeated calls and arbitrary 700-cell warm history.
Three embedded controls reject an actual one-cell-short value quota, use of
live content as backing, and omission of warm history. Nine behavioral tests
also check the B>A slack example 343 versus 352, source corruption, input limits,
and method restoration after both interior and context-entry quota rejection.
Acceptance remains enabled under `-O`.

The warm fixture extends only the predecessor test's fresh-entry acceptance
allowance to the explicit entry history. Runtime source stays unchanged.
This is author-checked evidence with a separate internal source/proof review;
no independent human review or formal-kernel proof is claimed. The all-depth
conclusion rests on the written induction, not finite enumeration.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/selected-continuation-backing
```

The registered replay authenticates inputs and runs normal/optimized checks
and behavioral tests. Direct replay is read-only and compares the complete
typed receipt. `verify.py --emit` prints a new receipt without replacing it.
Exact environment and final commands/results are in [VALIDATION.md](VALIDATION.md).

## Scope and research decision

The adversarial-audit draw supplied `uniform-transfer-audit`, refined to this
one selected-implementation storage implication under priority revision 5.
[TASK.json](TASK.json) records the nonce, source pins, overlap coverage,
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18972137)
and bounded stopping rule. PR2758's existing live-symbol proof and 214-cell
observation retain their credit; the addition is the directional all-depth
backing theorem and executable per-tape rejection controls.

Decision: finish this component and hand it off. The proof assumes successful
private weight execution and preserves all arithmetic/chronology/termination
premises. Numerical arenas, retained forms, program/field arrays, other caller
objects, physical reuse and movement, recursive grants, complete private
reserve, supplier admission and a new kappa remain unproved here.
The selected cold supplier replay is not required for this independent package
and was not rerun. No hosted-CI pass is claimed.

Build the Lever led to the authenticated per-tape checker. Prove It Works led
to literal lengths, returned coefficients, cleanup and real quota failures.
Test Behavior, Not Implementation led to the nine execution-based tests.
The managed-runtime and observation deviations from Power of Ten, bounded
fixture domain, cleanup and source constraints are recorded in TASK.json.

## Open next questions

1. Can the B>A allowance be made optimal? Derive a joint historical-maximum
   recurrence from the 343 versus 352 example. The possible incompatibility of
   separate stack maxima is the blocker; this matters for a tighter component
   in residue-dominant regimes.
2. Join the continuation component to numerical, program/field and native-action
   backing at common cuts, starting with one pinned actual Callback and its
   entry history. Complete object inventory, physical mapping/movement and
   outer recursive grants block a total reserve conclusion.

Both questions have structured first steps and blockers in TASK.json.

## Credit

Nick Petalas. New work is Apache-2.0. Jose Manuel/jmbarrancoml supplied the
unchanged callback, tape algorithms and retained implementation lineage.
PR2758 supplies the prior live/backing argument and fixture recipes. The
unchanged predecessor [NOTICE.md](../selected-continuation-storage/vendor/NOTICE.md)
retains its full source credit. PR2770's numerical lifetime component,
Ross Richardson's PR2831 arena backing, and the separate PR2923 native ADD
numerical/countdown join remain distinct contributions.
Substantial automated assistance was used for analysis, proof drafting,
implementation and internal review.
