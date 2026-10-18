# Mutable-source five-column connector interface

## Contract and changed hypothesis

Work over F2. The five source rows x_j, 31 output rows y_m (1 <= m < 32),
connector z and every private scratch row are distinct, arbitrarily dirty
length-L vectors. A common exact linear map B and fixed exact linear maps A_m
are read-only. None need be invertible or commute. The requested map is

    y_m += A_m B (sum_{j: bit_j(m)=1} x_j),

with every source, connector and private scratch row restored.

The inherited complete calls are Q_j: z += B x_j and R_m: y_m += A_m z.
Each call is additive, preserves its source and other rows, restores its private
scratch, returns its tape heads to declared positions, and has no dependence on
the old target value. No data row or z is private scratch. A call may depend on
its source port; any differing admission/routing prices must be charged.

The **added operation** is the complete elementary source shear
X_{p,j}: x_p += x_j, p != j. It is paid, and all sources must be restored before
return. They cannot be observed externally during the batch. Outputs likewise
cannot be observed until completion. There are no other source/output updates,
combined queries, copies, clean full rows, or direct A_m B calls. This changes
PR943's read-only-source premise and restricts its B_j maps to one common B.
Distinct B_j maps do not satisfy the new implementation identity in general.

## Construction

Use the following closed list of source-coefficient boundary points:

    0, 16, 8, 31, 5, 4, 6, 2, 3, 1, 0.

Every mask in F2^5 is a difference of two listed points. The literal readout
pairs for masks 1..31 are in CERTIFICATE.json. At an edge with nonzero
delta=q_s XOR q_{s+1}, let p be its least set bit. XOR every other active source
into x_p, call Q_p, then undo those source shears in reverse order. Linearity
gives exactly z += B(sum_{j in delta} x_j). Sources restore on every edge,
so subsequent edges and readouts use the original inputs. The ten edge masks are

    16, 24, 23, 26, 1, 2, 4, 1, 2, 1.

The source-shear count is 2*sum(popcount(delta)-1)=12. At boundary s,
z=z_in+B(sum_j bit_j(q_s)*x_j). Reading output m at its two chosen boundaries
cancels A_m z_in and yields the requested row. Readouts commute because their
destinations are distinct and they preserve z. The path closes, restoring z.
This proves the map for every L and all admissible operators and dirty states.

## Sharp ten-query lower bound with paired readouts

Allow **any number** of elementary source shears, with any straight-line order;
keep exactly two R_m calls per output. Sources are always F2-linear combinations
of their original values, so the source projection is still a closed walk q
in F2^5. Source shears do not change z and therefore introduce no new boundary
point. A t-query restored walk has at most t distinct points, including zero.

Necessity of the full difference cover follows by specializing B and every A_m
to identity at L=1 with the five input bits and z_in independent. Each paired
readout has mask q_s XOR q_t, so all 31 nonzero masks must occur. Eight points
have at most 1+binomial(8,2)=29 differences and cannot suffice.

For nine points, their span must have dimension five. Select five independent
members, and apply an invertible linear coordinate change sending those members
to 1,2,4,8,16. Difference-cover size is invariant under that change. Together
with zero, these are six fixed members, and the other three are a subset of
the remaining 26 points. Thus **all** nine-point covers are represented by the
26-choose-3 = 2,600 sets checked here; repetitions between equivalent normalized
sets are harmless. The exact coverage histogram is

| Coverage | 22 | 23 | 24 | 26 | 28 | 29 |
|---|---:|---:|---:|---:|---:|---:|
| Normalized sets | 60 | 60 | 810 | 660 | 750 | 260 |

None covers 32. Hence t>=10, attained above. This finite exclusion plus the
written normalization argument establishes the stated query minimum. It does
not minimize source shears or prove a weighted optimum when outputs may be read
four or more times. The separate census computes autocorrelations by integer
Walsh transforms rather than pair-set enumeration. No proof assistant is used.

## Completed price and recursive implementation

Let b and a be uniform complete Q and R call prices, x a complete source-shear
price, and I+P the shared admission and coefficient-preparation bill. Let D_old
and D_new pay actual program construction, storage, control and dispatch not
already included in those complete call prices. These must be evaluated for the
actual schedules, including their different instruction counts. Our bill is

    C_new = I + P + D_new + 10b + 62a + 12x.

In the old read-only-source alphabet, the Q/R portion has exact minimum

    10b + 62a + 2 min(a,b).

Every active Q and R must occur an even number of times, at least twice, by
specializing to identity on independent dirty data. PR943's 945-pairing
exclusion rules out achieving all those minimum counts. At least two additional
calls are needed, and its two repairs attain them (12 Q/62 R or 10 Q/64 R).
Here both literal repairs are replayed with the **same common B and A maps**;
they are not compared using PR943's different heterogeneous factor fixture.
Let D_src and D_out be the extra actual program bills of the two old repairs.
The new construction beats both repairs exactly when

    12x + D_new - D_src < 2b, and
    12x + D_new - D_out < 2a.

When D_src=D_out=D_old, this reduces to
12x+D_new-D_old < 2min(a,b). Arbitrary word-dependent routing or preparation
does not inherit a global optimum from the Q/R-only lower bound.

This criterion, not a free source change, is the useful mechanism. Prices may
depend on precision, ports or routing; in that case sum actual per-call bills
instead of assuming this uniform inequality.

For an explicit recursive word, factor B and each A_m into five independent
noncommuting leaves, in application order f0..f4. Split contiguously into R
(first floor(d/2) factors) and L (remaining factors). With a distinct dirty row w,
emit R(source,w), L(w,target), inverse R, inverse L. Every inverse includes its
complete reversed child word. Both linearity and scratch restoration are used:
no rounded or dirt-dependent child is admitted. The exact recurrences are

    ell(1)=1; ell(d)=2ell(floor(d/2))+2ell(ceil(d/2));
    n(1)=0; n(d)=1+2n(floor(d/2))+2n(ceil(d/2));
    h(1)=0; h(d)=1+max(h(floor(d/2)),h(ceil(d/2)));
    C(d)=2C(R)+2C(L)+complete node dispatch/preparation charge.

For d=5: ell=28, n=9, h=3. There are 160 distinct primitive map descriptors
(five for B, and five for each A_m); B descriptors are reused across sources.
Preparation is paid once, with all extra port/frame preparation charged if
required. There are 36 data rows and four borrowed dirty rows including z,
40 rows total; source shears need no extra full row.

| Quantity | Each old repair | New word |
|---|---:|---:|
| Compound Q/R calls | 74 | 72 |
| Primitive arbitrary-map ADD calls | 2072 | 2016 |
| Primitive identity-row XORs | 0 | 12 |
| Executed internal echo nodes | 666 | 648 |
| Root instructions including source XORs | 74 | 84 |
| Borrowed dirty rows | 4 | 4 |

Identity-row XORs and arbitrary-map calls have different implementations; adding
their counts does not assert equal scalar work. As one explicit **abstract
complete tariff fixture**, assign one unit to each completed primitive map
call, one to each completed identity-row XOR, one to each internal node, and
one to each root instruction, in addition to common I+P. Then the bills are
**2812 versus 2760**, a saving of 52. This is a model price comparison, not
measured execution or admission of those prices on a physical supplier.

A complete source XOR on a dense row needs L XORs, 2L bit reads and L writes,
plus loop/index work, instruction access and head travel/return. Every child
price must likewise include its coefficient/source access, arithmetic, scratch
cleanup, precision, frames and head returns. A concrete deliberately slow
realization uses 160 dense L-by-L bit matrices and 40 mutable rows, with
S=160L^2+40L data cells. For a map leaf, compute each target dot product in
one admitted clean scalar bit, update the target, and recompute to clear that
bit. This pays 2L^2 coefficient reads, 2L^2 source reads, L target updates,
and at most S*(4L^2+L+1) data-head travel before return. Source XORs pay at
most S*(3L+1) travel. Scalar bit admission/cleanup, counters, preparation and
instruction tapes must also be paid; O(log(L+2)) arithmetic/control overhead
per access gives a loose finite implementation bound. No clean full row is
assumed. These bounds establish implementability, not that either dense tape
realization satisfies the favorable tariff inequality.

## Limits

This is a changed abstract connector contract, not a selected-supplier boundary
instance. It requires common B, exact F2 linearity, temporary source ownership,
and unobserved batch outputs. It does not permit other source-dependent B_j
maps, nonlinear/rounded leaves, observers during temporary source changes,
unpriced layout transformations, or scratch aliasing. The sharp result concerns
the number of common-map queries with paired readouts only. No global scalar
circuit optimum, optimal source-shear count, favorable physical runtime,
complete supplier invoice, new moment or new kappa follows. The inherited
compiler/all-size, hosting, frame, precision/tape and analytic obligations are
not discharged.
