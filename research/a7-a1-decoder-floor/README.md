# The A7+A1 nine-normal decoder has sharp COPY cost 72

**Scoped exact theorem with finite binary premises. No new supplier or kappa.**

For the fixed **A7 weights + A1 root** frame proposed in
[joaqcoo's PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224),
on all 120 E8 root lines, the minimum separate-term copied-information cost is
**72**, allowing **arbitrary independent complex row shifts**. All nine terms
can be active: an exact witness has ranks `(1,8,9,9,9,9,9,9,9)`.

There is also an exact rank-shape statement. For every `0 < q <= 1`,

| Allowed terms | Minimum separate COPY power sum |
| --- | --- |
| Zero terms allowed | `8 * 9^q` |
| All nine terms active | `1 + 8^q + 7 * 9^q` |

Thus this overcomplete family cannot improve even the separate COPY power
bill of the ordinary eight-term **P120** coordinate decoder. At `q<1`, keeping
all nine terms active is strictly worse. These are COPY ranks and their
power sums, **not a complete recursive child profile or supplier moment**.

PR1224's sparsest-row witness costs 81 and its bounded annealing supplied no
optimum. This contribution replaces coefficient sampling for this specific
family by an all-complex-shift proof. It does not generalize the A8 simplex
floor to every nine-normal frame, and does not repeat the finite search.

## Exact model and source binding

Use all 120 unoriented E8 root lines in the standard eight-coordinate model:
roots `e_i +/- e_j` and half-sign vectors with an even number of minus signs.
Choose the representative whose first nonzero coordinate is positive. The
checker stores `x_i = 2 r_i`, so every stored root has squared norm eight.

In true coordinates the nine reader normals are

```
b_k = e_k - (1/8) * 1,    k=0,...,7,
a   = (1/2) * 1.
```

The eight A7 weights have the unique relation `sum b_k=0`; the A1 normal is
orthogonal to them. Set `T_ik = <r_i,b_k>` and `T_i8 = <r_i,a>`. The all-pairs
identity is `D T^transpose = 2 G`, where `G_ij=<r_i,r_j>`. Ordinary transpose,
not conjugate transpose, is intended throughout.

The roots span eight dimensions. Consequently exactness is equivalent to
`sum_k D_ik b_k + D_i8 a = 2 r_i` separately in each row. Its full solution is

```
D_ik = x_ik + t_i      (0 <= k < 8),
D_i8 = sum_k x_ik / 4,
t_i in C arbitrary and independent for each root line.
```

This is a complete parameterization, not a finite coefficient alphabet.
Generic complex shifts introduce no additional zero-support pattern.

The source uses a rotated A7 frame. The verifier authenticates both PR1224
Python source files **before importing them**, reconstructs its actual frame,
and checks an exact rational orthogonal map taking the displayed normals to
those source normals. The map carries all 120 root lines bijectively to the
source's lines, with recorded signs and indices. If `b'_k,a'` denote the
source's **doubled** normals, its columns are `Q e_k=b'_k/2+a'/8`. Thus this
result is bound to the actual source candidate, not just a similarly named
root subsystem. Full Git blob/SHA256 pins and exact source heads are in
[SOURCES.json](SOURCES.json); the selected record is historical provenance.

## Proof of the COPY floor

The binary pairing is `B_ij=(G_ij+1) mod 2`, of rank nine. Represent its row
space by binary labels `l_i in F2^9`. Each fixed reader support `Y_k` spans
all nine label dimensions, including the A1 reader. Therefore its term's
pairing rank is the label-span dimension of its row support `X_k`:

```
rho_k = rank_F2 B[X_k,Y_k] = dim span{l_i : D_ik != 0}.
```

The A1 row support is fixed and also has rank nine, so that term always costs
nine. For the other eight terms define

```
K_k = {w : w dot l_i = 0 whenever D_ik != 0},
delta_k = dim K_k.
```

The complete cost is `81 - sum_(k=0)^7 delta_k`. It suffices to prove that
this deficiency sum is at most nine.

### Compatibility and the finite lemmas

If `w in K_j`, `z in K_k` and both evaluate to one at line `i`, then
`D_ij=D_ik=0`. The row formula forces `x_ij=x_ik`. Define two characters to
be compatible when this implication holds on every root line.

For a binary plane `U=<u,v>` contained in `K_0`, and `k=1,...,7`, let
`H_k(U)` be the space of all characters compatible with every member of U.
It is the annihilator of the labels on

```
(supp(u) union supp(v)) intersect {i : x_i0 != x_ik}.
```

Thus `K_k` is contained in `H_k(U)`. For a nonzero character z in that space,
let `F_k(z)` be the span of labels with `z dot l_i=1` and `x_i0 != x_ik`.
Compatibility in the other direction gives `K_0 subset F_k(z)^perp`.

The verifier exhausts all `(511*510)/6 = 43,435` binary planes, encoded
uniquely by `0<u<v<u xor v`, and proves these finite premises:

1. Every `H_k(U)` has dimension at most one.
2. If it is nonzero, its unique character z has `dim F_k(z)` either one or
   seven. In the rank-one case the nonzero label is exactly `q_k`, the label
   of the root line `e_0-e_k`.
3. The seven `q_k` are independent.

The counts of planes with 0 through 7 nonzero H spaces are

```
5809, 13447, 13314, 7350, 2590, 735, 147, 43.
```

There are **75,565** rank-one and **1,778** rank-seven forced-space cases.
The `--direct` replay independently computes all **304,045** H dimensions
by binary annihilator elimination, instead of inferring their dimension
from the compatibility table, and checks the unique character when present.
It shares geometry and some arithmetic helpers; it is not independent human
review or a fully code-disjoint checker.

### Deduction for every complex shift

If all eight deficiencies are at most one, their sum is at most eight.
Otherwise the `S8` coordinate symmetry moves a term with deficiency at least
two to position zero. The checker verifies all seven adjacent-transposition
generators on the root lines and every pairing entry. This action permutes
the A7 normals, fixes A1, and preserves the row-shift family, including the
sign changes used to orient root representatives.

Choose a plane in `K_0`. By premise 1 every other nonzero deficiency is one;
let J be the set of these terms. If any corresponding `F_k` has rank seven,
then `delta_0 <= 2` and

```
sum delta_k <= 2 + |J| <= 2 + 7 = 9.
```

Otherwise each such term forces `K_0` to annihilate `q_k`. By premise 3
these are `|J|` independent conditions, so `delta_0 <= 9-|J|`, again giving
`sum delta_k <= 9`. This includes J empty. The total COPY cost is at least
72 for **every** complex shift assignment.

This adapts the deficiency-plane method of
[Philipp / mightyOil's PR1248](https://github.com/CrocSwap/integer-mult-bounds/pull/1248),
with credit. The A7+A1 problem has eight mutable columns and a forced rank-nine
A1 term; its 43,435-plane census is different. In particular the A8 proof's
extra eight-partner incompatibility step is not assumed here: the A7 family
has only seven possible partner columns.

### Sharp attainment and all powers

Set `t_i=-x_i0` on every line. Column zero vanishes, and the eight remaining
terms each cost nine. To make all nine terms active, change just the row
`x=(2,-2,0,0,0,0,0,0)` to `t_i=-x_i1=2`. The costs become
`(1,8,9,9,9,9,9,9,9)`. Both identities are checked on all **14,400** pairs,
with exact cleared-denominator arithmetic. The complete shifts are stored
in [RESULT.json](RESULT.json); they are regenerated, not accepted on trust.

Every separate rank is an integer in `[0,9]`. For `0<q<=1`, minimizing
`sum rho_k^q` subject to `sum rho_k>=72` first reduces total mass to 72.
Concavity then permits mass transfer from a smaller interior coordinate to
a larger one without increasing the sum, until at most one coordinate is
interior. With zero allowed the minimum profile is `(0,9,9,9,9,9,9,9,9)`;
with every term positive it is `(1,8,9,9,9,9,9,9,9)`. The witnesses attain
them, proving both power formulas. For `q<1`, `1+8^q>9^q`, so nine active
terms are strictly worse than the eight-active comparator. The integer
exchange algorithm is also checked on all 97 sorted feasible rank profiles;
the universal-in-q conclusion uses the written concavity proof, not numerical
sampling of q.

## Budget, relevance and limitations

The actual copy invoice includes all nine supports and the mandatory A1
term. Even granting free gathering, source access, frames, dirty restoration,
hosting, precision/tape and padding, the COPY floor is the P120 eight-term
baseline. Its ratio `72/120=3/5` exceeds the selected P112 ratio `64/112=4/7`.
Beating that ratio on 120 ports would require integer COPY at most 68.
This is an algebraic negative screen; **it is not a full supplier rejection
under every imaginable coverage or shared-copy contract**.

The task is explicitly **changed** from the chooser's physical rank-shape
synthesis gate to a scoped missing-optimum result for a source-proposed
candidate. It does not meet the card's 5% fully paid construction gate. No
incumbent ceiling calculator is applied outside its fixed 112-port premises,
and no physical or all-size claim is inferred from the power sum. Changed
normals, punctures, masked exactness, shared COPY billing, physical frame
paths and arbitrary nonlinear decoder architectures are outside this theorem.
The selected kappa `0.001672660197076918` and frozen predecessors are unchanged.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -B research/a7-a1-decoder-floor/verify.py --direct
uv run --python 3.12 --no-project python -I -O -B research/a7-a1-decoder-floor/test_verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/a7-a1-decoder-floor
```

The first command reports `PASS_A7_A1_DECODER_FLOOR`, `COPY=72`, the active
rank vector and `direct_H_checks=304045`. Default runs only read files;
`verify.py --write --direct` explicitly regenerates RESULT.json. The focused
controls include coefficient corruption, omitting the fixed A1 term,
swapping readers, a false nine-way dependency, a corrupted binary character,
a forged receipt, and executable-source drift rejected before import. A
clean-export optimized replay checks portability and absence of writes.
Observed execution is recorded in [VALIDATION.json](VALIDATION.json).

## Open next questions

- Can the same A7+A1 normals become competitive after a **specified puncture**?
  This matters because the reader spans, fixed A1 cost and deficiency lemmas
  can change; the P120 proof does not transfer automatically. First choose one
  puncture justified by its geometry, compute all nine reader spans and the
  replacement H/F lemmas, and require an optimistic complete copy invoice
  before synthesis. No punctured-family theorem or physical implementation
  is supplied here.
- Can a genuinely changed overcomplete normal frame beat the baseline before
  realization costs? Begin with a source-bound normal matrix, derive its
  entire dependency space and forced supports, then use support compatibility
  rather than another bounded scalar search. The unrestricted frame problem
  and legal physical realization remain open.

## Attribution, independence and license

Independent chooser seed **cf5042788fae24418be429f5a4587f5d**, track
`complex-mechanisms`; complete [SELECTION.json](SELECTION.json) and
[TASK.json](TASK.json). Base `e112d71c8d7bb32435debcc54df932593dd8223a`.
Coordination: [round3 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931253).
The initial A2+E6 idea was abandoned before computation because a concurrent
instance reserved it; none of that instance's mathematics was shared or used.

Credit **joaqcoo / PR1224** for this fixed frame, row-shift normal form and
heuristic candidate; **Philipp / mightyOil / PR1248** for the deficiency-plane
proof method; **DreamingOfClouds / PR717, PR446, PR595** for the decoder and
separate pairing-rank convention; and **themilkman216 / PR968**,
**woklerx / PR1077**, and the selected construction lineage for context.
PR1612/1614 concern the different A8 simplex frame and P112 punctures.
The executable predecessor is used only for exact frame binding, not to
certify the new deficiency lemma. All predecessor files remain unchanged.

Prepared for **Adam Gall (@adamgall)** with substantial **OpenAI Codex
(GPT-6 Astra)** assistance in research, proof, implementation and writing.
The theorem is a written argument with finite machine evidence, not a formal
kernel theorem, independent human review, hosted-CI claim or multiplication
proof. New material is **Apache-2.0**; source attribution is retained.
