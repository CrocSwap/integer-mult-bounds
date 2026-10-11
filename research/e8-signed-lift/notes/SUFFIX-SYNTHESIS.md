# Transported suffix-response synthesis for shared-cap helper kernels

## Sufficient signed target-map lemma

Consider a fixed signed linear scalar program with disjoint source registers X, target registers Y, and helper registers. Fix a cut c. Every selected helper has its original zero entrance, is untouched except for initial compensation READs before c, has its last such READ before c, and has its first physical MOVE and first non-READ use after c. Select disjoint pivot and donor sets P and B.

For a helper r, let T_r be its exact original initial-helper-to-final-target response. Let Q_r be the sum of its removed initial READ contributions **transported through the exact original suffix following each READ**, including later target-to-target operations. Q_r is not, in general, the raw incidence vector. The actual future response of the still-unmodified helper at c is F_r = T_r - Q_r.

Choose explicit integer coefficients alpha[p,d] satisfying, for every pivot p,

    sum_d alpha[p,d] F_d = Q_p.

Delete precisely the initial READs of the pivots. At c execute the literal setup ADDs

    helper_d += alpha[p,d] helper_p

for each nonzero coefficient. Keep all remaining original scalar gates. Because P and B are disjoint and the selected helpers have no other prefix writes, the pivot values at c are their original dirty inputs; the setup changes no pivot. The target-map difference caused by the deletions is -Q_p times that dirty input. The new setup contributes sum_d alpha[p,d] F_d times the same input. They cancel exactly. Hence the modified program has the same signed final target linear map on **every initial scalar input**, not merely clean source inputs. Source response is unchanged as a special case.

This is a complete sufficient lemma for the final target map. It does not assert that final helper contents equal the originals. The helper state change, arbitrary physical dirt, copied centers, and boundary/chart semantics must be checked for the literal modified program using the appropriate compiler contract. No restoration is silently free, and no unspecified recovery oracle is assumed.

## Sufficient frame permission and literal bill

Let E be a registered nondegenerate rank-one frame contained in the original first frames F_r of every selected helper. Require the common cut to precede every selected helper's original first MOVE. Give pivots entrance E, remove their zero-frame READs, and replace their first 0-to-F_p MOVE by E-to-F_p. Each distinct donor is moved from 0 to E once at the cut, receives all its setup ADDs there, then its original first MOVE becomes E-to-F_d. The original later gates remain at their original frames. Every new setup ADD has both operands at E. Nestedness follows from E contained in F_r. The last physical endpoints remain unchanged. An admitted compiler may require complementary boundary costs depending on its entrance convention; these belong to the complete supplier invoice, not to this local ledger.

For a rank-one E and first-frame dimension f_r, the literal local histogram change is:

- each pivot: +one child of rank f_p-1, -one child of rank f_p;
- each distinct donor: +one rank-one child, +one child of rank f_d-1, -one child of rank f_d;
- rank-zero children are omitted;
- the finite setup ADD count is sum over p,d of nonzero alpha[p,d], with their actual integer coefficient costs charged.

Shared donors are charged once even if they serve many pivots. This is the mechanism that a separate per-pivot invoice misses. For discovery, the fixed-stock compensated weight used in the native search is w(r)=r*((100/r)^a-1)+f, w(0)=0, a=0.000801725878336075, f=(32*100^2/10^16)*100^a. Floating-point discovery values are nominations; the exact complete supplier and all outer inequalities determine the admitted kappa.

## Constructive synthesis

For each actual common cap and cold interval cohort, form the exact response rows F_r and pivot requests Q_p. Gaussian elimination over F2 provides donor-basis nominations, explicit dependency lists, and no recovery oracle. A weighted closure/min-cut selects a shared-donor subfamily: pivots earn w(f_p)-w(f_p-1), and each distinct donor costs w(1)+w(f_d-1)-w(f_d). Exact signed verification then tests explicit unit coefficients against all 960 target columns. F2 nominations that do not pass this test are excluded from the signed candidate.

The native search additionally bounds eligibility by the **first physical MOVE**, not merely the first later ADD, excludes COPY participants and any other pre-MOVE touches, and uses the actual installed word's zero entrances. Thus previous installed gauge/kernel directions are not treated as free virgin donors.

## Actual own witness and scope

The pinned compact word has SHA-256 05df0a39669bb077a9a2fa527904023a5a9da18cf644e06429d44f2a7ea92603. The v2 reverse-adjoint extraction explicitly transported all initial READ responses. On this particular word the transported array equals the raw incidence array byte-for-byte; that equality was measured, not assumed as a general identity.

The native search examined 5,920 eligible cold helpers, all 1,470 registered-or-pair-difference cap directions in its finite library, and 71,594 common-cut cohorts. It tested 774,297 representable parity dependencies and performed 5,449,882 candidate full signed-row checks. These counts include repeated relations across cuts; they are not distinct new theorems or independent witnesses.

The strongest signed nomination uses E=span(e_12-e_13), cut before record 139669, 16 pivots, and 14 distinct donors, with explicit coefficients in SUFFIX-MATROID-351.json. Every selected relation passes all 960 signed transported suffix columns. Its literal predicted histogram change is {1:+14,2:+30,3:-30}; rank mass falls by 16 and its discovery compensated moment changes by -0.013110491280611425. Literal emitter admission and exact full-supplier pricing remain separate requirements. No kappa record is claimed by this file.

The sink variant removes original helper 6661, which occurs in the witness. Consequently the original witness may not simply be appended after sinking: missing-member relations must be removed or a fresh donor basis synthesized against the literal changed word, with response and role-map rechecks. Numeric gains must never be added independently.

## Relationship to earlier constructions

Public raw-read pair/triple kernel families and previous shared-cap searches already use compensation and elementary linear algebra. Gaussian elimination, adjoints, and weighted closure are established methods; there is no first-ever invention claim. The distinct contribution here is to synthesize unrestricted shared-donor cohorts on the **already installed** physical word using its **transported suffix response**, rather than only a prescribed raw-read tuple family, and to optimize the actual distinct-donor bill before emitting exact signed relations. The current concrete family goes beyond the sibling two-donor scan and the previously installed tuple basis. Novelty is scoped to this finite construction and inspected campaign, not all literature.