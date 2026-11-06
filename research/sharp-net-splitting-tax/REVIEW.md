# Author-side review record

Prepared for @CubeJerry with substantial OpenAI Codex assistance, 2026-11-06.
This records separate agent checks, not independent human review or formal
proof-kernel acceptance.

| Final file | SHA256 |
| --- | --- |
| PROOF.md | `984b5e2d253bce7e5782fd55c8d35343a0e6e6c13544204dd9df3941257ff364` |
| verify.py | `9107b8a71114fd142f9c43fdf61e173f4b9d764bdee0fd73ad316172dc63ac8c` |
| independent_family.py | `d7d8d4027653a1e26204cb8862661c395785614691e14e2fdefbe35f11d2f420` |
| SOURCES.json | `808dfda7022eb93ff988ed794fedecfe8836dd4b9cad2e2290f183350631e197` |

The lead agent separately derived the half-exponent attaining family, then
found the completing-square proof. Its independent fixture checker uses neither
the primary implementation nor predecessor code. The lead separately checked
the general H derivative, optimized quotient envelope, monotonic turning
criterion, integer sharpness, and complete net completion accounting, then
read the frozen #4480 proof to verify the comparison with its actual
`A=max(C/u,h)` bound.

A second worker (worker C), without editing this package, independently
rederived H and its derivative, the envelope derivative and H(a), strict
unimodality and adjacent-quotient reduction, endpoint cases, the half-exponent
family and square proof, complete net-gap accounting, and the true A threshold
and strict comparisons against frozen #4480. It found no substantive blocker
at proof SHA256
`d0519ada50b088c5700d4508195feed39bb7084b837c69c229b4b4c6056b1aaa`.

The final proof makes only its two suggested clarity edits: Section 3 now
explicitly assumes sigma>1, and Section 7 says 'finite-q interior maximizer'
instead of 'finite maximizing split'. The latter avoids implying a rational
maximizing remainder. Neither edit changes a formula, argument, or verifier.

All scientific checks, ordinary and optimized, registered replay, actual
corruptions, portable copies, and source hashes are recorded in
[VALIDATION.md](VALIDATION.md). Publication-byte and official export checks
also passed for the first coherent commit. This review record and the two
clarifications are documentation-only additions; final metadata, diff and
committed-byte checks are repeated after their commit.

Native correctness, all-size compiler closure, physical costs, selected cold
replay, supplier admission, numerical application, and all five framework
assumptions remain outside this contribution's review scope.
