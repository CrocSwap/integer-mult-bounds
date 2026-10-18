# Independent integration derivation review

Status: PASS for the frozen source/admission derivation; complete runtime admission remains a separate result. No integration blocker was found in the reviewed wrapper and cache/source bindings.

`check_integration_derivation.py` is portable and does not execute candidate, builder, wrapper or admission code. The fixture directories preserve the exact predecessor and successor admission scripts, the two source manifests, both versions of the two altered validator scripts, the builder receipt, and the frozen integration scripts. The bundle is about328KB; the two full manifests account for133KB. It now also includes the original and exactly derived runtime geometry-control script. No immutable source or executing wrapper was edited by this review.

## What was established

- The predecessor admission script is pinned at SHA256 `b926725ea029c71979e48e785578aa4821ea7ea73c8e9139c4e2c71fa6bfc91b`. The new admission AST differs only by the exact `shared-four` source record, exact PR2848 comparison record, the corresponding two CLI defaults, and one precisely specified runtime patch call for the geometry mutation tests described below. All remaining executable AST nodes, guards, function bodies and the docstring match. The new script is pinned by the executing wrapper at `c36c482e5df550daf1e0f0da8ed71eb00e12ac41df8de973583f4db9d98f586f`.
- The original541-file manifest and new547-file manifest are authenticated. There are exactly five modified paths and six added paths, with no deletions. The other536 original file hashes are unchanged. A separate executed whole-tree check rehashed all541 original and547 derived files, rejected symlinks, and rejected both bytecode files and empty cache directories.
- `new/rebuild_borrow.py` has exactly the declared additive stage before the retained final-word check. It authenticates the preceding word's canonical hash, invokes the pinned pure generator, checks the result hash and ledger, checks the changed-field set and derived cleanup, and appends the new state to the existing audit chain. All previous source bytes are retained. Because the complete source manifest binds the added stage-input files, the optional file-presence branch cannot omit this stage in an authenticated overlay.
- `verify.py` retains every original byte and adds exactly one independent-review call immediately after the original word-rebuild call. The inverse replacement recovers the original file byte-for-byte.
- The two archived original words match their original compressed hashes. The derived words, generator and review identities are bound through the manifest and derivation receipt. Manual provider inspection confirmed both profiles and all408 ordered widths: only positions236,238,254,256 shrink9→8, corresponding to helper IDs460,462,478,480. Provider record keys are unchanged.

## Wrapper and cache review

The executing `reproduce.py` is frozen at SHA256 `7fc4cd1277f42ba0a25a1eae72c6290878fefd5bab7053f4e548c15d95d914c5`. It accepts explicit paths, resolves them, requires fresh work outside both source and replay package, authenticates source and script/input hashes before work, runs every stage with bytecode disabled and assertions enabled, and rechecks bound inputs after each stage. At completion it checks exact headline equality, package/release hash chaining, original and overlay source immutability, and accurate fresh/reused-native provenance.

The primary admission comparator remains the immutable PR2848 claim. The PR2853 check is an additional exact rational comparison in the wrapper, with its separate claim hash and exact head recorded; it does not replace or relax the primary admission guards. Both before and after release, the expected/actual headline must beat the pinned PR2853 rational headline.

`prepare_shared_native.py` binds the complete derived source, refuses source caches, and checks the full retained-cache file map against the pinned PR2848 receipt. It verifies the retained parent source/claim/receipt and all16 retained parent stages, then copies only the authenticated retained proofs. Both changed providers run fresh five-stage native chains. Their complete literal word,408-helper/72-buffer ABI,632 all-column checks and paid profile are checked. The new receipt explicitly reports two fresh current chains, two reused retained chains and one reused retained parent; it does not claim all evidence is fresh. Original source and old cache are rehashed after preparation.

The builder and wrapper require no absolute scratch path. The minimal fixture checker can be run with Python isolated/optimized flags; it uses explicit exceptions instead of assertions for its own checks.

## Verification and failure controls

The checker passed11 named groups of checks and rejected20 mutations/invalid inputs, covering an altered stage-success predicate, wrong source manifest, wrong comparison field, a numeric-type change, wrong default, weakened final source guard, altered predecessor, unlisted source path, altered inherited validator, missing appended kernel stage, altered derivation receipt, weakened retained-cache predicate, weakened secondary comparison, empty source cache directory, bytecode file and symlink. Four additional controls reject a zero decrement, a geometry-control waiver, a weakened assembly predicate, and removal of the non-vacuity check. The same20 controls passed under `python -I -O -B`.

The four source/native wrapper files are authenticated by exact bytes; pinning them does not itself prove their runtime outcome. The runtime review above is a source inspection. The minimal fixture proof authenticates the full manifest maps but cannot rehash omitted payload files. `DERIVATION-REVIEW.json` separately records the actual whole-tree rehash; `DERIVATION-REVIEW-OPTIMIZED.json` records a portable minimal-fixture run without claiming those payload reads.

## Preserved first-run failure and exact runtime correction

The first full run passed source derivation and fresh native replay, then failed during complete admission because `old_call_count` assigned333 to both sweep counts. The actual T37 invoice already had333 invocation sweeps and333 bridge sweeps, so that particular mutation was a no-op. `FAILED-V1.json` preserves the actual invoice hash, counts, stage-log hash and executed v1 script hashes. Original v1 fixtures and receipts remain in the parent review directory. This failure was not waived or recategorized as a successful release.

The corrected adapter adds one exact runtime `patch('geometry_controls.py', ...)` call, placed between its existing rebind and verify-release patches. It makes exactly two replacements: decrement each actual sweep count by1, and require `(o,i)!=(owner,invoice)` immediately after invoking every mutation and **before** updating the owner hash or calling assembly. Thus at this invoice the undercharge is333→332 for both counts. All six mutation names, the original assembly calls, their exception requirements and the failure-on-acceptance branch remain byte-for-byte unchanged.

The checker authenticates the original geometry script against both unchanged source manifests, applies only those two literal replacements, and compares every byte of the derived runtime script. It checks both `-=` AST nodes and the complete six-control list. It removes only this exact, location-bound patch call before comparing the admission AST with its predecessor, so a change to the existing assembly predicates is still rejected. The geometry source file inside the547-file overlay is unchanged; this is a declared derived-package runtime patch. `T37-GEOMETRY-PREFLIGHT.json` records that all six corrected mutations were rejected against the first run's strict assembly. The corrected full replay starts in a fresh directory and its final release outcome remains separate from this source review.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B check_integration_derivation.py \
  --old fixtures/old --new fixtures/new --derivation fixtures/derivation \
  --out DERIVATION-REVIEW.json --controls
```

For an actual payload rehash also pass `--full-old-source ORIGINAL_PR2833_DIRECTORY --full-new-source DERIVED_OVERLAY_DIRECTORY`. This review does not replace fresh native phase/Gaussian replay, owner/controller/geometry checks, exact outer checks, or the final strict release receipt.

`PRODUCTION-EQUIVALENCE.json` additionally records that the current production generator `b3241527...` reconstructed both frozen candidate decoded words without mutating its inputs. The earlier prototype hash `90aa848c...` is historical, not the production generator's identity. The local algebra proof has been relabeled accordingly.
