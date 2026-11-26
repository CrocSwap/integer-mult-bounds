# A varying-arity exact interchanger with absolute linear space

Status: **written theorem; independently accepted by Route C**. See [REVIEW-ADAPTIVE-INTERCHANGE.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/route-c/REVIEW-ADAPTIVE-INTERCHANGE.md). This is the exact physical-address component. It does not alone prove a numerical transform or integer-multiplication bound. Unlike the fixed-profile component, it chooses a fresh finite parameter at each spatial descent.

Pins: programme `0607d044d1d09489580da0e5828588820e1a6775`; OpenAI math `3344da59991ed94f9ba711217b29c1d760badfa6`. Dependencies: B's [compact-interchange.md](compact-interchange.md) (CI), [succinct-factor.md](succinct-factor.md) (B1), [explicit-dyadic-geometry.md](explicit-dyadic-geometry.md) (B2), [full-rate-field-packing.md](full-rate-field-packing.md) (FP); A's [uniform-payload-shared-pencil.md](uniform-payload-shared-pencil.md) (UP); C's [COMPACT-SPECTRAL-REPAIR-EXECUTOR.md](compact-spectral-repair-executor.md) (SR); lead [packed-batch-with-small-radix.md](packed-batch-with-small-radix.md) (PB). The source supplies elementary streams, shared-pencil identities and the main/reserve recursion. All constants are independent of input and recursion depth. Write

    phi(y)=y^(2/3) (log2(y+2))^(1/3), y>=0.

**Theorem AI.** One fixed deterministic finite-alphabet multitape machine exactly interchanges two complete binary address fields of width u, with arbitrary complete prefix, gap and suffix spectator ranges, in

    time <= C V sqrt(1+u) 2^(C phi(log2(u+2))),
    visited cells <= C V,                               (AI1)

where V is the actual input bit volume and C is absolute effective. Occupied spectators are restored. The same bound holds for radix-3 fields of width e, replacing u by e. There is no input-dependent alphabet, advice, exponential-order matrix listing, or extension-field payload expansion.

## 1. Uniform local ingredients

Replace CI's pencil schedule by UP and use the safe larger endpoint constant Cg=2^22. The prerequisite m r_*/N<=1 is retained. Only an absolute number of full-volume arrays coexist: input/output; all query-by-rank accumulators together, of volume at most V; one rectangle's source/destination subsets; and fixed scalar/rotation scratch. Polynomially many ordinary scans in m are allowed. Recursive preparation is not repeated per query.

Serialize SR comparison tags by coarse role. A repair parent has 32B roles, each of raw volume w times the physical range, with B>=2m+1. Tag only the current input role: m ternary keys require 2m bits per scalar record, whose raw encoding has at least two bits. Thus its tagged size is at most (1+m) raw roles, hence less than one whole parent. Compute output checks by repeated aligned scans over retained raw input, accumulating their linear scalar contributions. This costs polynomial-m ordinary work. Complete forward/inverse converters remain outside these role loops. Strip tags before converter calls, retaining the four exact child masses 1/16. Other check/input/output arrays occupy only an absolute number of parent volumes. The optional tag-free lemma SK is not needed.

FP chooses hK=2eK, with eK a power of two and K=F_(4^eK) containing B nodes. Pack hK independent binary rows bijectively into each scalar; encoded and original bit volumes agree. Packing uses polynomial-m time per bit and fixed full-volume scratch. The field is fixed inside a finite repair tree. Each spatial child receives encoded bits with the coordinate index as suffix spectator. It may choose another field, since its completed map is an exact bit permutation.

The complete local template has ordinary work and locally parked space

    work <= m^K V+poly(m,log(V+2)),
    cells <= C0 V+poly(m,log(V+2)),                      (AI2)

for absolute K,C0. Enlarge K once to include constructor, descriptions, log row-width, role loops, formula traversal, scalar arithmetic, endpoint lists, label rank factorization and ordinary head returns. Descriptor polynomials also have absolute degree. These are explicit finite loops on polynomial-m descriptions, never template enumeration of w rows or all 3^m spectral keys.

## 2. A uniformly optimized compact family

For sufficiently large odd m, put u0=ceil(log2(m)), v=ceil(log2(u0+2)), and choose the largest power of two d>=2 with d^3 v<=u0. Thus d is within absolute factors of (log m/log log m)^(1/3). Let q=2^t be least with q^(d^2)>=2^(2d^2-2)m, and set

    h0=2d-1, N=q^(h0^2), Dg=2(2+h0 q^h0), a=Dg-2.

Retain the exact rank/incidence bounds

    r_*/N <= 2^(2d^2-2)q^(-d^2),
    lambda <= binom(h0,d)^(d+1)(q-1)^d t^(d(d-1)).

Consequently m r_*/N<=1 and N>=512. Above a fixed effective threshold, N<=m^5 and a<=m^(1/4). The latter follows from log Dg=O(log m/d+d). Moreover

    log2(Dg(1+lambda))
       <=3 log2(m)/d+O(d^2 log2(log2(m)+2))
       <=C1 phi(log2(m)).                               (AI3)

These choices give polynomial-m label/rectangle descriptions. As in CI, let Dp<=24sqrt(m), h=ceil(log2(m)/4), M=16^h<=16m and W=M N 32B w. Define

    Rpen=2^22 Dg(1+lambda)(1+m r_*/N),
    Qm=8Dp Rpen+3m 4^(-h).

The full independent-row swap identity, including finite repair leaves and its final order-three word, has normalized spatial-call mass Qm. The binary-row batch has hK W rows; put ell=ceil(log3(hK W)). Enlarging the one absolute K ensures ell,log2(W),retained descriptions<=m^K. Equation (AI3) gives

    2Qm+2a <= sqrt(m) 2^(C2 phi(log2(m))).              (AI4)

Each grouped main child is at most 1/N of its repair parent's volume, or at most 16^(-h) of the main root for direct finite leaves. Leading padding is beta<2, so each main child is below half the root volume. Full-volume reserve calls begin only after main payload arrays are cleared.

## 3. The executed nonstationary recurrence

Fix an integer R so large that delta=1/R satisfies delta<=1/4 and delta K<=1/8. It is a fixed machine parameter. At radix-3 width e let m(e) be the largest odd integer no greater than the integer R-th root of e. Below one fixed effective threshold E use direct elementary digit exchanges. Above E all Section 2 guards hold. Integer roots and finite descriptions are constructed with fixed-polynomial bit complexity.

Use ell(e) leading digits for the packed batch and set

    f(e)=floor((e-ell(e))/(m(e)+2a(e))).

Enlarging E guarantees

    e^delta/2<=m(e)<=e^delta,
    ell(e)<=e^(1/4), a(e)<=m(e)^(1/4),
    e^(1-delta)/8<=f(e)<=2e^(1-delta),
    f(e)<=e/m(e)<=e/2.                                 (AI5)

These follow from the definitions and fixed delta, rather than being input promises. With y=log2(e), another fixed threshold enlargement gives

    (1-2delta)y<=log2(f(e))<=(1-delta/2)y.               (AI6)

The lower bound records the actual descent scale. The upper bound and f<=e/m suffice for the time proof.

Let T(e) bound actual time per incoming bit uniformly over spectator ranges and inputs. Because the exponent in log V is absolute, the descriptor work in (AI2) is absorbed into c m^K V. PB pads the main row batch by beta(e)<2; merge and unpad before the 2a reserve calls. The actual invoice is

    T(e)<=c m(e)^K+Lambda(e)T(f(e)),
    Lambda(e)=beta(e)Q_(m(e))+2a(e)
       <=sqrt(m(e))2^(C2 phi(log2(m(e)))).              (AI7)

Every nonlocal spatial child uses common width f. The bounded remainder exchanges are local scans. This is a recurrence of the executed varying-parameter algorithm, not substitution of m(e) into a fixed-m asymptotic theorem with a fresh O_m(1) constant at each depth.

## 4. Solving the nonstationary time invoice

Consider the actual width chain e_0,e_1,...,e_k, where e_(i+1)=f(e_i) and e_k<=E is the first base width. Put y_i=log2(e_i), U_i=T(e_i)/sqrt(e_i) and q0=1-delta/2<1. Equations (AI5)-(AI7) give

    U_i<=tau_i+mu_i U_(i+1),
    tau_i<=c e_i^(delta K-1/2)<=c e_i^(-3/8),
    mu_i=Lambda(e_i)sqrt(e_(i+1)/e_i)
         <=2^(C2 phi(log2(m(e_i))))
         <=2^(C2 phi(y_i)),
    y_i<=q0^i y_0.                                    (AI8)

For 0<=r<=1, monotonicity of the logarithm gives phi(ry)<=r^(2/3)phi(y). Therefore

    sum_(i<k) phi(y_i)
       <=phi(y_0)/(1-q0^(2/3)).                         (AI9)

Every partial product of the mu_i is at most 2^(C3 phi(y_0)); C3 may depend on the fixed delta, but not on input. Also e_(i+1)<=e_i/2, so, reading the finite non-base chain backwards,

    sum_(i<k) e_i^(-3/8)<=1/(1-2^(-3/8)).              (AI10)

The base normalized cost is bounded by an absolute constant because E is fixed and all elementary widths there are bounded. Unfold (AI8), using the partial-product bound and (AI10), to obtain

    T(e_0)<=C sqrt(e_0)2^(C phi(log2(e_0))).             (AI11)

The initially bounded widths, including zero-width identity fields, are covered by replacing e with 1+e. Thus both the recursive branch contributions and local polynomial-m scans are paid. The estimate does not discard the local toll or assume a limit in m before a limit in e.

## 5. One absolute bound on cells ever visited

At an interchange node of volume V, the local main interpreter, including its finite repair recursion, uses at most C0' V payload cells with an absolute coefficient. UP, FP and one-role SR supply its local bound. Repair phases shrink volume by 1/16 and run sequentially, so their parked payload sums geometrically. Each spatial main child has volume at most V/2 after its own parent's leading padding. Along a stack, the sum of locally parked payload at such volume-shrinking descents is at most 2C0' V_root.

A full-volume reserve child begins after its parent's main arrays have been released. It takes ownership of the current data region; no additional full-volume parent copy is parked. Thus any number of intervening reserve descents contributes control descriptors but no additional parked payload volume. Reuse fixed end-access work/stack regions across siblings, phases and rectangles. This bounds cells ever visited, not merely simultaneously live data on independently allocated regions.

Each template/control descriptor and arithmetic scratch region has size polynomial(m,log(V+2)) with an absolute degree. Complete width-e fields imply V>=3^(2e). Since m(e)<=e^delta, all additive local descriptions are bounded by a fixed polynomial in log(V_root+2). A spatial path has O(log(e_root+2)) levels, and each finite repair path has O(log(m+2)) levels; even their product is polynomial in log(V_root+2). The sum of every parked control region therefore remains at most a fixed polynomial in log(V_root+2), which is at most C V_root for an absolute C. Generation scratch can be reused at every node. Field changes do not multiply payload volume because FP is a bijection on the incoming bits.

One should not bound space by the number of total calls: repeated calls reuse the same regions. Nor is an m-dependent coefficient of V hidden in these estimates. Polynomial-m growth appears only in ordinary work and additive descriptors. The coefficient of every simultaneously retained full-volume payload list is absolute.

## 6. Binary conversion and exactness

For binary field width u, pad each complete field's range from 2^u to the least power 3^e above it. Then e<=u+1 and the two-field volume grows by less than nine. Source ordered scans insert and remove padding. Every padded binary row carries independent original bits or explicit zero padding, and the complete main identity permutes only its intended physical fields while restoring spectators. Restriction therefore returns precisely the requested binary interchange.

At every finite level the exact completed cyclic-factor, prediction/repair and order-three identities are unchanged. Adaptive m affects only which exact finite realization and how many recursive field blocks are used. A child recursively performs its specified exact bit permutation, irrespective of its own scalar field. Induction on decreasing e proves correctness, and (AI11) plus the constant range-padding factor proves (AI1).

## 7. Scope, verification and next implication

This theorem closes the varying-parameter exact-interchange time and uniform-payload space interface. It is independent of a fixed-epsilon family scheduler. Numerical Walsh precision and its own local polynomial-parameter costs require a separate varying-arity analysis; setting its arity to a fixed power of its width would not follow from this note. Integer multiplication still requires that numerical component and the source complete integer caller.

[verify_adaptive_interchange.py](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/route-b/verify_adaptive_interchange.py) is a finite diagnostic for exact integer parameter/width invoices and normalized recurrence inequalities on executable toy profiles. The saved replay passes 96 root-boundary cases, 3,597 width/mass/toll invoices, 36 complete recurrences of depth up to 228, and 32 packed batches. It rejects 3,597 omitted-leading/reserve-budget cases and 36 omitted-local-toll controls. These cases cannot execute the asymptotically large optimized geometry or certify a tape implementation. The analytic inequalities above, together with the cited local constructions, establish the theorem; the checker distinguishes floor/leading-budget and local-toll mistakes.
