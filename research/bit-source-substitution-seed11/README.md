# Direct-source substitution census for the selected R439 bit word

**Scoped negative result; no new kappa.** In the class defined below, the only removable helper in PR589's tuned R439 word is helper 470, the source 77 boundary already constructed by Ali Romman in [PR1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043). This package adds a complete finite census and six exact frame obstructions. It does not claim that helper deletion, other circuits, or the bit supplier are globally optimal.

The base is `2921874911956718fcaaaf9396fe8267b3cfa9f0`, whose selected conditional kappa is `1661960547713947/1000000000000000000`, from PR942 with unchanged PR589 on PR555. The selected record is context, not a moving runtime input. The two consumed files and their exact SHA256 pins are in [SOURCES.json](SOURCES.json).

| Classification | Helpers |
|---|---:|
| Retained decoder totals, outside the deletion class | 9 |
| A read has no eligible source with the same clean response | 423 |
| All reads have unique source matches, but frames forbid substitution | 6 |
| Admitted, already known from PR1043 | 1 |
| Total | 439 |

The census covers all 430 non-retained helpers, all 2,102 of their A/B read occurrences, and all 111 source identifiers at each occurrence: 233,322 source slots screened, with self-donors excluded. Every symbol represents a complete linear response to the 111 source input coordinates; these are exact F2 calculations, not sampled inputs. All seven helpers surviving the response screen have a unique source match at every read. There is therefore no unsearched donor-choice branch for those helpers.

## Precisely bounded class

Choose one non-retained helper q. Delete every A/B gate whose destination is q. At each surviving A/B read of q, replace that occurrence by one current source register s, distinct from the destination. Cancel repeated operands over F2. Require that q and s have equal clean-source response rows immediately before that gate in the original word. Helper inputs and target inputs are set to zero only for this response screen; they remain arbitrary in the final construction checks.

Keep all other A/B gates, their order and frames fixed. Keep start/final frames, retained totals and COPY frames fixed. A changed read may use any common frame; the six exclusions below do not restrict it to the shipped catalogue. Rebuild C as the literal full-frame inverse of the surviving z-gates. Rebuild frame-zero D from the complete dirty-helper response. Source access, restoration and compensation are not free.

This class permits multiple reads of a helper, different source donors at different reads, and mutable sources carrying sums. It excludes simultaneous helper deletion, extra arithmetic gates, helper donors, reordering, changes to nonincident gates, decoder changes, and replacements that alter a clean response locally but cancel later. Those are possible directions outside this result, not ruled-out mechanisms.

## Why the certificates exclude the other helpers

Write alpha_r(t) for register r's clean-source response just before event t. Deleting a q-destination gate does not change another register. At a q-read, replacing q by s preserves the destination response when alpha_q(t) equals alpha_s(t). Induction therefore preserves every surviving clean response at every boundary. The independent checker reconstructs all these rows with sets and checks every candidate source, separately from the generator's packed-bit implementation. For 423 helpers it confirms a read with no permissible source. This excludes them from the stated local-preservation class; it does not exclude compensating global rewrites.

For each of the remaining six exclusions, temporarily omit every q-incident gate when finding fixed frame anchors, including changed reads as well as deleted writes. This relaxes the constraints: any legal replacement must still respect the previous and next unchanged event on each operand. COPY events remain fixed anchors.

At the witnessed replacement, one operand must already contain a line ell from a prior fixed frame L. Another operand must subsequently enter a fixed frame U. Any common frame F would require L to be contained in F and F to be contained in U. The certificate supplies an integer normal vector perpendicular to every generator of U but not perpendicular to ell. Thus ell is not in U, and such an F cannot exist, even outside the original frame catalogue. The checker verifies these dot products directly and independently reconstructs the anchors; it imports no search or nullspace routine.

| Helper | Forced source | Obstructed read | Prior fixed frame | Later fixed frame | Separating line |
|---|---|---|---|---|---|
| 462 | 47 | A[1986] | register 349 at 123 | source 47 at 121 | 48 |
| 463 | 52 | A[1986] | register 349 at 123 | source 52 at 120 | 48 |
| 464 | 54 | A[1987] | register 340 at 506 | source 54 at 56 | 5 |
| 467 | 27 | A[1991] | register 385 at 76 | source 27 at 156 | 74 |
| 469 | 50 | A[2030] | register 413 at 390 | source 50 at 52 | 1 |
| 471 | 92 | A[1994] | register 444 at 79 | source 92 at 184 | 77 |

All identifiers are zero-based original word identifiers. [CERTIFICATE.json](CERTIFICATE.json) contains every read, every matching source, the precise anchor events, and the six separating vectors.

## Reproduce and controls

To reproduce this result, run the following from the repository root with Python 3.10 or later and its standard library:

```sh
python3 -I -B research/bit-source-substitution-seed11/check.py
```

Expected final line:

```text
PASS_SOURCE_SUBSTITUTION_INDEPENDENT helpers=439 retained=9 clean_blocked=423 frame_blocked=6 survivor=470 reads=2102 controls=10 no_new_kappa
```

The checker reconstructs the known helper 470/source 77 substitution at frame 186 without importing PR1043 code. It removes the helper, rebuilds C and D, and checks all 661 baseline and 660 candidate dirty-input columns. The complete local ADD count, including scatter, restoration and compensation, is 24,305 before and 24,248 after; the local paid rank masses are 5,129 and 5,121. These corroborate PR1043's local witness and are not new savings. The unchanged owning checker also accepts E8 geometry, all frames, copied totals, H1-H5 and the scalar interface on both words.

Ten controls reject illegal late access, a scalar match with illegal frames, the wrong donor, missing cleanup, missing compensation, retained-helper deletion, omitted census coverage, a corrupted clean row, a false separator and a false anchor. A neutral pair is accepted and charged two ADDs. To regenerate and compare the certificate using the separate bitset implementation, run:

```sh
python3 -I -B research/bit-source-substitution-seed11/enumerate.py
```

Neither command overwrites committed evidence. The generator's optional `--output NEW_FILE` refuses an existing file. Source hashes are checked by the independent command; regenerated data are compared by decoded fields rather than gzip headers.

## Scope, coordination and attribution

Seed 11 was drawn once with OS randomness. It selected the third of three candidate tasks and rotates helper traversal by eleven. [CLAIM.json](CLAIM.json) records the alternatives, stopping rule, overlap and local claim; GitHub had no pinned coordination issue. The search stops after all 430 eligible helpers and all their reads. There are no random restarts or incomplete branches.

PR1043 explicitly left other boundaries unclassified. PR933's relocation/reframing result fixes helper stock, and PR1023's hosting result fixes width-eight residuals. This census changes the question to one-helper direct-source substitution and credits those distinct scopes. It does not combine circuit savings or change the selected frontier.

No new hosted supplier invoice, native multistage replay, selected complex cold replay, runtime speedup, or full-theorem formal proof is claimed. Removing a helper returns rank to its hosting window; the local rank reduction alone is not a supplier gain. PR1043's full hosted invoice is predecessor evidence, not rerun here. All inherited all-size/compiler, common-label/mutable-source realization, hosting, precision/tape and analytic assumptions remain.

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in research, mathematics, implementation, verification and writing. Apache-2.0. Credit Ali Romman for PR1043; DreamingOfClouds for PR589/545/510; eumemic for PR555/543 and the owning checker; Zhihao Chen for the interleaved-interface lineage; Dylan Crow, chafreaky, DaysSky, Jacob Sussman and the retained E8 supplier contributors. The original dependency packages and their notices are unchanged. Separate implementations here do not imply independent human review.
