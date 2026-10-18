# One-pass Gaussian normalization with encoded rank

**Physical arithmetic implementation; no new exponent.** This package implements
`z -> ((1-i)/2)^D z` on complete Gaussian packets with D supplied as an encoded
Count. It realizes the O(V) normalization already specified in PR2287 using
unit tape movement, **10 fixed scratch roles**, exact division checks and
complete cleanup. It avoids D repeated packet passes.

For h-bit components, N Gaussian fields and `0<=D<=h`, with `h>=2, N>=1`, the
written argument gives O(V) time for `V=2hN`, O(h+log(N+1)) local scratch and a
separately paid V-bit protected output. Sources and descriptors are preserved.
A caller must establish the common grid, complete packet and disjointness
contracts. See [PROOF.md](PROOF.md) for the finite-carry invariant, encoded
setup, full invoice, named rejection and nested ownership boundary.

The single-pass idea and operator identity are credited prior work. This
contribution supplies the encoded physical implementation; it is not a new
asymptotic bound over PR2287's written recipe or a completed fast recursive
supplier.

## Evidence

[RESULT.json](RESULT.json) records an independent Gaussian-integer oracle:
7,728 exhaustive cases at widths 2 through 5 and every `0<=D<=h`, plus 1,022
boundary/sample cases at widths 17 and 65. There are 3,196 successful exact
outputs and 5,554 inexact rejections. Large-width ranks include 0, 1, 2, 3,
`floor(h/2)`, h-1 and h. Samples use seed 34 and integer multiples of `(1+i)^D`.
The oracle computes `(1-i)^D` by repeated Gaussian multiplication and divides
by `2^D`; it does not reuse the production parity/rotation decomposition.

Controls check late-field rollback and reuse, invalid domain parameters,
protected-output reuse, owned-source aliases, a nested caller with four live
Counts, and four deliberately broken implementations: omitted low-bit rejection,
wrong phase, wrong odd shift and incorrect negative carry. These are finite
checks; the all-size claim rests on the scoped written argument and inherited
physical-tape contracts.

The registered replay also runs with Python assertions disabled in a read-only,
Git-free source export. Changed live source bytes, an undeclared dependency and
a boolean replaced by an equal-valued integer in the receipt must all fail.

The same-input comparison includes every physical source/descriptor access,
read/write/unit move, encoded loop, output copy and disposal. Its explicit
baseline calls the degree-one kernel D times; it is not an optimized baseline
or the original PR2287 program. At h=96, N=4:

| D | One-pass tape events | Repeated-step tape events | Ratio |
| --- | ---: | ---: | ---: |
| 1 | 63,767 | 98,982 | 1.55x |
| 2 | 64,000 | 174,316 | 2.72x |
| 8 | 64,774 | 626,264 | 9.67x |
| 17 | 65,567 | 1,304,153 | 19.89x |
| **34** | **66,930** | **2,584,607** | **38.62x** |
| 64 | 68,794 | 4,844,226 | 70.42x |

D=34 is the seed-selected primary comparison. The D=1 difference comes from
baseline parent copying/setup. These ratios measure abstract tape events,
not Python wall time or end-to-end integer multiplication performance.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/gaussian-normalization-stream
```

Expected final package marker: `PASS_GAUSSIAN_NORMALIZATION_STREAM`. The registered
command checks the complete typed receipt. `verify.py --emit` regenerates only
this package's receipt. `--suite identities`, `--suite controls` and
`--suite comparison` run the indicated subsets. The direct verifier also runs
in a Git-free export containing this package and its declared input files;
metadata/provenance validation through the generic runner requires Git.

Exact base: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`.
[SOURCES.json](SOURCES.json) pins proof/runtime input bytes and their Git blobs;
[VERIFY.json](VERIFY.json) declares all inherited live inputs. The loader
compiles authenticated local loader bytes and reuses the predecessor's unchanged
immutable archive. It preserves the inherited notices. Inputs must remain
stable during a replay; this is source binding, not a hostile-process sandbox.

OS assignment seed 34 selected the complex track. [TASK.json](TASK.json)
records the changed card scope, three candidates, overlap coverage and stopping
rule. The investigation responds to the released normalization boundary in
[discussion #2238](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-18988597).

## Open next questions

- Bind the `S_D` phase sweeps and this normalizer around the physical C supplier
  in the exact Hadamard identity. First check a complete caller with common grid
  admission and all protected-output transfers. The fast recursive C child and
  the caller's `D<=h` admission remain prerequisites for a full fast-layer claim.
- Attach this local linear tariff to the complete recursive closure. First
  identify every normalization call and its packet extent in the retained
  recurrence; do not replace an unimplemented child by the direct O(fV) leaf
  outside its stopping range. Whole-call restoration and root truncation still
  require their own implementation evidence.

## Credit and scope

Prepared by **Tekalign**, with substantial **OpenAI Codex** assistance in code,
mathematics, testing and writing; Apache-2.0. No independent human or formal
review is claimed.

Jose Manuel (`jmbarrancoml`) supplied the encoded physical Gaussian phases
([PR3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087),
`e7e49fb8176772c71ad7006920a407109a89e440`) and fused coefficient framework
([PR3091](https://github.com/CrocSwap/integer-mult-bounds/pull/3091),
`d546815f4b116a79bd0ecec6661d2b2b3de29377`) reused here. His general scalar
recipes ([PR3098](https://github.com/CrocSwap/integer-mult-bounds/pull/3098),
`ae54061980ef6a956d1276c7775aa833c1f669ca`) are related completed work, not a
new contribution of this package.

Jose Manuel also supplied the normalization identity and high-level specification in
[PR2287](https://github.com/CrocSwap/integer-mult-bounds/pull/2287),
`8c60765b5dea9d862b3b190d55da102a576031bf`. We retain Alejandro Zarzuelo Urdiales's
Gaussian parity/grid work, James Chang's PR1869 ripple-addition lineage, and
all contributors and notices in the inherited PR3055/2899/C0 source chain.
Upstream sources, existing packages and the selected conditional frontier
`0.001672660197076918` are unchanged. Completing normalization alone does not
supply the phase sweeps, recursive child, caller grid proof or final truncation.
