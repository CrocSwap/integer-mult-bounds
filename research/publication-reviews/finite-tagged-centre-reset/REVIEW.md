# Independent publication review: finite tagged centre reset

Accepted within the stated local and conditional scope. No unresolved
finding blocks this package. This review does not establish a complete
supplier, a universal precision lower bound, or a kappa improvement.

The reviewed final package manifest has SHA-256
`cf75b588f7bfef9d2836808c3494f4c2171fa8a37f02e97b8ae7961bb3a0621a`.
All 44 listed file hashes match. The package has 45 files, including the
manifest. The review used a separate OpenAI Codex agent. It is not a
human peer review.

## Review method and fresh execution

I read the new proof, README, notice, replay driver, and source inventory.
I checked the steps of the version 2 grid proof, the return-grid
correction, the corrected physical phase argument, the exact policy
proof, and both original independent reviews. I read both independent
checkers in full. They use explicit failure checks, so `-O` does not
remove their validation. They do not import the producer scripts.

I copied the frozen package to a new directory outside the workspace
and ran this command with one process at a time:

```sh
python3 -I -O -B /private/tmp/finite-tagged-reset-independent-20261022/replay.py --out /private/tmp/finite-tagged-reset-independent-result-20261022
```

The run took 14.074358 seconds. Both complete receipts match the frozen
independent receipts. The final status was:

```text
PASS_FINITE_TAGGED_CENTRE_RESET_PACKAGE
```

The [replay receipt](REPLAY.json) records the commands, runtime, source
manifest, and result hashes. The [local receipt](tagged-grid.json) and
[policy receipt](reset-policies.json) contain the decisive counts.

I also wrote [separate controls](check_review_controls.py), without an
import from another research checker. They replay the scalar cut on
each nonzero helper basis input, test the effect of a false zero reset,
expand the three error-margin formulas exactly, and check the parent
return-grid counterexample. See [their receipt](ADDITIONAL-CHECKS.json).
The scalar control leaves native canonical contents unchanged. It does
not repeat the native phase audit.

## Local construction

The fixed cut has centre contents `u+RY/4`. If the eight centre contents
are replaced by `v` and their eight old signs are skipped, the suffix
returns `Y` and `X-Y+R^T(v-u)`. The affected helper modes return `v`.
Thus `v=u` is necessary for the claimed arbitrary-helper restoration.
The other 472 helper modes are unchanged. The complete replay checks
all 704 input columns and restores all 480 helper contents.

The separate controls set each of the eight centre helper inputs to one.
Preserving its baseline restores the full column. Setting the baseline
to zero loses that helper and adds exactly `-R^T u` to the data output.
This rejects a false purity assumption. The local word clears only the
owned private field `C0`; it does not clear the helpers.

For the physical decoder, let `h,q` lie on the declared grid. From
`z=h+(1+delta)q+e`, the first nearest-grid rounding recovers `h+q` under
the stated strict margin. Subtracting that value and dividing by `delta`
recovers `q` by a second rounding. The coarse error allowance alone does
not meet the second margin. The source check tests 11,025 exact decoder
cases and its negative control. The proof gives the general identity.

The word adds 232 COPY, 240 SCALE, 240 ADD, 233 CLEAR, and 1,416 ROUND
passes, for a total of 2,361. The tag uses the owned field and the allowed
operations; it does not require a direct nonunit scale by `1+delta`.
There is no added native child. The sufficient fine profile contains
124 rank-one and eight rank-four children, with rank mass 156. The check
tests all 132 direct error impulses. This profile is sufficient for the
local proof; it is not the policy optimum below.

The physical grid premise uses the corrected quadratic conjugation
`K F_r K*`. A frame basis alone does not justify a plain product of its
listed transforms. The retained version 2 phase review gives the needed
argument. Its full audit and the underlying native kernels were not
executed again in this publication review.

## Finite error and carrier scope

The proof separates the relative child computation error from absolute
parent return rounding. A child value halfway between two parent grid
points has relative return error `1/2`, even for an exact child. Thus a
relative child contract alone cannot prove the stated parent margin.

For `g <= t+B e` and `P=2B e+2H+4G+32`, exact expansion gives the three
slacks `B e+H+2G+10`, `G+6`, and `B e+G+10`. The additional checker
confirms these identities without sampling. The source checker also
tests 96 exact margin cases. The `31,304 < 2^16` insertion count and the
scalar denominator and growth sums agree with the source word.

Errors may depend on earlier actual inputs. The proof uses each error
as an additive insertion and uses exact zero suffix responses. It does
not assume that the numerical errors lie on the coarse lattice. The
parent rounding allowance and all precision-width conclusions retain
the declared native and record-format premises.

The carrier witness is a local resolution statement for its specified
packing. I requested the explicit conditions `g>=3` and
`s_k in 2^-g Z intersect [-1/8,1/8]`. These conditions put all witness
inputs on the declared grid. The producer added them to the new proof.
This resolved the only review finding. It does not imply a lower bound
for arbitrary decoders or encodings.

Exact restoration starts from the declared grid inputs. Conversion from
finer caller records is outside this proof. That conversion needs its
own error and restoration argument before a complete node can use this
word.

## Complete policy family

The family permits any subset of individual pure-target resets after
existing scalar or native events before the fixed centre cut. It keeps
the ideal target row and sets its error derivative to zero. The theorem
grants these resets free implementation cost. It adds no access edge,
joint reset, changed basis, chronology, or error contract.

The exact check reconstructs all 860 eligible sites. Of these, 644 precede
the first native event. The remaining 216 are pure helper resets; the
last pure data reset occurs at event 637. A Boolean union-path argument
removes 180 irrelevant sites. A reset can delete a path but cannot create
one, so this step does not assume that numerical cancellations persist.
The remaining 36 sites form three disjoint groups of 12. No native error
ancestor is shared between those groups. Consequently, all 12,288 group
policies cover all `2^36` effective global policies.

The rational checker enumerates all 4,096 policies in each group and
composes all 255 nonempty query subsets. It also runs 528 direct native
error impulses for the empty, full, and optimal policies. These checks
agree with the complete frozen receipts. Resetting every eligible site
is not assumed to be optimal.

The all-query optimum uses reset events 10008 and 10012. Its profile is
121 rank-one and eight rank-four children, with mass 153. The minimum
masses by query count are `25,44,60,65,90,109,134,153`.

For every policy and nonempty query subset, the exact profile gives
`n1-4|S| >= 17`. With `x=2^sigma` in `[1,2]`,
`8^sigma-4^sigma=x^2(x-1) <= 4`. This proves the claimed moment surplus
of at least 17 on the full interval. Equality is witnessed at `sigma=1`
by the stated single-query masks. This is an analytic extension of exact
profile enumeration, not a sampled exponent search.

The layer integral gives the weighted-width statement under the stated
independent relative-error model. A policy that varies by layer retains
the stated additive cost conclusion; the proof does not emit such a
combined native word. No conclusion follows outside this reset family
and width model.

## Final document binding and omitted work

The cold replay used manifest
`59a8e93a315f09307ce40d0145f2d865599e232f21a0d12c7a98d6c7903ac8fd`.
The final manifest differs only in the new `PROOF.md` entry for the input
grid clarification above. All executable files and all frozen inputs are
unchanged. I inspected the exact diff and verified every final package
hash. [FINAL-DOCUMENT-CHECK.json](FINAL-DOCUMENT-CHECK.json) records that
comparison. No mathematical replay was repeated for this document change.

The complete native phase audit, historical record and tape audit,
finer-caller entry conversion, complete node endpoint and owner admission,
and a complete finite invoice were not performed here. The proof does
not establish admission to the changed PR #4470 selected construction.
The package is accepted for publication as a local construction and a
scoped conditional cost theorem only.
