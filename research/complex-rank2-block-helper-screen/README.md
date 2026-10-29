# Rank-2 block-helper inventory screen

**Exploratory exact planning bound; no new supplier or selected kappa.**

The pinned task/scope, source hashes and replay contract are in
[TASK.json](TASK.json), [SOURCES.json](SOURCES.json) and [VERIFY.json](VERIFY.json).

## Question and contract

Can the selected #1094 complex local word replace blocks of eight rank-1
children implementing one 2-by-2 matrix product with one recursive rank-2
helper, and what is the best optimistic moment if every eligible block is
replaced?

The proposed helper contract is the ordinary map
`(A,B) -> AB` for two 2-by-2 matrices. Its schoolbook implementation uses
eight scalar products. If eight rank-1 children in the selected local word
form one complete, disjoint instance of that map, they can be represented as
one rank-2 recursive call. For `t` such blocks per call, the changed local
profile is

```text
n1 = 2412 - 8t, n2 = 418 + t,
n3 = 432, n4 = 142, n5 = 82, n8 = 8,   0 <= t <= 301.
```

For `A=[[a,b],[c,d]]` and `B=[[e,f],[g,h]]`, the eight terms are
`ae,bg,af,bh,ce,dg,cf,dh`; the four outputs are respectively
`ae+bg`, `af+bh`, `ce+dg`, and `cf+dh`. Thus this is one coupled four-output
matrix product, not a direct sum of independent scalar products.

Each block lowers the paid rank mass by six; the optimistic screen returns
those six units to the rank-51 idle remainder. It charges no block extraction,
input/output framing, addition, source restoration, hosting, precision, or
other consumer cost. The arithmetic therefore prices a proposed interface; it
does not show that its eight-term blocks occur in the selected word.

## Exact screen

The prescribed baseline example passes. The parent model has `m=73`,
`W=896/9` live families per call, nine stages, centre charge 64, and the
halving-guard idle rank cap `R=51`. The source-bound selected local profile is
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` with local mass 5,586 and idle
mass 1,646.

The best profile in this one-rewrite class uses all 301 complete blocks:

```text
{1:4, 2:719, 3:432, 4:142, 5:82, 8:8}
local mass = 3,780; idle mass = 3,452; total = 7,232.
```

Using `ceiling.ceiling()` with exact rational intervals at grid `10^-12`, its
optimistic root is
`a in [0.002632122649, 0.002632122650]`, hence the complex-side planning cap
is `kappa <= 0.002625212768...`. The endpoint signs are certified by the
parent interval engine. Even this maximum inventory does not reach the
planning target `kappa=1/99`.

The exact first point where this optimistic complex ceiling clears the
unchanged selected bit root is `t=22`:

```text
{1:2236, 2:440, 3:432, 4:142, 5:82, 8:8}
local mass = 5,454; idle mass = 1,778.
```

At `a=bit_lower`, the previous inventory (`t=21`) has certified moment
strictly above one, and `t=22` has certified moment strictly below one. The
verifier prints the exact rational intervals for both signs. This is only a
zero-overhead threshold for source matching; it does not price the proposed
block extraction or its consumers.

More importantly, with the selected bit supplier unchanged, the overall cap
is still the bit-side value `b/(1+b)`, where the selected assembly has
`b=1733427039589844234749/1000000000000000000000000`; this is below a 5%
increase over the selected `kappa=0.001672660197076918`. This helper change
alone cannot meet the 5% system target. It could matter only as part of work
that also raises the bit-side bound.

For each `a>0`, replacing a block strictly lowers the relaxed moment because,
after factoring out `73^(-(1-a))`, its decrease is

```text
8 - 2^(1-a) - 6*51^(-a) > 0.
```

The expression is zero at `a=0` and has positive derivative for `a>=0`.
Thus `t=301` is the best ceiling in this restricted rewrite class, not a
sampled point.

## Reproduction

From the repository root (Python standard library only):

```sh
python3 -B research/complex-local-word-ceiling/verify.py
python3 -I -B research/complex-rank2-block-helper-screen/verify.py --check
```

The first command prints `PASS_COMPLEX_LOCAL_WORD_CEILING`. The second checks
the selected-source pins, the full per-call rank/idle bill, the exact root
bracket and both endpoint signs, the strict improvement over the original
ceiling, the unchanged bit cap, the 5% stop test, and out-of-range controls.
Neither command replays the complete selected construction.
Use `python3 -I -B research/complex-rank2-block-helper-screen/verify.py --write`
to regenerate the exact rational receipt `RESULT.json`.

## Scope, source and credit

Base: `20ecf2891d80b5acf18f980b2164fb44ea7faa90` (the session's pinned
canonical main). The
selected record is `certificates/selected-result.json`, kappa
`836330098538459/500000000000000000`; its reviewed source is
`docs/research/community-batch1099-review.md`, its assembly is
`research/community-frontier1094-audit/ASSEMBLY.json`, and its source manifest
is `research/community-frontier1094-audit/SELECTED-SOURCE.json`. The finite
coverage identity is attributed to PR #1012. The ceiling lemma and exact
interval engine are Douglas Colkitt's
`research/complex-local-word-ceiling/` contribution, prepared with Claude
(Anthropic) assistance.

This screen does not find any complete eight-term block in the selected
producer, prove compatibility with its frames, or charge the physical
realization of a block. It does not admit a supplier, change kappa or the
selected frontier, or establish the full multiplication theorem. No
independent human review is claimed. Prepared with OpenAI Codex assistance.

## Relation to nearby work

This candidate changes one *complete* 2-by-2 matrix-product subword. It is
different from PR #1960's direct sums of consecutive independent rank-2/rank-3
children, from the rank-one common-product/output-anchor claims in #1167, and
from PR #2224's six-coordinate `Q[S3]` convolution factorization. Those are
close block or bilinear mechanisms, so this package makes no novelty claim
beyond the exact object and moment screen stated here. It also differs from
PR #3874's combined ideal-lever grid: it changes the local parent subword and
releases the resulting six units of rank mass per block into idle capacity.

## Open next questions

Inspect the exact selected producer behind #1094 and determine whether even
one disjoint eight-term subword has the complete 2-by-2 input/output map above.
If so, price its frame, addition, restoration, hosting, and bit-side effects
before seeking more blocks. Otherwise stop this contract. Any continuation
must address the unchanged bit cap as well as the complex moment.
