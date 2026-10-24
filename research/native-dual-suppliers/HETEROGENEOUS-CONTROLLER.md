# Heterogeneous seven-axis suppliers with exact port transport

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

## Physical interface

Consider two independently admitted local words with 112 independent main pairs and 408 independent helper fields. Their main endpoints, after explicit monomial wrappers, are direct sums of seven-axis primitives with a common central Q:

    A = diag(D,D) S_y(Q^-1),
    B = diag(1,Q) A,
    C = A diag(Q,1).

Here D acts on seven fresh coordinate axes, Q on a separate central axis, and Q² is an explicit monomial. Each B-provider call has 56 A and 56 B ports. Each C-provider call has 56 A and 56 C ports. Their logical words, paid profiles and helper profiles remain separately authenticated; equal counts of main types do not identify the underlying helper inputs.

Backward interfaces are the actual inverse transposes. To compare them with the retained source controller, explicitly apply input-Y Q², output-Y Q^-2 and output D² on both fields. The resulting source-convention backward A is diag(D,D) S_x(-Q), backward B has its extra Q^-1 on output Y, and backward C has its extra Q^-1 on input X. The extra phases and even powers are retained as monomial wrappers. These corrections do not add recursive Gaussian calls.

## Arbitrary placement of the 56 exceptional ports

Let sigma be any permutation of the 112 main pairs. Apply the corresponding permutation to both input banks X_i,Y_i, execute the local word, then apply the inverse permutation to both main output banks. Leave helper banks untouched. The main endpoint is the conjugate direct sum, so any chosen 56 ports can carry the exceptional B or C type. The paid profile and all 408 independent helper endpoint operators are unchanged.

This conclusion uses the admitted direct-sum endpoint: each helper output depends only on its own arbitrary input, and no helper input contributes to a main output. Therefore main-only pair permutations introduce no disguised helper identification, sharing, loss of arbitrariness or changed input ABI. These zero cross-block facts are verified by the free-group-algebra endpoint certificate. No per-occurrence inconsistent warp map is chosen.

The pair permutation is an actual native operation. Decompose the permutation of 224 banks into at most 223 transpositions. Each transposition is the literal reversible scalar sequence x+=y; y-=x; x+=y; y=-y. It swaps the two fields exactly, preserves every independent input and uses no overwrite/CLEAR on borrowed data. One constant guard bit covers intermediate sums. Input plus inverse output use at most 446 transpositions, hence at most 1,784 scalar bank passes. At at most 16 native operations per complex-record scalar pass this is 28,544 V, leaving an additional allowance of 30,000 V including loop/index bookkeeping. Pointer relabeling may be cheaper but is not required. An owned-temporary cycle-copy implementation is also possible on ordinary RAM, but is unnecessary for the stricter reversible-scalar protocol.

In particular one may use two fixed groups of 56 global ports and independently choose at each LOCAL which group receives the exceptional type. This is a genuine new degree of freedom beyond keeping the same exceptional port class at every stage. A computed assignment still needs its complete chronological incidence check.

## Exact row-gauge consumption

At each controller row use a central gauge Q^a, retaining the full integer exponent and accounting for parity only when pricing Gaussian rank. For a logical ADD with coefficient epsilon Q^k, the physical coefficient is epsilon Q^(k+a_target-a_source). An odd exponent requires one rank-one Gaussian call; an even exponent is an explicit monomial. A temporary COPY/transform/ADD/CLEAR implementation preserves the source and pays that Gaussian exactly once. It uses only owned temporary erasure.

For an A-type LOCAL, input row parities must agree; the two outputs keep that common parity. For B, input parities agree and physical Y flips at the output. For C, input parities are opposite and both output parities equal the input Y parity; equivalently C has an input-X flip followed by A. The same parity rules hold in the backward source convention after the stated monomial wrappers. The X/Y identities refer to physical banks, not to whichever row is the shear source in that orientation.

The controller's scalar RIGHT boundary program runs first, then its physical events, then its scalar LEFT boundary program. Carry the gauges through both boundary programs and price every crossed-parity ADD. Signed swaps carry their gauges with the swapped rows. An optimizer that ignores these boundary programs does not establish a usable diagonal target.

## Exact whole invoice

Let n_B and n_C be the numbers of the two provider calls, with n_B+n_C=p+2 in the retained p-pair controller. The helper targets are the multiset sum n_B H_B+n_C H_C, with a fresh independent copy of every helper at every call. The local Gaussian paid jobs are n_B P_B+n_C P_C. Add each actual seven-axis IDLE job, each actual rank-one query/ADD/gauge-correction job, and every additional explicitly emitted recursive child. Do not also include the old thin-query bill if those queries were replaced by the actual gauged jobs; that would double-count.

For a final diagonal row with retained Laurent monomial Q^m product_s D_s^(e_s), its actual central rank is (m+a_final) modulo two, not a_final by itself. Its total target rank is

    7 sum_s e_s + ((m+a_final) mod 2),

for the retained 0/1 fresh-slot exponents. Initial gauges are frozen. All even powers, signs and inverse D orientations belong to explicit monomial normalizers. The complete formal Laurent identity must be replayed using the emitted gauged controller, not merely priced from a mask.

The exact whole rank-mass surplus is sum(rank*target_count)-sum(rank*paid_count) for this rebuilt invoice. A positive rank-mass surplus is only an initial screen. A strictly positive complete moment at a specified exponent, the mirror/critical majorant, finite uniform compiler, precision and native outer assembly are required before claiming a new kappa.

## Spectator and coordinate embedding

A B-provider's ninth local coordinate is a spectator on the main typed endpoint but may be active in independent rank-nine helper jobs. It must be embedded as a genuine extra coordinate chosen outside the central axis and current seven-axis block; another stage's fresh coordinate suffices because p>=2. The complete global address space has rank 1+7(p+2), so this extra coordinate exists. Main output identity on that coordinate is an actual typed-interface fact, not a reason to discard its helper action. The borrowed coordinate labels addresses; it is not borrowed storage and does not identify two independent helper fields.

A C-provider whose complete admitted word lives in an eight-plane may use only central plus seven local coordinates; its ninth identity spectator remains explicit. Every whole-job normalizer is formed on its actual active coordinates. No block-eight diagonal credit is inferred from a helper-only padded spectator.

## Local native allowance

For the frozen source words, each orientation contains 17,453 scalar events, 240 native warp events, 448 inherited adapter markers and at most 3,195 paid Gaussian jobs. All scalar numerator/denominator magnitudes are at most 8. Allow two exact nine-axis monomial normalizers per paid child, the native warp monomials, all explicit main wrappers, the backward-convention corrections and both helper whole-job normalizers. Fewer than 9,000 nine-axis lifted monomial operations suffice per local call. This is a conservative count, not a practical runtime estimate.

A lifted fixed nine-axis monomial is a binary 9×9 block map and a Z4 quadratic phase on nine f-bit blocks, with arbitrary identity spectators. Its address is formed with at most 81 block XORs and fixed shifts/masks. Compute each phase using at most 45 block parity/Hamming-weight-mod-4 functions; a parity chunk table on max(1,floor(f/16)) bits gives at most 31 chunks per f-bit block. Including the table setup, scatter/gather, phase multiplication, loop/index operations and fixed metadata, 10,000 V native operations per such map is a deliberately loose eventual bound. Tables are prepared by explicit recurrences and cost O(V), not an oracle. Thus fewer than 9e7 V operations cover these monomials; 64 operations per scalar event, the bank permutations and a further million-operation metadata reserve leave the nonrecursive LOCAL allowance below 10^8 V. Gaussian child work is charged separately in the paid profile. This bound concerns the local primitive, not the entire p-stage controller or its larger main whole-job normalizers.

All statements hold at each digit-column width f by the retained exact free-group-algebra evaluation theorem and blockwise tensorization of address-operator identities. They do not tensor the field-level 2×2 matrices. The full native construction remains source-bound in its inherited Gaussian, compiler and analytic premises. This note establishes a sufficient heterogeneous-consumer and exact accounting framework; it does not assert an unobserved profitable provider/gauge schedule.

Credit the actual B/C supplier constructions and source owners; DaysSky, Cinna Davis, Cao Yifan, the retained controller authors, Dugongue's native Word RAM and frame-interface work, zxv, Jacob Alan Sussman and all original notices. The useful new mechanism is per-call physical port transport together with an honest heterogeneous profile, rather than repricing a changed endpoint as the old common supplier.
