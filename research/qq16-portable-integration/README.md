# Portable replay of the complete QQ16 protected-return fixture

**Verifier engineering; no new saving, supplier admission or kappa.** This
package makes JoyboyBrian's PR4790 six-case integration replay executable on
native Windows with one source-bound, in-memory path-rendering correction.
The full original result is compared, including JSON scalar types. Frozen files,
archives, original inventory/hash checks and mathematical guards are retained.

The failure was already reported by Mainzu in
[`selected-stock-rho-ledger`](../selected-stock-rho-ledger/README.md) for PR3385,
and blocked the complete integration attempt in
[PR4949](https://github.com/CrocSwap/integer-mult-bounds/pull/4949). Mainzu's local
shim was not a registered reusable replay. This contribution supplies a narrowly
bound adapter, fault controls and the complete PR4790 replay; it does not claim
the path issue, return optimization or earlier ownership audit as new discoveries.
It answers [the explicit handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19137316).

## Exact failure and correction

On Windows / CPython 3.12.0, the unchanged command

```sh
python -I -B research/qq16-protected-return-caller/verify.py --case fixed
```

fails before the first return at retained PR2753 `verify.py:75`:
`ValueError: no omitted or extra predecessor files`. Its inventory renders
relative paths with the host's separator, whereas `FROZEN_FILES` uses `/`.
The complete 50-file inventory includes nested names such as
`vendor/controller.py`, rendered as `vendor\controller.py` on Windows.

The adapter changes exactly this expression in executable memory:

```diff
-str(path.relative_to(here/'predecessor'))
+path.relative_to(here/'predecessor').as_posix()
```

It requires the complete original module SHA256
`65126e788eeea10e830fc583cf4afe0bfc4d67495cbf8ac21de3507dbe624d56`,
exactly one matching expression, and the complete transformed-module SHA256
`d3685f34f88b1e2f5f8aaf5fe55bdbaf7f4bb004af8bcf321a2e9e4cb4e74ec9`.
No path is dropped, renamed in the manifest, case-folded or stripped. On POSIX,
the replacement gives the same names for this exact inventory. Controls check
both path flavours against every retained name.

The actual source chain is PR3087 `inputs/pr3055.tar` ->
`inputs/pr2899.tar` -> `inputs/pr2809.tar` -> `inputs/pr2753/verify.py`.
The source hashes for each archive boundary are checked in `verify.py`.
The original PR2809 loader's two allowed complete historical selected records
remain the only accepted records. Its compatibility controls still reject
changed kappa and proof supplements. The original PR4790 temporary projection
supplies its exact historical selected record; the repository's current selected
record is unchanged.

## Coverage and evidence

The new launcher authenticates **143 live files**: all 136 original inputs and
all seven files of the retained PR4790 package. `SOURCES.json` binds their Git
blobs and SHA256 values at main `cef4b52f2a59009865bf8eabde1be3f159063703`.
PR4790's published head is `38dd6b59d50d346bb34fea02a4ee1ac8d282ebbf`.
The retained package's own authentication also runs.

A temporary compiler hook recognizes only the exact PR2753 source image and
must fire exactly once per worker. It is removed in `finally`. The original
PR4790 aggregator is executed unchanged; a module-local subprocess facade
redirects only its six recognized worker commands to this launcher, preserving
order, `-I`, `-B`, optimization mode, fresh bytecode-cache namespaces and each
90-second timeout. Its original adapter, fixture, numerical execution, metering,
source census checks and every comparison remain executable predecessor code.

| Original case | Reproduced boundary |
|---|---|
| `fixed`, `adopt` | Two nonconstant generations, 24 actual child calls per arm, equal complete endpoints and exact final inventories; 8,046 record Tapes per arm |
| `stale-engines` | Original disjointness guard rejects after four completed returns |
| `stale-external` | Original external-inventory guard rejects before any completed return |
| `output-alias` | Original exclusive-inventory guard rejects after four completed returns |
| `service-stop` | Deliberate stop after the fifth return; actual controlled disposal checked before fixture cleanup |

Each successful generation retains the original order: four producer calls,
six service calls, then two later producer calls. Packets contain 512 bits in
this reduced fixture. The inherited whole-fixture difference is exactly
`(reads, writes, moves) = (61488, 24576, 49200)`. This reproduces PR4790's result;
it is not an additional optimization.

The canonical **complete original receipt**, rather than selected output fields,
has SHA256 `1c9579c7e34614030922e51697b511db7bea0a3e4c3a652a54bed162e3e19a67`.
The launcher compares it with retained `RESULT.json` after each full replay.

Twelve new failure controls exercise actual source/receipt boundaries: missing,
extra and changed predecessor files; changed Git blob; omitted predecessor
manifest entry, live source and CI input; altered adapter source; boolean to
integer and integer to float substitutions in the full original receipt;
omitted service cleanup; and changed saving. The positive authenticator checks
50 frozen files, four proof files and eleven live inputs before and after these
faults. The retained PR2809 selected-record controls run separately. On Windows,
the control also requires the original unadapted authenticator to reject at the
reported inventory boundary; on POSIX it requires both authenticators to agree.

## Reproduce

Python 3.12 standard library; no solver, Git subprocess or network is needed by
the direct verifier. From the repository root:

```sh
python -B scripts/research_package.py --package research/qq16-portable-integration
python -I -W error -B research/qq16-portable-integration/verify.py --json
python -I -W error -O -B research/qq16-portable-integration/verify.py --json
```

Expected marker: `PASS_QQ16_PORTABLE_INTEGRATION`. The registered hook executes
both modes, each with a 300-second bound. The direct `--controls-only` option
checks the source/receipt boundary without running the integrated cases.

Local verification on October 23, 2026:

- Metadata/source-pin validation and both registered commands pass on Windows /
  CPython 3.12.0 (119.465 seconds for the complete registered pair).
- Both adapted direct modes pass on Ubuntu under WSL2 / CPython 3.12.3
  (75.192 and 74.863 seconds). The unchanged original full PR4790 replay also
  passes there. Timings describe this host, not a speedup or performance promise.
- All three captured platform/mode JSON reports compare equal; the registered
  Windows commands compare the same complete original receipt.
- All 143 live input SHA256 values are unchanged after verification.
- The selected orientation helper returns `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`;
  this checks source bindings, not the selected mathematical cold replay.

The official exporter can snapshot the committed package and its declared
inputs. After integrity checking and extraction, the same direct commands run
without Git. There is no write/regeneration mode and no expected receipt is
updated by verification. Archive checks, publication-byte validation and hosted
CI status are reported in the linked PR.

This is a shallow checkout, so the optional full-history publication-ancestry
preflight was not run. Every declared pin resolves at the exact starting main
commit; no unmerged foreign Git object is required.

## Scope, coordination and credit

This is a reproducibility extension using the original mathematical checker,
not a second independent implementation or human/formal proof audit. The six
cases use reduced geometry. Production O73 execution, a new complete root
census, full native/all-size admission, stock/precision/compiler proofs and the
complete D* versus B* cost are not supplied. Finite rebinding control remains an
unknown signed charge. The inherited source census and whole-root saving
formula remain credited source evidence. No selected cold replay was run.

Handoff-first assignment, `portable-replay`, priority revision 7. The original
card and refinement are in `TASK.json`.
[Canonical claim and findings](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19137557).
Initial remote overlap covered 315 open PRs and 4,035 Discussion records with
complete pagination (03:44–03:45 UTC, October 23, 2026). Subsequent local search
covered all 6,601 tracked top-level notes and found the credited Mainzu precedent.
Canonical main was refreshed to `3fd7d441b898563fedb7dc45e5f926d937d4dfc8`;
none of the 143 inputs or governing guidance changed. The scientific source
pins remain at the starting main commit.
Arbitrary closed diffs, nested notes and unpublished work are outside that scan.

Credit JoyboyBrian for PR4790's installed composition and full receipt; Chris R /
Clear1nsight for PR4166/4167/4172/4177's caller, transaction, tariff and cost
lineage; DavidAriasC for PR2753's authenticator; Mainzu for the earlier Windows
observation; Tekalign for role exchange; Jose Manuel for physical machinery;
and all QQ16/native predecessors named in the retained package and archives.
The PR4949 handoff and finite ownership audit retain Mihir Srivastava's credit.
New adapter, controls and replay by Mihir Srivastava with substantial OpenAI
Codex assistance. No subagents or independent human review. Apache-2.0.

## Open next questions

- Price the complete D* versus B* comparison at the actual nonterminal C8 band.
  Start from PR4790 and current #4744 handoffs, with an explicit finite-control
  tariff and every unmatched native term. The reproduced return saving alone
  cannot decide that comparison.
- Other callers of the same frozen authenticator need their own source closure
  and full-receipt comparison. Mainzu's PR3385 replay note is one concrete
  starting point. This package does not install a repository-wide patch; check
  live overlap before extending it. These questions are structured in TASK.json.
