# Claim, construction and scope

## Claim

Under the retained interfaces, T(n) = O(n (log n)^(1−κ)) with

    κ = 6679123/10000000000 = 0.0006679123.

The complex saving is b = 219037/312500000 = 0.0007009184, on PR184's 10^-10 selection grid. The bit supplier starts with PR189's face-diagonal bit word and applies the exact endpoint-frame descent below. Its PR189 coarse saving is 167089706787281/250000000000000000; PR184's pricing gives coarse saving `C = 1670897/2500000000` and initial effective saving `a_0 = 6679380665463285737/10^22`. The finite depth-2 leaf wrapper uses `a_(j+1) = (1-C)C + C a_j`, yielding the exact leaf saving in `certificate.json` and κ = 6679123/10000000000. Thus the bit side still binds. This exceeds PR199's 267141/400000000 by exactly 299/5000000000, and exceeds PR194's κ = 1668581/2500000000 by 4799/10000000000.

## What changes

PR184 (icekylinx) built a source-parity local word and a source-assisted frame flow on the PR168 snapshot `fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`. This package keeps PR184's local configuration, arc transport, frame inheritance, flow, exact lift, contract checks, finite bridge, bit supplier and assembly. It changes two inputs. First, it replaces the three frozen query modules with PR168 v4's selected modules, the same modules that `scripts/paired_cube_producer.py` uses:

- `tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json` (triple module),
- `pmod_J0_full_6.0666810e-4.json` (pair module),
- `qmod_climb3u_best.json` (all-but-one module).

It also changes the donor/recipient pairs. PR184 pairs each live gauge (recipient) with an earlier donor role by a plain maximum bipartite matching, and its flow then erases some donors with original-source X controls at cube parity frames. The pairs in `data/physical-pairs.json` come from `source_aligned_local_v4.py --avoid-parity-erasure`. This option takes a minimum-weight full matching of the recipients that avoids pairs the purification could erase. With these pairs the flow erases no donor and reuses no kernel. It finds far fewer dependent outgoing values (8,116 instead of 10,364), so it needs 1,412 fewer dirty births: R = 9,412 and W = 12,052. Any legal pairing is allowed. `paired_cube_physical.physical()` checks the legality of the frozen pairs, and PR184's exact lift and contract checks run on the resulting flow.

The old word that supplies the inherited frames is PR168 v4's own complex word: the producer cache and `references/paired-cube/physical/frames.json`. PR184's code transports the old matching arcs and the old preferred operation frames to the new local word, clips each frame to its exact future cap, and closes the frames forward. It then matches donors to recipients and checks the physical layer with the original `paired_cube_physical.physical()`.

## Bit supplier

PR189 (chafreaky) builds a PR168 v4 bit word whose sums A[2,0] and A[2,1] come from the two face diagonals. It regenerates the carrier matching, the gauges and a physical layer, and it deletes 34 terminal sinks. Its own `verify.py` checks every formal column over F2, the frames, the aliases, the sinks and the paid moment, and it reproduces `research/paired-cube-twin-local-168/certificate.json`. That certificate gives the profile R = 17,554, W = 21,074, rank mass 1,515,392, deficit 1,936 and largest child 60.

The descent freezes 102 nonadjacent operation-frame lowerings from 2,534 structurally eligible endpoint candidates. Candidate costs were evaluated in physical row order, including donor operations, the recipient gauge splice, and recipient operations. Each selected frame is the join of the node's value span and its actual physical predecessor frames, is contained in both physical successor frames, and leaves every terminal-sink write unchanged. The exact assignments, 70 additional basis rows, and per-rank internal histogram delta are committed in `bit/frame-descent.json`. The operation program and its Boolean algebra do not change. `word.exact_frames()` and `word.row()` provide the exact geometry and profile used by the receipt; `bit/prove.py` binds the selected assignments, added basis rows, and exact coarse saving to the committed files.

`assemble.py` reads the descended profile and prices it with PR184's `select()`: the bad-row allowance 10^-16 with fallback 32 m^2 per edge, the coarse saving on the 10^-10 grid, and the least payable atom exponent on the 10^-12 grid. It checks that this coarse value does not exceed the descended supplier's own 10^-18 certificate value. The initial effective saving uses the legacy ordinary leaf 384599/10^10. It then applies the depth-2 finite acyclic ordinary-leaf wrapper from PR185's pinned `research/bit-leaf-bootstrap182/PROOF.md`; this is the same recurrence/assembly pricing pattern first applied to PR189 by PR199 (Maxime Fleury). The verifier checks both exact recurrence steps, the closed form, `a_0 < a_1 < a_2 < C < 1-a_2`, and records the positive atom and row-borrowing tolls. The physical wrapper is inherited from PR185, not newly constructed here. PR184's finite bridge needs only m ≤ 72, W < 10^7 and the uniform bit interface. PR184's `assemble()` then runs the unchanged balanced assembly: 47 strict constraints and seven margins.

## Checks

`verify.py` runs these steps:

1. The PR168 v4 producer regenerates the signed DAG, the carrier matching and the gauges, and checks them against `certificates/paired-cube-complex-input.json`.
2. `source_aligned_local_v4.py` builds the source-parity local word (all G channels `s`, all A channels `fd`, F = 2), with the frozen physical pairs in `data/physical-pairs.json`. `paired_cube_physical.physical()` checks every value span, alias, chain and target order.
3. PR184's `complex_frame_flow.py` prices the equal-frame flow with source-donor purification enabled and the frozen kernel reuse pairs in `data/kernel-pairs.json` (an empty list for these pairs).
4. PR184's `exact_complex_flow_lift.py` builds exact rational local lifts and inverse gate programs. It verifies the monotone flow and the zero-fresh kernel reuse DAG.
5. `contract_v4.py` runs PR184's contract validation unchanged: all fresh columns equal the identity over the integers, source controls sit at paid parity frames, original V injections precede all controls, controls precede K, centers finish in phase 1, target cap reads occur in phase 2, and target chains nest. It recounts the complete child histogram.
6. `assemble.py` checks the complex half of PR184's construction receipts, certifies the complex and bit moments with PR184's rational enclosures, applies PR184's finite bridge, and checks all 47 strict constraints and seven margins. PR189's `verify.py` separately regenerates the bit certificate.

The bootstrapped bit supplier binds: its effective saving is below the complex saving. PR197 still reports a higher κ, 0.000676080316519385, on a different packed PR187 bit supplier; this package does not claim the public record. A stronger bit supplier would raise κ further, up to the complex saving.

## Scope

The validation scope is PR184's. The exact lift and the contract checks establish the local maps and the flow ledger. A globally renumbered scalar transcript of the new complex word is not exported, and no full Clifford/router replay is done. The descended bit supplier retains PR189's word algebra, terminal operations, and stated upstream scope; this change certifies a different physical frame assignment and profile. The analytic, recursion, precision, weighted frame, fixed-tape routing, restored-row and all-size semantic interfaces are retained assumptions, as in PR184. The finite ordinary-leaf interface and nested restoration argument are inherited from PR185. This is a conditional finite witness, not a global optimum.
