# A direct native compiler for bounded exact scalar traces

Status: proved informally below, with finite regression checks in check_lanes.py. This is not a new multiplication κ and is not a freshly kernel-checked Lean theorem. The mechanism is a concrete adaptation of classical guard-bit / Kronecker packing to the independent dirty-column interface. No priority claim is made for packing itself.

## Sufficient theorem

Let a fixed straight-line scalar program have T gates, r input registers, and o requested output registers. Its permitted gates are copy, negation, addition, subtraction, multiplication by a fixed integer c with |c| ≤ C, and exact division by a positive fixed integer d in a finite set Δ. Here C ≥ 1. All f executions have the same control and register addresses. Suppose their inputs, every gate result, and every live scalar are integers in [−H,H]. Each division gate is certified to have d dividing its argument in every column. There is no relation among columns or among the dirty helper inputs beyond these bounds and exact-divisibility promises.

Choose B ≥ max(H,1) divisible by every d in Δ; for example B = D ceil(max(H,1)/D), where D is their least common multiple (D = 1 for no divisions). Choose s with R = 2^s > 2(C+2)B. Let k ≥ 1 satisfy ks ≤ w. Suppose all memory addresses used for packed registers and counters are below 2^w; their total number is the original register count times ceil(f/k), plus fixed scratch space. Then a single uniform native Word RAM program evaluates all f columns exactly in

    O((r+o)f + T ceil(f/k) + s + f)

word instructions, with the constant depending only on the fixed scalar gate set and address layout. With packed input and output already in this ABI, the conversion terms become O((r+o) ceil(f/k)). The program uses multiplication/division only on w-bit words and never simulates a Turing machine. The ordinary unpacked conversion cost is retained in the first bound.

## Encoding and identities

For a group of k columns, write Rep = Σ(j=0..k−1) R^j and E(v) = Σ(j=0..k−1) (v_j+B) R^j. A short final group is padded with zero-valued columns. Since 0 ≤ v_j+B ≤ 2B < R, these are canonical base-R digits and are uniquely decodable. All preconditions apply to padded executions too; linear homogeneous gates keep those added columns zero.

The exact native implementations are:

- addition: E(x+y) = E(x)+E(y)−B Rep;
- subtraction: E(x−y) = E(x)+B Rep−E(y), with the addition performed first;
- negation: E(−x) = 2B Rep−E(x);
- positive c multiplication: E(cx) = c E(x)−(c−1)B Rep;
- c = 0: return B Rep;
- negative c: negate, then use |c| multiplication;
- exact division by d: E(x/d) = E(x)/d + ((d−1)B/d) Rep;
- copy: copy the packed word.

For division, d divides both x_j and B; therefore every encoded digit x_j+B is divisible by d. Consequently E(x)/d = Σ ((x_j+B)/d) R^j as an exact integer identity. No assumption d divides R is needed. This addresses odd exact divisors as well as powers of 2. The displayed correction (d−1)B/d means the integer (d−1)(B/d), and is computed in that order. Division d = 1 is the identity. If d exceeds B, divisibility and B > 0 imply B ≥ d, so this case cannot arise under the chosen B.

## Proof of machine safety and correctness

Each digit of the addition temporary is at most 4B; each subtraction temporary is at most 3B; each positive-multiplication temporary is at most 2CB; each negation temporary is at most 2B. All are strictly below R by its choice. Each final digit lies in [0,2B] because the scalar gate result has magnitude at most H ≤ B. The division intermediate has nonnegative digits at most 2B/d, and its final corrected digits are at most 2B. Thus no intermediate carry reaches another lane. Every packed intermediate is below R^k ≤ 2^w, so native modular arithmetic is identical to ordinary natural arithmetic. Every subtraction is nonnegative: its difference is the encoding of a scalar result known to lie in [−B,B]; hence natural-number monus is also ordinary subtraction. Constants B Rep, 2B Rep and (c−1)B Rep fit for the same reason. For negative c, the negated intermediate remains within [−H,H].

Induction over gates now proves that every packed register is the encoding of the exact k independent scalar registers. This proves the theorem for all f and all admissible dirty inputs, not only for sampled data. Register overwriting is safe by reading the original operands into scratch words before writing the destination; the proof does not assume distinct gate destination and input addresses. The address-fit hypothesis excludes address wraparound, independently of value fit.

To construct the encoding from unpacked input, scan each group once, multiplying the accumulated word by R and adding the next biased digit in reverse lane order. The intermediate prefixes remain below R^k. Build Rep in the same way, using O(k) steps once; all recurrent affine correction constants then require O(1) operations because the gate set is fixed. Decode by repeated division/remainder by R and subtraction of the known bias using a signed two-word or sign/magnitude output convention; output costs O(of). B can be derived by integer division/multiplication from the supplied bound H and fixed D. For k >= 2, s < w, so construct R by s doublings. For k = 1 and s = w, R itself does not fit; bypass multiplication/remainder by R, since a one-lane word needs neither operation. Its repunit is 1 and its sole decoded digit is the word itself. These charges give the asserted bound. All scalar bound and count parameters stored in machine cells must fit; this includes f if a one-word outer-loop counter is used. The fixed constants C and D fit whenever the stated R and B hypotheses are satisfiable. For an asymptotic family, finitely many smaller widths may use a separately specified finite base case. A uniform implementation receives f, s and the bound H, rather than baking an input-dependent packed word into its program.

## Link to the native exponent, stated without a new value

Use the native normalization W(n) = O(n/(log n)^kappa0), with n and the input/output ABI exactly as in the native predecessor theorem. Suppose a complete algorithm in that same model has actually batchable scalar work S(n) = O(n/(log n)^kappa0), lane width s(n) = O((log n)^(1-delta)), word width w(n) = Theta(log n), and enough independent columns to fill Omega((log n)^delta) lanes. Suppose, additionally, all conversion, control and unbatched work totals O(n/(log n)^(kappa0+delta)). Then the concrete construction above gives native cost O(n/(log n)^(kappa0+delta)). Proof: k = Omega((log n)^delta), so S(n)/k has the target bound; add the explicitly charged remaining work. This is a sufficient native algorithmic implication. It does not establish those premises for the current supplier/controller. In particular s(n) = Theta(log n) gives only constant lane count, and an unpacked O(n) boundary would dominate the proposed native cost. A complete improvement must demonstrate growing usable packing and its boundary ABI within the already established native model; changing the unit of cost is not a contribution to this exponent.

## Reuse and attribution

The direct machine endpoint is the existing Problem 1.8 Lax13 compiler. Mathproof.Meta.Problem18RAMLax13ProofsSimulation20261001.compile_correct accepts a bounded IMP BigStepB run, explicit Layout.FitsWords and a representing machine state; it produces a native run with time ≤ Layout.const times the IMP cost. Its compileProgram_runsTo theorem handles literal input/output, clean initial memory and genuine halt. The theorem permits arbitrary initial represented environments in its local form. The scalar macro frame discipline in Problem18ClaudeFieldMacros20261001 gives the model for separating output slices, inputs and scratch. No RAM→TM module is needed in this route.

These statements were inspected as source only in this session; no current-source Lean replay or transitive axiom audit was run. PUBLIC-SOURCE-PINS.json fixes the inspected bytes. The source catalog search covered registered lexical hits for word RAM and packing; it did not exhaustively semantically inspect the entire DAG. The typed workspace query for compileProgram_runsTo returned no indexed hit. Existing compiled artifacts, if present elsewhere, do not upgrade this session's evidence.

Classical antecedents include Kronecker substitution and word-parallel arithmetic. Public formalization leads checked on 22 October 2026: Jan Dreier and Claude Fable 5's Lax word-RAM compiler (https://laxarchive.org/lax-13/index.html; superseded by https://github.com/lax-archive/lax-submissions/tree/9394e531cc51cb67a0214bca3f9264dfe97ba5c7/word-ram), the 3SUM/APSP native compiler (https://github.com/anthropics/formal-math/blob/main/3sum-apsp/docs/MACHINE.md), signed Kronecker correctness in https://github.com/leanprover/hex-poly-z/blob/main/SPEC/hex-poly-z.md, and https://github.com/teorth/sendov/blob/master/docs/design.md. The last two sources establish relevant precedents, not a fresh machine-cost theorem for this package; source paths behind their documented claims were not replayed here. No source copied from them is included.

## Open next questions

Apply the bound H to the actual retained supplier trace, including arbitrary dirty inputs and every recursive denominator grid. Determine whether an independently growing column multiplicity survives whole-job boundary conversions. Port the exact native finite trace to the bounded IMP semantics, then invoke the existing compiler and independently audit the resulting native theorem. These are applications of the proved sufficient construction above; no missing result is assumed to claim a higher κ.
