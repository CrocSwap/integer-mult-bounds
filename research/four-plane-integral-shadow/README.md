# One open four-plane class has exact COPY mass sixteen

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with a finite exact certificate.** For the four matched planes
`(0,1,44,49)` in the pinned PR1825 ordering, every finite scalar rank-one
factorization of `I_8` has additive full-plane COPY mass at least **16**, over
**every coefficient field**. Eight coordinate messages attain sixteen.

This settles one concrete quadruple marked uncertified in Ryanson Jonathan's
[PR4454](https://github.com/CrocSwap/integer-mult-bounds/pull/4454).
The new artifact is an integral pairing-matrix witness and its rank proof.
No predecessor census or certificate replay is a deliverable here. The
other quadruples and tariff classes are not classified.

## Exact object and tariff

The planes have ordered port pairs `(0,1),(2,3),(63,66),(72,75)` and ordered
binary labels

```text
11 19 | 35 67 | 296 392 | 400 416
```

Write `p(i)=floor(i/2)` for the plane of scalar coordinate `i`, with
`0<=i<8`. The integer zero-one matrix `G` is obtained by taking the binary
dot products of these labels and then interpreting the resulting bits as
integers:

```text
1 0 0 0 1 1 0 0
0 1 0 0 0 0 1 0
0 0 1 0 1 0 0 1
0 0 0 1 0 0 0 0
1 0 1 0 1 0 1 0
1 0 0 0 0 1 0 0
0 1 0 0 1 0 1 0
0 0 1 0 0 0 0 1
```

Every diagonal plane block is `I_2`. For nonempty subsets `S,T` of the four
planes, let `G[S,T]` contain their complete two-coordinate blocks and put
`t(S,T)=rank_F2 G[S,T]`. This is CubeJerry's PR4365 tariff, retained by
PR4454. Coefficient-field rank and binary tariff rank are different notions.

For vectors `u,v` in `K^8`, let `S(u)` contain every plane with at least one
nonzero coordinate of `u`, and similarly define `T(v)`. The charge of a
nonzero scalar message `u v^T` is `t(S(u),T(v))`. Zero messages may be
omitted. Charges add. The endpoint is exactly

```text
sum_j u_j v_j^T = I_8.
```

There is no bound on the finite term count, and cancellation is permitted.
This fixes the identity endpoint; it does not assert a result for every
strict scalar fitting matrix or for shared native operations.

## Integral rank certificate

For all 225 ordered nonempty closure pairs, the finite certificate establishes

```text
rank_Q G[S,T] = rank_F2 G[S,T] = t(S,T).
```

The tariff histogram, indexed by rank zero through six, is
`(2,26,80,40,55,13,9)`. The checker uses rational elimination separately from
binary elimination. More directly, it runs 697 minor checks of order
`t(S,T)+1` and finds each determinant exactly zero in `Z`. These count a
minor again when it belongs to another closure pair. When the order exceeds
a block dimension there is no
minor to check. Vanishing of these integer minors implies

```text
rank_K G[S,T] <= t(S,T)
```

in every field `K`, including characteristics in which the rank drops.
This implication uses integer determinants, not numerical sampling or an
assumption that rational rank is invariant under specialization.

## Proof of the mass floor

Partition `G` into two-by-two plane blocks `G_ab`. Define a linear map from
`8 x 8` scalar matrices to `16 x 16` matrices by replacing each entry with
its plane block:

```text
Phi(M)[(i,a),(j,b)] = M[i,j] G[(2p(i)+a),(2p(j)+b)],
0<=i,j<8, 0<=a,b<2.
```

This map is defined over every field by the displayed integer matrix. Since
every `G_aa=I_2`, it sends `I_8` to `I_16`.

For one message `u v^T`, define `A_u` with rows `(i,a)` and columns `(c,b)` by

```text
(A_u)[(i,a),(c,b)] = u_i [c=p(i)] [a=b].
```

Then direct entrywise multiplication gives

```text
Phi(u v^T) = A_u G A_v^T.
```

All block columns outside `S(u)` vanish in `A_u`, and all block rows outside
`T(v)` vanish in `A_v^T`. Consequently

```text
rank_K Phi(u v^T) <= rank_K G[S(u),T(v)] <= t(S(u),T(v)).
```

Apply linearity and rank subadditivity to the complete endpoint:

```text
16 = rank_K I_16
   = rank_K sum_j Phi(u_j v_j^T)
  <= sum_j rank_K Phi(u_j v_j^T)
  <= sum_j t(S(u_j),T(v_j)).
```

This includes arbitrary coefficients and any finite number of cancelling
terms. For attainment, take `u_j=v_j=e_j` for `j=0,...,7`. Every message
uses one plane on both sides and costs `rank I_2=2`. The sum is `I_8`, so
the total is sixteen. This proves the exact optimum.

The linear-map/rank argument is the established expanded-identity or
Hadamard rank method. Philippe Van Velzen's expanded-identity lineage,
DreamingOfClouds's PR2111 rank-preserving lifting route and Nick Petalas's
PR3505 reader-transfer discussion retain that credit. The new claim is this
explicit integral witness and its all-field consequence for the named open
quadruple, not a new general rank method or a claim of literature priority.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/four-plane-integral-shadow/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/four-plane-integral-shadow/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/four-plane-integral-shadow
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/four-plane-integral-shadow --check-source-history
```

Any CPython 3.12 installation can replace the absolute local path. Expected
marker: `PASS_FOUR_PLANE_INTEGRAL_SHADOW`, with `closure_pairs=225`,
`vanishing_integer_minors=697`, `literal_atoms=6400` and `minimum_mass=16`.
Both registered commands run the complete checker with assertions disabled
in the second command. Each has a 60-second limit.

Besides the rank certificate, the checker constructs all 6,400 literal
rank-one fixtures in which each touched plane contributes one of its two
coordinate vectors on each side. It computes their full `16 x 16` shadows
and checks the rank bound over `F_3`. These fixtures corroborate the map;
the written factorization proves the arbitrary-field atom inequality.
The eight-term coordinate endpoint and a ten-term endpoint with a cancelling
dense pair check attainment and linearity. Six rejecting controls cover an
empty mask, a Boolean mask, an omitted endpoint term, an underpriced self-plane
message, a false rational lift and a missing diagonal normalization. A free
cross-plane atom is a positive control whose ordinary scalar rank is one but
whose shadow is zero.

The printed receipt is freshly generated from the actual checks. It hashes
all five package files and both ordered result streams. It is not handwritten
or stored as a claimed execution record. Default replay writes no files and
works from a standalone export without Git or network access.

## Source and scope boundaries

Canonical base is `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7.
`SOURCES.json` pins the catalogue, selected record, source archive, matching,
PR4454 README and open-index bytes as historical provenance. The archive's
`candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json`
member has SHA256
`c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`.
The matching and that label inventory identify the displayed ports and labels.
In the pinned PR4454 index, zero-based lexicographic combination position
1369 has the two-byte index zero. Only that identification was read; the
predecessor's scientific replay was not run.

The original card is explicitly changed from a new helper construction to a
scoped obstruction in an existing complete-plane interface. Its historical
first command fails at `KeyError: 'complex_profile'` under the current
selected schema. The current `research_selected_baseline.py` orientation
passes. Neither command supplies evidence for this new theorem.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146140)
initially targeted characteristic three. Its
[progress update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146177)
records that the same first witness has an integral all-field certificate.
No wider class search followed that witness.

No physical preparation, coefficient execution, frames, routing, dirty-private
restoration, stock, precision, recursive caller, supplier, outer theorem or
new kappa is supplied. Concave power tariffs and other endpoints are outside
scope. Independent human and formal proof-kernel review are unclaimed. Lean,
Docker, the selected cold replay and historical scientific suites were not run.

The checker has no recursion, subprocesses or dynamic code. All matrices have
at most sixteen rows and columns; minors have order at most eight. Loops are
bounded by 225 closure pairs, the finite minor combinations, 80-by-80 atom
fixtures and ten endpoint terms. Functions are below sixty physical lines.
Power-of-Ten rule 3 has a managed-runtime deviation for Python integers,
fractions and collections within those fixed domains. Six local rejection
callbacks have fixed visible targets. File reads are capped at one MiB per
file, and warning errors are enabled in both registered commands. No native
fixed-memory guarantee or unavailable static analyzer is claimed.

## Open next questions

Can another specifically uncertified quadruple admit a signed or rational
block matrix with the same diagonal normalization and all closure ranks
bounded by the binary tariffs? First name one remaining index-zero quadruple
and check its complete closure table. Existence of such a witness is the
blocker; no general four-plane theorem follows from the present example.

Can the same rank-map certificate constrain a different actual scalar endpoint
at a paid caller boundary? First state that endpoint and compute the rank of
its image. Source access, native realization and its complete physical bill
remain additional blockers. This package stops at its first proved result.

## Credit

The new contribution was produced by Nick Petalas. Credit Ryanson Jonathan
for PR4454's open four-plane problem and PR4421's earlier rank duals;
CubeJerry for PR4365's contract and two-plane theorem; Cinna Davis for
PR1825/2126's plane data; Gonzalo Mier for PR3990/3997's support screens;
and Philippe Van Velzen, ctoth and the retained paired-plane/native/E8
lineage for the endpoint and expanded-identity context. Existing credit and
frozen evidence are unchanged. The lifting-method predecessors are credited
in the proof above. New material is Apache-2.0.
