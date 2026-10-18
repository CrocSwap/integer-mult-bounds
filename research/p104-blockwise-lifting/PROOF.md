# Independent conditional cost review: blocked residue lifting

This note audits the mathematical mechanism requested by batch member 01. It
does not construct an exact fast backend, admit a supplier, or claim a new kappa.
No repository files or public coordination state were changed by this reviewer.

## Sources and scope

Source PR3033 is pinned at
`b12bbaeb5ca2e83f15433fc2dd0ba3b766595281`, specifically
`research/p104-lifting-residue-reduction/README.md`, `split.py`, and
`vendor/lifting.py`. Its predecessor is PR3025 at
`a544ef068a46f4de3bc47d1d02149cbdc3ba547f`, by Tekalign with OpenAI Codex
assistance, Apache-2.0. PR3033 proves the translation lattice and prices an
ordinary mutable-buffer implementation. Its reset is explicitly not reversible
uncomputation. Its actual native fixture has N=512 and rank seven; no variable
rank native recipe follows merely from that fixture.

The all-parameter result below concerns the distinct-axis Gaussian-integer
lifting core L_r on N=2^r entries, optionally with separately priced Gaussian
monomial wrappers. It assumes fixed 0<a<1 and a genuinely uniform complete
reversible ideal backend for every rank used, in both directions. The cost model
is bit work with addressed-array access charged for its full address and payload.
It is not a fixed-tape movement bound.

## Exact block interface

For a block of k consecutive stages put g_k=floor(k/2)+1. PR3033 gives, for all
signed Gaussian integer vectors x,

    x = 2^g_k q + s,  0 <= Re(s), Im(s) < 2^g_k,
    B_k(x) = 2^g_k U_k(q) + B_k(s).

The same identity holds for the literal inverse, with B_k^{-1} and U_k^{-1}.
Permuting the active coordinate bits does not change this identity: it only
relabels independent k-cubes. No low-magnitude or nonnegative-input assumption
is made about x. All divisions use Euclidean residues, including negative x.

The required backend contract is stronger than an ordinary output routine. For
each sign epsilon in {+,-}, it must reversibly evaluate

    D_(k,+)(q) = 2^g_k U_k(q),
    D_(k,-)(q) = 2^g_k U_k^{-1}(q),

with exact integer results, preserved source and fully restored workspace, or
provide an equivalent reversible in-place U_k^{epsilon} interface on inputs
2^g_k q with the necessary clean extension bits. Its complete forward and
uncomputation tariff is bounded, up to a uniform constant, by

    E(k,V) <= K 2^k V k^(1-a).

It must account for local addresses, coefficient/phase access, internal widths,
initialization, source access, cleanup and any local head return. Merely having
the reverse of U_k on the image U_k(2^g_k Z[i]^(2^k)) does not supply U_k^{-1}
on every input of the form 2^g_k q. Both directional input lattices are needed.
The scaled map D_(k,+) is not a unimodular integer map; its overwrite cannot be
declared reversible without a specified extension or source-preserving interface.

Let V=W+O(r) bound all components of the complete lifting core and the copy/add
registers. The elementary magnitude estimate M -> 2M+1 per lift gives such a
bound. A narrow block beginning at s has width at most g_k+k+O(1)=O(k), so its
complete k-stage bit work, including k-bit local address arithmetic, is
O(2^k k^2). The backend's own internal width growth remains inside E; a bound on
its output norm alone is not a bound on every possible implementation prefix.

## Reversible cleanup with arbitrary source data

A clean evaluator for B_k preserves x and adds B_k(x) to a target y. It does the
following using clean quotient, residue and backend-output registers:

1. Reversibly copy the high and low bits of x to q and s.
2. Compute D_(k,+)(q) into a clean wide target and run B_k on s.
3. Add their sum to y at its full width.
4. Reverse the narrow computation and backend computation, then uncopy q and s.

The residue bank must represent its initial nonnegative range without sign
wrapping: it needs at least g_k+1 signed bits initially and O(k) bits for the
literal prefixes. Copying those residues into a smaller signed word can return
clean work while computing the wrong map. The stated O(k) narrow bank and
O(W+r) wide headroom pay for this requirement.

Thus (x,y,0) -> (x,y+B_k(x),0). The same construction, using D_(k,-) and the
literal narrow inverse, supplies an evaluator for B_k^{-1}. For an arbitrary
dirty target, fixed-width modular addition defines an everywhere reversible
operator; it agrees with integer addition on the stated no-overflow range. An
integer caller must price the target's own width as well.

To obtain a clean in-place block from x and an additional zero cube y, evaluate
B_k(x) into y, evaluate and subtract B_k^{-1}(y) from x, and swap x and y. The
original x register is then zero before the swap, and y is zero afterward.
This uses four backend calls in total, counting inverse uncomputations, and four
narrow passes. Hence it changes constants, not the exponent. Reversing this
whole circuit supplies the literal inverse with the same cost. This is a
construction using clean buffers; it does not establish that arbitrary dirty
helpers can serve as those buffers at zero cost.

## Paid local-cube dispatcher

Consider active bits p,...,p+k-1. A spectator index u has the unique decomposition
u=a+2^p b, where 0<=a<2^p. The local coordinate v embeds as

    i_(p,k,u)(v) = a + 2^p v + 2^(p+k) b,  0<=v<2^k.

The fields are disjoint. Every ambient index appears in exactly one such cube.
Computing or reversing an r-bit embedding takes O(r) bit operations; no
multiplication is needed. Counters and a scratch index can be restored because
the schedule is public and has known finite bounds.

Gather a single cube by swaps between its global entries and a zero contiguous
working cube, so the global entries are temporarily zero. Run the clean
in-place block locally, then swap the output back through the same embedding.
The working cube returns to zero. Process spectator cubes sequentially. Per
global block layer this pays O(N(V+r)) for all global index operations and
payload moves. Every local computation uses k-bit local addresses. In contrast,
charging an r-bit ambient index at each one of the Nk local butterflies gives
O(Nkr) per layer and O(Nr^2) overall; that interpretation cannot be used to
justify the improved bound.

This dispatcher is explicit in the addressed-array model. An r-bit address
does not itself pay for movement to that address on a physical tape. Such
movement, a global layout conversion and its cleanup remain a separate tariff.

## Exact tail partition and resulting bound

Let 1<=h<=r be an integer, write r=q h+t with 0<=t<h, and take q rank-h blocks
followed by one rank-t block when t>0. Let their ranks be k_1,...,k_B, with
B=ceil(r/h). The last block is genuine rank t, not a rank-h call with free
padding. The uniform backend must support t, or an alternative admissible-rank
partition must be proved and priced.

The complete core cost from the preceding construction is

    T <= C N [ V sum_i k_i^(1-a)
                + sum_i k_i^2 + (V+r) B ]
         + Setup + Wrap + PhysicalRouting.

There are four backend calls per local cube, so their exact number is
4 sum_i 2^(r-k_i); their total time is bounded by
4 K N V sum_i k_i^(1-a). All summands above are present. The block identities
give the elementary all-parameter estimates

    sum_i k_i = r,
    sum_i k_i^2 = q h^2+t^2 <= r h,
    r h^(-a) <= sum_i k_i^(1-a) <= 2 r h^(-a),
    B <= 2 r/h.

For the upper power bound, q h^(1-a)+t^(1-a) is at most
r h^(-a)+h^(1-a), which is at most 2r h^(-a). Thus, for W>=r and V=O(W),

    T = O(N [ W r h^(-a) + r h + (W+r)r/h ])
        + Setup + Wrap + PhysicalRouting
      = O(N [ W r h^(-a) + r h ])
        + Setup + Wrap + PhysicalRouting.

The last absorption uses h>=1, 0<a<1 and W>=r. It does not discard a physical
movement term. For smaller original W, replace W by V=W+O(r) in the bound.
For ambient dimension n>=r and N=2^n, the same construction replaces r by n
only in the dispatcher term: O(N(V+n)B). The displayed absorption therefore
also holds for n=O(r), W>=n, up to constant factors.

Taking h=min(r,ceil(W^(1/(1+a)))) gives, up to constants depending on a and the
backend tariff,

    O(N r W^(1/(1+a)))       for r <= W <= r^(1+a),
    O(N W r^(1-a))          for W >= r^(1+a),

before the three displayed external terms. At W=Theta(r), this is
O(N r^(2-b)), b=a/(1+a), compared with the scalar O(Nr^2) invoice. The inherited
ideal rank-r exponent a is recovered only in the wide regime
W=Omega(r^(1+a)). The block choice provides a conditional upper bound; it is
not a lower bound or an optimality theorem for possible residue algorithms.

## Peak storage and wrapper compilation

With spectator cubes processed sequentially, the retained data occupy O(NV)
bits and the additional clean working storage is

    O(2^h(V+h) + r) + max_(1<=k<=h) S_E(k,V),

where S_E is the backend's complete peak workspace. This includes the gathered
cube, the extra cube used for in-place cleanup, and constant-many wide/narrow
evaluation buffers. No simultaneous allocation for all N/2^h local calls is
needed. Backend stock cannot be inferred from its time exponent; it must be
specified. Source/query owners and any global wrapper tables are additional.

Generic monomial wrappers retain their complete Setup and Wrap tariffs. In
particular, leaving PR3033's O(Nr^2) degree-two plan-expansion bound unchanged
would consume the entire W=Theta(r) saving.

For the explicitly described affine-address/Z4-quadratic subclass there is a
separate addressed-array compiler: let y=Mx+o over GF(2) and

    phi(x)=c+sum_j l_j x_j+2 sum_(j<k) q_jk x_j x_k mod 4.

Traverse binary Gray x. Maintain y and d_j=l_j+2 sum_(k!=j)q_jk x_k mod4.
When bit j toggles, first add (1-2x_j)d_j to phi, toggle y by column j of M,
and add 2q_jk to every d_k for k!=j; d_j is unchanged. The sign in the latter
update disappears because +2 and -2 agree modulo four. This proves O(n) bit
work per address and O(Nn+n^2) total compilation, including n-bit table writes.
The inverse table can be emitted by reversing each recorded address/phase pair.
Given the bijection premise on M, no sorting is needed. Cycle scheduling and
payload swaps then cost O(Nn) and O(NV), respectively, in addressed arrays.

An ordinary O(N)-word compiler/scheduler can retain its O(Nn)-bit execution
history and reverse it after read-only use, keeping the same bit-work order.
Thus cleanup can be paid, but table/schedule/history storage is O(Nn), separate
from the local-cube peak. For n=Theta(r), W>=n this compiler removes the
quadratic setup obstruction in this model. This is a mathematical alternative
compiler; it is not a claim that PR3033 already implements it, nor that its
physical fixed-tape movement or stock is admitted.

## Decisive stop gates

The recurrence is valid under the explicit addressed-array backend, dispatcher,
clean-stock and optional wrapper premises. It should stop as a conditional
reduction at the first missing item below:

* An independent all-rank exact backend with both directional lattice contracts
  and complete tariff E(k,V). Direct Walsh evaluation has a=0 and supplies no
  exponent saving. Invoking this same nonlinear reduction as that backend is
  circular; the map a -> a/(1+a) has no positive fixed point.
* A backend based on approximate native calls must pay precision sufficient for
  exact recovery, including all rounding and cleanup. A sufficient relative
  request for a 2^k cube of V-bit components is
  u<=2^(-V-ceil((k+1)/2)-2), as in PR3033's norm argument. The collector's
  original accuracy request cannot replace this W-dependent one.
* A realizable clean/dirty stock assignment for the displayed peak, backend
  workspace and any O(Nn) wrapper control storage. A private collector returning
  zero does not prove this internal stock assignment.
* Physical gather/scatter, wrapper access and exact head-return costs compatible
  with the claimed time. The addressed-memory proof does not settle them.
* An all-size native recipe and full source/query/precision/call recurrence,
  followed by the project's joint bit/complex and outer assembly inequalities.
  The exponent b above is not a kappa and does not establish that implication.

## Independent checks

`cost_check.py` uses exact integer roots and rational outward
enclosures to check declared finite parameter ranges, independently of the
source implementation. It also compares the Gray compiler invariant with direct
quadratic evaluation and checks a deliberately omitted derivative update is
detected. These checks corroborate the written identities; the all-parameter
argument is the derivation above, and there is no formal-kernel proof here.

Executed with both `python3 -I -B independent-cost-screen.py` and
`python3 -O -I -B independent-cost-screen.py`: all 3,830 parameter
cases passed for r=1,...,256, a in {1/4,1/3,1/2,2/3,3/4}, and the declared
widths {r, r+floor(r/2), r^2}. The exact Gray comparison covered all 2,040
columns of four deterministic wrapper recipes in each dimension 1,...,8;
930 columns detected the omitted-update negative control. The script uses
80-bit-denominator rational bounds with exact integer-root inequalities, not
floating estimates. These finite checks do not evaluate any hypothesized fast
backend or any physical routing algorithm.

## Follow-up implementation review and fixes

The reviewer inspected the parent's `research/p104-blockwise-lifting/` reference
without editing it and found three issues that the parent corrected:

1. The Gray compiler's initial sorting check could add O(Nn^2) addressed bit
   work. The final version checks uniqueness with a seen-bit array, costing
   O(Nn), including full addresses.
2. A signed residue bank with insufficient width computed a wrong map while
   still returning clean work. The explicit original witness was rank six,
   width four, input `[(-1,0)] + [(0,0)]*63`, zero target: it returned normally
   but differed from the literal lifting result in all 64 entries. Here g=4
   and copying residue 15 into a four-bit signed word changed it to -1.
   The parent now requires width>=g+k+3, and this exact witness is rejected
   with `narrow signed headroom`. This stronger sufficient headroom bound
   remains O(k) and is consistent with W+O(r) overall width.
3. The default convenience dispatcher copied the complete input array. The
   parent added an explicit `inplace=True` path. The local-stock statement
   applies to that path; the convenience wrapper's global snapshot is additional.

A focused read-only check executed the exact reviewed `blockwise.py` bytes,
verified rejection of the rank-six witness and a singular wrapper, checked
the rank-seven (3,3,1) in-place forward map, literal inverse and complete macro
invoice, and compared 510 dense affine/quadratic wrapper entries in dimensions
one through eight with direct formulas. It returned
`PASS_FOCUSED_COST_REVIEW_FIXES`. Reviewed SHA256 values:

* `blockwise.py`: `0fc1c0b9858b41567d3d291897b041cbb4121bf9b50c6378ff7b9f5c53340780`
* `verify.py`: `10360cc91724d19829ffc1841e4b1bc040403d43b516c0314adf3bf4a5b0b013`

The two clean XOR evaluators and the inverse-XOR in-place permutation use four
backend oracle calls, matching the constant-factor mathematical construction.
No remaining mathematical mismatch was found in the inspected block order,
cleanup or macro tariff at these bytes. The Python reference remains semantic
evidence, with constant-many extra local arrays; it is not a physical reversible
machine or an allocation/dirty-helper certificate. The backend, stock, physical
and outer-transfer stop gates above remain unchanged. Later implementation
changes require review of the affected bytes again.

Prepared by the independent asymptotic-bounds reviewer, with OpenAI Codex
assistance. Source credit and historical model restrictions are retained above.
