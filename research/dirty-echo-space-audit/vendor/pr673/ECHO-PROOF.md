# Multiway dirty echo: fewer factor calls with logarithmic borrowed storage

This changes PR628's **binary composition schedule**, retaining its classical
rounded inverse leaf, coefficient preparation, charged phase access and routing.
For each fixed fanout k >= 2 it uses O(n^alpha) factor calls, where
alpha = log_k(4k-4) < 2 for k > 2, with O(log n) borrowed length-L arrays.
It does not provide a common-label Clifford supplier, bit-reversible compiler,
transform layout, or new multiplication κ. The phase-alias repair is required
at this interface too and is included in `echo.py` before execution.

## Exact algebra; no commutativity assumption

Let A_1,...,A_k be arbitrary composable linear maps on equal-length arrays.
Source x, target y and dirty arrays z_1,...,z_(k-1) are all distinct. Define C
as the following ordered sequence of shears:

    z_1 += A_1 x
    z_2 += A_2 z_1
    ...
    z_(k-1) += A_(k-1) z_(k-2)

Define D as C with its first shear omitted. Execute

    C; y += A_k z_(k-1); C^-1;
    D; y -= A_k z_(k-1); D^-1.

C^-1 and D^-1 reverse the operation order and negate every shear. They restore
all dirty arrays. The two target updates occur on dirty-chain states that differ
only by the propagated contribution of the first link. Inductively that
difference at z_i is A_i ... A_1 x. Consequently the net target increment is
A_k ... A_1 x. This proof holds for noncommuting maps and arbitrary initial dirt.
The source is never a target of an ideal shear. With k=2, D is empty and this
reduces to the original binary commutator.

The complete count is

    (k-1) + 1 + (k-1) + (k-2) + 1 + (k-2) = 4k-4.

It includes both ladders, both inverse ladders and both target updates. There
is no clean length-L work array or implicit copying. The two endpoint maps
are each called twice; each interior map is called four times.

## Recursive schedule and storage

Partition n factors into k' = min(k,n) consecutive groups, as evenly as
possible, preserving their order. Use k'-1 dirty arrays for this node. Recursively
implement each group map using a disjoint pool of deeper borrowed arrays,
which can be reused between calls because every call restores that pool.
Neither an ancestor source nor an ancestor target belongs to the deeper pool.
All mutable arrays, including surplus scratch, are checked distinct at entry.

For group sizes n_i, the exact recurrences implemented by `resources` are

    S(1) = 0, N(1) = 1
    S(n) = k'-1 + max_i S(n_i)
    N(n) = 2 N(n_1) + 2 N(n_k') + 4 sum_(1<i<k') N(n_i).

For n=k^h these give S=(k-1)h and N=(4k-4)^h. In general depth is at most
ceil(log_k n), so S <= (k-1)ceil(log_k n) and
N <= (4k-4)^ceil(log_k n). For fixed k this is O(n^alpha),
alpha=log_k(4k-4). The constant in O(log n) borrowed storage depends on k.
One must not increase k with n while claiming that constant is uniform.
For every fixed epsilon>0, a sufficiently large *fixed* k makes alpha<1+epsilon.
The flat choice k=n instead uses n-1 borrowed arrays and exactly 4n-4 calls.

| Factors | Binary: arrays / calls | Fanout 8: arrays / calls | Flat: arrays / calls |
|---|---:|---:|---:|
| 8 | 3 / 64 | 7 / 28 | 7 / 28 |
| 16 | 4 / 256 | 8 / 112 | 15 / 60 |
| 64 | 6 / 4096 | 14 / 784 | 63 / 252 |
| 512 | 9 / 262144 | 21 / 21952 | 511 / 2044 |

The generator streams instructions using O(k log_k n) active scheduling
records. It does not retain the expanded word. A positive or negative child
call takes the same resources. Negative calls reverse the full instruction
word, rather than negating signs in forward order.

## Exact restoration despite rounded, nonlinear increments

A valid PR628 leaf adds a deterministic function of its source to its target,
restores its source exactly, and does not read its target when computing the
increment. Its negative leaf subtracts exactly that same grid value. Fixed,
non-aliased phase and factor data are essential here.

Inductively, a recursive call adds a deterministic function of its source and
initial deeper dirt, independently of its target, and restores the source and
all deeper dirt. Thus C's child calls can be undone in reverse order: each sees
the same source and deeper dirt as its forward mate. The intervening target
update changes only y, which is excluded from every ladder's scratch pool.
The same argument applies to D. This proves exact source and scratch restoration
at every level for valid finite-grid inputs. Reversing the complete word gives
an exact inverse. It does **not** prove that the rounded target increment is
independent of dirt; the error estimate below bounds that dependence.

As with the pinned leaf, all input contracts must hold throughout execution.
This is not transactional rollback on arbitrary malformed coefficients or
stateful callbacks. The explicit alias checks reject ordinary list-identity
aliasing before any mutation; arbitrary overlapping views are outside the API.

## Complete inherited error and cost budget

Use PR628's leaf estimates with n=r-1, beta in (0,1], grid u=2^-w, and
multipliers bounded by r. The same hypotheses and preparation remain required.
Let D bound the initial joint max norm, K=r/beta,
a=13(r+1)/beta^3 and G=2+K. A rounded leaf on input norm at most B has error
at most a(B+1)u; an ideal shear has Lipschitz norm at most 1+K. Enforce
au<=1 and u<=beta^2/2.

Writing M_j for the computed joint norm after j leaves gives
(M_j + 1) <= G^j(D+1). Comparing the complete rounded instruction word with the
complete ideal word gives, by propagation through each remaining ideal shear,

    E_N <= N a (D+1) u G^(N-1).

This argument applies to the actual expanded word, including every restoration
operation. Substitute the new exact N; do not reuse the predecessor's 4n²
upper bound when measuring the improvement. The ideal identity proved above
cancels all initial borrowed dirt. Hence this E_N bounds target error while
actual source and scratch restoration are exact.

For requested p bits choose

    w >= p+1+ceil(log2(N a (D+1)))+(N-1)ceil(log2 G),

as well as the two leaf precision conditions. This budgets execution error
at most 2^(-p-1). The inherited coefficient/phase preparation error must still
be budgeted to 2^(-p-1), scaled for the original source norm as specified in
PR628. It does not receive a free exact phase table from this construction.

Under PR628's log2(beta^-1)=O(r³), fixed fanout k gives

    N = O(r^alpha),
    w = O(p + log(D+1) + r^(3+alpha)).

Joint transient integer magnitudes add O(log(D+1)+N log G) bits; the leaf's
causal state and closure add O(log(beta^-1)+log r), all covered by that budget.
Borrowed data storage is O(L log r) words for fixed k. Clean arithmetic storage,
read-only factor descriptors, indexing and fast-arithmetic workspace retain
PR628's qualifications. Charging the same factor preparation and leaf arithmetic
as PR628 gives the conditional local work upper bound

    soft-O((L r^alpha + r³) (p + log(D+1) + r^(3+alpha)))

plus charged phase-oracle and routing work. Every leaf still includes its
forward pass, output pass, undo pass and validation/access costs; none are
removed by a speedup claim. With k=8, alpha=log_8 28≈1.602452, replacing the
binary precision power 5 by about 4.602452. With flat k=n the corresponding
power is 4, but borrowed arrays become O(r), not O(log r).

The Fraction prototype tests identities, rounding and restoration; its timings
are **not** evidence for a fast fixed-precision implementation. No complete
multiplication recurrence follows without integrating the required transform,
paid storage/layout, bit supplier and all conditional assembly assumptions.

## Evidence and attribution

`verify_echo.py` compares the streamed ideal word against direct composition of
arbitrary noncommuting 2x2 integer matrices. It separately compares rounded
execution with an integer-grid arithmetic interpreter (sharing only the tested
schedule), and with PR628's independently assembled dense cyclic inverse oracle.
The latter checks the complete error bound at a precision chosen by the formula
above, with positive, zero and negative initial dirt. These finite tests support
the implementation; they are not a formal proof of the general statement.
The algebraic and inductive arguments above state the general obligations.

The schedule and analysis here were prepared for @androolloyd with substantial
OpenAI Codex assistance, under Apache-2.0. The rounded leaf and original binary
dirty inverse are Chafik Boukhalfa / chafreaky's PR628 work, with OpenAI Codex
assistance, built on Ali Romman's PR621 kernel and the sources retained in
SOURCE.json. This note claims an improvement relative to that pinned binary
schedule, not priority over all historical reversible-pebbling literature.
