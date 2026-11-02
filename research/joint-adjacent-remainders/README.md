# Two adjacent remainders with shared quotient corrections

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped proof and arithmetic construction, with exact finite
corroboration. After one base-p digit split, the remainders modulo p+1 and
p+2 share a correction predicate. The joint core uses exactly two correction
comparisons, versus a minimum worst case of three for separate correction
trees in the model below. Its input prefix is sharp:

    p >= 2,       0 <= x < p(p+2).

There is no new kappa, physical CRT implementation or selected-frontier
change. No inherited framework assumption is discharged.

## Construction

Write x=ap+r, with 0<=r<p. The input bound gives 0<=a<=p+1. Prepare
q1=p+1, q2=p+2 and 2q2 once per radix, and compute d=r-a and e=d-a.
Use this tree, whose leaves give the quotient corrections (c1,c2):

```text
d < 0?
  yes: e < -q2?  yes -> (1,2), no -> (1,1)
  no:  e < 0?    yes -> (0,1), no -> (0,0)
```

The two remainders are d+c1*q1 and e+c2*q2. The implementation uses prepared
constants at the leaves, so the trusted core has two subtractions, two
ordered comparisons and at most two additions. It uses no division,
remainder, multiplication, lookup or loop after the digit split.

Per-radix preparation uses three additions and one multiplication to form
q1, q2, 2q2 and the range limit p*q2. The split uses one divmod by p. When
p=2^k, it can instead use one shift and one mask. These are symbolic
operation counts, not measured time or physical instruction prices.
The wrapper also validates inputs. Its validation comparisons are outside
the trusted correction-core count and must be priced by a caller that
repeats validation. Forming the constant -q2 can be done once per radix;
the Python core spells it as unary negation.

## Proof of the identity

The uncorrected residues are d=x-aq1 and e=x-aq2. It remains to choose the
unique constant corrections making each output canonical.

If d>=0, then r>=a and 0<=d<q1. Also e=r-2a>=-a>=-(p+1)>-q2 and e<q2.
Consequently c1=0, and c2 is 1 exactly when e<0.

If d<0, then -q1<=d<0, so c1=1. Here r<a, hence e<0. The bounds on a,r
also give e>=-2(p+1)>-2q2. Thus c2=2 exactly when e<-q2, and c2=1 otherwise.
At e=-q2 the correct choice is 1. These are all four leaves above.
Both results lie in their canonical residue intervals, proving the identity
for every integer p>=2 and every input in the stated prefix.

## Exact comparison model and sharpness

Fix p. A correction tree may evaluate arbitrary binary predicates of the
input digits, but each leaf returns a constant integer correction pair.
It has no uncounted table selection, floor/mod operation, branch or
data-dependent arithmetic producing the correction pair. The final affine
remainder arithmetic is outside this decision-tree lower bound. This is a
bound on correction trees, not on every possible remainder algorithm.

All four correction pairs are necessary. These four inputs lie in the
legal prefix and attain them:

| x | Correction pair |
| --- | --- |
| 0 | (0,0) |
| p | (1,1) |
| p+1 | (0,1) |
| p(p+1) | (1,2) |

A depth-one binary tree has at most two leaves, so at least two comparisons
are necessary in the worst case. The displayed depth-two tree is optimal.

For separate trees, c1 has two attained values, so its tree performs at
least one comparison on every input. The second correction has three
attained values, so its tree needs depth at least two at some input.
Their total worst case is therefore at least three. A first tree testing
d<0, and a second testing e<0 and then e<-q2 when necessary, attain three.
Sharing the first predicate reduces this exact model's worst case by one.

At the first excluded input x=p(p+2), the digit quotient is a=p+2 and the
true correction pair is (2,2). This is a fifth pair, distinct from all four
already attained below the boundary. A depth-two tree has at most four
leaves. Therefore no two-comparison constant-correction tree covers any
larger initial integer interval. The largest such interval is exactly
0<=x<p(p+2), even if its predicates differ from this construction.

The moduli are consecutive and hence coprime. The complete canonical CRT
interval has (p+1)(p+2) representatives; this prefix omits its top p+2
representatives. No complete-interval tree is claimed here.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/joint-adjacent-remainders/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/joint-adjacent-remainders/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/joint-adjacent-remainders
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/joint-adjacent-remainders --check-source-history
```

Replace the interpreter path on another machine. The own verifier is
read-only and requires neither Git nor a network. Expected marker:
`PASS_JOINT_ADJACENT_REMAINDERS`. The runner registers both Python modes.

The verifier checks all 93,597 legal inputs for p=2,...,64 against Python's
integer remainder and division operations. It enumerates all four leaves
at every radix, 315 explicit small-radix sharpness witnesses, 176 additional
large-radix boundary cases through p=2^1024, and eighteen rejection controls.
Strict equality at each decision boundary is included. Static inspection
rejects division, remainder, multiplication, calls and loops in the trusted
core. Its three syntactic ordered predicates lie on two alternative paths;
every executed path evaluates exactly two. Finite checks corroborate the
quantified proof rather than establish its universal quantifiers.

The implementation caps radix length at 4096 bits. The proof has no bit-length
cap. No historical scientific replay, Lean build, Docker run or selected
replay is required or supplied.

## Scope and sources

Base: canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority
revision 8. The binding-only selected baseline passed at PR6030,
kappa=781451/250000000. Task and selected metadata are historical provenance
in SOURCES.json; this standalone proof and checker have no live predecessor
inputs. Frozen evidence and source credit lines remain unchanged.

This is an originally posed arithmetic side result on the
uniform-transfer-audit card. It does not identify a selected caller using
these moduli or prove its range bound. Radix division, quotient correction,
the Chinese remainder principle and binary decision-tree leaf counting are
classical. No claim of literature priority for those methods is made.
The joint tree, exact range statement, proof and checker are produced by
Nick Petalas. Independent human and formal proof-kernel review are unclaimed.

Entry overlap checks included live PR bodies and Discussion claims, local
reservations, an expanded 500-entry account history, main README object and
formula searches, and merged PR searches. The cached scan reports complete
remote pagination for 351 open PRs and 6,247 Discussion records. Its local
sparse note search was incomplete; direct Git searches supplemented it.
Unpublished work and arbitrary nested code were not fully searched.

## Open next questions

The structured questions and blockers are in TASK.json.

1. Bind the core to one encoded recovery caller with these moduli and a
   proved input-prefix bound. Price the split, preparation, validation,
   arithmetic, movement, branch history and restoration. None of those
   physical costs is inferred from the comparison saving.
2. Classify correction pairs and construct an optimal tree on the complete
   CRT interval. Start with the omitted top p+2 representatives. That larger
   interval is outside this theorem and implementation.

## Code constraints

Functions are below sixty lines. The trusted core has no recursion, loop or
indirect call. The verifier has fixed finite grids; its largest exhaustive
inner range has 4,224 inputs. Arithmetic capacity is bounded by the 4096-bit
radix limit. Explicit exceptions preserve checks under optimized Python.
Warning-strict normal and optimized execution and AST inspection provide
available diagnostics; no external linter or type checker is installed.

Power of Ten rules 3 and 9 have managed-runtime deviations. CPython allocates
integers and containers and dispatches their operations dynamically. Fixed
input/grid sizes bound live algorithmic state; no Python allocation-free
or native fixed-storage implementation is claimed. The rejecting-control
helper has only prepare and reduce_pair as callback targets. An embedded
deployment requires a separately priced fixed-storage implementation.
