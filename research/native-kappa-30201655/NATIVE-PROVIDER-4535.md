# Native Word RAM closure of the actual critical-root finite word

## Result

Put q_C=0.0030201656 and N=2^1000000000000. Under the pinned predecessor's **algebraic finite-word theorem** described below, its actual fixed uniform word yields a native bounded-word Gaussian kernel with work

    O(2^e (e+1)^(1-q_C))

on 2^e entries. For input component magnitude at most 2^b and requested absolute error 2^-B, where e,b,B=O(log n), a sufficiently large fixed constant times log n bits per word suffices. Preparation, address/phase metadata, integer batch widths, all complete paid children, owned allocation/initialization/erasure and fixed rational arithmetic are included. This closure does not assume a Turing-machine execution theorem, a unit-cost transform oracle, an unproved stability gadget, or a new scalar circuit supplied by a moment inequality alone.

The fixed finite word and its exact all-input correctness are predecessor mathematics. This result independently supplies its native random-access implementation, precision and asymptotic cost. It remains an informal proof, as do those predecessors. No practical cutoff, materialized giant word, Lean audit, new raw profile or new TM kappa is claimed.

## Exactly which algebraic predecessor facts are retained

PR #4535, head a6d7237f697185e857090e174c23c1cb22c6563c, `research/critical-root-multiplication/PROOF.md`, sections 2 and 3, applies the critical-root majorant of PR #4532 at 644607ba59ebe401ac7ecd627ae7f331f924d1b0 to the actual joint-helper word of PR #4470 at b9a13c1673e0e9697de410de16e8bbf3207a7363. It fixes N above and obtains

    P_leaf/W = L(N) < N^(1-q_C).

Here W is the actual independent productive width after integer denominator clearing and P_leaf counts every rank-one paid child. The ordinary base, source complements, unmatched premature exits and compiler-boundary jobs are charged. Each source input is distinct, even when a class has no incoming parent. This is a strict uniform moment for an algorithmically specified finite word, rather than an unnormalized raw-profile comparison.

The actual finite construction is given in the source at PR #4483 head fb0c208864e6b24e3473318a058aa5b2dbd5764b, **`research/direct-mixed-flow/README.md`, sections 2 and 3**. This is the relevant detailed construction; the short `research/compact-joint-compiler/PROOF.md` is a parameter consequence and is not itself that construction. The retained source defines the capped multinomial classes, matches the first D(b) whole issued jobs to child target slots and completes every remaining job as an exit. A paid round and its child finish before the next parent round resumes. Rank descent is strict. Nested widths B_n=B_(n-1)*S_n make every earlier complement/exit batch integral. Every original field receives its disjoint complement transform and its source transform; no productive input is copied or identified. This proves the all-input algebraic assembly by strong induction, using the source's whole-job Gaussian conjugacy identities and monomial normalizer recipes.

Those algebraic identities, the exact all-column joint-helper endpoint and the uniform majorant are retained credited results. The retained algebraic identity is its actual column/fiber lift for every positive f, including the literal lifted Clifford normalizers and phases f*gamma modulo 4; a finite replay at f=1 alone would not prove that fact. They are not re-inferred from histograms. The fixed normalizers are explicit binary affine matrices and quadratic fourth-root phase descriptors, as supplied by the source's Gaussian/Clifford reduction. There is no assumption here that an unspecified dense change of basis is cheaply evaluable. If the source's exact all-input word or stated monomial identities are wrong, this conditional native consequence fails; the native proof does not conceal that ordinary mathematical dependency as a cost oracle.

The strict leaf inequality is the numerical/mathematical premise used below. This document does not reuse PR #4535 section 4's TM movement, tape, precision, or finite-template execution contract. Word RAM closure is proved directly.

## Uniform finite setup and complete instruction inventory

Expand the effective construction at the single fixed N. Its recursion and width products terminate by strict rank descent. Enumerate every raw unit, all integer routing matches, each scalar ADD/SCALE, each child, each whole-job monomial adapter, and each owned buffer. Assign different storage to simultaneously live fields; a safe simpler construction gives a separate bank to every owned allocation. Count the actually emitted records and their coefficients. This computes finite integers W, P_leaf, O, R and a coefficient bound G. No assertion is made that these enormous integers or records have been physically produced here.

The expansion is one fixed finite algorithm independent of the eventual n and e. Run it as charged initialization, taking a fixed finite C_setup operations and space. It can be retained between calls within a multiplication run. Its binary integer arithmetic is performed in fixed finitely many limbs. Increase the global fixed word-width coefficient and eventual cutoff until its fixed literals fit. Alternatively expand each fixed coefficient into finitely many word limbs. This is uniform finite preprocessing, not advice depending on n and not free input-dependent arithmetic. C_setup is included in the asymptotic constant; finite small inputs use direct butterflies.

No normalized source-count division is introduced as a scalar gate: integer replication clears the batch widths. All literal scalar coefficients are dyadic (and the same proof permits any fixed nonzero rational denominators). Their numerator and denominator heights are fixed and explicitly enumerable. Normalizers and private allocation are included even when their scalar coefficient-height contribution is zero.

## Direct word implementation and paid address metadata

Use indexed arrays for the independent live roles and owned scratch. A scalar gate acts coordinatewise, with O(1) bounded-word numerator products, additions and divisions per coordinate; the fixed number of limbs can depend on the frozen finite word. COPY and CLEAR perform explicit passes. Do not clear dirty borrowed fields. Parked suspended callers retain their own storage until their return.

Every e-bit affine/quadratic monomial lift is implemented by the explicit table construction in NATIVE-PROVIDER.md: prepare parity and least-set-bit tables on mu=max(1,floor(e/16)) bits, then use a fixed number of chunk lookups per e-bit address. Increasing-index recurrences compute its affine image and quadratic phase in O(1) word instructions per entry. Their O(e^2+2^(e/16)) setup is absorbed by O(2^e); each application and owned scratch pass also costs O(2^e). Common live coordinate maps are bijections by the retained exact normalizer identities, so indexed gather/scatter preserves every input value and caller-live field. No popcount, ctz, PEXT or PDEP instruction is required.

For a rank-r child lifted to r*f active bits inside N*f bits, enumerate complementary fiber bases and selected-bit deposits. Explicit table construction and the chunk/parity method charge O(2^e) total gather/scatter work. Each fiber is passed to the child once; it is not reexecuted per output element. Disjoint fibers preserve arbitrary independent data. Child responses finish before a suspended caller continues. Metadata, full fiber descriptors, zero initialization and final flattening/clearing are included in the fixed count of array passes.

After N is frozen, all local record counts are fixed constants. Therefore the complete nonchild execution of one volume-V batch costs at most C*V, with a newly computed fixed C including setup and all role/owner passes. No tape-movement implementation is called.

## Rank recurrence and one-time stock reserve

Let z=1-q_C, f(e) be the active chunk size in the ordinary uniform recursion and t(e)=T(e)/2^e. The credited finite word has only rank-one paid leaves at rank N. Group only complete sets of W fibers, retain every leftover on its distinct original input, and run their direct completed butterflies. Reserve the actual preceding row stock at all nested levels; its width is O(log(e+2)) because W is fixed and the child rank contracts by N. Computing the high directions once, plus paying those leftovers, gives the direct native recurrence

    t(e) <= (P_leaf/W)*t(f(e)) + C*(1+log(e+2)),
    f(e) <= e/N,

above a fixed finite base cutoff. This is the same algebraic complete-batch decomposition; its nonchild word-time bound is proved above rather than obtained from a tape tariff. The fixed stock, complete batches, leftover direct transforms and high-direction transforms are actual operations. Any implementation must preserve their full field identities; replacing the stock by one reusable dirty field is not this construction.

An explicit conservative split is available. Put a=ceil(log2 W), lambda=ceil(log2(e+2)), and D_upper=1+ceil(log_N(e+1)); choose the fixed-cutoff branch until e exceeds a*D_upper+2*lambda+2*N. Above it take f=floor((e-a*D_upper-2*lambda-N)/N) and ell=e-N*f. Then ell=O(log(e+2)), ell>=a+2*lambda and f>=1. There are 2^ell complete fibers. Fewer than W leftovers occupy fraction at most W/2^ell<=(e+2)^(-2), so their O(e) direct cost contributes O(1) normalized work. The ell high directions cost O(ell) normalized operations. The a*D_upper stock reserve covers one actual W-role chunk at every possible nested depth; every role remains on its own indexed coordinates. Thus the displayed recurrence has an explicit direct native batch implementation, with no input-size-dependent padding factor hidden in its constant.

Put mu=(P_leaf/W)*N^(-z)<1. Since (e+1)^z dominates log(e+2), choose a fixed base cutoff and constant A so C*(1+log(e+2)) <= (1-mu')*A*(e+1)^z for some mu<mu'<1. Increasing the cutoff absorbs the harmless +1 in the child argument. Strong induction, with all finite base costs included, proves T(e)<=A*2^e*(e+1)^z. Since f(e)<=e/N, recursion depth D(e)=O(log(e+2)).

## Precision: literal coefficients and depth, not total word length

Consider the expanded finite template acting on all live and owned coordinate banks. For ADD x<-x+a*y use the exact operator-norm bound 1+|Re a|+|Im a|; for SCALE use max(1,|Re a|+|Im a|); COPY has bound 2 and CLEAR bound 1. Monomial permutations and quarter phases have norm 1. Their finite product gives a computable fixed integer K>=2 covering every local prefix and suffix, with completed recursive children treated as exact unitary Gaussian maps on their live fields and zero on freshly cleared owned storage.

An expanded prefix or suffix is inside at most one unfinished child per depth. Every other completed child acts unitarily on its disjoint live coordinates. Hence the complete exact prefix/suffix norm is at most K^(D(e)+1). This is proved from the actual finite inventory and all-input endpoint; no semantic-precision oracle is assumed. The constant log K may be enormous but is fixed. In particular, multiplying a varying depth by log K gives O(log(e+2)) guard bits, not an input-dependent unbounded coefficient.

With M(e)<=A*2^e*(e+1)^z scalar operations, exact rational local evaluation followed by rounding to P fractional bits injects complex error at most sqrt(2)*2^-P. Transporting every local error through the exact suffix and summing yields

    ||computed-exact||_infinity
      <= sqrt(2)*A*2^e*(e+1)^z*K^(D(e)+1)*2^-P.

Thus it suffices to set

    P=B+e+ceil(log2 A)+ceil(z*log2(e+1))
        +(D(e)+1)*ceil(log2 K)+3.

The exact input Euclidean norm is at most sqrt(Z_e*2^e)*2^b. A safe sequential allocation has Z_e bounded by a fixed polynomial in e (even allocating a fresh bank at every recursion depth contributes only a depth factor at equal total volume). The prefix estimate and the same transported-error sum therefore give integral width

    I=b+e/2+(D(e)+1)*ceil(log2 K)+O(log(e+2))+O(1).

If a chosen stock layout uses a larger fixed polynomial space envelope, include its logarithm instead. Consequently I+P=O(log n) whenever e,b,B=O(log n). Products and exact fixed-limb rational divisions add only a constant factor to the common word width. Fixed dyadic denominators contribute their literal finite height; they are not mistakenly charged as O(log e) when their constants are huge. Negative operands use signed magnitudes or two's-complement arithmetic with explicit guard bits. No intermediate is a unit-cost n-bit product.

The same local-error argument controls arbitrary approximate inputs to inverse calls and sums over independent fibers. The unnormalized Walsh conversion multiplies accuracy by 2^(e/2), so requesting B+ceil(e/2)+1 bits from the Gaussian kernel suffices. Its exact Gaussian-integer normalization is constructed in O(e) bounded-word steps and remains within O(log n) bits.

## Scope and credit

This proves the native execution/precision closure of the pinned actual algebraic finite word at q_C. It does not independently reprove the critical mirror/majorant or the source's all-column identities, and does not turn a numerical receipt into those proofs. The entire cyclic/tensor caller, precision propagation, paid Gaussian/phase preparation and packed integer recovery must be connected by the complete outer assembly before a multiplication exponent follows. A native target of 0.0030201655 requires that complete assembly with strict slack; it is not a new multitape-TM result and is not a better value obtained by printing more root digits.

Credit: Cinna Davis and the joint-helper/native contributors; Jacob Alan Sussman for integer matching; zxv for direct flow, nested widths and logarithmic majorants; Ryanson Jonathan for mirror windows; Dillon for the critical-root criterion; all retained Clifford and Gaussian sources; and the earlier #956 native provider lineage. This document adds direct indexed-RAM metadata, exact rational bounded-word lowering and quantitative depth stability for that actual larger finite word. Prepared for Dugongue with substantial OpenAI Codex assistance, Apache-2.0. No independent human or formal-kernel acceptance claim.
