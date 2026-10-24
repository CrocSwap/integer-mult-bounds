# Centre entry, code, and reuse services

This package supplies exact local services for two actual centre responses.
It gives a moving entry swap, a square code on the existing data fields,
rational capture and decode words, and exact tests for legal code transitions.
It also gives six joined D25 forward services that use a retained earlier
reader. The fixed-reader phase inverse is retained as a separate useful
construction when that reader must stay fixed.

These are component constructions and enabling proofs. They do not improve
the complete kappa calculation. A complete routed caller, helper host,
terminal code removal, finite address-map price, and recursive precision
bound remain separate obligations. Read the [proof index](PROOFS.md),
[source record](PROVENANCE.md), and [fresh replay](evidence/REPLAY.json).

## Moving entry and two different storage contracts

Write the actual response as E=I+UV, with B=VU invertible. Put H=I+B,
Q^4=I, and L=Q^2. The actual L fields are simultaneous translations.
The corrected entry uses

```text
J_in = L U,       D_in = B^-1 V L,       D_in J_in = I.
```

For arbitrary data a and an arbitrary separate centre bank z, the ordered
word a+=J_in z; z-=D_in a; a+=J_in z; z=-z gives

```text
S_in(a,z) = ((I-J_in D_in)a + J_in z, D_in a).
```

This map is an involution. One use stores the old z in the data. It does
not clear z or restore its prior value. Two consecutive uses restore all
inputs. This entry uses a separate bank of 30 or 16 centre fields.

The complete paid entry words use two passes of L on the 112 data fields:

| Separate-bank entry | Real dyadic primitives | Translation calls | Additional real odd scans |
| --- | ---: | ---: | --- |
| Rank 30 | 5076 | 224 | 22 multiplications and 22 divisions at each of 3 and 5 |
| Rank 16 | 4448 | 224 | 16 multiplications and 16 divisions at 3 |

Both words have exact stored opcode-prefix row norm 12. The odd-height
bound is one at each listed prime. These are opcode-boundary bounds;
they do not include the internal implementation of a dyadic ADD or a
recursive child. Translation calls need their finite map price.

A different square code uses only the existing 112 data fields. If a
selected row minor U_P is invertible, with complement R, set

```text
C0 a = (B^-1 V a, a_R - U_R U_P^-1 a_P).
```

The explicit inverse in the proof gives C0 E C0^-1=diag(H,I). The actual
rank-30 minor has determinant -1/256 and an integral inverse. The actual
rank-16 pivot code uses another complement and an unnormalised reader;
it is a different square code. The moving review checks both matrices
and both inverse orders on all 112 data columns. The separate-bank entry
invoice above is not a price for either square code.

The unnormalised sum-code variant is dyadic when U, V, and U_P^-1 are
all dyadic. The minor condition alone is insufficient. Both actual
source factors satisfy these premises. This qualification is part of
the retained [root-proof addendum](frozen/lanes/bridge-review-20261017/moving-code-review-20261020/ROOT-PROOF-ADDENDUM.md).

## Transport and the output code

Assume the actual data advance is A=F Q^-1. The common F must commute
with Q and with the scalar maps. Then

```text
J_out = Q U,       D_out = B^-1 V Q^-1,
Q E Q^-1 = I + J_out B D_out.
```

For any scalar C with C E C^-1=K, its code moves in the exact order

```text
C Q^2 -> Q^-1 C Q^-1 -> Q^2 C -> Q C Q -> C Q^2.
```

Successive F operators may differ, but each must commute with C and Q.
An opposite-sign advance can return the first output code directly to
C Q^2 under the same premises. A routed port-dependent advance must pass
the actual test C_(p,r)(F_p-F_r)=0, or supply a proved connecting operator.
Nominal frame labels do not prove this relation.

For rank 16, K has eight entries -5, eight entries -7, and 96 entries 1.
Its centre action uses existing pivot fields and commutes with arbitrary
independent linear frames on those fields. Each diagonal H direction
costs 32 old real scalar units plus 16 real odd scans at each of 5 and 7.
Forward scans multiply; inverse scans divide. This service does not
create or admit its input fields.

The encoded output remains Q^-1 C Q^-1. A raw exit requires the ordered
decode Q C^-1 Q. The complete physical cross-bank native calls also keep
their extra odd phase. An interleaved caller, borrowed restoration, and
productive helper advance need full endpoint proofs. The four-step cycle
does not remove a final code at an odd cut.

## Rational whole-bank and capture services

The rank-16 signed clique response in this package is a whole-bank code E.
It is distinct from the rational-unitary packing C16 in the centre-metric
encoder package. In its signed pair coordinates,

```text
E = I - sum_large(w w^T / 2) - sum_small(w w^T),
E^-1 = I - sum_large(w w^T / 10) - sum_small(w w^T / 7).
```

The eight large rows have squared norm 12; the eight small rows have
squared norm 8. They are mutually orthogonal. The eigenvalues are 1 on
96 dimensions, -5 on eight, and -7 on eight. Each direction costs 3420
real dyadic primitives plus 32 real fixed-odd scans. The forward scans
multiply by 5 or 7; the inverse scans divide. Exact local row norms are
20 forward and 18 inverse. The inverse has odd height one at 5 and 7.
Its valid-image inverse works without odd root scaling. Generic inputs
still require the exact grid.

For rank 30, the unnormalised code Csum stores V a on 30 selected ports
and a complement on the other 82. Its complete literal capture and inverse
each cost 2910 old real scalar units plus 22 real scans at 3 and 22 at 5.
The complete capture, G0 or G0^-1 action, and decode costs 6090 old units,
plus 22 real multiplications and 22 real divisions at each prime. These
words act on 640 arbitrary input columns and leave 528 outside roles fixed.
They require a common linear frame. No physical native capture is inferred.

Let R0=Z[i,1/2]. The exact image of Csum has quotient

```text
(R0 / 3 R0)^11 direct-sum (R0 / 5 R0)^11.
```

The proof supplies all 22 syndromes and explicit right inverses. The
rank-16 image has eight syndromes at 5 and eight at 7. A complete middle
operation M preserves the relevant code precisely when its full matrix
satisfies L_p M = S_p L_p modulo each prime. The test includes helper
columns and any array or owner coordinates. In particular, R0/5R0 splits
as two copies of F5; it is not the field F25.

The rank-30 G0 and G0^-1 actions preserve the image. Their capture/decode
chains have exact divisions with no odd root scale. An arbitrary ADD can
leave the code: the checker rejects both a data ADD and a helper-to-data
ADD that violate the syndromes. Local prefix bounds and generic grid
scales are in the exact receipts. The fixed-odd scan cost is additional
to the old scalar count, and descriptor work remains separately priced.

## Conditional composition theorem

A whole-state type declares stored state C u on every data, borrowed,
and live numeric work role. If each completed operation has endpoint
C_out A C_in^-1 with a Gaussian-dyadic semantic A, adjacent matching codes
cancel in their stated order. No commutation is needed. A common divisor
in two unrelated code matrices does not establish such a transition.

Under the explicit local-prefix and decoded-child-entry bounds in the
proof, recursive depth D gives odd height at most (D+1) ell_p+c_p.
Completed siblings do not add a term. The root must have identity type
or a paid initial encoding; every child entry needs its own decoded-input
bound. The final physical endpoint must be dyadic for exact unscaling,
and a required raw result must include paid removal of the final code.
This conditional theorem extends the retained common-grid method. No
current complete caller is claimed to satisfy all its premises.

## Six retained-reader D25 services

Both actual providers pass for the pairs (s,t)=(0,1),(0,2),(1,2). Here s
labels the retained reader; physical input progress is t-1. Pair (0,2)
therefore starts at physical level one, not zero. Put G=diag(I_P,q_R),
and let F_t be FULL on the first 9+8t axes. With the actual routed E_t,
set (A_s,t)_P=L_s E_t and (A_s,t)_R=(E_t)_R. The exact forward service is

```text
(F_(t-1) x, F_(t-1) G w) -> (F_t x, F_t G (w + A_s,t x)).
```

The bank w is arbitrary. Each service checks all 640 input columns and
keeps the 416 outside contents fixed. The native prefix costs 6456 real
scalar primitives; the late query costs 11168. The total is 17624, with
profile 1392 H1+64 H2+48 H3+16 H8, 1520 children, and rank mass 1792.
The complete monomial call bound is 5776: 448 DATA maps, 224 endpoint
adapters, 3040 native side maps, and 2064 late-query maps. No extra field
or odd division is introduced by the join.

Each body uses the inherited typed helper supply and restoration
contract. The DATA partition does not construct that helper host.
The full regular cover must complete before the global query. A per-body
query needs another source-availability proof. The exact content bounds
are 22 and binary height one for the prefix, and 448 and height two for
the query. These do not include internal native-child precision.

The fresh join replay checks all 35 consumed phase-source hashes and
keeps every inherited prefix, adapter, and phase record unchanged. It
checks the new DATA phase equations and routed query. It does not repeat
the earlier 4194304-coefficient spatial phase interpreter. A separately
packaged complete backward native service is not supplied.

## Fixed-reader phase inverse appendix

For the earlier fixed reader, T=V Q^2 U has an exact inverse at every
positive tensor width. Its physical translation kernel has 2712 terms, common
denominator 120, and infinity norm 88/5. Odd denominator factors 3 and 5
are necessary. The 512-character certificate proves the all-width result
because simultaneous translations depend only on the XOR of frequencies.
The review verifies both certificate product orders, not a second
independent inversion algorithm.

The complete fixed-reader section swap costs 208028 dyadic real primitives,
12072 translation calls, and 60 real multiplication-by-15 scans plus 60
real division-by-15 scans. It uses a separate arbitrary centre bank.
At physical input Qx it reads T^-1 VQx, whereas the earlier terminal needs
VQ^-1. In the older proof, QU is a section of the normalised reader
T^-1 VQ; it is not a section of VQ itself. The moving construction changes
the reader to remove this mismatch. The fixed-reader inverse remains
useful when that change is unavailable.

## Reproduction

Use Python 3.11 or later, the standard library, at least 3 GiB of free
disk, and a new output directory. No network access is needed.

```sh
python3 -I -B replay.py --output /tmp/centre-code-services-replay
```

Expected final output:

```text
PASS_CENTRE_CODE_SERVICES
```

The runner executes seven checks in normal and optimized Python, one
process at a time. All original checker bytes stay unchanged. Two old
checkers write beside their sources, so the runner uses fresh copies and
saves their outputs before it removes those temporary copies. It compares
compressed outputs after decompression. In JSON receipts it changes only
registered source-path values to package-relative paths, then compares
all values with the frozen receipt. It checks every frozen source hash
before and after execution. The file-access audit checks that inputs come
from this package, the fresh output, or the Python runtime. It is a
reproducibility check, not a security sandbox.

The checks include arbitrary-state swap restoration, both code inverse
orders, exact division domains, syndrome failures, mismatched repeated
codes, and wrong DATA phase order. No archived producer emitter, complete
native spatial phase suite, selected frontier, complete recursive supplier,
or Lean formalization was rerun.

## Open next questions

A moving-code caller must bind every routed advance and interleaved
cross-bank operation to its full input and output code. Start with the
actual three-call chronology and its final odd cut. Supply the ordered
final decode and restoration of all borrowed values.

A rational capture caller must prove each complete middle operation
preserves the image, including helper columns and address mixing. The
syndrome equations and their failed-ADD controls are a direct starting
point. A shared list of odd primes is not a transition proof.

The joined D25 forward service needs a complete inherited helper host
and finite map prices before it can enter a supplier invoice. A backward
native service needs its own literal word and full arbitrary-input check;
the abstract inverse-adjoint identity alone does not supply that word.

A recursive rational implementation must prove its decoded child-entry
and internal-prefix bounds for the actual caller. The conditional type
theorem supplies the required statement and a height bound once those
premises hold. It does not verify them for a current complete supplier.
