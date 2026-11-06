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

## Prior extension: cap two at every rank

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

## Complete all-rank, all-cap classification

The complete scientific integration is local commit
`25a96f015b33586a0df84b15696f75ff6e7d8d0f`. The earlier two stages were
published together at `31177ed748a99428537cb3b4423a88ece07132a8`; the prior
candidate IDs above identify local review snapshots. Their exact file hashes
remain the portable scientific bindings. This final stage replaces the two
sharp slices by the complete formula while retaining their evidence history.

| Reviewed file | SHA256 |
| --- | --- |
| PROOF.md | `a36b3197b005c0e1583691b116aec620e77f33c4de845e77c2fda5223ca486de` |
| verify.py | `30e729a7e85facd79fdf120a891e6663918be61ad52d1f92171094a27069d5e5` |
| independent_oracle.py | `a90fa95f357ae53aa973e092aad6b86aad7f4c947e3f25c79bf7fdf3a95a3a82` |
| gf4_oracle.py | `17af018d37d47a79a36088ba14fa9190788f7bb62c29a47177f3b17a9871e0b2` |

Worker B separately derived the injective intersection map for every even
cap, beyond the lead's initial power-of-two argument. Its scratch derivation
had SHA256 `03dc4e2be4c655b4a4f50691dfe0051cfa388506b5eab573144b8e40803b5f09`.
Worker A supplied the rank-s odd-cap argument, greedy bounded odd-core
attainment and integrated package. Both B and C independently reviewed
the complete proof hash above. The lead independently reviewed the same
mathematical argument and the constructor; no unresolved gap was reported.

The reviews explicitly checked the order of the telescoping identity,
the use of E squared equals E, the even binomial coefficient, invertibility
only on ker A^m, and the fact that the intersection itself need not be
invariant. They also checked the trace bound, odd-cap invariant subspace,
rank/dimension allocation, zero/full-rank and r=1 boundaries, and the
globally nilpotent existence criterion. These are independent AI reviews,
not human, external literature-priority or formal proof-kernel acceptance.

Worker C independently enumerated every binary matrix/rank/cap through
dimension four using a fresh column-action/kernel-growth engine. Its
maxima agreed with the theorem in all forty cases. C also inspected the
constructor and independently measured 184 constructed pairs at dimensions
1,2,3,4,5,8,12,16,33; every endpoint, cap and objective passed. These
measurements imported only constructed matrices, not author spectral
calculations. That check bound author hash
`b90d567388c9c191070469c7d208a0bb987383a4c04d0a3f78e4c4968ba8ee19`;
the only subsequent author-code change corrected the top docstring from
corank-one to all-rank scope, yielding the current hash above.

C's independently written packed F4 engine covers every rank and cap
through dimension three. Its package adaptation changes only the time
guard and deterministic read-only reporting. C compared every maximum,
eligible count, witness and arithmetic control with the original complete
receipt in normal and optimized mode: exact agreement, with byte-identical
stdout between modes. The lead reviewed both independent engines and the
complete author verifier, including generalized endpoint masks and all
declared coverage. No unresolved code issue was found.

All six final warning-strict registered commands passed on the scientific
bytes above. The author engine checks 329,780 ordered pairs, 1,316,964
pair/cap cases, 66,066 independent polynomial comparisons and 13,090
attaining constructions. The packed F4 engine adds 1,049,352 ordered pairs.
Binary maxima and admissible counts agree with the separate literal-kernel
oracle. Metadata/source pins, exact committed bytes and official export
integrity passed for the scientific integration commit.

Worker D separately checked the existing #5507 caller fixture and confirmed
that its helper extends the required native length-two chain to a length-three
zero chain. The README therefore requires a separate cap applicability proof;
no caller or supplier consequence is asserted. That check preserves the
predecessor's credit and full funding result. The current source manifest
pins the exact #5507 proof used for this scope boundary.

The committed complete export was replayed with read-only files, no Git
context and empty PATH. All six commands passed; each engine's normal and
optimized stdout reports were identical, and every exported file hash
remained unchanged. Author runs took 7.519/6.592 seconds, the literal-kernel
oracle 11.270/9.576 seconds, and the packed F4 oracle 1.323/1.604 seconds.
These are validation durations, not performance-improvement claims. The
optional full-history check remains unavailable in the shallow checkout.

A final bibliography-only correction uses the publisher's exact title,
*On the Representation of an Idempotent as a Sum of Nilpotent Elements*.
The complete proof was reviewed at SHA256 `094ed54fb6f1ede66ec356512cb33fc89402382c43422ae49740f2488d3947e0`;
removing the extra word from the citation yields the current proof hash in
the table. No mathematical text, formula, constructor or verifier changed.
