# Exact scalar argument and its boundary

## Transposition recognition

The source uses two chronological four-macro representations. For distinct
registers a,b, the forward representation is
`a += b; b -= a; a += b; b = -b`. It maps `(a,b)` to `(b,a)`.
The inverse-transpose representation is
`a -= b; b += a; a -= b; a = -a`, and gives the same transposition.
All four macros must share the same frame and use native L coordinates.
The compiler recognizes these literal forms. The separate checker multiplies
actual two-coordinate integer matrices; it does not use the literal recognizer.

## Location invariant

A run ends at every non-scalar event or frame change. Let `loc(r)` be the
physical slot currently containing the original logical register r. Initially
loc is the identity. Maintain `physical[loc(r)] = logical[r]` for every
persistent/center coordinate. Omitting an exact SWAP(a,b) and exchanging
loc(a),loc(b) preserves that equality. Any other scalar macro reads and writes
only the remapped slots; therefore it makes exactly the original logical
update. Both COPY operands must be remapped. All untouched registers retain
identity locations. Coefficient work W is outside the native permutation.

The invariant is a statement about exact scalar values in the common frame.
It is not an assertion that all physical primitive-array and phase contracts
have been admitted. No replacement spans a frame/event boundary. Scalar
common-frame membership follows because every moved slot appears in a swap
at that frame; production address/chart transport is a separate obligation.

## Paid materialization and arbitrary dirt

At the end the required assignment is `slot[r] = old_slot[loc(r)]`. For each
nontrivial cycle `(r0,r1,...,r[l-1])`, pay

1. COPY W <- r0;
2. COPY r[j] <- r[j+1] for j=0,...,l-2;
3. COPY r[l-1] <- W.

Each cycle costs l+1 COPY primitives. Overwrite W at the beginning of the next
cycle; no incoming clean value is needed. Pay one final CLEAR(W), even if all
swaps cancel and there is no nontrivial cycle. The original swap's additions
clear W, so surviving arbitrary initial work would violate the boundary.
Consequently d moved slots in c cycles cost d+c+1 primitives. The compiler does
not restore incoming coefficient dirt; the pinned original macro interface
erases it too. Native helper dirt is restored by the complete scalar endpoint.

With s omitted swaps, PR696 charges 7s primitives (three ADD/CLEAR pairs and
one NEG). The clean-work comparator charges 4s (three ADDs and one NEG), when
W is already known zero. Other remapped macros retain their cost. Actual runs
have either s=1,d=2,c=1 (tie with clean-work arithmetic), or s=7,d=5,c=2
(28 versus8). Per component, fourteen larger runs save14*20=280 against that
comparator. Both real components give560. These are exact finite paid counts,
not a whole-circuit optimum or a runtime measurement.

Clear elision is applied identically to both complete words. Initially W is
unknown. A retained CLEAR establishes W=0; a write invalidates that fact.
Only a further CLEAR known to write zero into an already-zero W is dropped.
Induction proves that each deleted event is the identity on the admitted
incoming states. No source read, copy, coefficient operation or restoration
is removed by this rule. PR839's known-zero principle retains credit.

## Prefixes and linear extension

Inside a transformed run, a native logical value sits in a different physical
register but equals its original value. The remapped coefficient preparation
computes the same scalar work values as the original at its corresponding
non-swap macro. During materialization only boundary values are copied. Every
replacement row therefore occurs among original prefix/register rows; an
independent dense-rational checker enforces this for every changed block.
For arbitrary correlated incoming data, evaluation of the same row gives the
same scalar value. Taking a maximum over registers and prefixes establishes
containment of that magnitude envelope. Register-by-register containment is
not claimed. Rows copied into W may originate in other native registers.

All operations are linear over the rationals and have real coefficients.
Equality on every independent scalar input column therefore extends to
arbitrary real/complex inputs, separately on real and imaginary components.
The finite full words include every native helper and all private input dirt.
Exact dyadic denominators and row-L1 peaks are recomputed for all four versions.
No denominator or row-growth inference replaces those complete replays.

This argument establishes the declared scalar substitution and its finite
implementation evidence. It does not prove approximate-arithmetic rounding,
address/phase realization, whole-call hosting, complete compiler precision,
physical tape cost, the outer multiplication theorem or a new exponent.
