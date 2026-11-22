# Tensorizing local circuits without dimension padding

Status: an algebraic compiler and scan-cost lemma. It reduces a tensor product of different bounded-depth local circuits to a bounded sequence of simultaneous binary Hadamard calls and diagonal scans on the **same** data volume. The retained supplier must support the stated Hadamard call on selected local bits and restore the agreed endpoint record order. No new fast-transform supplier is asserted here.

## 1. Interface and conclusion

Let N=2^m and let g axes each have N local coordinates. A coarse-label block contains V=N^g data records in lexicographic local-coordinate order. On axis a let C_a be an N-wire linear circuit of depth D; every layer consists of disjoint invertible two-coordinate gates and one-coordinate diagonals. The permitted gates are bounded shears, swaps, FFT butterflies, and diagonals. Circuits, pair matchings, coefficients and depths can differ by axis and by coarse label. Their tables are fixed independently of data values.

Write H=[[1,1],[1,-1]]. A simultaneous Hadamard call means the tensor product of one H acting on one selected bit in each axis, with all remaining local and coarse coordinates as spectators. It acts on existing 2^g-coordinate fibers inside the N^g records; it allocates no new coordinate. The bit selected in an axis may be prescribed by the compiler.

After padding shorter circuits by identity **operations**, the tensor product C_1 tensor ... tensor C_g is a sequence of

    at most (8m+2)D simultaneous H calls

and O(Dm) tensor-diagonal scans. A tensor diagonal has the form

    d(i_1,...,i_g;c)=product_(a=1)^g d_a(i_a;c),

where c is the fixed coarse label. Each diagonal scan uses O(1) amortized coefficient multiplications and O(1) amortized coefficient-table record movements per data record, after loading gN local values. The number of arithmetic-data coordinates remains exactly N^g throughout.

If all local gate coefficients and inverses are bounded by B and all original prefix and inverse-prefix norms by Lambda, the compiler's local prefix bounds are Lambda times poly(B), up to absolute constants. For polynomial B and Lambda this is N^O(1). The tensor-prefix logarithmic bound is O(g log N). More generally depth D=polylog(p), B=poly(p), N=poly(p) gives an O(g polylog(p)) guard even without a stronger prefix theorem.

An outer similarity whose logarithmic range is Q_a on axis a adds only sum_a Q_a. Therefore the retained phase-cell case Q_a=O(a d) uses

    p + O(g a d + g polylog(p))

working bits. The condition g a d+g polylog(p)=O(p) is sufficient for O(p)-bit records.

## 2. Fixed Hadamard words, including zero shears

All formulas below are matrix-product order; execution reads right to left. Let U(t)=[[1,t],[0,1]]. Direct multiplication gives

    H diag(2,1) H diag(-3,1) H = [[-8,-10],[0,-6]],
    diag(-1/8,-1/6) H diag(2,1) H diag(-3,1) H = U(5/4).

For q nonzero, conjugate by A_q=diag(4q/5,1):

    U(q)=A_q diag(-1/8,-1/6) H diag(2,1) H diag(-3,1) H A_q^-1.

This has three H factors. To include t=0 with uniformly invertible diagonals, choose a known B>=|t| and c=2B+1. Then

    U(t)=U(t+c) U(-c).

Both parameters have magnitude at least B+1 and at most 3B+1. This is a **six-H word for every t**, with all scalar coefficients and inverses bounded by poly(B). There is no division by t and no case split at t=0. Transpose the word to obtain the same six-H count for lower shears.

There are two bounded identity words:

    I = (1/2) H H,
    I = diag((1-i)/4,(1+i)/4) H diag(1,i) H diag(1,i) H.

The second identity uses three H factors. Its middle product before the leading diagonal equals diag(2+2i,2-2i). Complex coefficients are permitted by the retained complex H interface.

Consequently every gate type can be given **exactly six H factors**, separated by diagonal matrices:

- Upper/lower shear: the six-H word above.
- Diagonal, including I: append three two-H identity words.
- Swap J: use J=(1/2)H diag(1,-1)H, then append two two-H identity words.
- FFT butterfly H diag(1,w), optionally scaled by 1/sqrt(2): append a two-H identity and a three-H identity. Here |w|=1.

Combining neighboring diagonal matrices puts every word in one common alternating shape with six H factors and seven diagonals. Thus different gate types, zero parameters and inactive pairs can coexist in one simultaneous schedule without branches or padded data coordinates.

## 3. Every matching can be routed to adjacent pairs

For one local layer, assign its oriented pairs (i,j) to positions (2k,2k+1). Unpaired coordinates are assigned arbitrarily to the remaining positions, in pairs carrying diagonal or identity gates. This defines a permutation pi on exactly N coordinates. The layer equals

    P_pi^-1 (direct sum of adjacent-pair gates) P_pi.

We use a Beneš network of 2m-1 switch layers. At each layer all switches join indices differing in one fixed bit; the bit sequence is

    0,1,...,m-1,m-2,...,1,0.

Here is a constructive proof of rearrangeability. Form a bipartite multigraph whose left vertices are input pairs {2j,2j+1} and whose right vertices are output pairs {2k,2k+1}. Input i supplies an edge to output-pair floor(pi(i)/2). Every vertex has degree two, so each component is an even cycle (parallel edges are allowed). Alternately color each cycle's edges 0 and 1. The first switch sends an input edge into the subnetwork of its color; the last switch sends that color to the required output parity. Each color class induces a permutation on N/2 pair indices. Recursively route both color subnetworks in parallel. This gives exactly the displayed bit sequence and uses no storage coordinates.

The switch is either I or J. Both are obtained from the common two-H word

    S_epsilon=(1/2) H diag(1,epsilon) H,
    epsilon=+1 for I, epsilon=-1 for J.

Thus all axis-dependent switch controls are diagonal entries. A physical switch on bit k simply uses a simultaneous H call selecting bit k in each axis. No interstage wire shuffle is needed. If a supplier accepts only a contiguous selected-bit field, the existing paid bit router must gather that field and undo the gather; that is a supplier-interface cost, not an uncharged permutation.

Each forward or inverse Beneš route uses 2(2m-1) H calls. The adjacent gates use six. Hence one original matching layer uses

    2[2(2m-1)]+6 = 8m+2

H calls. The schedule is identical on every axis and every coarse-label block; only diagonal tables change.

## 4. Tensor fusion is literal multiplication, not a sum expansion

Let the compiled axis-a circuit be D_(a,L) H_(a,L) ... H_(a,1) D_(a,0), with the same number and arrangement of H factors. Kronecker multiplication gives

    tensor_a C_a
      = (tensor_a D_(a,L)) (tensor_a H_(a,L)) ...
        (tensor_a H_(a,1)) (tensor_a D_(a,0)).

Every tensor of diagonals is a single diagonal scan. Every tensor of binary H factors is one simultaneous H call. This introduces neither a sum of 2^g branches nor a 2^g padding factor. The 2^g-dimensional Hadamard fibers are subsets of the N^g existing coordinates.

An axis with no work at a particular original depth receives an identity layer, routed and compiled with the same fixed shape. Its intermediate H operations are still present, but the complete local word is I. Coarse-label variation is equally harmless: for each fixed label the identity above holds separately, and the whole data operator is a direct sum over labels.

## 5. Uniform intermediate bounds and precision

A completed switch route is a permutation and has norm one. Each partial switch word has absolute constant norm and inverse norm. Between original local circuit boundaries, at most one original gate word is partially executed. Its length is constant, and its scalar coefficients and inverses are poly(B); all different pairs act as a direct sum. Therefore

    max_prefix ||C_compiled,prefix||,
    max_prefix ||C_compiled,prefix^-1|| <= poly(B) Lambda.

The length O(D log N) does not require multiplying this polynomial bound afresh at every stage: completed original prefixes already have bound Lambda; completed route and padding words have their exact intended endpoints. The corresponding suffix bound is also polynomial when the original endpoint and inverse-prefix bounds are.

For g tensor factors, the operator norms multiply, so their logarithms add. A microbox coarse-label direct sum takes the maximum over labels, not a product over labels. Hence polynomial local bounds give exp(O(g log N)); using only the rough original bound Lambda<=(2B)^D gives exp(O(gD log B)). Adding the original cell similarity contributes exp(sum Q_a).

The number of compiled stages is polylog(p). Allocate each rounding or supplied-transform error below the final tolerance divided by this stage count and the prefix/suffix amplification. This costs O(g polylog(p)+sum Q_a) guard bits. Supplier-internal precision charges still must be those already guaranteed for the simultaneous H call; this compiler does not erase them.

## 6. Product diagonals with constant amortized scan cost

Fix one diagonal stage and one coarse label. Load the gN coefficients d_a(i) on a coefficient tape in axis order. Use base-N lexicographic enumeration with axis 0 fastest. Store suffix products

    P_j=product_(a=j)^(g-1) d_a(i_a),       1<=j<g,

and P_g=1. A normal record uses d_0(i_0) P_1, one coefficient multiplication. If the odometer carries through axes 0,...,k-1 and increments axis k, recompute only P_k,P_(k-1),...,P_1. A carry of depth at least k occurs at most V/N^k times. Therefore the total extra products are bounded by

    V sum_(k>=1) k/N^k = O(V),

plus O(g) initialization. No division by d_a(i) is used, so this method also permits zero diagonal entries when an external application permits them. Every cached product is recomputed from current factors, never updated by a long chain of multiplicative ratios, so numerical drift does not depend on the number of records scanned.

The same accounting works on a fixed number of tapes. Keep the coefficient-tape head normally in axis-0's N-record table. Rewinding that table costs O(N) once per N records. A depth-k carry visits the needed tables up to axis k and returns, moving O(kN) coefficient records. Summing over carries gives

    O(V sum_(k>=1) kN/N^k)=O(V)

record moves. The suffix-product tape is accessed near its front except on carries, with the same geometric bound. Counter/address arithmetic costs only polylog(p) per record. This does not require g work tapes or a random-access lookup every record.

The table loading cost is O(gN) records per coarse block and stage. For N>=2 it is O(N^g), including small g, and polynomial-time table construction is negligible per N^g block in the retained asymptotic regime g=p^beta tending to infinity. If tables are supplied rather than constructed locally, no additional assumption is needed. Both generation and loading costs must be charged once per visited coarse block, not silently once for the entire input.

At O(p) working precision, O(1) amortized scalar multiplications per record and O(1) record movements cost O(V_bits polylog(p)) under the retained pointwise-arithmetic kernel, where V_bits counts bit volume. There is no g V_bits coefficient-generation term.

## 7. Exact controls

`check_tensor_compiler.py` constructs the network controls and all fixed words. `TENSOR-COMPILER-CONTROLS.json` records:

- every permutation for N=2,4,8, including all 40,320 permutations at N=8;
- 100 random permutations each at N=16,32,64;
- exact symbolic checks of upper/lower zero and nonzero shears, diagonal, Swap and FFT words;
- an exact two-axis N=4 replay with different axis matchings and gate types: 16 data coordinates, all 256 input-output matrix entries, 18 simultaneous H calls, no dimension expansion.

The finite controls support the constructive proofs; the cycle coloring, word identities, Kronecker identity and geometric scan sums establish the asymptotic statements.

## 8. Cost substitution into the retained supplier

Suppose a simultaneous H call on g selected bits, across V_bits bits of data and spectators, has paid cost O(V_bits g^(1-q) polylog(p)). Suppose also that any required bit-field gather/restore has cost O(V_bits g^(1-a_bit) polylog(p)). For D=polylog(p), N=poly(p), the compiler uses only polylog(p) such calls, and its diagonal scans cost O(V_bits polylog(p)). Thus the grouped local circuit costs

    O(V_bits [g^(1-q)+g^(1-a_bit)+1] polylog(p)).

When a_bit>q and 0<q<1, this is O(V_bits g^(1-q) polylog(p)). The compiler therefore preserves the supplier saving q. The substitution is valid with different local circuits and control masks per axis/coarse label, provided their uniformly bounded tables are generated within the separately charged polynomial preprocessing budget. It introduces neither a g V_bits full-scan term nor a 2^g volume multiplier.


The retained supplier returns the normalized butterfly H0=H/2. After one
simultaneous H0 call, multiply all coefficients by 2^g to obtain the raw H
used by these identities. This is one binary-shift diagonal scan and adds
O(g) precision guard. The support audit in `SUPPLIER-SUPPORT-AUDIT.md`
justifies the stated call cost globally on the complete dyadic tensor,
using only O(g log p) selected-neighborhood positions plus support-local
helper reservoirs. It does not require g log p bits inside any one axis.
