# Selected cold-wrapper identities by exact amplitudes

**Research audit / independent finite verification; no new kappa.** The 14
distinct cold-ended helper wrappers used by the selected PR626 construction
have the claimed exact operator, including global phase. An independent
amplitude implementation checks all 512 input basis columns for each wrapper.
These identities occur at 22 helper registers in each of the CK and JP8
providers: 44 provider-local instances, not 44 distinct matrices.

The result is 7,168 checked columns, determining 3,670,016 matrix entries.
Each column has 16 nonzero entries; equality of the sparse columns also checks
all zero entries. No producer, Clifford tableau, `lower_child`, or state-vector
executor is imported. The new checker derives the canonical-frame kernel and
separately decodes the serialized left and right monomials. Those two paths
share only elementary Gaussian-integer arithmetic and the specified tensor
coefficients of `C`.

## Replay

From the repository root, with Python 3.11+ and no additional dependencies:

```sh
python3 -B research/cold-wrapper-amplitude-audit/verify.py
```

Expected output:

```text
PASS_COLD_WRAPPER_AMPLITUDE_AUDIT: 14 frames; 44 helpers; 7168 columns; 3670016 entries; 70 rejected mutations
```

The command reads pinned, committed inputs and compares the complete result
with `EXPECTED.json`; it writes nothing. It also works with `-I -O` and from
another working directory. `--write /new/path.json` writes a fresh receipt and
refuses to overwrite an existing file. `--root` selects a checkout containing
the same pinned inputs. `test_verify.py` exercises failure detection separately.

## Exact statement and source chain

At base `66849e1475c930fd7732b1a0067ffee7e1e95f60`, the accepted conditional
result is `51110230636731/31250000000000000`, from PR626 at
`660de893d27bb7abd1d5b01b1640207528a5c851` with the PR543 bit supplier.
The main review explicitly reuses PR622's identical native providers. Its
archived `ck-local` and `jp8-local` canonical words and residual adapters are
the inputs here. Their canonical JSON SHA256 values must match both
`SOURCES.json` and PR626's pinned `data/SPEC.json`. Compressed container bytes
are not an equality criterion.

For each helper with entrance `E=0` and proper terminal frame `U`, the checker
requires `dim U=4` and extracts the exact recipe `(L,R)` indexed by `0:U`.
It verifies

```text
T_U = L (C_[4] tensor I_[5]) R,
```

equivalently `L^-1 T_U R^-1 = C_[4] tensor I_[5]`. Operators act from right to
left. Here `T_0=I`, so `T_U` is precisely the residual `T_U T_0^-1` in the
predecessor's Lemma A. This is a statement about these finite 512-dimensional
complex-linear operators, and therefore about arbitrary complex input
vectors, not only clean scalar inputs.

`SOURCES.json` also pins the exact canonical-frame and monomial definitions,
the existing wrapper checker, the helper-interface check and the proof/review
context. It does not download or execute those definitions. The selected
pointer and the original packages are unchanged.

## Independent kernel derivation

The primitive in the retained source is

```text
C = ((1+i) I + (1-i) X) / 2,
```

where `X` flips one binary coordinate. It is not an unnormalized Hadamard
matrix. For `r=4`, its tensor kernel on the first four coordinates has
Gaussian-integer numerator

```text
a_s = (1+i)^(4-|s|) (1-i)^|s|,       s in F_2^4,
```

and common denominator 16. There are no floating-point calculations.

For an ordered frame `U`, complete its columns to `G` by taking the first
independent standard basis vectors in order `e_0,...,e_8`. The source defines

```text
Q = I + (G^-1)^T G^-1 over F_2,
K = D_Q P_G,
T_U = K C_[4] K^-1.
```

The checker constructs inverse coordinates by enumerating the entire binary
span. It uses neither the source's row reduction nor its matrix inversion.
For the canonical diagonal define

```text
q_Q(x) = sum_i Q_ii x_i + 2 sum_(i<j) Q_ij x_i x_j mod 4.
```

Applying `K^-1`, then `C_[4]`, then `K` gives the first kernel directly:

```text
16 T_U[y,x] = i^(q_Q(y)-q_Q(x)) a_s    if y = x xor G(s,0),
              0                       otherwise.
```

For the second kernel, a serialized monomial `M` is decoded as

```text
M |x> = i^(phi_M + q_M(x)) |G_M x xor b_M>,
q_M(x) = sum_i alpha_i x_i + 2 sum_(i<j) Q_ij x_i x_j mod 4.
```

Thus `L C_[4] R |x>` is obtained by applying the right affine map, adding
each of the 16 coordinate displacements with coefficient `a_s`, and applying
the left affine map. Both affine maps are checked to be bijections; the
quadratic symmetry and diagonal/linear parity conditions are checked too.
There are exactly 16 distinct outputs in each path, so the sparse comparison
loses neither cancellation nor unlisted entries. Equality on every basis
column establishes the finite operator identity by linearity. It does not
establish an all-size compiler theorem or a proof-assistant formalization.

## Adversarial control: zero input and support do not fix phase

For every one of the 14 frames, replace the right wrapper by `R Z_6`.
In the serialized recipe this adds 2 modulo 4 to `linear_Z4[6]`. The mutant
still has the same residual width and the same support in every column, and
its output on `|0>` is unchanged. But its complete operator is

```text
L C_[4] R Z_6 = T_U Z_6.
```

It negates exactly the 256 columns with input bit 6 set. Since `T_U` is
invertible, none of those columns is zero, so all 256 differ. The checker
confirms this for each frame and records exact counterexamples. For the
seed-selected first frame `[266,138,75,30]`, at input 64 and output 11 the
correct amplitude is `4/16=1/4`; the mutant gives `-4/16=-1/4`.

This is a concrete counterexample to using only width, support and the
zero-input column as an admission test. **It is not a defect in the existing
checker**: that checker also compares full Clifford tableaus, which detect
the `Z_6` change. Its additional zero-state check fixes global phase once the
tableau is known. The all-column implementation supplies evidence from a
different representation of the same obligation.

The other controls independently change each wrapper's global phase, swap
the two wrappers, or change the left translation. All five controls are
rejected on every frame: 70 exact counterexamples in total.

## Scope, coverage and overlap

Assignment seed 60 selects the mathematical audit track, starts at sorted
frame index `60 mod 14`, and selects phase coordinate `60 mod 9=6`. Coverage
is exhaustive over the extracted 14 matrices and all 512 columns; the seed
does not sample or reduce that coverage. The stopping rule is completion of
those matrices and the five stated controls per matrix, followed by source
and receipt checks. There is no search for a better construction.

The existing `verify_cold617_interface.py` and PR662's performance adapter
already check these residuals with the source Clifford engine. PR662 speeds
up that engine; this package imports none of it and checks all columns with
a direct kernel. PR581 proves one different rank-one child in Lean; this
package concerns all current rank-four cold ends and is not a Lean proof.
PR675 audits owner timing and controller bridges, a different obligation.

No flaw was found in the claimed cold-wrapper identities. This audit does
not re-establish the full dirty scalar word, wrapper placement, cold-end
no-later-touch conditions, paid invoice, owner charts, entering-helper
wrappers or supplier moments. The inherited common-label/mutable-basis,
pooled hosting, all-size, precision, tape and analytic assumptions remain.
There is no new multiplication kappa, practical speedup or novelty claim
about Clifford algebra. See `NOTICE.md`, `CLAIM.json` and `VALIDATION.md`.

After `research/clifford-state-production/`, the multicold `clifford_exact.py` digest is recorded under `provenance_sha256` only (this audit does not import that module).
