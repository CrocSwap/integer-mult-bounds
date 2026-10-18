# Independent PR540 literal-source audit

**Independent finite verification; no new κ or formal theorem.** The audit
corroborates [cheesegrader's PR540](https://github.com/CrocSwap/integer-mult-bounds/pull/540)
at `acc1917034d10f464271ab115fda314fd4eee7a3`, for the PR442 R747 invocation
at stage 2, replica 0, pair 0, forward. No discrepancy was found within this
scope. The exact base is `dd6403f774a0891093a006ae9716c02e371b1fdb`;
the PR442 source is `4e16d001d505d4f21dd2bcfc44591f9be4c279bd`.

## Result and independence

[EXPECTED.json](EXPECTED.json) binds the complete ordered binary/JSON/Lean word:
19,002 events, comprising 14,693 ADDs, 4,291 MOVEs and nine COPY/ERASE pairs.
A separate sparse-support GF(2) implementation compares all 97 scalar and frame
states: 99,328 scalar rows and 99,328 frame labels, including the clean private
row and all 36 padding rows. All 987 original input columns remain independent;
this checks arbitrary, potentially correlated dirty payloads in normalized
coordinates rather than sampling assignments.

The audit decodes all twelve relocated ownership tables and compares their
logical and padded domains with the literal source routes: 987 roles, 747
helpers on 317 helper families, sixteen 64-axis permutations and their inverses.
The inverse owner table is checked on all 11,520 logical codes and all 4,864
padding entries, including unused-slot sentinels.

[verify.py](verify.py) imports only Python's standard library. It does not
import or execute PR540's parsers, generators, checkers or Lean modules.
It decodes the six-integer source records, consumes the restricted literal
constructor grammar, follows low-bit tree indices and propagates finite sets
of variables. PR540's primary replay uses generated bitmask/tree certificates.
The source semantics were read to specify the independent implementation;
this is code independence, not a blind audit.

PR540 already reports independent word/checkpoint tests and random dirty trials.
This package adds a shipped, reproducible external checker, complete symbolic
column coverage and explicit fault tests. It corroborates those claims rather
than claiming priority. [PR1228](https://github.com/CrocSwap/integer-mult-bounds/pull/1228)
and [PR1231](https://github.com/CrocSwap/integer-mult-bounds/pull/1231) separately
derive the pending ranges; this audit uses PR540's supplied bases 15 and 1.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/pr540-literal-source-audit
```

Expected: `PASS_PR540_LITERAL_SOURCE_AUDIT`, 31 passing tests (one complete
positive fixture and 30 rejection controls), then
`PASS_REGISTERED_RESEARCH_PACKAGE research/pr540-literal-source-audit outcome=completed`.
The registered tests run with assertions disabled. A standalone offline replay,
also supported on Python 3.14, is:

```sh
python3 -I -B research/pr540-literal-source-audit/verify.py
python3 -I -O -B research/pr540-literal-source-audit/test_audit.py
```

Controls include a target-invisible dirty-helper checkpoint fault, an omitted
ADD, a changed operand, dirty temporary overwrite, wrong ERASE center, retained
center write, closed private read, out-of-range tree alias, frame/rank faults,
literal/suffix/parser faults, owner collision, permutation/inverse/mask faults,
unused owner sentinel corruption, wrong invocation and raw/archive corruption.
Semantic controls deliberately bypass immutable input admission to exercise the
mathematical checks; the production entry point always admits the pinned snapshot.

[SOURCE-SNAPSHOT.json](SOURCE-SNAPSHOT.json) lists the original Git paths, blob
IDs, SHA256 digests and byte counts for all 53 files in `PR540-SOURCES.tar.gz`.
Files are checked in memory without extracting or executing them. The original
PR540 NOTICE is retained in the archive and [NOTICE.source.md](NOTICE.source.md).
Local environments and check results are recorded in [VALIDATION.json](VALIDATION.json).
Full Git history is required only for
the registered package's base/catalogue provenance check; the standalone audit
uses its self-contained snapshots. A source pin can be independently checked by
comparing an archive member with `git show acc1917034d10f464271ab115fda314fd4eee7a3:<source_path>`.

## Scope and remaining obligations

This verifies the finite data/execution boundary. It does not run the Lean
kernel, verify theorem elaboration or prove extraction correctness for arbitrary
inputs. The parser recognizes the audited data constructors, not general Lean.
The snapshot manifest records the Git commit-to-file association obtained during
extraction; blob checks alone are not an authenticated Git commit/tree proof.

Frame-label agreement does not establish projector equations or native address
isometries. Original-bank ownership, rational gauge matrices, common-cover
geometry, cross-invocation disjointness, the later pending-swap schedule,
physical costs, uniform compilation and analytic transfer remain outside scope.
Only the parent and hosted **local words** are compared here. There is no native
supplier cold replay, new allocation, selected-record edit or κ claim.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

- Audit original-bank ownership by decoding PR540's `ParentOwnershipData.lean`,
  comparing its 61 slots and 59 coordinate permutations with the same parent
  template. This would cover the other layout; exact matrix isometries remain
  a separate obligation.
- Move the fixed six-integer record decoding and ordered projection into a
  formally checked parser. This could remove part of the external extraction
  boundary; it requires a serialization specification and a proof-assistant build.

## Credit

Prepared by **Sricharan Vagvala (@theon199)** with substantial OpenAI Codex
assistance in research, implementation, testing and documentation. No independent
human mathematical review is claimed. New work is Apache-2.0.

Credit cheesegrader's PR540 formalization, source extraction and review handoff;
Douglas Colkitt's PR1228/PR1231 pending-range follow-ups with Claude assistance;
and the PR442/PR434 construction and hosting lineage, including Dylan Crow,
Jacob Sussman, Zhihao Chen and the earlier contributors named in the preserved
NOTICE. Their mathematical constructions and Lean proofs are not new work here.
