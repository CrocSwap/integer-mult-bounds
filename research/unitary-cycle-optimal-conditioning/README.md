# Best conditioning of a unitary-coupled observation cycle

This contribution was produced by Nick Petalas. Apache-2.0.

For any number of banks `W>=2`, internal dimension `d>=1`, and real
`0<r<1`, let

\[
 (Sx)_j=U_jx_{j+1\bmod W},\qquad A=I+rS,
\]

where every `U_j` is unitary. Put `a=1+r²`, `b=2r`, and `c=cos(π/W)`.
The exact minimum Euclidean condition number over all the couplings is

\[
 \boxed{\min\kappa_2(A)=
 \begin{cases}
 \sqrt{(a+bc)/(a-bc)},&W\text{ even},\\
 (1+r)/\sqrt{a-bc},&W\text{ odd}.
 \end{cases}}
\]

Equality holds exactly when the ordered product
`H=U_0 U_1 ... U_(W-1)` is `-I` for even `W`, or `I` for odd `W`.
This includes every finite internal dimension, arbitrary complex unitary
couplings, arbitrary dirty input vectors, and all `0<r<1`.

At `W=3,r=1/2`, the optimum is **√3**. The real rational matrix

\[
 A=\begin{pmatrix}1&1/2&0\\0&1&1/2\\1/2&0&1\end{pmatrix}
\]

attains it. Its Gram eigenvalues are `9/4,3/4,3/4`.
At `W=2`, choosing one edge `I` and the other `-I` gives condition number
one for every `r`. The new contribution is an exact optimum, equality
classification and attaining changed interface. It is a **scoped algebraic
proof with exact finite corroboration**, not a supplier or multiplication theorem.
The spectral method is classical; no literature-priority claim is intended.

## Why this question

Chris R / Clear1nsight's [PR #4842](https://github.com/CrocSwap/integer-mult-bounds/pull/4842),
head `acd3384454083d4eb673343eb7762877d43e5394`, establishes condition number
3 for the existing cyclic observation matrices in hexapode's
[#4818](https://github.com/CrocSwap/integer-mult-bounds/pull/4818),
[#4819](https://github.com/CrocSwap/integer-mult-bounds/pull/4819) and
[#4826](https://github.com/CrocSwap/integer-mult-bounds/pull/4826).
That source result is cited, not rechecked here. This package changes the
couplings and asks for the best possible conditioning in the resulting
algebraic class. The smaller constant does not apply to the unchanged sources.

The retained construction lineage includes Dugongue #4743, Yiyang / Lyy-iiis
#4710, lee-phys #4688, and Jacob Alan Sussman #4628. Their source notices and
credit are retained by citation. No predecessor code, scientific receipts or
unmerged Git objects are needed by this verifier. The separate two-bank port
conditioning result #4828 studies a different matrix and is not this target.

A bankwise unitary change of basis only conjugates `H`. It cannot turn an
existing noncentral product into the attaining scalar product. Thus the result
identifies a changed-interface design target, rather than a free reencoding of
the existing observations. There is no paid-call or κ improvement claimed.

## Proof

### The ordered cycle product controls the whole spectrum

The map `S` is unitary. The eigenvalue equation `Sx=z x` gives
`x_(j+1)=z U_j* x_j`, and closure gives `H x_0=z^W x_0`.
For every eigenvalue `h` of `H`, each of its `W` distinct roots `z` is an
eigenvalue of `S`, with the multiplicity of `h`. These eigenvectors span the
whole `Wd`-dimensional space. Equivalently, successively changing bank bases
makes every edge except the closing edge the identity, leaving `H` there.

Since `A` is normal, its squared singular values are exactly

\[
 a+b\cos\big((\theta+2\pi k)/W\big),\quad k=0,\ldots,W-1,
 \qquad e^{i\theta}\in\operatorname{spec}(H).
\]

All are positive because `a-b=(1-r)²>0`. The full condition number is at
least the condition number within any one such root orbit. We minimize one
orbit first, then characterize when every orbit can attain the minimum.

### Even number of banks

The orbit is closed under negation. Let `t` be the angular distance of its
nearest point to `+1`, with `0<=t<=δ=π/W`. Its extreme cosines are
`cos(t)` and `-cos(t)`. Its squared condition number is

\[
 R(t)=\frac{a+b\cos t}{a-b\cos t}.
\]

It decreases strictly on this interval away from zero and is minimized
uniquely at `t=δ`. The root orbit then satisfies `z^W=-1`. The minimum is
`(a+bc)/(a-bc)`. This reasoning also covers `W=2`, where `c=0`.

### Odd number of banks

Here `W>=3`. With the same `t` and `δ`, the distance of the nearest orbit
point to `-1` is `δ-t`. The squared condition number is

\[
 R(t)=\frac{a+b\cos t}{a-b\cos(\delta-t)}.
\]

The sign of its derivative is the sign of

\[
 a\{\sin(\delta-t)-\sin t\}+b\sin\delta
 =2a\cos(\delta/2)\sin(\delta/2-t)+b\sin\delta.
\]

The last expression is strictly decreasing on `[0,δ]`, is positive at zero,
and negative at `δ`, since `a>b>0`. Thus the sole interior stationary point
is a maximum, and the minimum lies at an endpoint. The endpoint values are

\[
 R(0)=\frac{a+b}{a-bc},\qquad R(\delta)=\frac{a+bc}{a-b}.
\]

Their denominators are positive, and
`(a+bc)(a-bc)-(a+b)(a-b)=b²(1-c²)>0`.
Therefore `R(δ)>R(0)` and zero is the unique minimizer. Its root orbit has
`z^W=1`, giving the stated odd formula.

### Attainment and equality for arbitrary dimension

If the complete matrix attains the lower bound, every individual root orbit
must do so too: each orbit's largest-to-smallest ratio lies between one and
the full ratio, and is already bounded below by the optimum. The unique
one-orbit minimizers force every eigenvalue of `H` to be `-1` for even `W`,
or `+1` for odd `W`. A unitary matrix with only that eigenvalue is the
corresponding scalar matrix. Conversely that scalar `H` makes all the root
orbits identical, so it attains the bound.

For any prescribed first `W-1` unitary edges, choose

\[
 U_{W-1}=(U_0\cdots U_{W-2})^*\,\sigma I,
 \qquad \sigma=(-1)^{W+1}.
\]

Then `H=σI` and the optimum is attained. This is an explicit algebraic
construction; it does not assert that a source native port can implement the
changed closing edge at its existing price.

## Reproduction and finite evidence

From the repository root, with the Python standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unitary-cycle-optimal-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/unitary-cycle-optimal-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unitary-cycle-optimal-conditioning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unitary-cycle-optimal-conditioning --check-source-history
```

Any CPython 3.12 executable can replace the displayed interpreter. The direct
verifier computes complete rational Gram characteristic polynomials from
literal bank matrices, independently of the root-orbit formula. It compares
them with Chebyshev predictions, checks exact attaining fixtures, exercises
noncommuting edges and nonmonomial rational orthogonal edges, and rejects
boundary mutations. Its generated JSON receipt binds all package sources by
SHA256. Use `--receipt PATH` to save it outside the checkout.
The exact enumeration checks 756 scalar cycles, including 378 attaining
products, and 576 two-dimensional cycles, including 72 attainers. Forty-two
noncommuting rational gauge fixtures and eleven boundary controls pass. The
all-size and arbitrary-complex claims depend on the written proof, rather
than the finite fixtures. See `TASK.json` for the exact verification domain.

## Scope, budget and limitations

The original `complex-rank-shape-decoder` card is changed to a local conditioning
result for a specified observation interface. Current source binding, rather
than the card's historical packing baseline, is the orientation control. The
source-bound positive control passed on base
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The independent inquiry is the changed-coupling optimum; no predecessor audit
is its deliverable. Live PRs, recent claims, local reservations, merged searches
and distinctive main-tree README searches found no same optimum in their stated
coverage. Sparse notes, unsearched diffs and unpublished work limit coverage.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134008).

This result assumes equal edge magnitudes `r`, Euclidean bank norms and unitary
edge factors. It does not optimize unequal gains, bank-dependent weighting,
nonunitary couplings, or intermediate execution norms. The norm formula applies
to the completed observation matrix only. Source-compatible native emission,
dirty-bank ownership/restoration, full caller costs, stock, compiler, physical
storage/tape, rounding and analytic recovery remain open and unpriced. Lean,
Docker, predecessor scientific replays and selected-frontier replay are unrun.
Independent human and formal proof-kernel review are unclaimed.

Power-of-ten inspection: no recursion; every computation is bounded by fixed
fixture limits `W<=13,d<=2` and matrix size at most 26. Functions stay below 60
lines. Explicit exceptions enforce scientific checks under optimized Python.
Python's rational arithmetic and collection allocation are a managed-runtime
deviation from fixed steady-state allocation; finite fixture sizes bound live
matrix storage, while exact coefficient sizes are determined by the fixed
rational inputs. There is no external runtime input except an optional receipt
path. Warning-strict ordinary and optimized runs are registered.

## Open next questions

- Can one actual native port change its closing coupling to the attaining
  product while retaining all independent targets and restoring dirty state?
  Start with a literal three-bank word and its complete paid invoice. A
  source-compatible realization is missing; the algebra alone does not provide it.
- Does a nonuniform gain profile improve the complete interface after paying
  its normalization and precision costs? First fix those physical prices and
  one concrete gain vector. Equal-gain spectral normality does not settle that
  different problem, and no expansion is justified without that ledger.
