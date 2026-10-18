# R420 ghost-return obstruction and supporting frame certificates

**Independent verification and a scoped negative result; no new κ.**
The [ghost-return screen](GHOST-SCREEN.md) tests a specific application of
Ghost Parametrization: retain temporarily dirty source/helper state and defer
its restoration. The first target output remains correct, but the restoration
debt has rank 539. Helper-to-source drift has rank 120; setting only helper
register 251 makes an unchanged second call corrupt target 0. Even gifting
all 2,973 cleanup XORs leaves the paid child profile unchanged under the
original frame endpoints. The selected assembly remains complex-bound.

The supporting geometry audit was developed independently during the sprint.
Concurrent [PR #737](https://github.com/CrocSwap/integer-mult-bounds/pull/737)
by Sagar Thakrar submitted the same main exterior-algebra result first. We
credit that overlap; the distinct central contribution here is the concrete
ghost-return/carryover obstruction and its complete fixed-profile cost screen.
Our geometry receipt additionally enumerates every frame inclusion and
orthogonal complement, and remains supporting independent corroboration.

All 672 frames of the selected #543 bit supplier have exact orthogonal
projectors with denominators dividing 4. Their dimensions, root-line
memberships, inclusions and orthogonal complements survive reduction modulo
every odd prime power. This is certified by integer exterior products,
without importing the supplier's elimination, determinant or prime-witness
code. The checked finite certificate and the specialization argument below
are not a proof-assistant formalization or a full multiplication theorem.

## Reproduce

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 -I -B research/r420-exterior-frames/ghost_screen.py
python3 -I -B research/r420-exterior-frames/verify.py
```

Expected:

```text
PASS_R420_GHOST_RETURN_SCREEN: debt rank 539; 2973 gifted XORs; child profile unchanged; selected kappa unchanged; 2 rejected returns
PASS_R420_EXTERIOR_FRAMES: 672 frames; 80640 memberships; 28713 inclusions; 8 rejected controls; every odd prime
```

The additional screen and focused tests are:

```sh
python3 -I -B research/r420-exterior-frames/ghost_screen.py
python3 -I -B research/r420-exterior-frames/test_verify.py
python3 -I -B research/r420-exterior-frames/test_ghost_screen.py
```

The screen prints `PASS_R420_GHOST_RETURN_SCREEN`; the test scripts pass eight
and two tests respectively. Optimized Python (`-O`) retains all mathematical
checks. The verifier compares every field against [CERTIFICATE.json](CERTIFICATE.json).
`--output /new/path.json` writes a fresh checked copy; it refuses to overwrite.
`--word /path/to/recompressed.json.gz` accepts another gzip container only when
its canonical decoded JSON matches the pinned word. Nothing is regenerated
in the supplier, `upstream/`, or selected-frontier files.

## Pins and coverage

- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- #543 supplier: `2065fe4f72a914d907f1046603f5a36f17018535`.
- Word: `research/e8-bit-r420/data/bitE8mut-r420.json.gz`;
  canonical decoded SHA-256
  `e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2`.
- [SOURCE.json](SOURCE.json) records source hashes and Git blob IDs, including
  the unchanged reference checkers and #626 assembly used by the cost screen.
  The independent geometry checker consumes only the word.
- [CLAIM.md](CLAIM.md) records OS-random seed 78, the three candidate tasks,
  scope, time budget and overlap review. Seed 78 rotates the candidate root
  order for choosing bases; every frame and every root is still checked.

There is no adaptive search, timeout-based conclusion, or sampled coverage.
The domain is exactly the pinned 672-frame table and its 120 integer labels:
80,640 membership obligations, comprising 14,400 members and 66,240 exclusions.
There are 28,713 ordered inclusions (including 672 equalities), 422,871 ordered
noninclusions, and 336 complementary pairs. Symmetric projector idempotence
and complement identities each check 43,008 entries.

| Dimension | Frame count |
|---:|---:|
| 0 | 1 |
| 1 | 120 |
| 2 | 180 |
| 4 | 70 |
| 6 | 180 |
| 7 | 120 |
| 8 | 1 |

## Certificate and specialization argument

The form on the source labels is `dot/2`. Multiplying a nondegenerate form
by a nonzero scalar does not change its subspaces or orthogonal projector,
so work with the ordinary dot product until reduction; 2 is invertible at
every odd prime.

For each frame, append the root vectors in seed-rotated order to an exterior
product. A zero product skips a dependent root. Divide each nonzero product
by the gcd of its integer coordinates and fix its sign. The resulting
primitive blade B, the selected root IDs and every removed gcd are in the
certificate. Masks encode increasing exterior basis indices. This calculation
uses alternating products and integer gcds, not a rational echelon basis.

Put `S = <B,B>` and `N_ij = <ι_i B, ι_j B>`, where `ι_i` contracts with the
i-th coordinate vector. For a nonzero decomposable d-blade, the orthogonal
projector onto its span is `P=N/S`. One proof chooses a real orthonormal basis
of the span: the formula becomes the sum of its d rank-one projectors and is
independent of the chosen basis. This gives the rational identity as well.
For d=0 the contractions vanish; for d=8 the projector is the identity.
The checker independently checks symmetry, `N²=SN`, `trace(N)=dS`, and both
membership tests `B ∧ u=0` and `Nu=Su` on every source label u.

All removed gcds are 1 or 2. If their product is c, the wedge of the selected
*original* roots is `±cB`. Cauchy–Binet therefore gives the original basis's
dot-Gram determinant `c²S`. The 672 values of S are 1 (28 frames), 4 (344),
16 (268), and 64 (32). Thus those Gram determinants are units modulo every
odd prime power. This also proves the selected roots remain a free basis of
a nondegenerate direct summand of the same dimension there: the inverse Gram
matrix gives a left inverse and the orthogonal projection. Dividing by the
normalization contents has introduced no hidden odd-prime restriction.

For every excluded root u, the nonzero integer vector `Nu-Su` has gcd a power
of two (between 1 and 64). Consequently it cannot vanish modulo any odd prime,
or modulo any power of that prime. Every included root satisfies an exact
integer zero identity. Root membership is therefore identical after reduction.
Because each listed frame is generated by its listed roots, this preserves
*all* frame inclusions and noninclusions, not just the pairs counted by a
finite-field replay. The checker also finds each perpendicular frame and
checks `P_F + P_(F-perp) = I` entrywise; this identity reduces over the same rings.

The reduced projectors have common denominators 1 (28 frames), 2 (100), or 4
(544). These are address-label statements over odd-characteristic rings;
the bit **payload** XOR arithmetic is still over F2. No claim excludes F2
payloads or proves the complete q-adic compiler/bad-class interface.

## Controls and independence

Eight controls run the mathematical predicates directly, bypassing source
hashes: remove a redundant root from the full frame; corrupt a projector's
diagonal; double its denominator; change its dimension; make a symmetric,
trace-preserving idempotence error; insert an A2 plane with an odd bad prime;
scale an in-frame generator by 3; and scale an outside root by 3. The latter
two isolate restrictions invisible to rational projector equality alone.
They are deliberate modified inputs, not alleged production defects.

The actual A2 plane uses source roots 0, 73 and 78. Its primitive squared
blade norm is 3. It passes the rational closure/projector checks but has
nonzero radical `(0,0,0,2,2,0,0,1)` modulo 3. The full witness is in the
certificate. Thus **the conclusion does not cover arbitrary E8-root spans**.
Positive controls preserve the projector under generator rescaling and the
primitive blade under a different basis order. The tests additionally check
all 512 binary 3×3 exterior determinants against a signed-permutation oracle,
all 672 frames in unrotated order, and source/receipt corruption behavior.

eumemic's #543 `xcheck.py` already checks rational closures by nullspaces.
Dylan Crow's exporter and Gram checker use echelon bases and the inherited
Bareiss/prime-witness engine. This is a separate implementation of related
obligations and supplies explicit projectors and all-odd-prime-power root
exclusions. Concurrent #707 accelerates that Bareiss engine on these same
frames; no code from #707 is used. #612 checks source boundaries and scalar
interfaces in Lean; #661 concerns fixed-order frame optimization. Those
scopes are credited and are not reclassified as unfinished by this audit.

Submission overlap review also credits #710's shorter restored cleanup and
its unchanged-child-cost observation, and Joshua Snider's #731 compensation
kernel audit. The latter studies helper-to-target compensation K, whereas
this screen studies helper-to-source drift in U. Complete cleanup omission,
the unchanged-second-call counterexample and the inherited #626 grid ceiling
are the additional scope here. Reviewed heads: #737
`b41e73169430641be18c988c659d2855a6a6218a`, #710
`d97c8d20a8b885271a24c5a4e8446ac7f5697d5c`, #731
`cf5ff54a358b400a7e69abe941d1d0ad0944b25e`.

## Limits and credit

This package proves no improved circuit, hosting schedule, optimum, or new
exponent. It does not certify fresh all-size compilation, common-label or
mutable-basis realization, full whole-call hosting, q-adic selector density,
precision, tape, exact recovery, or analytic transfer. Those remain inherited
from the selected construction. In particular the dyadic certificate does
**not** authorize deleting the bit bad-class surcharge.

See [NOTICE.md](NOTICE.md) for predecessor attribution, the auxiliary-state
motivation, Apache-2.0 licensing, and substantial OpenAI Codex assistance.
Validation commands and their actual outcomes are in [VALIDATION.md](VALIDATION.md).
