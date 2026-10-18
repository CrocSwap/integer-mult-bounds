# Approximate-call error budget for the complete QQ16 decoder

**A scoped local stability certificate; no new supplier or kappa.** This gives
an all-tensor-depth error contract for the unchanged 2,463-event word in
[PR2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540).
[PR2603](https://github.com/CrocSwap/integer-mult-bounds/pull/2603) bounds the
exact caller grid and magnitude, and explicitly leaves approximate native-child
errors open. The new result bounds their propagation, together with ADD errors,
through the complete added decoder. No predecessor verifier is imported or run.

For every positive integer payload depth `lambda`, put

```text
X = 2^ceil(lambda/2),     Y = 2^(4*lambda).
```

If each ADD result has componentwise error at most `eps_add`, each signed
rank-one call at most `eps_line`, and each rank-eight call at most `eps_stage`,
then the following bounds hold against the exact reference word:

| Fields | Error bound, in the physical componentwise norm |
|---|---|
| All 224 decoded outputs; every owned/scratch caller boundary | `(928 + 784Y) eps_add + 49 eps_line + 392 eps_stage` |
| Each of the 112 borrowed Y returns; their intermediate boundaries | `(1 + X) eps_line` |
| The 112 borrowed X fields | Zero |
| Retired early banks and scratch after their exact CLEARs | Zero |

For a common tolerance `epsilon`, **every declared caller boundary** has error
at most

```text
(1369 + 784*2^(4*lambda)) epsilon < 2^(4*lambda+10) epsilon.
```

At one tensor layer this is **13,913 epsilon**; borrowed Y return error is at
most **3 epsilon**. Thus local errors at most `2^-(q+4*lambda+10)` suffice for
strict error below `2^-q` at these boundaries. This is an error allocation
condition, not a proof that a recursive child achieves that accuracy at the
stated bit width or cost. In particular, approximate inverse calls need not
restore borrowed arrays exactly.

## Precise contract

The reference and perturbed executions have the same physical inputs. Errors
are measured as the supremum over all owners, payload addresses and real and
imaginary components. They need not be random or independent. Each local error
is relative to the **exact operation on its actual, possibly perturbed input**.
The tolerance must therefore hold on every input the approximate run reaches.
An ADD error is measured after the whole declared `dst += c*src` operation.
Native errors are measured after the whole signed-line or rank-eight call,
including its exact monomial wrappers. Each noisy ADD or child writes only
its declared destination; child-private workspace must meet the inherited
restoration contract.

The native semantics are the inherited PR2540 contract: signed line calls are
tensor powers of `C_v` or its inverse; a rank-eight stage is a product of eight
such lines per tensor layer. Cover/owner maps and monomial wrappers are exact
permutations with Gaussian-unit signs. CLEAR writes exact zero. No error is
inserted in those maps, clears, lifetime markers or metadata checkpoints.
There is no overflow, saturation, address error or data-dependent control change.
Those failures are outside this additive-error model.

The early capture happens after F0. The `history_boundary` denotes the
inherited B1 execution and introduces the 224 current physical reference inputs;
it is **not a zero-cost B1 implementation**. The sixteen retained banks keep
any capture error across that boundary and remain isolated from B1. Perturbations
inside F0/B1 are excluded. Their output errors require a separate input-error
contract; resetting them in this calculation does not assert that an actual B1
call removes errors. Initially arbitrary owned-bank dirt is identical in the
reference and perturbed runs and is discarded by the charged exact CLEARs.

The literal private bodies execute completely at one owner before moving to
the next. They contain no cover map. The same recurrence therefore bounds each
owner's local body; its supremum bounds every partial sweep. Whole-cover maps
preserve that supremum. Native child interiors and elementary instructions
inside a declared ADD are not caller boundaries covered by this theorem.

## Proof

### 1. Native operator norms

Write

```text
C_v = ((1+i)/2) I + ((1-i)/2) T_v,
```

where `T_v` is binary translation. In a product of `m` independent line
factors, the coefficient at a cube point of weight `w` is

```text
2^-m (1+i)^(m-w) (1-i)^w.
```

For even `m`, each of the `2^m` coefficients has one nonzero Gaussian
component of magnitude `2^(-m/2)`. For odd `m`, both components have magnitude
`2^(-(m+1)/2)`. The norm from componentwise input bounds to one real or
imaginary output component is the sum of absolute real and imaginary kernel
components, hence `2^ceil(m/2)`. The same holds for inverse signs. Dependent
translations can only lower this triangle upper bound when terms combine.

For a tensor-depth-`lambda` line use `m=lambda`, giving gain `X`. For the
rank-eight stage use `m=8lambda`, giving gain `Y`. Signed permutations have
gain one. Euclidean unitarity is **not** a unit bound for this norm. The
separate checker computes 1,020 Gaussian Fourier coefficients directly for
both signs and dimensions one through eight; this checks the formulas and
exhibits a physical counterexample to using gain one. The argument above,
rather than those finite examples, establishes all positive depths.

### 2. Exact error recurrence on the complete word

Assign a nonnegative polynomial `E_f` to each live field, initially zero. Its
coefficients multiply three formal error tolerances. For each literal event:

```text
ADD dst += c*src:  E_dst <- E_dst + |c| E_src + eps_add
signed line:      E_f   <- X E_f + eps_line
rank-eight stage: E_f   <- Y E_f + eps_stage
exact CLEAR:      E_f   <- 0
exact cover map:  E_f unchanged
```

The triangle inequality proves these rules by induction, without assumptions
on error signs or independence. A fresh temporal input has zero perturbation
relative to its reference; the retained banks are not reset. A private field
starts with zero difference and is checked to have zero error after its final
CLEAR. The same formulas apply to an arbitrary bounded error function across
owners and addresses.

`verify.py` scans every event in the byte-exact word. At each changed field it
checks coefficientwise domination by the appropriate displayed envelope. The
only nonzero monomials are `eps_add`, `Y eps_add`, `eps_line`, `X eps_line` and
`eps_stage`. The owned maxima are exactly `928, 784, 49, 392`; the borrowed
maxima are exactly the two unit coefficients in `(1+X) eps_line`. All four owned
maxima occur together at final `W0` **in this nonnegative recurrence**. This is
not a claim that physical errors attain every intermediate triangle equality,
or that the actual operator norm or minimum precision is sharp.

An independently written reverse sensitivity sweep starts at each of the
464 exit fields. For an ADD it sends `|c|` times the destination sensitivity
to the source; for a child it first charges that event's error and then
multiplies the incoming sensitivity by the child gain. Clears cut the
sensitivity path. It reproduces all 464 forward polynomials, including the
borrowed return and retired-bank rows. It does not import the forward checker
or any predecessor implementation.

### 3. Uniform tolerance and caller reserve

At positive depth, `X <= Y`. For a common error tolerance the owned expression
is `(1369+784Y) epsilon`, which also dominates `(1+X) epsilon`. Since `Y>=16`,

```text
1369 + 784Y <= (1369/16 + 784)Y = (13913/16)Y < 1024Y.
```

This proves the `4lambda+10` error-allocation margin. No finite-depth
extrapolation is used. PR2603's exact-prefix magnitude envelope can be combined
by the triangle inequality: under its additional entry assumptions, a
perturbed caller field has magnitude at most

```text
H*(48 + 48X + 144Y) + (1369 + 784Y)*epsilon.
```

This additional headroom is a conditional overflow-planning bound. It does not
supply recursive-child precision, F0/B1 entry bounds or a complete tape budget.

## Reproduce and evidence

Python 3.10+ and the standard library suffice. From the repository root:

```sh
python3 -I -O -B research/qq16-decoder-error-budget/verify.py
python3 -I -O -B research/qq16-decoder-error-budget/check_reverse.py
python3 -I -O -B research/qq16-decoder-error-budget/test_verify.py
python3.12 scripts/research_package.py --package research/qq16-decoder-error-budget
```

The first three commands also work from a copied package without Git or a
network. Default replay is read-only; receipt regeneration requires the explicit
`--write-result` option. The generic package hook additionally checks historical
Git provenance. [RESULT.json](RESULT.json) records exact coefficients, coverage
and table hashes. [SNAPSHOTS.json](SNAPSHOTS.json) binds the literal word and
reference contracts to Git blobs and SHA-256 hashes. Vendored Python is read
only as source evidence and is never imported or executed.

Checks include the complete word and all 224 output rows, all 464 reverse
polynomials, exact Fourier sums, a capture-before-stage versus post-child error
fixture, and a concrete signed-line echo with nonzero borrowed-return error.
Controls reject all four one-unit reductions in the claimed output polynomial
at actual prefix fields, four source corruptions, a changed/missing receipt,
and an invalid boolean child rank. Underclaim controls concern this triangle
certificate; they do not rule out tighter analyses of physical cancellations.

The selected baseline binding check passed at the pinned main commit. The
selected `make frontier1094-verify` cold replay, PR2540's complete native
admission replay, PR2603's prefix-grid replay, recursive child implementations
and a proof assistant were **not** run. Existing native correctness and input
contracts remain inherited. Two implementations written in one AI-assisted
session are algorithmic cross-checks, not an independent human review.

## Scope and source credit

This changes the `joint-query-controller` card to the specific approximate-call
obligation left by PR2603. It does not construct another controller or establish
a favorable complete supplier bill. The source word, invoice and selected
frontier are unchanged. The original draw, scope change and overlap limits are
in [TASK.json](TASK.json).

Credit **ywz65** for PR2540's complete native word and PR2603's exact caller
reserve and open error question; Ali Romman and the retained QQ16 lineage;
ywz65's PR2511/2512 composition; thakrarsagar/PR2470's L2 relation and
starship-s/PR2443's cut/F0 reconstruction. Source snapshots retain their text
and attribution. The norm and error-propagation lemmas are elementary; the new
result is their independently checked application to this complete word.
New material by **BigCactusLabs**, with substantial **OpenAI Codex** assistance
in derivation, implementation, validation and writing. Apache-2.0; see the
repository license and [inputs/NOTICE.md](inputs/NOTICE.md).

## Open next questions

1. **Supply an actual child error contract.** Start with one signed rank-one
   normalization and its inverse, at the perturbed input magnitudes above.
   This would make `eps_line` operational. Internal rounding, range and cost
   are the blockers; a caller tolerance alone does not discharge them.
2. **Propagate errors from the inherited F0/B1 calls.** Start with a separate
   input-error channel on the sixteen early and 224 current physical arrays,
   preserving their temporal relationship. This would extend the local result
   to a composed pair. Their actual output-error and retained-bank contracts
   remain missing here.
3. **Reduce the conservative amplification.** Start with the reverse `W0`
   polynomial and combine signed owner-labelled operators before taking norms.
   This may reduce precision costs. The current certificate deliberately loses
   cancellations, so it provides no sharp lower bound.
