# R439: all-support common-frame kernel entrance classification

**Scoped negative result in the bit-supplier track; no new κ.** For the fixed
PR589 R439 word, the only nonzero binary response-null direction whose entire
support shares a nonzero rational first-contact frame is

```
e_444 + e_470,
U = span_Q(0, 1, 0, -1, 1, 0, 1, 0).
```

This is the same pair already constructed by Adam Gall in [PR1179](https://github.com/CrocSwap/integer-mult-bounds/pull/1179).
The new result removes that package's support-at-most-four restriction:
**arbitrary binary support sizes among all 439 helpers are covered**. There is
no second independent null direction in this fixed common-entrance model.
This does not exclude changed raw words, later chronological cuts, changed
first-contact frames, differently timed basis changes or different physical
interfaces.

## Concrete evidence

The selected record at base `dd6403f774a0891093a006ae9716c02e371b1fdb`
selects #1094, conditional κ `0.001672660197076918`, with the unchanged #589
bit supplier. Its actual source manifest binds the word used here. The complex
supplier binds. The selected record, `upstream/` and predecessors are unchanged.

| Object | Exact result |
|---|---:|
| Original dirty helper columns | 439 |
| Distinct first-contact rowspaces | 264: 111 lines and 153 planes |
| Helper counts by first-contact dimension | 286 at rank one; 153 at rank two |
| Distinct plane pairs checked | 11,628 |
| Pairs meeting in a line | 549 |
| Complete nonzero intersection closure | 366: 213 lines and 153 planes |
| Restricted response spaces with zero nullity | 365 |
| Restricted response spaces with nullity one | 1 |
| Helpers eligible at the unique surviving line | 390, 391, 444, 470, 578, 580, 582 |
| Complete nullbasis there | `{444,470}` |

The full [certificate](CERTIFICATE.json) records every subspace, every eligible
helper set, its exact binary rank and a complete nullbasis. `verify.py` also
rederives the raw A/scatter/B/C operator and checks equality with compensation D
on all 661 dirty columns. COPY values are snapshots of the retained helpers;
this finite scalar endpoint check is not a native COPY/ERASE or physical audit.

The [proof](PROOF.md) explains why the finite closure covers every rational
common entrance and every support size. The main engine uses rational RREF,
orthogonal complements and binary column elimination. A separately written
engine uses exact Gram projectors, two-column residual equations, and binary
row elimination. They compare all 366 spaces and all 366 restricted response
matrices, rather than just agreeing on final counts. Neither engine imports the
other or PR1179's implementation.

## Reproduce

Python 3.10 or newer, standard library only, from the repository root:

```sh
python3 -I -B research/r439-kernel-entrance-closure/verify.py
python3 -I -B research/r439-kernel-entrance-closure/independent.py
python3 -I -O -B research/r439-kernel-entrance-closure/test_package.py -v
```

The first two commands print `PASS_R439_KERNEL_ENTRANCE_CLOSURE` and
`PASS_R439_KERNEL_ENTRANCE_INDEPENDENT`, with 366 classes and the unique
`444+470` direction. The test command checks all 4,096 binary 3×4 response
matrices against all 16 support masks, a minimal six-helper dependency beyond
the old cutoff, rational geometry controls, source/receipt corruptions and a
relocated optimized replay. See [VALIDATION.json](VALIDATION.json) for the
executed environment and results.

The package also opts into the bounded registered replay:

```sh
python3.12 scripts/research_package.py --package research/r439-kernel-entrance-closure
```

The registered wrapper specifically requires Python 3.12. The standalone commands
also pass on Python 3.14. Exact source bytes and the base commit are pinned in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical Git provenance, not moving
runtime inputs. This package does not rerun the selected hosted construction,
PR1179's complete candidate, native compilation, all-size interfaces or the
multiplication theorem.

## Scope and paid-cost implication

The question is whether a new binary helper direction `c` can satisfy `Kc=0`
while every helper in its support can receive the **same nonzero rational
entrance subspace before its original first raw contact**. The raw word and
its first-contact frames are frozen; no helper/source/target replacements,
free frame descent, reassigned frame paths or later-cut borrowing are allowed.
Geometry is over Q; response coefficients are over F₂. An algebraic direction
is necessary, not sufficient, for a compiled and hosted entrance gauge.

PR1179 already supplies the known direction's finite entry/exit shear witness.
Its inherited complete local bill is 24,252 ADDs versus 24,305, with rank mass
5,128 versus 5,129; those construction claims are credited, **not re-executed
here**. Its old width-eight host needs an additional rank-one idle child when
hosting the width-seven residual, cancelling the local one-rank gain before
adapters. Even granting free entry/exit synthesis cannot create another algebraic direction.
This package supplies no new gate saving, physical invoice, hosted
supplier, precision improvement or exponent saving. It closes only the hope
that larger supports alone produce another direction under the same boundary.

## Task, overlap and stopping rule

OS assignment seed **5**, drawn with `secrets.randbelow(100)`, selects the bit
supplier track in the user's assignment. The alternatives and local claim are
in [CLAIM.json](CLAIM.json). The catalogue card is declared **changed** in
[TASK.json](TASK.json): this investigates a nonzero-entrance necessary condition,
not a replacement H2/K proof for frame-zero helper mixing. PR1194 already covers
that narrower semantic-D task.

Live open-PR and discussion checks preceded the experiment and submission;
there was no pinned coordination issue, so the authorized local-claim fallback
was used. The experiment stops after the complete intersection closure and all
restricted kernels, with independent verification. It is not an enlarged
random sparse-support search. All support sizes are handled by exact nullspace
algebra. Scope exclusions remain material.

## Open next questions

The full fixed-first-contact common-frame question is closed by this result.
A useful distinct next step is to choose one later chronological cut and
recompute both the remaining response and actual current frames, then price
all transport and restoration. Such a cut may change this necessary condition;
the blocker is a complete, legal entry/exit and hosting contract. No wider
search under the same frozen first-contact rule is warranted.

## Credit and AI disclosure

Prepared for **mightyOil** with substantial **OpenAI Codex, GPT-6 Astra**
assistance in research, proof, implementation, verification and writing.
The two algorithms were written by the same AI-assisted contributor; no
independent human review or proof-assistant verification is implied.

Adam Gall's #1179, pinned at `a09f799fdb312e049a81f59b44f1339b5a053bbe`,
provides the sparse-support first-contact formulation and the known pair's
construction. This package independently corroborates that pair and completes
its support domain; it makes no priority claim for the gauge mechanism.
Dugongue's #254 (`9ce32efb421132420242cfdb91ddd9eabe2c3795`) and
Chafik Boukhalfa's #382 (`536329e6cddd37d70a6b52cbe2c2604ea18c5e83`)
are earlier kernel-entrance precedents. DreamingOfClouds' #589
(`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`) supplies the tuned word on
eumemic's #555/#543 construction. Their original notices and license remain
unchanged. Ali Romman's #1128 and #1043, Hanson Sun's #1079, and the broader
kernel/retiming lineage are related work, not imported dependencies. New work
is under the repository's Apache-2.0 license.
