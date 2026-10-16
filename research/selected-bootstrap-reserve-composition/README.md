# Later selected bootstrap stages do not multiply external leaf stock

This is an independent conditional composition audit, not a new stock formula.
The retained PR185/PR387 argument and the pending [PR2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)/[PR2120](https://github.com/CrocSwap/integer-mult-bounds/pull/2120)
stock arguments imply that stages 2 through 7 need no additional external
leaf factor **if each preceding ordinary callee is internally completed at
all widths, with pointwise row and complete-spectator restoration**.
The same conditional parent coefficient, 6748 from PR2120, then suffices for
all fourteen recorded native/conservative fit guards. This does not establish
that an actual selected implementation meets those hypotheses.

The added evidence is a separately implemented nested-borrowing regression and
an explicit stagewise endpoint/space induction. A fault that negates an outer
row after each of the two body calls passes the whole completed endpoint,
because the negations cancel. In the explicit F3, stage-two, width-four
witness, an initial row value 1 becomes 2 after the first body return and
returns to 1 after the second. It fails the individual child-return contract
required to reuse the parent's stock. Thus checking only the final two-call
endpoint cannot establish this stock induction. This is a countermodel to a
weakened premise, not a bug report against the selected implementation.

No new exponent, supplier admission, changed cutoff or selected-frontier
change is claimed. The fourteen guard comparisons corroborate predecessor
arithmetic; they are not the contribution's novelty.

## Exact source and overlap boundary

Scientific base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The selected record binds PR1094's assembly and its PR589 BIT receipt.
The ordinary producer is **BIT m=64, maximum child rank 42**, not the separate
complex m=73 supplier that constrains the common atom exponent.
The BIT receipt has 28,416 live and 28,425 physical roles.

The source-pinned PR1087 assembler is read, not executed. Its seven updates
and both branch inputs reproduce the recorded exponents, gaps and cutoffs.
The retained PR185 proof's sections "Required completed leaf contract" and
"Nested row restoration and fixed tapes" supply the precise completed-leaf
hypothesis. PR387 extends that argument to a fixed number of stages and
explicitly says that the external allowance 252 is not an internal reserve
estimate. Neither 252 nor the historical m=120 increment 57,604 is used here.

Pending sources are frozen byte-for-byte under `sources/`, with their original
credit and notices retained:

| Source | Exact head | Used scope |
| --- | --- | --- |
| Adam Gall, PR2084 | `8001a23b003bec5dff5e61edec907b652c475932` | Conditional GL64 packet and completed-leaf stock argument |
| Nick Petalas, PR2120 | `378593574261e0b0915e7e8a83147aa640274fc8` | Conditional coefficient 6748 and ceiling-free depth bound |

These sources already state the generic fixed-stage reuse argument. This
package independently audits it; it does not claim that argument as new.
[PR2183](https://github.com/CrocSwap/integer-mult-bounds/pull/2183) separates
later-stage completion from first-stage arithmetic.
The replacement-caller work in PR2234, callee-substitution PR2399 at
`14458fda3cac4441c27980d584582ebbbb3e9233`, and spectator-completion PR2457 at
`0362534712dca8639917a733be62840d5ce55978` are complementary proposals, not
admitted implementations of the retained fourteen stages. Their checkers
are not imported, executed or certified here.

## Conditional endpoint/space closure

Fix an eligible prime `q>2^80` and a finite bootstrap depth `J<=7` before
choosing input widths. Use one native or conservative branch at a time.
For each stage set `w=ceil(e^s)` using its branch's fixed selected `s`.
Retain the following hypotheses, separately from any time estimate.

1. `A0` is an ordinary interchange for every required width. It accepts two
   complete chunks and arbitrary complete spectators, returns every external
   row coordinate pointwise, and obtains its own borrowing internally. Its
   additional externally supplied row divisor is one.
2. The same selected full-cover constructor is available at every fixed stage.
   For fixed atom width w it has floor-child bound `42*floor(n/64)`, terminates
   below 64 atoms, preserves exposed ancestors, and restores each child's row
   before the next child uses it. Its complete physical packet divisor is
   `W_q(w)=28425*|GL64(F_q)|*q^(4096*(w-1))`.
3. Once the borrowed stock fits, this constructor's ordinary wrapper has its
   stated endpoint using only already completed previous-stage ordinary
   calls for leaves, routing, remainders and high-part exchange. Padding is
   removed only after a completed endpoint preserves the genuine rectangle.
   This is a uniform endpoint contract, not merely an eventual asymptotic
   statement. All required complete-spectator/radix conversions are included.

Let `D(n)=0` below 64 and `D(n)=1+D(42*floor(n/64))` otherwise. Choose the
parent's divisible stock from the original width before choosing the borrowed
width or body:

```
S(e,w) = W_q(w)^D(e).
```

At a node, expose one packet and pass its quotient to a child. Every child
needs at most one lower power. Since that child restores the supplied row,
siblings and successive residuals reuse the same quotient. At an ordinary
leaf the external factor is one by hypothesis 1, or its inductive successor.
Neither the two wrapper calls nor the number of bootstrap stages multiplies
this external divisor. This says nothing about the leaf's internal workspace,
number of tapes, padding/time constants or recursion cost.

For each `j=1,...,J`, define `Aj` to use the new constructor above its recorded
cutoff and `A(j-1)` below it. Suppose `A(j-1)` is internally completed at all
widths. The packet induction supplies exactly the same `S(e,w)` as at stage
one. The inherited bound from PR2120 is

```
log_q S(e,w) <= 6748*w*(1+log2 e).
```

The recorded cutoff satisfies the sufficient fit guard with
`ell=ceil(log2(8*6748))=16`. Therefore stock fits above that cutoff.
Hypothesis 3 completes that branch, while `A(j-1)` completes the below-cutoff
branch. Thus `Aj` has the same all-width endpoint/space contract and zero
additional external factor. Induction proves this for every `j<=J`.
Coarse calls strictly decrease n; ordinary calls strictly decrease j. The
construction has no circular dependency on its own completion.

The numerical checks reconstruct, for each branch,

```
a0 = 384599/10^10
s = min(bit_lower, (1-10^-24)*complex_lower) - 10^-27
a_j = (1-s)*s + s*a_(j-1)
delta_j = min(s-a_j, 1-a_j-s, 1-a_j-s*(1-a_(j-1)), 1-s)
L_j = max(ceil(36/delta_j^2), ceil(1032/delta_j)).
```

They verify the source records and `L_j>=3`, `L_j*delta_j^2>=36`,
`L_j*delta_j>=2*(4+16)`, and `0<delta_j<=1-s` for all fourteen stages.
The conditional fit lemma is Josie Elliston's PR1965 result, not a new proof
here. None of this supplies its H2 uniform time estimate. In particular,
endpoint/space closure alone does not assign the improved running exponent
to the completed callee. Actual uniform primitive bounds remain necessary.

## Independent finite evidence

`verify.py` expands a borrowed-high-digit wrapper using an explicit bounded
work stack, not recursion. Its old callee is either a direct swap or another
completed wrapper of smaller stage. Each wrapper borrows one high digit,
executes the two reversed body calls with all five algebraic steps,
then exchanges the high digits. A nontrivial involution reverses each body.
Every call records and checks all non-target rows at its return.

The fixture uses digit vectors over F3 and F5, widths 1 through 9 and stages
0 through 7. It checks 144 complete linear maps on 1,872 basis columns,
including three arbitrary outer spectator coordinates. Widths below three
use the old completed callee. These are finite algebraic fixtures, not an
all-size q-adic tape implementation, GL64 payload run or stock-size model.
The universal implication rests on the conditional induction above.

Controls omit the final high exchange, mutate stage fields and source bytes,
exceed stage/width capacities, corrupt/miss the required receipt, and insert
the canceled row fault described above. Public-CLI source and receipt controls
run in an isolated copy under `-O`; no frozen input is modified. Checks use
explicit exceptions rather than removable assertions. Replays never generate
or repair `RESULT.json`.

From the repository root, with standard-library CPython 3.12:

```
python3.12 -Werror -I -B research/selected-bootstrap-reserve-composition/verify.py
python3.12 -Werror -I -O -B research/selected-bootstrap-reserve-composition/test_verify.py
python3.12 scripts/research_package.py --package research/selected-bootstrap-reserve-composition
```

Expected primary output is `PASS_SELECTED_RESERVE_COMPOSITION stages=14
sigma=6748 wrappers=144 child_return_control=1 no_new_kappa` on one line.

## Open next questions

- Bind one actual selected ordinary callee to hypotheses 1 and 3 at all widths,
  including its below-cutoff fallback and each child-return checkpoint.
  This matters because a correct final wrapper endpoint alone misses the
  canceled-row countermodel. Begin with one source-bound borrowing invocation;
  physical all-size lowering and arbitrary complete-spectator conversion
  remain blockers.
- Bind uniform local tolls and callee substitution at every required site
  before invoking H2 and claiming the stage's time exponent. PR2087 and the
  PR2399/2457 components are relevant predecessors. A numerical stock-fit
  certificate cannot provide those implementation/time contracts.

## Credit and limits

The nested restoration argument is Rohan Arun's retained PR185/PR387 work.
Josie Elliston supplied PR1956/PR1965's cutoff audit and separation of time
from stock; ToikY supplied PR1990's independent audit. Adam Gall supplied
PR2084's conditional selected BIT stock implication, and Nick Petalas supplied
PR2120's refinement. DreamingOfClouds' PR589, eumemic's base, Rohan Arun's
selected PR1094 and Jeremy Kothe's PR1087 retain construction credit.
Callee and spectator follow-ups remain credited to commdata2338 and ywz65.

This package is submitted for review. No independent human review, full
selected cold replay, physical/compiler admission, H2
implementation proof, precision/tape discharge, formal kernel or hosted-CI
success is claimed. Frozen sources and the selected result are unchanged.
New work follows Apache-2.0; retained source text keeps its original attribution.

The Python runtime allocates managed integers, matrices and test objects.
This is a Power-of-Ten rule 3 deviation, bounded by widths at most 9, stages
at most 7, 21 state rows, word capacity 50,000 and source capacity 64 MiB.
Each state matrix has at most 441 entries; call nesting is at most 15.
Rule 9's test dispatch and rule 8's fixed dataclass declaration use standard
Python machinery with fixed targets. The verifier has no dynamic imports,
code evaluation or predecessor execution. Tests load only this fixed local
verifier with `runpy`, and subprocesses have 30-second timeouts and scoped
cleanup. Reassess these bounds before expanding the fixture domain.
