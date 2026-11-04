# Which inputs to the restricted header are actually equivalent?

A coordinate packet for a pencil is $(u_i,b_i,w_i)$. At a nonzero image coordinate scale it to $(1,u_i b_i,u_i w_i)$. At a zero image coordinate retain either $(0,0,0)$ or the projective row pair $(0,b_i,w_i)$ scaled to make its first nonzero entry one. A monomial change preserves the multiset of normalized packets, and equal multisets are connected by coordinate permutations and scalings. Thus a packet multiset describes one complete free orbit. Keeping the zero-image packets makes this a group-action quotient even if the current prefix charges alone coincide.

For each ordered pair of present packet types (two copies if the types agree) and each nonzero coefficient, apply an actual row addition to those two packets, normalize them, and replace them in the multiset. These are precisely the paid edges on the quotient. Changing representatives merely rescales the coefficient or relabels the edge. All edges lift to real header operations. Breadth-first distances from the passing vertices are therefore exact paid distances. For ternary full pencils a passing vertex has all slope charges zero and signed scalar imbalance one or minus two. The smaller raw-state oracle instead initializes its permissible orders with actual principal submatrices. Their weighted distance histograms agree on their common ternary domains.

For any fixed field and number of slope rows, this also gives a finite exact solver beyond the closed-form subfamilies. If there are $d$ slope rows, the number of packet types is
$q^{d+1}+(q^{d+1}-1)/(q-1)+1$. The possibilities are a nonzero image normalized to one, a nonzero projective row tuple at image zero, and the zero packet. The number of multisets is at most $\binom{m+t-1}{t-1}$ for $t$ types. Orders at a goal can be checked by the prefix recurrence over counts of types instead of labeled subsets. For fixed alphabet and slope dimension the state count and these tests are polynomial in $m$, albeit with a potentially large degree.

Each normalized multiset represents
$m!(q-1)^{m-n_0}/\prod_j n_j!$ labeled tuples, where $n_0$ is the number of all-zero packets. The weights sum to $(q^m-1)q^{m-1}(q^{m-1}-1)$ for a single nonzero slope. For each $u\ne0$ there are $q^{m-1}$ choices of a normalized $b$ and $q^{m-1}-1$ choices of $w\ne0$ orthogonal to $u$. For $q=3$ the quotient search returns:

| Dimension | Free orbits | Labeled pencil tuples | Tuples above $\max(S,L)$ |
| ---: | ---: | ---: | ---: |
| 2 | 6 | 48 | 0 |
| 3 | 48 | 1,872 | 0 |
| 4 | 234 | 56,160 | 0 |
| 5 | 894 | 1,568,160 | 1,920 |
| 6 | 2,913 | 42,810,768 | 155,520 |
| 7 | 8,445 | 1,160,136,432 | 7,741,440 |
| 8 | 22,344 | 31,361,929,920 | 307,535,872 |

The first gap occurs in dimension five. Dimension eight includes 14,336 labeled tuples with gap two. These are counts of states represented by free orbits, not billions of separately inverted matrices. The sharp all-dimensional upper bound and attaining families are proved in GAP.md. The graph was not truncated to a prescribed maximum cost.

The three exceptional free orbits at dimension five each have weight 640. All five image coordinates are nonzero. In normalized $(b_i,w_i)$ notation, three packets are $(1,0)$. The other two are one of the pairs $(0,1),(1,-1)$ or $(0,-1),(1,1)$ or $(-1,1),(-1,-1)$. The respective separate bounds are $(1,1),(1,1),(1,0)$ and all three true costs are two. The last orbit is the five-coordinate pencil from GAP.md. EXAMPLES.json independently rejects every paid word of smaller cost using actual minors.

The optional extension through dimension 12 is in [LARGE-ORBITS.json](LARGE-ORBITS.json). Across dimensions 9–12 it checks 1,034,466 more free orbits. At dimension 12 the first gap-three orbit appears. The weight of all gap-three orbits there is 12,165,120. The labeled pencil count there is 16,677,056,175,605,280.
