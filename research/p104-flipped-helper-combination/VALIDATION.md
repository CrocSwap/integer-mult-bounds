# Verification scope and reproducible evidence

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Source #6917: `07e81202470957555569d0c1077b2d6915e897fe`.
Method source #6916: `ed359c115fa713395da380dcc602761196f5df4a`.
All three were refreshed before final verification and remained unchanged.

| Frozen object | SHA-256 |
|---|---|
| WORD.json.gz bytes | `874a0279d9456816f6bdb72ceb01e8404ab478648bc43504d6ae8e8f438ff80b` |
| Canonical native payload | `ab8f4266d23b8d90f8a34b4da060e3874ba67616810c4875d3afe3eeba9dcb6b` |
| WITNESSES.json | `31645b5e22e6b6dcfc794476a8987bd67f8af9a30a26fa0f5548ccbe78c50a6e` |
| CALLER-COMPRESSED.json | `4e6f78c3312341a089bd514c4fdbbc8d215384888a62666621351721070ce8e5` |
| CUT-AUDIT.json | `138eca67a7983f19e6f7c48a661492e20a8ed984eed175c25457b31e71293737` |

`SOURCE-PINS.json` authenticates all 53 retained files by exact repository,
commit, path, Git blob and SHA-256, with no missing or duplicate inventory
entry. The original word, caller and roots are retained unchanged.

## Registered checks

The six commands in `VERIFY.json` run sequentially on Python 3.12, using only
the standard library and no network. Their declared total timeout is
1,200 seconds. The command is:

```sh
python3 -B scripts/research_package.py --package research/p104-flipped-helper-combination
```

1. **Construction and full budget.** Rebuild all 58 cuts with exact rational
   prefix/suffix checks, separately reverse-check each cut and its COPY guards,
   and compare every intermediate source/output hash and final word. Replay
   every arbitrary public input, all frames, scalar alphabets and owned
   lifetimes. Check both literal/root accounting views, preserve every paid
   operator, regenerate the caller compression and recount both ordinary
   budgets. Coverage: 60 MOVE relocations, 19 later-COPY guards and 2,016,400
   native public coefficients.
2. **Every physical native map.** Check all distinct final-word paid/helper
   chart pairs, exact ranks, signed Pauli action and absolute Gaussian phase.
   Check the 208 first-plane boundary recipes, whose identical-chart second
   copies give 400 main adapter instances. Reject a phase-only corruption.
   There is no inherited-pair shortcut in this registered command.
3. **Original mixed caller.** Reverse-propagate the native endpoint and all
   6,084 formal caller coefficients. The polynomial stage variables are free
   and a no-overflow bound is checked. Reject removal of QUERY, IDLE_ONE and
   LAMBDA separately for A and B, removal of a joint, a wrong B target mask,
   and a wrong native scale. Check all physical caller contacts, idle owners,
   stage order and injective joint/public allocations.
4. **Compressed mixed caller.** Run the same checks on the independently
   regenerated compressed caller. Its type-A transfer separately proves
   60,800 exact scalar equalities across 38 blocks, preserves every joint,
   and retains the full B/J subsequence verbatim.
5. **Price and outer application.** Check both exact roots and wrong-root
   controls, independent root/caller invoices, three rational interval
   implementations, strict derivative, all tail bounds, actual ambient cap,
   logarithm power and first winning integer grid point, all 54 strict and
   four functional outer predicates. Reject overclaim and insufficient BIT.
6. **Assertions-disabled controls.** With Python `-O`, reject a wrong cut
   functional, wrong source hash, wrong retiming owner, a window crossing a
   real contact, swapped port assignments and a missing paid MOVE.

The complete target/paid moments have rank surplus 1,520; the certified raw
crossing interval is `(0.003579065166491, 0.003579065166492)`. Full ordinary
charges are 996,089,112 and 836,590,872, both including every global LAMBDA
translation. The raw height charges are independently recomputed from the
literal event coefficients as documented in `PRECISION.md`; this statement
means a fresh recount, not a second accounting implementation.

## Limits of the evidence

The retained directional core predates this session and imports no producer
scientific code. The reverse native/formal caller and alternating-series
moment checks use different algorithms from the forward replay and retained
interval engines. These are AI-assisted implementation checks, not human
peer review or a proof-kernel certificate. The Gaussian map check is exact;
it does not demonstrate a fixed-tape execution of the enormous compiled
supplier. Physical mixed-port admission, owned ascent/erasure, BIT admission,
precision, stock and the five framework assumptions remain as stated in
`PROOF.md`. No accepted-frontier change is requested.

## Completed execution

All six registered commands passed on 2026-11-09 with Python 3.12.14.
The final marker was
`PASS_REGISTERED_RESEARCH_PACKAGE research/p104-flipped-helper-combination outcome=completed`.
The complete captured output is `VALIDATION-OUTPUT.txt`; `CHECKS.json`
records its hash and the physical-map receipt. Those are outputs, not
substitutes for running the registered commands.

The full physical run checked 2,993 distinct native/helper chart maps,
208 main adapter recipes representing 400 instances, and 2,040 helper
normalizers. Its pair-set digest is
`50c8137616308e912afecde9fb0189777bc2121c78c64d44ed45dd30615e4125`.
Both caller views passed all 7,488 first-plane contact-phase checks and the
separate 22,504-field allocation check. The original caller has 4,519 events;
the compressed caller has 3,221. No scientific input or verifier changed
after the successful gate; only explanatory documentation and this output
record were added before publication.
