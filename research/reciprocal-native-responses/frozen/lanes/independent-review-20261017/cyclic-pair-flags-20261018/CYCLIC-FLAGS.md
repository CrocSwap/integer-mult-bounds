# A cyclic frame schedule for the actual pair modes

The actual pair code admits all 240 off-diagonal coefficients of eight
six by six blocks. No separate centre-query child is needed. Every data
field receives total native rank eight. This packet proves the exact
scalar maps and the nested-frame schedule. It does not yet certify the
native phases, the ordinary response on the other 64 ports, a recursive
host, or a complete supplier.

The full 48-port signed response is in this family. The family also
contains nontrivial responses whose inverses remain in the family. Thus
the schedule is not limited to one centre correction or one matrix.

## Actual pair coordinates

Use the pinned pair incidence and signed centre rows K. For each physical
pair e=(a,b), incident to vertices v,w, set

```text
A_e = [[K_va, K_vb], [K_wa, K_wb]].
A_e A_e^T = 2I,     A_e^-1 = A_e^T/2.
```

Let A be the direct sum of these 24 two-field codes. The two coded
carriers use the original physical field labels a,b. Carrier a belongs
to v and carrier b belongs to w. At each vertex, order its six carriers
by their occurrence in the pinned `pair_edges` list. The payload records
these orders in `cyclic_carriers`.

Let z=45. On a pair, q_a+q_b=z over F_2. Its plane is
P_e=span(z,q_a)=span(z,q_b). At each vertex the six chosen representatives
q_0,...,q_5 are orthonormal. They are all orthogonal to z. The seven
vectors z,q_0,...,q_5 are independent and span U_v. These are exact facts
about the pinned 9-bit directions.

The current signed response J and signed ordinary term G satisfy

```text
A G A^-1 = direct_sum_v alpha_v I_6,
A J A^-1 = direct_sum_v alpha_v (I_6 - 1_6 1_6^T).
```

Each J block has zero diagonal. The checker verifies the two identities
by applying each inverse pair-code column in original coordinates, then
applying G or J and the pair code. It checks all 2304 entries of each
conjugation.

## The cyclic schedule

Indices in this section are modulo six. For k=1,...,5 define

```text
S_i(k) = span(z,q_i,q_(i+1),...,q_(i+k-1)),
T_j(k) = span(z,q_(j-k),...,q_(j-1)).
```

Both spaces have dimension k+1. They increase with k. The decisive
identity is S_i(k)=T_(i+k)(k).

First advance both source fields of each physical pair from their
entry lines to P_e. Apply A_e there. Apply the same pair code to the two
target fields while both are still at I. Advance every affected coded
target to Z=span(z).

For k=1,...,5, advance coded source i to S_i(k), and coded target j to
T_j(k). At this step add

```text
Y_(i+k) += B_v[i+k,i] X_i
```

for all six i and all eight vertices. The two fields in each addition
have exactly the same frame. Each ordered off-diagonal pair occurs once.
There is no update to a source value. Hence the order of these additions
does not impose a relation between their coefficients.

After step five, advance each coded source directly from its rank-six
frame to FULL, with rank three. Apply the inverse pair codes at FULL.

For target i the last frame is

```text
T_i(5) = U_v intersect P_i^perp.
```

It is contained in P_i^perp. Advance both coded fields of each physical
pair to that common rank-seven frame. Apply the inverse pair code there.
Each restored physical target then advances to its own rank-eight hole
q_p^perp. The inclusion P_e^perp subset q_p^perp holds for both endpoints
of the pair. No nonzero value receives a free change of frame.

The other 64 fields of each data bank advance directly with rank eight.
Their response coefficient is zero in this packet. All 416 other fields,
including the eight unused C labels, are arbitrary and unchanged. The
word does not use owned or private fields.

## Full forward and backward maps

Let B be any direct sum of eight zero-diagonal six by six matrices, and
let E=A^-1 B A on the affected ports. Extend E by zero on the other
64 ports. The forward logical map is

```text
(x,y,h) -> (x,y+E x,h).
```

The same frame paths give the backward map. At each common-frame step,
replace the forward addition by

```text
X_i -= B_v[i+k,i] Y_(i+k).
```

The logical result is (x-E^T y,y,h). To see the transpose, use
AA^T=2I. It gives A^-1 B^T A=E^T. No response matrix is commuted through
a source C_q map. With the current source and target endpoint adapters,
the intended physical entries and exits are the same as the earlier
pair-coded service. Those adapters and every new native edge still need
their exact phase certificate.

The checker represents each of the 240 entries of B by a separate
formal parameter. A reverse event replay checks all 640 columns in both
directions. It permits no product of two parameters. It then compares
each coefficient with A^-1 B A or its negative transpose. This proves
the full coefficient family, not only the signed J example.

## Reciprocal responses inside the family

Let M and N be any three by three units over Z[1/2]. Then

```text
B = [[0,M], [N,0]],
B^-1 = [[0,N^-1], [M^-1,0]].
```

Both matrices have zero diagonal. They therefore use this same frame
schedule. Taking N=M^-1 gives an involution. Taking N=M^T gives a
symmetric reciprocal pair. Transposes also have zero diagonal, so an
inverse-adjoint response remains available. The scalar invoice depends
on the exact dyadic coefficients chosen.

This gives an inverse-closed block family with two free three by three
units per vertex. It is a sufficient family, not a classification of all
invertible zero-diagonal matrices with zero-diagonal inverse. The checker
includes explicit nontrivial triangular dyadic M,N and checks both
inverse orders and an involution. These statements concern the affected
48-port block. A unit on all 112 ports also requires a compatible unit
on the other 64 ports.

## Local invoice and limits

For either direction, the fixed schedule has the profile

| Native rank | Children |
| --- | ---: |
| 1 | 624 |
| 3 | 48 |
| 8 | 128 |

There are 800 children and native mass 1792. All this mass is productive
progress on the 224 data fields. The 48 affected source paths use ranks
1,1,1,1,1,3. The 48 affected target paths use eight ranks of one. The
other 128 fields each use one rank-eight child. There is no query rank.

The literal pair codes and inverse codes cost 1880 real scalar
primitives across both data banks. For a nonzero dyadic coefficient
c=a/2^k in lowest terms, the stated scalar lowering charges its complex
ADD as

```text
2 (1 + bit_length(abs(a)) + popcount(abs(a)) + bit_length(2^k)).
```

Sum that charge over the nonzero entries of B. Zero entries need no ADD.
The full signed J48 uses 240 signed unit additions, so its scalar count
is 3800 in either direction. Exact prefix row-sum bounds for this example
are in `CHECKS.json`. They bound top-level array norms, not the internal
state of a recursive child.

There are 224 endpoint maps and at most 1600 native side maps. This
schedule trades extra children and side maps for zero separate query
rank. Native mass alone does not give its recursive cost or an exponent.
The full 64-port response, native phases, helper completion, memory host,
recursive precision, and final assembly are separate duties. No selected
frontier or complete kappa calculation changes in this packet.

## Verification and credit

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/cyclic-pair-flags-20261018/check_cyclic_flags.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/cyclic-pair-flags-20261018/check_cyclic_flags.py
```

The expected output is `PASS_CYCLIC_PAIR_FLAGS`. Both runs must produce
the same payload and receipt bytes. The checker rejects omission of one
cyclic transfer. It also checks the direct diagonal obstruction: q_i is
in P_i but not in q_i^perp, since q_i has odd norm. This last fact concerns
this monotone direct-transfer schedule only.

The root lane supplied the common radical and pair conjugation. The
oblique-native lane supplied the productive pair-code construction. The
controller lane supplied the actual signed centre and pair geometry.
This lane derived the cyclic schedule. The root lane identified its
general zero-diagonal family and asked for reciprocal extensions. This
work was produced with AI assistance. Independent review and native
phase lowering are requested separately. No publication is authorized.
