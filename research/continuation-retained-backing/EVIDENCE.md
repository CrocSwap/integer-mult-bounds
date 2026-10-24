# Source, verification and scope record

Canonical main: `1ec1119972c9aefe42525172d07b332fcff81cb4`, task priority
revision 7. The selected record, source manifest and review were resolved:
κ remains .0030217758 under its five inherited framework assumptions;
its reproduction command is `make frontier4610-verify`. No selected data or
shared code is changed, and no selected cold replay was needed or run.

New work is confined to `research/continuation-retained-backing/` on the
isolated `codex/continuation-retained-storage` branch. Pending source bytes are
retained verbatim with original notices. EXPORTS.json records their GitHub
heads/paths and SHA256 hashes; load.py authenticates every export before any
predecessor source is compiled. Runtime loading compiles captured bytes rather
than trusting bytecode caches. No unmerged Git object is needed to execute.

Source exports were obtained from the GitHub contents API with `ref` equal
to the pinned PR head; canonical source exports use `git show BASE:path`.
The proof and bodies of the source PRs were read alongside the code.

## Executed checks

Environment: macOS 26.5.1 arm64, CPython 3.12.8, standard library only.

```sh
python3.12 -B scripts/research_package.py --package research/continuation-retained-backing --check-only
python3.12 -B scripts/research_package.py --package research/continuation-retained-backing
```

Both pass. The manifest executes the full verifier normally and under `-O`,
isolated with warnings treated as errors. The registered pair ran serially
under a 180-second wall guard and sampled 1-GiB descendant-RSS guard (0.5-second
sampling). It completed in 3.739 seconds with sampled peak 88,784 KiB. These
resource observations are not an algorithmic memory bound. RESOURCE.json
retains the exact command and measurement. Each manifest command also has
its own 60-second limit. No Lean, Docker or concurrent heavy replay was run.

RESULT.json records:

* 648 declared small call trees with independently predicted exact per-tape
  capacities, every source write guarded before allocation, full parent bytes,
  heads, prefixes and descriptor checked after return.
* Mixed-role warm histories, sixteen capacity-rotation invocations, erased
  interiors with identical boundary sizes, nesting through depth31, unequal
  sibling/nested descriptors and offsets, empty frames and descriptor copying.
* A shared 128-cell relay with unchanged capacity at depths1,2,8.
* Six actual compact-source calls, two field orders and prefix lengths0,257,4096,
  sixteen occupied parents, complete128-record/1024-bit output, independent
  endpoint permutation, complete physical return state and unchanged24388-action
  return bill. The source-derived per-Role1920-cell local grant is guarded.
* Seven rejecting/probing controls: actual one-cell-short grant, allocating
  blank write versus nonallocating reads/moves, omitted actual-source keys,
  omitted relay, and three malformed peak/head models.

The source compact body theorem and the complete tree/history formula received
separate assisted source/proof reviews with shared context. The latter reviewer
also ran both complete modes. An initially overbroad exact online-prefix
sentence was corrected: a mid-push prefix needs a partial-frame model; final
successful-history grants still bound every interior. There is no independent
human or proof-kernel acceptance claim.

The literal source calibration retains its inherited weak-reference allocator,
logical counters and bulk/control facade. The modeled nineteen tape arrays are
all charged, but that does not compile the facade or prove all-size slot success.
The arbitrary-tree proof is a written induction; finite tests do not substitute
for the production local peak/descriptor/summability obligations.

## Overlap coverage and unrun obligations

At 2026-10-23 22:23 UTC the overlap helper reported complete pagination for
350 open PR bodies and 4,684 Discussion records. Its sparse local search covered
zero of7,267 tracked top-level notes; that absence is not novelty evidence.
The live Discussion5012 continuation handoff, start-here and handoff hub were
read separately. Targeted cached text searches and exact source inspection
distinguish the older coefficient stacks, the alternative continuation encoding,
the literal-interchange history theorem and this physical bank. Arbitrary
diffs and unpublished work remain outside coverage. No public claim post was
made during this donor's local-draft checkpoint.

Primary pending heads:

* [#5356](https://github.com/CrocSwap/integer-mult-bounds/pull/5356):
  `ef1cc26e1e9a08c11cf382de948ee433bebab16d`.
* [#5368](https://github.com/CrocSwap/integer-mult-bounds/pull/5368):
  `a2b809f7e000750bc487ad34d3ffc452080e2058`.

Distinct inspected work includes
[#5286](https://github.com/CrocSwap/integer-mult-bounds/pull/5286),
[#5274](https://github.com/CrocSwap/integer-mult-bounds/pull/5274),
[#5364](https://github.com/CrocSwap/integer-mult-bounds/pull/5364) and
[#5401](https://github.com/CrocSwap/integer-mult-bounds/pull/5401).
The first supplies the prior history-accounting principle; none is imported
as proof of the present tree formula. Pending primitive contracts remain
premises. No full production rectangle, production recursive C, full caller
stock/precision, scientific frontier update or physical allocator is claimed.

Full source-history preflight requires a non-shallow checkout and is unavailable
here. Metadata/source pins, direct base ancestry, committed-byte checks and
portable export checks are separate from that unavailable history check.

Final transport checks passed at scientific-code commit
`668d3bb200587de389ec9ede20fb5c1a630a15fc`: committed-byte verification,
official19-file export and integrity validation, and an isolated optimized
Git-free replay from the export with empty PATH. Every exported file remained
byte-identical after replay. Direct base ancestry passes; the optional full
history command reports `source-history check requires full Git history`.
The final canonical-main fetch still returned the pinned base, and both pending
source heads remained unchanged. Subsequent changes only record these checks.
