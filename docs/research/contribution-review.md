# Contribution review: release update and historical triage

The selected PR #39 chain has now passed the [conditional maintainer audit](community-final-audit.md)
and is incorporated in the community release at kappa=3.886675852e-5 > 2^-15.
The dated snapshot and original triage below are preserved as historical records;
their pending/non-import statements describe the earlier 2^-30 checkpoint.
PR #40 and later submissions remain outside this audit.

## Original triage record

Snapshot taken October 8, 2026. This is a triage index, not acceptance of any
submitted bound. No PR was merged, modified or commented on during release
preparation. The repository's included checkpoint remains conditional 2^-30.

## Overlap and attribution

[Zhihao Chen's PR #7](https://github.com/CrocSwap/integer-mult-bounds/pull/7)
was submitted before this checkpoint and contains the same F3 five-subset
motif, rational form I-(2/25)J, common-pair source-span argument and fixed
finite-alphabet direction. Its producer and center schedule differ, and it
claims a stronger bound. The release credits that earlier submission and
makes no priority claim for the motif. No PR #7 source code is imported.

[eumemic's PR #3](https://github.com/CrocSwap/integer-mult-bounds/pull/3)
was submitted after the local complex checkpoint commit `1c09a58`
(October 8, 01:10 UTC) and before this release. Its compressed complex circuit
and binary phase-frame argument are related work;
it is explicitly acknowledged. The included complex implementation and its
certificates remain those of the previous local 2^-31 commit.

The review so far read the PR descriptions and the pinned PR #7 construction
note, and inspected PR #34's dependency/reproduction entry point. It has not
reproduced their suites or independently audited their general tape and
precision arguments. A contributor's successful test report, or a large
headline in a PR title, is not treated as verification by this project.

## Review order

1. **Foundation: #3, #5, #7.** Review signed complex restoration and binary
   residuals, the faster Gaussian tape/error argument, and the retained-total
   ternary frame schedule. Reproduce the whole dependency chain with pinned
   inputs and preserve every contributor's attribution.
2. **Bulk recursive calls: #10 and #13.** Verify that contiguous projector
   blocks use one compatible controlled basis, that the actual children have
   the stated volume/width, and that the dependency-path guard covers every
   physical call. These changes appear to cross the singleton-rank recurrence
   limitation; the headline alone does not establish that step.
3. **Source frames, partial swaps and semantic precision: #18–#25.** Audit
   source/output endpoints, restoration, setup and row stock, and the exact
   semantic error propagation. Check changes to the Gaussian enclosure and
   resulting assembly rather than only rerunning rational inequalities.
4. **Two-stage topology: #29, #31, #33, #34.** Check the paid endpoint copy
   correction and complete physical list, the common-basis existence proof,
   exact rank partitions, and compatibility with every inherited interface.
   #34 is a small refinement of a long dependency chain, not a standalone
   proof of its final multiplication bound.
5. **Copied centers and fixed bases: #35–#39.** Check paid transforms and endpoint
   corrections, both invocation orientations, complete child lists and compatible
   bases. These layer on the earlier analytic and two-stage dependencies; a
   focused final-PR check is insufficient.
6. **Lean certificate PR #26.** Identify exactly which arithmetic statements
   are formalized and build them. Do not equate a certificate check with
   formalization of the full multiplication machine.

Any accepted stronger witness needs a coherent complete proof package,
reproducible artifacts, checked downstream substitutions, and provenance.
The independent 2^-30 checkpoint can be preserved even if a stronger
contribution later supersedes its headline.

## Submitted claims (unverified here)

This table records all open and closed submissions at the checkpoint snapshot.
Titles are contributors' claims, not accepted results. The complete head hashes
and dates are in [contribution-snapshot.json](contribution-snapshot.json).
See [CONTRIBUTORS.md](../../CONTRIBUTORS.md) for contributions and parallel work.

| PR | Contributor | State | Submitted title | Head at snapshot |
| --- | --- | --- | --- | --- |
| [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1) | Paureel | open | Refine paired parameters and derive the fixed-exponent supremum | `bfb168a5611c` |
| [#2](https://github.com/CrocSwap/integer-mult-bounds/pull/2) | Bortlesboat | open | Align pair groups for a conditional 17*2^-63 bound | `1c200af99d34` |
| [#3](https://github.com/CrocSwap/integer-mult-bounds/pull/3) | eumemic | open | Compress the complex network for a conditional 59/10^11 > 2^-31 bound | `dfe5b818aad4` |
| [#4](https://github.com/CrocSwap/integer-mult-bounds/pull/4) | dleen | open | Combine PR #3 shared exclusions with retained totals and stage sharing | `8c225e619168` |
| [#5](https://github.com/CrocSwap/integer-mult-bounds/pull/5) | eumemic | open | Faster Gaussian resampling for a conditional 1479/10^12 > 2^-30 bound | `d3d370c34937` |
| [#6](https://github.com/CrocSwap/integer-mult-bounds/pull/6) | eumemic | open | Aligned bit circuit with cheaper centers for a conditional 1624/10^12 bound | `5015011bd9a6` |
| [#7](https://github.com/CrocSwap/integer-mult-bounds/pull/7) | jacklightChen | open | Ternary five-subset networks for a conditional 373/10^11 > 2^-28 bound | `6725c6a17b17` |
| [#8](https://github.com/CrocSwap/integer-mult-bounds/pull/8) | rohanarun | open | Review conditional geometric complex-network candidate with kappa = 5.9e-10 | `428bb215bb8a` |
| [#9](https://github.com/CrocSwap/integer-mult-bounds/pull/9) | rohanarun | open | Refine PR #7 ternary star templates for conditional kappa = 3.8e-9 | `cfd6a2baded9` |
| [#10](https://github.com/CrocSwap/integer-mult-bounds/pull/10) | icekylinx | open | Batch recursive networks for a conditional kappa > 2^-23 bound | `62691e395a04` |
| [#11](https://github.com/CrocSwap/integer-mult-bounds/pull/11) | rohanarun | closed | Generalize geometric bank matching and screen extensions (no kappa change) | `a97c1baaf354` |
| [#12](https://github.com/CrocSwap/integer-mult-bounds/pull/12) | rohanarun | open | Use dimension-30 geometry for conditional kappa = 1.2649e-7 | `35d31e30f28b` |
| [#13](https://github.com/CrocSwap/integer-mult-bounds/pull/13) | eumemic | open | Auxiliary source frames for a conditional kappa = 7699/10^10 > 2^-21 bound | `3ef246fa4f69` |
| [#14](https://github.com/CrocSwap/integer-mult-bounds/pull/14) | rohanarun | open | Combine source frames and data corners for conditional kappa = 9.0799e-7 | `1fa5b9a9aacc` |
| [#15](https://github.com/CrocSwap/integer-mult-bounds/pull/15) | eumemic | open | Smaller h30 producer and full complex batching for conditional κ > 2^-20 | `a17cab396ce1` |
| [#16](https://github.com/CrocSwap/integer-mult-bounds/pull/16) | jacklightChen | open | Nested controlled bases for a conditional 9799/10^10 > 2^-20 bound | `a80f5e676c84` |
| [#17](https://github.com/CrocSwap/integer-mult-bounds/pull/17) | rohanarun | open | Compose nested geometry and smaller h30 producer for conditional κ = 1.248342e-6 > 2^-20 | `c915b4117626` |
| [#18](https://github.com/CrocSwap/integer-mult-bounds/pull/18) | icekylinx | open | Partial-swap networks for a conditional kappa = 1.884586e-6 bound | `f2ab41aebad4` |
| [#19](https://github.com/CrocSwap/integer-mult-bounds/pull/19) | rohanarun | open | Partial-swap ternary geometry for conditional κ = 2.093495e-6 > 2^-19 | `817aeb7b1225` |
| [#20](https://github.com/CrocSwap/integer-mult-bounds/pull/20) | hipotures | open | Source-framed h53 conditional witness above 2^-20: attributed research record | `4f8d6c8272b5` |
| [#21](https://github.com/CrocSwap/integer-mult-bounds/pull/21) | jacklightChen | open | Translated partial-swap frames for a conditional 5499/10^9 > 2^-18 bound | `5ba6cf0bfb68` |
| [#22](https://github.com/CrocSwap/integer-mult-bounds/pull/22) | DominikScholz | open | Refine translated parameters to conditional κ = 5.7114918e-6 | `c2f03ed48637` |
| [#23](https://github.com/CrocSwap/integer-mult-bounds/pull/23) | jacklightChen | open | Semantic precision and bulk resampling for a conditional 1099/10^8 > 2^-17 bound | `661ebabc1076` |
| [#24](https://github.com/CrocSwap/integer-mult-bounds/pull/24) | icekylinx | open | Endpoint gauges for a conditional kappa = 5.98615e-6 bound | `ed90fd940279` |
| [#25](https://github.com/CrocSwap/integer-mult-bounds/pull/25) | rohanarun | open | Expose an A5 block for conditional κ = 1.1447067e-5 > 2^-17 | `003f366cfa99` |
| [#26](https://github.com/CrocSwap/integer-mult-bounds/pull/26) | princezuda | open | Lean certificate check | `f764fb982085` |
| [#27](https://github.com/CrocSwap/integer-mult-bounds/pull/27) | DominikScholz | open | Compose endpoint bit and semantic bulk interfaces for conditional κ = 1.19720853e-5 | `c297233e788a` |
| [#28](https://github.com/CrocSwap/integer-mult-bounds/pull/28) | rohanarun | open | Rectangular geometry for conditional κ = 1.2260937e-5 > 2^-17 | `bb1143d0714b` |
| [#29](https://github.com/CrocSwap/integer-mult-bounds/pull/29) | jacklightChen | open | Two-stage controlled corners for a conditional 15536/10^9 > 2^-16 bound | `9d963275075f` |
| [#30](https://github.com/CrocSwap/integer-mult-bounds/pull/30) | DominikScholz | closed | Near-balanced bit blocks for conditional κ = 1.3001411e-5 | `01c9e7023ac2` |
| [#31](https://github.com/CrocSwap/integer-mult-bounds/pull/31) | rohanarun | open | Exact data-corner certificates for conditional κ = 1.5878574e-5 > 2^-16 | `122e6453e803` |
| [#32](https://github.com/CrocSwap/integer-mult-bounds/pull/32) | icekylinx | open | Structured projector blocks and bulk assembly for conditional kappa = 1.2523415e-5 | `0ef3aeb61f55` |
| [#33](https://github.com/CrocSwap/integer-mult-bounds/pull/33) | DominikScholz | open | Compose smaller two-stage dimensions and data blocks for conditional κ = 1.638103206e-5 | `a499a345c040` |
| [#34](https://github.com/CrocSwap/integer-mult-bounds/pull/34) | jamesyc | open | Reversed two-stage basis and balanced assembly for conditional κ = 1.639226629e-5 | `7fecbe3651e0` |
| [#35](https://github.com/CrocSwap/integer-mult-bounds/pull/35) | DominikScholz | open | Fixed local bases in two stages for conditional κ = 1.6631776e-5 | `9c345a2a11e5` |
| [#36](https://github.com/CrocSwap/integer-mult-bounds/pull/36) | icekylinx | open | Copied retained centers and two-stage assembly for conditional kappa = 3.84569e-5 | `11817ccacb56` |
| [#37](https://github.com/CrocSwap/integer-mult-bounds/pull/37) | rohanarun | open | Copied centers and reversed corners for conditional κ = 3.850771033e-5 > 2^-15 | `2f7578affce4` |
| [#38](https://github.com/CrocSwap/integer-mult-bounds/pull/38) | DominikScholz | open | Copied centers with fixed local bases for conditional κ = 3.886224e-5 | `605323bab4ba` |
| [#39](https://github.com/CrocSwap/integer-mult-bounds/pull/39) | rohanarun | open | Fixed middle basis and copied reversed corners: conditional κ = 3.886675852e-5 > 2^-15 | `70ae24129649` |

## Later queue entries

- [#40](https://github.com/CrocSwap/integer-mult-bounds/pull/40), rohanarun: Both fixed bases and copied reversed corners: conditional κ = 3.918734894e-5 > 2^-15.
  Pinned `43f59ff533598762cbc43a5e14af2bbbc76fabbd`; not imported in the #39 integration pass.

## Later stacked candidate: terminal elimination on shrunk frames (9 October 2026)

- **Submission:** [Draft PR #140](https://github.com/CrocSwap/integer-mult-bounds/pull/140), based on upstream `main` with head `sennemmi:research/terminal-elision-shrunk-frames`.
- **Candidate snapshot:** `9cdf73e8682fb12749482e710e50bc585d282a7c`.
- **Pinned sources:** Joel Pulikkan's PR #125 head `dda535bdcfc321a13a1ebd3c2d70e2b5bb72368e`; SovereignSteak's PR #122 head `b1a6f24e57141637b3ff040d6f2ce9d896ffb9bb`.
- **Submitted result:** conditional κ = `110875518403/10^15`, about 0.257% above the fixed #125 parent. The live upstream Draft PR #139 has a higher finite candidate on the separate triple-core lockstep route; this candidate makes no global-frontier claim.
- **Review status:** draft awaiting independent mathematical review. Its finite verifier and controls pass; inherited transfer, analytic, fixed-tape and all-size assembly interfaces remain open proof obligations.
