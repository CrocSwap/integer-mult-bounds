> Current evidence: independent conditional paper acceptance at the scope in [REVIEW.md](REVIEW.md). Historical author/pending labels below describe the frozen submission; imported predecessor hypotheses remain explicit.

# Conditional balanced composition of reversed two-stage corners

Prepared with OpenAI assistance, 8 October 2026. This is a focused conditional paper increment with exact arithmetic. It is neither a formal verification nor an unconditional multiplication theorem or global-priority claim.

## 1. Result, source correction and hypotheses

The exact PR33 head used here is DominikScholz/integer-mult-bounds at e0399d0e1a222bebf72e44ad374004bbcb7f2c64. It already includes the contiguous standard-order profile 11 singletons + [43,37,1933], with bit saving 1638156876/10^14 and final saving 1638103206/10^14. Its older certificate-47-45.json remains a separate 91-singleton checkpoint with bit saving 16039/10^9. Comparing only against that older checkpoint would overstate the new contribution. The frozen source manifest gives repository, commit, path, Git blob hash and SHA-256; every downloaded file was checked against the exact Git blob. Supplier programs were read but never executed.

There are two conclusions, with separate obligations:

1. Keeping PR33's standard bit graph and profile unchanged, the already accepted balanced transfer yields kappa = 1638130040/10^14.
2. If the separately reviewed reversed-order common-basis theorem supplies the profile 9 singletons + [43,39,1933] at ordered dimensions (45,47), the same transfer yields kappa = 1639226629/10^14 = 0.00001639226629.

The second result improves the pinned PR33 saving by 1123423/10^14. Its bit saving is a = 1639253501/10^14. No producer optimization from the concurrent producer lane is included.

The assumptions are explicit. Retain the fixed finite alphabet and fixed finite number of one-dimensional tapes multiplication framework, the actual PR33/PR29 finite producer scalar identities, carrier ownership and label inclusions, arbitrary dirty-auxiliary restoration, same-common-basis local and auxiliary profiles, and arbitrary-width complete-record interchange with compact spectators. For the second conclusion also retain the new uniform reversed-order geometry theorem, including ordered contiguous pivots, simultaneous nonvanishing in the common rational family, both invocation orientations, and no uncharged reorder. The present arithmetic does not establish these geometric or circuit theorems.

Retain the PR21 all-role complex phase circuit, its normalized error and exact-recovery interfaces, and the attributed RaD/PR23 semantic guard, arbitrary-coordinate router, balanced positional layout, phase-cell inverse and bulk-resampling constructions. The [previous balanced composition](https://github.com/jamesyc/integer-mult-bounds/blob/a2d8ac18b2c5a6ca53efa802f48e64b8140ae2d9/research/a5-blocks-28-22/COMPOSITION_PROOF.md) and [rectangular composition](https://github.com/jamesyc/integer-mult-bounds/blob/7a7fd0d463ec75e19ea60dc6eb513d3d95672865/research/rectangular-a5-extra22/ASSEMBLY_PROOF.md) supply this generic transfer under their explicit assumptions. Here we audit the changed finite graph interfaces and instantiate the transfer; we do not re-prove or rename the inherited results.

## 2. Complete physical histogram and what reversal changes

Put m=45*47=2115, v_h=binom(h,3), and N=v_45*v_47=230090850. The retained producer records are:

- h=45: c=309138, q=42615, matched=5649, R=346104, loss=1980.
- h=47: c=354791, q=48692, matched=6135, R=397348, loss=2162.

For each h, R=c+q-matched and loss=h(h-1), with no additional center roles. The source histogram H_h satisfies sum_r r H_h(r)=h R_h+2 loss_h. Let B_h=(N/v_h)R_h. Then B_45=5612076360, B_47=5638368120,

W=2N+B_45+B_47=11710626180,
L=sum_h (N/v_h)loss_h=62784480,
s=Wm-N+2L=24767869848810,
Wm-s=104521890.

The complete list is reconstructed from these records as follows:

- Exterior h-bank: B_h copies of [h,m-2h].
- Internal rank-r residual: (N/v_h)H_h(r) copies of its ordinary local profile. At r=h this is [h]; at 2r>h and r<h it is h-r singletons plus [2r-h]; otherwise it is r singletons.
- Physical growth for each h: 2N copies of [1,h-2].
- Data macro: 2N copies of the relevant data profile, including width1933.
- Endpoint copy correction: N additional width-one children.

This exactly reconstructs both the older full 91-singleton list and PR33's current full standard list. The sum of child widths times multiplicities is s in every case. The paid copy correction is included, and every child has the same role-volume factor 1/W.

Changing (47,45) to the geometry theorem's ordered (45,47) reverses which factor is first, but preserves the unordered producer pair, N, B_45+B_47, W, L, s, growth profiles and exterior profiles. The ordered exterior banks become [45,2025] and [47,2021], with their original respective multiplicities. Their sum is unchanged. The largest child remains 2025<2115. The only complete-histogram change from current PR33 is

n_1 -> n_1 - 4N,
n_37 -> n_37 - 2N,
n_39 -> n_39 + 2N.

Its rank change is -4N-37*2N+39*2N=0. This replacement is valid only because the separate geometric theorem realizes those matching intervals contiguously in the actual physical order. It is not justified by matching ranks, sampled pivots, or freely gathering arbitrary coordinates.

## 3. Exact moments and justified negative conclusions

For every positive child width t, the checker encloses log(m/t) by reducing m/t=2^k y, with 1<=y<=2, and using

log(y)=2 sum_{j=0}^{23} z^(2j+1)/(2j+1) + tail,
z=(y-1)/(y+1),
0<=tail<=2 z^49/[49(1-z^2)].

Lower and upper endpoints are rounded outward on the rational 10^-12 grid. For u>=0, the upper bound is exp(u)<=1+u+u^2/[2(1-u/3)] when u<1. Indeed j!>=2*3^(j-2) for j>=2, so the positive Taylor tail is dominated termwise by that geometric series. For a lower bound use 1+u+u^2/2+u^3/6. Thus the checker proves bounds on the actual characteristic

M(a)=sum_t [t n_t/(mW)] exp(a log(m/t)).

It exactly reproduces the published 91-singleton and PR33 standard upper moments. At a=1639253501/10^14 the reversed moment is strictly below one, with certified gap greater than 16/10^16. At the next grid point 1639253502/10^14 its certified LOWER bound exceeds one. The standard profile likewise has a lower bound above one at its next grid point 1638156877/10^14. These are genuine grid-level exclusions for the stated histograms, not a claim inferred from a failed upper enclosure. Monotonicity of M, because 0<t<m, justifies the binary search. There is no broader algorithmic optimality conclusion.

The checker also proves that the standard histogram fails at the reversed saving by a lower bound, and that the 91-singleton histogram fails at the standard saving. All consumed numerical inputs are integers or Fractions. The older source's unused decimal numeric_root diagnostic is explicitly discarded before validation; no floating-point value participates in any certificate calculation.

## 4. Why the unchanged Gaussian semantic guard applies

The bit routine only permutes complete encoded coefficient records. The common-basis geometry is rational address geometry, reduced at one eligible odd prime after all finite minors and denominators are fixed; it is not the binary payload field F_2. The complex payload remains Gaussian dyadic. The bit and complex arities need not agree: arbitrary-width complete-record interchange is the adapter contract. Choose the common address prime outside the finite union of the two setup families' exceptions.

The actual unchanged PR21 complex data are

m_c=21952, W_c=2085111546336, s_c=45772350635112192,
r_c=21924, b=18/10^6.

Its full characteristic is recomputed at b and is strictly below one. An invocation on u selected axes returns the complete all-role map C^(tensor u), or its correctly unit-conjugated inverse, and identity on every spectator. It accepts arbitrary dirty auxiliaries, returns coefficients on the incoming grid shifted by at most u dyadic places, and has row norm at most 2^u. Parent arithmetic never observes an incomplete child intermediate. No child is rounded or re-encoded at its boundary. Replacing the bit adapter therefore changes a movement exponent, not the complex scalar operator or Gaussian coefficient growth.

For this graph the literal grouped scalar upper charge is

G_scalar=3 binom(28,3)^2 (4*64298+4 binom(28,3)+4)=8702721518400.

Set E=64(W_c+m_c+1)^3, B=s_c+E and C0=32m_c B^2. The exact check proves

2G_scalar W_c^2+8s_c+4W_c+4+32m_c<E,
2B(m_c-r_c)>=s_c+E.

The accepted completed-child induction A(e)<=max_r A(r floor(e/m_c))+s_c floor(e/m_c)+E consequently retains A(e)<=2Be. With the disjoint outer selected pieces and individual work, A_layer<C0 d. Thus C1=1 is the PR21/PR23 semantic constant, not a transferred path guard from another graph. The same encoding, normalized contraction/signed-monomial bounds and single outer truncation retain the exact-recovery interface.

## 5. Actual mixed row stock and the paid correction

The exact least integers giving a strict factor-two contraction are 16 for (2115,2025) and 544 for (21952,21924): the checker verifies m^D>2r^D and failure one exponent lower. The role counts satisfy W<2^34 and W_c<2^41. Reversal or the data regrouping changes neither maximum nor role count.

For global call width U<=C p, reserve the PRODUCT

Q=W^[16 ceil(log2 U)] W_c^[544 ceil(log2 U)].

A complex ancestor retains its own split while a bit adapter runs, so using the maximum rather than the product is invalid. When p>=C and log2 p>=25,

log2 Q <= (16*34+544*41)*(51/25) log2 p
=22848*(51/25) log2 p <47000 log2 p.

The strict degree gap is 9752/25. Thus p^47000 complete rows suffice. Apply exact individual phase kernels to a physically preceding prefix of ceil(log2 Q) selected positions and retain those whole chunks. If the root is shorter, use the elementary fallback. Otherwise pad once to Q ceil(R/Q)<2R. Descendant splits cut complete rows whose active, compact-control and spectator fields remain complete. Completed all-role maps return padded zero rows to zero; remove padding only at completed boundaries. No suffix is moved into this prefix for free.

The two-stage paid correction copies one existing complete role stream, applies its width-one bit child, XORs into the other data stream, and erases the copy. Its O(V/W) ordinary work and one recursive child are already in the list. Process it sequentially with its existing row fields: it adds a fixed parked stream to the depth-first stack, not an independent row-index family. No new row divisor or padding is introduced. Dirty-scratch restoration and the final full interchange are the retained topology theorem, required in both orientations. Accordingly the original complete-row proof applies without multiplying Q by a fictitious correction reservoir.

A sufficient row-suffix inequality is b_input^(1-epsilon)>188000(log2 b_input+8). It is checked with the actual degree47000, rather than inherited by numerical substitution.

## 6. Reuse of the accepted balanced transfer, with changed-interface audit

The accepted balanced proof permits any bit graph having the complete-word, both-orientation, dirty-scratch contract just checked and a strict characteristic exponent a. Its implementation processes each long FFT axis's extra top bit individually, then partitions the common named low positions into complete groups of widths K_j in [K,2K), K=floor(d^c). Every axis in one call supplies the same K_j. The axis-major/group-major permutation and its inverse use the paid arbitrary-coordinate router, including its untouched spectator, three-reservoir matching split, active-masked shears and current-address repair. It is not a free relabeling or the older slower sequential-transpose implementation.

The bit substitution is valid because that router and the bulk mover call only the bit interchange contract on complete records with arbitrary complete spectators. Each current rectangle is [P] x [2^K_j]^(d-1) x [S]. Supplied widths K_j>=K satisfy lower compact tests; K_j<2K changes upper bounds by a fixed constant. The row prefix remains disjoint from front/back control fields; complete-row splitting does not cut those fields. Semantic precision depends on selected axes, not unused within-chunk coordinates. These are the same hypotheses used in the accepted transfer; the exact new stock was established in section5.

Named FFT level order, twiddle exponents and frequency significance remain unchanged. The inverse recovers lower named coordinates before their inverse twiddles. The physical forward alignment is L_new B F-, the pointwise product uses that same alignment, and inverse alignment is F+ B^-1 L_new^-1. Original prime-box ordering and final normalization are retained. The extra individual top work costs O(T p d), uses p+d+O(1)=O(p) bits and contributes at most d guard bits.

The same global rounded H, exact diagonal one, inverse row norm<=8p and gap>=1/(8p) are retained. With alpha^2=Theta(p^r), w^2=O(p^(1-r)); the normalization gamma=d(2alpha^2+ceil(log2(32p))+1) still requires epsilon+r<1. The phase-cell inverse uses conventional unconditional multiplication for its small convolutions. Its principal windows restrict this same H with artificial-boundary distance>=512p^2 w and complementary period>w. The bulk mover keeps L>=p^8, halo4096p^3, persistent L+2A target windows, current-small-field-only padding, alternating overlap tapes, ordered pages and axis-completed cropping. Its total tensor volume is <2T, and its cost remains

O(Tp[p^(1-a) polylog p + d polylog p + d p^delta + w^2 p^delta + d w^2 p^delta/L]) + n^o(1).

None of these maps or physical period cuts depend on the new data-corner partition. Distinct-prime packing 12d^2<x^(19/40), with x=2^Theta(p^(1-epsilon)), remains eventual because epsilon<1. The BHP threshold, native finite basis/prime/table setup, catalogue domination, logarithmic absorption and exact-recovery threshold remain separate eventual assumptions.

## 7. Explicit strict parameters and conditional conclusion

Use b=18/10^6, beta=1/20 and h=10^-12. For either certified bit saving a, define

q=a(1-2h), c=q+h/4, epsilon=(1-h)/(1+q),
lambda'=1-q, lambda=((1-a)+lambda')/2,
G=epsilon q, r=(G+1-epsilon)/2, delta=h/8.

Stopped complex leaves have exponent sigma+beta(1-sigma), sigma=1-b; the internal exponent is (1-a)+(1-beta)max(sigma-(1-a),0). Their saving (1-beta)b=17.1*10^-6 exceeds both bit savings. The PR29 choice beta=1/10 would give16.2*10^-6 and fails; silently retaining it is invalid. Positive beta1/20 changes the stopped-leaf threshold, which is explicitly checked as357 bits, but changes neither complex scalar operator nor stock depth.

The seven balanced savings are

1-epsilon, a, G, a, min(1-epsilon-delta,r-delta), 1-epsilon-delta, epsilon.

Their minimum is G. The exact identities

1-epsilon-G=h,
1-epsilon-r=h/2,
1-epsilon(1+c)=h-epsilon h/4>3h/4

provide strict small-field, normalization and compact-geometry gaps. Reservation gap c-q=h/4 is positive. The checker tests all47 retained strict conditions: internal/leaf/reservation exponents, lambda ordering, compact geometry, semantic guard, record suffix, short-record fallback epsilon>a, phase-cell separation epsilon>(1-r)/2, alpha/delta ranges, scalar charge, actual product stock and all seven margins above kappa.

For the reversed graph,

G=819626750497541119748501639253501 / 50000819626750498360746499000000000000,
kappa=1639226629/10^14,
G-kappa=45758854322893654446028229 / 5000081962675049836074649900000000000000 >9*10^-15.

This fixed positive gap absorbs the retained logarithmic factors asymptotically. A sufficient common numeric checkpoint is log2(input bit length)>=14000000000000. Exact compressed power checks cover the actual row suffix, compact width, alpha, periods and stopped leaves at this checkpoint and its next five doublings. For a denominator k, the check deliberately uses the affine right-hand side at Z+k against 2^floor(Z/k). This controls the whole interval [Z,Z+k). On each subsequent interval the lower bound doubles, while its positive affine right-hand side increases at most linearly in the interval index; 2^j>=j+1 proves dominance for every real z>=Z. Thus the checkpoints are supported by an all-size argument, not treated as an extrapolation from six samples. Prime/native-setup, catalogue and recovery thresholds remain additional requirements; this is not a practical input-size cutoff.

Negative controls reject the old nonlinear guard, the old separate movement exposures, the original-prefix charge, beta1/10, and the next kappa grid point. In particular the original prefix saving1-epsilon(1+c) is below kappa: the balanced construction is essential, rather than an unearned change to an inequality. Within this declared balanced interface the constraints imply kappa<a/(1+a); that scoped ceiling is not an impossibility theorem for other algorithms.

Under the hypotheses above, the retained multiplication assembly therefore gives T(n)=O(n(log n)^(1-kappa)) with the stated kappa. The only newly required geometric fact is the separately proved reversed-order contiguous profile; the transfer result does not assume it follows from this arithmetic certificate.

## 8. Attribution, reproducibility and verification boundary

Dominik Scholz PR33 supplies the actual standard47/45 corner composition and refined savings; Zhihao Chen PR29/21/23 supplies the two-stage composition, complex graph and semantic/bulk assembly; Rohan Arun PR31 supplies the standard data-corner development; Aurel Prosz supplies the two-stage topology and paid correction; Swapnil Jain, icekylinx PR24/18/10, RaD/hipotures, eumemic, Douglas Colkitt's framework, OpenAI's upstream manuscript and Harvey--van der Hoeven's analytic background remain credited. The source's recorded AI assistance and licenses remain in force. The balanced construction belongs to the pinned RaD source, not this increment. The reversed common-basis theorem belongs to its separately identified author/review packet.

Run python3 reproduce.py --source-root ../.. from this directory; use --output for an alternate output path. The packaging adapter preserves the exact scientific checker bytes and stages only pinned inherited inputs in a temporary directory. The checker imports only Python standard-library modules, verifies exact source Git blobs and hashes, rebuilds the complete lists, verifies moments with rational lower and upper enclosures, derives Gaussian and row constants from the actual graphs, and tests all47 inequalities and cutoff checkpoints. It does not run downloaded producer, corner-search or assembly code, and it does not materialize the large producer graphs. Independent mathematical review must bind the final proof, checker, certificate and the separate geometry dependency bytes. Arithmetic and finite controls do not prove the imported all-size algorithmic hypotheses.

The precise reversed-geometry dependency is IM-PAPER-TWO-STAGE-TOPOLOGY-031, GEOMETRY_PROOF.md SHA-256 b5b13558d1537202210035ed8f4eff5b66fe8baf027a01e0ed7c5edc5c5d5ff0, and REVERSED_45_CERTIFICATE.json SHA-256 6e2dcd6fa858bb1f1be78070af0798ca7b309bbf3a21ae3a03b369adff206770. Its separate independent review is required; this packet cannot self-accept that prerequisite.
