# A diagonal obstruction to rank-seven helper408 extraction

For the two pinned PR2894 providers carried by PR2908, helper408 cannot be
isolated and restored at its original rank-seven last frame by the proposed
scalar input/output basis changes. This remains impossible when protected
terminal helpers are generously made available. The decisive certificate is an
11 by 11 diagonal forbidden-input minor with determinant `-1/4`.

This is a fixed-word, fixed-entrance, fixed-terminal-support obstruction. It
does not exclude a changed middle word, changed source access, additional
intermediate operations, or a different endpoint. There is no new supplier and
no new kappa claim.

## Exact premises

The source scientific pins are PR2908 head
`51309592971e3b5be935599eed2a95404dc7781e`, containing the PR2894 providers at
`18d03c447886895ef9abf888398178e0428533ca`. The shared research base is
`475fec190d5ad746bd4690574dca30d6901acdaf`. Source bytes, provenance and their
independent integrity gate are recorded by the surrounding package.

| Provider | SHA256 of compressed source bytes |
| --- | --- |
| `PARENT-base.json.gz` | `c20a470aec0f3e61833cb41fe190639eb358f58017143d2336c55c80fba265eb` |
| `PARENT-extra.json.gz` | `db34e39876241087b581ed9374c53e9cd393e3e86ef6103bfb54f3077c3d2761` |

Work over the dyadic ring `Z[1/2]`, enlarged to `Q` for the complete linear
space computation. Every live data/helper input is arbitrary and independent;
no helper is assumed initially zero. A zero entrance *frame* does not mean a
zero value. The non-target coordinates are

```
L = {0,...,703} \ (removed union {112,...,223}),   |L| = 520.
```

`M` is the complete non-target middle operator: `A[prelude_events:]`, followed
chronologically by `B` and all its inserted warps, followed by `restore`,
omitting exactly the target writes. Each warp is its own invertible formal
generator, multiplied on the left. Only adjacent inverse cancellation is
allowed. No source auditor or source `structure.py` is imported. The exact
replay uses 4,583 gates and produces 11,912 nonzero free-word terms.

Let `P` be the union of `helper_final`, `start_extra`, and initial-correction
source registers. The allowed input coordinates are

```
H = {r in L : r >= 224 and r not in P},   |H| = 226.
```

Input basis changes `S` are arbitrary invertible scalar changes inside `H`,
extended by the identity elsewhere. In particular, existing 72 cold helper
entrances, nonzero entrance frames, and operator-correction sources stay
protected. The checker also verifies that no prelude warp lender lies in `H`.

The proposed helper408 entrance/terminal pair is

```
(empty, E7),    E7 = span_GF(2)(256,128,66,36,22,8,1).
```

If a supplier existed, its physical residual would be the paired operator
`T_native(E7) T_native(empty)^-1`. No native factorization or phase identity
for this residual is assumed or certified here. The symbol `T` below denotes
the proposed *scalar output basis change*, not this native residual.

## Deriving the terminal support

Replay the entire literal frame chain, including all `A` incidents, target
writes' source incidents, the 24 prelude warps, all 72 `B` warps, and the
`restore` incidents. Scalar incidents must be monotone; a warp checks its
recorded incoming frame and replaces it by its recorded outgoing frame. A
union of all historical frames would be incorrect across these resets.
The replay covers 10,456 scalar register incidents.

Let `F_r` be the frame after `restore` and before the prescribed final climbs.
Every register available to an appended scalar gate at `E7` must satisfy
`F_r <= E7`. Thus the maximal relaxed non-target support is

```
R = (105,307,309,314,369,371,373,378,408,572,573).
```

The following are the derived last frames; the list is complete.

| Registers | Last frame basis |
| --- | --- |
| 105, 408, 572, 573 | `(256,128,66,36,22,8,1)` |
| 307, 309, 314 | `(385,74,44,30)` |
| 369, 371, 373, 378 | `(392,67,37,22)` |

The nine registers in `R \ {105,408}` are existing cold helpers. Allowing
arbitrary terminal mixing on them relaxes the requirement that those existing
extractions survive. A negative result for this larger `R` therefore also
applies with the original cold-helper protection enforced. Ordinary data
register105 is likewise allowed. Target registers are excluded throughout.

## Necessary paired identities

Write the desired isolated helper as `h=408`. If scalar changes `S,T` produce
both an identity column and identity row on that helper, define

```
v = S e_h,           alpha = e_h^T T,
y = M v,            u = alpha M.
```

Then `v,u` are scalar supported on `H`, `y,alpha` are scalar supported on `R`,
and `alpha y = u v = 1`. Indeed, the row identity
`e_h^T T M S = e_h^T` already gives
`alpha M = e_h^T S^-1`, which is supported on `H` and nonzero.

The complete rational spaces checked here are

```
V = {v in Q^H : Mv is scalar and supported on R},
A = {alpha in Q^R : alpha M is scalar and supported on H}.
```

They have dimensions zero and zero in both source variants. The forward
system has 608 nonzero coefficient equations and rank226; the dual system has
17 nonzero coefficient equations and rank11. Consequently the full pairing
matrix on their bases is empty and zero. This is exact rational elimination,
not a random or modular rank estimate.

## Small certificate: every terminal readout vanishes

The full space computation is corroborating evidence. The following minor
alone proves the obstruction. In the order of `R` above, take the forbidden
input columns

```
J = (14,307,309,314,369,371,373,378,41,572,573).
```

Every member of `J` is outside `H`: 14 and 41 are data inputs and the others
are protected cold helpers. Exact free-word replay gives

```
M[R,J] = diag(-1/2,1,1,1,1,1,1,1,1/2,1,1),
det M[R,J] = -1/4.
```

All off-diagonal polynomials are zero, and all diagonal polynomials are the
displayed scalars with no nonempty operator words. Thus, for a readout
`alpha` supported on `R`, the requirement that `alpha M` be supported on `H`
forces

```
-alpha_105/2 = 0,       alpha_408/2 = 0,
alpha_r = 0 for r = 307,309,314,369,371,373,378,572,573.
```

Hence `alpha=0`, contradicting the required unit pairing or merely the
nonzero row identity. The determinant is a unit in `Z[1/2]`; no odd-denominator
normalization is used. The obstruction remains valid over `Q` and for every
representation of the frozen free-operator word on a dyadic module. Because
the minor is already a scalar identity, this conclusion does not depend on
distinct nonempty free words remaining independent after specialization.

The two source files were independently loaded and replayed. Their complete
non-target middle operators compare equal, with canonical term-list SHA256
`d1c29a23fbe07da932c44d9e9b1467ab866894faac115d456eae8e42069aec68` under the
encoding in `operator_digest`. Neither equality nor one variant's result is
assumed when checking the other.

## Positive calibration and invalid controls

The existing PR2908 rank-eight `E52=(256,128,64,36,20,8,2,1)` certificate is
reconstructed from its 24 input gates and three output gates. The checker
derives `S,T,v,u,alpha,y` and verifies all seven displayed identities:

```
S e408 = v,       u S = e408^T,       M v = y,
alpha M = u,     alpha y = 1,        T y = e408,
e408^T T = alpha.
```

In particular it obtains `y=2 e42` and
`alpha=e408^T+(1/2)e42^T+e105^T`, with unit pairing. Its explicit `v,u` are
included in the checker output. Register42 has last frame `E52`, so it is
unavailable at `E7`. This explains a concrete capability lost by the proposed
smaller endpoint.

The following changed candidates are each rejected for an actual failed
equation or support requirement in both variants:

| Changed candidate | Failed obligation |
| --- | --- |
| Change known `v_226` from `1/2` to `1` | `Mv` scalar/support requirement at E52 |
| Change known `alpha_42` from `1/2` to `1` | `alpha M` scalar/support requirement on H |
| Claim the unchanged known E52 pair at E7 | Terminal readout support: register42 is outside R |

These are algebraic or frame mutants of a valid witness. No checksum failure
is counted as a mathematical negative control.

## Cost consequences and remaining boundaries

There is no changed word and therefore no realized local cost change. The
proposed saving fails before target-compensation changes, native lowering,
cleanup regeneration, owner assignment or recursive admission can be
constructed. None of those obligations may be waived by this obstruction.

For the favorable screen declared before computation, an ideal extraction
would remove helper408's rank-two terminal climb from the PR2894 profile,
change its width9 to width7, and require a 73rd private zero buffer. Relative
to PR2908's actual rank-eight extraction, which already pays that buffer and
has local delta `+3 H1 - 2 H2` from PR2894, the optimistic local child-count
delta would be `-3 H1 + H2` per supplier call. There are 666 calls; every
other local child, all eight center H8 children, every bridge and every owner
residue remain charged. If `k_b` copies of helper408 are present in owner bin
`b`, shrinking each width8 to width7 changes its idle rank from `r_b` to
`r_b+k_b`, not necessarily only by one. The favorable raw moment delta is

```
666 * (-3 * 1^p + 2^p) + sum_b ((r_b+k_b)^p - r_b^p),   0 < p < 1,
sum_b k_b = 666.
```

This is only the unrealizable favorable budget being screened, with added
terminal climbs, scalar compensation, inverse cleanup, native conversion,
routing, precision and stock changes still owed. The parent package owns the
literal owner-bin verification and full cost ledger. Physical families would
be `66304+408+8+73+2=66795` if no further scratch were needed; this count does
not certify a new supplier. No native phase, chronological owner realization,
all-size recurrence, precision, machine or outer theorem follows here.

This finite exact computation has a short written linear-algebra implication
for arbitrary dirty inputs and arbitrary allowed scalar basis changes. It is
not a formal-kernel proof and is not a classification of other words or
endpoints. In particular, a source-partner recovery that changes `H`, a
changed middle `M`, or altered incident frames would invalidate one of the
explicit premises and would require its own proof and full invoice.

## Reproduction and credit

From the repository root, using only Python's standard library:

```sh
python3 -I -O -B research/helper408-rank7-pairing/verify_boundary.py
```

Expected terminal status: `PASS_SCOPED_RANK7_OBSTRUCTION`. The checker also
prints the complete support sets, dimensions, diagonal certificate, source
digests, positive calibration and the three rejected mutants for each
provider. Its source hashes authenticate the input bytes; its exact checks use
explicit exceptions and remain active with Python optimization enabled.

The paired boundary construction and E52 calibration are credited to Jeremy
Diviney (PR2908). The input providers and chronological frame conventions are
credited to Jeremy Kothe (PR2894 and PR2833), with the retained Yiyang Lu
(PR2857), Dugongue (PR2863), Marius-Paul Dumitrean (PR2843/2802), Philippe Van
Velzen (PR2853), Tekalign and exact/native lineage credits in the surrounding
package. This new scoped obstruction and independent standard-library checker
were prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0.
