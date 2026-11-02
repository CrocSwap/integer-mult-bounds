# Unit13 initial checker review

Frozen at 2026-11-02T18:03:56.149959+00:00. **Initial P3 checker rejected by static inspection; no tests or imports executed.**

**C01 — BLOCKER.** `implementation/at_random_producer_v1.py`, lines 32,33,229,236,245.

need() requires condition is True. positions() always returns a list, but three source-analysis callsites pass that list directly; even nonempty lists are not the singleton True. Every valid production source bundle reaches a SemanticError at the first allocation-pattern gate. make_witness/check_witness cannot succeed. Use explicit bool or length predicates at the three callsites. Preserve strict need semantics; do not weaken general truthiness validation.

**C02 — EARLY_RESOURCE_BOUND_CORRECTION_RECOMMENDED.** `implementation/at_random_producer_v1.py`, lines 80,87.

source_map scans keys and allocates set(bundle) before checking source-role cardinality; an oversized exact dict causes work/additional allocation outside the fixed24-role packet before it is rejected. Source payload byte caps do not bound this prior top-level metadata/set allocation. Immediately after exact-dict validation, require len(bundle)==len(SOURCE_PINS), before key scan/set/value iteration.

## Other static findings

- Exact source-key types precede set/equality; payload values are exact bounded bytes before hashing. Plain witness validation rejects nonexact containers/keys/integers before profile comparisons.
- Duplicate JSON keys/noninteger values are rejected, canonical bytes are checked, raw/nodes/depth/container/int bounds are explicit.
- Two K phases, seed/U residual stages and later failure/return distinctions agree with accepted conditional argument; computed_destination models unsigned modulo64 only.
- Semantic analysis is separate from literal source authentication; production APIs require all24 pins. Semantic layer is a source-specific argument projection, not a generic C/preprocessor or native runtime proof.
- Package reader uses only fixed input-NNN.data filenames beneath retained directory FDs, bounded reads, regular/single-link/size/drift checks and source pins. It retains raw chunks and first delivered error; imports only the new core. It is not current C07/ancestor ownership, original handler/native failure totality or physical-cost qualification.

Parent controls the sole formal repair. Preserve initial proof/pins/core/reader/witness/receipt and static failures. After repair independently review exact delta and actual new-only controls/results; no initial tests/imports were run and no failure log may be invented.

P1/P2 conditional argument remains accepted; P3/P4 remain open. All original flags/credit/bounds stay unchanged, costs OPEN_NOT_ZERO.

## Same-read snapshots

- `core`: `outputs/c05-v03-completion-20261102T055710Z/unit13/review/snapshots/at_random_producer_v1.py.35bc50f6f66b29acb3ce3fd36a1dbf750dfd80914b7da3cc44f5ad3d50dc323b.txt`; 19989B; SHA256 `35bc50f6f66b29acb3ce3fd36a1dbf750dfd80914b7da3cc44f5ad3d50dc323b`.
- `reader`: `outputs/c05-v03-completion-20261102T055710Z/unit13/review/snapshots/package_reader_v1.py.63c67d9060cd7eae9e8fb95ebdd799e947a911fd3baf200127a5be673c26a2a5.txt`; 4826B; SHA256 `63c67d9060cd7eae9e8fb95ebdd799e947a911fd3baf200127a5be673c26a2a5`.
- `authored_witness`: `outputs/c05-v03-completion-20261102T055710Z/unit13/review/snapshots/WITNESS-v1.json.3bc1e7dd7d6cf17e5dd11129defe1baa05c73c90e617a0b7205af7df114e6f70.txt`; 2617B; SHA256 `3bc1e7dd7d6cf17e5dd11129defe1baa05c73c90e617a0b7205af7df114e6f70`.
- `initial_receipt`: `outputs/c05-v03-completion-20261102T055710Z/unit13/review/snapshots/AUTHOR-INITIAL-FREEZE-v1.json.14e9f327c75b3fc01e76af2786e3882634a57012134185458aecf023c556e6fa.txt`; 2317B; SHA256 `14e9f327c75b3fc01e76af2786e3882634a57012134185458aecf023c556e6fa`.
