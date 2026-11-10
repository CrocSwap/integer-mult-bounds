# Finite precompilation of a mixed-target rule

Status: constructive bridge under the precise native hypotheses below,
independently audited in `../transfer-audit/AUDIT.md`. This is a written
argument, not a formal proof or a completed integer-multiplication admission.
The companion finite scheduler checks actual integer flow and ordering.
The original immediate-normalization BIT interface failed hypothesis 3.
`../bit/DELAYED-COVER-BRIDGE.md` supplies the distinct delayed-cover
implementation, with a finite local-ring check and the native binding in
`../bit/BIT-P3-NATIVE-BINDING.json`. Its fixed rational cover routes are a
costed program schema, not dense coordinate gates in a plain native word.

Substantial OpenAI assistance. Apache-2.0. The mixed-target asymptotic flow is
Jacob Alan Sussman's Theorem 1G, PR4268, with the detailed proof at commit
`563b4e6e913625637f36ba7869bf5fcd0dd4975a` of
[`wht-power-saving-lean`](https://github.com/jacobalansussman/wht-power-saving-lean).
The source, exact scheduling code and notices are preserved under `sources/`.
The contribution proposed here is clearing the finite flow into a single
uniform native supplier before applying the inherited outer theorem.

## 1. What needs to be assumed

Let a job of rank `s` apply a specified tensor operator to `s` selected
coordinate blocks of one array, fixing all other coordinates. A block has
an arbitrary positive tensor multiplicity `f`. A completed rank `s` job
therefore acts on `s*f` axes. All productive inputs are arbitrary.

Fix one mixed unit with productive targets `W_k` of ranks `k`, a chronological
list of paid child ranks `r_j`, and a finite number of scalar and routing
passes. These assumptions are required, separately from the moment inequality:

1. **An all-column native word.** At every integer column count `c`, the unit
   computes exactly its independent rank `k*c` output jobs. Its paid rounds
   are rank `r_j*c` jobs in the stated order. All borrowed data return to the
   declared endpoint, and owned storage is explicitly initialized and erased.
   Its finite operation count is uniform in `c`.
2. **Disjoint splitting and spectators.** A rank `a+b` job is a rank `a` job
   followed by a rank `b` job on disjoint coordinates. The resulting programs
   preserve arbitrary complete spectator fields and accept arbitrary data.
3. **Whole-job adapters.** Any job passed between two units has an explicitly
   priced, permitted embedding into its destination. For the intended complex
   application these are fixed monomial binary address maps and unit quadratic
   phases, together with role permutations. The adapters must work at every
   tensor multiplicity. Rank equality by itself is insufficient.
4. **Finite-program closure.** A finite composition of these words and
   adapters is again a permitted finite supplier. Constantly many owned fields
   may be supplied with their full cost and no productive output credit.
   The eventual ordinary recursion must have the same arbitrary-input,
   restoration, scalar and precision interface as the retained supplier.

Put `m=max{k:W_k>0}`, `k_min=min{k:W_k>0}`, and
`r_max=max{r_j}`. Require `r_max<k_min`.

The hypothesis in item 3 is the material distinction between the two current
applications. The complex source supplies canonical Gaussian-dyadic jobs
after known monomial adapters. On the BIT side, a proper projector becomes
`g P g^-1` under the GL cover; immediately converting each one to a weighted
canonical query creates incompatible role-specific weights. The delayed
construction instead routes complete cover fibers `g -> g*S`, keeps one
external weight throughout the entire finite circuit, and lowers only its
final rank-one leaves. All rational matchers, role routes and their inverses
are fixed before choosing the odd prime and its exclusions. Every route
uses complete equal-multiplicity cover fibers and the retained, costed row
permutation primitive. This gives the same finite DAG argument in the
rational-cover program category. The BIT binding supplies the actual native
projectors; a rank count alone would not provide this implementation.

## 2. Proposed conclusion

Suppose the preceding hypotheses hold and the mixed balance has root
`tau` in `(0,1)`:

```
sum_j r_j^tau = sum_k W_k k^tau.
```

For every `z` with `tau<z<1`, there exists a finite **uniform** supplier with
some fixed ambient rank `N>=2`, a fixed number `B_N` of productive arrays,
and only rank-one paid children, whose number `P_N` satisfies

```
P_N < B_N * N^z.
```

Every productive output is the full rank-`N` job. The construction may have
an enormous finite scalar word, role inventory and owned-storage requirement.
Those quantities affect constants and the eventual input threshold. They are
not omitted and are not credited as extra output jobs.

If this uniform supplier is admitted under the retained native, precision and
fixed-tape premises, the existing uniform recursion applies directly. A new
dynamic RAM-to-Turing-machine simulation is not being assumed here.

## 3. The integer lockstep flow at a fixed rank

This is the part of Theorem 1G used by the compiler. At one fixed top rank
`N`, its units, source jobs and exit jobs have integer multiplicities.
For a multi-index `a` on the target types define

```
c(a) = product_k k^(a_k),
u(a) = multinomial(|a|;a) * product_k W_k^(a_k).
```

The exact Pascal identity is

```
u(b) = sum_{k:b_k>0} W_k*u(b-e_k).
```

Let `G` be the largest `|a|` with `m*c(a)<=N`. A class is indexed by a
sequence of paid rounds `s` of length `d<=G`; its dilation is
`rho_s=product r_j`. It contains `u(a)` units at column `rho_s*c(a)` for
each `a` with `|a|=G-d` and `m*rho_s*c(a)<=N`.

For one parent paid round, the Pascal bijection matches its job copies to
target roles of the child class, at exactly equal integer ranks. Missing
demands are top sources. Separation ensures every parent job is consumed.
The source ranks lie in `(N/m,N]`; only the deepest classes produce exit
jobs, all strictly smaller than `N` once `N` is outside the finite base range.

Process a class in word order. At round `j`, suspend every unit of that
class, complete the entire child class fed by that round, and only then
advance the parents to round `j+1`. This forbids a unit from requiring both
an earlier and a later round of the same suspended parent. The resulting
dependency graph is finite and acyclic. Its edges carry complete array jobs,
not individual scalar values copied for free.

These integer quantities exist before normalizing the sources to total
weight one. Let `S_s` be the number of source jobs of rank `s`, let
`S=sum_s S_s`, and let the ordered exit batches be `(e,t)` with `t` jobs
of rank `e` each. This finite integer flow is the compiler input.

## 4. Clear every batch denominator constructively

Induct on the integer top rank `N`. For each smaller rank `e` the compiler
has already constructed a uniform program on `B_e` arbitrary arrays,
computing full rank `e` with `P_e` paid rank-one calls. For a sufficiently
small rank use the ordinary sequential program: `B_e=1`, `P_e=e`.

For the current flow choose an integer `a` divisible by every `B_e` needed
for an exit and every `B_(N-s)` needed for a nonzero source remainder.
The product of those finitely many positive integers is a valid choice;
their least common multiple is a smaller optional choice. Set

```
B_N = a*S.
```

Assign `a*S_s` of the input arrays to each source rank `s`. On each of those
arrays, first complete its `N-s` complementary coordinates using the
already-compiled smaller uniform program. All such batches are integral
because `a` is divisible by their program widths. This preliminary action
commutes with the intended `s`-coordinate job and fixes its input coordinates.

Make `a` copies of the integer lockstep flow. Route its source arrays to
their exact input slots using permitted whole-array adapters. At a deepest
exit batch, `a*t` is divisible by `B_e`; replace that batch by copies of
the smaller uniform rank-`e` program. Restore its role ordering and adapters
before resuming the suspended parent class. Execute the finite DAG in the
lockstep order, and finally restore the original source-array ordering.

Every array has now received its disjoint complementary job and source job,
hence the full rank-`N` transform. No copied scalar input or blank helper is
treated as another independent output. Every original array occurs exactly
once as a source; interior target slots are jobs on those arrays, not new
productive inputs.

Induction removes all recursive calls: the only remaining paid children
have rank one. Clearing denominators multiplies productive arrays and paid
operations equally, so it preserves the per-array leaf count. In formulas,

```
P_N/B_N = (1/S) * [
    sum_s S_s * (P_(N-s)/B_(N-s))
  + sum_(ordered exit batches e,t) t * (P_e/B_e)
].
```

Zero-rank terms vanish. Any plain rank-one exits are the ordinary base
program. Scalar and routing passes have their own analogous nonnegative
count and must be included in the asymptotic cost used to choose `N`.

This construction uses full integer batches; it does not assume that
fractional pieces of a physical array can be routed at zero cost. Its exact
replication factors can be impractically large, which is acceptable for a
fixed finite supplier existence statement but must be disclosed.

## 5. Why some fixed N has the required saving

The independent audit sharpened this step to a direct count of paid leaves.
It does not require a running-time comparison between a RAM flow and native
tapes. Let `L(n)=P_n/B_n`, let `w_s=S_s/S`, and let `x_e` be the exit counts
normalized by the number S of source arrays. The actual integer compiler
satisfies

```
L(n) = sum_s w_s L(n-s) + sum_e x_e L(e),
sum_s w_s = 1,
sum_e x_e e^tau = sum_s w_s s^tau.
```

The last equality follows by canceling every internal matched job in the
exact tau-potential balance. The source ranks satisfy `n/m<s<=n`. Put
`theta=log(r_max)/log(k_min)<1`; the greatest exit rank is at most
`E(n)=r_max*(n/m)^theta`. Choose `tau<z0<z<1` and set `delta=z0-tau`.
Potential conservation yields

```
sum_e x_e e^z0 <= (m*E(n)/n)^delta * sum_s w_s s^z0.
```

That coefficient tends to zero. On the other hand, with
`eta=z0*m^(z0-1)>0`, concavity gives

```
n^z0 - sum_s w_s (n-s)^z0 >= eta * sum_s w_s s^z0.
```

Indeed, for `t=s/n` in `[1/m,1]`,
`1-(1-t)^z0 >= z0*t >= eta*t^z0`. For every sufficiently large n the
exit coefficient is less than `eta/2`. Every complement and exit has
smaller rank than n, so strong induction on the exact recurrence proves
`L(n)<=A*n^z0`, with finite A chosen to cover the smaller ranks. Eventually
`L(N)<N^z`.

This is an effective finite construction: enumerate N, generate its exact
integer recipe and count, and test the strict inequality. For rational
`z=a/b`, the final test is the integer comparison
`P_N^b < B_N^b*N^a`. The argument proves termination without requiring a
numerical estimate of A. It may still produce an astronomically large
template. The current work does not claim to have materialized the winning
near-threshold instance.

The result is materially different from rotating the same mixed roles
through every array once. Such a rotation replaces `sum W_k*k^tau` by a
smaller concave expression and does not retain the mixed saving. The
hierarchical split, source supply and exit recursion are essential here.

## 6. Tensor lift, owned storage and physical costs

The precompiled rank `N` and every role/axis index are constants of the
eventual program. Replace each one of its coordinate axes by `f` axes.
Every rank-one leaf becomes the ordinary rank-`f` child. A fixed coordinate
permutation becomes a fixed block permutation. Native binary monomial maps
and quadratic unit phases lift column by column, with their exact absolute
phase raised to the tensor multiplicity. The logical scalar program itself
is not tensor-powered; it acts on the same fixed list of role arrays.

Different suspended units may simultaneously retain live owned centers.
One owned `C0` per recursion depth is therefore insufficient in general.
The safe finite allocation is one owned center bank per live unit instance,
or even per compiled unit instance. Retain each bank until its unit clears
it. All are excluded from `B_N`, and all initialization, scalar operations,
movement and erasure remain in the fixed scalar cost. A smaller reuse
allocation requires its own lifetime proof.

An owned center can be the physical field of a paid round. If its parent
has just copied a nonzero linear combination into that center, its child
receives that very field as one of its productive slots. Arbitrary-input
child correctness applies equally to this correlated value. The child does
not create a new independent source for that slot, and its own center has
a different unit tag. Its other, missing source slots are supplied by the
distinct top-level arrays counted in S. The parent resumes, reads or erases
its center only after the entire child unit has completed. Thus COPY never
duplicates an independent productive input, and a clear never acts on a
descendant's live storage. These are field-identity and chronological
requirements; statistical independence of current values is not required.

Once the word is finite, the original depth-first fixed-tape recursion can
reserve its fixed number of role/work tapes and use the usual parking stack.
At one ordinary recursive node the number of child calls and stored fields
is a constant, possibly enormous, so its actual scans contribute a fixed
multiple of logical volume. This statement still requires the admitted
primitive implementations for the fixed address/phase operations; it is
not permission to treat an arbitrary address permutation as a linear pass.

The new finite scalar count, frame matrices, role count, denominator heights,
prefix norms and center inventory replace the old constants in the retained
semantic precision and row-stock bounds. The strict child ratio is `1/N`.
Fixed huge constants can be absorbed in an eventual threshold, but only
after that substitution has been written. An old scalar cap cannot be reused
merely because the exponent calculation is favorable.

## 7. Present applications and separate bindings

The strongest retained complex tariff is the p3, keep-mask43 construction
in `P3-CONTROLLER-TARIFF-CERTIFICATE.json`. Its productive target ranks are
`{6:192,7:56,8:93,9:1229,25:448,57:224}` and its complete paid profile is
`{1:17623,2:5065,3:1738,4:714,5:254}`. Its exact mixed-root bracket is
`[0.002305090194876170622919094755,
  0.002305090194876170622919094756]`.
The construction uses the full-identity suppliers and does not depend on
the separate H-monodromy research. The preceding p2 and prefix-cut
certificates remain preserved as independently reproducible earlier stages.

The following are separate, necessary bindings rather than consequences
of the moment inequality:

- all global owner fields, residual idle axes and whole-helper adapters;
- constant THREE/base selection, or the exact alternative dispatch;
- every whole-job normalization used at a mixed class boundary;
- all-column/tensor lift of the resulting complete word;
- the owned-center inventory and updated scalar/precision/stock constants.

For BIT, the actual p3 word is bound in `../bit/BIT-P3-NATIVE-BINDING.json`;
its targets are `{8:3073,22:444,50:222}` and its paid profile is
`{1:9261,2:9394,3:553,4:308,5:714,6:77,7:1465}`. The delayed whole-cover
proof and its receipt bind the whole-fiber matching and final-leaf
normalization. The ordinary two-call wrapper and its row-stock allowance
must still be charged in the outer transfer. This note proves the finite
compiler implication; the repository's separate outer-parameter receipt
is where the common integer-multiplication exponent is checked.
