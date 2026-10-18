# Local evidence

Checked on 2026-10-17 against canonical main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
The 11:06 UTC pre-submission fetch found no guidance or selected-record change.
The refreshed overlap snapshot covered 277 open PRs and 1,915 discussion records,
with complete reported pagination. Relevant hits were PR3154, Discussion3156
and this session's claim, not a second result on this fixture. This was not an
exhaustive closed-PR or code-diff novelty search.

## Environment and commands

- Linux x86_64, WSL2 kernel `6.6.87.2-microsoft-standard-WSL2`, glibc 2.41.
- CPython 3.12.15 and 3.13.5. Standard library only.
- Ruff 0.17.1.

Run from the repository root, with TMPDIR pointing to a session-owned external
directory for temporary test files:

```sh
python3.12 -B -W error research/p112-four-deletion-counterexample/verify.py
python3.12 -B -W error research/p112-four-deletion-counterexample/test_verify.py
python3.12 -O -B -W error research/p112-four-deletion-counterexample/test_verify.py
python3.13 -B -W error research/p112-four-deletion-counterexample/test_verify.py
python3.12 -B scripts/research_package.py --package research/p112-four-deletion-counterexample --check-only
python3.12 -B scripts/research_package.py --package research/p112-four-deletion-counterexample
ruff check --no-cache --select E,F,B,I,UP research/p112-four-deletion-counterexample
ruff format --no-cache --check research/p112-four-deletion-counterexample
```

The canonical proof reports determinant `-2`, five independent directions,
individual deletion sizes `2,4,2,4,4`, next character-support sizes
`13,14,13,14,14`, and minimum common deletions `12`.
The test suite has 19 passing tests, including twelve rejection controls.
Metadata validation and registered replay pass. Both Python versions agree.

The separate arithmetic controls check all 120 root labels by rational matrix
solution, the minor by its 120-term Leibniz expansion, and all character supports
by XOR generation of a binary code. The 36-line residual has exactly one valid
deletion set among all 66,712 subsets of size at most four. That test uses a
separate low-bit-first elimination, not the production rank function.

A Git-free copy with all package files read-only passed the proof and all 19
tests under Python 3.12. Its printed proof bytes equal `RESULT.json` exactly.
Test scratch remained outside that copy. This is an export check, not another
Git checkout or a native backend replay.

## Exact source translation

The optional `--source-data` replay passes for PR3154 head
`708f0ad8928c383de8294aea3c126e9461d2066d` and its
`checks/FINITE/data80.txt`, SHA256
`d23ad440471c3afd1a894b3439e29a05f498edfe2af33d7a667ca1d8f1d6b9c5`.
`SOURCES.json` also records the exact Git blobs and hashes of the source
statements and both predecessor programs. These extra pins are documentary;
the optional checker authenticates the actual data file before translating it.
The default proof does not depend on an unmerged Git object being installed.

Three direct source-binding probes on the literal witness reject:

| Mutation | Observed rejection |
|---|---|
| Replace direction ID 793 by 1249 without changing its vector | `source direction differs` |
| Replace one source deletion index by zero | `source deletion translation differs` |
| Change the source V1 basis without changing the canonical space | `source space translation differs` |

The CLI also rejects wrong source bytes and invalid witness inputs. Source IDs
are provenance, not an assumption in the self-contained geometric proof.

## Search and review limits

The source-bound baseline command `scripts/research_baseline.py` passed and
still identified the complex supplier as binding. No selected cold replay was
needed or run because no supplier or selected artifact changed.

Two initial scratch nominations, one on the first mask representative and one
restricted to 20-line mask pairs, stopped without a completed slice. They prove
no exclusion. A dual-character filter then nominated a rank-five example at
source representative 82 and second-mask index 1839. That scratch filter agreed
with the predecessor's bounded deletion predicate on 10,000 small tests across
budgets zero through four. None of these searches is the acceptance argument.
Only five literal vectors, their spaces, and the exact finite proof are retained.

The p=2 check here is a local control, not an independent repeat of the
predecessor's full p=2 census. C5's complete p=4 maximum remains uncomputed.
The original common-P beta target, other C1-C7 conjectures, full decoder floor,
native operators, hosting and outer multiplication theorem remain outside scope.

A local mathematical review checked the quantifier distinction and the proof
that every rank-lowering deletion contains a nonzero restricted character
support. A separate local code pass checked frame membership, label rotation,
binary dimensions, source pins, bounded reads and failure paths. These were
reviews in this same session, not independent human or model review.

Build the Lever led to the kept deterministic checker. Prove It Works led to
literal source translation, a read-only export and negative controls. Test
Behavior led to arithmetic oracles and corrupted-input cases. Laziness Protocol
kept the change in one new package without editing predecessor or shared code.
The managed-allocation and finite unittest-dispatch deviations are documented
in the README. No new theorem admission or selected-frontier change is implied.

Before publication, run `scripts/check_research_commit.py` on the committed
package. That publication-byte preflight is separate from mathematical checking.
