# Validation and limits

Local validation on 2026-10-13, Windows, CPython **3.12.10**. Base commit:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. This is author/AI-produced
computational evidence, not independent human review or formal verification.

## Completed checks

1. `python -X utf8 -I -O -B research/space-capped-dirty-echo/verify.py`
   completed with
   `PASS_SPACE_CAPPED_DIRTY_ECHO calls=160->152 scratch=5 no_new_kappa`.
   The entire recomputed JSON certificate equals EXPECTED.json as canonical
   compact/sorted JSON, converting tuple trees to arrays while distinguishing
   integer, boolean and float values. Its canonical JSON SHA-256 is
   `a37c11b94c0ac897e4dc537b2321daa64d2978f31ac033485326afdaf657919f`.
   See README.md for the finite domains and PROOF.md for the general argument.
2. The same full isolated optimized replay passed from a **new minimal copy
   in a path containing spaces**, containing only this research package and
   the three pinned repository context files. It had no `.git`, surrounding
   research packages, network access or source-tree import paths. Its complete
   expected certificate matched. This tests relocation and dependency closure;
   it is not a second hardware/platform result.
3. `python -X utf8 -I -O -B research/space-capped-dirty-echo/test_contracts.py`
   passed **9/9 tests**. These exercise five actual implementation mutations,
   nonlinear dirt dependence, a target-dependent invalid callback, complete
   precision, source/context corruption, certificate corruption/normalization,
   the primary all-cuts optimum and all 326 circuit/admission controls. The
   earlier eight-test version also passed without optimization before the
   serialization regression test was added.
4. `python -X utf8 -B scripts/verify_selected_result.py` passed:
   `PASS selected record, exact kappa, original source inventory and proof supplement: 51110230636731/31250000000000000`.
5. All **18** source/context files were separately compared byte-for-byte to
   `git show <pinned-commit>:<source-path>`, as well as to their declared hashes.
   Vendored bytes in the Git index also match the pins, including LF line
   endings. The latest inspected PR673 head
   `156f259b99723468cfdd2b5d47d0ba894f09bea7` changes none of the three consumed
   files relative to pinned `bfff94e78f0e75ebd2593e3cc7710ae5290e8be3`.
6. New Python sources parse; local documentation links and staged whitespace
   checks pass. The diff adds only this directory. Existing tracked sources,
   `upstream/`, certificates, generators and the selected pointer are unchanged.

The initial ordinary-Python generation run also completed all mathematical
checks and wrote the exact receipt. After documentation pins and the weighted
symbolic check were added, final verification used the current complete schema.
Only counts of operations are claimed; there is no before/after runtime claim.
After the integer/boolean/float comparison hardening, the ordinary isolated
full replay passed again, and a fresh minimal relocated copy passed both the
full optimized replay and the concurrent comparison. These completed by
2026-10-13 05:09:38 UTC. The main EXPECTED.json receipt is unchanged.

## Failures found and corrected during development

- The first corruption-fixture test could not create a subdirectory in this
  Windows sandbox's default temporary location. The test now creates its
  temporary directory under the caller's writable working directory and
  verifies that containment before automatic cleanup. This was an environment
  failure, not a failed mathematical identity.
- The first comparison-mode full replay completed the mathematics but rejected
  its receipt because in-memory tuple trees were compared directly with JSON
  list trees. `compare_certificate` now normalizes that representation and
  still compares every field. The added test accepts the round trip and rejects
  both a changed tree leaf and a changed call count. Follow-up hardening also
  rejects boolean/float substitutions for integer fields. The corrected
  comparison is covered by explicit regression tests.

## Concurrent-publication comparison

During the immediate publication refresh through #745, PR730 and PR744 had
arrived. This did not change the chosen mechanism: higher arities were already
included in the claimed scope, implemented, and independently verified.
The package now credits both prior publications and makes the distinction
testable instead of claiming novelty for unbalanced/weighted trees.

`python -X utf8 -I -O -B research/space-capped-dirty-echo/compare_concurrent.py`
passes with `PASS_HIGHER_ARITY_COMPARISON`. It executes the pinned PR730
optimizer and literal words, with two additional source files authenticated
by CONCURRENT-SOURCES.json. At (n,S)=(15,5),(15,6),(27,6),(58,8), its minima
are 160,144,464,1728 and ours are 152,128,448,1600. The same actual weighted
radix-16 instance gives 3840 versus 3656 phase reads. This comparison does not
audit PR730's other checks or claims. PR744's larger strict-ternary finite
coverage is credited; its implementation is not consumed.

## Checks deliberately not represented as completed

No repository-wide `make verify`, `frontier626-verify` cold supplier replay,
Linux/remote CI, Lean build or new formal multiplication proof was run. This
isolated addition changes no existing generator or selected construction; its
affected package checks and the selected-record integrity check were run.
The root aggregate would rebuild unrelated historical and supplier packages.

The root certificate's 47 outer inequalities and supplier identities remain
inherited. The new all-size tree statement rests on the written Bellman and
restoration inductions, not extrapolation from the finite tests. The actual
cyclic factors' preparation, precision hypotheses and analytic provenance are
retained with their exact source notices. The minimum is only within the stated
tree class. Physical integration, common-label/mutable-basis realization,
all-size compilation, fixed-tape execution, exact recovery and analytic transfer
are unresolved or inherited; no new kappa is claimed.
