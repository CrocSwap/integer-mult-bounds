# A fixed precision contract for composed coarse-grid inverse shears

Let every data array lie on the same grid u=2^-w, with w>=1. Each owned
source word has W>=w fractional bits, so its low W-w bits are zero between
calls. This is reserved clean capacity and is charged for every data array.
It is not arbitrary dirt. A source and target of a call must be distinct.

Use the preceding coarse-grid source-recovery construction to evaluate
T x in the source with error E<=u and restore the source exactly afterward.
While the source contains the working-precision approximation, round that
value to the coarse grid and add it, with the requested sign, to the target.
Call the computed coarse-grid function f(x). Then

    ||f(x)-T x|| <= E+u <= 2u.

The implemented external map is exactly (x,y) -> (x,y+sign*f(x)). Its
source is restored exactly, both arrays finish on the coarse grid, and
f does not inspect y. Using the opposite sign is its exact inverse,
including the same deterministic ties and roundoff. A sequence is inverted
by reversing the sequence and negating each sign. Factors within a kernel
and shears within a sequence need not commute. The word is generally a
nonlinear integer-grid bijection approximating a linear shear word; no
Clifford or common-label implementation is inferred from bijectivity.

For a finite menu of operators, let A bound every operator norm and C=1+A.
Suppose there are at most m stages in the entire planned execution and the
initial joint maximum norm is <=D. Each exact shear has norm <=C. Each
computed shear adds error <=2u<=1, so its joint norm M obeys

    M_next <= C M + 1,
    M_next+1 <= (C+1)(M+1).

Thus B=(C+1)^m(D+1) bounds every source in the word. Choose a single W
using that B, all operators' stable-factor budgets, E<=u, and the source
recovery test R<u/2. Every call then meets the source-recovery contract;
the low bits return to zero and the same W is reusable at every stage.
No extra precision is accumulated merely because one stage's target
becomes another stage's source.

Comparing the computed word with the ideal linear word, its joint error
after m stages is at most

    2u sum_(j=0)^(m-1) C^j <= 2m C^(m-1) u.

`plan` selects w so that this is <=2^-p, then selects W for B. Both data
and working precision still depend on the planned word's condition and
length; the claim is reuse of one fixed pair (w,W), not a precision bound
independent of the word. The magnitude bound includes arbitrary nonzero
initial contents of all data arrays. It does not grant arbitrary contents
in their reserved low bits.

Execution uses the earlier O(nL) scalar work per n-factor kernel and no
full-length borrowed array. It retains all coefficient, phase, magnitude,
layout and arithmetic-workspace charges. Neighboring cyclic layouts are
covered. Arbitrary-stride fixed-tape scheduling, source enlargement in an
enclosing compiler, and a full multiplication reduction remain unproved.
There is no new kappa.

The exact verifier uses 20 generic instances of six interacting shears on
three nonzero arrays, followed by the complete inverse word. Lengths are
1,2,3,8,17; two stability margins and both directions are covered. Twelve
instances compare with a separately implemented exact dense-matrix word.
All 20 cancel exactly. Four controls reject wrong inverse order, aliased
arrays and source or target values off the promised coarse grid.

This local extension was prepared by Chafik Boukhalfa with substantial
OpenAI Codex assistance. It reuses the local coarse-grid source-recovery
implementation, itself based on the PR628 cyclic scan. `SOURCE.json` pins
the mathematical predecessors and `MANIFEST.json` binds this implementation.
No external checkout is needed to run `run.py` as documented in the README.
No separate human or agent review is claimed.
