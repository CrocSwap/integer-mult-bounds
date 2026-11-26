# On-demand spectral repair on fixed tapes

Status: **proved scalar-repair interface, finite replay passed, pending
independent review**. This removes all-frequency table enumeration at one
interface. Shared query pencils, initial batching, address maps and global
multiplication remain separately charged obligations.

Pins: programme `0607d044d1d09489580da0e5828588820e1a6775`; OpenAI math
`3344da59991ed94f9ba711217b29c1d760badfa6`. Dependencies read in full:
[structured-shift-check-refinement.md](structured-shift-check-refinement.md),
[power-two-degree-predictor.md](power-two-degree-predictor.md),
[characteristic-two-order-three-interchange.md](characteristic-two-order-three-interchange.md); actual tape
source `build/interchange.tex` for ordered scans and address conventions.
The shifts and tensor checks are predecessor results. Polynomial exponents
below are absolute, independent of the module width and address lengths.

## 1. Exact interface

Let m>=4096. Use B=3^r ternary shifts, with r least such that
(3^r-1)/2>=m, formed from m nonproportional vectors a_j in F3^r including
a basis: beta_j(t)=a_j dot t. Then 2m+1<=B<6m+3. Put b0=5ceil(sqrt m),
let T be the least power of two at least 2b0+1, and set D=T-1 and
u=m-floor(D/2). The predecessor's power-two predictor has D=O(sqrt m)
and common independent module width w. Set

    v=32w, R=Bv, s0=floor(B/32), S=R/32=Bw.              (SR1)

The containing exception set has at most s0 shifts at every frequency.
Use an s0-by-B Vandermonde H0, tensor I_v, followed by S-s0*v zero rows.
Use K=F_(4^e), e=ceil(log_4 B), with explicit degree-e defining polynomial
and e F4 coordinates per scalar. Bounded polynomial enumeration constructs
the field and B nodes in polynomial m time; coordinate arithmetic is
polynomial in log m. A scalar record has exactly 2e bits.

Physical addresses form a complete Cartesian range Omega in source order,
containing equal-width paired fields H_j,N_j with H_j before N_j. Positive
prefix, intervening, reserve and suffix ranges are arbitrary. Set k_j=0
at equality, 1 when H_j<N_j, and 2 when H_j>N_j. Negate k_j modulo three
for inverse queries. The source completed forward converter mathcal T and
inverse mathcal S are separately charged. This interface acts after the
entire forward word and before the entire inverse word, in original
physical address order.

Parent rows have order (shift,module,Omega); nonpadding checks have order
(check,module,Omega), followed by padding. Labels and repeated parent
blocks are outer prefixes, preserved by this procedure. Every module row
is an independent input. Let V be the parent encoded bit volume including
those prefixes.

For packed physical composition, split v=32w explicitly: parent coarse
roles are (shift,duplication), of count 32B, followed by the same w-index.
Nonpadding checks have coarse roles (check,duplication), of count 32s0.
The S=Bw check rows therefore have B coarse roles: 32s0 real roles and
B-32s0 zero roles, all followed by w. The padding is not claimed to be an
integer number of v-modules. A two-family child has 2B coarse roles and
the same w-index; grouping sixteen parent blocks gives 32B coarse roles.
This is a polynomial-size coarse-row gather/scatter, never a permutation
inside or a transposition of the exponentially wide w-module.

**Theorem SR.** A fixed finite-alphabet multitape interpreter applies the
tensor check, padded check, transpose lift, and completed-interface repair
table on exactly 2S=R/16 rows per parent block with

    time <= V poly(m)+poly(m,log(V+2)),
    visited cells <= V poly(m)+poly(m,log(V+2)).            (SR2)

Finite descriptions and coefficient generation cost polynomial m time and
space. It enumerates neither 3^m frequencies nor the w-row module matrix.
The parameter-dependent linear-space coefficient is suitable for the
existing common-cap wrapper, not itself a global common-cap theorem.

## 2. A polynomial scalar table from the short spectral key

For key k and each shift t compute

    c_t=sum_j ((k_j+beta_j(t)) mod3), z=omega^(sum_j k_j),
    J={t: c_t outside [u,u+D]},
    p_t=omega^(u-sum_j beta_j(t)+(c_t-u mod T)), g_t=p_t-z. (SR3)

The prior pairwise-variance/Chebyshev argument gives |J|<=s0 for every k.
The p_t formula follows because a Boolean low bit B_i obeys
1+(omega-1)^(2^i) B_i=omega^(2^i B_i). Thus the factored Lucas predictor
uses the residue of c_t-u modulo T, including negative offsets. In the
central window this residue is c_t-u and p_t=z. All values lie in F4,
so every nonzero g_t has cube one. Counts, J and values use polynomial m
bit operations and workspace. Scanning the entire polynomial-size seed
description for every record is allowed and charged.

Write j=|J|. Let V_J be the j-by-j Vandermonde on columns J and powers
0,...,j-1. Distinct nodes make it invertible. Define the s0-by-s0 matrix
with only this possibly nonzero block:

    M_J[0:j,0:j]=V_J^(-T) diag(g_t^2:t in J) V_J^(-1).    (SR4)

For J empty use zero. Deterministic elimination costs polynomial m
coordinate work. Only nonzero Vandermonde pivots are inverted, never g_t.
For the two transformed check families U=H0(PX)^hat and V0=H0 X^hat,
return, independently at every module coordinate,

    a=M_J(U-zV0), z a,                                    (SR5)

and zero in every padded coordinate. Each family retains exactly S rows.

**Correctness.** The error e_t=g_t Xhat_t is supported on J. Its first j
checks are V_J e_J. Inverting and transpose-lifting (SR4) gives
Zhat_t=g_t^2 e_t on J. If g_t is nonzero this is Xhat_t; if g_t=0 the
original error already vanishes. Outside J the original gap and predictor
error vanish; the lifted correction Zhat need not vanish there. Completed
inverse conversion and transpose lifting return Z,FZ, and PX+PZ+FZ=FX,
since its spectral error is g_t(Xhat_t+Zhat_t)=0. This permits containing
sets with accidentally correct rows and zero discrepancies. Padding is
internal workspace, never additional independent parent inputs.

## 3. Actual tape control generation and record widths

For one H_j,N_j pair, fix the earlier prefix containing H_j and all
intervening fields. Its complete N_j fibre has three consecutive runs:
values below H_j, equality, and values above H_j, each with the complete
trailing range. The fibre pays for reading H_j, computing the two
boundaries and resetting counters. Source amortized ripple counters and
block scans generate the trit stream in linear volume plus a fixed
polynomial descriptor term. No full binary address is stored or read per
symbol. In particular a control of f radix-b digits is read only once
per complete target range, whose b^f positions pay that cost.

Repeat for m pairs. A fixed number of tapes suffices: zip each new two-bit
trit stream with existing tagged records into an alternate work region,
then reuse the old region. After i passes the tagged scalar width is
exactly 2e+2i bits, plus an optional fixed number of role bits. Even charging
that full width on every pass gives O(m^2 V) work and O(m V) visited cells,
plus polynomial descriptor setup. This is independent of address-field
width and w. Keys refer to original physical addresses and are generated
only at the completed-converter interface. No mask is moved through an
endpoint change or an incomplete converter word.

## 4. Applying shift maps by aligned scans

There are polynomially many shift/check row pairs. For each output row,
initialize its contiguous (module,Omega) accumulator. For each input row,
copy its complete block, scale it, and add into the accumulator in aligned
order. Heads may scan or rewind the complete current parent block between
passes; polynomially many passes cost V poly(m). There is no random access
or implicit transpose of an exponential row matrix.

For (SR5), loop over output and input check indices. At each record read
its m trits, recompute the desired M_J entry through (SR3)--(SR4), multiply
the scalar, and add into the aligned accumulator. Recomputing the whole
polynomial-size matrix for every record is charged polynomial m time and
reusable polynomial m workspace. Thus no all-key enumeration or random
coefficient access is required. Obtain z and the second family from the
same key. Fill padding with explicit zero scans.

Labels and repeated parent blocks are processed sequentially, reusing
marked regions; their count is already in V. All module rows retain their
order. A final charged scan removes tags **before any inverse converter or
recursive child call**. Constant H0 checks require no spectral tags before
the forward converter. Thus all four paid conversion phases carry only
the original 2e-bit scalars; O(m)-bit sidecars remain parent scratch and
never inflate child volume. Only a fixed number of work tapes is used.
This proves (SR2), including cells ever visited. A complete array
copy, all head returns, zero initialization and erasure are in this bill.

For a deliberately loose explicit envelope, shift count B<6m+3, at most
B^2 input/output row pairs, O(B^3) field operations per matrix inverse,
and polynomial-in-log(m) coordinate operations imply V*m^C for one
absolute C. The proof allows recomputation rather than assuming an
unpriced cache. Descriptor setup includes the binary lengths of ranges
and complete role/module counters, of total length poly(m)+O(log V).

## 5. Fractions, parked arrays and composition

The two check families together contain exactly 2S=R/16 rows. Each
converter word has two order-three transforms, so the predecessor's four
sequential child phases retain size R/16 and total mass 1/4. The table
lies between the completed forward and inverse words. Labels and module
multiplicities remain unchanged. Label-preserving regrouping for the child
caller is separately charged by that caller.

During finite contraction, child volume is one sixteenth of parent volume.
The parameter-dependent parked scalar workspace therefore sums as a
geometric series under depth-first execution. Sequential children reuse
their regions. Scalar work sums by total child mass 1/4, so it acquires no
depth factor. These bounds price the scalar component only; recursive
spatial-query calls remain separate.

Together with B's succinct scalar-factor executor, this closes two
specific expanded-matrix/table costs. A polynomial complete profile still
requires actual shared endpoints preserving recursive call mass, label
maps, bounded numeric address operations, complete batching/regrouping,
and the global precision/common-cap compiler. No improved H(n) follows
from this component alone.
