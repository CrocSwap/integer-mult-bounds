# Independent integer-root audit of PR1536's 200-digit complex endpoints

**All four pinned endpoint decisions are confirmed. No new construction or κ
is claimed.** This separately written verifier checks the T74 native and
conservative complex moments at their `SPEC.json` lower endpoints and at each
endpoint plus `10^-200`. It uses integer square roots and outward dyadic
products. It imports no supplier, logarithm, exponential or predecessor checker.
The numerical method is prior art from arkfx's [PR706](https://github.com/CrocSwap/integer-mult-bounds/pull/706).

The audited source is Jeremy Kothe's [PR1536](https://github.com/CrocSwap/integer-mult-bounds/pull/1536),
head `527d7623009f295b7311e98ae36f5e2fbdbbc3e5`. That proposal repairs the
fine-Mercator enclosure defect found by philippeVV in PR1519. This corroborates
the repaired proposal's moment decisions with a different arithmetic path;
it does not claim another repair or establish general soundness of those engines.

## Result and precise model

Read the full endpoint rationals and exact residual intervals in
[CERTIFICATE.json](CERTIFICATE.json). Let `b` and `c` be
`inputs/SPEC.json:expected.complex_lower` and `conservative_complex_lower`.
The following rational display intervals contain the certified residuals:

| Model and exponent | Moment minus one, in units of `10^-200` | Strict decision |
|---|---:|---|
| Native at `b` | `[-1.232, -1.231]` | below one |
| Native at `b + 10^-200` | `[1.690, 1.691]` | above one |
| Conservative at `c` | `[-0.986, -0.985]` | below one |
| Conservative at `c + 10^-200` | `[1.935, 1.936]` | above one |

The pinned aggregate is
`H={1:1559100, 2:339000, 3:277392, 4:84912, 5:54612, 8:5328, 48:22748}`,
`m=73`, `W=66304`. It has 2,343,092 children, rank mass 4,816,512 and
deficit `mW - mass = 23,680`. Its construction-level correctness is inherited.
This audit checks its equality to SPEC's aggregate and rank mass, without
reconstructing the children from operations or owners.

The native moment is

`M(a) = Σ_r H[r] * r/(mW) * (m/r)^a`.

The conservative model adds the source assembler's fallback charge

`32*m*Σ_r H[r]/(10^16*W) * m^a`.

All coefficients are exact positive rationals. Both models are continuous and
strictly increasing in `a`, since every `m/r>1`. Therefore each pair of strict
signs brackets its unique moment-one root in an interval of width `10^-200`.
This is a statement about these two pinned aggregate cost models.

PR1536's committed `evidence/ASSEMBLY.json` retains the coarse predecessor
endpoints. This audit consumes the fine SPEC endpoints and reads the source
assembler's formula; it does not treat the old evidence file as a fine replay
receipt. The six copied inputs are authenticated against both Git blob IDs and
SHA256, and five are cross-checked against the copied upstream manifest. The
whole 160-file source package is not replayed or authenticated here.

## Why the enclosure is valid

For a rational base `x>=1`, choose `S=2^P`. Start with integers
`l_0=floor(S*x)`, `u_0=ceil(S*x)`. If
`l_k/S <= x^(1/2^k) <= u_k/S`, then

`l_(k+1)=isqrt(l_k*S)` and `u_(k+1)=ceil_sqrt(u_k*S)`

enclose the next square root. This follows from monotonicity of the square
root and from `isqrt(n)^2 <= n < (isqrt(n)+1)^2`. Ceiling is computed as
`isqrt(n) + [isqrt(n)^2 != n]`; no approximate square root is used.

For `n/2^N` in `[0,1]`, its binary bits select the factors
`x^(1/2), ..., x^(1/2^N)`. Multiplying nonnegative scaled intervals with
`floor(l*l'/S)` and `ceil(u*u'/S)` preserves inclusion. The cases `n=0` and
`n=2^N` use one and the initial base interval, respectively.

For the actual rational `a`, set `n=floor(a*2^N)` and
`n'=ceil(a*2^N)`. Monotonicity of `x^a` gives
`x^(n/2^N) <= x^a <= x^(n'/2^N)`. Use the lower product bound at `n` and
the upper product bound at `n'`. Taking only the truncated exponent as an
upper bound is unsafe and has an explicit failure control.

Exact positive weighting and summation then enclose the complete moment.
No series remainder, floating point, logarithm or exponential is used.
An interval touching zero is unresolved; it is never treated as a rejection.
The receipt uses `N=768`, `P=1024`; `N=896`, `P=1280` gives contained,
narrower intervals and the same four strict signs. This containment is checked
on the actual inputs, not assumed to hold for every possible precision pair.

## Reproduce and controls

Python 3.12 standard library, no network. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/pr1536-root-endpoint-audit
```

Direct standalone commands, also usable in an exported package without Git:

```sh
python3 -I -O -B research/pr1536-root-endpoint-audit/verify.py
python3 -I -O -B research/pr1536-root-endpoint-audit/test_verify.py -v
```

The first command prints `PASS_PR1536_INTEGER_ROOT_ENDPOINT_AUDIT decisions=4
controls=12 exact_power_comparisons=30`. The second runs ten test groups.
Regeneration is explicit: `verify.py --write-certificate`. Normal replay only
compares the committed receipt and leaves all package bytes unchanged.

The verifier includes 30 exact small-power comparisons and twelve controls:
invalid arguments, inverted/unresolved intervals, deliberately insufficient
precision, swapped surcharge policy, one omitted rank-48 child, a changed
histogram preserving both count and mass, and physical-stock normalization.
The model mutations expose false conclusions under changed inputs; they are
not alleged defects in PR1536.

Tests also cover 4,105 integer square-root rounding cases, 2,048 division cases,
30 rational-power comparisons including non-dyadic exponents, actual unsafe
square-root/product-rounding mutants, exponent truncation, corruption of each
copied source, head/inventory corruption, a corrupted certificate, and
optimized relocated replay without any supplier modules. Test scratch
directories are created beside the package and removed after each test.

## Assignment, independence and remaining obligations

Started from current main `c5108f0f68d482e5712a8e26a5978d47762dfc16`.
Chooser nonce `0cfced81e5b410bca1d5fd3d27a63fce` selected independent
verification. [TASK.json](TASK.json) records the changed `independent-moment`
scope: the selected PR1094 ledger/endpoint checks already have extensive
coverage, including PR1262/1421 and the retained engines. This audit instead
checks a new pending 200-digit claim after an enclosure defect was reported.
[Discussion1561](https://github.com/CrocSwap/integer-mult-bounds/discussions/1561)
records the precise advisory claim and handoff.

PR706 introduced this enclosure method for historical PR626 at `10^-24`;
no new numerical method is claimed. PR1536's oracle checks logarithm
enclosures, while this verifier constructs power intervals without those
logarithms. PR1549 refines the outer κ grid on the same endpoint family;
this audit does not verify that outer refinement. Source/provenance pins and
overlap coverage are recorded in [INPUTS.json](INPUTS.json),
[SOURCES.json](SOURCES.json) and TASK.json.

Unrun obligations: full cold admission, operation/owner ledger reconstruction,
native/Clifford replay, bit supplier, all outer/bootstrap inequalities,
roundoff/tape, Lean, and the inherited all-size compiler, common-label/mutable
source realization, hosting and analytic transfer. This partial arithmetic
audit does not adopt PR1536 or PR1549 as a supplier, change the selected
frontier or certify their complete headline κ. Hosted CI is separate from the
local evidence in [VALIDATION.json](VALIDATION.json).

## Open next questions

Could this root oracle serve as an opt-in independent check for future
fine-endpoint nominations? The first step is to compare equal source-bound
brackets, unresolved cases and deliberate bad-enclosure mutants against the
repaired log/exp engines. Distinct arithmetic could catch implementation
errors, but general coverage and performance have not been established by
these four decisions. The structured question and blocker are in TASK.json.

## Credit and license

- Jeremy Kothe (`jeremykothe2`): PR1536 fine endpoints and repaired package;
  retained parent/donor construction and PR1377 grid refinement.
- Rohan Arun (`rohanarun`): PR1424 outer refinement and PR1319/1297/T74
  exact-fill construction.
- philippeVV: PR1519 fine-Mercator enclosure finding.
- arkfx: PR706 integer-root/dyadic enclosure method.
- Sagar Thakrar: PR1051/1069 independent atanh/Taylor pricing precedent;
  the PR1536 oracle and retained Mercator/base-two engine authors.
- Jeremy Diviney, Thomas DiFiore, PR1195/1196 and the cumulative construction,
  bit and audit lineage retained in the unchanged input README and NOTICE.

Prepared for Arham Tahir (`Arham-Tahir64`) with substantial OpenAI Codex
assistance in mathematics, implementation, verification and prose. No
subagents or independent human review. New material is Apache-2.0;
the copied predecessor [NOTICE](inputs/NOTICE) is retained unchanged.
