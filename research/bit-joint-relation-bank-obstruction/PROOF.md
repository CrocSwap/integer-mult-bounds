# Joint helper relations on the fixed BIT word

For the exact PR7001 word, no relation subspace within one cocharted helper
group can improve the complete signed moment for `0<=kappa<=1/100`.
This holds in either orientation separately, for every possible codimension
from one through the size of the group. The largest group has 410 helpers.
This result gives no new kappa.

## Contract and inherited evidence

Use the word and caller in [SOURCE-PINS.json](SOURCE-PINS.json). Let G be one
of the nine helper groups with common entrance A and exit D. Let H_G be its
binary coordinate space. Choose any subspace U of H_G. Impose all relations
`u*x_G=0` for u in U. If `k=dim(U)`, an invertible binary boundary basis can
express these relations as the removal of k productive helpers. Each lost
target has rank `d=abs(dim(D)-dim(A))`. Keep all main inputs and helpers in
other groups arbitrary and independent.

As in the retained [single-relation proof](retained/research/bit-single-relation-bank-obstruction/PROOF.md),
keep paid forms, order and frames fixed. Grant all past receiver banks and
ordinary scalar XOR work for free. Reconstruct an omitted bank from strictly
earlier same-chart banks and free entrance fields. Coefficients are in F2.
New routes, changed forms, matrix-valued coefficients, mixed boundary groups,
nonlinear operations and compositions across orientations are outside scope.

The complete retained PR7720 package runs first. It proves that every original
receiver bank list is independent, supplies every exact clean space
`L_C=V_C intersect H_G`, checks both raw-word orientations and proves its
codimension-one exclusion. It also authenticates all source frames and the
complete caller invoice. Its source files and inputs are unchanged here.
The new result must account for interactions that its single-line proof did
not cover.

## Rank loss and common pivots

At A, U lies in the free entrance space. Quotienting by U reduces free rank
by k and cannot remove a paid bank. At every other chart C, the rank loss is
`dim(U intersect L_C)`. No other dependence can appear because the original
bank list is independent. At most that many paid banks can be omitted.
Each omitted bank is a leading position of the relation space in the ordered
bank list. Its rank is at most r_C, the maximum rank at any leading position
of the full space L_C. The certificate computes all these possible positions.

Fix one coordinate basis and order on H_G. Write P(W) for all possible leading
positions of nonzero vectors in a subspace W. Row elimination gives
`|P(W)|=dim(W)`. Since a vector in `U intersect L` belongs to both spaces,

```text
P(U intersect L) is contained in P(U) intersect P(L).
dim(U intersect L) <= |P(U) intersect P(L)|.
```

Let `t=1-kappa`. The saved paid moment at nonterminal C is therefore at most
`r_C^t * |P(U) intersect P(L_C)|`, and at most
`r_C * |P(U) intersect P(L_C)|` for `0<t<=1`.
All receivers use the same P(U). Thus every coordinate pivot in P(U) can be
charged for all receiver spaces whose pivot set contains it. This controls
all subspaces at once, not just vectors in the supplied receiver bases.

## Forward coordinates and transposed terminal flags

For the forward word, use the original helper coordinates. At D, at most k
banks can be omitted. Charge each pivot in P(U) the maximum possible terminal
rank. Add r_C for each nonterminal receiver whose pivot set contains it.

For the transpose, this coarse terminal charge is insufficient. Instead,
construct a basis `b_0,...,b_(n-1)` of H_G from successive increases of the
terminal clean prefix. Each b_i has a verified bank witness whose last token
is q_i, with the q_i strictly increasing. These are all possible terminal
leading tokens. The latest token of any nonzero sum of the b_i is exactly
the q_i for its largest nonzero coordinate i. Consequently, the terminal
paid moment removed by U is exactly the sum of `rank(q_i)^t` for i in P(U).
Use this basis for every transposed nonterminal receiver as well.

The certificate gives all 874 per-coordinate rank lists across the 18
cases. The first entry is the terminal charge. Later entries are the
nonterminal charges. It covers all 385 nonterminal spaces with nonzero clean
intersection. The complete replay checks the zero spaces in the retained
receiver certificate too.

## Power bounds for every codimension

In 17 cases, each coordinate's list either consists of the one entry d, or
has integer sum at most `d-1`. The single entry d cancels one lost target
exactly. For every other list, exact integer checks give
`d^99>(d-1)^100` for d in 2, 4, 6 and 8. Thus

```text
sum(charged_rank^t) <= sum(charged_rank) <= d-1 < d^(99/100) <= d^t.
```

Summing over the k pivots of U proves that its saved paid moment cannot
exceed the k lost productive targets. Some terminal-only cases can be neutral;
no strict loss is claimed for those cases.

The remaining case is the transposed 410-helper group from chart 1 to chart 0.
Exactly one coordinate has integer charge eight; every other coordinate has
charge at most seven. For any `k>=2`, the total is at most `7k+1<=15k/2`.
The exact integer inequality `2^100 * 8^99 > 15^100` proves
`15/2 < 8^(99/100)`. Hence every such joint subspace strictly loses throughout
the stated interval. For k=1, the retained PR7720 certificate supplies the
already checked exclusion. The zero subspace changes nothing.

| Group size | Lost rank | Forward maximum charge | Transposed rule |
| ---: | ---: | ---: | --- |
| 410 | 8 | 7 | `7k+1` for `k>=2`; retained certificate for `k=1` |
| 2 | 4 | 3 | At most 3 per pivot |
| 1 | 6 | 5 | At most 5 per pivot |
| 7 | 4 | 4 | Five pivots charge 3; two have one terminal charge 4 |
| 6 | 4 | 1 | At most 3 per pivot |
| 5 | 4 | 1 | At most 3 per pivot |
| 3 | 4 | 1 | At most 3 per pivot |
| 2 | 4 | 1 | At most 3 per pivot |
| 1 | 2 | 2 | One terminal charge 2 |

This proves the result for arbitrary U, including combinations that do not
occur as individual rows in any source certificate.

## Complete bill and a control for joint effects

The unchanged paired caller has 36 local invocations, 107352 paid calls,
19950 productive targets and rank surplus 1506. Its query, idle and root
terms cancel in this change. The local target-minus-paid difference is
multiplied by 36. An alteration of only some invocations also cannot help.
No whole multiplication improvement or new physical implementation follows.
Any positive cost for the resources granted free can only strengthen this
exclusion within the fixed contract.

Single-line exclusions do not imply this joint theorem. As an abstract
receiver-space control, take a two-dimensional helper group with target rank
four. Give its terminal two rank-one banks. Give three other receivers rank-two
banks on the three distinct binary lines. A nonzero line removes one terminal
rank-one bank and one rank-two bank. Their integer sum is three, so every
single line loses for `99/100<=t<=1`. The full two-dimensional relation space
removes all five banks. Put `x=2^t`. Its signed gain is
`3x+2-2x^2=(2-x)(2x+1)`, which is positive for `0<t<1`. The common-pivot charges
are 3 and 5, so the new certificate gate rejects this example. This is a test
of the rank argument, not a constructed native BIT word.

## Verification and remaining limits

[generate.py](generate.py) constructs the basis, receiver transforms and pivot
charges with packed rows. [verify.py](verify.py) checks each transformed row
against coordinate-set source values, checks every terminal witness, and
computes pivot sets by an independent greedy column-rank procedure. It rejects
six changed certificates and checks the joint-effect control. The retained
single-relation package also reruns its two native interpretations, frame
checks, full invoice and six original controls.

Both implementations are by the same author after source inspection. They
are not blind review, independent human acceptance or a formal-kernel proof.
The original physical caller, native phases, owned storage, compiler, tape and
analytic interfaces remain inherited; all five framework assumptions remain.
Full predecessor suites, selected cold replay, Lean and Docker were not run.
A changed paid path or simultaneous relations across different boundary groups
requires a new analysis. This result does not establish a universal BIT limit.
