# Selected R439 compensation through a restored target basis

**Finite bit-circuit construction; no new κ.** Applying the target-basis
method of PR713/716/794 to the selected PR589 word saves **11,097 additions**:
the full local word falls from **24,305 to 13,208 ADDs**. All target
preparation, helper reads and target restoration are paid. Helpers, copies,
frame paths and paid recursive ranks stay unchanged.

The positive reverse bound increases. The candidate needs **100 local payload
bits** under the inherited 104-bit ceiling. The source nine-stage expression
`2^18 F^5 B^4` needs **189 bits**, within the existing **192-bit prefix charge**.
A full changed-word hosted invoice and supplier integration are separate work.

| Quantity | Selected PR589 | Candidate |
|---|---:|---:|
| D target preparation / restoration | 0 / 0 | 306 / 306 |
| D helper injections | 18,085 | 6,376 |
| Complete D ADDs | **18,085** | **6,988** |
| Other local ADDs | 6,220 | 6,220 |
| Complete native ADDs | **24,305** | **13,208** |
| Exported records | 27,234 | 16,137 |
| Forward positive bound F | 49,347 | 49,347 |
| Reverse positive bound B | 1,113,070 | 9,534,616 |
| Local payload bits | 93 | 100 |
| Nine-stage prefix bits / charge | 177 / 192 | 189 / 192 |
| Helpers / retained copies / paid rank mass | 439 / 9 / 5,129 | 439 / 9 / 5,129 |

## Required interface change

Only the frame-zero D prefix changes. For the original binary compensation
matrix K, the new D applies an invertible target basis E, adds helpers along
`R = E K`, and undoes E in literal reverse order. Thus

```text
E^-1 (E y + R s) = y + K s.
```

This holds for arbitrary target inputs y and arbitrary helper dirt s. D never
writes a source or helper. Every non-D field is identical to PR589.

**The original syntactic H2 and its direct K extractor reject this word.**
Their false results are retained in the receipt; the source checker is
unchanged. The replacement contract is a legal frame-zero D with complete
operator `(x,y,s) -> (x,y+Ks,s)`. The proof of prefix substitution is in
[PROOF.md](PROOF.md), following the semantic D-boundary work of PR686 and
the target-side constructions of PR713/716/794. The original H1/H3/H4/H5,
all other interface conclusions, complete geometry, frame legality and full
arbitrary-input endpoint pass. Maintainer acceptance and source binding of
this semantic contract are required for integration.

The identity is over F2. The signed integer lifts have newly computed
cancellation-free bounds; no equality of the forward integer matrices is
asserted. The existing common-label, mutable-source and realization assumptions
remain inherited.

## Reproduce

Use Python 3.12+, a C++17 compiler and Boost headers:

```sh
python3 -I -B research/r439-target-compensation/verify.py
python3 -I -B research/r439-target-compensation/test_package.py -v
```

Expected main marker:

```text
PASS_R439_TARGET_COMPENSATION: D=18085->6988 ADDs=24305->13208 steps=306 nine_bits=189; semantic D; no new kappa
```

`CXX` selects the compiler; `BOOST_INCLUDE` selects a directory containing
`boost/` if it is outside `/usr/include`. No Python packages, Git metadata or
network are needed. `--output NEW_DIRECTORY` retains logs, regenerated data
and fresh native binaries; `--receipt NEW_JSON` writes the full deterministic
receipt. Both refuse existing paths. Without these options, outputs are
temporary and nothing is written to the package. `--source-root` supports a
relocated minimal closure of the 14 in-tree inputs in [SOURCES.json](SOURCES.json).
The pinned PR794 proof is retained verbatim under `provenance/`.

The verifier repeats the nomination, compares every decoded candidate field,
reconstructs the recipe using independent set-valued rows, and literally
replays the complete positive word in **both directions for all 306 accepted
steps** (9,643,960 instructions). It checks **661 separate Boolean input
columns** on baseline/candidate D in both directions. All full source checks
then run, with exactly the two expected syntactic rejections recorded.

Unchanged native legality and 5/9/11-stage checkers accept both complete words
on **883 / 1,327 / 1,549 columns** per word. All **96 omitted-bridge controls**
reject. Fourteen local controls cover missing entrance/restoration, wrong undo
order, missing helper injection, frame/operand/receipt faults, unrelated edits
and precision overruns. A missing entire entrance passes helper-only checking
and fails arbitrary-target checking. A cancelling target pair is accepted
semantically and charged two ADDs. Eight package tests cover source corruption,
typed JSON, recompression and output preservation. Executed portability checks
are recorded in [VALIDATION.md](VALIDATION.md).

The nine-stage prefix expression is bound to the pinned source AST, bridge
exponent and PR589 baseline receipt. Its new bound is
`633952218342189222305933054575935669674977721489175871488` (189 bits).
This check does not reconstruct the hosted parent or its complete finite invoice.

## Bounded search and prior work

OS seed **10** selected the bit track and the compensation candidate among
three tasks. The [local claim](CLAIM.json) records the domain, stopped searches
and overlap review. Each iteration scores all 12,210 ordered target pairs,
charging two basis gates for a row change. Seed 10 fixes tie order. The search
accepts the highest-gain pair satisfying exact forward and reverse guards;
it stops at no eligible gain or 1,000 accepted steps.

This run stops after **306 steps and 3,748,470 pair scores**, with **218,204
positive scores across the successive matrices**. No prefix guard rejected a
nominee in this run. Independent enumeration of all 12,210 final pairs gives
maximum additional gain **zero**. This is a local stopping certificate for
one additional paid row shear. Neutral detours, multi-step improvements,
helper-basis changes and globally optimal circuits are outside the search.

**commdata2338's PR794** supplies the guarded target-basis method and exact
incremental bound argument, on historical R420. **Scott Woolsey Biggart's
PR713** and **Sagar Thakrar's PR716** give earlier target-pair constructions;
**Mikhail R. Gadelha's PR686** and **Greer Guthrie's PR694** supply the semantic
D-boundary/helper-basis lineage. This contribution applies that mechanism to
the selected punctured R439 matrix, supplies the 11,097-ADD reduction and
replays all accepted-step bounds independently. It claims no priority for
basis factoring or the semantic contract.

PR848 explains why R439 sharing is blocked by the unchanged H2 syntax; this
uses the explicitly stated semantic replacement. PR904 changes A/B windows
and leaves D unchanged. No combined candidate with PR904 or any other circuit
PR is certified. The selected #799 κ stays `1661634653669567/10^18`.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Word: **DreamingOfClouds's PR589 tuning of eumemic's PR555**,
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
Integration requires acceptance of the semantic D boundary and a full updated
hosted reconstruction and invoice. The selected construction's other assumptions
are recorded in the [maintainer review](../../docs/research/community-frontier799-review.md).
These finite checks do not prove that the construction compiles correctly for
every input size or establish the analytic reduction used by the multiplication
theorem. The selected construction is unchanged; no runtime improvement is measured.

Prepared for **Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance**. One AI agent performed the work; no independent human review
is claimed. Apache-2.0. See [NOTICE.md](NOTICE.md).
