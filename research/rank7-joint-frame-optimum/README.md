# Complete A/B/restore frame optimum for the six-skip words

Both pinned PR3042 providers already minimize their complete local frame bill
when **all A/B and restore scalar frames may change jointly**, with scalar
operations/order, endpoints, centre interfaces and warp interfaces fixed.
The result holds uniformly for `0 < b <= 1/100`. It extends PR3057's
restore-only result to all 6,141 A/B/restore scalar events. It supplies a scoped
mathematical obstruction, **not a new κ or supplier admission**.

## Exact claim

At every scalar event, choose any subspace of F₂⁹ common to its operands.
Each register's frames must increase by containment between fixed interfaces.
Keep the initial and terminal frames, the eight centre interfaces, and the
input/output frames of every literal A/B warp fixed. The removed helpers
remain unused. Charge every rank-difference transition, including transitions
to fixed interfaces and endpoints, and the fixed centre descents.
The precondition, compensation, cut and full-frame cleanup sections stay fixed.

This is a relaxation of native admissibility. In particular, it permits a paid
frame climb just before a fixed interface. An actual native program may require
the preceding event to reach that interface already. Allowing more assignments
makes the negative result stronger within the stated fixed-interface contract.
Operator/cone/phase checks can further restrict these assignments.

For `Hr(b) = r(73/r)^b`, the minimum complete local profile is the source's:

```text
{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}.
```

The fixed endpoints retain 408 ordered helper widths with inventory
`{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}` and all 91 private return buffers.
The same two complete frame problems give identical receipts. The idle bill
has no changed width to exploit under the inherited owner contract. This is
not an independent replay of that allocation or its physical implementation.

## What is new

[PR3057][3057] left joint prefix/restore reassignment open. Its fixed prefix
left 27 restore variables and 2,160,000 assignments per provider. This proof
allows every scalar frame in A, B and restore to vary. Forward/backward
propagation leaves 743 variables with quotient dimension at most three.
They form 210 independent components; the largest has 94 variables.

Exact elimination needs 57,681 candidate combinations and 9,776 projected
states per provider. The largest step has 2,560 combinations and six boundary
variables. Every component's source profile is optimal throughout the declared
exponent interval. [RESULT.json](RESULT.json) records the complete component
orders, source/optimum profiles, and exact feasible and optimal counts.

The discovery probe used a numerical CP-SAT objective at `b=0.00173` and found
no improvement. That probe is not evidence used by the published verifier.
The retained proof uses Python's standard library, integer arithmetic and
rational inequalities, without an optimizer, floating-point objective, imported
predecessor checker, numerical root or cached result as an acceptance gate.

## Reproduce

Python 3.12 and its standard library suffice. The direct replay takes about
one second on the recorded macOS host:

```sh
uv run --python 3.12 --no-project python -B -W error \
  research/rank7-joint-frame-optimum/verify.py
uv run --python 3.12 --no-project python -B -W error -m unittest discover \
  -s research/rank7-joint-frame-optimum -p 'test_*.py' -v
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/rank7-joint-frame-optimum
```

The final verifier line is

```text
PASS_JOINT_FRAME_OPTIMUM providers=2 scalar_events=6141 variable_frames=743 components=210 range=(0,1/100] no_new_kappa
```

Add `--output /external/path/RESULT.json` to regenerate the deterministic
receipt. The verifier does not read the committed receipt. All contracts remain
active under `-O`. [PROOF.md](PROOF.md) gives the completeness and tariff
arguments. [SOURCES.json](SOURCES.json) authenticates the unchanged gzip exports
from PR3057, including exact source commit, Git blob and SHA256. Their literal
word provenance is PR3054 `4773c3ea67b471415870e38411fae313ec44a675`, retaining
PR3042 `84cc406ad91ec53fff329a11a445d7effe564a77`.

## Scope and stopping decision

The proposed local improvement was not found. The useful retained result is a
uniform optimum theorem for the entire fixed-scalar, fixed-interface frame
problem. No construction search is expanded after this proof.

Changing scalar operations or order, warp frames/maps, centre interfaces,
entrances/endpoints, helper inventory, or allowing nonmonotone frame transforms
changes a hypothesis. Such mechanisms remain open. PR3056's scalar contraction
and PR3060's native-tariff rewrite are explicitly outside this fixed-word scope.
This does not exclude new multiplication algorithms or improve the selected κ.

Scalar/operator correctness, source-native realization, literal ownership,
physical movement/backing, precision/tape, stock/caller, analytic and all-size
compiler obligations remain inherited. No full cold replay or outer release
was run for this unchanged-word lower bound. Unknown implementation costs are
not assigned zero.

## Open next questions

Can one changed scalar block or warp interface reduce the complete bill?
Start with its exact arbitrary-dirty operator and compare the full resulting
frame graph, helper widths, cleanup and consumer charges against this baseline.
A legal source/native realization and complete-cost replay are the blockers.
This proof tells a follow-up which fixed-word premise must change; it does
not justify another seed search with the same interfaces.

## Credit

Nick Petalas contributed this joint graph and exact elimination proof.
Credit dcharb78 for PR3042's six-skip words, Jeremy Kothe for the scalar/frame
accounting and R1, Marius-Paul Dumitrean for PR2979's coordinated rank-seven
construction, Sagar Thakrar for PR3053's reassignment handoff, and Gareth
Davidson for the earlier fixed-word monotone-frame bounds in PR1995/2013.
PR3057 supplies the explicit-subspace representation and retained word exports.
The source lineage includes Mason Hale, Jeremy Diviney, Yiyang Lu,
Ross Richardson, Tekalign, Dugongue, icekylinx and themilkman216.
The original [notice](inputs/NOTICE-PR2979) is unchanged. Apache-2.0.
Development used substantial automated assistance. Evidence is author-checked;
no independent human review or proof-kernel validation is claimed.

Build the Lever led to the rerunnable exact elimination checker. Prove It Works
led to literal source recounts, an improvable fixture and separate proof/code
review. Engineering limits and verification are recorded in
[ENGINEERING.md](ENGINEERING.md). Canonical baseline is
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.

[3057]: https://github.com/CrocSwap/integer-mult-bounds/pull/3057
