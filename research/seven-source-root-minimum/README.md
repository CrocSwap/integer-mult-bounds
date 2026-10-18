# Four dirty roots are necessary and sufficient at seven sources

**Scoped root-count optimum; no new kappa.** In the generic F2 connector
interface below, all 127 nonzero seven-source masks require **at least four
arbitrary-dirty root rows** if every source map and every output map is called
exactly twice. This remains true with arbitrarily many invertible F2 root-frame
changes and per-occurrence physical ports. The four-root star construction
already supplied by [PR2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182)
attains the minimum. **The new contribution is the three-root exclusion and
therefore the exact seven-source root minimum, not the attaining construction.**

The proof reduces every schedule in this infinite frame/length domain to a
finite necessary condition. Two separately written implementations exhaust
135,135 source words and 651 source-class partitions: 87,972,885 cases. Every
case fails that condition. The smallest deficit is four mandatory masks.
A literal attaining program, symbolic replay, rectangular-map checks, and
failure controls accompany the census. This is a written proof with exact
finite evidence, not a proof-assistant formalization.

## Interface and quantifiers

There are seven immutable sources x_j, 127 distinct output rows y_m, and k
root rows z_p, all initially arbitrary. All roots have the same vector width.
For independently chosen compatible F2-linear maps B_j and A_m, the target is

```
y_m += A_m(sum_{j: m_j=1} B_j(x_j)),  1 <= m <= 127.
```

A schedule uses complete fixed-map additive calls B_j into a root and A_m
from a root into its own output. It uses **exactly two calls to every B_j and
every A_m**. The schedule is data-independent and must implement the identity
for arbitrary maps and inputs. Sources and roots restore; outputs are not
observed or used as workspace. Child scratch is private, restores, and cannot
alias source, target or root rows. Linear maps need not be invertible, square,
symmetric or commuting.

For the lower bound, grant every invertible scalar F2 mixing of the k root
rows at any time, at no cost, and allow any physical port on each child call.
This is a relaxation of paid root XORs. It does not grant resets, clean roots,
source mixing, target feedback, extra map calls, or matrix-valued transformations
inside a root row. The upper bound uses only explicitly charged XORs
`X(p,q): z_p += z_q` and restores the identity root frame.

The theorem is about the minimum root count **at these minimum map incidences**.
It does not minimize total work across schedules that call maps more often.
Multi-root source incidence need not be even in general: the verifier includes
a restoring three-call source excursion to guard that distinction.

## Reduction to source-axis classes

Write h_j = B_j(x_j), and let R_t be the current invertible root frame. A
source call at physical port p injects normalized axis R_t^-1 e_p. Since
exactly two calls to each source must restore all independent h_j columns,
their normalized axes coincide; call this nonzero vector v_j. Let q_t be the
source-incidence parity after the first t source calls. The normalized root
state is

```
z_initial + sum_j v_j q_t[j] h_j.
```

A physical root with dirty covector r has source coefficients
`(r dot v_j) q_t[j]`. Two readouts of the same arbitrary A_m must have the
same dirty covector, or initial root dirt survives. Their target mask is thus

```
m = s_r AND (q_a XOR q_b),   where s_r[j] = r dot v_j.
```

This is a necessary condition even if the selected covector is not available
at those boundaries. Granting all covectors at every boundary only enlarges
the realizable set. Put `D(w) = {q_a XOR q_b}` for the closed source word w.
Transfers between source calls do not add new q values.

It suffices to exclude k=3: fewer rows embed in this model with unused dirty
rows. The all-ones output requires a covector r_* with r_* dot v_j = 1 for
every j. Thus the occupied axes lie in the four-point affine plane
`{v in F2^3: r_* dot v = 1}`. Partition the seven sources by identical axes.
There are at most four nonempty classes.

**Mandatory-mask lemma.** With three or four occupied classes, a mask meeting
at least three classes can only use a covector responding to every occupied
axis. Consequently it must itself belong to D(w).

For three occupied axes the assertion is immediate: responding to three means
responding to all three. For four axes, their sum is zero, so every covector
has even total response. A response containing three axes therefore contains
all four. Equivalently, three distinct points in this affine plane are linearly
independent: a dependence among them would contradict r_* dot v = 1.

With one occupied class, all nonzero masks already require the all-source
response; choose any refinement into three nonempty classes and its mandatory
masks remain necessary. With two classes, split one into two nonempty classes.
Every mask meeting all three refined classes meets both original classes, so
it also requires the all-source response and lies in D(w). There are seven
sources, so these refinements exist. This covers the smaller-class cases
without importing a prior lower-bound census.

## Complete finite domain and result

Every source occurs twice, so relabeling by first occurrence reduces the source
order to a pairing of 14 positions: `(14)!/(2^7 7!) = 135135` words. After this
relabeling, retain **every** set partition of the seven labels into three or
four nonempty classes. There are S(7,3)=301 and S(7,4)=350, respectively. No
source-color symmetry is discarded without retaining its class assignment.

For every word/partition pair, compute the mandatory set M of masks meeting
at least three classes and count `|M minus D(w)|`. The exact minima are:

| Class sizes | Partitions | Minimum missing mandatory masks |
|---|---:|---:|
| 5+1+1 | 21 | 4 |
| 4+2+1 | 105 | 10 |
| 3+3+1 | 70 | 13 |
| 3+2+2 | 105 | 20 |
| 4+1+1+1 | 35 | 19 |
| 3+2+1+1 | 210 | 28 |
| 2+2+2+1 | 105 | 33 |

Every minimum is positive. Hence no three-root schedule exists. This is an
exhaustive necessary-condition exclusion, not a failed heuristic search. Full
missing-count histograms and the source-difference histogram are in
[CENSUS.json](CENSUS.json). A further check is possible: merging two of four
classes yields three classes whose mandatory set is a subset of the original;
the four-class enumeration is redundant for exclusion but supplied explicitly.

The C++ engine generates position matchings, forms prefix XOR differences, and
builds mandatory masks by testing per-mask class incidence. The Python engine
generates restricted-growth words, accumulates contiguous-interval parities,
and builds mandatory masks by products of within-class subsets. Their complete
histograms agree. Neither imports predecessor census code. The registered
Python replay recomputes all cases; it does not trust a native receipt.

Specializing extra source maps to zero and discarding their identity calls
extends the lower bound to **at least four roots for every n >= 7** in the same
paired-call model. It does not assert that four suffice beyond seven.

## Attainment and complete cost

PR2182's construction uses k=n-3 roots. At n=7, reserve a center z0 and three
leaves z1,z2,z3. Run the closed center source cycle B0 B1 B0 B1, visiting all
8 center frames `z0 += sum u_i z_(i+1)` at each of its four prefix states.
Use alternating forward/reverse reflected Gray tours, returning the frame to
identity after four tours. Inject B4, B5, B6 into the three leaves. Run the
analogous center cycle B2 B3 B2 B3 and the same tours. Finally repeat the three
leaf injections to restore their arbitrary dirt.

For mask `m = a | (b << 2) | (c << 4)`, read A_m at prefix a and frame c in
the first phase, and prefix b and frame c in the second. The dirty covectors
match, and their difference is the requested source sum. This proves the
attainment for arbitrary compatible maps. [WITNESS.json](WITNESS.json) lists
every physical operation; [program.py](program.py) emits this **credited
predecessor construction**, and the verifier independently interprets it.

The program has 14 complete B calls, 254 complete A calls, and 56 root XORs:
32 of X(0,1), 16 of X(0,2), and 8 of X(0,3). With p_j=0 for j<4 and p_j=j-3
otherwise, its full conditional node bill is

```
C_7(L) = H_4(L) + 2 sum_j T_Bj(L,p_j) + 2 sum_m T_Am(L,0)
         + 32 T_X(L,0,1) + 16 T_X(L,0,2) + 8 T_X(L,0,3).
```

Here each T is a complete child/transfer price including that operation's
access, dispatch, scratch restoration and head return. H_4 includes root
admission, initial layout, reusable map preparation, schedule generation/storage
and any remaining controller costs; charges included in T are not counted
again. Four root rows must remain reserved throughout. Sequential child calls
may reuse private scratch only when its admission contract permits it; with
maximum private scratch S(L), roots plus private scratch need 4L+S(L) cells,
in addition to all source/output and preparation storage. On a direct scalar
backend, a root XOR costs L bit XORs, not a free frame change. No actual recursive
supplier/caller is bound here, and no favorable physical recurrence or new
multiplication exponent is inferred from this invoice.

## Reproduce and checks

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. The selected
conditional kappa remains `836330098538459/500000000000000000` (PR1094).
With Python 3.12 standard library, from the repository root:

```sh
python3.12 -I -O -B research/seven-source-root-minimum/verify.py
```

Expected:

```
PASS_SEVEN_SOURCE_ROOT_MINIMUM words=135135 partitions=651 cases=87972885 roots=4 B=14 A=254 X=56 dense_columns=4362 mutations=329 affine_checks=245
```

The independent native comparison (GCC or Clang with unsigned 128-bit support):

```sh
c++ -O3 -std=c++17 -Wall -Wextra research/seven-source-root-minimum/census.cpp -o /tmp/seven-root-census
/tmp/seven-root-census > /tmp/seven-root-native.json
python3.12 -I -O -B research/seven-source-root-minimum/verify.py --native-result /tmp/seven-root-native.json
```

Registered replay:

```sh
python3.12 scripts/research_package.py --package research/seven-source-root-minimum
```

Besides full census regeneration, verification checks all formal dirty/source
columns of the attaining program forward and backward, 4,362 concrete basis
columns across 18 rectangular/singular-map forward/inverse cases, all 324
single-operation omissions, five port/direction/label/schema mutations, the
245 finite affine-plane cases, and a differently computed mandatory mask set.
Positive controls admit the known six-source/three-root program, a neutral
transfer pair, and odd source incidence in a restoring multi-root excursion.
Historical pins require Git only for the registered metadata check; direct
scientific replay is self-contained and performs no network access or writes.

## Scope, overlap and credit

The three candidates considered were the five-source arbitrary-price frontier
(already PR2063), paired heterogeneous output events (already PR2230), and the
seven-source root minimum explicitly left open by PR2182. The last was chosen
under the user's fresh OS assignment seed 54, recursive interfaces. The card's
scope is recorded as **changed**: this settles an interface-capacity question,
not a new supplier or success at the original alphabet-cost acceptance gate.

PR2182, pinned at `dc252de1cc594829c3031abdb4de104713bc474a`, supplies the normalized-axis
method, the two-root n>=6 boundary, and the attaining star. It explicitly leaves
n>=7 root optimality open. Ross Richardson's PR934/PR943 supply the underlying
dirty-connector contract and prefix criterion, and Douglas Colkitt's PR1185
supplies the earlier six-source/Gray lineage. Their common-factor/dirty-commutator
predecessors include PR889 and Chafik Boukhalfa's PR628.

Cinna Davis's PR2229 and PR2236 use one root and weight-1/2/3 output masks at 14
and 16 source calls. The full-mask, arbitrary-frame, three-root exclusion here
has a different quantified domain. Adam Gall's PR2063 establishes five-source
one-root tariffs; it is not resubmitted. Related PR2208 allows additional calls
and develops different all-word tariff bounds. Exact heads, source hashes and
fresh overlap coverage are recorded in [SOURCES.json](SOURCES.json) and
[TASK.json](TASK.json). The final refresh at 2026-10-15 03:20 UTC completely paginated 502 open PRs
and 989 discussion/comment/reply records, with no warnings. No matching result
was found; this is not a guarantee against unseen work.
The coordination record is [Discussion2275](https://github.com/CrocSwap/integer-mult-bounds/discussions/2275).

Prepared by **Mason Hale**, with substantial **OpenAI Codex** assistance in
proof derivation, code, experiments, review and writing. Apache-2.0. No
independent human review or proof-assistant verification is claimed. No selected
frontier, upstream source, or frozen predecessor file is changed. Global
selected cold replay is not needed for this isolated package and was not run.

## Open next questions

1. Does four-root attainment extend to eight sources at two calls per map?
   This would locate the next storage boundary. Start from the normalized
   affine-plane model in F2^4 and the existing five-root star; a complete
   reduction is needed before scaling the census.
2. What is the minimum paid transfer bill at seven sources with four roots?
   The 56-X star is an upper bound only. Start by optimizing a fixed legal
   readout/source schedule with exact dirty-frame states. Global optimality
   needs a justified search-length bound and actual port tariffs.
3. Does a concrete recursive caller profit from the four-root interface?
   Instantiate every T and H term above and compare with a one-root schedule
   using extra child calls. The missing caller, stock, tape and precision
   contracts remain the blockers; this root theorem alone supplies no gain.
