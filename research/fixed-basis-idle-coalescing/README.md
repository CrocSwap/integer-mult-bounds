# Fixed common bases cannot improve idle coalescing

This contribution is produced by Nick Petalas. Claim type: scoped written
proof with exact finite corroboration. No new kappa.

For coordinate stage masks over every field, allowing one arbitrary fixed
common basis gives exactly the same feasible idle-degree multisets as the
coordinate basis. Match each basis vector to a distinct coordinate in its
support. Replacing its idle uses by that coordinate preserves every stage
and every degree. The result also covers fixed globally independent
subfamilies. [PROOF.md](PROOF.md) gives the contract and proof.

This settles a subclass of the noncoordinate-direction gap in CubeJerry's
[#7002](https://github.com/CrocSwap/integer-mult-bounds/pull/7002). Its
coordinate-role idle-coalescing obstruction now applies to arbitrary fixed
common bases under the same degree-only tariff. The predecessor's coordinate
optimum and numerical shortfall are cited inputs, not replayed results.

The equality holds for every common function of idle degree, including its
concave rank-power tariff. It does not require concavity. The theorem does
not cover dependent direction families, a basis that changes between stages,
changed masks or idle counts, or a changed native/caller contract. Those are
possible routes beyond the obstruction, rather than proved improvements.

## Evidence and reproduction

From the repository root, use standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fixed-basis-idle-coalescing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/fixed-basis-idle-coalescing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fixed-basis-idle-coalescing
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fixed-basis-idle-coalescing --check-source-history
```

Any CPython 3.12 interpreter may replace that absolute interpreter path.
The direct marker is `PASS_FIXED_BASIS_IDLE_COALESCING`; the runner also
reports `PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier writes nothing.
Each execution emits a generated JSON receipt containing the exact census
counts and SHA256 hashes of all six package files.

The checker enumerates 85,833 square matrices and checks 31,617 bases and
1,251,947 eligible stage/subset pairs. Its domains are F2 in dimensions one
through four and F3 in dimensions one through three. For each basis it compares
an augmenting-path matching with all supported permutations. It then tests
every coordinate mask and every eligible subset of directions. A separate
five-stage noncoordinate fixture checks the complete degree vector. Six
invalid input controls reject, and two boundary controls expose dependence
and the need to match within support. Explicit exceptions keep every check
active under optimized execution. The universal theorem comes from the
written determinant argument, not extrapolation from these finite domains.

## Scope and provenance

Base is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8. The selected record still names conditional #7000. SOURCES.json
pins #7002's README and IDLE-COALESCING.md as historical mathematical context.
They are not executable inputs. The standalone verifier imports no predecessor
code or data and does not repeat a predecessor census or invoice check.
TASK.json declares a changed joint-query-controller scope, a local allocation
obstruction rather than a completed producer/consumer program.

The card's first binding-only command passed. Live open PRs, active
Discussions, recent account contributions, local claims, merged searches and
all-main README searches were checked before the
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19540656).
The cached overlap helper reports incomplete sparse-local coverage; absence
of a search hit is not a novelty certificate. The related open packages below
construct normalized schedules; this theorem concerns all fixed globally
independent families and imports neither schedule nor numerical comparison.

Native implementation, HOST compatibility, paid basis changes, chronological
transport, dirty restoration, ordinary costs, precision/tape, stock, compiler,
supplier admission and the full multiplication theorem remain outside scope.
No numerical frontier, selected files or predecessor files are changed. The
selected cold replay, Lean, Docker, independent human review and formal proof
kernel are unrun. The application to #7002 uses its published coordinate
obstruction as a premise without independently validating that result.

## Related open work

- Rohan Arun's [#7098](https://github.com/CrocSwap/integer-mult-bounds/pull/7098)
  constructs and prices a noncoordinate projector relocation for #7002.
  This proof gives a fixed globally independent family obstruction, without
  recomputing that schedule or its price.
- Rohan Arun's [#7106](https://github.com/CrocSwap/integer-mult-bounds/pull/7106)
  extends the normalized projector scheduling work. Its construction enforces
  compatibility on overlapping intervals. This theorem requires global
  independence across the whole schedule, a stricter premise. No numerical
  agreement or disagreement is claimed.

## Open next questions

- Can a globally dependent family of directions lower a fully specified idle
  bill while each stage still has independent idle directions? Start with
  three lines in a two-dimensional coordinate space and a short mask sequence.
  A favorable allocation and the actual paid preparation/restoration are
  missing. The matching theorem does not decide this case.
- Can changing the basis between stages improve a complete connected-root
  caller after paying conversion and HOST compatibility costs? Start with
  two explicit bases and one transition. No legal conversion or favorable
  complete bill is supplied here.

Structured relevance, first steps and blockers appear in TASK.json.

## Credit and engineering

Credit CubeJerry, Jerry Chen, #7002 for the connected-root question and
coordinate coalescing relaxation; DreamingOfClouds #6937 for the connected
mask lineage, and the retained #6936/#6912 native/root authors. The support
matching fact is classical determinant expansion or Hall matching. The new
step is its stage-set-preserving application, not the predecessor optimum.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

The investigation playbook guided the work. Build the Lever supplied a
standalone checker; Prove It Works required all eligible stage subsets and
the chronological degree fixture. Power of Ten bounds dimensions by four,
fields by three, matching paths by dimension, and census domains explicitly.
All functions have fewer than sixty lines and there is no recursion, dynamic
code execution, subprocess, network or shared mutable state. Python allocation
is a managed-runtime deviation: matrices have at most sixteen entries,
permutation lists at most twenty-four entries and vector tables at most
eighty-one entries under the enforced entry-point caps. Runtime allocator
internals are not inspected. Receipt files are limited to 128 KiB each.
Warning-strict normal and optimized commands are registered diagnostics.
Ruff and mypy were unavailable on PATH. No repository-wide diagnostic policy
was changed for this isolated package.
