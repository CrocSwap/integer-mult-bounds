# Continuation storage in the selected BIT coefficient evaluator

This package proves an explicit space bound for the four continuation tapes in
Jose Manuel's PR2697 coefficient evaluator, pinned at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. It supplies one component of the
[first-node reserve handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18957549).
The supplier, selected cutoff and kappa are unchanged.

For fixed index and residue word lengths `I` and `R`, and ancestor depth `h`, set

```text
A = 2I + 4                       one VALUE record
B = R + 3                        one scalar record
T = max(A, B)
F(h) = (h + 1)T + hB

live nonblank continuation symbols <= F(h)
live symbols including four LEFT markers <= F(h) + 4
retained backing cells across the four tapes <= 2F(h) + T + B + 2
```

The last line counts blank cells retained in Python's four bytearrays. It is a
conservative bound on their lengths, not on Python object/allocator overhead.
The live bound is sharp in the admitted binary request grammar. The proof below
covers every depth, successful unary, binary, constant and unit-reset branch,
partial pushes and the copy-before-erase interior of `Stack.pop`.

This replaces no producer and proves no total reserve inequality. The
arithmetic arenas, serialized input program and raw fields, directories,
other caller tapes, placement and simultaneous callback lifetimes require
their own bounds. A capacity guard in `Arena` does not prove successful
execution. The numerical arena bound is deliberately left open.

## Proof and exact source boundary

The unchanged exports are `vendor/controller.py`, `vendor/records.py`,
`vendor/matrices.py` and `vendor/words.py`; the original NOTICE is retained.
[SNAPSHOT.json](SNAPSHOT.json) pins their source paths, commit, Git blobs and
SHA256 hashes. The verifier executes the exact authenticated source bytes in
dependency order. It bypasses bytecode caches and refuses preloaded modules.
Its live main input is the earlier
[uniform control proof](../selected-control-uniformity/PROOF.md), whose
stack grammar and asymptotic control result remain predecessor work.
This contribution adds the serialized coefficient, buffer distinction and
literal implementation checks.

Assume the callback was constructed successfully, its fixed-length word
operations succeed, its stack interfaces are private, and the four tapes
start erased with restored heads. Their backing arrays start fresh, or are
left by earlier successful evaluations with the same bounds. The supplied
coordinate is valid. We count only the two `Stack` instances in that callback.
There is no claim about arbitrary mutation, failed execution or ambient Python
state. All constant coefficients and divisions use the source's unit contracts.

A VALUE record contains one tag, two I-bit words, two WORD_END delimiters
and one RECORD_END, hence `A=2I+4` symbols. CONSTANT, MULTIPLY, PAIR and RETURN
each contain a tag, one R-bit word, WORD_END and RECORD_END, hence `B=R+3`.
Word LEFT/RIGHT markers are not serialized by `append_word`.

Consider a request of remaining depth d with fixed external continuation
content E. Its evaluation, including partial stack instructions, uses at most
`E+F(d)` symbols. At depth zero the VALUE is popped before one RETURN is
pushed, giving `F(0)=max(A,B)=T`. CONSTANT and UNIT similarly terminate with
one RETURN and no descendant request.

GOOD leaves one MULTIPLY of size B while its only child executes. Its charge
is at most `B+F(d-1)`. After the child returns, MULTIPLY and RETURN use `2B`;
the source pops both before pushing the result. Both fit `F(d)`.

PAIR pushes one PAIR and two requests. Either request is a VALUE of size A
or a CONSTANT of size B. The source evaluates the top request first. While
that descendant executes, the waiting sibling and PAIR add at most `T+B`.
While the second executes, the first RETURN and PAIR add `2B<=T+B`. At
combination, PAIR plus two RETURNs uses `3B`. This is at most `F(d)` for d>=1.
The source pops those records before pushing the result. Thus

```text
F(d) = F(d-1) + T + B = (d+1)T + dB.
```

A complete push bounds every partial push because it only appends symbols.
For pop, RECORD_END is erased first. Each subsequent `reverse.append` copies
one symbol before its source is erased, temporarily using that one vacant
cell. Therefore the combined main/reverse content never exceeds its value
at pop entry. The tag and operands are then erased from reverse. Returned
numerical words live in arenas, outside this category. The proof consequently
covers each individual tape write, not just loop boundaries. Once evaluation
returns, both main and reverse tapes are blank after their LEFT markers and
all four heads are restored.

For sharpness, take the complete depth-h binary grammar. If A>=B, the first
descent has h pending PAIR records and h+1 VALUE requests, totaling
`hB+(h+1)A=F(h)`. If B>=A, descend into each second child after retaining its
first result. At the last leaf return, h pending PAIR records and h+1 RETURNs
total `(2h+1)B=F(h)`. These establish grammar sharpness, without asserting
that every selected catalogue item realizes that grammar.

For retained backing lengths, each main tape has length at most `F(h)+1`,
including LEFT. During pop, `pending.reverse` holds at most `T-1` copied
symbols, while `values.reverse` holds at most `B-1`. Including their LEFTs
gives `T+B` more cells. The total is `2F(h)+T+B+2`. Popped blank regions are
included. Reusing a successful callback at the same depth cannot increase
any of these individual high-water marks.

## Reproduction and evidence

Use standard-library Python 3.12:

```sh
python3.12 -I -Werror -B research/selected-continuation-storage/verify.py
python3.12 scripts/research_package.py --package research/selected-continuation-storage
```

The registered normal and optimized commands compare fixed, typed receipts.
`verify.py --emit` prints a fresh receipt without changing the committed one.
[RESULT.json](RESULT.json) records the exact measurements.

The control census executes the pinned `Callback.weight`, `Stack`, word and
ring operations on 524 fixtures. It covers every level-homogeneous combination
of GOOD, two-real-child PAIR, either mixed real/constant PAIR, two-constant PAIR
and UNIT through depth three, in two word regimes. Binary stress cases extend
through depth six. Only the step/preparation oracles are replaced by finite
unit tables. This is control coverage, not selected geometry or a full caller.
All 12 nonempty pure-binary cases attain F exactly. Every write is metered;
direct cell scans check the meter after each pop.

Three separate 64-dimensional fixtures execute the real Callback constructor,
program/field validation and matrix preparation/fallback. They use q=3,
rank two, identity preparation, zero high digits and an explicit low header
with columns `(e0+e1,e2,e1,e3,...)`. These are test templates, not claims of
membership in the selected source catalogue. Their projector has
`P00=P10=P22=1`, and fallback maps field 0 to field 1. Both ancestors are
therefore real requests. Runtime `Word.inspect` is disabled. Each tape write
also receives a separate direct cell scan.

| Depth | I | R | Proved live bound | Observed live peak | Retained cells |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 3 | 20 | 20 | 54 |
| 1 | 14 | 3 | 70 | 70 | 122 |
| 2 | 20 | 3 | 144 | 144 | 214 |

The returned coefficients are respectively 1, 2 and 2 modulo 3. The source
program/field bytes and heads are preserved, and all numerical temporaries
and continuation content are erased. The larger retained lengths show why
`F(h)+4` cannot be used as a bound on backing cells.

Controls reject missing source erasure, a live budget one symbol too small,
using live content as retained extent, malformed stack delimiters/tags,
invalid numeric domains, changed source bytes, preloaded source modules,
stale bytecode caches and typed-receipt substitutions. These check specific failure modes, not the
full multiplication theorem. The written induction is not formal-kernel
verification; the literal fixtures are finite implementation evidence.

## Open next questions

- Bound the simultaneous live numerical words in the actual matrix/form and
  nested parent/leaf callbacks. This matters because a fixed arena capacity
  rejects exhaustion but supplies no success proof. Start by counting retained
  projector, fallback/form and arithmetic scratch words at each call site.
- Compose program/field, continuation, directory and count lifetimes with the
  payload bounds. Include extra empty callback markers and retained blank
  buffers if that is the chosen reserve convention. Start from the pinned
  `children.coefficient` parent/leaf overlap; total placement and larger
  recursive returns remain separate blockers.

At the 2026-10-15 20:31 UTC refresh, a complementary
[primitive arithmetic-scratch claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18957966)
was active. Coordinate there before repeating that component; its provisional
claim does not establish a complete numerical-arena bound.

Structured next questions and the changed task scope are in [TASK.json](TASK.json).

## Credit and engineering constraints

Jose Manuel, `jmbarrancoml`, supplied PR2697 and the retained control compiler.
PR2332's uniform-control proof already gives the generated grammar and
asymptotic stack argument. The exact source NOTICE retains PR2310/PR2188,
commdata2338's descriptor work, the PR2234 caller and earlier source lineage.
Nick Petalas's PR2749 supplies the complementary count-tape result; PR2743
supplies payload/key lifetimes, starship-s's PR2731 residual content, and
ywz65's PR2688 directory storage. This package claims none of those results.
Evidence is locally checked with a separate internal mathematical review;
independent human review and hosted CI success are not claimed here.
Apache-2.0, with the original source notice preserved.

Build the Lever led to the rerunnable literal-source census rather than a
numeric estimate. Prove It Works required returned coefficients, direct cells,
restored heads and source hashes. Power of Ten is applied to new code with
bounded fixture sizes and loop domains, explicit runtime checks and
warnings-as-errors replay. Its managed-allocation and dispatch deviations
are confined to this offline Python verifier: at most depth six, 524 synthetic
and three literal fixtures; only four authenticated byte strings are compiled
and executed in a fixed module namespace. Fixture method replacements are
limited to the documented oracles and meters, and restored in `finally` or
context-manager exits. The frozen source uses dynamically growing tapes and
data-dependent arithmetic loops; it is unchanged, with successful execution
an explicit premise. A numeric-arena proof and a physical controller are
follow-ups, not inferred from these finite checks.
