κ = 7.92580093369946e-4

# w3 cube layer on PR #325's p10b bit word, with a stronger p = 10 complex supplier

A conditional finite construction with **κ = 396290046684973/(5·10¹⁷) ≈ 7.92580093369946 × 10⁻⁴**, +3.71 % over
PR #315 (7.64230861320245e-4) and +1.97 % over the best open PR at packaging time (#332/#333, 7.77268259042372e-4).
The complex supplier binds; the bit root lies 1.07 % above its leaf cap.

| side | supplier | coarse saving |
| --- | --- | ---: |
| bit | PR #325's p10b word + w3 Design T + twin condensation | c = 32069035133443/(4·10¹⁶) ≈ 8.01725878336075·10⁻⁴ |
| complex | p = 10 gcert/1 program: PR #304's recipe on PR #325's pair module, PR #327's triple module and PR #315's all-but-one module | b = 396604388013523/(5·10¹⁷) ≈ 7.93208776027046·10⁻⁴ |

## Bit word

The base is PR #325's p10b local word (h = 20, v = 960, m = 100, R = 8,100), exported unchanged from PR #325's own
`prepare`, `physical527` and parity fusion into the PR249 snapshot format (`code/export_p10.py`). On that snapshot
w3's pricer returns PR #325's bit root 7.70276909563042·10⁻⁴ exactly; its five-stage profile equals the banked
profile of PR #315's pipeline row for row.

1. **Design T** (PR #310's supplied builder, ported to h = 20). All 120 cubes carry the 12 plane block holders,
   8 partner singles and four 011 mixes the builder expects. 480 helpers are freed (entrance FULL, no records); no
   new frame is needed because every tetra-edge frame span(χa, χb) already exists in the word.
2. **Twin condensation** (PR #310's `twin.py`, ported). 480 planes whose two arrivals are mix-frame starters take
   their leftover at the 1-dimensional intersection line of the two mix frames (σ = 1); 320 new line frames.

Root: 7.70277 → 8.00345 (Design T) → 8.01726·10⁻⁴. W = 10,476 per copy; residual census {20: 5,940, 19: 480, 4: 1,200}.

## Complex supplier

PR #304's build chain (PR #202 tree with PR #315's centre-sharing `Graph.finish` patch, PR #184 flow and exact lift,
PR #256's emitter), made p-generic and run at p = 10 (`producer/`). A one-instance proxy of the base compile
(R = additions + roots − carrier arcs, exact on the tested pair and all-but-one modules) selected the modules: PR #325's
re-annealed pair module (92 net registers per instance against 95 for PR #315's), PR #327's p = 10 triple module
(549 against 593 for a p = 11 module cut down) and PR #315's all-but-one module (8). Flow R 6,265 (PR #327's own
p = 10 program: 6,455, 7795/10⁷).

Checks run on this program: PR #200's complete complex checker (all formal source/target/dirty columns), PR #194's
contract (13 checks, physical R = flow R, equal histograms), and in `verify.sh` PR #315's complex checks ported to
p = 10 (`code/complex/`): Sussman's `gx.check1` with the exact scalar identity and his `gxcore` mirror, every label
and paid child, both scalar words and lifetimes, the five-window splice with all controls rejected, and the finite
precision guard (external rows 15,125 < 20,161, induction gap 115·B, half-shrink 84 < 100). The five places where
#315 pinned its p = 11 program are now derived from the certificate (h, v, R, centres = h, centre rank h − 2,
m = 5h, W = 4v + R) or re-pinned to this program (`code/complex/pins-p10f.json`).

## Verify

    bash research/w3-p10b-complex-p10/verify.sh /tmp/w3-p10b-verify

About five minutes; needs Python 3.11+ with numpy, mpmath and sympy, g++ (C++17) and Boost headers. It checks the
manifest, rebuilds the final word from the vendored base snapshot (hash-checked), runs the ported Design T verifier
(legality, all F₂ columns, nondegeneracy), PR #266's official legality and five-stage columns checkers (11,940 columns,
six omitted-bridge controls), exact rational nondegeneracy and PR #315's prime-witness rule on the 320 new frames
(determinants ≤ 6 bits, primes {2, 3}), an exact width-100 bank tiling with 60 replicas, the complex checks above,
both rational moment engines with the 10⁻¹⁶ fallback on both sides, and PR #315's outer assembly on the complex-bound
path (47 strict constraints; the cap itself fails `leaf_saving_above_bit`; the adjacent 10⁻¹⁸ κ is rejected).

Regeneration from source (optional): `code/export_p10.py` exports the base from PR #325's package at
`0eca9340a3df6141b8e71a41638c3937b3522888`; `producer/run_one.sh L10f 10 tmod_t2_p10.json pm_p10b.json bit_qmod_p10.json`
rebuilds the complex program on the PR #202 tree (see `producer/README.md` of the predecessor complex-p10 work).

## Open obligations

- Not ported: PR #310's native downstream chain (bank review with charts and normalizers, changed projector charts,
  geometry admission, finite invoice). Only bank feasibility is shown; freed roles carry no records and are not banked.
- PR #315's scalar/prime/finite stages regenerate the word from its generator and cannot take an edited word; the
  official cohort checkers replace them for the edited word.
- The complex guard keeps PR #315's additive row constants (9909 + 252) derived at p = 11.
- All inherited interfaces of PR #315/#325 remain assumptions (all-size compiler, weighted selectors, common
  charts, restored rows, routing, prime supply, precision/recovery, complex symbolic correctness, analytic transfer).
  This is a conditional finite construction, not a formal verification of the multiplication theorem.

## Credits

Bit base word, pair module and the p = 10 five-stage pipeline: DreamingOfClouds (#325 on #315, gen5 lineage on
eumemic's source527 and hcg890/Sussman's five-stage architecture, Evan McKinney's completed banks). Design T, twin
condensation and diagnostic checkers: utcorvusvolat-dotcom's w3 work (#310); official checkers: #266. Triple module:
#327. Complex chain: #304/#256/#233/#202/#200/#194/#184 lineage; Sussman's gx checker. See `NOTICE.md`.
