# Paired-plane factorization: a scalar endpoint obstruction

**Scoped negative result, not a universal plane-port lower bound. No new kappa.**

At PR1825 head `d16fb8936795ff101e4d2f63cfdc6a25066ebabf`, the published
binary factorization is correct, but it is not a scalar decoder for the proposed
two-unpaid-coordinate endpoint. The obstruction already occurs on two ports.
It also rules out every **parity-preserving integral lift** of those binary
factors, even with arbitrary zero-copy endpoint corrections. It does not rule
out a different rational/complex decoder, paid cancellation, or another call
contract.

## Why the coverage law needs this check

The selected construction has one unpaid direction `q` per live data family.
The inherited exact geometry specifies initial source level `C_q`, target level
`I`, and final levels `C_all` and `C_all C_q^-1`. After the signed exchange, the
source datum would have operator `C_all C_q^-2 = C_all X_q`; the charged terminal
translation `X_q` removes it. The direction is not simply left unadvanced.
The other 72 directions are partitioned between data climbs, hosted helper
residuals and idle children, giving the incumbent mass `72W + 64N`.

Source: [inherited geometry](../split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt),
lines 53–69 and 71–90; [hosting proof](../idle-axis-hosting/PROOF.md), sections 1–2.
The verifier binds the selected archive and checks `terminal_Y_translation == q`
for all 112 selected ports. It does not independently recensus every hosted
family. The all-family partition and plane-port endpoint were already reported
by ctoth and collaborators in [Discussion1587, comment18914510](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18914510).
They retain priority for those results.

Replacing the line by an orthonormal plane `E=<q,r>` gives the valid local
correction `C_E^2=X_(q+r)` and suggests mass `71W + C N`, **provided the scalar
data endpoint is implemented exactly and every replacement charge is included**.
A terminal translation acts inside a single port. It cannot remove a nonzero
linear dependence of target port `i` on the wrong source port `j`.
That is the endpoint obligation audited here; no optimistic moment is priced for
an invalid scalar map.

## The two different matrices

Let the selected labels be `q_i in F2^9`, and let `E_i` be the shared plane of
port `i` and its matched partner. The proposed contract is source
`E_j -> FULL`, target `0 -> E_i^perp`. An endpoint cross-addition is rank-zero
only if `E_j <= E_i^perp`, equivalently all four pairings between bases of
`E_i` and `E_j` vanish. Therefore a normalized scalar decoder `K` must obey

```
K_ii = 1,
K_ij = 0 for i != j whenever E_i and E_j are not orthogonal.
```

Only entries on orthogonal-plane pairs may be repaired freely. A different
common nonzero diagonal normalization, such as the inherited `4`, does not
change the required off-diagonal zeros. This is the plane version of the
inherited scalar fitting condition in
[complex-rank8-decoder-rigidity/PROOF.md](../complex-rank8-decoder-rigidity/PROOF.md),
lines 11–16 and 28–34. In particular, because `q_i in E_i`, the weaker necessary
condition `K_ij=0 whenever i!=j and q_i dot q_j=1` holds independently of how the
second plane directions are chosen.

PR1825 instead proves over **F2** that

```
D T^transpose = B0,       B0_ij = q_i dot q_j.
```

`B0` records label incompatibility; its off-diagonal ones are not the desired
scalar coupling. Both the required target matrix and the field of addition
matter. Replaying the complete 12,544-entry binary identity is a positive
control here, not evidence against that identity.

## Exact source-bound counterexamples

The package retains the unmodified PR1825 certificate. The selected labels
come directly from the pinned selected replay archive, not from an independently
chosen E8 numbering. Expanding the published nine rank-one and seven rank-two
queries yields **23 binary scalar column pairs**. Regard each bit coefficient
literally as integer 0 or 1, and form their ordinary outer-product sum `H`.

### Ports 0 and 7: robust to every parity-preserving integral lift

```
q_0 = 11,       E_0 = span(11,19),
q_7 = 21,       E_7 = span(21,446),
q_0 dot q_7 = 1,
H[{0,7},{0,7}] = [[7,5],[5,7]].
```

Thus the coefficient from source 7 to target 0 is **5 instead of 0**.
With source 7 equal to 1, all other sources zero, and arbitrary dirty target 0
initially 11, the literal scalar interpretation returns 16, whereas any exact
portwise endpoint must leave that target at 11. This conclusion does not depend
on the required diagonal normalization. The verifier separately replays all
112 source-basis and 112 target-basis columns of the scalar layer, so preservation
of preexisting target dirt is checked rather than assumed.

**Integral-lift obstruction (written proof).** If integral matrices `D',T'`
reduce modulo two to the certified `D,T`, then

```
(D' T'^transpose)[0,7] = B0[0,7] = 1 (mod 2).
```

It is odd, hence nonzero over Q or C. Any zero-copy endpoint correction is zero
at this nonorthogonal pair, so cannot change that coefficient. The same argument
applies to every off-diagonal one of `B0`: **6,608 ordered pairs**. Signing binary
ones or changing coefficients by even integers does not evade the obstruction.
A common nonzero rescaling of the resulting scalar map cannot turn its nonzero
cross-entry into zero either. Arbitrary rational coefficients that do not retain
this integral reduction are outside the statement.

### Ports 0 and 1: the old line mask is also insufficient

The matched ports have `q_0=11`, `q_1=19`, so their lines are orthogonal, but
`E_0=E_1=span(11,19)` is nondegenerate and is not orthogonal to itself.
The literal sum has `H[0,1]=4`. Its binary reduction is zero, yet a plane decoder
requires the actual scalar coefficient to be zero. A line-only mask checker
would miss this additional error.

### Complete finite census

| Check | Exact result |
|---|---:|
| Selected labels / paired planes | 112 / 56 |
| Binary factorization entries checked | 12,544 |
| Off-diagonal nonorthogonal-plane entries | 11,560 |
| Nonzero literal integer entries among them | 11,559 |
| Parity-forced forbidden entries | 6,608 |
| Formal dirty scalar basis columns replayed | 224 |
| Rejection controls | 6 |

A positive scalar fixture with diagonal one, zeros on the full plane mask, and
arbitrary nonzero entries on free pairs is accepted. Controls reject the
literal integer lift, binary pairing as endpoint, omission of a factor, mutation
of a plane matrix, an invalid matching, and substitution of the old line mask.
These checks use exact integers/F2 and no floating point, solvers, predecessor
code imports, network access, or assertion statements.

## Scope, cost and invalidation

The certificate proves a binary linear-algebra identity and local translation
identities; those are not disputed. This audit identifies a missing implication
between those identities and the proposed data endpoint. The reported `C=126`
and its favorable packing screen therefore **do not certify a scalar plane-port
decoder** under the inherited scalar-factor interpretation. This is an
exactness issue before routing/hosting/precision overhead, not an estimate that
such overhead will be too expensive. We do not claim a new numerical lower
bound on the cost of a corrected decoder, and do not reinterpret a bundled
rank-two query as a fully implemented scalar word.

An operator-valued or block-valued interpretation would need its own complete
endpoint identity and charges; it is not ruled out by an audit of scalar factors.
The verifier's dirty tests are of the finite scalar map, not an unprovided full
native/hosted invocation or all-size multiplication theorem. No upstream archive,
selected record, frontier, shared index or production code is changed.

## Reproduce

From the repository root, Python 3.12 with no third-party dependencies:

```sh
python3.12 -I -O -B research/paired-plane-scalar-mask-obstruction/verify.py
python3.12 scripts/research_package.py --package research/paired-plane-scalar-mask-obstruction
```

Both commands emit `PASS_PAIRED_PLANE_SCALAR_MASK_OBSTRUCTION` with the census
above; the registered wrapper also checks metadata and source pins. The verifier
is read-only. `SOURCES.json` binds repository inputs and the exact remote fixture
by SHA256 and Git blob `7ca668d7d50c7276e89b0f6f9575e1b9f1ad9ef6`, independently
resolved from the exact PR1825 head through GitHub's contents API. The verifier
recomputes both digests offline. `PR1825-CERTIFICATE.json` is byte-for-byte
predecessor evidence, not a new result.

Local validation on 2026-10-14, CPython 3.12.12 on macOS arm64: the registered
replay passed after integration into a separate checkout, including source
authentication, all 224 dirty scalar columns, the positive fitting matrix and
all six rejection controls. A separate direct calculation, without importing
this verifier, reconstructed the 23 columns, checked all 12,544 binary entries
and corroborated the `(0,7)` coefficient 5 and dirty output 16 rather than 11.
Hosted CI and the selected supplier's complete cold replay are not claimed.

## Overlap, provenance and credit

Base main: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Closest predecessors:

- [PR1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825), Cinna Davis
  (`1337isnot1337`), head `d16fb8936795ff101e4d2f63cfdc6a25066ebabf`: matching,
  binary factors and endpoint translation checks audited here.
- [Discussion1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18914510),
  ctoth and collaborators: unpaid-line derivation and valid small plane endpoint.
- [PR1808](https://github.com/CrocSwap/integer-mult-bounds/pull/1808), Josie Elliston,
  head `b3d9b9813e0f2e82d8379cd4dafa2a355a900a44`: complementary planning budgets,
  not a decoder construction.
- Selected PR1094 by Rohan Arun, the Jeremy Kothe / Hao Yan word lineage, and
  the inherited decoder/geometry contributors retain all source credit.

The final full overlap refresh covered 543 open PR bodies including
drafts, complete pagination fetched 2026-10-14T13:23:53.012964Z, and 529 discussion
records including comments/replies fetched 13:25:07.056183Z. Relevant full PR and
discussion text was read; PR1825's exact head was independently rechecked unchanged.
The later P111 bit-side Parseval-frame claim in Discussion1587 comment18924772
has a different object and is not this P112 scalar-mask audit.
The refined search found no corresponding scalar-mask audit; it did not search
every code diff, nested file or closed PR and is not a novelty certificate.
Coordination: [Discussion1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884).

Prepared for adamgall with substantial **OpenAI Codex** assistance in research,
verifier implementation and proof exposition. No independent human review or
formal proof-assistant check is claimed. Apache-2.0, including the attributed
predecessor certificate.

## Open next questions

Can these paired planes support an affordable **scalar fitting matrix**, rather
than a factorization of their incompatibility matrix? First solve the displayed
masked scalar equations over Q or Q(i), then compute copied ranks from the
complete source/target planes and charge every changed local operation,
restoration, host and route. The blocker is that neither such a factorization
nor its all-cost implementation is supplied here. This question matters because
only an exact, fully charged replacement can realize the two-unpaid coverage law.
Structured fields are in `TASK.json`.
