# Independent exterior-algebra audit of the R420 frames

**Independent finite verification; no new kappa.** All 672 rational frames in
eumemic's selected PR543 bit word have orthogonal projectors with common
denominator 1, 2 or 4. An exterior-algebra implementation independently checks
their root-line closure and all 2,460 distinct nested pairs used by the word.
It also supplies exact witnesses that the listed root spans and incidences
survive reduction over every odd prime-power ring.

This corroborates the predecessor's finite geometry result by a different
method. It does not remove the other prime restrictions or the conditional
physical, recursive and analytic interfaces of the multiplication construction.
No defect in the selected word was found.

## Reproduce

From the repository root, with Python 3.9 or later and its standard library:

```sh
python3 -I -B research/r420-exterior-audit/verify.py
```

Expected output:

```text
PASS_R420_EXTERIOR_GEOMETRY: 672 frames; 2460 nested pairs; 258 positive oracles; 11 rejected controls
```

The command checks pinned inputs, recomputes every witness, runs the controls,
and compares the complete result with [CERTIFICATE.json](CERTIFICATE.json).
It does not write files. `--emit` prints the full regenerated certificate.
Only the decompressed word hash determines word equality, so recompressing
identical payload bytes is allowed. The original container hash is provenance.

## Exact result

| Quantity | Count |
|---|---:|
| Frames of ranks 0, 1, 2, 4, 6, 7, 8 | 1, 120, 180, 70, 180, 120, 1 |
| Projector denominator 1 | 28 |
| Projector denominator 2 | 100 |
| Projector denominator 4 | 544 |
| Primitive exterior squared norm 1, 4, 16, 64 | 28, 344, 268, 32 |
| Persistent-register moves in A, B, C | 1,649, 840, 451 |
| Distinct ordered nested frame pairs | 2,460 |
| Nonincident frame/root pairs checked | 66,240 |
| Retained copy frames | 9, each rank 8 |

There are no persistent-register moves in D, scatter or finalization. The
2,940 move occurrences agree with the predecessor's 29,874-record export after
subtracting 26,916 binary additions and 18 COPY/ERASE records. This audit checks
the retained frames and zero target frames at scatter, not the COPY/ERASE
operator or its restoration semantics.

For each frame, the certificate records a root basis, its exterior content,
the primitive exterior coordinates, their squared norm, the reduced common
projector denominator and a histogram of nonzero residual contents. Frame
records use the original frame-table order. A coordinate mask denotes the
increasing wedge of the corresponding axes. The stream record lists every
distinct ordered pair rather than only a digest or a sample.

## Method and finite implication

The word uses eight integer coordinates with inner product `dot/2`. Multiplying
the inner product by a nonzero scalar does not change an orthogonal projector.
All exterior norms and contractions below use the ordinary dot product.
The implementation imports no producer, rational elimination, Hermite reduction,
determinant, Gram checker or geometry cache. It uses integer wedge products and
contractions instead.

For a frame of rank r, append its listed root vectors to an exterior product,
skipping a vector exactly when its wedge is zero. Divide each nonzero result by
its coefficient gcd and normalize its sign. Root indices are ordered by
`(index - 83) mod 120`; reversing that order must give the same normalized
exterior vector w. This cross-checks two basis orders on every frame. The product c
of the discarded positive gcds is retained, so the selected basis B satisfies
`wedge(B) = +/- c w`. The empty basis has w=1 and c=1.

Let `D = sum_I w_I^2`. For each coordinate i, contract w with the i-th coordinate
vector, obtaining `a_i`. Set `N_ij = <a_i,a_j>`. Then `P = N/D` is the orthogonal
projector onto the frame. To see this, choose an orthonormal basis u_1,...,u_r
of its real span and write `w = alpha u_1 wedge ... wedge u_r`. The r products
obtained by omitting one u_k are orthonormal. Their contraction coefficients
therefore give `N_ij = alpha^2 sum_k u_ki u_kj` and `D = alpha^2`.
The rank-zero case gives N=0 and D=1. This argument establishes the identity;
the verifier checks its finite instances using exact integers.

The code reduces N and D by their common gcd, giving P=n/d, and checks
symmetry, `n*n = d*n`, and `trace(n) = r*d`. A listed root v lies in the frame
exactly when `n*v = d*v`. Testing all 120 roots for every frame proves closure
relative to this finite label set. A move from P=a/ad to Q=b/bd is nested
exactly when `b*a = bd*a`; the stream additionally requires a strict rank
increase for a changed frame. The source starts, target hyperplanes, helper
endpoints, D frames and retained-copy frames are checked separately.

Two extra witnesses justify reduction at every odd prime, without sampling
primes or assuming that positive rational determinants suffice:

1. Every c and D is a power of two. Cauchy-Binet gives
   `det(B B^T) = c^2 D`, so the Gram determinant for `dot/2` is
   `c^2 D / 2^r`. It is a unit over `Z[1/2]` and over every `Z/p^e` with p odd
   and e >= 1. Thus the actual listed basis spans a nondegenerate free
   rank-r direct summand there. Tracking c matters: primitive normalization
   alone would conceal an odd index in the supplied basis.
2. For each nonincident root, the gcd of the coordinates of `n*v-d*v` is a
   power of two. At every odd p at least one residual coordinate is a unit
   modulo p. A nonincident listed root therefore remains nonincident modulo
   p^e. Incident roots remain incident by the exact zero identity.

Since d is a unit at every odd p, the exact projector and nesting identities
also reduce there. In particular nested frames retain their ranks and split
orthogonally: for nested P and Q, Q-P is the complementary idempotent inside Q.
These statements concern this frame table and these 120 labels. They do not
assert that it exhausts all modular roots or establish any all-size compiler.

## Controls and verification boundary

The 258 positive oracles cover all 256 coordinate subspaces, an oblique line,
and a mixed-sign plane with an explicit projector. Eleven negative controls
reject a corrupted projector, an isotropic line at prime 3, a closed A2 frame,
a nondecomposable exterior vector, an odd-index basis, a new incidence modulo 3,
an omitted line, a duplicate line, a wrong target hyperplane, an illegal
phase-B descent and a nonzero D frame.

The A2 control uses the word's actual root indices `[0,16,23]`. Its rational
root-line set is closed, but its primitive exterior squared norm and projector
denominator are both 3. It demonstrates why rational closure and positive
Gram determinant alone would not justify the odd-prime conclusion. It is an
alternative frame, not a counterexample to the selected construction. The
odd-index and extra-incidence controls use synthetic vectors to isolate those
two logically separate obligations.

The finite domain is exactly the pinned 672 frames, all 80,640 frame/root
incidence tests, and all 2,940 persistent moves in the frozen stream. It is
exhaustive within that domain, with no search stopping heuristic. The assignment
seed changes the greedy basis order, not the covered domain.

This checker does not independently prove that the labels generate the E8
lattice, replay scalar XOR semantics, reconstruct hosted parents, price calls,
or validate coefficients, tapes, rounding or analytic transfer. Those remain
the predecessor's checks and inherited assumptions. This is an executable
finite certificate with a written algebraic argument, not a Lean proof or a
formal verification of integer multiplication.

## Provenance and credit

[SOURCE.json](SOURCE.json) pins the base commit
`66849e1475c930fd7732b1a0067ffee7e1e95f60`, PR543 source
`2065fe4f72a914d907f1046603f5a36f17018535`, reference files and word payload.
At that base, the [selected result](../../certificates/selected-result.json)
is #626 with #543, conditional kappa `51110230636731/31250000000000000`.
The [maintainer review](../../docs/research/community-k492-review.md) explains
the construction and inherited obligations. This package changes none of them.

Credit belongs to eumemic for the R420 word and its independent checker,
Dylan Crow for the E8 word/export and earlier Gram checks, and the supplier
lineage credited in the [PR543 README](../e8-bit-r420/README.md), including
DreamingOfClouds, Zhihao Chen and the shared-label work. Chafik Boukhalfa's #626
uses this bit supplier with the complex construction reviewed by Douglas
Colkitt. No predecessor code is copied or imported by the new verifier.

The [local claim](CLAIM.md) records the three candidates and overlap check.
Concurrent #707 and #709 accelerate existing geometry checks; #612 formalizes
boundary and scalar interfaces. This contribution instead reconstructs finite
geometry using exterior algebra and records the odd-prime incidence witnesses.
Those concurrent implementations are not dependencies.

The submission refresh covered 549 open PRs through #730. #718 studies split
target-read schedules, #726 studies A2 gather neighborhoods, and #729 audits
complex helper lifetimes. None supplies this exterior-coordinate frame audit.
The A2 control here is an independently derived prime-three obstruction, not
a gather construction or a claimed census result.
The final pre-submission metadata check also covered #731's binary compensation
kernel and #732's star punctures; neither studies these rational projectors.

## Local validation

The reproduction command passed on macOS arm64 with CPython 3.9.6 and 3.14.8,
including 3.9.6 with `-O`. The selected-record integrity check and the original
PR543 `xcheck.py` also passed. The latter independently retains its complete
660-column scalar replay and interleaved-interface checks.

A second AI-assisted implementation used rational Gram-Schmidt projectors and
Gaussian-elimination minors, with the listed root order rather than the seeded
order. It matched every frame's primitive exterior coordinates, norm, all 64
projector entries and residual-content histogram, and every used transition.
It also checked every emitted basis content by maximal minors. Its implementation
was a separate review experiment, not an additional committed checker.

Six in-memory implementation mutations were detected: wrong wedge signs,
omitted closure, omitted basis content, omitted residual-prime check, omitted
idempotence and reversed nesting. Recompressed word bytes reproduced the entire
certificate; changed payload bytes and a changed certificate were rejected.
Local Markdown links and staged whitespace were checked.

The repository-wide suite, selected cold replay, native cohort replay, Linux CI
and Lean were not rerun. This isolated package does not change their inputs or
claim their obligations as newly verified.

Prepared by **Sagar Thakrar / @thakrarsagar**, with substantial **OpenAI Codex
assistance** in implementation, mathematical checking and documentation.
New material is under Apache-2.0. Independent implementations here were also
AI-assisted; no independent human review is claimed.
