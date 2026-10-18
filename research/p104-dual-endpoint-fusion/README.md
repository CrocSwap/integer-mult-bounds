# P104 physical-dual endpoint fusion

The ordinary physical inverse-transpose in [PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586)
charges 416 rank-one endpoint conversions separately. **128 of them can be
fused with a neighboring transport**, preserving the complete physical map,
all 3,104 ADDs in their original order, all 150 dirty helper values, and all
eight exact zero erasures. This answers its first open question in a bounded
rewrite class. The 104 X entries, two Y entries, 78 X exits and 104 Y exits
that remain are blocked by ADDs, including source reads.

This is a finite construction and a scoped optimum, with author-checked exact
evidence. It is not a complete supplier or a new kappa. The predecessor corrects
only two of the 104 forward target rows; this work preserves that boundary.

| Local quantity | PR2586 | Fused word |
| --- | ---: | ---: |
| Events | 5,398 | **5,270** |
| Positive transports | 2,070 | **1,942** |
| Transport rank mass | 3,542 | 3,542 |
| Scalar ADDs / signs | 3,104 / 208 | 3,104 / 208 |
| Private zero initializations / zero erasures | 8 / 8 | 8 / 8 |

The new complete transport profile is

```
1504 H1 + 58 H2 + 74 H3 + 93 H4 + 57 H5 + 57 H6 + 91 H7 + 8 H8.
```

There are 102 Y-entry and 26 X-exit fusions. Their old middle ranks
`r = 2,3,4,5,6` occur `16,28,39,30,15` times respectively. Each replaces
`H1 + Hr` by one `H(r+1)`. Twenty-six scalar signs receive updated chart
annotations when the fused transport is delayed; the physical sign is unchanged.
Rank mass does not fall. For every `0 < p = 1-a < 1`, however, the local
normalized child sum strictly decreases by

```
sum_{r=2}^6 n_r ((r+1)^p - r^p - 1) / m^p < 0.
```

This comparison fixes the caller width and all charges outside these segments.
It is not a complete recursive moment: chronological owners, idle/residual
children and physical scalar/address costs have not been priced here.

## Exact scope and proof

An **endpoint run** consists of the endpoint conversion and all consecutive
transports or scalar signs on that register, stopping at its first ADD when
read from the corresponding boundary. Both the source and target of an ADD
are barriers. Events on other registers may commute past the run. We retain
all nontransport operations, their order, and their physical maps; only scalar
sign chart annotations may change. No ADD conjugation or cross-register
resynthesis is permitted. There are 416 such runs in this fixed word.

The two-edge runs are exactly the 128 reported above. All are increasing
`A -> B -> D`, with `A` a subspace of `B` and `B` a subspace of `D`, and one
edge has rank one. In the predecessor's conjugated canonical charts
`Delta_W = conjugate(Gamma_W)`, their physical composition is exactly

```
(Delta_D Delta_B^(-1)) (Delta_B Delta_A^(-1))
    = Delta_D Delta_A^(-1).
```

This equality includes phase. A scalar sign `-I` commutes with either
transport. Delaying the composite to the second event therefore requires the
intervening sign to be annotated at `A`. There is no other use of the register
between the two transports. Disjoint events commute, so these 128 rewrites
compose without affecting any ADD or private operation. `model.fuse` checks
these conditions at every source event, and the verifier uses a separate
one-pass dependency scan to corroborate all 128 pairs and all 288 barriers.

The initial and final frames are literally unchanged. Thus the rewritten
program has precisely PR2586's physical map
`Delta_f S^(-T) Delta_i^(-1) = F^(-T)`, under its original canonical boundary
convention. Transpose here is ordinary bilinear transpose, not adjoint.
The logical matrix fixes Y and all dirty helpers and maps
`X_s -> X_s - sum_t C[t,s] Y_t`, where the first two rows of C are identity
rows and the other 102 are Gram/2 rows. A new sparse rational interpreter
checks the original and fused words against that matrix on all 358 independent
public columns, including every zero coefficient. It checks common frames at
every ADD and exact zero at every private erasure. The E8 port coordinates are
reconstructed from the authenticated fixture, without predecessor executables.

### Optimality inside these endpoint runs

Write a Clifford's binary symplectic matrix in blocks, and let `b(U)` be the
rank of the block carrying input Z coordinates into output X coordinates.
The retained Gaussian monomials have `b=0`; a rank-r positive child has `b=r`.
Block multiplication gives

```
b(UV) <= b(U) + b(V).
```

Consequently any implementation of a fixed run using arbitrary such monomials
and paid children of ranks `r_j` has `sum_j r_j >= b(run)`. This remains true
with any number of children and either orientation. For `0<p<1`, subadditivity
of `x^p` gives `sum_j r_j^p >= (sum_j r_j)^p >= b(run)^p`.

The independent native interpreter computes the intrinsic block rank of all
416 runs. It is one for every blocked run and `r+1` for every fused run.
The existing H1 or the newly compiled single H(r+1), with Gaussian monomials,
attains both bounds. Thus the endpoint-run minimum is

```
288 H1 + 16 H3 + 28 H4 + 39 H5 + 30 H6 + 15 H7,
rank mass 928, one positive child per run.
```

The other 2,614 rank units are retained. This proves rank-mass and child-moment
optimality **only in the stated independent endpoint-run rewrite class**.
Crossing an ADD with an explicit compensated operation, changing its order or
using additional register interactions is outside the theorem. It is not an
unrestricted lower bound on the physical dual or its 416-conversion surcharge.

## Reproduce and evidence

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -O -B research/p104-dual-endpoint-fusion/verify.py
python3 -I -B research/p104-dual-endpoint-fusion/verify.py --regenerate
python3 scripts/research_package.py --package research/p104-dual-endpoint-fusion
```

Expected summary:

```
PASS_P104_DUAL_ENDPOINT_FUSION pairs=128 blocked=288 transports=1942 rank_mass=3542 columns=358 native=128 zero_erases=8 controls=9 no_new_kappa
```

[WORD.json](WORD.json) is the complete literal candidate; [NATIVE.json](NATIVE.json)
contains all 128 new native recipes and their exact event occurrences.
[RESULT.json](RESULT.json) records the complete recount and run census.
Default replay is read-only and checks the entire typed receipt and regenerated
word. `--regenerate` also invokes the authenticated retained Clifford compiler
and compares the complete native payload. `--out NEW.json` writes exclusively.

The default checker imports neither that compiler nor PR2586's builder/checker.
The credited independent Gaussian interpreter checks each new recipe against
both its direct chart operator and the two literal old transports: 256 signed
Pauli and exact-phase comparisons. These determine each entire 512-address
operator, not only its action on one sample. The phase check supplements the
Pauli action because that action alone cannot detect a global scalar phase.
All 416 intrinsic ranks are checked with a separate binary elimination routine.

Nine semantic controls reject wrong global phase, rank, missing recipe,
occurrence binding, fusion across a source-read ADD, stale sign frame, an
omitted sign, private cleanup and a public correction coefficient. An equivalent
binary frame basis is accepted. The behavioral checks cover regeneration,
optimized Git-free read-only replay, typed receipt drift, source authentication
before executable import, and exclusive output. These are author checks,
not independent human review or a proof-assistant certificate.

## Limits

The native identities for unchanged transport implementations are inherited
from PR2586; its entire 1,245-recipe native replay is not repeated. The new
operator identities and exact equivalence rewrite are checked directly in
canonical charts. No selected cold replay, rounded-child execution or full
multiplication proof is claimed. Exact zero erasure does not establish a
rounded erasure contract. Intrinsic caller adapters, decreasing-edge hosting,
private storage, idle/residual charges, precision/tape, all-size admission and
the other 102 forward corrections remain open. The selected record is unchanged.

## Open next questions

Can a blocked X-entry or Y-exit conversion cross one ADD with a fully charged
conjugated source/target operation and lower the total bill? First use the
X0 entry's recorded ADD barrier or Y0 exit's final source read, derive the full
two-register operator, and compare native ranks with the preserved physical
boundary. A plain commute is invalid; the correction operation and its rank
are the missing ingredient. This changes the bounded rewrite class above.

Can the fused word be hosted with its rank-3 through rank-7 children and the
decreasing boundary conversions? Start with one concrete owner window and
retain every private return/erase obligation. A full hosted invoice and rounded
storage contract are needed before translating the local moment improvement
into a supplier claim. Structured questions are in [TASK.json](TASK.json).

## Credit and provenance

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex (GPT-6 Astra) performed the derivation, implementation, checks and
writing. No independent human review is claimed. Apache-2.0.

The claim is in [discussion #2619](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619).

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
PR2586 is pinned at `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`.
[PREDECESSORS.json](PREDECESSORS.json) records exact retained bytes, Git blobs
and hashes; [SOURCES.json](SOURCES.json) authenticates live inputs. Only the
source word, its receipt and attribution-bearing README are retained from that
PR. The original native implementation and physical-dual theorem are credited
to ywz65/PR2586, with PR2497's clean logical dual and PR2551's boundary distinction.
Nick Petalas/PR2550 supplies the complementary-frame idea.

Retain credit to Ross Richardson/PR2445; commdata2338/PR2393; Hiroki Kumazaki;
Philippe Van Velzen; Chafik Boukhalfa/PR1991; Rohan Arun/PR1972; Adam Gall/PR1940;
Josie Elliston/PR1071; Ali Romman/PR1125 and PR1862 (the independent interpreter);
and icekylinx/PR531 and the retained compiler lineage. Standard Clifford block
rank and concavity inequalities are used, not claimed as new mathematics.
The contribution is their exact binding to these 416 endpoint runs and the
complete changed native word/profile.
