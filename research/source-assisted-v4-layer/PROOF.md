# A stronger complex supplier: PR200's reuse pairing on the source-assisted v4 word

**Claim.** The source-assisted complex word of PR #184 (icekylinx) on the PR #168 v4 modules (PR #193/#194,
ikeboy), with every input of PR #194's pipeline unchanged **except the 2,310 reuse pairs** of its physical layer
(PR #168's operation frames are kept byte for byte), certifies the complex saving

    a_C = 3549537/5000000000 = 7.0990740·10⁻⁴      (PR #194: 219037/312500000 = 7.0091844·10⁻⁴, +1.28%).

Composed with PR #200's bit supplier through PR #194's unchanged 47-constraint assembly the result is
κ = 6768823/10¹⁰, the same as PR #202, because the bit branch binds (effective 6.7734·10⁻⁴). **No new κ.** The
complex cap of every composition on this lineage rises from 7.0092·10⁻⁴ to 7.0990740·10⁻⁴, and the exact-DFT
exponent saving of `research/exact-dft-transfer` (PR #225) rises with it.

## What changes

PR #194's pipeline is: regenerate the PR #168 v4 complex cache (`scripts/paired_cube_producer.py`); the
source-parity rewrite of the three query modules (`source_aligned_local_v4.py`), which also runs PR #168's physical
layer (endpoint descent and late compensated reuse pairs) and writes it to
`references/paired-cube/physical/{frames,pairs}.json` of the aligned tree; the equal-frame fresh-channel
compression (`complex_frame_flow.py`), which reads that physical layer; the exact arbitrary-dirty lifts
(`exact_complex_flow_lift.py`); the contract (`contract_v4.py`); and the assembly.

The flow's child histogram depends on the reuse pairs it receives: a pair identifies a dead ungauged donor's
register with a gauged recipient, and the flow's equal-frame compression follows those identifications. This
package replaces only the pairing. PR #168's pairing is its maximum matching of donors to recipients in a fixed
order; the pairing in `witness/physical-pairs.json` is PR #200's late compensated pairing (`discovery/`,
`physical_opt.py:pairs`) with the maximum-weight pairing of `pairs_mw.py` (transversal-matroid greedy with augmenting paths, donor weight the gain heuristic of PR #200): the same legality (donor ungauged, non-root, dead before the recipient's
first operation, donor end frame inside the recipient gauge), a maximum matching, but a different selection among
the maximum matchings. The operation frames are PR #168's own (0 of 17,789 changed); the matching arcs, modules,
local circuit, gauges, aligned rewrite and flow options are PR #194's.

Discovery record (`discovery/README.md`, float flow roots): PR #168's pairing 7.00918·10⁻⁴; PR #200's default
pairing 7.09765·10⁻⁴; the maximum-weight pairing of `pairs_mw.py` (transversal-matroid greedy with augmenting paths, donor weight the gain heuristic of PR #200) 7.0990740·10⁻⁴. Random pairings fall to 6.6·10⁻⁴, and single operation-frame moves on
top of PR #168's frames never raise the flow root (a screen over every endpoint move), so the frames are left
untouched.

## What is checked (`verify.py`, about 80 seconds, Python 3.11+ with numpy/scipy for the regeneration steps)

1. **Pins.** `baseline-pr202.tar.gz` holds the 308 files of PR #202 at `8d8d67b` that the pipeline runs (PR #194's
   package and PR #184's decision/global scripts, the PR #168 v4 scripts, references and inherited witnesses, the
   Clifford frames note, and PR #200's certificate, arithmetic and complex checker), each pinned by sha256 in
   `SOURCE.json`; the three witness files are pinned too. Reviewers can confirm with `git show 8d8d67b:<path> |
   sha256sum`.
2. **Regeneration.** The producer and the aligned rewrite run unchanged, including PR #168's physical layer and its
   own physical scalar/frame checks on that layer; the frames this package installs are byte for byte that layer's.
3. **Admission of this pairing.** With the package's pairs installed, PR #200's complete complex checker
   (`complex/physical.py` with `verify_fused.py`) re-executes the aligned word: every frame contains its node span
   and is nondegenerate, every role chain nests (entrance, operations, root frame, full space), every alias is read
   at its deadline after its donor's last operation with the donor's end frame inside the recipient gauge, the
   target read chronology holds, the exact adjoint is rederived, and every formal source, target and dirty column
   is replayed in both shear signs on an injective packed basis with an independently derived coefficient bound.
4. **Flow, lift, contract.** PR #184's flow runs on this layer with the package's kernel pairs; the exact lift
   verifies every local map and inverse gate program over the rationals (all coefficients dyadic) and the monotone,
   acyclic once-only reuse DAG with frame containment; the contract certifies the fresh columns, read chronology,
   target chains and the normalized profile (13 checks), with the package's physical and kernel pairs as the frozen
   witnesses that PR #194's contract compares against.
5. **Assembly.** PR #194's `assemble.py` composes the certified complex profile with PR #200's bit certificate and
   reproduces `certificate.json` exactly (exact fields only; the full run record is `report.json`): complex saving
   3549537/5000000000, κ 6768823/10¹⁰, the next grid point rejected by the unchanged assembly.

The complex profile keeps PR #194's m = 66, W = 12,052 roles per vertex, rank mass 794,112 and deficit 1,320; only
the child histogram changes (the flow compresses the same 13,372 physical roles to 9,412 but splits the remaining
increments differently).

## Scope and limits

- Conditional exactly as PR #194: the retained analytic, uniform-recursion, precision, weighted bit frames,
  fixed-tape routing, restored-row and all-size semantic interfaces remain hypotheses; the scalar replays and exact
  lifts are finite checks. PR #184's independent complex scalar transcript is not re-exported here; the one-column
  identity is replayed by PR #200's checker on the pre-flow word and by the lift's inverse gate programs.
- Nothing here changes κ; the bit supplier binds. It raises the complex cap for every bit-side construction on
  this lineage and the exact-DFT exponent.
- The pairing is a discovery heuristic; no optimality among maximum matchings is claimed.
