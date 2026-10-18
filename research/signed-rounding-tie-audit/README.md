# Moving an inverse sign inside half-up rounding breaks dirty cancellation

At unchanged precision4, the actual pinned PR628 `lift` with source1/16,
coefficient0 and final multiplier1/2 adds1/16 to its target. Its original
negative call subtracts the same rounded value and restores the target exactly.
A proposed rewrite that negates **before** the final rounding adds0 instead,
leaving **1/16**. Source restoration and all original admission checks still pass.

This is a source-level counterexample to a compiler rewrite, **not a defect in
the retained implementation**. Its `scaled(value,sign)` deliberately occurs
after rounding. The audit never edits frozen sources; it creates an in-memory
single-site mutant and checks that exact source location before mutation.

## Quantified sign criterion

Let `Q_w(t)=2^-w floor(2^w t+1/2)`. Direct floor arithmetic gives

`Q_w(t)+Q_w(-t) = 2^-w` if `2^w t` is a half-integer, and0 otherwise.

Therefore replacing `-Q_w(t)` by `Q_w(-t)` is safe on an entire domain exactly
when that domain contains no half-grid tie. Same precision, closeness to the
ideal operator and exact source restoration do not imply this property.

For the unrestricted affine rational progression
`t=c+q1*z1+...+qk*zk`, with integer parameters z, choose a common positive
denominator D such that `2^w(c,q1,...,qk)=(u0,u1,...,uk)/D` with integer u.
A tie is reachable if and only if

`D is even and gcd(D,u1,...,uk) divides D/2-u0`.

Proof: the tie equation is `u0+sum uj*zj = D*n + D/2`. For odd D it has no
integer solution. For even D, the integer combinations of D and all uj are
exactly their gcd times Z, giving both directions. This remains valid for
unreduced common denominators, negative coefficients, zero slopes and arbitrary
numbers of parameters. Apply it separately to each real component of a vector
or complex increment. The proof is independent of the finite test ranges.

For example, a zero-offset slope1/3 never hits a half-integer and is safe.
Slope1/2 does hit ties. An affine offset1/4 with slope1/2 avoids every tie,
while offset1/4 with slope1/4 reaches one. Thus denominator parity alone is
not sufficient for affine domains; the gcd/offset condition is necessary.

## Source-bound evidence

The pinned `dirty.py`, `weighted.py` and `scan.py` are loaded only after their
Git blobs and byte hashes are checked. The mutant moves the sign through the
last rounded multiplication in `lift`; all other operations and guards remain
unchanged. Across285 actual leaf trials,150 odd-numerator inputs leave exactly
one positive grid unit and135 off-tie inputs still cancel. All285 unchanged
same-grid inverse pairs restore arbitrary target dirt and their sources.

The theorem's arithmetic is independently checked on21,316 scalar domains and
21,316 two-parameter affine lattices by enumerating their complete residue
periods and directly testing the two signed roundings. This oracle does not
use the gcd criterion to decide equality. Four additional controls isolate
odd denominators, even denominators, a safe affine offset and a reachable tie.

```sh
python3 -I -O -B research/signed-rounding-tie-audit/verify.py
python3.12 scripts/research_package.py --package research/signed-rounding-tie-audit
```

Expected: `PASS_SIGNED_ROUNDING_TIES ... source_failures=150/285`.
Python's standard library suffices; optimization does not disable checks.

## Relation to other precision work

The earlier mixed-precision-inverse-boundary result changes the execution grid;
this audit keeps the grid fixed and changes where the inverse sign is applied.
The retained dirty-prefix proof requires equal deterministic increments in
opposite orientations and is consistent with this finding. No entire PR628
internal increment is asserted to be an affine function merely because its
ideal operator is linear. The affine tie theorem applies only after that
representation and its reachable domain have been established.

## Open next questions

Can a compiler prove tie-freedom at the actual final multiplication of a useful
leaf? First derive its exact reachable affine constraints and apply the gcd
criterion. Internally rounded intermediate values may require a richer domain
analysis. Keep subtract-after-round as the exact fallback and price any extra
analysis or execution needed. No supplier, native compiler, selected cold replay
or new kappa is claimed here.

## Credit

Chafik Boukhalfa's PR628 supplies the signed rounded leaf; Gareth Davidson's
dirty-prefix-precision supplies the retained deterministic-increment restoration
argument. Prepared for woklerx with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review is claimed.
