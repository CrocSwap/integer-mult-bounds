# Sharp rank-six A3 shortening at common support 29

Work over a characteristic-zero field K. Remove any orthogonal eight-root
frame F from the 120 E8 root lines to obtain P112. Use doubled integral
root representatives r, binary labels `(1,c_1 mod2,...,c_8 mod2)` in the
simple-root basis, and the root-evaluation code
`C={ (<r,h>)_(r notin F) : h in K^8 }`.
Binary weight means the F2 rank of the labels of a vector's support.

**Theorem.** Suppose `a_1,...,a_k,q_0,...,q_3` are collectively independent
vectors on P112. If the union S of the small-piece supports has size at
most 29 and every q_i has binary weight at most six, their span T satisfies
`dim(T intersect C)<=2`.

The uniform allowance 29 is sharp: at 30 there are actual independent
pieces satisfying the endpoint conditions with intersection dimension three.
The witness uses one explicit orthogonal puncture, which suffices for
sharpness of a theorem uniform over all such punctures.

PR3221 proved the general statement at 22. PR3227 treated a different
common-support contract: one six-flat plus four coordinates. The new
argument uses robust singleton spans and charges nonminimal shifts.
No new historical profile exclusion is claimed.

## Retained geometry and field transfer

SOURCES.json pins every source and predecessor head. The unchanged
main-branch geometry supplies these finite premises, replayed here:

* Full-root evaluation has Gram matrix 120I. An orthogonal doubled-root
  frame has Gram matrix 8I, so live evaluation has Gram matrix 112I and rank eight.
* Minimum nonzero live support is 53. Every direction of support below 70
  is a scalar root direction.
* A plane with three root lines is A2, with equal-norm coefficient ratio
  plus or minus one. All 7,140 root planes are checked.
* A binary space of dimension at most six contains at most twenty root
  labels. All 788,035 six-spaces are checked through RREF annihilators.

The support claims use the standard real Weyl-chamber theorem and finite
parabolic counts: rank-six parabolics contain at most 36 lines; the eight
seven-node faces contain `42,28,22,14,16,23,37,63` lines. Only the 63-line
E7 face has enough perpendicular roots for support below 70, and its normal
is a root. Root directions have full support 57. If a root belongs to F,
only its own nonzero coordinate is deleted. Otherwise all nonzero frame
pairings have magnitude four, and Parseval gives exactly four such
pairings from `sum_F <r,f>^2=64`. Thus live support is 53 or 56 uniformly.
Nonroot directions have full support at least 78, so eight deletions leave
at least 70.

These facts transfer to K as in PR3221. Perpendicular rational roots have
rational rank at most seven. A nonzero direction vanishing on more than
36 roots cannot have perpendicular rank at most six: a generic real
normal to that rational span would contradict the rank-six parabolic cap.
Thus its rational kernel is one-dimensional whenever the low-support
classification is needed. Its K-valued normal is a K-scalar multiple of a
rational normal, to which the real classification applies. A nonsingular
rational minor likewise transfers the A2 plane relation to K. The chamber
theorem remains a written dependency, not a proof-kernel result.

## Normalize the quotient to A3

Suppose D=`T intersect C` has dimension at least three. In T/D the images
of all k small pieces together with any one q_i are independent. A nonzero
relation would be a nonzero codeword on at most `29+20=49<53` coordinates;
collective independence rules out a zero combination. Since `dim T=k+4`,
this forces `dim D=3` and `dim(T/D)=k+1`.

Modulo the small-piece images, the four q_i have nonzero images in one
dimension. Rescale them to agree, preserving supports and independence.
For suitable small-piece combinations s_i, the codewords
`c_i=q_i-q_0-s_i`, i=1,2,3, are independent by their separate q_i
coefficients. Every nonzero edge has support at most `29+40=69<70`.
Injective evaluation and the A2 relation normalize their directions to
one common nonzero K-scalar multiple of an A3 star: the root-plane
coefficient ratio forces all scales to agree up to signs, which are
absorbed into the equal-norm roots.

Fix the doubled-root star `h_j=2(e_0+e_j)`, j=1,2,3. Successive extension
sets have single pointwise-stabilizer reflection orbits of sizes 240,56,27,
covering every ordered A3 star. The puncture moves with the star, so all
2,025 orthogonal frames are used. Simple reflections act on simple-root
coordinates by invertible linear maps modulo two and fix the leading
coordinate. All 960 root/label bindings are checked; binary weights survive
normalization.

## Robust singleton spans

At a full-root coordinate r define

`v(r)=(0,<r,h_1>/4,<r,h_2>/4,<r,h_3>/4)`,
`k(r)=4-max_z #{i:v_i(r)=z}`.

Outside S the endpoint values are a common nonzero scalar multiple of
v(r), plus a common shift. Thus k(r) lower-bounds their local support.
The full spectrum is `0:20,1:64,2:36`, with total cost 136.

At a cost-one coordinate, three vertex values agree. A unique modal
shift leaves only the exceptional endpoint nonzero. Partition the
64 coordinates into four exceptional sets M_i. Each has sixteen labels,
binary rank six, and full-root label closure exactly M_i. Every proper
hyperplane of that span contains at most ten labels. The primary checker
enumerates all 63 hyperplanes; a separate checker tests all
`4*binomial(16,11)=17,472` eleven-element subsets by elimination. Actual
ten-element rank-five subsets are losing controls.

If q_i contains at least eleven M_i coordinates, its rank-six constraint
pins its entire support to that sixteen-label closure. Call the other
endpoints unpinned, and let u be their number. Each unpinned endpoint
misses at least six mandatory singleton coordinates. If P is total
endpoint support, then

`P <= 16*(4-u)+20*u = 64+4u`.                         (1)

The complete joint puncture census is:

| Frame cost f | Deleted singleton coordinates t | Frames |
|---:|---:|---:|
| 8 | 0 | 45 |
| 8 | 4 | 720 |
| 8 | 8 | 240 |
| 10 | 4 | 960 |
| 12 | 0 | 60 |

The separate checker reconstructs roots and labels, traverses orthogonal
cliques by levels, and reproduces every joint count.

## Charge every missing singleton

Let s=`|S|`, `c_S=sum_(r in S) k(r)`, `d=2s-c_S>=0`, and
`L=136-f-2s`. The number of singleton coordinates deleted by S is at
most d. Let b count live singleton coordinates outside S where the
exceptional endpoint is zero. Each uses the nonmodal shift: the other
three endpoints are nonzero, costing at least two more than its local
minimum one. Other coordinates cost at least their minima; endpoint entries
on S have nonnegative cost. Therefore

`P >= L+d+2b`.                                      (2)

Across all four M_i sets, at most `t+d+b` mandatory coordinates are
missing. The unpinned endpoints require at least 6u omissions. Thus

`6u <= t+d+b <= t+P-L`,

and hence

`L+max(0,6u-t) <= P <= 64+4u`.                       (3)

At s=29 no integer u from zero to four satisfies (3). In particular,
`P>=L` requires the lower bound below, while `P>=L+6u-t` requires the upper:

| (f,t) | L | Required u at least | Required u at most |
|---|---:|---:|---:|
| (8,0) | 70 | 2 | -3 |
| (8,4) | 70 | 2 | -1 |
| (8,8) | 70 | 2 | 1 |
| (10,4) | 68 | 1 | 0 |
| (12,0) | 66 | 1 | -1 |

Smaller s increases L, so every s<=29 is excluded. No binary-rank or
layout assumption on S was used. This proves the theorem.

## Actual counterexample at 30

RESULT.json records the literal witness in canonical full-root order.
Choose its cost-twelve frame; let S be the thirty live cost-two coordinates.
Take one coordinate unit for each element of S. Outside S, set each
q_i to `v_i(r)-mode(v(r))`; set every q_i to zero on S. The frame deletes
no singleton. Each endpoint has its own sixteen-label M_i support and
binary rank six. The thirty units and four endpoints are independent:
their nonempty supports are disjoint.

Outside S, `q_i-q_0` evaluates h_i/4. Correct its discrepancy on S with
the units. Three independent codewords therefore lie in their span.
Exact rational elimination gives piece rank 34, code rank eight and union
rank 39, so the intersection is exactly three. Alternatively, the units
and any one endpoint have support at most 46<53 and independent quotient
images, giving the matching upper bound. The separate checker verifies
every literal identity and matrix ranks modulo 65,537 and 65,539.

This refutes the general common-support assertion at thirty; it does not
realize an original TWOSIDE rank profile. The thirty small pieces are
unrestricted coordinate units. A named caller may have stronger structure.

## Scope and credit

Nick Petalas contributes the robust singleton-defect argument, sharp
support29 contract and support30 witness. PR3221 supplies the original
rank-six A3 shortening and equality closure; PR3227 supplies the neighboring
special-cover result. DreamingOfClouds/PR3154 supplies the original decoder
reduction and conjecture map. Retained E8/P112 and joaqcoo decoder lineage
remains credited in the pinned sources.

Evidence is author-checked, with separate exact implementations and internal
automated review. Human review, formal verification and hosted CI are separate.
Full C5, `C(P112)>=64`, physical suppliers and kappa remain open or unchanged.
New work is Apache-2.0. Development used substantial automated assistance.
