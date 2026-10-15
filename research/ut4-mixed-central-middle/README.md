# The mixed UT4 z/uz endpoint needs exactly fourteen calls

In PR2027's formal `F2[UT4(F2)]` model, one pure-central z target and one
central-twisted uz target require **fourteen paid calls**, for every finite
number of arbitrary dirty roles. The existing direct fourteen-call word attains
this minimum. No physical supplier or new kappa is claimed.

This answers the first concrete case in
[PR2027's open next question](../ut4-mixed-root-tariffs/README.md).
The target premise changes to include a pure-central role, outside that
predecessor's sharp family. The paid alphabet remains the three adjacent letters
and every nonzero binary rank-one coupling, including nilpotents. Scalar mixing
is free, but clean roles, free address maps, COPY/ERASE and unpaid undo are not.

## New result and evidence

[PROOF.md](PROOF.md) gives a general necessary middle bound
`n_b >= 2d+k`, where d is the number of active target roles and k counts
pure-central roles. It extends the predecessor's `2d` bound; it is not a sharp
tariff for every mixed family and does not replace stronger central-only bounds.

For z/uz this gives counts at least `(4,5,4)`. At thirteen total calls, every
scalar column and row span is exactly the active two-role plane. Thus every
putative thirteen-call word already acts only on those two roles, even when
unlimited restored dirty workspace is available.

The new standard-library checker completely excludes that split:

| Exact census | Count |
| --- | ---: |
| Zero-sum ordered middle sequences | 3,600 |
| Distinct four-call outer profiles | 9,721 |
| A / C profiles passing their coefficient screens | 89,052 / 1,201,320 |
| Cross-compatible key / profile pairs | 68 / 152 |
| Fully expanded thirteen-call words | 5,536 |
| Complete quotient survivors | 0 |

Of the expanded words, 1,480 first fail the AC coefficient and 4,056 first fail
ACB. Rejection in the necessary quotient excludes a formal identity. The checker
accepts the existing fourteen-call upper witness only after checking its **full
formal operator**, including arbitrary dirty workspace.

The middle four-matrix relaxation does admit five columns. A tested fixture in
the proof makes the distinction explicit. It is not a chronological word; the
remaining quotient coefficients exclude all actual thirteen-call candidates.

The profile-screen method is credited to Aaron Wang/PR1690. This implementation
builds concrete gap placements directly, without importing predecessor code.
An optional LOCAL-ONLY exploratory cross-check using the retained PR1690 helpers
gives the same census counts; it is not an additional proof premise. The kept
tests use dense matrices and a separate forty-word relation quotient, compare all 20,440 short words, recover planted
thirteen-call words, compare indexed joins with direct pairs, and execute all
192 faithful regular-action basis columns of the upper witness. Fifteen
full-endpoint failure controls, a mutated relaxation, invalid paid alphabets,
source drift and output-overwrite controls also pass.

## Reproduce

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/ut4-mixed-central-middle
python3.12 -I -O -B research/ut4-mixed-central-middle/verify.py
```

Expected scientific marker:

```text
PASS_UT4_MIXED_CENTRAL_MIDDLE minimum=14 middles=3600 words=5536 q_pass=0 no_new_kappa
```

The full checker takes about eleven seconds in the recorded local environment. Normal replay writes
nothing. `verify.py --emit NEW_PATH` explicitly regenerates a deterministic
receipt and refuses existing outputs. [EXPECTED.json](EXPECTED.json) includes
the complete expansion digest. [SOURCES.json](SOURCES.json) pins predecessor
proofs and provenance. [VALIDATION.md](VALIDATION.md) records actual checks and
limits; [TASK.json](TASK.json) records the scope and upstream freshness.

The scientific base is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The selected kappa remains `0.001672660197076918`; the selected cold command is
`make frontier1094-verify`. That full supplier replay was not run for this
standalone formal-model result.

## Open next questions

1. Does a fourteen-call word with five b calls exist if one outer letter uses
   five calls? This matters for weighted tariffs when b costs more than an
   outer letter. Start with the `(5,5,4)` and `(4,5,5)` profile domains and their
   enlarged span slack. The thirteen-call compression does not automatically
   extend to those domains or arbitrary workspace.
2. Can the formal a,b,c alphabet be implemented with a favorable complete
   recursive bill? Start with one physical letter and its actual frame,
   dirty-state, restoration, hosting and precision contract. No rational-frame
   or compiler realization is provided here.

The first question is mathematical follow-up, not evidence of an attainable
weighted saving. The second is required before any supplier interpretation.
Structured questions are in TASK.json.

## Scope and credit

This is a computer-assisted formal-algebra theorem with a written uniform
workspace implication. It is not a Lean theorem, a physical bit supplier,
a rational-frame identity or an improvement in the multiplication exponent.
Native/compiler, common-label realization, hosting, precision/tape, all-size
and analytic-transfer obligations remain outside scope. No independent human
review or hosted CI success is claimed.

Credit Gareth Davidson/PR2027 for the mixed target family and this handoff;
ToikY/PR1662 and PR1680 for the degree-three quotient and compression methods;
Aaron Wang/PR1690 for profile screening; and steph4n-gh/PR1573, Arham Tahir/PR1589
and Hanson Sun/PR1607 for the zero-sum and coefficient-span lineage. The direct
upper word is predecessor work, not a new construction. All original source
files and notices remain unchanged. New material is Apache-2.0.
