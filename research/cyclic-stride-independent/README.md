# Independent weighted-stride resolvent and dual audit

**Status: independent verification / research note. No new kappa.**

This contributes a finite-geometric-sum oracle, a written all-length
cycle/dual identity, and a source-bound comparison with the neighboring
weighted factor in Chafik Boukhalfa's pending PR628. It covers non-coprime
strides with separate cycle closures and the bilinear inverse transpose.
Those are different obligations from the predecessor's neighboring forward
Gaussian checks, PR668's resultant CRT, PR666's composite lifting, and
PR663/PR673's dirty composition. No defect in PR628's stated neighboring
scope was found. Incorrect extensions have exact rejecting controls.

PR628 already supplies a charged two-sort layout for a constant scalar gauge
and the direct-sum norm argument. Neither is new here. This package instead
checks per-cycle closures with independently varying phases and the bilinear
dual through a different exact algorithm; it does not replay or improve the
predecessor's sorting implementation.

## Pins and current state

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR628: `0768f97d06c623b8211e651543c66135796b62bf`.
`SOURCE.json` binds eight source/proof/layout/notice files by SHA-256. `CLAIM.json`
records OS-random seed 79, three candidates, exclusions and local scope.
No pinned sprint coordination issue was found; no reservation issue opened.

At the base, the selected certificate is #626 with #543, conditional
kappa `51110230636731/31250000000000000 = 0.001635527380375392`.
It was followed to `research/complex-k492-owner-repair`, the retained
`research/community-k492-audit/pr626/replay/ASSEMBLY.json`, and
`docs/research/community-k492-review.md`. That frontier is not a dependency
of the algebra checked here and is not changed by this contribution.

## Reproduce

Python 3.9+ and Git, standard library only. Fetch the exact pending source
object once if it is absent; this does not check out or modify its files:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git 0768f97d06c623b8211e651543c66135796b62bf
```

From this contribution's checkout, the complete deterministic check is:

```sh
python3 -B -I research/cyclic-stride-independent/verify.py --check research/cyclic-stride-independent/EXPECTED.json
```

Expected:

```text
PASS_STRIDE_RESOLVENT_AND_DUAL
{"all_entry_checks": 252730, "exact_cases": 266, "rejected_controls": 16, "rounded_cases": 4256, "rounded_coordinates": 53472}
```

The source files are extracted to an automatically removed temporary
directory and checked before execution. Only the unchanged scan/apply ASTs
and their original arithmetic are executed; no approximate-root setup or
full-kernel verifier is run. `--oracle-only` is a separately labeled partial
mode and cannot pass a full-receipt comparison. `--out PATH` writes a fresh
receipt; `--check PATH` compares every parsed field, not only status.

Additional focused tests: `python3 -B -I research/cyclic-stride-independent/test_verify.py`.
Optimized replay: add `-O` to the complete command above. Mathematical
checks use explicit exceptions and remain enabled under optimization.

## Fixed domain and completed coverage

Lengths 1 through 12, plus 16,18,21; every stride residue; both roots
`1/4+i/8` and `2-i/4`; deterministic nonconstant rational-unit phase patterns
and RHS values from seed 79. There is no adaptive search or early success
stopping rule: every domain point is executed. Each exact inverse is checked
on ALL matrix entries in both orders, together with both inverse-transpose
products and its entrywise transpose identity. Signed representatives and
the zero-root edge case are checked separately.

The receipt has 266 cases (122 with multiple cycles, 30 zero-stride),
252,730 matrix-entry obligations, and 266 signed-stride checks. Rounded
comparisons cover forward/dual, both neighboring enumeration directions,
12/40-bit grids, a dense rational RHS and a selected basis RHS: 4,256 calls
and 53,472 output coordinates. Rounded arithmetic is nonlinear; these finite
RHS tests are not an all-input proof. Exact forward/dual matrices and rounded
outputs have deterministic digest evidence, with actual phases and cycle
holonomies retained in the receipt.

Sixteen controls reject global-product closure, global rather than local
cycle length, omitted closure, wrong dual phase indexing, conjugation,
a missing cycle, wrong scattering, a genuinely singular root, bad phases,
empty/noninteger inputs, altered source hashes, the predecessor's built-in
wrong-inner-phase mutant, wrong RHS length, underprecision and a root that
fails the admitted margin. The concrete closure example is in `PROOF.md`.

See `VALIDATION.md` for executed commands and limits; `NOTICE.md` for credit.
