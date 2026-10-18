# Phase accumulation: exact stateful closure, failed recursive budget

**Author-checked exploratory result; no new kappa or selected supplier.** A
Pauli phase accumulator supplies a quadratic Fourier phase on arbitrary joint
data. Its scalar identity does not justify using one fixed bank for an entire
batch: that substitution produces unwanted cross-column terms. A tensor bank
works, and a single bank also works when consumers unwind producers in reverse
order. Both corrected contracts are implemented here, including their returns.

The resulting two-operation recursion is exact through two levels, but its
optimistic recursive bill is critical before paying its wrappers. This closes
this candidate's construction round. The reusable delta is an explicit
tensor-versus-shared-state comparison, a working reverse-order contract, and a
testable budget gate for successors—not a new representation-theory theorem.
The canonical investigation is [Discussion 2842](https://github.com/CrocSwap/integer-mult-bounds/discussions/2842).

## Assignment and candidate choice

The donor assigned up to five hours to seed a different research direction:
compare three stateful interfaces, choose one, require actual two-level
composition, and include state size, movement and final restoration. This
overrides random task selection. [TASK.json](TASK.json) records the changed
`connector-alphabet-change` scope and stopping rule.

| Candidate | Entry evidence and decision |
|---|---|
| Cyclic or changing-reader carries | PR1287, PR1391/1410, PR1439/1506 and `unipotent-return-seed53` already contain local identities or finite-depth contracts. No distinct supplier reduction identified. |
| Source/output borrowing and accumulation | PR1057/1164, `mutable-source-port-borrowing`, dirty-output anchors and in-place accumulation are close predecessors. Borrowing alone would repeat their premise. |
| Noncommuting phase accumulator | Chosen to test whether a useful scalar quadratic phase survives tensor lifting with a paid, recursively composable implementation. |

The one bounded pivot was from a fixed bank to existing spectator address bits
as the bank, with every change of basis charged. The corrected fixed-bank
schedule below is a scope control, not a second construction campaign.

## Exact objects and ownership

All maps are classical linear maps on arrays of arbitrary complex numbers.
Let `x,y` be disjoint `f`-bit address blocks and `u,v` their Fourier labels.
Other address bits are spectators. Define `Q_f` by the Fourier multiplier
`(-1)^(u dot v)`. Its physical kernel on each spectator fiber is

```text
Q_f[(x',y'),(x,y)] = 2^-f (-1)^((x' xor x) dot (y' xor y)).
```

A bank with address `c` has independent arbitrary coefficients at every lane;
there is no prepared state, zero input, separability assumption or discarded
column. `I_bank tensor Q_f` preserves the bank coordinate while applying Q to
every lane's data. It does not promise to leave a separate dirty helper array
unchanged. All bank lanes count in the operand volume `N`. The same full `N`
is charged to each child even when that child acts on fewer address axes.

The referenced complex kernel from the pinned
[`05-layers.tex`](../../upstream/build/sections/05-layers.tex) is

```text
a=(1+i)/2, b=(1-i)/2, C=[[a,b],[b,a]], C_n=C tensor n axes.
C^2=X, C^-1=-i Z C Z.
H0=(1/2)[[1,1],[1,-1]]=b S C S, S=diag(1,i).
```

`H0` is dyadic and its inverse is literal, including the inverse scale. No
irrational normalization enters the programs. All phases, translations, chart
changes, scales and inverse wrappers appear in [model.py](model.py).

## Producer and consumer contracts

On a bank `c in F2^f`, set `Z(u)|c>=(-1)^(u dot c)|c>` and
`X(v)|c>=|c+v>`. The producer executes a bank-controlled translation of x,
then `H0_bank`, a bank-controlled translation of y, and `H0_bank^-1`.
Its Fourier-bank operator is `P(u,v)=X(v)Z(u)`; a consumer with the same labels
executes the same word. Thus `P(u,v)^2=(-1)^(u dot v) I`.

Entry type R is the original physical frame. The producer returns type P,
including its source-label association; the paired consumer accepts exactly
that state and returns type R with Q applied. A child cannot silently treat
type P as restored. The independent physical formula for the open producer is

```text
x'=x+c,
coefficient = 2^-f (-1)^((c'+c) dot (y'+y)).
```

Replacing the tensor bank by one bit and aggregating the labels computes
`(-1)^((xor_j u_j)(xor_j v_j))`. For `f=2, u=(1,0), v=(0,1)`, the required
phase is +1 and this phase is -1. The full physical counterexample is recorded
in [RESULT.json](RESULT.json). Positive contracts are checked on every joint
input column, including all nonzero bank coordinates.

There are two correct shared-bank continuations. Close each scalar column
before the next one, or execute the chronological sequence

```text
P_0 P_1 ... P_(f-1) P_(f-1) ... P_1 P_0.
```

Adjacent identical innermost words square to their scalar phase, so the latter
sequence returns the bank only at the parent boundary. It works on arbitrary
joint input and retains unfinished state across child boundaries. Using the
same producer order for the consumers instead fails at f=2. The literal
reverse-order program has `4f` one-axis C calls, plus its wrappers. This is a
cost of that program, not an optimality claim for all interleaved schedules.

The state-return types R/P and the recursive operation types C/Q below are
distinct contracts. To connect them explicitly, the f=3 tensor-bank fixture
substitutes the C/Q recursion into all four bank basis changes. Every one of
its 512 joint input columns is checked both at the open P boundary and after
the consumer returns. Twelve one-axis C leaves execute on the entire
512-cell array, including the bank's live arbitrary state.

## The restricted bank-size bound

Here is the standard Pauli/finite-Heisenberg representation argument applied
to the proposed batched interface. Suppose A and B are group homomorphisms
from `(F2^f,+)` to `GL_d(C)` and

```text
A(u) B(v) A(u)^-1 B(v)^-1 = (-1)^(u^T M v) I_d.
```

If M has binary rank r, then **`2^r` divides d**. Choose r pairs of labels
with pairings `u_i^T M v_j=delta_ij`. The commuting involutions `A(u_i)`
have simultaneous sign eigenspaces indexed by `F2^r`. Each `B(v_j)` maps
one eigenspace bijectively to the space whose j-th sign is flipped. All
`2^r` spaces therefore have equal dimension, proving divisibility. Neither
irreducibility nor unitarity is assumed.

For q *closed separable commutator blocks* on a fixed d-dimensional bank,
producing `M_1+...+M_q=I_f` consequently requires

```text
f <= sum_j rank(M_j) <= q v_2(d).
```

Partitioning columns attains `q=ceil(f/b)` for `d=2^b`. A conjugation of the
bank basis does not change the bound. The bound does **not** cover arbitrary
interleaved open states; in particular it does not exclude the correct shared
bank reverse-order program above. The exact finite census checks all 530
binary forms of sizes 1, 2 and 3, 33,032 source-label pairs, every coordinate
of their rank-factorized Pauli banks, and 64 sharp partition examples. It
illustrates the written all-size proof; it is not its substitute.

## Actual recursive closure and the budget gate

Borrowing f spectator address bits avoids adding data lanes, but a bank basis
change is then a real f-axis operation. The literal tensor-bank commutator
uses four C_f calls. A stronger ordinary implementation uses only two:

```text
Q_f = H0_x P_(x,y -> x,y+x) H0_x^-1.
```

There is also a one-call implementation of *width 2f*: with
`D(x,y)=(-1)^(x dot y)`,
`Q_f=D Swap (2^f H0_(2f)) D`. The scalar reduces exactly to `(-i)^f`
when H0 is expanded through C. Both implementations are checked. One named
call of width 2f has not saved the total child width.

For original Fourier bits `(a,b,c)`, put `p=a+b+c, u=a+c, v=b+c` over F2.
Per column,

```text
a+b+c (as an integer) = p + 2(ab+ac+bc) mod 4,
ab+ac+bc = uv+c over F2.
```

This yields `C_(3f)` from one C_f on p and one Q_f on (u,v), plus a chart
and a sign translation. The physical chart is `L^-T` for the displayed
Fourier-label change L. Its chronological packed XORs are
`u^=v; v^=u; p^=u; v^=p`. After the children, translate all three blocks by
all-ones and reverse the chart. The emitter recursively substitutes the
actual C/Q children and all these wrappers.

Normalize the operation types as `A(n)=C_n`, `B(n)=Q_(n/2)`.
For a proposed saving exponent a, write `tau=1-a`. The two-C realization
has child matrix

```text
M(a) = [[ (1/3)^tau,     (2/3)^tau ],
        [ 2*(1/2)^tau,  0         ]].
```

At a=0 its positive fixed vector is `(1,1)` and its spectral radius is one.
For a>0 every nonzero entry increases. Equivalently, eliminating Q leaves
three C children of relative width 1/3: moment `3^a`, and after two levels
`9^a`. No positive weighting supplies strict contraction. Even granting all
non-child work zero for this rejection test fails; its actual nonnegative
charges cannot repair that failure. This is not a new multiplication bound.

There is a useful elementary gate beyond that particular word. For a matrix
T, let s(T) be its maximum column support. Then `s(AB)<=s(A)s(B)`.
Monomial maps (permutations and nonzero coordinate scalings) have support one;
C_k on a fixed full array has support `2^k`. Q_f has support `2^(2f)` in
every column and C_n has support `2^n`. Hence any exact product of these C
calls and monomial maps needs total C-axis width at least 2f for Q_f and n
for C_n, including endpoints with an identity bank. Arbitrary monomial
interleaving does not evade this gate. If every recursive child has width
at most its parent, the width-normalized moment is at least one for a>=0.

This support argument concerns a direct whole-array product. It does not
price a different mixing primitive, an encoded endpoint accepted by a caller,
or the selected supplier's additive/encoded interfaces. It is not a general
lower bound for integer multiplication or all algorithms for Q.

## Paid finite execution and remaining terms

[invoice.py](invoice.py) specifies a deliberately simple unrolled array
machine. Each record reads its operands, computes and writes its result,
clears private work and returns the data head to cell zero. A C butterfly
uses 12 real ADD/SUB operations, four exact halvings, four real reads and
writes, and eight private-register clears. Swap, phase and scale records
have separate tariffs. Eight private real registers are also cleared at
startup. No spare data array or clean bank is granted.

These are exact counts for the declared schedule, not an optimized tape
implementation or wall-clock predictions. The Q rows below all use the
**same 64-cell operand**, including the bank spectators.

| Program | Data cells | C children | Records | Data-head cell steps | Program bits |
|---|---:|---|---:|---:|---:|
| Direct C_3 | 8 | one width 3 | 12 | 168 | 120 |
| Typed C_3 | 8 | three width 1 | 82 | 926 | 820 |
| C_9, two levels | 512 | nine width 1 | 23,904 | 13,528,352 | 525,888 |
| Q_2, two-C implementation | 64 | two width 2 | 728 | 47,136 | 11,648 |
| Q_2, one-wide-C implementation | 64 | one width 4 | 760 | 53,424 | 12,160 |
| Q_2, tensor-bank implementation | 64 | four width 2 | 1,504 | 122,064 | 24,064 |

For B bits per real component, data storage is `2NB` bits and private data
storage is `8(B+2)` bits. A descriptor has `4+2 log2(N)` bits; all descriptor
storage, reads and instruction-head travel are recorded. If d is the cell
movement count and E the complex-cell visit count, the literal scan/return
schedule costs `2B*d+2(2B-1)E` data-head bit steps. Real data accesses and
private clears are separately charged in bits.

If input components are dyadic with p fractional bits and magnitude below
`2^b`, a conservative sufficient signed width is `B=p+b+q+g+2`: q counts
all C axes and positive b-scales, while g counts all C axes and inverse
b-scales. The integer-grid replay checks every required division exactly.
Arithmetic temporaries use B+2 bits; these are sufficient bounds, not minimal
precision or a rounding-error theorem.

At the recursive interface the bill is the sum of child prices and wrapper
costs. The finite invoice instead expands those children into butterflies;
their arithmetic is already included and must not be added twice. Its full
implementation cost has the form

```text
displayed arithmetic/access/clear/head/dispatch costs (children expanded)
+ program generation and descriptor writes + control workspace/work
+ caller admission/decoding + native hosting/precision/analytic obligations.
```

Program generation must at least write every recorded descriptor bit. Control
storage needs address and instruction-position registers; concrete bit-level
ALU and control implementations remain unpriced. Those terms are recorded
explicitly as unknown nonzero costs, not set to zero in an admitted budget.
The optimistic *rejection* above already fails without them, so completing
that native construction is not justified in this session.

## Reproduce and evidence boundaries

Python 3.12, standard library only; from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/phase-accumulator-tensor-closure --check-only
python3.12 -B scripts/research_package.py --package research/phase-accumulator-tensor-closure
```

The registered commands run under `-I -O -B`; correctness checks do not use
Python assertions. Normal verification is read-only. `verify.py --emit` and
`independent.py --emit` print regenerated receipts for deliberate comparison.

The primary replay checks all input columns of 23 fixtures: 1,692 columns
and 559,952 complex coefficients, including the complete 512-by-512 C_9
two-level map and the nested live-bank map. It also checks all 512 columns
of the C_9 literal inverse and 512 nested open-state boundary columns. Ten
failure controls cover an unconsumed producer, omitted return, wrong consumer
source, missing inverse scale, wrong sign/chart, missing movement or child,
false half-volume normalization and an invalid odd-dimensional bank.

[independent.py](independent.py) imports none of the primary implementation.
It uses Fraction-valued generic matrices and an integer Walsh spectral
reference. It checks every column of each fixture with at most six address
bits and 12 disclosed columns each of C_9, its inverse, the nested bank map
and that map's open-state boundary; it independently
recounts the finite program invoices and binary ranks. This is a separate
implementation by the **same AI-assisted author**, not independent human
review. [test_package.py](test_package.py) checks relocation, read-only replay
and corrupted evidence/program rejection. Written proofs are not formalized
in a proof assistant.

The scientific baseline is `23ef28cbeb7a3e2e985be22cab6832424bd98cf6`;
[SOURCES.json](SOURCES.json) pins exact inputs and provenance. The selected
record at that baseline has kappa `836330098538459/500000000000000000`.
On the untouched base, `scripts/research_baseline.py` rejects the selected
digest of `scripts/verify_hpe_lean_binding.py`: expected
`52aa1d23641e4c716b43c98f6b883ad042087dd03a9d01369e8e6a735b07aa03`,
actual committed bytes
`2fe5aac5828b1fdb79ff5e9ba87faef4db77e0c9339f362a1775b498a6d59e13`.
That unrelated mismatch was not edited or bypassed. At the hourly checkpoint,
canonical main `1fb5ac85b019b58a53e18baa8629137beb90dd57` had corrected this
selected digest; priority revision 5 and this package's kernel input were
unchanged. The older scientific provenance is retained intentionally. No selected cold replay,
native compiler admission, new supplier or selected-record change is claimed.

## Open next questions

The structured questions and stopping tests are in [TASK.json](TASK.json).

1. **Can a caller consume an encoded boundary that changes the support gate?**
   First pin one actual supplier call site and its accepted input/output maps,
   then test a paid encoding/decoding pair on f=1,2 through two parent levels.
   A transform moved to the root must still be paid. This matters because
   direct whole-array C/monomial refactoring is already width-critical.
   The blocker is an explicit caller contract with a favorable complete bill;
   the present package does not supply one.
2. **Can a different native mixing primitive implement the quadratic phase
   at a favorable price?** Start with the explicit 4-by-4 Q_1 kernel and
   identify a legal supplier operation outside the C/monomial product model.
   Expand two levels and price its full operand volume, movement, precision
   and restoration before searching larger instances. The blocker is the
   native implementation and its outer recurrence, not another phase word.

Neither question authorizes a larger search in the unchanged alphabet.
The working reverse-order schedule is available as a correctness control
for a successor that actually changes one of these premises.

## Prior work and credit

The Pauli commutation/dimension fact is standard; see Thomas Vidick's
[Pauli braiding](https://mycqstate.wordpress.com/2017/06/28/pauli-braiding/)
and [Natarajan–Vidick](https://arxiv.org/abs/1610.03574). The proof above is
the elementary exact eigenspace argument, not a robustness theorem. The
Walsh/Clifford identities and support-count inequality are also standard
linear algebra, and are not presented as new discoveries.

The candidate comparison was informed by [Dumas–Grenet's in-place
accumulation](https://arxiv.org/html/2307.12712v3) and [Johnson–Frigo's
mutually recursive scaled FFTs](https://www.fftw.org/~athena/papers/newsplit-pub.pdf).
Neither algorithm is implemented or claimed to transfer here.

Nearby repository work remains credited to Ross Richardson (cyclic frames,
PR1287, and the scalar-versus-recursive audit PR2500), Cinna Davis (PR1391,
1410 and 1506), @woklerx (PR1439), and the credited authors of
[`mutable-source-port-borrowing`](../mutable-source-port-borrowing/README.md),
[`unipotent-return-seed53`](../unipotent-return-seed53/README.md),
[`bit-dyadic-ternary-catalyst`](../bit-dyadic-ternary-catalyst/README.md) and
[`heisenberg-commutator-incidence-seedb054`](../heisenberg-commutator-incidence-seedb054/README.md).
The last two use different formal alphabets and tariffs; their bounds are
not silently transferred to this complex whole-array model.

The checkpoint also inspected the newly integrated `selected-child-compact-return`
and `selected-invocation-frames` work by ywz65 and its credited predecessors:
those provide actual selected-child/caller boundaries and remain relevant to
the first next question. They do not supply this phase-accumulator recursion.
The `typed-window-fusion-audit` explicitly prices a different fixed-reader
frame correction; `qq16-clifford-denominator` concerns an odd-denominator
observation obstruction. Neither is treated as a new result of this package.
Jose Manuel's live [PR2742](https://github.com/CrocSwap/integer-mult-bounds/pull/2742)
at `8571b04372f539b725e7f27d1ab00c506ca616fd` supplies a changed native
covariant reader action, while explicitly retaining its eight centre children.
That closes a different frame-alignment obligation; it is not evidence of a
child-width saving for the present recursion.

Prepared for Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance in design, proof drafting, implementation and checking. New files
are Apache-2.0. No third-party code is vendored. Live overlap coverage and
upstream checkpoint decisions are recorded in TASK.json; searches cover
bodies/notes, not every diff, and do not establish novelty.
