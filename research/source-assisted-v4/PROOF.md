# Claim, construction and scope

## Claim

Under PR184's retained interfaces, T(n) = O(n (log n)^(1−κ)) with

    κ = 103873/156250000 = 0.0006647872.

The complex saving is b = 219037/312500000 = 0.0007009184, on PR184's 10^-10 selection grid. PR184's effective bit saving 1663073692132636741/(25·10^20) ≈ 0.00066522948 is smaller, so the bit supplier binds. The previous record, PR186, has κ = 0.000661885549259598, and the gain is about 0.438%. The gain over PR191 (κ = 0.0006626307) is about 0.325%.

## What changes

PR184 (icekylinx) built a source-parity local word and a source-assisted frame flow on the PR168 snapshot `fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`. This package keeps PR184's local configuration, arc transport, frame inheritance, flow, exact lift, contract checks, finite bridge, bit supplier and assembly. It changes two inputs. First, it replaces the three frozen query modules with PR168 v4's selected modules, the same modules that `scripts/paired_cube_producer.py` uses:

- `tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json` (triple module),
- `pmod_J0_full_6.0666810e-4.json` (pair module),
- `qmod_climb3u_best.json` (all-but-one module).

It also changes the donor/recipient pairs. PR184 pairs each live gauge (recipient) with an earlier donor role by a plain maximum bipartite matching, and its flow then erases some donors with original-source X controls at cube parity frames. The pairs in `data/physical-pairs.json` come from `source_aligned_local_v4.py --avoid-parity-erasure`. This option takes a minimum-weight full matching of the recipients that avoids pairs the purification could erase. With these pairs the flow erases no donor and reuses no kernel. It finds far fewer dependent outgoing values (8,116 instead of 10,364), so it needs 1,412 fewer dirty births: R = 9,412 and W = 12,052. Any legal pairing is allowed. `paired_cube_physical.physical()` checks the legality of the frozen pairs, and PR184's exact lift and contract checks run on the resulting flow.

The old word that supplies the inherited frames is PR168 v4's own complex word: the producer cache and `references/paired-cube/physical/frames.json`. PR184's code transports the old matching arcs and the old preferred operation frames to the new local word, clips each frame to its exact future cap, and closes the frames forward. It then matches donors to recipients and checks the physical layer with the original `paired_cube_physical.physical()`.

## Checks

`verify.py` runs these steps:

1. The PR168 v4 producer regenerates the signed DAG, the carrier matching and the gauges, and checks them against `certificates/paired-cube-complex-input.json`.
2. `source_aligned_local_v4.py` builds the source-parity local word (all G channels `s`, all A channels `fd`, F = 2), with the frozen physical pairs in `data/physical-pairs.json`. `paired_cube_physical.physical()` checks every value span, alias, chain and target order.
3. PR184's `complex_frame_flow.py` prices the equal-frame flow with source-donor purification enabled and the frozen kernel reuse pairs in `data/kernel-pairs.json` (an empty list for these pairs).
4. PR184's `exact_complex_flow_lift.py` builds exact rational local lifts and inverse gate programs. It verifies the monotone flow and the zero-fresh kernel reuse DAG.
5. `contract_v4.py` runs PR184's contract validation unchanged: all fresh columns equal the identity over the integers, source controls sit at paid parity frames, original V injections precede all controls, controls precede K, centers finish in phase 1, target cap reads occur in phase 2, and target chains nest. It recounts the complete child histogram.
6. PR184's `assemble_profiles.py` certifies the complex and bit moments with rational enclosures, applies the finite bridge, and checks all 47 strict constraints and seven margins.

The bit supplier binds: PR184's effective bit saving is below the complex saving. A stronger bit supplier would raise κ further, up to the complex saving.

## Scope

The validation scope is PR184's. The exact lift and the contract checks establish the local maps and the flow ledger. A globally renumbered scalar transcript of the new complex word is not exported, and no full Clifford/router replay is done. The bit supplier is PR184's, with PR184's stated scope. The analytic, recursion, precision, weighted frame, fixed-tape routing, restored-row and all-size semantic interfaces are retained assumptions, as in PR184. This is a conditional finite witness, not a global optimum.
