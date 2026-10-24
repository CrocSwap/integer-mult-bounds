# The exact 66-grade equal-weight sign tariff is 68 executions

This scoped proof and finite sign certificate were produced by Nick Petalas.
Apache-2.0.

## Contract and theorem

Let `V = V_0 direct-sum ... direct-sum V_65`, with each grade nonzero and
of arbitrary finite dimension over a field of characteristic zero. A completed
linear program W acts on V. A root wrapper may run W K times, conjugating
execution t by a grade-constant sign map D_t, and return the equal average

```
                  (1/K) sum_t D_t W D_t.
```

The same signs must extract the block diagonal of W for every W. The signs
are independent of W and its input. Signs have entries +1 or -1, and each
execution has the same positive weight 1/K. Each complete W is one charged
execution. The target is the smallest K in this contract.

**Theorem.** The exact minimum is K=68. For dyadic W and dyadic inputs,
the wrapper can retain a common exact per-execution output grid and recover
the diagonal output by an exact binary shift and an exact integer division
by 17. It does not require a persistent odd denominator in the recovered output.

This concerns the extraction wrapper, not a native implementation of W.
The sign design and its arithmetic are independent of the dimensions of the
grades. The conclusion also holds when the allowed W are arbitrary block
lower-triangular operators: each unordered grade pair still has an allowed
off-diagonal block whose cancellation is necessary.

## Lower bound

Write s_th for the sign on grade h in execution t, and S for the K-by-66
sign array. On block (h,j) the multiplier is

```
                   (1/K) sum_t s_th s_tj.
```

Testing one nonzero off-diagonal block forces distinct columns of S to be
orthogonal. Thus `S^T S=K I_66`, and rank gives K>=66.

Take any three columns. Multiplying each row by its first-column sign
normalizes the first column to all ones without changing dot products.
The other two columns are balanced. If their four joint sign counts are
`n_++, n_+-, n_-+, n_--`, balance and their mutual orthogonality give
`n_++=n_+-=n_-+=n_--=K/4`. Consequently 4 divides K. The least multiple
of four at least 66 is 68.

No lower bound is asserted for unequal weights, independent input/output
maps, complex phases, W-dependent signs or exploiting missing blocks of a
particular W.

## Attainment from the classical Paley construction

Use the prime p=67 and its quadratic character chi, with chi(0)=0. Index
rows and columns of Q by the residues modulo 67 and set

```
 Q_ij = chi(i-j),                  H = [1  1^T]
                                      [1  Q-I].
```

This is the classical Paley order-68 Hadamard matrix. Paley's construction,
Hadamard orthogonality and character averaging are credited methods, not
new constructions claimed here. See R. E. A. C. Paley, [On Orthogonal
Matrices](https://doi.org/10.1002/sapm1933121311), 1933, pp. 311-320.

Here is a self-contained proof at the required prime. The nonzero squares
are half the nonzero residues, so each Q row sums to zero. Since 67 is 3
modulo 4, chi(-1)=-1 and Q is skew-symmetric. For a != b,

```
                 sum_x chi(x-a) chi(x-b) = -1.
```

Indeed, the number of pairs (x,y) satisfying
`y^2=(x-a)(x-b)` equals 67 plus that sum. The invertible change of
variables `u=2x-a-b-2y`, `v=2x-a-b+2y` gives
`uv=(a-b)^2`, which has exactly 66 solutions, one per nonzero u.
For a=b the character dot product is 66. Therefore
`Q Q^T=67I-J`. Skew-symmetry now gives

```
             (Q-I)(Q-I)^T = 68I-J,       H H^T = 68I.
```

The top/bottom cross terms vanish because each Q row sums to zero.
As H is square, `H^T H=68I` also follows. Take its first 66 columns as S.
These columns give exactly the required extraction by the block multiplier
formula. The verifier independently enumerates the quadratic residues,
constructs H and checks every entry of its upper-triangular Gram matrix.

## Exact dyadic recovery and the extra arithmetic

Suppose a chosen common grid `2^-b` represents all execution outputs and
the desired block-diagonal output y. For dyadic operator entries and inputs,
choose b at least the sum of their denominator exponents, and any larger
exponent needed by the intermediate-value contract. This represents y because
its coordinates are sums of a subset of the same matrix-entry/input products.
A grid guaranteed only for one W/input pair by cancellation is insufficient.

Write `y=2^-b z`, with z an integer vector. Orthogonality proves that the
signed-output accumulator is exactly `2^-b (68z)`.
Thus its numerator is divisible by four and then by 17. Divide first by
four and then divide the integer numerator exactly by 17. The quotient is
z on the same grid. Division by 68 is not an arbitrary free dyadic scalar;
the divisibility proof makes this implementation legitimate.

Signed binary long division by 17 is explicit. Scan the magnitude bits
from left to right, maintaining `0<=r<17`; replace r by `2r+bit`, emit one
quotient bit if this is at least 17, and subtract 17 in that case. Restore
the input sign. The final remainder is zero on the proved accumulator.
This takes one pass over the numerator with a bounded remainder alphabet.
`verify.py` implements and tests this procedure, including negative values
and rejection of inexact division. Its 512-bit test cap bounds finite
corroboration only; the written recurrence works for every finite width.

If every signed execution output numerator has magnitude at most M, the
accumulator magnitude is at most 68M, so seven extra integer bits suffice.
Signs preserve input magnitudes and exact grids. Use the original preserved
input, one reusable complete-run workspace and one accumulator. The cost is
68 complete executions plus sign/copy/accumulation passes and exact division.
For N scalar coordinates of bounded numerator width B, the wrapper's own
bit work is O(68NB), including division, under sequential binary storage.
No full fixed-tape instruction tariff is claimed. Only the original inputs
receive productive credit, and the wrapper is placed once at the root.

## Application to the cited bounded-lane interface

Yiyang's [PR #5037](https://github.com/CrocSwap/integer-mult-bounds/pull/5037)
supplies the root-only same-grade extraction contract in
`research/bounded-lane-border-core/precision/EXTRACTION.md`. At 66 grades,
its Walsh wrapper uses `2^ceil(log2(66))=128` complete executions. The above
wrapper uses 68, saving 60 complete executions, a fraction 15/32 of the
previous wrapper's count. It is optimal in the declared equal-weight sign
contract. The seven-bit accumulator bound is unchanged.

This does not prove a wall-clock speedup or change the local native invoice.
The actual native shears, recursive source/exit matching, rounded execution,
physical ownership/movement/restoration, stock, BIT transfer and outer admission
remain obligations of the predecessor program. No new kappa or complete
multiplication theorem follows. The Paley construction itself is classical;
the contribution is the sharp extraction count and exact-divisibility wrapper
for this declared graded interface.
