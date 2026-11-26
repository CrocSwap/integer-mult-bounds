# A polynomial-profile packed interchange family

Status: **complete written physical component; independently accepted by Route C**. See [REVIEW-B-COMPACT-INTERCHANGE.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S003/route-c/REVIEW-B-COMPACT-INTERCHANGE.md). This is a field-interchange theorem, not a complete multiplication bound. Its linked local constructions are explicit, rather than assumptions that the desired interchanger exists.

## 1. Dependencies and parameters

Pins: programme `0607d044d1d09489580da0e5828588820e1a6775`; OpenAI math `3344da59991ed94f9ba711217b29c1d760badfa6`. Dependencies: actual `build/interchange.tex` shared-pencil identity and spatial recursion; S002 characteristic-two labels, power-two count formulas, order-three word and finite repair; S003 [succinct-factor.md](succinct-factor.md) (B1), [explicit-dyadic-geometry.md](explicit-dyadic-geometry.md) (B2), C's [COMPACT-SPECTRAL-REPAIR-EXECUTOR.md](compact-spectral-repair-executor.md) (SR), and lead [packed-batch-with-small-radix.md](packed-batch-with-small-radix.md) (PB).

Let m be sufficiently large, d>=2 a power of two, h0=2d-1, and q=2^t the least power satisfying q^(d²)>=2^(2d²-2)m. Put

    N=q^(h0²), Dg=2(2+h0 q^h0), a=Dg-2.

Retain the proven rank and incidence bounds

    r_*/N <= 2^(2d²-2) q^(-d²),
    lambda <= binom(h0,d)^(d+1)(q-1)^d t^(d(d-1)).       (CI1)

Assume the effective polynomial guards N,Dg,lambda,d<=m^C0 with an absolute C0; the later cubic-logarithmic family meets them. In particular m r_*/N<=1. Use SR's B=O(m) ternary shifts, polynomial-size predictor formula of degree Dp<=24sqrt(m), and full independent module w with log2 w=poly(m). Set

    h=ceil(log2(m)/4), M=16^h<=16m,
    W=M N 32B w.                                       (CI2)

The scalar field is K=F_(4^eK), eK=ceil(log_4 B)=O(log m), with explicit polynomial-m construction. The physical address radix is the fixed prime 3.

A's independent count bounds the new small-dyadic endpoint lists by 1024Dg(1+lambda)(1+m r_*/N) calls per row. Take the deliberately larger effective constant Cg=2^20, and put

    Rpen=Cg Dg(1+lambda)(1+m r_*/N),
    Qm=8Dp Rpen+3m 4^(-h).                              (CI3)

This new constant replaces the older expanded compiler's numerical invoice. The compact instruction list also permits direct exact rational call-volume checks.

## 2. The theorem

**Theorem CI.** One fixed finite-alphabet multitape interpreter, given admissible m,d,q and input descriptors, exactly interchanges two equal-width binary address fields of width u with arbitrary positive prefix, gap and suffix ranges. If 1/2<rho<1 and 0<eta<=1/2 satisfy

    2Qm+2a <= (1-eta)m^rho,                              (CI4)

then, for binary bit volume V,

    time <= eta^(-1)m^C V(1+u)^rho,
    visited cells <= m^C V.                             (CI5)

One absolute C bounds actual finite generation, retained descriptions and all parameter coefficients. Descriptor arithmetic has an absolute polynomial degree in log(V+2). The bounded-width base is included. There is no w-by-w matrix listing, all-frequency table, huge numeric address multiplier or variable tape count. The intended family takes eta=1/2. The integer caller, numerical Walsh and common-cap scheduler are separate obligations.

## 3. Packed layout and ordinary row work

Main rows have order `(repair block[M], geometric label[N], shift[B], duplicate[32], module[w], physical address)`. All dimensions before w are polynomial in m. Its grade fields have polynomial-m total length. Every original row is independent; check padding and copied arrays are paid workspace.

Polynomially many coarse roles can be handled by repeated scans on fixed tapes. To extract one role across an arbitrary outer prefix, scan the full array and copy its contiguous (module,address) blocks. The child then has that outer prefix followed by module and physical address. Reverse scans scatter results. A coarse permutation uses one such pass per desired role, accumulating back into the original prefix order; it does not transpose the outer prefix with an exponential row index for free. Long prefix counters advance amortized and are not rescanned per symbol.

B1 applies scalar module-coefficient slices by polynomially many masked grade rotations. Physical data form their complete suffix. Formula masks read only polynomial-m grade bits and the current phase. Even reading the whole polynomial-size formula per scalar remains within m^C V. No scalar grade mask is moved through a spatial coordinate change.

## 4. Shared pencils keep their original recursive call order

For one predictor phase use

    A0+sum_j(A_(j,1) C_j+A_(j,2) C_j²)
      =A0+sum_j(A_(j,1)+A_(j,2))Q_j
         +sum_j(A_(j,1)L_j+A_(j,2)U_j).

The first sum is one shared-swap pencil. The comparison terms use retained input in its original physical order, with source three-run scans; B1 applies their coefficient slices. No spatial comparison mask passes through an endpoint map.

For the shared part retain exactly the source schedule:

1. Copy each rectangle incidence's source rows and perform B2's reserve-only preparation once. Retain these copies across every query j.
2. For each j, use the remaining lower triangular maps, form rectangle sums in their actual common-address order, apply the row slice, and accumulate destinations before undoing their shared preparation.
3. Use P_*'s independent binary rows/columns for the low-rank contribution. Only r_* intermediate vectors and their incident singleton/rectangle terms undergo the query-dependent full common-layout conversions. Apply the binary transfer matrix and row slices there; return and accumulate in the source order.
4. Undo endpoint preparation after all j have accumulated, and join the original-layout comparison/A0 terms.

Every label, incidence, query, rank index and coarse role has polynomial-m range. Retaining all prepared copies and accumulators uses at most m^C V cells, deliberately permitting a polynomial parameter coefficient. Repeated scalar/array scans cost m^C V. Repeating recursive endpoint preparation for every j is expressly excluded. B2 supplies O(Dg) actual small-dyadic elementary operations per needed conversion. Upper-target shears use two swaps; lower triangular operations use none. The exact source endpoint/low-rank accounting therefore gives Rpen, with the stated safe new Cg. B1 row moves add no spatial calls.

## 5. Grouped calls and their exact volumes

A coordinate conversion is identical on all module/shift rows at one geometric endpoint or intermediate vector. These rows form a complete spectator prefix for a single child interchange after the packed extraction scan. They carry arbitrary independent data. Replacing R individual calls by one call on R prefix fibres preserves the total encoded volume, without assuming the data agree.

At a repair node, each such geometric group has at most 1/N of that node's volume. Distinct physical maps stay separate polynomial coarse roles. Direct order-three transforms at finite leaves use m swaps, and leaves are processed sequentially. Each leaf has fraction 16^(-h)<=1/16 of the root repair volume. Since N>=512, every main spatial call has volume at most one sixteenth of its root, in particular below one quarter.

Two predictor evaluations cost 2Dp Rpen per row per finite repair node. Four sequential child phases each have fraction 1/16, total mass 1/4. Hence either order-three transform or inverse has

    sigma_F/W <= (8/3)Dp Rpen+m4^(-h).

The final exact three-transform swap word gives Qm in (CI3). Pointwise diagonals are ordinary scans. The complete map restores every occupied reserve and returns the exact main field-swap product on every independent row.

## 6. Repair roles and on-demand controls

Use w alone as the invariant module. The factor32 belongs to coarse roles. SR's real checks give32s0 coarse roles and are padded to B roles; S=Bw. Two families contain2B roles, exactly2S=R/16 rows.

For a child phase combine sixteen parent repair blocks:16 times2B becomes32B child shift/duplicate roles, while the repair-block count divides by16. Labels remain unchanged. The explicit map `(parent block=16r+q,label,family,check)` to `(r,label,child shift,child duplicate)` uses combined index `(2q+family)B+check` in `[32B]`, then divides it into shift/duplicate. Only polynomial-size coarse indices move; w remains the suffix. The inverse restores parent roles after return. The scan cost is Section3's polynomial invoice.

SR constructs its key using m comparison-trit passes in original physical address order after the completed forward converter. Reading the entire long address per small finite-field scalar is neither needed nor allowed. Tagged width after i passes is2eK+2i. Per-record containing-set computation, small Vandermonde inversion and discrepancy table cost polynomial m; no3^m table is listed. The complete inverse converter follows the table in its exact order-three word order. Strip all spectral tags before a recursive converter call, so child fractions refer to raw2eK-bit records. The temporary tags are ordinary paid workspace, not an increase in recursive call volume.

## 7. Fixed radix and spatial recurrence

B2's address factors are valid modulo every power of3. Set

    ell=ceil(log_3 W), Bbatch=3^ell,
    Cbatch=W ceil(Bbatch/W), beta=Cbatch/Bbatch<2.

All descriptions have polynomial-m bits since log W=poly(m). PB exposes W rows from ell leading digits by a packed scan, without a radix above W or a W-way tape split. Remove padding only after the completed identity preserves each leading row's original value.

At width e let f=floor((e-ell)/(m+2a)). If f<1, direct digit swaps cost polynomial(m) per symbol, since e<ell+m+2a=poly(m). Otherwise run the packed main template, merge and clear its arrays, then perform2a full-volume reserve descents and the ell leading plus bounded-remainder digit exchanges. Those direct exchanges have fixed radix3 and polynomial-m count. The actual recurrence is

    T(e)<=m^C+(beta Qm+2a)T(f), f<=e/m.                 (CI6)

(CI4) dominates beta<2, so induction with the polynomial base gives eta^(-1)m^C max(1,e)^rho. Actual generation of formulas, labels, rectangles, binary rank factors, dyadic operation lists, field/nodes, role maps and big integers W is polynomial m. No polynomial-W generation step is present.

## 8. Encoding, descriptors and all visited cells

Encode K records in2eK=O(log m) bits and perform coordinate field arithmetic on fixed binary tapes. Original bits may be embedded as0,1 once and decoded after the exact completed swap, with polynomial-m cost. This format stays fixed through every spatial descent; there is no repeated per-depth embedding. Full basis descent is optional and unnecessary for this profile.

After beta<2 padding, each grouped main child has volume below half its parent. Park at most m^C times parent volume on end-access stacks; payload sums geometrically. Finite repair has the stronger factor1/16. Clear main arrays before the full-volume reserve descents; only descriptors remain parked. Reuse regions across siblings and phases.

A descriptor has polynomial(m)+O(log(V+2)) bits: coarse counters, field widths, spectator ranges and return state. Schoolbook descriptor arithmetic has one absolute polynomial degree, repeated polynomially many times per local instruction. Thus its total local work is m^C(1+log(V+2))^E for an absolute E, bounded by another m^C V: the supremum of (1+log(x+2))^E/x over x>=1 is finite. This is not a template-dependent exponent silently absorbed into a constant.

Non-base spatial width shrinks at least by m. The stack depth is O(log(e+2)); complete fields imply encoded V>=3^(2e). Hence all parked descriptors fit m^C V. Global template storage is polynomial m and can be retained once or regenerated within the same bill. These are bounds on cells ever visited because stack/work regions are reused.

Binary-to-radix3 range padding increases volume by less than9 and uses e<=1+u. The source ordered scans implement padding/restriction in linear volume plus the same descriptor bill. This proves(CI5).

## 9. Quantitative consequence and open composition

Dg is at most twice the previous coarse dimension bound. Thus

    log2(Dg(1+lambda))
       <=3 log2(m)/d+O(d² log log(m+4)).

Choose d a power of two in[KJ,2KJ] with sufficiently large absolute K, and log2 m=C J³ log2(J+2) with sufficiently large absolute C. The explicit bounds give a strict fixed margin in(CI4) for rho=1/2+1/(2J): Dp=O(sqrt m), the finite leaf term isO(sqrt m), and a=m^o(1). The new Cg only enlarges the effective absolute parameter constant. The compact constructor can check the exact invoice before accepting its parameters.

The interchanger therefore has polynomial-m prefactors, generation and space at the established cubic-logarithmic parameter scale. This removes the exponential matrix/geometry interface from the preceding expanded construction. Numerical Walsh, integer assembly, precision, common-cap scheduling and the final envelope must still be composed and independently reviewed. No endpoint or positive polynomial-s saving is asserted here.

## Credits

Shared physical endpoints and spatial recursion are OpenAI source results. S002 supplies the count/shift, scalar-label and order-three identities. S003 uses B's succinct factors and explicit dyadic geometry, C's on-demand repair, lead packed batching and A's independent geometry review. Prepared for Jerry Chen (@CubeJerry) with substantial OpenAI AI assistance. No full multiplier execution, Lean refinement or independent human referee certification is claimed.
