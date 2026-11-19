# A clean physical canonical-coefficient readout at width 13

Given an explicit list of repeated computational matrix units with Gaussian-unit weights and a runtime four-qubit Clifford/Pauli target, this circuit returns the real and imaginary parts of the full width-13 Moore–Penrose coefficient, rounded once to any prescribed binary precision. The routine computes the target matrix entry and phase, chooses its shell, accumulates the signed complex numerator and performs the terminal division. It preserves the inputs, clears the workspace and returns the head home. Every Clifford class is covered by the supplied absolute-factor interface. [Equations, gate construction and costs](PROOF.md) · [Optional normal-form compiler](BRUHAT.md)

The least common component denominator for this observation family is **$H=7852360022325\cdot2^{19}$**. A single four-Hadamard coefficient attains that denominator in lowest terms. The proof also determines, at each target, the entire attainable Gaussian lattice and the fewest unit-weight records needed to realize each of its elements. The prior general inverse kernel has a different denominator. The observation interface here is a list of repeated matrix units and the numerical target is one named coefficient. [Arithmetic certificate](check_arithmetic.py) · [Upstream canonical weights](https://github.com/apoursh/integer-mult-bounds/blob/eead545a4ba6c50010fcac0919a9fdc6b14bd673/research/clifford-compact-adjoint-fibres/CANONICAL.md)

A three-record example cancels in the real component. At 48 fractional bits the complex grid output is $(0,-1701)$; rounding individual terms first gives $(0,-1702)$. The end-to-end reversible calculation takes **458 ten-track sites** and **1,353,992 adjacent head moves**, including register cleanup and return to the input end. Its primitive gate invoice is 97,574 NOTs, 849,046 CNOTs and 171,478 Toffolis. These costs are uniform over all target and record fields at the stated list length and precision. [Published input](example.json) · [Literal elementary replay](check_local.py)

## Input and replay

From the repository root use Python 3.12 and the standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/clifford-reversible-coefficient-readout
~~~

From the package directory run the following example. The CLI returns the signed integers in units of $2^{-\mathrm{precision}}$, the workspace size and the gate/motion invoice. Omitting the literal option executes equivalent reversible gates with the clean propagation routes metered by their lengths.

~~~sh
python3.12 -B readout.py example.json --literal
~~~

Each request provides left and right monomials. Their four binary row masks, translation nibble, four coefficients modulo four, and six cross-term bits define affine basis maps with quadratic phases. The cross bits follow ordered pairs $(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)$. The four-bit mask chooses partial Gaussian Hadamards, the two-bit phase chooses a central Gaussian unit, and the two nibbles $x,z$ specify $X^xZ^z$. Each list item is $[r,c,t]$ for weight $i^t$ on a computational matrix unit repeated over 13 sites. The precision is a nonnegative integer. Register allocation assumes the labels have been supplied at the documented fixed-width input positions. Building the external observation or translating another target representation can have additional costs. [Machine-readable example](example.json) · [Input encoding and wire layout](readout.py)

Four reproducible checks cover the rational scales and component lattice, exact complex sums against dense Gaussian matrices for all partial-Hadamard masks, actual elementary tape execution including modulus setup and output cleanup, and the constructive Bruhat compiler. Each checker also runs with optimized Python. [Dense oracle](check_values.py) · [Factorization check](check_bruhat.py) · [Registered commands](VERIFY.json)

## Open next questions

1. Can a moving-head compiler accept a symplectic matrix and its signed lift generators on tape, carry out the Bruhat reduction reversibly, and retain an interface of comparable cost for many queries?
2. For many named outputs, can the packet of returned coefficients share arithmetic and movement while preserving a clean output layout? Give a complete cost for an entire 256-label fibre and include placement of the outputs.

## Attribution

The five canonical weights and the repeated-site theorem are from apoursh's #7821, using the width-13 conditioning calculation by Ali Romman, with the Clifford and character work of alephnan and Nick Petalas. The local quotient and nearest-even gates are taken from apoursh's #7820. This extension derives the smaller exact denominator and record metric, supplies normal-form coverage and connects runtime target and observation labels to a clean local numerical readout. Prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. The selected conditional multiplication exponent remains 0.00363005817. [Retained source hashes](SOURCE-PINS.json) · [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19757301)
