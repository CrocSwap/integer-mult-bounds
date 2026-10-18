# Sharp endpoint accumulation for the balanced dirty word

**All-size local precision lemma; no new supplier or κ.** For the unchanged
PR628 balanced dirty commutator, arbitrary additive defects introduced at the
actual destination of **every** completed leaf have a sharp endpoint target
coefficient

```
T(1)=1,       T(n)=T(floor(n/2))+2 T(ceil(n/2)).
```

If every ordered subset product of the ideal factors has norm at most `G>=1`
and every defect has norm at most `epsilon`, the completed target error is at
most **`T(n) G epsilon`**. No commutation is needed. The coefficient `T(n)` is
sharp for independent defects already with scalar identity factors (`G=1`).
For `n=2^h`, it is **`3^h`**, although the unchanged paid word has `4^h` leaves.
This is neither a reduction in paid calls nor a statement about arbitrary
intermediate cuts.

We also give the exact coefficient for every restored scratch register in this
independent-defect model. At `n=8`, the target coefficient is **27**, but the
largest scratch coefficient is **32**. Do not use the target count for the
whole state. Actual rounded-leaf defects may be correlated and may restore
scratch exactly; sharpness here is for independent additive defects, not for
a particular deterministic numerical kernel.

A conditional substitution into Philipp/mightyOil's PR1295 precision theorem
for Ali Romman's **PR1054** leaf contract gives **1,162,598 → 1,162,590 fractional
bits** at its radix-64 example. The separate interior feedback requirement is
retained, not inferred from endpoint accuracy. The 1,291,709 signed integer
bits, 516,499 factor bits, 4,000 leaves and six dirty arrays stay unchanged.
This modest eight-bit comparison is to that exact contract; it is not a
comparison to PR905/1085's different numerical leaf budget or a production
precision change. The main result is the exact all-size endpoint response law.

## Precise theorem

Let `A_0,...,A_(n-1)` act on one normed vector space. Use distinct registers
`x,y,z_1,...,z_h`, `h=ceil(log2 n)`, with the same depth scratch shared by
siblings. An ideal leaf is the shear `y += s A_j x`, `s in {-1,+1}`. A positive
nonleaf splits at `l=floor(n/2)`, `r=n-l`, and executes chronologically

```
U, V, U^-1, V^-1,
U: z_1 += B x,       V: y += A z_1,
B=A_(l-1)...A_0,     A=A_(n-1)...A_l.
```

The negative word is the literal inverse, `V,U,V^-1,U^-1`, with the child's
full instruction order reversed when its sign is negative. Every full child
restores its deeper scratch in the ideal linear model. The complete parent
map is `y += s AB x`, with all other registers restored.

After leaf `k`, add an arbitrary vector `e_k` to its destination **only**.
For the fixed realized error vectors, linearity gives the endpoint error

```
Delta = sum_k S_k J_(d_k) e_k,
```

where `S_k` is the ideal suffix strictly after leaf `k` and `J_(d_k)` injects
one register. This identity also holds when the `e_k` were produced by a
nonlinear actual trajectory: first fix that trajectory, then use its actual
leaf defects. No independence, randomness or unbiasedness is required for the
upper bound. Arbitrary independent choices are used only to prove sharpness.

**Endpoint response law.** Each entry of `S_k J_(d_k)` is zero or one signed
monomial whose factor indices are strictly decreasing. Let `C(n)` count the
nonzero responses to each endpoint row, in order `(x,y,z_1,...,z_h)`. For both
word orientations,

```
C(1) = (0,1),
C_x(n) = 0,
C_y(n) = T(l) + 2 T(r) = T(n),
C_z1(n) = 2 T(l),
C_z(k+1)(n) = 2 C_zk(l) + 2 C_zk(r).
```

Missing deeper coordinates of a child contribute zero. In particular, if all
ordered subset products (including the empty product) have norm at most `G`,
then for every row `i`

```
||Delta_i|| <= G sum_(k: response_i,k != 0) ||e_k||
            <= C_i(n) G epsilon.
```

The sharper first inequality allows nonuniform leaf bounds. Its response
monomial norms can also be used individually instead of the common `G`.

### Proof by the four completed-child phases

The leaf case has one identity response on its target. Suppose the statement
holds for both children. Consider one error occurring inside one child phase,
and propagate it first to the end of that phase. The induction hypothesis
says its source component is zero; its target and deeper components are signed
ordered monomials. Propagate this vector through the **completed ideal** later
children. These complete maps fix every deeper connector, even though sibling
executions reuse those connectors internally. Thus there is no fresh-scratch
assumption and no ignored intervening execution.

The child's target error has the following further transport. The table lists
its contributions to the parent connector and parent target; every deeper
component simply remains in its own register.

| Parent word | Phase | Child | Parent `z_1` coefficient | Parent `y` coefficient |
|---|---:|---|---:|---:|
| positive | 1 | `U` | 1 | 0 |
| positive | 2 | `V` | 0 | 1 |
| positive | 3 | `U^-1` | 1 | `-A` |
| positive | 4 | `V^-1` | 0 | 1 |
| negative | 1 | `V` | 0 | 1 |
| negative | 2 | `U` | 1 | `-A` |
| negative | 3 | `V^-1` | 0 | 1 |
| negative | 4 | `U^-1` | 1 | 0 |

For example, a positive phase-1 connector error is added to `y` by the later
`V` and subtracted by `V^-1`; `U^-1` changes it only by a multiple of the zero
source error. A phase-3 connector error meets only `V^-1`, so contributes
`-A` to `y`. The negative table follows from its explicitly reversed order.

There is at most **one route from this child's error response into any parent
row**: a left-child target can reach `z_1` and, in one phase, `y`; a right-child
target reaches only `y`; deeper components remain deeper. Hence no sum of two
monomials appears in one response entry. Multiplication by `A` prepends the
complete right block to a left-block monomial, so all indices remain strictly
decreasing and disjoint. Different leaf defects are distinct channels, so
counting the nonzero channels in this table yields exactly the displayed
recurrences. This proves the response law for every n and both orientations.
The norm inequalities now follow by the triangle inequality and the ordered
subset-product premise. Finite replay is not the all-size proof.

For sharpness at a chosen output row, take all `A_j=1` on the real line and
choose each `e_k` to equal the sign of that row's response, or zero when it has
no response. Every contributing term is then `+1`, attaining `C_i(n)`. These
are admissible independent destination defects of norm at most one.

### Closed form at powers of two

Induction gives, for `n=2^h`,

```
C_y = 3^h,
C_zk = 2 * 4^(k-1) * 3^(h-k),       1 <= k <= h.
```

The whole-state coefficient is `max(3^h,4^h/2)` for `h>=1` (and one at h=0).
For h>=3 it is `4^h/2`. Thus the subquadratic target coefficient must not be
relabeled a subquadratic whole-state independent-error bound. The exact all-n
recurrence, rather than an extrapolation of the power-of-two examples, is used
in the verifier.

## Conditional precision consequence, with the full budget

Keep an available leaf-boundary prefix bound `B`, an **interior** interval
bound `L`, initial norm bound `D`, and a valid bound for each actual signed leaf

```
||e_k|| <= a u (M_actual+1),       u=2^-W.
```

A negative leaf needs its bound at the correct positive preimage, as explained
in PR1295 §2; merely negating a rounded formula is not a replacement proof.
Stable closure, source restoration, actual finite execution and all internal
leaf bounds remain premises. The existing variation-of-constants argument gives

```
t = N L a u,
M_actual <= B D + t (M_actual+1).
```

**Require `t<=1/2` separately.** Then `M_actual<=2BD+1`, and this package's
endpoint result gives the target execution error

```
E_target <= 2 T(n) G a u (B D+1),
```

instead of the retained `2 N L a u (B D+1)`. No smaller interior amplification
is asserted. For `D<=2^m`, `G<=2^K`, `B<=2^J`, `L<=2^H`, `a<=2^A`, a sufficient
fractional width for `E_target<=2^(-p-1)` is

```
W = max(w_input, inherited_closure_width,
        1 + ceil(log2 N) + H + A,
        p + 3 + ceil(log2 T(n)) + K + A + m + J).
```

All logs of integers are computed by exact bit lengths. This formula never
coarsens incoming grids. The endpoint inequality alone does **not** imply
feedback: at n=1024 with contraction budget `G=1`, `B<=16`, `L<=256`, `a=1`,
`D<=1`, `p=0`, the accuracy term is 23 but feedback requires 29. The semantic
control rejects the 23-bit substitution.

The radix-64 receipt uses exactly the PR1295/PR1054 constants: n=63,
`N=4000`, **`T=727`**, `K=258274`, `J=258277`, `H=258280`, and its own
`A=5g+ceil(log2(68(r+1)))`. The old/new accuracy terms differ by
`ceil(log2 N)-ceil(log2 T)+H-K = 12-10+6 = 8`. Closure and feedback still pass.
PR1295's internal inverse-preimage reserve, root preparation, complete per-leaf
and data-record movement costs are unchanged. Its conditional complete bill
remains preparation plus `O(N M_len M(Aword+Bdesc))` arithmetic and
`O(N(h+2) M_len (Aword+Bdesc))` movement, with all N calls including restoration,
all immutable descriptor/source access, and `Aword=W+I`. This changes no calls,
register allocation, paid recursive rank profile, asymptotic cubic precision
order or multiplication exponent. The analytic factorizer and numerical leaf
hypotheses are reused, not independently proved or executed here.

## Reproduce and evidence

Python 3.12, standard library only, from repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/dirty-endpoint-error-accumulation/verify.py
uv run --python 3.12 --no-project python -I -O -B research/dirty-endpoint-error-accumulation/test_verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/dirty-endpoint-error-accumulation
```

The mathematical marker is `PASS_DIRTY_ENDPOINT_ERROR_ACCUMULATION`.
`RESULT.json` is compared in full; normal replay is read-only. Explicit
`--write NEW_PATH` is authoring mode and refuses overwrites. Compressed archives
are not generated or compared. `SOURCES.json` binds every external proof input
with Git blob and SHA256; `VERIFY.json` declares the full input set.

The evidence package checks:

- All endpoint response entries for n=1..32,63,64,65,127,128, both orientations,
  against the exact all-size count recurrence and complete product endpoint.
  It executes the unchanged pinned `compose` AST with instrumented leaves,
  rather than importing its unrelated numerical dependencies.
- Ordered free-algebra suffix propagation, with no commutative, squarefree or
  involutive quotient. A separate **forward** error-symbol engine checks every
  response for n=1..8. Noncommuting 2-by-2 rational contractions distinguish
  left/right multiplication and deliberately reversed factor order.
- Simultaneous signed-error witnesses for both the target and maximal endpoint
  row, and exact power-of-two recurrence evaluations through h=20. Large h is
  recurrence evidence, not an expanded literal word.
- Seventy-two deterministic rounded **model-leaf** executions on the actual
  dispatcher, using rational contractions and nearest rounding, including
  nonzero errors, arbitrary dirt, both orientations, restoration and literal
  inverse cancellation. These are not executions of PR628/PR1054 numerical
  cyclic-inverse kernels and do not instantiate the million-bit example.
- Negative boundaries for omitted restoration, incorrect inverse chronology,
  aliased scratch, source rather than destination error, understated target
  count, target count reused for scratch, endpoint bound reused at an interior
  cut, noncontractive factors with G=1, dropped feedback and source corruption.

Final local replay passed on macOS arm64, **CPython 3.12.12**:

```text
PASS_DIRTY_ENDPOINT_ERROR_ACCUMULATION leaf_occurrences=114350 T63=727 conditional_fractional_bits=1162598->1162590 no_new_kappa
Ran 7 tests ... OK
FORWARD_FREE_IMPULSES 430
NONCOMMUTING_REVERSED_ORDER_REJECTIONS 12
PASS_REGISTERED_RESEARCH_PACKAGE research/dirty-endpoint-error-accumulation outcome=completed
```

The exact early-cut control is n=4, factors `(-1,-1,1,-1)`, cuts `[3,5)`,
with destination-supported unit input yielding state `(0,0,1,2)`. It rejects
using the endpoint single-response bound one at arbitrary intermediate cuts.
There were 36 rounded model fixtures, each also reversed: 72 executions.
No selected cold replay, native/physical compiler admission, complete
transform, Lean or hosted CI success is claimed.

## Provenance, overlap and credit

Base: `e112d71c8d7bb32435debcc54df932593dd8223a`. Full chooser output in
`SELECTION.json`: independently drawn nonce
`dc96b7ed19e1045ea40350f775120d39`, adversarial-audit / uniform-transfer-audit,
priority revision 3. [The scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931183)
and TASK card preceded the experiments. The selected κ remains
`0.001672660197076918`; the complex supplier still binds.

Credit Chafik Boukhalfa for PR628's dispatcher (head
`0768f97d06c623b8211e651543c66135796b62bf`) and PR862/905;
Hanson Sun for PR1085's prefix/inverse-prefix invariant (head
`82b99c7d12dac009d35636562df4c6c91e885409`); Charles Bethin for PR1278
(`06b8c006891ae78abe24b30d2fe9d8c188deafe8`) and the single-register interval
corollary; Arham Tahir for PR1374's quadratic joint-error boundary; woklerx
for PR1855's finite destination-column census
(`ef1e0a8bd94aa37cb2ecf5ea88081b7457370f3b`); Philipp/mightyOil for PR1295
(`3a6773708f0d73f7dbee164f4c6e7658b0b41509`); Ali Romman for PR1054/985;
and Gareth Davidson/PR877, 0xkilgore/PR663 and the retained numerical lineage.
All consumed bytes are pinned at the base; no predecessor file is changed.

PR1855 explicitly excludes error accumulation and all-size extrapolation.
The single-register corollary gives an `(h+2)G` interval bound but not this
sharp cumulative endpoint count. PR1295 reduces commuting interval transport
and separately retains inverse-preimage costs; this package does not claim
priority for either step. The new result is the all-size, both-orientation,
all-row endpoint response recurrence and its output-only accuracy substitution.

The shared overlap snapshot covered 329 open PRs including drafts (2026-10-14
18:11:09.770757Z) and 692 Discussions with comments/replies
(18:12:32.610168Z), complete pagination. Cached targeted searches and local
merged predecessors were inspected. Open titles alone and no-match searches
are not novelty certificates. At **2026-10-14 18:29 UTC**, targeted live API
reads confirmed those PR1855 and PR1295 heads, both merged, with the same
explicit finite-versus-accumulation and conditional-precision boundaries.
A live search for PRs containing both `accumulation` and `precision` returned
30 records with `incomplete_results=false`; the nearest mathematical hit was
PR1430's different Gaussian/Neumann recurrence, already represented locally.
No matching balanced-word endpoint recurrence was identified. This is a
bounded search, not complete live comment/diff coverage or a priority claim.

Prepared by **Adam Gall (@adamgall)** with substantial **OpenAI Codex**
assistance in source research, proof, implementation, verification and writing.
No subagents or independent human review are claimed. New material is
**Apache-2.0**; source attribution is retained.

## Open next questions

1. **How much tighter are the realized correlated defects of one numerical
   kernel?** The independent-defect coefficient is exact but may be conservative
   for reversible rounded leaves. First bind the actual PR1054 leaf evaluator
   and record its defect correlations on one complete small word. A valid
   all-size correlation invariant, not empirical cancellation, is the blocker.
2. **Can an output-specific budget be admitted by a real caller?** This would
   test whether the local improvement is useful beyond a lemma. First retain
   the original internal/inverse-preimage reserve and regenerate one caller's
   complete arithmetic, precision and movement invoice at the new W. Analytic
   preparation, physical/compiler realization and full caller replay remain
   blockers; this package changes no production reserve.
