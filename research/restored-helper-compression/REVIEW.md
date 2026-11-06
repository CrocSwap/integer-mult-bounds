# Independent review of restored-helper compression

Reviewer: Worker C for @CubeJerry, with substantial OpenAI Codex assistance.
Apache-2.0. Review completed 2026-11-06, before the 04:35 UTC deadline.
This is a separate AI-assisted mathematical/code review with finite exact
checks. The review was not blind: the reviewer received the proposed theorem,
proof, constructor, and review targets. It is not independent human peer review or proof-kernel verification.

## Conclusion

**No blocking mathematical or constructor defect found in the stated scope.**
The full-endpoint quotient argument is valid, the descent to binary column
spaces is justified, and the exact bound is

\[
u+v\le k-t,\qquad
w=\operatorname{rank}_{\mathbb F_2}(V^TU)
\le\min(u,v)\le\left\lfloor\frac{k-t}{2}\right\rfloor.
\]

The constructor realizes the particular quotient needed by the proof. Its
output preserves the entire restored-helper endpoint, not only the data
block. The optimality claim is correctly restricted to fixed data components
and all scalar pairings. The result applies to the exactly restored helper
subcase of #4118; it does not settle that predecessor's more general arbitrary
diagonal helper endpoints or its remaining five-call existence question.

The reviewer did not edit the package. These are the reviewed proof and constructor bytes:

| File | Bytes | SHA256 |
|---|---:|---|
| `PROOF.md` | 8,281 | `4d9edf19ed4eec2708cbfcd186e9d6085af43cc0213e14fb2bd54efdeda2a20b` |
| `compress.py` | 2,685 | `47b702b79f454a3aa86adf13edac807e7f3fddc286f83d737f3c1c8ea745075c` |

Both paths are in this package.
Later edits require comparison with this reviewed version.

## 1. Fraction field, binary descent and the exact surplus

For the finite set of exponents used by the word, the generated torsion-free
abelian group is free abelian. Its binary group algebra is a Laurent polynomial
domain. Passing to its fraction field therefore preserves the nonzero
diagonal entries `a_j` of the ordered-path matrix `H`; `H` is invertible.
The fixed ordering supplies an upper triangular `H` with
`P-I=X H Y^T`. The entries use only the unchanged coefficients `a_j` and the
scalar contractions `y_i^T x_j`.

The endpoint makes the column and transposed row spaces of `P-I` exactly the
data-coordinate space `E`, of dimension `t`. Every `d_i-1` must be nonzero;
the target frames need not share a flag or commute as rational matrices.

The written rank-invariance descent to `F_2` is sound. An independent way to
see the same step is to take a binary row `z^T` with `z^T X=0`. Then
`z^T(P-I)=0`, so `z_i(d_i-1)=0` for every data coordinate. Because `z_i` is
binary and `d_i-1` is nonzero, all data coordinates of `z` vanish. Thus
`ker(X^T)` is contained in `E^perp` over `F_2`, and `E` is contained in the
binary image of `X`. Applying the transposed argument gives the same inclusion
for `Y`. No field-dependent scalar mixing has been silently introduced.

The helper projection of `im X` has image `im U` and kernel exactly `E`,
giving `rank X=t+u`; similarly `rank Y=t+v`. Sylvester's inequality over the
fraction field yields

`t = rank(X H Y^T) >= (t+u)+(t+v)-k`.

Therefore `u+v<=k-t`. Combining `w<=min(u,v)` with
`2 min(u,v)<=u+v` gives the stated floor, without an off-by-one issue. This
also implies `t<=k`. The proof handles zero helper width and zero paired rank.

## 2. Why the quotient preserves the whole endpoint

On `W=im U`, take the kernel `W_0=W intersect ker(V^T)` and a complement
with basis matrix `S`. Its dimension is exactly `w=rank(V^TU)`. A map `Q`
annihilating `W_0` and satisfying `QS=I_w` exists; extending it outside `W`
is harmless. For every original helper column,
`U-SQU` lies in `W_0`, so `V^T S Q U=V^T U`.

Consequently the new vectors preserve all scalar pairings, including the
self-pairings equal to one. Each new projector remains a nonzero binary
rank-one idempotent, with the same address frame. The ordered-path matrix
`H` is therefore unchanged.

For a compact independent full-endpoint check, set

`R=diag(I_t,Q)` and `T=diag(I_t,S)`.

Then `RT=I`, `X_hat=RX`, `Y_hat^T=Y^T T`, and

`P_hat-I = R(P-I)T`, hence `P_hat=RPT`.

For `P=diag(D,I_r)`, this is exactly `diag(D,I_w)`. This verifies all cross
blocks and the helper identity at once. It is an algebraic proof of a newly
specified word, not permission to discard live helpers while executing the
old word or to implement physical basis changes without a charge.

Preserving pairings alone for an arbitrary replacement realization would
not justify this conclusion. An explicit counterexample appears below. The
particular quotient, or an equivalent minimal factorization, is substantive.

## 3. Constructor and minimality

`factor_helpers` forms the Gram columns `G=V^T U`. The selected independent
columns of `G` correspond to independent original columns of `U`: any relation
among the latter would also be a relation among their images. The selected
columns therefore give a valid `S` complement. The returned left coordinates
define `Q` on `im U`, because every relation among columns of `U` is also a
relation among their Gram columns. The returned right coordinates are exactly
`S^T V`. Thus the implementation follows the proof's quotient, rather than
merely returning an unchecked pairing-preserving replacement.

I checked the bit-mask indexing and the incremental column-basis coordinate
algorithm. Pivots retain coordinates in the original selected basis; dependent
columns do not advance the basis index. Empty and all-zero Gram matrices give
width zero. `compress_calls` retains frames and both data components in call
order, and checks the binary self-pairings before construction.

Any realization with `h` helpers preserving the data components and all
pairings must factor the same `G` as `V_new^T U_new`, so `h>=rank G=w`.
The quotient attains this bound with the required endpoint. This is precisely
the claimed restricted optimum. It is not an unrestricted lower bound on
helpers for all words implementing the endpoint.

The constructor is not an endpoint or theorem-precondition validator. In
particular it does not test nonzero address frames, the full restored endpoint,
or which data targets are nonidentity. This is consistent with its stated
separate-check contract. Those conditions must be established before its
returned width is compared with the surplus bound. The zero-frame control
below makes that boundary explicit.

## 4. Exact counterexamples to stronger claims

Let `D(a,x,y)=I+(z^a-1)xy^T` in `F_2[z,z^{-1}]`; coordinate indices start
at zero. All vectors below have self-pairing one. These examples were checked
by direct Laurent matrix multiplication, independently of `H`.

1. **Allowing nonidentity helper endpoints invalidates the width bound.**
   Take one data register and one helper, with calls
   `D(1,e0,e0), D(1,e1,e1)`. The endpoint is `diag(z,z)`;
   `k=2,t=1,u=v=w=1`. Thus `w=1>floor((k-t)/2)=0`.
   The same word is correct on zero helper input and returns that input to
   zero, so zero-initialized-only correctness does not rescue the bound.

2. **Zero-input correctness can violate the stronger span inequality even
   with an identity helper diagonal.** One call with `x=e0`, `y=e0+e1`
   gives `[[z,z-1],[0,1]]`. Its action on `(data,0)` is `(z data,0)`, but
   `u+v=1>k-t=0`. The missing hypothesis is the zero upper cross block on
   arbitrary dirty input.

3. **Identity targets cannot be counted in `t`.** The helper-only inverse
   pair `D(1,e1,e1),D(-1,e1,e1)` has endpoint `I_2`, but if the identity
   data coordinate were counted as `t=1`, it would give `w=1>0` again.

4. **Zero frames cannot be retained when applying the surplus inequality.**
   The calls `D(2,e0,e0),D(0,e1,e1)` have endpoint `diag(z^2,1)` and paired
   helper rank one, violating the putative `k=2,t=1` bound. The second call
   has `a_j=0` and is explicitly outside the theorem. This illustrates why
   constructor output alone is not a certificate of the width bound.

5. **Arbitrary nonminimal pairing-preserving replacements can change the
   full endpoint.** Start from
   `D(3,e0,e0),D(1,e1,e1),D(-1,e1,e1)`, whose endpoint is `diag(z^3,1)`.
   In a three-register realization replace only the last `x` by `e1+e2`.
   Every data component and every scalar pairing is unchanged. The new
   endpoint has helper block `[[1,0],[z^-1-1,1]]`, not `I_2`. The quotient
   construction avoids this unpaired direction.

6. **Paired rank is not an unrestricted helper lower bound.** The original
   word in the preceding example has `w=1`. Moving both adjacent cancelling
   calls onto `e0` gives the same endpoint `z^3` with no helper, the same
   frames and order, but different data components and pairings. This is
   excluded by the stated optimality contract.

An additional positive edge case uses the word
`D(3,e0,e0),D(1,e0+e1,e0+e2),D(-1,e0+e1,e0+e2)`.
Both original helper spans have rank one, while `V^T U=0`; the constructor
removes both helpers and preserves the exact endpoint. This rules out
substituting separate span ranks for the paired rank.

## 5. Scope against the retained predecessors

I read the retained READMEs for `bit-dirty-auxiliary-registers`,
`bit-span4-auxiliary-structure` (#4118), and
`three-register-no-target-flag` (#720), and checked all three SHA256 and Git
blob hashes against the current package's `SOURCES.json`. This checks context
bytes, not the complete predecessor proofs or finite engines.

The dirty-auxiliary model explicitly permits arbitrary diagonal monomial
helper endpoints; #4118 inherits that broader setting. Its five-call,
three-data-target, two-dimensional address block is therefore not generally
reduced to one helper by the new theorem. For **exact restoration**, however,
`k=5,t=3` gives `w<=1`. The frames, their span and their rational realizability
are unchanged. #720's six-call result for exactly three scalar registers
excludes zero helpers under its cited hypotheses, leaving the four-register
case. The 120-projector count and `120^5=24,883,200,000` ordered-word count
are correct. No such census was run in this review.

For `k=8,t=3`, the restored-helper reduction to at most two helpers also
follows. Neither consequence proves a new paid-call lower bound, solves the
remaining address relation obligations, establishes a physical implementation,
or changes the selected result or its five assumptions.

## 6. Independent executed evidence

The separate checker is [independent.py](independent.py). Its packaged copy
changes only the package locator from the original review workspace to its own
directory; no mathematical or test logic was changed.
It uses the Python standard library, a separately written rectangular binary
elimination, and direct sparse Laurent matrix multiplication. It does not
import the package's verifier or use the ordered-path identity as its endpoint
oracle. The constructor is loaded from source bytes without bytecode writes.

Under CPython 3.12.14, both commands passed with byte-identical JSON output:

```sh
python3 -I -W error -B research/restored-helper-compression/independent.py
python3 -I -O -W error -B research/restored-helper-compression/independent.py
```

Marker: `PASS_C_INDEPENDENT_COMPRESSION_REVIEW`; seed `2026110655`.

| Independent check | Count |
|---|---:|
| Arbitrary helper factorizations, through 65 helper bits and 13 calls | 448 |
| Exact full-endpoint words | 181 |
| Strict reductions in helper dimension among those words | 121 |
| Explicit counterexamples to stronger claims | 6 |

The restored words include products in arbitrary binary scalar bases,
coordinate helper inverses, additional idle helper coordinates mixed by an
independent helper basis, and the zero-paired-rank example. The generated
original and compressed whole matrices, all scalar pairings, frames, data
parts, paired ranks and applicable surplus inequalities were checked.

The original normal and optimized receipts were compared during review.
Their executed counts and reviewed source hashes are retained above. The packaged
checker emits a fresh receipt containing the proof and constructor hashes. The universal conclusion rests on the written argument
audited above; these finite cases corroborate it without extending its scope.
