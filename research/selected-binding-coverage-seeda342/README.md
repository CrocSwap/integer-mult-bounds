# Selected binding coverage: which check pins each consumed source?

**Scoped adversarial audit of one acceptance obligation; no new kappa.** The
selected record carries a `source_manifest` whose inventory check ("Selected
package inventory or bytes changed") is what binds the audited supplier
sources. This package traces that obligation to its actual source-bound checks:
for every repository input consumed by the selected fast acceptance
(`scripts/verify_selected_result.py`) and by the documented reproduce driver
(`scripts/verify_frontier1094.py`, including its `--baseline1042` reuse mode and
the frozen `research/complex-t16-rare-pattern-exchanges` chain), it names the
check that pins the bytes, and it exercises the real `check()` acceptance
function on fixtures that are semantically invalid but superficially
well-formed.

Prepared by **Aaron Wang**, with help from opencode. Apache-2.0. Substantial AI
assistance is disclosed in [TASK.json](TASK.json); this is not independent human
review.

## Reproduce

From the repository root, standard library only (Python 3.10+; the registered
replay uses 3.12):

```sh
python3 -B research/selected-binding-coverage-seeda342/verify.py
```

Expected final line:

```text
PASS_SELECTED_BINDING_COVERAGE_AUDIT unbound=4 fixtures=7
```

## Result

Of the 20 consumed repository inputs:

| Binding class | Count | Examples |
| --- | ---: | --- |
| manifest-roots inventory (1,579 pinned files over 13 package roots) | 8 | the whole frozen complex chain, including `upstream1087.tar.gz` |
| record `proof_supplements` digests | 5 | `verify_frontier1094.py`, `verify_frontier1042.py`, `verify_replay_coverage.py`, `check_frontier1094.py`, the batch1099 review |
| record `certificate_sha256` | 1 | `ASSEMBLY.json` |
| checkpoint self-binding (its own record re-enters `check()`) | 1 | `certificates/checkpoints/frontier1042.json` |
| record root of trust | 1 | `certificates/selected-result.json` |
| **NONE** | 4 | see below |

The four unbound consumed inputs:

1. `research/community-frontier1094-audit/SELECTED-SOURCE.json` — the inventory
   anchor itself. `check()` binds all 1,579 inventory files to the manifest's
   digest list, but the record has no `source_manifest_sha256`, so the manifest's
   own bytes are read unverified. Fixture 7 shows the consequence: a
   semantically invalid but superficially well-formed forgery that changes an
   inventory file **and** the manifest digest list consistently passes the
   acceptance unchanged.
2. `scripts/verify_selected_result.py` — the acceptance checker's own bytes are
   pinned by no record-level check (root-of-trust observation).
3. `research/community-frontier1042-audit/RESULT.json` — the published baseline
   receipt that `verify_frontier1094.py --baseline1042` compares its supplied
   work directory against. The comparison target is unbound at record level; the
   receipt's *claims* are still constrained downstream (the driver checks its
   stage list, kappa constant and recorded script hashes against the live
   repository scripts), but the anchor bytes are trusted.
4. `docs/research/community-batch1099-integration.json` — an existence-only
   publication pointer by documented design ("Other publication pointers retain
   their existence check").

## Fixtures (through the real `check()` of `scripts/verify_selected_result.py`)

| Fixture | Outcome | Exact error / note |
| --- | --- | --- |
| healthy synthetic record | accepted | — |
| mutate one manifest-inventory file | rejected | `Selected package inventory or bytes changed` |
| mutate one proof-supplement file | rejected | `Selected proof supplement changed: ...` |
| proof with no covering digest | rejected | `Selected primary proof is not covered by a verified digest` |
| wrong `decimal` | rejected | `Selected decimal differs from exact kappa` |
| mutate existence-only pointer | **accepted** | documented boundary |
| mutate unbound sidecar | **accepted** | no check covers it |
| consistent manifest-anchor forgery | **accepted** | the pin mechanism cannot bind its own anchor |

So the obligation "the audited sources are the consumed sources" does follow
from source-bound checks for the entire frozen supplier payload (all 1,579
manifest files, both upstream archives via package MANIFEST self-pins, and the
five pinned harness scripts), and does not follow for the four items above. No
selected certificate, supplier, or frontier value is affected; this changes no
kappa.

## Scope, method and controls

- Exact base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
  Pins: [SOURCES.json](SOURCES.json); task card: [TASK.json](TASK.json).
- The consumed set is enumerated from the pinned scripts' literal path reads and
  subprocess calls. A control regex-scans both pinned scripts for path literals
  resolving to repository files and requires every one to sit inside the
  enumeration or the record's `proof_supplements`; the receipt records the
  (empty) remainder.
- Fixtures run the imported production `check()` in a temporary directory; the
  working tree is read-only. The receipt is deterministic and compared to
  [EXPECTED.json](EXPECTED.json).
- Not checked: the mathematical content of any supplier obligation, the full
  cold replay (`make frontier1094-verify`, whose make target could not run on
  this host; make is not installed), CI, and any proposed record change. The
  enumeration covers the fast acceptance and the documented reproduce driver;
  deeper frozen-chain internals are classified by their package pins, not
  line-audited.

## Nearest prior work and what this adds

`research/selected-source-coverage-audit` (seed 97 consolidation note) maps
*review* coverage of the selected record's `source_prs` list against the PR
ledger; it asks whether dispositions exist. This package asks a different
question: which check pins the *bytes* of each consumed input, with fixtures
against the live acceptance function. `research/frontier1094-ancestry-binding-seed69`
(Sagar Thakrar) reproduces the PR799/PR741 ancestry binding of the reuse path
through `check_selected`; that binding is counted here as `checkpoint-self-binding`
and not re-audited. `research/retained-bit-supplier-binding` guards the bit
supplier identity across committed assemblies; this package does not touch that
identity. Credit to the `research/owner-boundary-audit` line (Tekalign) for the
"trace one obligation, then try to break it with one fixture" method.

## Open next questions

- **Should the selected record pin the bytes of its source manifest?**
  Why it matters: the inventory anchor is currently trusted, and fixture 7
  shows a consistent forgery passes. First step: add `source_manifest_sha256`
  to `certificates/selected-result.json` and one `require()` in
  `scripts/verify_selected_result.py`. Blocked by: maintainer authorization to
  change the selected record and its acceptance script.
- **Should the `--baseline1042` comparison target and the acceptance checker
  itself be record-pinned?** Why it matters: both are unbound anchors of the
  documented acceptance. First step: add the two digests to `proof_supplements`
  and re-run this trace. Blocked by: maintainer authorization, and a decision
  on whether a checker should pin itself inside the record it verifies.
