# Source-bound native Word RAM multiplication with saving 0.0030201655

## Precise claim and retained mathematical inputs

On the standard finite-word random-access model with indexed memory, add/subtract, shifts, Boolean operations, comparison and multiplication/division of O(log n)-bit words, the constructions below give packed n-bit integer multiplication in

    O(n/(log n)^kappa),  kappa=0.0030201655.

The word-width coefficient is a sufficiently large fixed constant. This is a Word RAM claim, not a stronger multitape-TM exponent. It is conditional on the correctness of the specifically retained algebraic and analytic predecessor proofs listed next. It imports no TM algorithm or TM complexity theorem. No new unknown compiler, stability oracle, fast multiplier or unpriced coefficient instruction is a premise.

Retain these mathematical source results:

1. The literal all-input dyadic native identity and chronological finite compiler of PR #4470/#4483/#4532/#4535, including distinct productive fields, all paid jobs, owned scratch restoration, exact endpoint phase normalizers and the finite compiler majorant. The pinned #4535 certificate funds a fixed uniform provider saving q_C=0.0030201656 at N=2^(10^12). In particular P_leaf/W<N^(1-q_C), with every complement, leaf, copied query and owned job counted. The enormous finite program is algorithmically specified, not materialized here.
2. The actual Gaussian/Poisson identities, prime-grid cyclic embedding, rounding/recovery theorem, and coefficient error formulas of the retained analytic reduction. Fine prime padding is specifically PR #1786, as bound in FINE-PADDING-COMPOSITION.md; fractional-shift accretive Toeplitz circuits are PR #1758's GAUGEFREE-INTERIORS.md, using the constructive SHALLOW-TOEPLITZ and TENSOR-COMPILER recipes. These are mathematical identities, circuit constructions and error bounds, not their tape tariffs.
3. The exact dyadic core/halo and sparse-axis decomposition: full complete-tensor H calls preserve coarse labels, and each sparse axis operator acts only on its own explicitly generated boundary slabs. This is the actual decomposition in the cited capped/fine-padding construction, including original physical period cuts and original-input halo repairs.

The new contribution is a concrete finite-word execution and cost assembly for those actual recipes: native short products and FFTs, paid sublinear coefficient/index tables, constant-word scalar evaluation, direct indexed sparse visits, batched boundary arithmetic and explicit nine-row native accounting. The statement remains source-bound while the predecessor algebraic/analytic proofs retain their stated status. Finite replay checks cannot independently establish their universal correctness.

## Parameters and model

Write p=Theta(log n), d=Theta(p^epsilon), g=Theta(p^beta), choose alpha^2=Theta(log p), and use its spare bound alpha^2<=p^r eventually. Fix

    q_C     = 0.0030201656,
    q       = 0.00302016555,
    stop    = 10^-9,
    kappa   = 0.0030201655,
    epsilon = 1-10^-8,
    beta    = 1-3*10^-8,
    r       = 10^-9,
    c       = 3/32,
    layout  = 10^-10,
    xi      = epsilon*(1+q)-c+layout.

Every constant is fixed before n varies. Working scalar components have C p bits for a sufficiently large fixed C. Their exact raw products, sums and divisions use a fixed number of machine words. Multiplication is used only on these bounded words; no whole n-bit product is a unit-cost instruction. Signed complex scalars are represented by two signed dyadic components.

The input and output are ordinary packed words. Digitization, final carry propagation and packing cost O(n/log n) operations. All target-box coefficient counts T satisfy T p=Theta(n). Original axes have bit length ell=Theta(p/d), and actual axis lengths 2^Theta(p/d)=n^{o(1)}. In every growing range, all fixed finite-template constants and every fixed polynomial descriptor preparation are absorbed by one explicitly enlarged eventual cutoff. No practical cutoff or implementation size is asserted.

## 1. The actual finite provider becomes a native bounded-word kernel

Execute the fixed expanded provider word from retained input 1, with each bank an indexed array and every owned allocation distinct. Scalar dyadic ADD/SCALE/COPY/CLEAR instructions use direct bounded-word arithmetic. Completed child endpoints are exact unitary Gaussian operators on arbitrary bank contents; source coefficient/denominator and restoration bounds give a fixed linear guard C0 e at rank e, or the stronger fixed-template depth guard when applicable. Since e<=d or g and epsilon,beta<1, C0 e=o(p). No data-dependent test changes the linear identity.

Its rank recurrence is the actual whole-program leaf recurrence, with strict moment P_leaf/W<N^(1-q_C), ordinary base costs and rank remainders paid. The ordinary induction gives O(2^e e^(1-q)) word operations up to fixed logarithmic factors and fixed-template constants. On T records, applying the kernel as a direct sum over selected-bit fibers costs

    O(T e^(1-q) polylog p).

The endpoint is the canonical selected-axis Gaussian kernel with all distinct independent productive inputs and all owned scratch restored. Phase frames convert it to the actual simultaneous normalized H calls in TENSOR-COMPILER.md. Owned banks are memory banks with fixed multiplicity; they receive no productive credit.

A finite rank-N compiler is fixed independently of n, despite its extreme size. Its enumeration, scalar coefficients and matrix/phase recipes are actual finite algorithms. Runtime preparation is not permitted to query an unspecified optimal circuit. One may conservatively allocate a distinct owner for every expanded allocation, exactly as #4535 specifies.

## 2. Native metadata and coefficient tables are explicitly paid

One fused Gaussian group uses g original axes. All their complete physical coordinate bits occupy

    K=O(g ell+g log p)=O(p^(beta+1-epsilon)+p^beta log p)=o(p).

For each of the polynomially many group/stage types, enumerate every K-bit key and run the actual local coefficient/address/predicate recipe. This includes phase-cell classification, holes, capped boundaries, anchored fractional shifts, the prescribed matching/Benes controls and separable diagonal values. The remaining axes are spectators, so no other coordinate is needed to determine these functions. Tables store O(p)-bit output values or addresses. Their total time and space are

    poly(p)*2^O(K)+poly(r,p)=n^{o(1)}.

Here r=max(s_i,t_i)=n^{o(1)}. First prepare each one-axis coefficient/factor/page catalogue by its actual polynomial(r,p) constructor, once per axis. Each group-key evaluation then combines/lookups those stored one-axis recipes with polynomial(p) work. This pays global axis preparation separately from the thin group tables.

Coefficient construction starts at precision Cp+O(p^2 log p) and is performed with explicitly implemented multi-limb integer/rational arithmetic. Global one-axis Schur, factor and generator construction may have dimensions and exact rational numerator/denominator bit heights polynomial in r and p, rather than polynomial in p alone. Grade-school limb addition, multiplication, long division and exact finite rational elimination therefore take polynomial(r,p) native word operations in total for each such constructor. Gaussian exp/root coefficients use convergent rational series and certified remainders at that paid precision. Local polynomial-size circuit generation and group-table evaluation are charged separately as above. No polynomial(r,p)-bit scalar is treated as one machine word. Only source-conditioned O(p)-bit guarded coefficients are retained online: polynomial(r,p) error/count factors add O(log r+log p)=o(p) guard bits, while the actual conditioning and normalization bounds supply the remaining Cp allowance.

Project a group key from the complete O(p)-bit address by a precomputed Benes permutation of word bits, implemented with O(log p) masked shifts; mask away spectators. Its control masks are generated in polynomial(p) preprocessing. Lookup is one indexed word operation. Hence classification and diagonal/coefficient access take polylog(p) native work per visited record, without a hidden factor g. Unlike TM transition batching, these tables encode explicit algebraic coefficient and coordinate functions; no TM occurs in their definition or evaluation.

For the main simultaneous selected-bit kernels, deposit maps on 2^e local bit indices and every fixed-template basis/quarter-phase map are also explicitly tabulated. They require poly(p)*2^O(d+g)=n^{o(1)} preparation. Enumerating complementary submasks by next=(current-mask)&mask visits all selected fibers without PEXT/PDEP or one extraction per axis. Fixed-dimension binary column lifts use a fixed number of whole-block XORs. Arbitrary physical bit permutations use the paid word-level Benes recipe above.

The global FFT twiddle product and global separable normalizations may instead use the mixed-radix prefix-product scan: suffix products are recomputed only on odometer carries, yielding O(1) amortized scalar work per record, with no division by possibly zero entries. No g-fold product is silently charged as a unit scalar instruction.

## 3. Main simultaneous transform

The exact common-level tensor FFT decomposition has ell=Theta(p/d) rounds. Its local H calls are precisely the native selected-bit kernel of section 1, with separate charged recordwise twiddles. Therefore

    main = O(T ell d^(1-q) polylog p)
         = O(T p^(1-epsilon*q) polylog p).

All addressing, fixed-template normalizers, owned scratch and base exits are included in the native call bill. Direct word-addressed permutations replace tape routing; a separate fast BIT supplier is unnecessary.

## 4. Fused actual Gaussian adapters

Fine source primes have theta=Theta(p^-2). The shifted Gaussian symbol and its accretive section/Schur bounds are the actual GAUGEFREE-INTERIORS theorem. A dyadic interior of cap B=p^xi has only the quadratic chirp range O(alpha^2 theta B^2); the linear Gaussian drift has been absorbed exactly into its shifted Toeplitz kernel, not erased. The shallow in-place Toeplitz circuit has polylog(p) rounds and polynomially bounded local coefficients/prefixes. Its common local wire order is the retained DYADIC CORE/MICROBOX of side L=p^128, not the full original axis of length r. Thus the Benes circuit width has log2(L)=O(log p) local bits and contributes only polylog(p) stages; using log2(r) as the local routing depth here would be incorrect. Coarse axis labels remain spectator coordinates. All completed simultaneous H calls are nevertheless executed globally across the whole complete tensor and all coarse labels, with the prescribed selected local bits and restored spectator order; they are not separate isolated suppliers per coarse box. TENSOR-COMPILER gives a common sequence of these H calls and diagonals on the same data coordinates, with identity operations on inactive axes. The group-key table may include full coarse coordinates to choose local coefficient/control pages, but this does not enlarge the local circuit wire width or stage count. There is no constant-factor data padding on each of g axes.

The per-group precision guard is

    O(p^(beta+2xi-2) polylog p + p^beta polylog p)=o(p).

Global normalization costs O(d log p)=o(p), since epsilon<1. Offline raw weights may require the larger setup precision already charged in section 2; the online shifted/anchored coefficients still use O(p) bits. The completed narrow inverse, broad identity-hole completion, local Schur complements and physical-prefix inverses have the cited polynomial bounds. Their errors are allocated at completed-map boundaries rather than multiplying large internal gauges across successive completed maps.

Apply the compiled g-axis circuits using section 1. There are d/g groups and polylog(p) calls per group, so

    fused Gaussian = O(T d g^(-q) polylog p)
                   = O(T p^(epsilon-q*beta) polylog p).

This is the actual tensor-fused algorithm. Merely applying g separate O(t log p) line FFTs would reintroduce T d work and would not prove the claimed saving.

## 5. Boundary and sparse recovery

Each original axis has O(s W/B polylog p) boundary coordinates, with W=O(sqrt(p) polylog p). Exact setup forms the correct rounded principal matrix and its Schur complement, preserving physical cuts and the actual fine-prime polynomial conditioning. Precompute its whole-boundary-block factors and periodic closure once. On a batch of W independent spectator right-hand sides, every dense W by W block update, block-pivot inverse, periodic correction, and both original coupling directions uses Strassen's explicit seven-product recursion. Its O(log W) depth and polynomial intermediate growth require O(log^2 p) extra guard bits. Global residual/condition bounds control final error, not a product of per-cell amplification bounds.

This is the constructive batched inverse in the companion analytic proof. There are O(s/B) boundary groups per axis. Per right-hand side the cost is O((s/B) W^(omega-1) polylog p), including all couplings. Summing all d axes and all fibers gives

    boundary = O(T (d/B) W^(omega-1) polylog p)
             = O(T p^(epsilon-xi+29/32) polylog p),

using 7^16<2^45, hence omega<45/16. Any final incomplete batch is padded with zero right-hand sides once, by less than a factor two; it does not add a coordinate on each tensor axis. All required same-axis factors are reused, never refactored per fiber.

Every sparse axis operation is supported only on its own listed endpoint slabs. Enumerate those slabs by indexed coordinates and visit only that axis's records. Operators on distinct axes commute at a fixed tensor stage, and processing an axis preserves the other axes' slab flags. Total visits are the sum of slab sizes, not g times their union size. Therefore sparse metadata/movement costs

    O(T d W/B polylog p)=O(T p^(epsilon+1/2-xi) polylog p).

The dense arithmetic on these slabs is already charged in the boundary row. Group construction adds O(T(d/g) polylog p) scans. Direct random access avoids sorting complete records by growing group keys.

The core/halo decomposition uses halo A=p^48 and dyadic core L=p^128. Its exceptional copied volume is O(T g A/L) per group. The original group inputs supply all halos; inaccurate core edges are discarded. Even retaining the predecessor's deliberately loose p^2 arithmetic allowance gives total core-face work bounded by O(T p^(epsilon+beta+48-128+2) polylog p), negligible here. No halo volume is padded by 2^g.

## 6. Native elementary and record products; exact recovery

All O(p)-bit scalar/short products are direct bounded-word operations. Long polynomial records have r coefficients of O(p) bits. Use the direct native FFT on those records with digit width Theta(p) and GLOBAL word precision Theta(p), not a fresh local Theta(log(rp))-bit machine. With explicitly generated roots and the fixed-point error theorem, a product costs O(r log r) word operations. It uses word products, not a TM multiplier. Here log r=Theta(p/d), so the complete retained record-product bill is O(T p/d polylog p), saving epsilon. This includes the constant number of signed/complex encodings and normalizations of the actual retained ring product.

The convolution/recovery caller's explicit error target is met by the chosen C p precision, including Gaussian gamma, supplier semantic guards, circuit prefix/suffix bounds and polynomially many local errors. The retained integer-recovery inequalities then give coefficient error strictly below 1/4; nearest-integer rounding recovers the exact coefficients. The standard bounded-word radix carry pass and packed output cost O(T polylog p). No external theorem of fast integer multiplication is used at any point of this native algorithm.

## 7. Nine paid native rows and exact strict margins

Every work term is O(T p^e polylog p) plus n^{o(1)} setup, and T=Theta(n/p). Thus its saving is 1-e. The nine retained rows have these native savings:

| Actual operation | Native saving |
|---|---:|
| main simultaneous transform | epsilon*q |
| initial/final standalone complete-address routing | 1 |
| fused Gaussian circuits | 1-epsilon+q*beta |
| additional standalone addressing passes | 1 (native masked shifts/table queries) |
| group scans and table lookup passes | 1-epsilon+beta |
| boundary algebra, both couplings, closure | 3/32+xi-epsilon |
| indexed sparse-axis visits | 1/2+xi-epsilon |
| global-precision polynomial record products | epsilon |
| core-face recovery | 1-(epsilon+beta+48-128+2) |

Per-call selected-bit gather, restore and address evaluation are already included inside the main-transform and fused-Gaussian call bounds. Extra per-group whole-array scans are included in the 1-epsilon+beta row. The two standalone addressing rows refer only to a fixed number of additional global passes; they do not classify all ell transform calls or all d/g group calls as one pass. Thus no T*ell or T*d/g toll is left uncounted. Native routing rows include their fixed logarithmic costs and are not assigned zero work. The smallest strict saving is epsilon*q=0.0030201655197983445, exceeding kappa by exactly 0.0000000000197983445. The fused Gaussian saving is 0.0030201754593950335. The boundary saving is epsilon*q+10^-10. Every other row has a fixed positive excess over kappa. Therefore all fixed polylog(p) factors can be absorbed into those strict margins; n^{o(1)} setup is smaller than n/p^kappa. This proves the claimed source-bound native asymptotic bound.

All essential interface inequalities are strict: beta<epsilon<1, xi>1/2, xi<epsilon, epsilon+r<1, beta+2xi-2+r<1, beta+1-epsilon<1, and beta+2(1-epsilon)<1. They respectively pay grouping, cap geometry, normalization, chirp precision, thin tables and the retained membership bound. The companion exact rational ledger should verify these rather than rely on decimal displays.

## Evidence, limitations and credit

This is an informal asymptotic assembly proof using actual predecessor recipes. It does not claim a materialized astronomical native supplier, an independently kernel-checked mathematical theorem, practical constants, a new TM bound or worldwide priority for FFT, Strassen, Toeplitz, word lookup, diagonal dominance or Woodbury. Executable component replays must be reported separately from universal source proofs. In particular a finite agreement with classical multiplication cannot verify the enormous fixed provider identity or the entire asymptotic caller.

Credit includes Jacob Alan Sussman's matching/Pascal construction; zxv's flow/majorant; Ryanson Jonathan's mirror-window method; Cinna Davis and the joint-helper lineage; Dillon's #4532 critical-root theorem; Vlado Vojdanovski's #1673 circuit tensorization and phase-cell fusion; PR #1758's shifted/accretive gauge-free interiors; Chafik Boukhalfa's #1786 fine padding and Tim Trudgian's prime estimate; Jeremy Kothe's ledger lineage; eumemic and icekylinx's Gaussian chirp/error work; Harvey and van der Hoeven's analytic multiplication/Poisson groundwork; and PR #4554's native arithmetic/adapters with their notices. Preserve exact source notices and commit/hash pins in the integrated package. Prepared for Dugongue with substantial OpenAI Codex assistance.
