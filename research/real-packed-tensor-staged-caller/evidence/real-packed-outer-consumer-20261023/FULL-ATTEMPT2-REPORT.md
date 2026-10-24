# One completed reduced staged packed caller

The single root-authorized replacement process exited 0 with `PASS_ACTUAL_TWO_TENSOR_STAGED_PACKED_CALLER` in 781.405280 seconds. It used the unchanged published PR5095 scientific source at `e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1`, the published 100402-byte p48 cache, and the frozen packed caller. It did not prepare catalogues, replay the original three-Tensor full caller, change the scientific fixture, or retry automatically. JoyboyBrian's source caller and its authenticated dependency cohort retain their original notices and credit.

The earlier full attempt remains an observed failure at 580.390962 seconds, including its deadline-triggered scratch-lease and marker-erasure cleanup exceptions. Its receipt, log, harness and report remain unchanged at their original paths and in `full-attempt1-frozen/`. This successful normal-return run does not repair or disprove that inherited interruption-cleanup boundary.

## Exact fixture and execution

- Independent radix digit streams: `[255, 0, 3, 17]` and `[1, 254, 0, 9]`; b=8, q=4.
- Source shape (5,7), target shape (8,8), p=48, P=80; all 35 complex records compared at each declared numerical stage.
- `require_recovery=False`. This published reduced cache is diagnostic, and default production entry remained rejected.
- Actual command: clean environment PATH=/usr/bin:/bin and LANG=C.UTF-8; `/usr/bin/timeout -k 10s 900s /usr/bin/python3 -I -B -W error run_full_packed_attempt2_DRAFT.py`. Internal alarm 880 seconds, 30-second heartbeats. Exec session 53886 completed; no numerical process remains.
- Every attempt-2 result/checkpoint/tmp/log/launch path was absent before launch. Log and launch metadata were exclusively created; metadata was fsynced. Child checkpoints use fsynced temporary-file replacement. This promises atomic complete JSON and retention across later process failure, not power-loss durability of the directory entry.

## Observed numerical chain

Exactly two numerical Tensor calls and three numerical Converter calls started and completed. Both forward CRTs compared all actual input and return records; the inverse CRT compared all recovered input and return coefficients. The actual forward and opposite Tensor inputs and all 35 complex return records matched the separate inherited staged oracle. No observed output was overwritten by an oracle value.

| Actual stage | Completion time / record count | SHA256 of actual returned bits |
| --- | --- | --- |
| Forward CRT, first stream | 35 complex records | e8018d05dbcd3a56e294986f321ab5ad3bf394dca054077ce4a3928354d3c8bf |
| Forward CRT, second stream | 35 complex records | 94f9f38c22dbf4b8b02faf2d07b4a6c2366bf32a0ff14d3b46ff281c2d6665e6 |
| Packed forward Tensor | 372.575 seconds, 35 complex records | c8ca6eefe2d864683cdcf5257e1485830b1a3ebaea7ec31733704822efb74b86 |
| Paid J route and fused product | 35 complex records | 8697b1e5d265b236653847496b582ca5138709522dca434bf83b51a5c4b69382 |
| Opposite Tensor | 776.413 seconds, 35 complex records | 35b2040a56c60e04e883349c5f2fd0edc0a8530b798eb9d29268d14ee5a0fc4f |
| Inverse CRT | 35 coefficients | bb5cb6199f244df19a4bd2a36c31d8b733ad3ee0837ed887bee09326ddc0b0e9 |
| Final carry output | 64 zero bits | f5a5fd42d16a20302798ef6ed309979b43003d2320d9f0e8ea9831a92759fb4b |

Raw actual Tensor/CRT arrays, expected arrays and actual fused-product bits are retained in `FULL-PACKED-ATTEMPT2-RESULT.json`. Completed child returns were attached to the receipt before the caller ran and checkpointed synchronously after their equality assertions. The forward has 28 nonzero complex records; the fused product has 35; the opposite result has zero. The observed final diagnostic integer is **0**, equal to the staged reference. The true product is **43113955509404415**, so observed diagnostic minus true product is **-43113955509404415**. This mismatch is explicit; this fixture establishes physical staged conformance, not accurate production multiplication or the production guard premises.

Each completed Tensor reported natural_padding=4, gathers=4, halos=4, expansion_axes=2, compression_axes=2, assembled_axes=2, chirps=1. Each CRT reported global_routes=1, triangular_shifts=2, padding_passes=2 and router batches=1, edges=3, involutions=2, literal=1.

## Ownership and failure scope

The complete normal caller closed with no live scratch leases and one pending return. Borrowed first/second/catalogue values and heads, and borrowed b/q values and heads, matched entry state. Tensor and Converter owners were idle. Moving the output head to its end did not evade the pending-return guard. Paid consume cleared the output and token, and a subsequent default-production entry rejected the reduced cache with empty/closed state.

One separate declared failure cut executed after the normal run: the first Converter dispatch raised before the original numerical child operation, while the parent owned its first ingress bank. It added zero numerical calls and passed parent closure, no pending output, no live parent leases, borrowed/metadata restoration, and resident empty-origin checks. This does not test arbitrary failure inside a numerical child or full interruption cleanup. Preflight also passed the source constructor controls and six dynamic metadata-alias plus five descendant-private-alias controls; these are not exhaustive dynamic coverage of all port coincidences.

## Finite tariff and limits

Observed frozen-caller counters are transforms=2, conversions=3, pointwise_products=1, packed_records=35, J_axis_passes=2, split_records=35, split_exact_adds=140, pointwise_real_products=140. The raw split uses width 51 and final shift 50. The declared J tariff remains 30200 source-loop moves and 7000 writes for two axes, plus clears, resets, metadata, packing, split arithmetic and storage obligations in the source-bound contract. Recovery still has 70 width-86 real products; all source S-squared/scales and three CRT calls remain. The observed catalogue-setup metadata counters were `1^(.002):36`, `51^(.997):18`, `52^(.997):18`.

This demonstrates the finite two-completed-Tensor caller chain on one staged fixture. It is not an all-operation runtime comparison or a complete priced physical saving certificate. No original matched three-Tensor baseline was rerun. The Core's existing doubled real work remains billed. No recursive normalized-rank moment or kappa improvement follows. The four full numerical mutants (wrong opposite sign, inverse R, missing S, double gamma) remain unrun; earlier method-leaf mutation controls retain their narrower scope. No all-size theorem, production recovery admission, compiler/Lean admission, external publication or push occurred.

All 83 public source files, frozen caller and executed harness matched their before/after SHA256 inventories. The candidate remains `5dfcdfe63d9d03a89a00dd92e681ab0a0efc5bbc86aa7edae58f007baf752483`; executed harness remains `c7bb6a705f42469709995f7d8a4c29ab0c12764d744546508a443151ec0345dc`; cache remains `7dd7adbe9e8f6d5ffbecd425a72827b31d7222ee51bcd67a4148ebfd03420381`. Exact receipt and evidence hashes are frozen in `FULL-ATTEMPT2-FREEZE.json`.
