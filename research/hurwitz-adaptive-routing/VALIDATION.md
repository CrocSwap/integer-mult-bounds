# Verification and handoff

Executed 2026-10-13 on Linux, CPython **3.12.14**, using only the standard
library. Base and final refreshed main are both
`f567884aeb8851b6e794af1184119a3bfbe1e631`.

## Completed checks

- `python3 -I -B research/hurwitz-adaptive-routing/verify.py`: PASS. The
  committed receipt agrees with the complete exact replay: 240 roots, ten
  rational four-dimensional line spaces, 100 singleton pairings, 45 spanning
  pairs, 32 transversals and all 1,048,576 support pairs. It exhausts all
  65,536 four-variable Boolean routing functions and verifies all 30 attaining
  nonconstant headers. No random subset or early stopping is used.
- `python3 -I -B research/hurwitz-adaptive-routing/independent_census.py`:
  PASS. Six independently generated receiver-conflict graphs, each with
  65,536 candidate fibres, reconstruct the two-source-bit witness family.
  All 1,920 selected receiver inversions pass. The closed-form header families
  have 16 members each, overlap in two and equal the 30 witnessed tables.
  This checks attainability independently; arbitrary-payload exclusion still
  uses the written bound and the producer's exhaustive bound calculation.
- Five protocol rejection controls pass: dropped bit, undeclared source,
  hidden support selection, over-width payload and non-prefix-free header.
  Three graph controls distinguish a demanded-bit collision from a harmless
  change in mate side information. Correct but underpriced/free-header and
  free-termination examples demonstrate the pricing/prefix assumptions.
- Three complete ten-port code checks each cover 1,024 inputs and 10,240
  receiver states: constant-cost-ten adaptive routing, constant-cost-ten
  variable-length routing, and a valid nonpointwise example with mean 187/16.
  The selected four-port nonlinear code adds 64 receiver states.
- `python3 -I -B research/hurwitz-adaptive-routing/test_package.py`: all
  **five tests pass**. A minimal package copied to an unrelated path containing
  spaces replays under isolated optimized Python. Changed reference source
  bytes, an altered coverage receipt, an omitted optimum header and a changed
  decoder witness are rejected. The last two controls use only the independent
  conflict-graph checker. Production guards do not depend on Python assertions.
- A direct `python3 -I -O -B .../verify.py` also passes. Python 3.10+ is the
  code's stated compatibility target; only the version above was executed.
- An archive of staged Git tree `3325c9317e8b109ffadae71286480e1111c4cae5`,
  restricted to this package, passed both isolated optimized checkers after
  extraction under `/tmp` to a path with spaces. Its freshly written receipt
  was byte-identical to the committed candidate, with SHA256
  `61306f6ec8c14d963e659d860dfd65f62795a7c18ca4706684b6496d28144f15`.
  The later validation/claim handoff text does not change any replay input.
- `make selected-record-check`: PASS for the exact selected rational κ and
  source/proof inventory. Existing construction files and `upstream/` are
  unchanged. The retained PR703/PR785 proof SHA256 and Git blob hashes match
  their immutable GitHub source paths.

The complete scoped transcripts are in [evidence/](evidence/). They record
local checks, not hosted CI. Check durations are incidental and not a claimed
performance result.

## Scope of the result

The proof is for the explicit public-header and additive pairing-price model,
with uniform independent demands, zero error and header-determined fixed-width
payloads. The prefix-code proof covers all finite headers and block widths;
finite truth tables do not establish that all-width theorem by extrapolation.
The source/reader geometry and exact census are finite obligations.

The inherited Dfc stage screen grants all other costs zero; its negative
deficit excludes a gain in this format before a physical supplier is built.
There is no κ improvement or unconditional multiplication claim. Private or
localized metadata, interactive relays, cheaper physical implementations and
different stage accounting remain outside scope. All-size realization,
hosting, precision/tape and analytic transfer remain inherited obligations.

The repository-wide `make verify` and selected supplier cold replay were not
run: this change adds only a standalone research package and changes no
generator, supplier, admission check or selected artifact. The package's
affected checks and the selected-record integrity guard were run. No hosted
CI or proof-assistant certification is claimed.

## Coordination and reproducibility

[OVERLAP.json](OVERLAP.json) records the final scan of **695 open PRs through
#904** and relevant exact heads. Both consumed predecessors remain at the
same pinned heads. An immediate pre-submission metadata refresh covered new
arrivals through #907; the latter's abelian metric counterexample was read
and is distinct from this header model. No pinned coordination issue exists; [CLAIM.md](CLAIM.md)
is the local claim and result handoff. No other contributor's PR was modified.

The branch was pushed successfully to the contributor fork. Both CLI GraphQL
and connected GitHub REST PR creation failed with `Resource not accessible by
integration` (REST status 403). A follow-up head-branch query confirmed that
no PR was created. The clean patch and prepared PR text provide the requested
fallback; this is a submission-permission limitation, not a failed replay.

The entry point is read-only by default and can be invoked from any working
directory. Explicit `--write /tmp/hurwitz-adaptive-replay.json` regeneration
produces the same canonical JSON receipt. `SOURCES.json` distinguishes the two
required retained proof files from the base-only contextual file hashes; no
external checkout, optimizer, prior replay directory or network is required.

Prepared for Jerry Chen (@CubeJerry) with substantial OpenAI Codex assistance.
The separate implementation is additional code-level evidence, not independent
human review. Apache-2.0.
