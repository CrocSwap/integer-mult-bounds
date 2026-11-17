# Chart 1062 on the original erasure contract

The comparator is Ali Romman's 76,636-event #7605 word and Rohan Arun's
signed #7113 caller with 17 native invocations. The conditional multiplication
saving is the exponent in the fixed-multitape bound
$T(n)=O(n(\log n)^{1-\kappa})$. The maintainer-selected certificate at the
pinned main commit reports $\kappa=0.00363005817$.

## Literal construction

Use zero-based clocks of the unmodified #7605 tape. At entrance chart 3,
add the same eight sources to each of 185 and 196 in the order in
`data/edits.json`. Source and coefficient pairs are
$(991,-1/16),(988,3/16),(599,5/4),(453,-1/4),(415,-1),(367,1/4),(350,-4),(311,-1/2)$.
These 16 ADDs have disjoint operand support from the other 24 entrance
operations in the #7611 edit. The generator checks that separation, the
five-clock shift from the peer's base in the affected interval, and the
original literal instructions at every deletion.

| #7605 clock | Source event | Change |
|---|---|---|
| 42110 | 185 moves from 401 to 1062 | Remove |
| 42111 | 82 moves from 740 to 1062 | Remove |
| 42112 | 185 receives −1/2 of 82 at 1062 | Remove |
| 42194 | 82 moves from 1062 to 1071 | Move directly from 740 |
| 43584 | 185 moves from 1062 to 922 | Move directly from 401, then subtract 1/4 of 779 |
| 43586 | 185 receives 7 at 922 | First subtract 5/4 of 7, then keep the original ADD |

The result has 76,651 events. Its canonical SHA-256 is
`86bc8a1d1276c5b8d80a19704f90279e85b24b9490a02b9afa67c1a5b119c114`.
The two targeted stays have only the shared ADD between their paid legs.
The exact source at that ADD is $x_1+x_6+x_{75}+x_{82}$. Both later
corrections use operands already present at chart 922. At chart 3 all
eight entrance sources are public. The two late operands are recovered
from their complete source functionals on the old tape.

Linear row interpretation assigns an independent variable to each public
input. A scalar event updates the destination by its exact coefficient
times the source row. Equal rows at a return give equality on every
public input. The builder propagated exact rational differences, checking
74 ordered CLEAR values, 1,501 public returns, 68 vacant private returns,
the COPY condition and every touched owned operand. In particular the
45th CLEAR, owned 1557 at original clock 42713, retains coefficients
$-1$ on 451, $-3/2$ on 902 and 985, and $+1$ on 1495. This preserves the
original #7605 erasure interface. DreamingOfClouds introduced these same
contractions and coefficients on a different CLEAR44 in #7611. The
original-clock manifest keeps role 46 and the source #7605 caller.

SYLforge's W1 in #7616 at `22b310ba50a554b6111804824782793beb41073f`
already ported the larger #7611 stay-drop set and the #7612 contact
rechart onto uncollapsed #7605. Its fully replayed W2 adds 39 stationary
lifetimes to the original 74, for 113 total, and reports conditional
$\kappa=0.003656628302607$. Here the package isolates the two chart-1062
stays while retaining exactly the 74 original ordered erasures.
[SYLforge's W1/W2 construction](https://github.com/CrocSwap/integer-mult-bounds/pull/7616).

Dropping the entrance correction from 991 into 196 changes final row 196
at input 991 by $+1/16$. Dropping the late correction from 7 into 185
changes final row 185 at input 2 by $+5/8$. The separate native checks
require the correct source frame for each direct MOVE and compare both
contractions with the two original chart maps in each direction on all
512 columns, including absolute phase.

## Complete invoice and application

The original 740→1062→1071 leg ranks are 2 and 1, and the new direct
rank is 3. The 401→1062→922 leg ranks are 3 and 2, and the direct rank
is 5. Productive fields stay fixed. Across 17 invocations the net paid
changes at ranks 1, 2 and 5 are −17, −34 and +17. Rank 3 cancels.
There are 110,332 paid positions, 22,461 productive positions, and
weighted surplus 1,424. With $a=1-C$ the signed-moment improvement is

$$17(1 + 2\,2^a-5^a)>0 \qquad (0<a<1),$$

by strict subadditivity at $5=1+2+2$. This establishes improvement of
the complete fixed invoice on the tested interval. Conversion to a
multiplication exponent also requires the positive compiler and outer
slacks, the retained BIT gate, the ordinary-cost ceiling, and the actual
word's precision and tape bounds.

The registered application first authenticates the original #7605
engines and retained bytes. It records the generated-source adaptations,
checks the full protected interfaces, executes the native application
and hands its actual word-bound result to the signed application. An
integer interval calculation checks the old and new full invoices at the
public gate, the slack point and both ends of the new price bracket.
The signed application has its own directed evaluator and checks the
outer assembly. The final stage compares the complete deterministic
certificate and both directed-price receipts to the frozen review files.

The five inherited premises are the all-column native operator and
spectator convention, the owned-erasure and suspended-center contract,
the uniform mixed-target compiler and chronological splitting, uniform
precision and fixed-tape accounting, and analytic decomposition and
integer recovery. The transfer uses #7605's conditional framework and
the original #7113 caller. Finite replay leaves those all-size premises
explicit. It provides no execution timing for a full multiplier.

## Fresh complete result

The complete application passed on the original source-bound word. Its
signed framework claim is $3651286663723/10^{15}=0.003651286663723$.
The separately tested public bound is $0.0036512866636$. It charges
782,673,236 ordinary units and the precision factor is 2,430. The tape
bounds are 298,434 monomial-map slots, 25,445,676,576 elementary records
and 43,932,448 scalar services. The native stage checked 51 affected
lineage chart pairs and 435 original clocks involving owned operands.
The signed catalogue covered 3,042 maps, 104 main boundaries and the
17-call signed application. All 54 strict and four functional predicates
passed. [Complete certificate](receipts/FINAL.json) and
[second directed price certificate](receipts/DIRECTED-PRICE.json).

## Independent replay of the frozen candidate

A fresh GPT-6.2 Sol high context wrote its check plan before examining
the word differences. Its integer-grid interpreter confirmed all 1,569
final rows, 74 ordered erasures, 630 private interfaces and 14 retained
downstream source observations, including the exact rows seen by their
first reads. Its second physical interpreter checked both directions and
absolute phase for both contractions. Changing the coefficient at candidate
clock 43,598 from −1/4 to −1/2 changed outputs 185 and 196. A global
phase mutation also failed. It reconstructed the signed paid, productive,
ordinary and tape bills and obtained the original precision factor 2,430.
[The scientific receipt](receipts/independent.json) gives the full exact
results, matched binary inputs, two directed interval prices and the
M-model gate. [The execution record](receipts/independent-run.json)
records which original-engine checks were assigned to the separate
native and signed application.

## Search scope

The pool was fixed before the semantic checks. The optimistic invoice
crossings and order after charging the scalar repair were as follows.

| Removed stays | Optimistic crossing | Final rank | Full ordinary bill |
|---|---:|---:|---:|
| 82 + 185 | 0.00365128666372 | 1 | 782,673,236 |
| 185 only | 0.00365098125226 | 2 | 782,690,236 |
| 82 only | 0.00365074956598 | 3 | 782,690,236 |

Removing the shared ADD requires charging the repair even in the two
single-stay screens. Each adds 472 scalar units per invocation. The
joint route saves 34,000 ordinary routing units across the caller,
yielding a net improvement of 25,976 after 8,024 repair units. Only the
top-ranked word was emitted for complete application. The finite search
does not establish optimality among other premixes or route edits.
