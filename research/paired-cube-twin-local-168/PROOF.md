# Construction and retained proof contracts

The exact prerequisite is PR168 at `4a3c769e5c5430e7114c4d3e099ff34664677f17`. PR144 supplies the paired-coordinate/shared-core framework and the configurable local channel circuit; PR161/168 supply the annealed modules, fused outputs, scalar words, L1 bit association, nested schedules and the bit physical layer; PR162 supplies the carrier extension rule; PR166 supplies terminal-output accumulation. This package changes both local circuits, rebuilds the bit physical layer, deletes 34 bit terminal sinks and rederives the complete finite composition under the inherited all-size interfaces.

## Shared-edge local circuit

Each of the 165 cubes computes the same 13 local outputs: the six single-bit sums $A[i,a]$ of the four ports with bit $i=a$, the six signed channels $G[j,k,m]$ and $F=A[f,0]+A[f,1]$. PR144's circuit lets every $A[i,a]$ be assembled from two edge sums along a direction $d\ne i$ or from two face diagonals, and every $G[j,k,m]$ from edge differences along the third direction, long-diagonal differences or fixed-coordinate differences. PR168's L1 circuit assembles $A[1,\cdot]$ from direction-2 edges, $A[2,\cdot]$ from direction-1 edges and $G[1,2,0]$ from direction-0 edge differences.

This package assembles $A[1,0]$, $A[1,1]$ and $A[2,1]$ from direction-0 edges. The four direction-0 edge sums of a cube are then shared by three $A$ channels and the $G[1,2,0]$ channel, while the four direction-2 edge sums disappear and the direction-1 edge sums remain shared by $A[2,0]$ and $G[0,2,\cdot]$. The circuit has 29 additions per cube instead of 27. Every addition still has support-disjoint operands and every root support equals its contract; the graph builder and the independent scalar audit check this. The modules, the `f8:00111100` fold order and the nested schedule of PR168 are unchanged.

The new signed graph has c=21,249, q=3,157 and M=32,971 mixer operations. Carrier arcs are chosen by our own legal-edge Hopcroft–Karp matching on the coordinate-padded frames and extended by PR162's greedy rule; the compiled closure is acyclic and span-contained. There are 11,364 arcs instead of 10,704, so the complete virtual auxiliary stock is R_scalar=c+q−11,364=13,042. Gauges are selected by PR144's chronological greedy rule: 2,310 roles of rank 18.

## Physical word, handoffs and frames

Operation frames are descended from the compiler frames by exact endpoint moves of single operations, equal-frame components and connected bundles: each move takes the join of incoming frames and value span or the meet of outgoing frames. 12,869 operations differ from the compiler frames. The 2,310 compensated handoffs pair dead ungauged non-root donors, whose last frames lie in the recipient gauge, with gauged recipients read at their first-use deadline; they leave 10,732 roles before terminal deletion. Only the explicit final frames and pairs are mathematical inputs.

The verifier reconstructs every signed source/target identity, binary value span, carrier, center closure, physical role chain and actual target read. Compensation reads the current inherited dirty value with independently derived exact adjoint coefficients. The original physical word is checked on all 13,372 formal source, target and dirty columns under both shear signs. Every signed gate a←c_a a+c_b b is undone by a←c_a a−c_a c_b b, in reverse chronology; gates whose carried operand is the minuend are compiled with the sign on the destination coefficient and are audited as such.

## Terminal-output accumulation

The terminal compiler selects 44 ungauged, destination-only, disjoint-root roles. Each has eight targets, rank-18 common read frame and coefficient 1/2. No removed role is a source, gauge, alias endpoint, retained consumer input or another root. All sink writes are additive in the final frame. Target groups are disjoint, and each pivot's first old nonzero-frame target read follows its sink's last write. Of the 165 disjoint roots, 119 have retained producer consumers, 13 are written in the center phase and 4 have no uncorrected pivot.

Retain every surviving coordinate's original dirty-response correction, including response through a deleted sink. At the common zero frame after the center phase, subtract each pivot from its seven other targets. Replace r←r+c b by y_p←y_p+c b/2. After the last write, add y_p back to those seven targets. Remove the old sink read and register. The independent target checker includes all intervening compensation reads and every new target-frame event; source-role frames at replaced writes remain as before.

The modified executor checks all 1,320 source, 1,320 target and 10,688 dirty columns in both directions. An independently computed absolute residual coefficient bound of 397,506 makes 24-bit packed digits injective. The actual literal reverse word restores all retained dirty coordinates. Missing a pivot write, deleting an ancestor's original response and omitting the initial target shears are rejected. The scalar addition delta is −202, so the complete earlier virtual scalar charge remains conservative; the fixed odd divisor remains three.

For each terminal sink, the pivot copies the old rank increments and the remaining seven targets enter the shared rank-18 frame. The sink's final rank-four increment and one target rank-18 increment disappear. The three-core histogram loses three children of rank 4 and three of rank 18; W loses one. The final profile is m=66, W=13,328, rank=878,328, deficit=1,320 and largest child 20. The exact stock identity is 13,042−10,688=2,310 handoffs+44 terminal sinks. Outward rational intervals prove b=132438677973/(2·10^14); its next 10^−15 grid point fails this fixed profile.

## Bit local circuit, physical word, terminal sinks, exact decoder and prime range

The bit graph (p=12, h=24, v=1,760) is PR168's: its annealed pair module, its all-but-one module with n=10, its L1 association of the G channels, its partner-pair source mixing and its output merge are unchanged. Only the per-cube local circuit differs: the sums $A[2,0]$ and $A[2,1]$ of the four ports with bit 2 fixed are assembled from the two face diagonals instead of two direction-1 edges; every addition keeps support-disjoint operands and every output keeps its contract. The carrier arcs are a fresh maximum matching by the retained generator's Hopcroft–Karp rule, and the gauges are PR144's chronological greedy selection with the G-nondegeneracy filter: 3,960 gauges of ranks 20 and 21. The virtual stock is R=19,348. Admission runs the retained package checker on this graph: exact rational frames, the mod-2 decoder with stars and side parts, source lines and target caps, operand nesting, role and target chains, the partner chronology, G-nondegeneracy, an F2 dirty-scratch replay, the ledger recount and five mutation controls.

**Physical layer.** Operation frames are descended from the compiler frames by moving equal-frame connected groups to the join of their incoming frames and node spans or to the meet of their outgoing frames, repairing degenerate endpoints by one row; gauge, root and target frames are fixed. 6,138 operation frames differ from the compiler frames, including 164 enlargements; each is nondegenerate for G and contains its node's full value span. The 1,760 aliases pair dead ungauged non-root donors, whose last frames lie in the recipient gauge, with gauged recipients read immediately before their first operation. All physical role chains and retimed target reads are recounted independently.

**Terminal sinks.** Apply James Chang's PR166 substitution to 34 face0 side roots. Each selected root is a destination-only, ungauged, non-alias, non-source register with a single root read, no retained consumers, no center-phase writes, all writes inside its rank-21 root cap and a pivot target with no earlier gauge correction. Its register is deleted; at the common zero frame the pivot is subtracted from the other targets, every write goes to the pivot, and after the last write the pivot is added back at the root frame. The compiler recomputes every condition from the physical frames and the actual gauge read chronology, replays the complete modified target chronology with every retained partner delivery, and checks the whole modified word on all 1,760 source, 1,760 target and 17,554 dirty columns over F2 and over the integers with an independently computed residual bound of 62,018 and 24-bit packed digits. Omitting a write, an ancestor response or the initial target shear is rejected. The scalar addition delta is −158, so the retained virtual scalar inventory remains conservative. Per core the histogram loses three children of rank 21 and three of rank 3 per sink.

The final bit profile has virtual R=19,348, physical R=17,554, W=21,074, rank=1,515,392, deficit=1,936 and largest child 60. Independent literal execution checks every one of the 21,108 formal columns of the physical word over F2 before deletion, restores every source/dirty coordinate and verifies the identity on targets. Separate integer execution verifies the defining integer decoder, whose F2 reduction is the identity; it does not assert an integer identity. Missing compensation, missing partner delivery, stale dirty reads and a zero operation frame are rejected.

Exact Bareiss witnesses cover all 24,459 used bit frame IDs and their distinct integer bases B. Each nonzero d=det(9BGB^t) factors into powers of primes at most 31 times a positive residual below 2^80; every factor identity is checked. Determinants reach 118 bits. Every prime q>2^80 therefore avoids every determinant, preserving all Gram inverses/projectors over Z/q^w and the original fixed-prime range. Sources, gauges, roots, operation frames, partner mixes/deliveries and ambient frames are included. Zero determinants, incorrect factors and oversized residuals are rejected.

Every ideal bit edge pays the full 32m^2 fallback on fraction 10^−16, and 2m^3/2^80<10^−16. The contaminated moment and rank mass contract. Outward rational intervals certify a0=668298937775631/10^18; the next 10^−18 grid point fails this fixed envelope. The true bad fraction may be smaller; no optimality claim is inferred.

Use the retained standard ordinary wrapper with a_old=384599/10^10. Select the first 10^−24 grid point above a0/(1+a0−a_old): theta=133575656392233867107/(2·10^23). Its ordinary saving is A_B=(1−theta)a0+theta a_old. Both adapter and restored-row tolls are paid by A_B<theta<1−A_B; the previous grid point fails the strict lower condition. The full uniform weighted local-ring and restoration contracts remain inherited assumptions.

## Full finite scalar, group, router and row bills

Retain R_scalar=13,042 and M=32,971 despite physical handoffs and terminal deletion. The complete local scalar charge is

    L=4(c+v)+10v+4hv+4h^2+8h+8+2h+8 R_scalar v(M+16)+32v
     =4,543,086,018,280.

Decoder denominators divide six, signed gate coefficients are ±1, dirty numerators use M+16 bits and 3q<2^15. The fixed odd divisor is three. Let V=|O(66,2)|, W=V·13,328, N=V·1,320 and s=V·878,328. Group cardinality cancels only in the normalized moment. It remains in K=3VL+8W+4N+8·66·R_scalar·V, G_route=64·67^3(K+1)(W+1)^2 and E=64(W+66+G_route+1)^3. The verifier rederives literal charges, B=s+E, C0=32·66·B^2, C1=1 and exact-child induction.

The 66→20 halving depth is one. Full W has 2,159 bits. The separate reserves 9,909 and 252 give total row coefficient 12,320, polynomial degree 70,000, positive gap 224336/5 and suffix slope 280,000. Bit selector rows are borrowed and restored internally. Dropping any reserve, replacing full W by local W, charging only physical roles for the scalar word, omitting terminal removals or counting them as aliases is rejected.

## Paid balanced transfer

Use the PR34/RaD paid positional layout as applied to signed words in PR100/103 and retained in PR141. Both axis-major/group-major permutations are paid by the ordinary arbitrary-coordinate router. Active, spectator, scratch, phase, control and restored-row fields move together. The additional long-axis top bit is paid, with twiddle order and inverse alignment preserved. The geometric inequality remains strict. The application retains ordinary complete interchange/restoration and completed exact complex tensor contracts.

Set b=132438677973/(2·10^14), beta=eta=10^−24, zeta=10^−30 and a=min(A_B,(1−beta)b−zeta). The complex branch binds: a=(1−beta)b−zeta. With q=a(1−2eta), choose

    c=q+eta/4, epsilon=(1−eta)/(1+q), lambda'=1−q,
    lambda=((1−a)+lambda')/2, g=epsilon q,
    r=(g+1−epsilon)/2, delta=eta/8.

The seven margins are 1−epsilon, a, g, a, min(1−epsilon−delta,r−delta), 1−epsilon−delta and epsilon; their minimum is g. The identities 1−epsilon−g=eta, 1−epsilon−r=eta/2 and 1−epsilon(1+c)=eta−epsilon eta/4 preserve strict gaps. All 47 inequalities remain, including epsilon−a>0. Source normalization proves the PR141 arithmetic body changes only bridge plumbing and the explicit guard a≤A_B.

The certified point is kappa=330877589979561/(5·10^17). Its next 10^−18 grid point fails only for these fixed supplier certificates and parameters. Matched comparisons change the positive outer backoffs while holding the same suppliers; the published parent certificate is reported separately.

Finite checks establish supplied words, profiles, exact moments, prime witnesses, source closure, finite bills and arithmetic. General Clifford lifts, common generic bases, uniform weighted compilation, arbitrary-width routing, restored internal rows, layout applicability, prime supply, precision/recovery, uniform setup and analytic fixed-tape transfer remain inherited all-size contracts.
