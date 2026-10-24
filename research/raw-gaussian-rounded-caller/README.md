# Independent audit of the rounded raw Gaussian caller

Prepared for Brian (`JoyboyBrian`) with substantial OpenAI Codex assistance.
Apache-2.0.

This package independently proves the actual raw caller's three-stage error
composition, in both the forward and stored-inverse directions. It follows
[PR #4756](https://github.com/CrocSwap/integer-mult-bounds/pull/4756), which
stopped at uniform common-reference admission. Here the checker constructs
the actual `RawGaussian` factory, executes its actual primitive gates with
independent exact rounding, and binds the intermediate radius, shared grid,
diagonal reciprocals and reference charge to the written argument.

[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19131469).
The audited implication is `RAW-GAUSSIAN-PROOF.md` §7, not a new compiler or
an assertion that its original proof was missing. No source is modified.

## Quantified contract

Use Euclidean vector and operator norms. Let the ideal raw map be `A T B`,
where `A,B` are invertible diagonal matrices and `T` is the normalized child.
Suppose `G,H>=1` bound

```
||A||,||B||,||A^-1||,||B^-1|| <= G,
||T||,||T^-1|| <= H.
```

Let `n>=1`, input radius `R>=1`, target `τ=2^(-t)` with integer `t>=1`,
and incoming data grid `F₀>=0`. Set the actual caller's allowances

```
δ = τ/(24GH(R+1)),   b_g = max(1,ceil(log2(4G/δ))),
R* = 2G(R+1),        t* = t + ceil(log2(16G)),
F >= max(F₀, t+ceil(log2(24nGH)), child_required_grid),
r = n 2^(-F),       E <= 2^(-t*) <= τ/(16G).
```

The normalized child's forward program and the reverse of its stored gates
must each approximate `T` or `T^-1` with error at most `E` on every input
of norm at most `R*` on the `F` grid. This is an explicit dependency on the
retained normalized circuit theorem; testing a few vectors does not prove it.
The child's incoming-grid dependence is a maximum, permitting its allocation
at the **same** `F` used by both outer diagonal stages.

Assume the stored diagonals `Â,B̂` and their exact reciprocals satisfy
operator errors at most `δ` against each ideal diagonal and its inverse.
Round data after the input diagonal, every emitted child gate and the output
diagonal. The complete forward order is `B̂; child; Â`; the stored-inverse
order is `Â^-1; reverse stored child; B̂^-1`. Then for every admissible input,
in either direction, the error against the ideal raw map or inverse is at most

```
E_raw = 2GE + 3GHδR + 3GHr < 3τ/8.
```

If the same immutable reference satisfies
`E_ref <= τ/(8(R+1)Q_raw²)` and `Q_raw=G²H` bounds the ideal raw inverse,
the forward and inverse errors against that reference are respectively bounded by

```
E_raw + E_ref R < τ/2,
E_raw + 2Q_raw² E_ref R < 5τ/8.
```

In particular both are below `τ`, as required by the caller. These explicit
slack bounds audit the existing allocation; no smaller precision is installed.
The rounded forward and reverse instruction sequences are nonlinear and are
not asserted to be exact inverses of one another.

## 1. Positive stored coefficients also control their reciprocals

The retained positive exponential producer, at relative request `b_g`, returns
one lower value with relative loss at most `ε=2^(-b_g-2)`. Its nonzero lower
bound makes an exact stored reciprocal legal; the reciprocal's relative
error is at most `ε/(1-ε)<=2ε`. Exact rational prefactors, including the
broad `α^-1`, are multiplied separately. The raw caller's `G` bounds each
ideal coefficient and its reciprocal, so the absolute error in each stored
choice, and in its exact reciprocal, is at most `2Gε<=δ/8<=δ`.
The source also checks each actual enclosure receipt against `δ`.

For the narrow similarity, a chirp and its exact reciprocal are stored as a
pair; they are not generated as unrelated rounded exponentials. For any
number of coordinates the diagonal operator norm is the maximum coordinate
modulus, so this coefficient allowance incurs no factor of `n`.

This argument uses the predecessor interval-width/positive-weight contract,
independently audited at the scalar boundary in #4220 and at the reference
allocation in #4756. The present result binds those receipts to the later
raw execution and inverse use; it does not implement another transcendental
oracle or admit the normalized matrix inverse theorem independently.

## 2. The actual intermediate input is within the child's radius

Nearest-grid rounding of each complex output component has Euclidean vector
error at most `n 2^(-F)=r`, a conservative allowance for `n>=1`.
For either direction, let `D_in` be the ideal input diagonal and `D̂_in`
its stored counterpart. After this first rounded layer,

```
z = round_F(D̂_in x),
||z-D_in x|| <= δR+r,
||z|| <= (G+δ)R+r <= R*.
```

Indeed `δ<=G` and `r<=G` follow from the displayed allocation, so the last
quantity is at most `2GR+G<=2G(R+1)`. The normalized contract applies to this
rounded, perturbed input `z`, not merely to the ideal `D_in x` or to the
original input radius. This is why a callback certificate at the original
radius `R` cannot be substituted without checking the entrance.

The first layer's output is on the `F` grid. The source binds the child's
actual data grid to that same `F`; incoming grid `F₀` is retained by the
maximum. Both scalar layers and the child therefore execute within one
unbroken grid convention.

## 3. Three-stage composition, without assuming commuting errors

Write `V=T` for the forward direction and `V=T^-1` for the inverse. Let
`D_out` be the corresponding ideal output diagonal and let the child output
be `V z + e`, with `||e||<=E`. Before final rounding, compare
`D̂_out(Vz+e)` with `D_out V D_in x`. Adding and subtracting in that order
bounds the difference, including final rounding, by

```
(G+δ)E + δ H G R + (G+δ)H(δR+r) + r.
```

Since `δ<=G` and `G,H>=1`, this is at most
`2GE+3GHδR+3GHr`. No error is commuted through `T`, and no error at the input
diagonal is charged as though it occurred only after the child.
The allocation gives

```
2GE <= τ/8,
3GHδR = τR/(8(R+1)) < τ/8,
3GHr <= τ/8.
```

This proves the strict raw error bound. The same proof covers the inverse
because its input/output diagonals are `A^-1,B^-1` and the child consumes
its **stored reversed program**, under the same norm and error hypotheses.
A global adjoint or an unreversed wrapper would generally be a different map.

## 4. The fixed reference and inverse perturbation

Let `M=A T B` and let `M_ref` be the same reference restriction used at raw
admission. `Q_raw E_ref<1/2` follows from its guard, since `Q_raw,R>=1` and
`τ<=1/2`. The resolvent identity and Neumann bound give

```
||M_ref^-1-M^-1|| <= 2Q_raw² E_ref.
```

Multiply this operator comparison by the **original** input radius `R` and
add it to `E_raw`. The inverse charge is less than `τ/4`, while the forward
reference charge is less than `τ/8`, proving the displayed final bounds.
The source checks the reference description and actual window again at
compile time, so changing or rerounding a window cannot borrow the old
admission. Core/halo/global composition remains a different obligation.

## Source-bound evidence

The independent oracle imports the actual `RawGaussian`, `Gaussian` and
`Reference` classes and their declared transitive primitive closure. It imports
no predecessor verifier. It implements matrix products, Gaussian elimination,
matching-layer execution and component rounding separately; only the exact
Gaussian-rational scalar representation is shared. Actual source `exact.apply`
is also run on the same prepared programs, and the two rounded outputs and
counts must agree exactly.

Four actual size-two factories cover both directions of narrow and broad
blocks and both signs of the center phase (`17/194`, `-73/194`). Each emits
23 layers. Across 24 forward/inverse trajectories, the independent engine
checks 1008 rounded coordinates, actual normalized entrance radii, complete
same-reference output errors, source receipt arithmetic and exact unrounded
stored inverses. Data grids are 119 or 120 bits, including a nonzero value on the requested 9-bit incoming grid. These small
fixtures bind the actual caller; the theorem above is quantified independently.

Five controls discriminate wrong inverse wrapper order, source rejection of
a changed child data grid, source rejection of an underfunded intermediate
radius, direct-only error accounting for a reciprocal, and omission of the
input diagonal's amplified rounding. The latter two are exact mathematical
countercontrols, not claimed source defects. The broad nonuniform diagonal
fixture supplies the noncommuting wrapper-order discrimination.

## Exact sources, overlap and reproduction

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The raw source was completed at `c9db4069d59bfad26a15fe000b91cc3a058684e5`
and retained by #4205 head `78c72e563173f3822fcb4efed9ceeccf05630258`.
#4756 head `3bda06c5d2735161a0e0f1350ed517866ae15198` covers uniform reference
admission and explicitly excludes the execution audited here. All live inputs
are pinned in `SOURCES.json` and declared in `VERIFY.json`.

The round's fresh search covered 299 open PRs, 3721 Discussion records and
6319 local notes, with complete inventories. Relevant live predecessor heads
and #4202 were checked. Existing generic simultaneous-rounding, scalar backend,
reference-allocation and tensor/raw-H work retain their different scopes.
This search is coverage evidence, not a novelty certificate.

```
python3 scripts/research_package.py --package research/raw-gaussian-rounded-caller --check-only
python3.12 scripts/research_package.py --package research/raw-gaussian-rounded-caller
python3 -B scripts/check_research_commit.py --package research/raw-gaussian-rounded-caller --check-source-history
```

The registered normal and optimized commands use Python 3.12 and the standard
library only. Run the last preflight after committing. Official exports can
be checked with `scripts/export_research_package.py`, then the documented
`verify.py` run directly without Git. No full historical suite, Lean, Docker,
complete raw-axis enumeration, native execution or multiplication replay is
claimed. Author-process agent review is not independent human/formal acceptance.

## Open next questions

Can the actual core/halo caller preserve this local contract at every raw
invocation, including the true intermediate radius and its immutable reference
restriction? First bind the caller's stage-by-stage input bounds, block carving,
reference identities and precision requests to the concrete raw objects, then
compose the output errors without replacing the actual entrance by the root
radius. Physical ownership, preparation and delivery remain separate costs.

## Attribution

Jose Manuel supplied the original normalized/raw construction and three-stage
error argument. Credit Vlado's circuit and phase-cell lineage, Jeremy Kothe's
raw identities, Mason Hale's interval routines, Chafik Boukhalfa's phase
certificates, Cinna Davis's later caller and ToikY/#4220's scalar audit.
The contribution is the independent caller derivation and actual source-bound
execution oracle; classical perturbation and diagonal norm facts are retained.
