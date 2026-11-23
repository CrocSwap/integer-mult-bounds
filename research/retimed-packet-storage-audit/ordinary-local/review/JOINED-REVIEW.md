# Scoped review of the exact joined storage coefficient

**Accepted** for the native-entry and reservation-history domains stated in
`JOINED-STORAGE.md`, retaining the binary bank-capacity/mass, complete-field,
ownership, header/control and fixed-stage lowering premises.

Reviewed source remains #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`.

| Reviewed joined artifact | SHA256 |
|---|---|
| `JOINED-STORAGE.md` | `d7c339e01d678aaa24c143cadf98946f8c9afd9a3940fb73c696198e0511a858` |
| `check_joined.py` | `ee21ec3147bd914eb15221826712e499e735834efb25add3dda7d9d05752cbbf` |

## Applicability and individual-role join

The named-head coefficient and complete local table concern the same
installed `ordinary_carrier -> binary_receiver` source and role assignment.
The common twenty-two resolved source files agree byte for byte; the
additional `compact_crt.py` supplies the six public cold-only roles.
The final joined checker authenticates all twenty-three files. The earlier
version checked only the common subset; that limited standalone coverage
has been corrected without changing the mathematics.

For fixed stage index j, B_j is fixed by the installed rank. The named-page
coefficients were proved individually before applying B_j/(B_j-1), and the
local table supplies individual a_r values before summing A(B_j). Root,
public rectangle and cold coefficients are also individual-role bounds.
Therefore adding G(B_j,2), 8 and A(B_j) preserves a uniform coordinatewise
bound over changing shapes and different maximizing calls. The join does
not use a maximum per-call total in place of summed role maxima.

No true child argument is multiplied by the scratch coefficient. The
ordinary predecessor is strictly earlier, each stage root pads by less
than two, and the resulting per-stage argument caps are the separate
factors 2^(m-j+1)T. The binary owner-capacity premise capacity<=2B remains
the input needed for the compiler backing portion of G; the Gaussian
census is not substituted for it.

## Exact arithmetic and slack

The decomposition is correct:

\[
 G(B,2)+8+A(B)\le31+r(B),\quad
 r(B)=\frac{123}{8(B-1)}+\frac{54}{B}
     =\frac{555B-432}{8B(B-1)}.
\]

Both positive summands decrease for B>1. The source's B=N^92 and minimum
installed rank log 5610 imply the much weaker B>=32768. Independent
integer cross-multiplication gives

\[
 254r(32768)=\frac{144349851}{268427264},\qquad
 1-254r(32768)=\frac{124077413}{268427264}>0.
\]

The correction is not automatically below one at a smaller convenient
threshold: B=16384 fails this particular gate, a useful rejection control.
The integral part is

\[
 2+31\cdot254+3\cdot128=8260.
\]

Consequently all m<=7 native-stage cases are strictly below 8261T, and
T<9X gives 74349X. This check uses small exact integers rather than
production-sized ranks or fields. Its uniform positive slack also permits
the displayed strict bound after taking suprema over histories.

## Warm and mixed histories

The six binary-cold positions have individual coefficients
(1,1,1/4,1/4,1/4,1/4), totaling 3. A fresh native call does not use them,
but a reservation history may contain both branches and retain their
different historical peaks. Adding their coefficient gives 74352X_max.

The claim is valid for a fixed installation/role map, valid uniform
envelopes, and X_max bounding every public slab in the relevant nonempty
history. The source's valid slab volumes are positive. For an initial
historical vector K_init, the stated exact update and sufficient grant
retain every untouched or previously larger blank allocation:

\[
 K'_r=\max(K_{init,r},\sup_i h_{i,r}),\qquad
 H\le\sum_r\max(K_{init,r},c_rX_{max}).
\]

The strictly smaller coefficient sum yields the author's conservative
aggregate inequality with `sum K_init + 74352X_max`. Erasure is correctly
used for return safety, not historical deallocation. Changed installations,
additional role families and external caller backing require their own
charges, as the joined note states.

## Execution and limits

The final joined checker passed in the publication layout and authenticated
all 23 source files. `JOINED-RESULT.json` records that replay. A separate
integer cross-multiplication receipt is `JOINED-INDEPENDENT.json`. An
earlier attempted replay stopped solely because the two component folders
had not yet been copied into the publication layout; a temporary assembled
layout then passed, and the final publication-layout replay also passed.

The joined checker authenticates and evaluates the substitution; it is not
a proof assistant. Universal applicability comes from the written component
proofs and their distinct source reviews. These are conditional ordinary
data-file coefficients, not complete multiplier storage constants. The
selected kappa and all five canonical assumptions remain unchanged.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
This is scoped model-assisted review, not human or formal-kernel approval.
Apache-2.0.
