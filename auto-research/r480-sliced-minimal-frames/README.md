# PR541 trace refinement with sliced R480 frame reductions

**Conditional kappa = 0.001587467473762886**, about **0.0160671% above PR541's0.001587212454640692**. Fresh finite physical verification passes. The unchanged cited complex supplier now binds.

## Construction and contribution

Dugongue PR541 supplies60 commuting preloads in PR510's R480 bit word. This package reconstructs that exact source word, then adds our observable slice and frozen frame reductions:

1. Compute exact backward F2 target responses and remove227 target-zero A gates plus their227 inverse cleanup gates. The whole scalar endpoint remains unchanged.
2. On the original sliced R480 word, process gates chronologically and replace each A/B frame by the exact rational span of its preceding operand frames. This is the least feasible assignment in subspace inclusion for that fixed word, not a claim of moment optimality. It finds19 smaller operation frames and3 new rank-three root closures.
3. Transfer those19 specific reductions to the sliced PR541 word by exact gate identity and verify every frame containment. Retain all other PR541 frames and regenerate literal inverse cleanup at the full frame.

Re-minimizing every frame after adding PR541's preloads was a losing composition. Separate histogram deltas also do not add: the two changes interact. The final combined word is independently recounted, then physically emitted and audited.

The local paid profile, including9 rank-eight center copies, is

`{1:1286,2:1319,3:45,4:169,5:1,6:130,8:9}`.

The complete nine-stage profile is

`{1:370368,2:395232,3:12960,4:64032,5:288,6:52800,7:23040,8:2592}`.

All480 helpers retain width8; the original literal PR510 owner selection remains valid. Live stock30720, physical stock30729 and rank deficit9984 are unchanged. Every positive idle remainder is included.

Two independent rational moment engines certify bit c = **0.001590005077309865651707**, rejecting the next10^-24 grid point. PR535 complex b = **0.001589991533606044174031** is cited unchanged and repriced. It now binds. Six explicit bootstrap levels and47 strict outer inequalities give kappa = **793733736881443/500000000000000000**. Literal bit fallback charging follows PR539 and its461/464/465 ancestry.

## Verification and reproduction

Arithmetic/construction replay (Python3.11+, SymPy):

```sh
python -B verify.py /absolute/new/output
```

Complete offline finite replay also needs NumPy, C++17 and genuine Boost headers:

```sh
python -B verify.py /absolute/new/output --physical --boost-include /usr/include
```

Use `/opt/homebrew/include` for the tested macOS Homebrew installation. Outputs must be new and outside the package. No optimizer, network or Lean is required. The pinned PR493/510 dependencies are included as byte-preserved source archives and extracted only into the fresh output directory.

Completed checks cover:

- Exact source reconstruction and final-word equality; independent720-column scalar/nesting check, all120 sources restored, and674 nonzero used frame Grams.
- Fresh native C++ legality,960-column five-stage and1440-column nine-stage checks,18 omitted-bridge controls and inherited structural/mutable-source corruption checks. Native prefix payload101bits satisfies the104-bit bound.
- All675 catalogue frame Grams and prime witnesses, fresh compressed geometry, both local orientations and unbanked global scalar replay.
- Explicit138240 whole-helper owner occurrences and10500480 emitted events;17 parent mutations and16 hosting mutations rejected.
- Fresh finite invoice: prefix191bits charged192; two-level coefficient421bits charged512; row coefficient18355 below20161. The previously assumed allowances are therefore justified for the changed word.
- Both exact moment engines, six explicit finite bootstrap cutoffs,47 strict outer inequalities, and rejection of the next kappa grid point, zero eta, zero beta and unit beta.

Python3.14 direct physical replay and Python3.11 full packaged physical replay pass. Raw emitted records, exact profile, invoice and kappa agree; final rational arithmetic receipts are identical. Timings and gzip metadata differ. The initial3.11 packaged attempt rejected only the floating discovery diagnostic `fee_delta`; its failure is retained. Only that diagnostic and timing are excluded from receipt equality; actual frames, candidate words, profiles and rational prices remain checked exactly.

Receipts are in evidence/, including the manifest tested by the full3.11 run. BASE-prefixed receipts describe the earlier standalone candidate and are preserved separately. The dedicated GitHub workflow runs the complete finite replay on3.11 and3.14; local success is not a claim that CI has completed.

## Scope and credits

All inherited all-size compiler, common-label/mutable-source realization, compressed geometry, whole-call hosting, restored work, precision/tape and analytic-transfer assumptions remain conditional. PR535's complex operator is cited rather than freshly rebuilt. No unconditional multiplication theorem, full Lean proof, unrestricted optimum or measured speedup is claimed.

Dugongue541 supplies the preload transformation; our contribution is the observable slice, lower frames and this verified composition. PR510/493 supply the underlying circuit and controller; original notices and licenses remain in NOTICE.md, SOURCES.json and dependency archives. Prepared for rohanarun with OpenAI Codex assistance.
