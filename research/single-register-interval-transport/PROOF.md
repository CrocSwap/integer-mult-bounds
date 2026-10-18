# Single-register transport at complete leaf boundaries

Status: conditional corollary of pinned PR1085 and PR1278. This draft awaits
external review. It gives no new multiplication exponent or working precision.

Let n >= 1, h = ceil(log2 n), and d = h+2. Use the unchanged balanced
PR628 ideal word on one source, one target, and h disjoint reserved connectors.
Deeper connectors remain shared between sibling calls.

Let P_t denote a prefix
at a complete ideal-leaf boundary, in either call direction. Let J_j inject
one register into the full state. Every norm on the full state is the maximum
of the register norms. Source and target registers have the same normed space.

## Claim

For every pair of cuts s,t, either order, and every register j:

1. If every factor is a contraction, with no commutation assumption,
   `||P_t P_s^-1 J_j|| <= d`.
2. If factors commute and every subset product has norm at most G >= 1,
   including the empty product, `||P_t P_s^-1 J_j|| <= d G`.

The quantifier over j includes the destination of the leaf just completed at s.
It also includes every other register; the upper bound needs no special destination property.
These are single-register input bounds, not the full joint-state operator norm.

## Entrywise argument

PR1085 proves that each entry of P_t and P_s^-1 is either zero or one signed
ordered squarefree monomial. Thus each entry of their product starts as a sum
of at most d signed monomials. Combining equal words and cancellations cannot
increase the sum of absolute coefficients. This coefficient sum is at most d
in each entry, although an entire row can have quadratic total coefficient sum.

In case 1, each product term is a contraction by submultiplicativity.
Repeated factors and their order do not affect this conclusion. The triangle
inequality bounds each entry by d. Case 1 does not use PR1278.

In case 2, PR1278 proves that every surviving free word in the interval matrix
is squarefree, including reverse intervals and both signs. Commutation converts
each such word into a subset product, whose norm is at most G. The coefficient
bound therefore gives dG for each matrix entry. Cancellation occurs in the
free algebra before substitution; no commutative quotient is used to remove
repeated indices. Merely bounding individual factors by G does not suffice.

For any vector v in register j, the i-th output is the single block
`(P_t P_s^-1)[i,j] v`. Taking the maximum over output registers proves both
claims. It does not sum over output registers. This is the point where a
single-register perturbation differs from arbitrary simultaneous perturbations.

## Relation to the quadratic example

PR1374's all-height commuting-isometry family has a target-row coefficient
of absolute value j on connector z_j. Its cuts are
`a_h=floor(3*4^(h-1)/5)` and `b_h=(4^h+2)/3`. For h >= 2,
the leaf immediately before a_h has destination z_(h-1). Therefore its
destination column attains h-1 at b_h. This proves order Theta(h) even
for errors injected into the actual completed leaf destination.

Here is the destination argument, separate from the predecessor's coefficient
formula. In a positive height-k call define `c_k^- = floor(3*4^k/5)`
and `c_k^+ = ceil(3*4^k/5)`. For k=1, the instruction just before c_k^-=2
and the instruction just after c_k^+=3 both write the call's target.
For k>=2, both cuts lie strictly inside the inverse-left phase, of length
L=4^(k-1). The complementary child cuts satisfy
`3L-c_k^- = c_(k-1)^+` and `3L-c_k^+ = c_(k-1)^-`.

Reversal exchanges the preceding and following instructions. It preserves
their destinations. Recursion therefore follows the left child and exchanges
these two cases until the height-one case. The terminal destination is the
connector one level above the deepest connector (or the target when k=1).

Apply this to the first left child of the height-h parent: its height is h-1,
and the resulting destination is z_(h-1). This argument uses addresses only;
it holds for the predecessor's signed factors too.

For all h >= 2, the worst destination-supported amplification is consequently
between h-1 and h+2 in the contraction domain, and also in the commuting
subset domain with G=1. This does not establish the exact optimal constant.

For n=4, its target row at cuts [2,6) is (-2,1,-1,2). Its full row norm is 6,
whereas its largest single-register effect is 2. The two conclusions coexist.
PR1374 retains credit for the example and its all-height family.

## Conditional error transport

Suppose an actual completed leaf differs from its ideal linear map only in
that leaf's destination. Let its error there have norm at most
`a u (M_actual+1)`, uniformly over the actual trajectory. The source and other
registers must return exactly at each leaf boundary. Let there be N leaves,
and let the initial joint norm be at most D.

In case 2 put B=dG and t=N dG a u. Variation of constants and the column
bound give `M_actual <= B D + t(M_actual+1)`. If t <= 1/2, then
`M_actual <= 2 B D+1`, and the execution error is at most
`2 N dG a u (B D+1)`. In case 1 take G=1.

The error coefficient a must include a valid bound for negative leaves at
their required preimages. Fixed coefficient preparation, internal leaf growth,
phase access, exact restoration, and the full arithmetic/tape bill are separate
premises. This note does not validate those premises for PR1054 or PR1295 and
does not substitute a smaller precision into either implementation.

## Evidence and trust boundary

The proof is a new entrywise deduction from the two explicitly pinned lemmas.
Finite checks do not establish those all-size premises. The checker executes
the original compose AST with ideal scalar leaves and propagates unit impulses.
A second implementation computes prefix matrices recursively, replacing each
completed subtree by its product shear, and uses exact Gauss-Jordan inversion.
It imports neither a predecessor verifier nor the literal dispatcher traversal.
The source inventory separately checks pin equality against Git objects.

No proof assistant or independent human reviewer has checked this corollary.
No rounded numerical kernel, supplier, selected frontier, or upstream file changes.

## Credit

Chafik Boukhalfa supplies PR628 and PR905. Hanson Sun supplies PR1085 and
PR1244. Charles Bethin supplies PR1278. Arham Tahir supplies PR1374.

Philipp/mightyOil supplies PR1295's precision follow-up. Gareth Davidson and
0xkilgore supply related precision and nonlinear restoration work.
Prepared for Charles Bethin with substantial OpenAI Codex assistance.
New material is Apache-2.0; retained predecessor text and notices stay unchanged.
