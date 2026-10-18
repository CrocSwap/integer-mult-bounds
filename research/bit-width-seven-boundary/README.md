# Selected BIT helper boundaries require a changed prefix

**Status: scoped negative result. No new kappa.**

Under the current contract for restoration of dirty helpers, the selected
PR589 word cannot obtain width-seven helpers by replacing its cleanup alone.
All 439 helpers require a terminal frame of rank eight after
the selected phase B. A stronger two-sided cut already excludes 433 of them
immediately after the retained-total scatter, even if B and C are both
replaced. Six helpers remain outside that exclusion.

This result permits arbitrary finite reversible linear circuits at common frames,
arbitrary rational frame choices, target access, extra restored dirty
registers, and simultaneous changes to several helper endpoints. It does
not assume literal reverse cleanup or the selected frame catalogue. The
suffix must use monotone frame changes and cannot add a COPY or another
operation outside that interface. [PROOF.md](PROOF.md) states the class.

| Boundary | Exact necessary result |
|---|---|
| Semantic compensation before the fixed raw entry | All 439 helper inputs must start at rank zero |
| After D, A and scatter | 433 of 439 helpers must end at rank eight |
| After the selected B | All 439 helpers must end at rank eight |

The six after-scatter survivors are helpers **465, 466, 468, 469, 470, 476**.
They pass necessary rank-seven conditions. No construction or caller-window
admission is supplied for them.

## Why it matters

PR1023 proves that the selected width-eight no-bank placement cannot improve
the bit endpoint on its stated grid. Its width-seven slot model motivates
this work: 74 one-unit conversions could raise bit c by about 5.6% to 6.7%,
before the missing physical boundary costs are known. The present result
shows that those conversions cannot come from a cleanup replacement on the
selected word. With the prefix through scatter fixed, 433 helpers are also
excluded from any B/C rewrite in the stated interface.

At the exact base `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`, the selected
PR942 kappa is `0.001661960547713947`. During this work, main
`ba82555c64e1879e4b7decce28186f208fcb8262` selected PR1042 at
`0.001672188119205421`. Both use the identical PR589 input checked here.
The latter complex value is `0.001674989015937672328468`; the bit value is
`0.001733427039589844234749`. The complex side still binds. This package
does not change either supplier or the selected result.

## Exact evidence

For helper h, two kinds of boundary information must fit in its terminal U:

1. Every boundary register needed to reconstruct the original dirty input
   s_h. The inverse scalar matrix gives this unique set.
2. Every boundary register that still contains s_h. The span of registers
   outside U cannot lose information under reversible common-frame gates.

Their frame join gives the lower bound. CERTIFICATE.json contains all 878
helper/cut rows, both support sets, exact frame identifiers, determinant
witnesses for rank eight, and normal vectors for the six rank-seven joins.
It also contains all 439 nonzero compensation columns.

The generator uses packed binary rows and inverse gate order. The checker
uses sets, reconstructs the prefix matrices, and inverts them by Gaussian
elimination. It checks geometric witnesses with integer determinants and
dot products. It imports neither the generator nor a predecessor checker.
Both use only the Python standard library.

## Reproduce

From the repository root, run:

```sh
python3 -I -B research/bit-width-seven-boundary/verify.py
```

Expected final line:

```text
PASS_BIT_BOUNDARY_OBSTRUCTION after_scatter=433/439 after_B=439/439 entry=439/439 controls=11 no_new_kappa
```

To regenerate the certificate and compare its decoded fields, run:

```sh
python3 -I -B research/bit-width-seven-boundary/derive.py
```

The generator also accepts `--output NEW_FILE`. It refuses to overwrite an
existing file. The verifier does not write files. The two programs accept
`--root REPOSITORY` for an exact pinned input at another checkout.

Eight certificate controls reject a wrong inverse row, a missing dirty
carrier, false frame provenance, a zero determinant, a false normal, an
omitted helper, a false compensation column, and a Boolean rank. Each must
fail for its stated reason. Three small boundary controls accept a legal
rank-seven cleanup and reject one case that needs each separate condition.
The checker also replays all 661 dirty inputs through the original word and
checks the nested frame paths and the required scalar endpoint.

## Attempts and stopping rule

The three candidate approaches were hyperplane cleanup, rank-one entrance,
and a coordinated semantic compensation/cleanup replacement. The first
attempt replaced literal cleanup by an arbitrary inverse circuit. The exact
inverse-row obstruction blocks all 439 helpers after B. The next attempt
moved the cut to the scatter and added the erasure condition. It excludes
433 helpers while retaining six precise candidates for future body changes.

A separate exploratory scan checked direct single-register restoration at
all 198,137 helper/gate-boundary pairs after the helper's last selected raw
gate or scatter use. It found 3,138
locally admitted helper/cut pairs on 462, 463, 464, 467, 470 and 471. These
are readouts, not complete restorations of the other dirty registers. The
scan does not prove a width reduction and is not part of the certificate.
Helper 470 already has the stronger source-deletion construction in PR1043.
No saving from that result is added here.

For rank-one entrances, every helper has a nonzero compensation column.
The semantic prefix argument rules out a promotion that preserves the raw
entry state and zero-frame targets. A new full-width bridge with paid path
0 -> 1 -> 7 -> 8 also fails the optimistic complete cost test: after returning
and consuming the exact idle ranks, it replaces one rank-seven child by
rank-one and rank-six children. PROOF.md gives the strict moment inequality.

The stopping rule is exact coverage of every helper at the two selected
cuts, plus a check of every compensation column. No random search was used.
The six early-cut survivors and changes to A, copies, source preparation,
helper basis, or recursive transport remain open. Closing those routes would
need a different construction or another theorem. This package does not
claim their impossibility.

## Validation limits and source pins

SOURCES.json pins the sole mathematical input by SHA-256 and records the
base, context files, predecessor heads, and later selected comparison.
Context hashes document the reviewed state; they are not moving runtime
dependencies. The exact BIT input is identical at both selected commits.

This is a finite exact certificate with a written theorem. It is not a Lean
proof, a native 5/9/11-stage replay, or a complete physical supplier invoice.
No new word is proposed, so there is no new hosted invoice to certify. The
selected cold replay, full repository regeneration and remote CI are not
claimed. All inherited realization and analytic assumptions remain.

## Credit and overlap

Credit DreamingOfClouds for PR589 and the PR545/510 word and hosting lineage;
eumemic for PR555 and the interleaved interface; Zhihao Chen for the earlier
scalar-interface argument; DaysSky for idle-axis hosting; Jeremy Kothe for
complex hyperplane ends; Dominik Scholz for complex entrance promotion; and
Sagar Thakrar for PR1023's width-packing incentive.

Ali Romman's PR1043 changes the source boundary and deletes helper 470.
PR1079, prepared for Hanson Sun, gives the direct-source substitution census.
PR1048 audits one/two-move reframing with fixed endpoints. PR1100 concerns
positive single-write programs at frames 509 and 521. PR1105 shows that raw
endpoint independence does not justify projected target-feedback cleanup.
This package keeps the prefix fixed and requires the complete final map; it
does not assume that a projected cleanup is valid. It instead allows arbitrary
scalar suffix replacement and changed helper endpoints.
The scope is distinct, and the prior savings are not combined.
PR1122 composes changes to A, B and semantic D while preserving paid frame
paths. Its changed prefix is outside the present selected-word theorem.

Prepared for Ali Romman (@aliromman), with substantial OpenAI Codex assistance
in the research, proof, implementation and review. New material is under the
repository's Apache-2.0 license. Separate code paths do not imply independent
human review. No push, PR creation, or selected-frontier edit was made by this
worker.
