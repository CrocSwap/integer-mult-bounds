# Independent union-support census of the seven-label exclusion

A separately implemented complete census corroborates Nicholas Stone's
[#2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973) exclusion
of restored universal seven-label words of length 20. All five admissible
weight-split representatives have zero hits. The length-18 control also has
zero hits. Together with the directly checked existing length-24 witness,
this corroborates `22 <= f(7) <= 24` in Ross Richardson's PR943 singleton
prefix-walk model. It is not a new bound, a supplier admission or a change to
selected kappa.

The new [C++20 engine](census.cpp) uses an iterative stack of complete prefix
states and a bound on the **union** of same-parity pair supports. It neither
imports nor adapts the old or corrected census engines. The
[Python oracle](oracle.py) instead partitions word positions into positive
even blocks and checks literal pairwise-XOR coverage. This supplies the
independent full-domain implementation missing from #2973's open questions.
[#2984](https://github.com/CrocSwap/integer-mult-bounds/pull/2984) independently
accelerates the predecessor's representation but explicitly retains its DFS
and pruning logic. This package addresses a different verification gap.

## Evidence

[FULL.json](FULL.json) contains fresh uncapped runs from the empty prefix,
not shard receipts or a validation of historical counters. `entered` counts
accepted prefix states including the root. `attempts` counts label extensions
before rejection, so neither count should be compared to another engine's
node count without reconciling its definition.

| Length | Weight split | Entered prefixes | Attempted extensions | Hits |
| ---: | ---: | ---: | ---: | ---: |
| 20 | 10,10 | 322,881,109 | 2,260,000,903 | 0 |
| 20 | 10,9 | 112,232,469 | 785,502,139 | 0 |
| 20 | 10,8 | 6,082,255 | 42,550,772 | 0 |
| 20 | 9,9 | 14,322,217 | 100,157,693 | 0 |
| 20 | 10,7 | 25,087 | 174,540 | 0 |
| 18 | 9,9 | 239,661 | 1,675,590 | 0 |

Every run returns exit 0, `complete=true`, `cap=0` and an empty witness file.
All branches are rejected before a candidate restored leaf survives. These
are not counts of all restored words. GCC 14.2 and Clang 19.1 independently
compiled the same new source and produced identical complete JSON receipts.
The registered GCC replay of both obligations took 115.0 seconds; Clang's
full command took 86.9 seconds on the recorded Linux WSL2 host. This is not a controlled speed comparison with #2973 or #2984.
[ENVIRONMENT.json](ENVIRONMENT.json) records commands and versions.

[QUICK.json](QUICK.json) records 270 exact engine/oracle comparisons over
all splits at `(n,L)=(2,4),(2,6),(3,6),(3,8),(4,8),(4,10),(5,10),(5,12)`. Each split is
run with the support bounds enabled and disabled. Every witness set must
match, including zero-hit splits. With support pruning disabled, every
restored-leaf count must also match. Canonical universal counts are
`3,15,10,182,26,1310,0,1116`. These positive cases test revisits as well as simple
walks. The oracle enumerates 51,975 restored canonical words at `(5,12)`.

Twelve controls check caps, malformed parameters and failed witness output.
Four compiled mutants test a bit-0 partition, rejection of revisits, an
unsound strengthened support bound and omission of the last label. All are detected.
The full `(4,10)` comparison also passes an undefined-behavior/bounds sanitizer
build. Critical checks remain enabled under Python `-O`.

## The old error, reproduced at its source

The prefix states of `01021323` are
`[0,1,3,2,6,4,12,8]`, followed by the restored zero. Their pairwise XORs
cover all 16 masks. Weight parity gives sizes `4,4`; bit 0 gives `6,2`.
The bit-0 within-group collision excess is 8, exceeding the substituted
balanced budget `2*C(4,2)-7 = 5`. Its valid actual-size budget is
`C(6,2)+C(2,2)-7 = 9`.

The pinned [PR2542 engine](../universal-f7-singleton-seedb859517b/engine.py),
`cyclic_census`, groups new points using `nq & 1`. Quick replay calls that
actual function on this one forced simple word. Without a collision budget
it returns one leaf and one universal word. With budget 5 it returns neither.
The new engine and oracle do not call that function. This historical audit
subject is the only predecessor code executed here.

The affected word-census exclusions are PR2542's `n=7,L=18,budget=9`
invocation, PR2634's vendored word traversal and PR2691's C completion of
that traversal. Their old counters reproduce a filter, not its necessity.
The new six-case census provides separate corrected exclusion evidence;
it does not make the old prune sound. The set-level lemmas and explicit
witnesses in those packages require separate assessment. In particular,
this result does not revoke later set-level Fourier or Sidon arguments.
Frozen predecessor files stay unchanged.

## Why the new enumeration is complete

For a restored word of even length `L`, let `P` be its distinct nonclosing
prefix states. A prefix at index `d` has weight parity `d mod 2`. Let `E,O`
be the distinct even/odd states, with final sizes `s,t`. Both sizes are at
most `L/2`, since the closing zero repeats the initial zero. Revisited
points add no pairs and no capacity.

At a partial prefix, let `e,o` be the current sizes and let

```
U = {x XOR y : x,y in E, x != y} union {x XOR y : x,y in O, x != y}
V = {x XOR y : x in E, y in O}
```

`U` is maintained as one union, not two separate support counts. A completion
can introduce at most

```
C(s,2) + C(t,2) - C(e,2) - C(o,2)
```

additional same-parity pairs, and at most `s*t-e*o` additional cross pairs.
Each additional pair contributes at most one new mask. Therefore a universal
completion necessarily satisfies

```
|U| + C(s,2) + C(t,2) - C(e,2) - C(o,2) >= 2^(n-1)-1
|V| + s*t-e*o >= 2^(n-1)
```

These bounds include overlaps between the two same-parity supports, unlike
#2973's separate within-side excess bound. Both remain necessary with
revisits to already visited states. A new state adds its XORs with every
previous state on the appropriate side. Copying the complete node into the
next stack slot makes backtracking restore all sets and counters together.

Other pruning is elementary:

- Only labels `0..used` may follow, with `used<n` for a new label. Every word
  has exactly one such representative under coordinate relabeling. There is
  no self-avoidance restriction and no shard, heuristic or seed restriction.
- With `r` positions left, each currently odd-count label needs at least one
  occurrence and each unused label at least two. Reject when
  `popcount(position) + 2*(n-used) > r`.
- Reject a new point when its side is already full. After depth `d<L`, only
  `L/2-1-floor(d/2)` nonclosing even positions and
  `L/2-ceil(d/2)` odd positions remain. Reject an unreachable target size.
- At a leaf, check restoration, all `n` labels used, the exact split and
  `|U|+|V|=2^n-1`. The zero mask comes from a point paired with itself.

The independent slot-partition oracle enumerates each restored canonical word
once. Its blocks are the positions bearing one label. Every block has positive
even size; ordering blocks by their smallest positions fixes first-occurrence
order. This enumeration uses no prefix feasibility or collision pruning.

### Split coverage and the retained bound

At `n=7,L=20`, basic pair capacities leave, up to swapping sides,
`(10,10),(10,9),(10,8),(9,9),(10,7),(9,8)`. To remove `(9,8)`, let
`A_x,B_x` count unordered within-side representations of an even nonzero
mask, and let `a,b` be their collision excesses. Universality gives

```
B0 = C(s,2)+C(t,2)-63, a+b <= B0
sum_x A_x*B_x >= ceil((s*t-64)/2)
sum_x A_x*B_x <= B0+a*b
```

The lower bound double-counts cross-pair collisions:
`sum_y C(r_y,2)=2*sum_x A_x*B_x`, with `r_y>=1` on all 64 odd masks.
For the upper bound, expand `A_x*B_x` on shared support and bound the residual
product by `a*b`. At `(9,8)`, `B0=1`, so `a*b=0`, whereas the lower bound
is 4. The remaining five splits are precisely the complete L20 runs.
[oracle.py](oracle.py) recomputes this finite split list independently.
At length 18 the same argument leaves only `(9,9)`.

Rotating a closed word by one position translates `P` by an odd-weight state,
swapping `E,O` without changing `P+P`. Relabeling by first occurrence restores
canonical form. Thus the mirrored splits need no separate exclusion.
Appending repeated pairs of any already used label preserves restoration and
coverage, so a shorter restored universal word would yield one of length 20.
Odd lengths cannot restore. The zero-hit runs therefore corroborate `f(7)>=22`.
The literal existing upper word `010201030102010345464546` restores and covers
all 128 masks, giving `f(7)<=24` independently of the census.

## Reproduce

Python 3.12 standard library and a C++20 compiler are required. The default
`c++` must support the warnings in `verify.py` and UBSan/bounds sanitizers.
The registered hook does not install a compiler. From the repository root:

```sh
python3.12 -I -O -Werror -B research/f7-union-support-audit/verify.py
python3.12 -I -O -Werror -B research/f7-union-support-audit/verify.py --full
python3.12 -B scripts/research_package.py --package research/f7-union-support-audit
```

Expected markers are `PASS_F7_INDEPENDENT_QUICK` and
`PASS_F7_INDEPENDENT_FULL`. Each command compiles fresh native code and uses
a private temporary directory. `--compiler clang++` chooses the second tested
compiler. `--emit` prints reconstructed JSON rather than comparing it with
the committed receipt. Full mode has a 540-second native budget; timeout,
nonzero exit, a cap, a changed counter or a nonempty witness file fails.
Quick and full commands are separate obligations; full mode alone does not
run the small-domain controls. No predecessor artifact is regenerated.

For the native CLI, run `census n L s t mode cap hits-file`, with `mode=1`
for the proved support bounds and `mode=0` to disable them. `cap=0` requests
an uncapped traversal; a positive cap counts attempted label extensions and
returns exit 2 with `complete=false` when reached. Exit 1 is an input, I/O or
internal failure. Only exit 0 with `complete=true` can support an exclusion.
The witness path is overwritten, so use a fresh workspace.

## Open next questions

Does a length-22 seven-label universal word exist? It would decide the
remaining gap in this abstract model. First derive its admissible weight
splits and estimate a separately bounded search before extending this engine,
whose enforced maximum length is 20. No length-22 exclusion or automatic
family expansion follows from this audit.

A formal proof of the full traversal and pruning remains open. The written
completeness argument, independent oracle and cross-compiler runs are executable
evidence, not a proof-assistant kernel check. A first formalization step is
the two union-support completion inequalities, including revisits.
Structured questions and blockers are in [TASK.json](TASK.json).

## Scope, attribution and engineering limits

Scientific base main is `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority
revision 6. [SOURCES.json](SOURCES.json) pins the exact old/corrected source
subjects and proposed exclusion receipt. [TASK.json](TASK.json) records the
bounded scope expansion, freshness, live overlap and canonical claim.
No old engine contributes candidate pruning or a full-run result to the new
engine. The result does not prove a statement outside the PR943 model.

Credit Ross Richardson for that model, Aaron Wang for PR2542/PR2634 and the
set-level/census lineage, Nicholas Stone for PR2691, the parity correction,
corrected exclusion and counterexample in PR2973, Tekalign for PR2984's
separately scoped representation acceleration, and Douglas Colkitt for the
retained research and source-binding framework. Nick Petalas contributes this
independent union-support implementation, slot-partition oracle and replay.
Apache-2.0. Substantial automated assistance was used in research, implementation,
checking and writing. No independent human or formal-kernel review is claimed.

Build the Lever led to a retained second implementation rather than another
receipt-only replay. Prove It Works required exact complete witness-set
comparison and actual uncapped native runs. Test Behavior, Not Implementation
led to positive universal fixtures and compiled incorrect implementations.

Power-of-Ten inspection found no new recursive code. The native core uses
21 fixed stack slots, two 64-bit words per mask, at most ten points per side,
and a hard `2<=n<=7, 2n<=L<=20` input boundary. Its loop bound is twice
`sum(n^d,d=0..L)`, which fits uint64 throughout that domain. Every new function
is under 60 lines. All acceptance checks are explicit under `-O`, native
compilation treats the listed warnings as errors, and sanitizer controls run
in quick mode. `ruff check research/f7-union-support-audit` applies the local
strict diagnostic list. The one E402 suppression permits the explicitly
bounded sibling import under isolated Python. Each native process has a timeout and temporary outputs are
removed on success or failure.

Rules 3, 8 and 9 need bounded runtime deviations. Python and C++ stream/runtime
libraries allocate; Python's slot oracle has a two-million-state iteration
and worklist limit in its enforced small domain. The new native search itself
uses fixed-capacity value storage and no callbacks. The historical control
loads one authenticated old module, makes two depth-eight, 100-node-capped
calls and checks their actual results. That old recursive code is an audit
subject, not a dependency of the new search. Reassess resource and runtime
controls before widening the domain. Hosted CI, the full selected supplier
cold replay and all-size multiplication obligations are not claimed passed.
