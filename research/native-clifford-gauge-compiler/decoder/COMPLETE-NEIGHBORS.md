# Complete local transvection neighborhoods in 1,022 candidates

Every one-step transvection change of a nine-dimensional Lagrangian is represented by exactly one of 1,022 explicit axes. This replaces the 261,632 nonfixed axes of the original local search by a complete list with 256 times fewer candidates. It does not prune a possible rank improvement or neutral chart transition. The statement concerns candidate count, not an unmeasured wall-clock speedup or an improved κ.

## Universal theorem

Let U be an n-dimensional Lagrangian over F₂, with basis u₀,…,u_(n−1). Choose vectors v_j with ω(u_i,v_j)=δ_ij. They need not form an isotropic basis. For each nonzero bit vector b, put

    a₀(b)=sum_j b_j v_j.

Choose any j with b_j=1 and put a₁(b)=a₀(b)+u_j. Then

    { T_a₀(b) U, T_a₁(b) U : b ≠ 0 }

contains every Lagrangian obtainable from U by a nontrivial symplectic transvection, exactly once. Its cardinality is 2(2ⁿ−1). Each such neighbor is represented by exactly 2^(n−1) of all the nonfixed ambient axes.

**Proof.** For a outside U, the nonzero functional ℓ_a(x)=ω(x,a) on U has kernel I of dimension n−1. The intersection U∩T_a U is exactly I. Indeed the vectors in I are fixed, while an x outside I is sent to x+a, outside U. The changed Lagrangian is I plus the span of x₀+a, for any x₀ in U with ℓ_a(x₀)=1.

If i is in I, replacing a by a+i gives the same changed Lagrangian. Conversely, if a and a′ give the same neighbor, their intersection kernels in U coincide. Over F₂ the associated nonzero functionals are therefore equal, so a+a′ lies in U. The displayed one-dimensional extension of I is the same precisely when a+a′ lies in I. Thus each neighbor consists of one axis coset a+I, with 2^(n−1) representatives.

The linear map a↦ℓ_a from the ambient space to U* is onto and has kernel U, so dual vectors v_j exist. For each b, all axes with that functional are the affine coset a₀(b)+U. This coset has exactly two cosets modulo I. Since b_j=1, u_j lies outside I, so a₀(b) and a₁(b) represent those two classes. All b and both classes are distinct, which proves completeness, uniqueness, and the multiplicity count.

## Exact implementation

neighbors.hpp solves the nine linear pairing equations by binary row elimination. Its augmented rows use a 64-bit integer, and its supported n is at most 15. The low 2n bits are coefficients and the following n bits carry the right-hand-side identity. Setting free variables to zero produces the required dual vectors. The loop over b builds a₀(b) from a₀(b without its least set bit), so each candidate pair needs one XOR beyond the fixed dual solve.

The accelerated dynamic_neighbors.cpp is a separate derived copy of the reviewed source; the original running source is unchanged. It retains the actual chosen axes in its move ledger, recomputes all incident ranks after each accepted move, and rebuilds the full paid/helper histogram at the end. It rejects productive helper ranks below two. Equal objective candidates use reservoir sampling among ties.

Its interface is

    dynamic_neighbors INPUT OUTPUT SEED PASSES [TEMPERATURE]

Temperature defaults to zero. An explicit positive temperature allows a minimum local candidate with positive objective change to be accepted with probability exp(−delta/T). The temperature decreases by pass, and the final pass has temperature zero. At zero temperature, positive moves are rejected and neutral moves retain the original one-third acceptance policy. A positive-temperature run is exploration, not a certificate; the final exact profile and rigorous moment checks are still required.

Different axes in one class can differ as full symplectic matrices and in their Clifford phase lifts, although they induce the same changed Lagrangian. The search only needs one representative for each chart. The later actual-word compiler must use the representative actually saved in the move ledger and retain its absolute phase; it cannot silently replace that axis by another representative after proof artifacts have been frozen.

## Independent exact validation

neighbor_check.cpp checks all Lagrangians through n=4: respectively 3, 15, 135 and 2,295, totaling 2,448. It compares the complete transformed-space set from every nonzero axis with the set from the representative generator, and checks that every changed Lagrangian has exactly 2^(n−1) original axes. This covers 593,964 axis cases.

On 32 deterministic frames from the current nine-dimensional graph it additionally checks every representative's pairing functional, then compares transformed Lagrangians for 130,824 nonfixed sampled ambient axes with their computed representatives. The replay returns

    PASS_COMPLETE_TRANSVECTION_NEIGHBORS small_lagrangians=2448 small_axis_cases=593964 actual_n9_axes=130824

Reproduction from the repository root (the complete inputs are included):

    c++ -std=c++20 -O3 research/native-clifford-gauge-compiler/decoder/neighbor_check.cpp -o neighbor_check
    ./neighbor_check research/native-clifford-gauge-compiler/decoder/ALL-SMALL-LAGRANGIANS.txt research/native-clifford-gauge-compiler/inputs/round3-contact-graph.txt

The proof is all-dimensional; these finite checks verify the implementation rather than extrapolating a theorem from samples. This exact geometric acceleration does not establish an admitted supplier, full Clifford lowering, a new frontier bound, or optimality of any bounded search.
