# Independent implementation and scoped proof review

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

## Prior corank-one version

The session lead reviewed publication candidate
`7e414eda36abae0ae4e7dce46e79c030854083dd`. This note records independent
AI review within the same research session. It does not claim human,
external mathematical, or formal proof-kernel acceptance.

| Reviewed file | SHA256 |
| --- | --- |
| PROOF.md | `5bd4d3761ac888ef80af5a8be0da9b0e141ab1f649d0830c81bd5010960fdb83` |
| verify.py | `9baaa99a1cde872a72348af8bd090707d1618b7fcc88d935bfd23f7a2f37843a` |
| independent_oracle.py | `13e45b5d3f0e08faa7418933fa159ac041bb0989877d1f18b3568759e74bbd85` |

The lead checked the invariant subspace W, its codimension bound, the
symmetry argument forcing both spectra into zero and one at equality, the
even-cap trace contradiction, binary odd-core attainment and the r=1
boundary. No proof gap was found within the stated characteristic-two,
corank-one, zero-primary-cap contract. The globally nilpotent interpretation
and its empty cap-four domain are kept separate.

The lead also reviewed the complete author verifier, README and source/replay
manifests and ran the committed-byte/mode preflight at the candidate commit.
No unresolved code or scope issue was reported. The exact source pins and
the original task card passed the package metadata validator.

The independent oracle was written by the lead without importing the author
engine or predecessor code. It computes characteristic polynomials by
determinant permutations and zero-primary indices by counting literal
kernel vectors, rather than the author's binary matrix powers and Gaussian
elimination. Complete binary censuses through dimension four and F4
censuses through dimension two agree with the theorem and with the author's
binary admissible counts. The two characteristic-polynomial implementations
both use the classical Leibniz formula; their mathematical method is not
claimed independent in that component. The power/elimination and literal
kernel-vector routes to the chain cap are distinct implementations.

All four registered warning-strict normal/optimized commands passed under
CPython 3.12.14. Official committed export and input-coverage integrity checks
passed. The exported files were made read-only and each engine was run
normally and with `-O`, from outside Git and with empty PATH. Each engine's
two stdout reports were byte-identical, and every exported file hash stayed
unchanged. Author runs took 2.061 and 1.965 seconds; independent-oracle runs
took 16.241 and 16.093 seconds. These are replay durations, not performance
claims. The optional source-history preflight refused the shallow checkout;
full-history ancestry validation is explicitly unclaimed.

These checks establish bounded corroboration and review evidence. All-field
and all-dimension quantifiers still depend on the written proof, and none
of the native caller, global invoice, supplier-admission or retained
framework obligations are discharged by this review.

## Extended version: cap two at every rank

The scientific extension is committed at
`40f45b8d26631c368b33be866f3c4f6eac04ec91`. The prior evidence above is
retained as a versioned record; the following hashes identify the extended
proof and both engines reviewed by the lead.

| Reviewed file | SHA256 |
| --- | --- |
| PROOF.md | `98688bca0d0d83961631cc9c02f9c6fdc2d8499bcba1dec4a82804bba0ffbae0` |
| verify.py | `ae11b07c17d53e69f2b806006ada31136e605f72dacffbc75ef1bdaddc775b7e` |
| independent_oracle.py | `978c965518f17b0abd85d4df58707e4d5374111e39815e0f40e8d386abe8eab6` |

The lead independently re-derived `D(A^2+B^2)D=D`, its rank consequence,
and the conversion `rank(X^2)=r-z(X)` under the zero-primary cap, including
r=1. The lead also checked `(A,B)=(0,D)` for sharpness and the dimension-three
cap-three counterexample. No gap was found in this complementary theorem.

The full scientific code diff was reviewed, including the generalized
coordinate endpoint mask, all-pair square compression checks, and the
independent oracle's flattened-coordinate diagonal updates. The latter
caches only its own separately computed determinant/literal-kernel profiles;
it does not import results from the author engine. No unresolved code issue
was reported. The expanded binary maxima and admissible-pair counts agree
between the two engines at every dimension and rank checked.
The worker added the all-rank loop around the lead's unchanged determinant
and literal-kernel routines; the lead reviewed that loop separately.

All four expanded registered commands passed in normal and optimized mode,
with 329,780 all-rank binary pairs and compression-identity checks, 594 new
general-rank attaining constructions, and fifteen rejection controls. The
independent oracle also covers 776 all-rank pairs over F4 through dimension
two. The earlier corank-one census and constructions remain in both engines
where applicable. Committed-byte and official export/input-integrity checks
passed for the extended scientific commit.

The expanded committed export was then replayed with read-only files and
empty PATH. Author normal/optimized runs took 3.122/3.400 seconds; independent
oracle runs took 11.277/10.739 seconds. Each engine's normal and optimized
stdout was identical, and every exported file hash remained unchanged.
These timings document verification duration, not a speedup claim.

The optional full-history limitation and all mathematical trust boundaries
stated above remain in force. This extension and its review establish no
native applicability theorem or selected supplier admission.
