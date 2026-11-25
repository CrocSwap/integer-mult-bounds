# Construction specialization for κ = 4999/10000

This note specifies how OpenAI's November 24 construction supplies the selected
bound, including explicit outer parameters and the remaining finite searches.
It supplements the [theorem-to-contract proof](PROOF.md). The algorithm and its
existence proof are OpenAI's; this contribution is a specialization and dependency
account. A theorem application is a mathematical κ claim when its hypotheses and
machine contract match. It need not introduce a new multiplication algorithm.

All upstream references below are pinned to
`92b516ef8e2abf66c3db7aa31438d3010bc7956f`. The finite interchange and Walsh
templates have **not** been generated here, no complete tape transition table has
been materialized, and no multiplier has been executed. The explicit parameters
below do not turn the source-binding verifier into a full construction replay.

## 1. Explicit exponents and an interchange parameter

The required logarithmic exponent is

\[
1-\kappa=\frac{5001}{10000}=0.5001.
\]

The candidate family in [uniformity.tex, “Constructing the candidate programs”][uniform]
uses \(\theta_j=1/2+1/(j+2)\). An admissible specialization is:

| Parameter | Exact choice | Role |
|---|---:|---|
| \(j\) | \(19998\) | Candidate index in the manuscript's family |
| \(\theta_j\) | \(10001/20000\) | Candidate multiplication exponent |
| \(\epsilon=\theta_j-1/2\) | \(1/20000\) | Input to `thm:integer` |
| \(\rho=\alpha\) | \(20001/40000\) | Walsh and interchange time exponent |
| \(\gamma\) | \(40001/80000\) | Intermediate interchange call-count exponent |
| \(p\) | \(240007\) | Prime characteristic for the interchange label construction |

These are compatible choices for the paper's effective construction, not
constants extracted from an upstream executable or Lean witness. In particular,
we have not established that any particular upstream generator picked this
\(p\). The local checks certify admissibility of the displayed choices.

These choices satisfy

\[
\frac12<\gamma<\rho<\theta_j<1-\kappa<1.
\]

The first two strict gaps are \(1/80000\); the next gaps are \(1/40000\)
and \(1/20000\). The conditions in [integers.tex, `thm:integer`][integers]
are therefore met. For the interchange construction, trial division through
\(\lfloor\sqrt p\rfloor=489\) confirms that \(p\) is prime, and

\[
\gamma-\frac12-\frac{3p-1}{p^2}
=\frac{1760049}{4608268803920000}>0.
\]

This checks the prime/exponent condition preceding
[`eq:interchange-contraction`][interchange]. It does **not** check the remaining
template conditions. This \(p\) belongs to the interchange construction; it is
not asserted to be a common parameter for every Fourier or Walsh template.

## 2. Finite templates still to generate

For interchange, the source next chooses sufficiently large fixed \(m\), with
\(q\) the least power of two at least \(m^{1/p^2}\). Its label matrices determine
a rational address-space dimension \(D\), reserve width \(a=D-2\), and batch
parameters. The completed main-swap program must have at most \(Wm^\gamma\)
child calls and satisfy

\[
2m^\gamma+2a<m^\rho.
\]

After fixing the matrices and factorizations, it chooses a compatible radix
prime larger than \(W\), avoiding their forbidden denominators and required
unit numerators. These choices yield the recursive interchange theorem
`thm:interchange`, including arbitrary prefix, gap and suffix ranges and linear
visited space. [Interchange construction and recursion][interchange]

Separately, [walsh.tex, `lem:tape-walsh`][walsh] uses a finite normalized binary
template with arity \(A\), batch size \(W\), and child-call count \(\sigma\)
satisfying \(\sigma/W<A^\rho\). Its \(W\) is local to that template. The source
imports the repair and binary-template results from the [Fourier companion][fourier],
including `thm:repair` and `prop:binary-template`.

The effective-generation argument in [uniformity.tex][uniform] enumerates finite
parameters, constructs bases and tables, and accepts actual call counts with
strict recurrence slack. The upstream existence proofs guarantee termination.
This review has not performed those searches: \(m\), the completed matrices,
both batches, the radix, and the Walsh instruction list remain unspecified
numerically. No running-time constant, space constant, or crossover length has
been calculated.

## 3. The resulting fixed candidate

Once those finite templates are fixed, the manuscript specifies the following
algorithm on two unsigned MSB-first \(n\)-bit operands.

1. **Choose the digit and address widths.** For \(n\ge2\), set
   \(b=\lceil\log_2n\rceil\), \(h=\lceil n/b\rceil\),
   \(k=\lceil\log_2(4h)\rceil\), and \(N=2^k\). The operands become
   length-\(h\) radix-\(2^b\) coefficient lists. Here \(b\) is a digit width,
   distinct from the interchange radix. For large lengths, \(Nk=\Theta(n)\).
2. **Build the cyclic box.** Choose pairwise-coprime short axes \(a_i\), padded
   to widths \(l_i\), with \(\sum l_i=k\) and \(S=\prod a_i\ge2h\).
   The manuscript gives a prime search and a possible final power-of-two axis.
   Check volume, coprimality, row-padding and borrowed-coordinate conditions.
   Use schoolbook multiplication for degenerate lengths or failed shape tests.
   The source proves that only a bounded initial range needs this fallback.
   [“Packing the digits,” `eq:integer-box`; candidate shape tests][integers]
3. **Move from digit order to CRT order.** With \(P_i=\prod_{j<i}a_j\) and
   \(\mu_i=P_i^{-1}\bmod a_i\), map rank \(t\) to
   \(y_i=\mu_i t\bmod a_i\). This is a group isomorphism preserving cyclic
   convolution. The balanced triangular schedule and
   [`lem:controlled-blocks`][permutations] charge for control-table preparation,
   forward movement and inverse movement. [Integers, `eq:integer-crt`][integers]
4. **Compute the convolution.** Apply the synchronized short Fourier transform
   \(\mathcal U\) to each input, multiply corresponding entries, apply
   \(\mathcal U^*\), and scale by \(\sqrt S\). `lem:synchronized-short`
   decomposes the transforms into \(O(\log k)\) layers of permutations,
   phases and selected-bit normalized Walsh transforms. Borrowed coordinates
   are restored by the ideal transform; padding does not multiply the volume
   once per axis. `lem:tape-walsh` supplies the tape cost and error control for
   the numerical layers. [Synchronized transforms][integers] · [Walsh layers][walsh]
5. **Recover exact coefficients and write the product.** Use certified numerical
   widths and phase tables so that total coefficient error is strictly less
   than \(1/2\). Undo CRT, round the real coefficients, propagate carries,
   reverse digit order, and trim or pad to exactly \(2n\) output bits.
   Because \(S\ge2h>2h-2\), cyclic convolution has no coefficient wraparound.
   [“Rounding the convolution to the exact product”][integers]

The precision requirement is constructive in the source: [uniformity.tex][uniform]
computes instruction-count and gain bounds, obtains a majorant
\(H_j(k)=2^{O_j(k+1)}\), and chooses fractional precision \(P\) with
\(2^P>8H_j(k)+2k\), together with sufficient integer bits and exact fixed
dyadic coefficients. It proves \(O_j(k)\)-bit records suffice. This note has
not computed \(H_j\) or a numerical precision multiplier.

## 4. Why the paid costs fit the target

The full fixed-candidate budget in [`eq:integer-budget`][integers] is

\[
O_\rho\!\left(Nk(1+k)^\rho(1+\log(2+k))^{O(1)}\right).
\]

With \(Nk=\Theta(n)\), \(k=\Theta(\log n)\), and the positive gap
\(\theta_j-\rho=1/40000\), every fixed power of \(\log k\) is eventually
absorbed into \(k^{1/40000}\). Thus this candidate takes
\(O_j(n(1+\log n)^{10001/20000})\) time, which is stronger than the selected
\(O(n(\lg n)^{5001/10000})\) target. Finite small lengths are absorbed into
the constant. This is an asymptotic deduction, not a computed threshold.

The source's space argument separately bounds complete numerical streams,
recursive parked streams, and descriptors. Work areas are reused; parked
volumes decrease geometrically on the relevant descents. It obtains
\(O_j(n)\) **visited** cells, not merely a bound on simultaneously live values.
[Interchange recursion][interchange] · [Walsh space proof][walsh] ·
[Final multiplication accounting][integers]

## 5. Fixed candidate versus the selected uniform machine

The candidate above alone is sufficient for this numeric κ: after its finite
parameters are chosen, its program, alphabet and tape count are fixed before
\(n\). The selected claim additionally uses one machine for **every** fixed
\(0<\kappa<1/2\). [Uniformity, `sec:single-machine`][uniform]

The manuscript serializes candidates onto a common fixed number of tapes and
enumerates attempts indexed by a candidate \(j\) and a power-of-two operand
chunk count \(r\). If a candidate has physical space constant \(c_j\), some
fixed \(r>2c_j\) eventually fits inside the common linear-space fences.
An attempt computes the \(r^2\) chunk products and assembles them. Correctness
comes from the candidate construction; it is not inferred from an unchecked
output test. Timeouts and space violations abandon the attempt.

The scheduler's attempt index \(i\) is **not** the candidate index \(j\).
In round \(s\), attempt \(i\le s\) receives \(2^{s-i}\) steps. A fixed
successful attempt of duration \(t\) finishes within total time
\(O(2^i(t+1))\), apart from the initial linear scan. A schoolbook attempt
ensures termination. For \(j=19998\), the appropriate chunk count and attempt
index exist, but have not been computed here. For any fixed κ below \(1/2\),
some \(j\) gives \(\theta_j<1-\kappa\); the **same scheduler** covers it.
No κ-dependent program choice is required for the selected uniform claim.

## 6. Formal source chain and open next questions

The actual Lean [proof entry][lean-main] obtains the native interchange family,
supplies CRT, permutation and Walsh procedures to `uniform_of_procedures`, and
applies `uniformMultiplicationSpec_iff_worstCase`. The resulting
`UniformWorstCaseSpec` matches the separate [comparator specification][comparator]
at source level. The manuscript parameters above are not claimed to have been
extracted from a compiled Lean machine.

- **Formal corollary and comparator replay.** Build the actual pinned solution
  and comparator, record accepted declarations and actual axioms, then compile
  the fixed-κ corollary with the repository's logarithm convention. The first
  step is the upstream [comparator workflow][comparator-readme]. The missing
  build environment and full dependency replay remain blockers here.
- **Materialized construction.** Implement the documented finite searches and
  export their accepted templates, exact call counts and precision data before
  attempting a full tape implementation. The unresolved work is the finite
  construction and its faithful compilation, not another decimal κ check.

Prepared with substantial OpenAI Codex assistance. This specialization retains
OpenAI's construction and attribution and is licensed under Apache-2.0.

[integers]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/integers.tex
[uniform]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/uniformity.tex
[interchange]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/interchange.tex
[walsh]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/walsh.tex
[permutations]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/permutations.tex
[fourier]: https://github.com/openai/math/tree/92b516ef8e2abf66c3db7aa31438d3010bc7956f/preprints/The-logarithmic-exponent-of-finite-Fourier-transforms-November-24-2026/build
[lean-main]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/lean/OAI/Computability/NearSquareRoot/Main.lean
[comparator]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/lean/ComparatorChallenges/NearSquareRootMultiplication.lean
[comparator-readme]: https://github.com/openai/math/blob/92b516ef8e2abf66c3db7aa31438d3010bc7956f/lean/ComparatorChallenges/README.md
