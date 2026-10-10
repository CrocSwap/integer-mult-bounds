# Fixed prime and seven completed ordinary suppliers

This is a conditional refinement of Rohan Arun’s completed-bank PR237 at a7b0ce212bc9f09353a7161bf8a5cee9cefd600c, on hcg890’s PR234 at af3fe331ca60c936229e060681ffccbc1c208678. It inherits that construction's computational model and all-size interfaces, and changes two fixed parameters. It does not assert unconditional formal verification of integer multiplication.

## A smaller positive rare-case bill

Choose q = 2^127 − 1 = 170141183460469231731687303715884105727 **before** choosing any input or atom width. `Prime.lean` proves primality with mathlib's Lucas–Lehmer sufficiency theorem and a kernel-checked `norm_num` residue calculation; it also proves q > 2^80. The Python certificate independently records all 126 residues, beginning at 4 and ending at zero after 125 updates. This prime is classical; no discovery of a prime is claimed.

PR234's immutable `proof/three-stage-cover-bit.tex`, subsection “Finite covers, batching, and the strict moment”, proves an upper bound 2m^3/q on bad low classes, separately for every edge type. Each cleared minor polynomial is nonzero after preservation of rank modulo q; the total degree is at most m^3. Conditioning on invertibility costs at most two. The condition remains valid for our fixed larger prime. Its freshly regenerated prime check excludes only 2,3,5,7 and verifies every remaining fixed factor is below 2^80. The route denominators are 1,2,3,6. Thus no consumed witness or rational denominator vanishes modulo q. No simultaneous union bound over edges is substituted for the separately averaged moments.

For m=120, retain the sharper positive density

    rho = 3456000 / 170141183460469231731687303715884105727.

PR234 replaced this with the looser envelope 10^-16. Every rare class still executes the entire 32m^2 rank-one fallback. We add its full cost, without subtracting the displaced good case. With PR237’s unchanged freshly regenerated banked histogram H, W=261659, E=5916300 and rank mass 31346280, the normalized paid moment is

    P(c) = sum_r [r H_r/(mW)] exp(c log(m/r))
           + rho [32mE/W] exp(c log m).

This is the original weighted moment with tau=1−c. All ranks satisfy 0<r<m, so P is strictly increasing. Rational Mercator logarithm and Taylor exponential enclosures inherited from the parent admit

    c = 709084859748818674574370 / 10^27

and exclude c+10^-27. A second independently implemented positive atanh logarithm and Taylor exponential enclosure checks both signs. Floating-point root finding is not used. Reinstating density 10^-16 at this c makes even the **lower** moment bound exceed one. The improvement consequently requires the proved rare-density change; it is not just printing more digits of the parent result.

Both recurrence gaps are positive: delta_tau = 1−P_upper(c)>0 and delta_linear = 1−31346280/(120·261659)−rho·32·120·5916300/261659>0. The coefficient A=C(1+1/delta_linear+1/delta_tau) is finite. The banked maximum child ratio is 50/120<1/2, so its halving degree is one. No histogram multiplicative factor is introduced.

## The large prime has large, fully paid constants

The new prime makes the cover and all initialization/table costs enormous. Their size is a constant, not a missing term: q never grows with n,w or ancestors. The retained exact-tape contract permits C_primitive to depend on q, the fixed source recipe, the fixed bootstrap level and retained primitive implementations, but not on n,w,ancestor values, or spectator widths except through the logical volume V.

PR234's regenerated finite ledger retains all scalar operations, all 120 rank-22 center-copy children, the single extra copied work stream, 24 temporary roles, generic wrappers, high affine factors, low transpositions, descriptor/matrix preparation, port routing and restoration. These original charges are paid twelve times for twelve data copies. The banked live denominator is W=261659; physical temporary stock is bounded separately by W+12·24=261947, never used to dilute the moment. Complete high fibers are batched and their cardinality cancels in normalized child volumes. They are not independent growing tapes or free row fields.

In particular, writing d=14400, N=240, J=208670, W0=23683 and E0=495304, each original copy retains the parent's exact bound B_base(q):

    B_base(q) <= [unit + J·16(d+1)^2 + J(W0+24)
             + E0(8m^2+8) + E0·128N^3 +16m^3+120+E0+1] q^14400
          = 1568901757016837 q^14400 < q^14401.

PR237’s exact 231 address charts and proper 60-edge-colouring are recomputed from the pinned source. Twelve copies give 177179 full width-120 banks and 998580 incidences. The endpoint uses disjoint residual projectors and the retained PR197 completed-bank lemma. Source-owned gauges are still unbanked. All chart numerators and denominators are below 2^80<q, so their exact inverse and factor replay remain valid over this prime. The removed exterior rank mass is **225370**, calculated directly from 2200·100+18·60+48·65+13·90; PR237’s prose “226200” is a transcription error, while its executable profile correctly uses 31346280 and deficit 52800. We use the executable fresh count.

PR237’s additional selector/routing bill K=12227329044<2^40 stays paid in the ordinary toll. To make the larger-prime overcharge explicit, we conservatively assign each selector an entire high-affine, stock, wrapper and matrix-preparation allowance, despite many of these not being required:

    B_bank(q) <= [12·1568901757016837
                  + 12·208670·(261659+12·24)
                  + K(16(d+1)^2 + (261659+12·24)
                       +128N^3+(8m^2+8)+1)] q^14400 < q^14401.

The coefficient is freshly computed and is below 2^80<q. The extra middle term charges every original routing family against the entire enlarged bank role set, in addition to its original per-copy charge. This adds costs; it never reduces the existing inventory. All q-dependent preprocessing and tape scans remain in C_primitive(q,source,j)(1+B_bank(q)) times the logical-volume-normalized linear/ordinary-width toll. That constant is not assigned the numerical value one. The signed payload prefix upper bound 303094329841208644962256113408<2^98 also lies below q; choosing a larger prime introduces no tighter digit constraint. The separately paid row reserve is bounded by

    log_q stock <= 4 ceil(log2(max(2,n))) (14400w+1) + log_q S_old_leaf.

It is restored and reused. One outer padding factor is less than two, and conversion from binary input has volume factor below q^2, another fixed paid constant. Ordinary leaf algorithms may retain their own primes; complete restored interfaces, rather than a common prime, are required.

## Seven finite levels, with no circular supplier

Start with the parent's completed ordinary saving a0=384599/10^10. For j=1,...,7 define

    a_j = (1−c)c + c a_(j−1) = c−c^j(c−a0).

At level j every ordinary leaf uses only the already completed level j−1 algorithm; recursive coarse children have rank r<m. Seven is an input-independent fixed integer. Each level retains the weighted recurrence and its original coarse/ordinary decomposition:

    T_j(e)/V = O(e^(1−c) + e^((1−c)^2+c(1−a_(j−1))) + e^c log e).

The middle exponent is 1−a_j. The certificate verifies all four finite admission gaps:

    atom: c−a_j;
    borrowing: 1−a_j−c;
    remainder: 1−a_j−c(1−a_(j−1));
    stock: 1−c.

They are strictly positive, including at level seven. The parent finite-cutoff argument therefore applies anew at every level. For each quantified actual constant C>=1 and the smallest gap delta, take

    L = ceil(max(1,36/delta^2,2(4+ceil(log2 C))/delta)), e0=2^L.

Then C(1+log2 e)e^(−delta)<=1/16 beyond e0; below it use the previously completed algorithm. The next finite constant can be C_large+C_old·2^(L(a_j−a_(j−1))). It may be immense but is finite and independent of input width. Certificate cutoffs at C=1 are arithmetic illustrations, not asserted bounds on actual primitive constants. No new external row field is added by nested complete calls; they restore their supplied chunks and treat other outer fields as spectators. The unattained limit a=c is used only for a monotone upper bound on this parameter family, never as a completed ordinary supplier.

## Unchanged complex bridge and exact outer reduction

Retain complex saving b=747454944651775/10^18, the parent's finite bridge, eta=10^-12 and beta=10^-9. The complex cap remains inactive: a7<(1−beta)b. For z=a7(1−2eta), the active outer margin is g(a7)=(1−eta)z/(1+z). The unchanged assembly checks all 47 strict constraints and seven margins. On the 10^-24 grid it admits

    kappa = 354291207342277673841 / 500000000000000000000000
          = 7.08582414684555347682 × 10^-4.

The next grid point fails. Seven levels improve on six by exactly 85·10^-24 and attain the grid floor of the monotone family upper bound, even if the coarse moment is replaced by its adjacent excluded endpoint. This is only a certificate of this fixed parameter family and grid, not global optimality.

The gain over PR237's published 177145602695277/250000000000000000 is exactly

    1951723673841 / 500000000000000000000000
    = 3.903447347682 × 10^-12.

The certificate also compares against the banked parent's unrounded three-level outer bound and a matched 10^-24-grid comparator. Thus the claimed improvement exceeds a reporting/rounding change.

## Verification scope and dependencies

The verifier first checks the exact parent commit and every immutable package byte, then executes all six parent stages afresh: bit physical/geometry, all-column F2 word and inverse, all-used determinant witnesses, complex label/scalar/splice/guard, exact mathematics and finite accounting. It then regenerates PR237’s charts, inverse factor replays, completed banks, colouring, profile, selector bill and original arithmetic, and compares the entire bank certificate to the pinned publication. It consumes those fresh outputs and independently computes this refinement. Saved execution receipts are not inputs. Source drift, missing parent stages, cyclic suppliers, a coarse ordinary oracle, corrupted prime residues, the old rare density and adjacent coarse/kappa points are rejected.

The pinned complex scalar identities hAi,hBi,hx,hy,hid, Lab.inv and five-window NetCert proof sources remain inherited; this package does not rebuild their entire Lean chain or claim a fresh all-column complex scalar proof. The same weighted q-local compiler, complete-stream tape movement, unit-pivot fallback, prime supply, Clifford synthesis, common precision, restored-row, recovery and all-size reduction interfaces remain hypotheses. The new Lean result certifies only the fixed prime and its size. The conditional theorem is T(n)=O(n(log n)^(1−kappa)) in the retained model under those interfaces.

Developed with OpenAI Codex. Original construction and bootstrap attribution are preserved in NOTICE.md.
