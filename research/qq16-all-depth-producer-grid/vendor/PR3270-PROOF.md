# One-layer full-cover exactness of F0 followed by B1

## Statement and inherited semantics

Fix exactly one tensor layer, with `N=2^73` complex payload coordinates
per cover owner. Use the literal `F_0` then `B_1_2` event streams from the
pinned joint-query certificate. For a positive binary quantum `h` and an
integer `P>=0`, suppose every real and imaginary input component in all
704 persistent fields, uniformly over every owner and payload coordinate,
belongs to `h Z` and has magnitude strictly below `2^P h`. The eight owned
private fields enter zero. Arbitrary correlations and dirty helper values
within this bound are allowed.

Under the inherited native/bridge semantics described below, working quantum

`q = h 2^-71`, with signed width `W=P+215`,

executes every primitive of this full-cover finite reference exactly. No
rounding, overflow or underflow is needed. Its arithmetic defect, relative
to that exact reference, is zero at every cut. The inherited exact QQ16
endpoint/restoration theorem is a separate premise; this package does not
reprove it or certify a physical implementation of the reference.

The primitive semantics are PR3226's pair-first Gaussian lowering, exact
signed monomials and dyadic scalar ADD/SCALE operations, applied through the
retained core/bridge. The nine-axis kernel acts with spectators in the full
73-axis layer. Source and target endpoint adapters and residual adapters are
the authenticated signed monomials. These are actual component operations,
not identity replacements for native children. Inherited bridge correctness
and endpoint semantics are not independently replayed here.

B1's cover maps remain

`out(d,z) = in(d*g, z XOR d*delta)`.

They act on the entire cover, including its owner index. Each authenticated
used owner matrix `g` has binary rank 73; every retained translation has
73-bit range and the literal action string is checked. Hence this action
is a bijection: recover `d` using `g^-1`, then undo the payload translation.
The source binding supplies the particular `delta` and inherited cover
closure. A uniform component bound and lattice across *all* owners survive
this bijection unchanged. It is not a permutation of one 512-entry array.
The source contains translations outside that array, so such a replacement
would not establish this theorem.

## Induction through native interiors and the stage boundary

Represent a field by `(M,g)`: each component has absolute value at most
`M 2^P h` and belongs to `h 2^-g Z`. Use the canonical zero for a proved-zero
field. Initially persistent fields have `(1,0)` and private fields zero.
For a nonzero dyadic constant `c=n/2^k` in lowest terms, scaling changes
the bound to `(|c|M, g+k-v2(n))`. Adding two fields uses the sum of their
magnitudes and the larger grid exponent. Signed permutations preserve both.
All of these are inclusion bounds, so dependence or cancellation does not
invalidate them.

An integer constant product is implemented by shifted copies and additions
before exact binary division. Every partial sum is bounded by `|n|M`,
and its grid is no finer than the input grid. The ledger explicitly visits
the partial-product bound, numerator and divided result.

For each paired complex input `a,b`, a native Gaussian line computes
`s=a+b`, `d=a-b`, then `((s+i*d)/2,(d+i*s)/2)`. If input component bounds
are `M`, the pair sums are bounded by `2M`, the real cross numerators by
`4M`, and outputs by `2M`. The output grid exponent increases by at most
one. The ledger visits all three bounds for every line of each recipe;
monomial factors preserve component magnitude and grid. The same reasoning
applies to all spectator assignments in one full 73-axis layer.

CLEAR writes zero only to owned private state. Scalar instructions, native
recipes, adapters and full-cover maps are processed in literal order.
Private sweeps are owner-local and clear C0 before reuse; the source's
full-cover sweep order is inherited. Uniform bounds are valid across this
order because every field/owner used by a cover move is included in the
same input supremum.

Crucially, the 712 field bounds at the end of F0 become B1's entry bounds
without resetting data, helpers, private fields, magnitudes or grids. The
separate integer-lattice implementation reconstructs the event expansion
and agrees on each completed-cut digest and the full primitive trace.
The reset-state control yields a different B1 result and a smaller guard.

## Exact finite certificate and signed width

`RESULT.json` records 53,118 literal events and 270,288 primitive-bound
observations. F0 alone reproduces PR3226's grid guard 35 and magnitude
bound `42822849617116776290`. Continuing through B1 gives maximum grid
exponent 71 and maximum component multiplier

`Mmax = 35714190970741142696015664337123072062513575 / 4 < 2^143`.

The grid maximum occurs at global event 50,998, in a constant result;
the magnitude maximum occurs at global event 52,876, in a scalar ADD.
The rational and integer-only recurrences agree on all stage/output hashes,
the primitive trace hash and the direct operation counts. The finite data
is an author-checked certificate supporting the induction above, not a
formal proof-kernel result.

Every visited value is an integer multiple of `q`, since its grid exponent
is at most 71. In units of `q`, its magnitude is strictly below
`2^(P+71+143) = 2^(W-1)`. Thus the signed `W`-bit interval contains every
component, native numerator and constant-product partial. Every division
has its required divisibility at the chosen quantum. No minimum-width or
sharpness claim is made.

## Symbolic per-owner density and remaining costs

Counts are normalized to a 512-coordinate *local kernel* in `RESULT.json`.
All bulk component counts scale by `N/512`; scalar control labels and recipe
counts do not. This normalization is arithmetic bookkeeping, not an
execution of the full B1 program at dimension 512.

The pair-first reference requires at most `483082 N + 12` W-bit word
operations per cover owner. This sum counts scalar and native additions,
exact shifts/halves, signed moves, constant-product copies and scratch
clears; it excludes diagnostic recipe/call/phase counters. All 528 full-cover
maps additionally require `2112 N` conceptual component transfers per owner
with an out-of-place buffer and copy-back. Their physical routing/address
cost is unknown. A transfer is not assigned a recursive tariff here.

Logical numeric storage is at most `1426 N + 12` W-bit words per owner:
`1424 N` for 712 complex fields, `2 N` for one owned reusable global-cover
buffer, and 12 scalar temporaries. Code, tables, addresses, routing resources
and control storage are additional. These are symbolic upper bounds for the
reference, not measurements or a favorable complete supplier invoice.

Zero primitive defect meets the numerical part of PR3235/2965's completed
producer tolerances on this input lattice. It does not bind an admitted
caller's entry grid/range, pay for its word arithmetic or access, give a
consumer, or establish exact physical restoration under an approximate
backend. No supplier, kappa or selected-frontier claim follows.

Exactly one tensor layer is essential to the stated constants. Tensor
powers repeat native Gaussian lines and change both the magnitude and
grid guards. No lambda>1 or all-depth extrapolation is claimed. The full
`N=2^73` payload was not allocated or executed; the proof is the uniform
component induction plus the source-bound finite envelope.
