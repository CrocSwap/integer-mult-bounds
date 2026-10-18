# Explicit cap-safe repair of W_i four-input degeneracy

2026-10-09. Universal sufficient mathematical construction, with independent exact C++ Bareiss checks. No formalization or new kappa claim.

Use p=12 physical pairs in dimension24, G=I-J/9. Fix pair i and its endpoints i0,i1. Let z_a=B_a+e_i0 for a!=i, and d=e_i1-e_i0. For a set K of k other pairs, W_K=span({z_a:a in K},d). Its Gram is [[2I_k,-1],[-1^T,2]], determinant2^(k-1)(4-k). Four-input nodes genuinely fail nondegeneracy.

Fix the four-pair set A of one such node. Define the INTEGRAL padding vector

    w_A = 11 e_i0 + 2 sum_(a notin A union {i}) B_a.

For every future bad target T=B_i+e_j with j belonging to a pair outside A union{i}, the true read-cap equation is satisfied:

    (3 chi_T - 1) dot w_A =3(11+2)-(11+2*14)=0.

Thus this ONE fixed vector lies in every future receiver cap of the four-input node. It does not add a new source or fresh value; it enlarges its operator frame by one real dimension. All extra child increments and adapters are still paid.

For any ancestor support K containing A, |K|=k between4 and11, extend the W_K basis by w_A. Its half-scaled w=w_A/2 has G norm2; G pairings with z_a are -1 on A and+1 on K\A, and with d are -11/2. Eliminating the 2I_k block leaves the2x2 Schur complement

    [[(4-k)/2, (k-19)/2], [(k-19)/2,(4-k)/2]].

Therefore the exact Gram determinant with the integral padding is

    det Gram_G(z_K,d,w_A)=15 *2^k *(2k-23).

This is nonzero for every relevant integer k4..11. Its prime factors are at most13. Clearing G's denominator contributes9^(k+2), which only adds prime3. The largest exact cleared determinant in this range has absolute value78086118246266880, below2^57 and hence far below the retained2^80 prime guard.

The same construction works after any permutation of physical pairs and exchanging the two endpoints of i. No Gram search or assumed normalizer oracle appears.

## A literal module avoiding simultaneous padding conflicts

allbut-n11.json is an exact37-addition C++ module for all11 leave-one-out sums on11 singleton weights. It uses the balanced interval split5+6 and memoized disjoint support sums. Its only support-size4 nodes are the five sets A obtained by removing one element from the first block of five. Each has ONLY its own unique final support-size10 output as a later scalar consumer. The right block's leave-one-out nodes have size5, not4. Thus each repaired four-input branch uses one w_A; distinct padding vectors never have to be merged into the same later helper frame. Full size5/6 helpers and every other size are already nondegenerate.

Assign the new six-dimensional frame W_A+<w_A> to the offending node, and the new twelve-dimensional frame W_K+<w_A> to its own size10 output. All other nodes retain their old W frames. Incoming operand frames are subsets of their new destination frames. Each padded output still lies in both endpoint target read caps by the formula above. Its largest local frame dimension is12, comfortably below h24. After this output read, its complete paid tail remains in the full ambient frame and can execute the same inverse transparent schedule.

The output's extra dimension MUST enter the actual frame/path histogram; this is a complete cap/nondegeneracy repair, not a claim that dimension padding is free. The parent owns the complete root-chain changes, dirty response computation, source-pair controls and final recurrence bill.

C++ source w-padding.cpp checks all14 future target cap equations exactly, constructs every ancestor Gram directly in integer coordinates, and computes each determinant by fraction-free Bareiss elimination using128-bit integers. It checks equality to the displayed factored formula. w-padding-check.json stores the exact results. allbut.cpp and allbut-n11.json give the explicit scalar module, separately checked on support masks.
