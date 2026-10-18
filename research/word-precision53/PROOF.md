# A componentwise fixed budget for a planned signed word

This is standard componentwise error propagation applied to the pinned
coarse-grid source-recovery interface of Chafik Boukhalfa. The predecessor's
joint maximum bound is valid. No flaw in its proof and no new general
numerical-analysis principle is claimed.

There are r distinct owned arrays. At stage k the source s and target t
are distinct; the ideal operation is y_t += sigma T_k y_s, where sigma is
+1 or -1 and ||T_k|| <= a_k. Its implemented completed call leaves every
other array, including its source, exactly unchanged and changes the target
by sigma f_k(x_s), with ||f_k(x)-T_k x|| <= 2u, u=2^-w. The same deterministic
f_k is used in both signs. These are exactly the hypotheses proved by the
pinned COMPOSITION-PROOF.md, under its stated source-magnitude, stable-factor
and clean low-bit conditions. Arbitrary nonlinear reversible maps do not
satisfy this interface automatically.

For initial array norms <=D, initialize B_i=D and E_i=0. At each stage,
with the old source values on the right, update only the target:

    B_t <- B_t + a_k B_s + 1
    E_t <- E_t + a_k E_s + 1.

Assume w>=1. Since 2u<=1, triangle inequality proves by induction that
the implemented array norm is at most B_i, and its discrepancy from the
corresponding ideal word prefix is at most 2u E_i. The sign disappears
only in this upper bound; execution retains every sign and stage order.
No commutation, source independence between calls, or exact additivity of
f is required. Source and target equality is excluded.

All bounds are nonnegative and nondecreasing. Thus B=max_i B_i and
E=max_i E_i at the last stage cover all intermediate external array states.
Choose the least w>=max(1,p) with 2 E 2^-w <= 2^-p. Choose one W as the
maximum of the unchanged source `working_bits` function over the operator
menu, with this B and target/coarse precision w. Its proof gives leaf error
<=u and source recovery error <u/2. The final coarse rounding adds <=u.
This discharges the hypotheses used in the induction, so there is no
circular reliance on observed fixture magnitudes. W and w are fixed for
the entire planned word.

If exact cancellation of a word is required, include its inverse word in
the plan: reverse the original stages and negate each sign. Do not recompute
precision between the forward and inverse calls. Each individual inverse
uses exactly the same deterministic f and therefore restores the previous
state, even though f is nonlinear due to rounding. The entire inverse
restores all data exactly. External arbitrary nonzero contents are allowed
on the promised coarse grid within D; the reserved low W-w bits must be
zero at call boundaries. This is not arbitrary dirty-bit restoration.

## Comparison with the source plan

Let A=max a_k and C=1+A, and let m count every planned stage. Then
B_max,next <= C B_max +1 and E_max,next <= C E_max+1. Consequently our
B is no greater than the predecessor's (C+1)^m(D+1), and E is no greater
than sum_(j=0)^(m-1) C^j <= m C^(m-1). The new coarse guard cannot exceed
the old guard. The source leaf error and recovery formulas are monotone
in B, so their existing working-bit search also cannot increase. Strict
improvements are fixture results, not guaranteed for every word.

The bound is optimal as a componentwise recurrence using only these
nonnegative norm limits and a fresh unit defect each stage: positive scalar
operators, positive initial data, and positive unit defects attain it.
This is not optimality for a specific signed word, rounded cyclic scan,
actual correlated rounding errors, or minimal possible machine precision.

## Complete local execution and cost boundary

The source fixture is parsed from the unique `stages` assignment in pinned
`check_composition.py`. In chronological source,target,operator,sign notation:

    (0,1,0,+1), (1,2,1,-1), (2,0,0,+1),
    (0,2,1,+1), (2,1,0,-1), (1,0,1,+1).

Its six inverse calls are appended, giving 12 complete calls. Each has two
inverse factors and two forward restoration factors: 24 of each for the
whole word. There are three nonzero length-L data arrays, each with two
real components and owned W-bit fractional words, hence 6 L W fractional
data bits, including 6 L (W-w) reserved low zero bits. Magnitude/sign bits,
coefficient and phase descriptions, scalar work registers, program/control
storage and arithmetic workspace remain additional charges. The source
uses no full-length scratch array and O(1) scalar workspace per leaf, and
performs O(L) scalar work per fixed two-factor call. The new planner does
not remove or defer any execution/restoration call or source-access cost.

The receipt counts actual source helper invocations inside all 12 completed
calls, including their validation. It records phase evaluations and the
source's complex add/mul/div/round helper calls. These are partial observation
counters, not a complete primitive or bit-operation invoice: inline scalar
operations, validation comparisons, metadata and Python rational costs are
not equated to unit-price gates. The original phase/coefficient preparation,
physical data movement, head return, source enlargement in a compiler, and
fast arithmetic obligations are retained. The planner itself performs two
scalar updates per stage per bound vector, plus the unchanged working-bit
search over the supplied operator menu; descriptors and exact arithmetic
are not free. No fixed-tape implementation, supplier admission, runtime
speedup, global recurrence for multiplication, or new kappa follows.

## Evidence and its limits

The proof above covers every finite word satisfying the interface. The
separate finite evidence covers the predecessor's 20 fixtures (five lengths,
two margins, two directions). Every executed prefix is checked for source
restoration, coarse-grid closure, and its per-array magnitude bound. At
lengths 1,2,3, the predecessor's independent Gaussian-elimination oracle
checks all 144 prefixes against the per-array error bound. Every 12-stage
word cancels exactly. This reused oracle is attributed, not newly invented.

The independent checker imports neither planner nor leaf implementation.
It expands formal initial-value and defect coefficients for all 240 fixture
prefixes, and separately simulates all 4,680 signed two-port words of lengths
1..4 with norms in {1,3}, all 279,616 initial/defect sign corners. The 340
positive words saturate the abstract recurrence. This bounded check does
not establish the all-word theorem; the induction does.
