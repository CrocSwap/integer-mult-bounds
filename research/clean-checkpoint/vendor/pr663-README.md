# Independent audit: PR628's balanced dirty commutator

**Result:** the pinned commutator restores its input and borrowed arrays under
its stated leaf contract, including nonlinear rounded leaves. No defect was
found in this scoped obligation. Its exact leaf count is

\[
 C(n)=3qn-2q^2<\frac98n^2,\qquad q=2^{\lfloor\log_2n\rfloor}.
\]

This tightens the submitted allowance `4*n*n` without changing the instruction
word, and can replace that allowance in the execution-error budget. It does
not change the asymptotic precision order or establish a new multiplication
exponent. The constant `9/8` is the sharp supremum for this splitting rule.

The contribution adds an independent free-term audit of the **actual pinned
recursive dispatcher**, a written all-`n` argument, and exact accounting.
PR628 already supplies dense rational accuracy comparisons and instruction
mutations. This audit's different evidence is that leaf functions are left
uninterpreted: they need not be linear, continuous, zero-preserving, or close
to a linear map for the restoration check. A second engine checks the intended
product in a free noncommutative algebra, without assuming that factors commute.
No literature-priority claim is made for the commutator or recurrence.

Interpreting input generators as initial arrays and function atoms as deterministic
leaf outputs preserves every symbolic cancellation. Thus each checked symbolic
identity holds for every such leaf instantiation at that tested factor count.

## Reproduce

From the repository root, with Python 3.9+ and no third-party packages:

```sh
python3 -B research/dirty-commutator-audit/verify.py --check
```

Expected output:

```text
PASS: 64 symbolic words; 10000 recurrence cases; 7 rejected controls; nonlinear dirt counterexample. n=62: 3904 leaves, 6 scratch arrays.
```

The command authenticates the vendored source and compares its complete result
with [EXPECTED.json](EXPECTED.json). `--write /tmp/dirty-audit.json` writes a
new certificate. The checker uses explicit exceptions; checks remain enabled
under optimized Python. It does not import or execute the producer's arithmetic,
root preparation, matrix solver, or top-level module initialization. It extracts
only `compose` from the pinned Python AST and intercepts leaf operations.

## Mathematical obligation and proof

Let a primitive on distinct arrays `x,y` add a deterministic function `F(x)` to
`y`, restore `x` exactly, and have a target-independent increment. Its negative
call must implement the exact inverse. Coefficients, phases, and any other
read-only parameters must remain fixed between paired calls. Arrays below are
elements of an abelian group; rounded dyadic arrays satisfy this requirement.

For a recursive child let `F(x;t)` denote its increment, where `t` contains
the deeper scratch arrays' **initial** contents. Inductively assume it restores
`x,t` and does not depend on its initial target. The parent performs

```text
z += B(x;t)
y += A(z;t)
z -= B(x;t)
y -= A(z;t)
```

Every child restores its deeper scratch. The paired `B` calls see identical
`x,t`, so `z` returns to its initial value `z0`. The net increment is

\[
 F_n(x;z_0,t)=A(z_0+B(x;t);t)-A(z_0;t).
\]

It is independent of the initial `y`; all other arrays are restored exactly.
This proves the recursive contract by induction, **without linearity**. With
linear ideal factors, the same induction gives exactly `A B x`, with no
dependence on the initial scratch. The factor list executes in list order,
so the resulting operator is `F_(n-1) ... F_1 F_0`.

The inverse word reverses the whole instruction sequence and inverts every
sign. The pinned `compose` does this at each recursive call. Just negating signs
in their original order is invalid: for `B(x)=x`, `A(z)=z^2`, and `x=z0=1`, the
positive increment is `3`, the true inverse increment is `-3`, and same-order
sign negation gives `+1`.

All source, target and scratch arrays must be pairwise distinct. In particular,
an ancestor target cannot be borrowed as deeper scratch: it can change between
the paired calls. The pinned implementation explicitly enforces this exclusion.

Exact restoration does **not** imply independence from initial scratch for
nonlinear leaves. The same two-factor example with `x=1` gives increments `1`
and `3` at `z0=0` and `z0=1`, respectively, while restoring the source and scratch
in both executions. This concrete example corroborates PR628's stated caveat;
it is not a counterexample to that PR's claim.

## Complete call recurrence

Count all forward and inverse primitive leaf calls, without cancellation or
special treatment of identity factors. The exact recurrence is

\[
 C(1)=1,\qquad C(n)=2C(\lfloor n/2\rfloor)+2C(\lceil n/2\rceil).
\]

Write `q=2^k <= n < 2q`. Repeated balanced splitting gives `2q-n` ordinary
factor-tree leaves at depth `k` and `2n-2q` at depth `k+1`. To see that these are
the only depths, after `k` splits the group sizes are one or two; each group
of size two splits once more. Each descent in the commutator doubles a factor
leaf's execution multiplicity. Therefore

\[
 C(n)=(2q-n)q+(2n-2q)2q=3qn-2q^2.
\]

The exact identity

\[
 \frac98n^2-C(n)=\frac{(3n-4q)^2}{8}
\]

proves the strict upper bound: `3n=4q` is impossible for integer `n` when `q`
is a power of two. Along the integers nearest `4q/3`, the square is `1`, so
`C(n)/n^2` tends to `9/8`. The recursion uses exactly
`ceil(log2(n))` distinct scratch arrays, with zero when `n=1`.

| Factor count | Exact leaf calls | Submitted allowance `4n²` | Scratch arrays |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 4 | 0 |
| 3 | 10 | 36 | 2 |
| 7 | 52 | 196 | 3 |
| 15 | 232 | 900 | 4 |
| 31 | 976 | 3844 | 5 |
| 62 | 3904 | 15376 | 6 |
| 63 | 4000 | 15876 | 6 |
| 64 | 4096 | 16384 | 6 |

The seed-selected `n=62` case tests the generic dispatcher. It does not assert
a prime-power kernel at radix 63. The neighboring `n=63` case is the factor
count for a radix-64 kernel.

## Consequence for the inherited execution-error budget

Retain PR628's assumptions on **both signs** of each leaf: ideal operator norm
at most `K=r/beta`, and local error at most `a*u*(B+1)`, where
`a=13*(r+1)/beta^3`, `u=2^-w`, and `B` bounds the source norm. Let `M_j` be
the maximum array norm after `j` completed leaves and `D` its initial bound.
Under `a*u <= 1`, with `G=2+K`,

\[
 M_{j+1}\le(1+K)M_j+au(M_j+1),\qquad
 M_j+1\le G^j(D+1).
\]

The second expression means **one plus `M_j`**, not the next indexed norm.
If `e_j` compares computed and ideal completed-leaf states, then

\[
 e_{j+1}\le(1+K)e_j+auG^j(D+1),\qquad
 e_N\le Na(D+1)uG^{N-1}.
\]

Thus the submitted sufficient execution precision remains valid with the
**exact** `N=C(n)`:

\[
 w\ge p+1+\lceil\log_2(Na(D+1))\rceil
       +(N-1)\lceil\log_2G\rceil,
\]

together with `a*u<=1` and `u<=beta^2/2`. This is an implication conditional
on the inherited leaf estimates, not a new audit of those estimates. It gives
execution error at most `2^(-p-1)`; coefficient/phase preparation must still
supply the other half of the total error budget, scaled to the original input.
The existing `O(p+log(D+1)+r^5)` precision and `O(r^2)` pass orders remain.
This package does not modify PR628's generator or its certificates.

## Evidence, coverage and limits

- **Exact symbolic checks, `1 <= n <= 64`:** source/scratch restoration,
  target independence, whole-word inversion, equality of pinned and independently
  compiled instruction traces, and the noncommuting ideal linear product.
- **Exact integer checks, `1 <= n <= 10000`:** recursive and closed counts agree,
  and the sharp-envelope square identity holds.
- **Seven negative controls:** omitted final subtraction, omitted scratch
  restoration, missing inverse reversal, borrowing an ancestor source or target,
  reusing a scratch depth, and insufficient scratch depth.
- **Nonlinear example:** exact dirty restoration with different target increments
  for two initial scratch values.

The finite symbolic replay checks these concrete instruction words in an exact
term model; it is not a formal proof of the all-`n` theorem. The induction above
is the written all-`n` argument, independently reviewed by another Codex agent.
No human peer review, Lean certification, or full multiplication theorem follows.
The actual rounded leaf's accuracy and restoration, preparation complexity,
phase access, bit arithmetic, routing, and full-transform composition retain
their separate obligations. Selected supplier assumptions remain unchanged.

This is a bounded audit, not a parameter search. There is no random search:
seed 62 selected the object and uneven-split case; the enumerations above were
completed in full with no adaptive early stop.

## Pins and attribution

Repository base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Subject:
[Chafik Boukhalfa's PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628),
head `0768f97d06c623b8211e651543c66135796b62bf`, specifically
[`DIRTY-PROOF.md`](https://github.com/CrocSwap/integer-mult-bounds/blob/0768f97d06c623b8211e651543c66135796b62bf/research/prime-power-cyclic-scan/DIRTY-PROOF.md)
and [`dirty.py`](https://github.com/CrocSwap/integer-mult-bounds/blob/0768f97d06c623b8211e651543c66135796b62bf/research/prime-power-cyclic-scan/dirty.py).
The latter is retained byte-for-byte for offline replay. SHA-256 pins,
the accepted-frontier snapshot, and analytic predecessor information are in
[SOURCE.json](SOURCE.json). [CLAIM.md](CLAIM.md) records track selection and overlap
review. See [NOTICE.md](NOTICE.md) for source credits and assistance disclosure.
