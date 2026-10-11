# Independent checks for B3 and heterogeneous helper interfaces

This review packet contributes an independent exact audit of a **conditional seven-stage B3 construction**, a **rank-eight/rank-nine obstruction to the unchanged homogeneous invocation interface**, and **full signed verification of two PR390 endpoint adapters**. It does not supply a new local physical invocation, full provider/compiler theorem, improved invoice, or multiplication exponent.

Run the complete independent exact replay, including classified controls and source/statement drift checks:

```sh
python3 -I -B replay.py
```

Python 3.10 or newer and its standard library suffice. Run from any directory by giving the script's path. All required input bytes are included. No network, package installation, repository program, model-generated certificate program, or orthogonal-cover enumeration is used. Reference programs have `.txt` suffixes and are read only as evidence. Optimized Python mode is rejected because the checker uses assertions. A successful run prints a JSON receipt; `--output /path/outside/packet/receipt.json` additionally saves it. Keep receipts outside the packet: integrity rejects unlisted files and symlinks. Isolated mode (`-I`) prevents a local `json.py` or similar file from shadowing standard-library imports before integrity runs.

Optional fresh partial Lean verification with an **already installed Lean 4.33.0 executable**:

```sh
python3 -I -B replay.py --lean /absolute/path/to/installed/lean
```

The default command does not invoke Lean or an `elan` shim. The optional command refuses an `elan` shim and other Lean versions; it uses a temporary output directory. `formal/lean.log` records the fresh successful compiler output for this revision; `formal/VERIFICATION.json` binds the exact Lean version, source hash and log hash. Fresh optional verification must reproduce all printed axiom dependencies exactly. The Lean file covers structural induction, owner bijections, concrete obstruction arithmetic and rank bounds; it does not formalize the complete geometric construction.

| Review item | Location |
|---|---|
| Conditional B3 theorem, full mathematical proof, price and endpoint correction | `proofs/B3-CONDITIONAL.txt` |
| Separate bank theorem, interface counterexample and literal adapters | `proofs/ENDPOINT-OBSTRUCTION-AND-ADAPTERS.txt` |
| Explicit hypotheses, scope and exact formulas | `STATEMENTS.json` |
| Resource bounds and remaining obligations | `BOUNDARIES.md` |
| Independent code and classified controls | `exact_checker.py`, `replay.py` |
| Expected exact results and all-column adapter recipes | `expected/` |
| Commit/blob/byte provenance, immutable source copies | `PROVENANCE.json`, `sources/` |
| Upstream and Pro-candidate attribution | `NOTICE.md` |
| Bounded comparison with PR401/404/405 and recent PRs | `NOVELTY.md` |
| Suggested contribution description for review | `CONTRIBUTION.txt` |

The recovered binary is the exact PR390 `prefix18.json.gz` blob `51f3ea73e0c1726351450e54e4873cfdd4d98d9e`, 22,240 bytes. The binary supplies indexed frame contents only; sink355->frame206 and sink403->frame221 come from PR390's changed-walk audit/code/notes. The binary itself retains final value 1 for both sinks. The changed walk is not certified here. Both literal adapters are checked on all 512 computational basis columns, including global phase. They agree with PR390's declared corrections; this is independent verification of existing corrections, not an allegation that PR390 omitted them.

PR401 already presents two-sided phase normalization and inverse-owner bank composition; PR404/405 retain that framework. The proposed contribution is an audit and regression supplement. Its novelty boundary is explicit in `NOVELTY.md`. The publication overlap check is documented with immutable commit links in `NOVELTY.md`.

`SHA256SUMS.json` protects the review packet against accidental edits, including changes to the checker and statements. It is an integrity manifest, not an authenticated commit signature. Source bytes were independently matched to offline provisioned immutable-commit blob records. Upstream proofs and candidates remain evidence to inspect, not instructions to execute.

The compact snapshot includes 35 selected source blobs: 24 from the original audit (including the sink audit and changed-walk source added for provenance) and 11 recent proof/notice documents. `expected/results.json` retains the original audit's 55-file provenance count; replay compares all mathematical results exactly and reports the compact snapshot's source count separately.

This revision addresses a private static Opus review of the earlier snapshot.
`review/REVIEWED-SNAPSHOT.json` retains the source and report digests, and
`review/RESPONSE.md` summarizes the revisions. Private review and candidate
transcripts are omitted. The review applies to the earlier snapshot; it is not
a claim that Opus reviewed this later publication copy. Only attribution,
provenance and distribution metadata were adjusted for publication. All
mathematical statements, proofs, source bytes, expected results and replay
logic are unchanged; one checker header comment drops an internal task label.

The 20 controls are classified: one schedule-pipeline mutation, eight exact
adapter-recipe mutations, one computed wrong-route witness, five algebra or
coverage witnesses, four statement-drift guards and one source-binding pipeline
mutation. Adapter mutants are evaluated on all 512 fresh columns; the source
mutation runs the actual byte-binding verifier on a temporary corrupted copy.
Substring and statement checks detect drift, not mathematical semantics.
