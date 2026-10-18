# Independent source-level initialization and validation audit

The frozen `Consumer.apply` prefix, from entry through immediately before
`packet_engine.run`, has exactly **4096 additional live residue Words** at its
residue maximum. Its exact additional index-Word maximum is

\[
 K(h,H)=
 \begin{cases}
 18,&h=0,\\
 22,&h>0\text{ and }H=0,\\
 23,&H=1,
 \end{cases}
\]

where `h` is the validated program depth and `H` indicates whether its admitted
chronological program contains a `UNIT_KIND` step with `half=1`. A half step is
possible only for positive depth. This is a successful-path, source-level
numerical-lifetime statement. The two category maxima occur in different phases.

The source export is unchanged from PR2801 commit
`e2564b80b86fb77610b4b78701e5446a76fbe962`, retaining the PR2697 runtime at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The package pins, rather than current
upstream contents, determine the covered implementation. The independent analysis
was performed by the Codex `math-storage-lifetimes` specialist. Runtime code and
the underlying arithmetic are predecessor work; this note and the integer event
model are new review material under the repository's contribution license.

## Assumptions and accounting boundary

* The residue arena and index arena are distinct. `L_R,L_I` count **all** their
  live Words at `Consumer.apply` entry, including arguments, modulus, ring one,
  context cap and unrelated caller residents. An entry resident is never
  counted again when borrowed by a subroutine.
* The context is the selected dimension `d=64`; `64 <= n < 128` for the current
  parent width. The entire finite encoded program is admitted by the source
  validation predicates, has final width `n`, and has the incoming field prefix
  of exactly `h+1` records. The root word has its source-required canonical high
  margin. The root coefficient is a unit in the valid fixed ring `M=q^w`,
  `q` prime and `w>=1`.
* The source vocabulary/specification lookups, binding and plan construction are
  numerical-arena neutral. Program, ring, indices and fields use the source's
  matching arenas; hooks and observations do not allocate there. All capacities
  and arithmetic margins suffice, and execution is sequential and successful.
* The old directory contains exactly the positive encoded number of complete
  physical prefixes, with valid frozen codes and high digits. Its finite size,
  positive spectator counts, and the index width may otherwise be arbitrary.
* A Word is counted through allocation initialization, use and final erasure,
  until `Arena.free` releases it. Count tapes, serialized programs and fields,
  directories, four continuation tapes, source/output payload, fixed control,
  LEFT markers, Python heap objects and retained backing capacity are separate
  categories. The arena's permanent template is not in `Arena.live`.

This contract does not bound failure paths, coefficient evaluation, the packet
engine, whole recursive caller storage, physical placement, or machine steps.
In particular, the caller's `try/finally` starts only after layout construction;
the successful prefix is not an exception-safety theorem.

## Source-derived primitive invoices

These invoices are above all entry residents and include outputs. They follow
the actual ownership order in `vendor/words.py`; no historical constant is
assumed without its source lifetime reason.

`Unsigned.add`, subtraction and `read_word` allocate one result. `times_small`
has a current result and one newly allocated double/add result, hence at most
two additional Words and one output. `Unsigned.divmod` retains scan, quotient
and remainder, then allocates a shift before freeing its predecessor: exactly
four extra Words are reached. Its subtraction branch has already freed the old
remainder before allocating the replacement, so also stays at four. It returns
two Words.

`Ring.multiply` retains scan and result. A modular addition may retain a raw
sum while allocating its reduction, giving at most four extra Words. Euclidean
inversion retains four loop Words; division returns two more, and multiplication
can use four while all six remain live, for ten. The optional quotient
reduction reaches seven, and the subsequent modular subtraction reaches nine.
Each inverse iteration frees quotient, product and two old Euclidean residents,
restoring its four-Word invariant. A successful inverse returns one Word.

`records.seek_record` allocates a copied countdown and a one. At a positive
slot, the fresh decremented count coexists with both: exactly three additional
indices. At slot zero, it uses exactly two. It releases all of them. Traversing
more records changes time and serialized tape movement, not this live count.

## Directory and caller preparation

In `directory.produce`, `high_power` drives `radix_power`, which retains divisor
and power around a four-Word division: at most six residue Words. This phase
finishes before directory enumeration. `old_prefix` decodes and frees one old
residue Word at a time; its countdown is a separate Tape. Once that decoding
returns, `Odometer` retains exactly `64^2=4096` residue Words. Its in-place
increment allocates none. There is no overlap between the six-Word arithmetic
phase, the one-Word decoding phase, and the odometer phase. The positive old
prefix count guarantees that an odometer is constructed. Thus the directory
phase's residue peak is exactly `max(6,1,4096)=4096`, with no extra index Words,
and no arena Word retained on return. This rederives the relevant PR2810 invoice.

After directory production, `Consumer.apply` allocates divisor64 and one;
its first division reaches six extra indices. It then frees divisor and
remainder, computes `fields=h+1`, and frees one. This leaves exactly `columns`
and `fields`. `Geometry` adds one, two and cutoff64, giving five retained
indices.

`Layout` begins at that common five-Word baseline. It allocates `core`, then
`remaining`; `times_small(remaining,2)` needs two more while both coexist.
After releasing remaining, `times_small(parent_size,2)` likewise has core and
extra resident. Both routes peak at four additional layout indices; the
constructor returns three (`core,extra,total`). This verifies the relevant
PR2815 count directly from `vendor/layout.py`, without adding its peak to a
later disjoint phase. The layout-construction peak is nine extra indices and
the subsequent caller baseline is exactly eight:

```text
columns, fields,
geometry.one, geometry.two, geometry.leaf_cutoff,
layout.core, layout.extra, layout.total.
```

`read_prefix`, `Fields` construction and comparisons create no arena Words.
This verifies the eight-Word overlap needed from PR2801. Its later ADD-callback
claim is outside the prefix studied here and is not used.

## Callback validation: complete depth-independent invariant

All counts in the following table exclude the eight caller indices just listed
and all `L_I` entry residents. `Callback` first creates exactly three constants.
`Program.root` subsequently decodes root size and depth into two index Words.
The root-unit inverse allocates only in the residue arena.

| Validation interval | Additional callback indices |
| --- | ---: |
| Constants, root size and program depth | 5 |
| Loop boundary: also current size and count | 7 |
| Newly allocated level | 8 |
| Program seek at this positive level | 11 |
| Decoded parent and child after that seek returns | 10 |
| `divmod(parent,64)` interior | **14** |
| Returned `f` after the remainder is freed | 11 |
| Good-step `times_small(f,rank)` interior | 13 |
| Unit half-step `divmod(f,2)` interior | **15** |
| Unhalved unit/pair expected-size copy | 12 |
| After expected-size validation and disposal | 11 |
| Frozen-field `check_code(count,...)` seek | 13 at count0; 14 at positive count |
| Free parent, f, old current and old count | 7 |

At each loop boundary the seven residents are exactly the three constants,
root size, program depth, current size and count. `child` and `level` become the
next current and count; the four old residents are freed before repeating.
Hence this invariant holds for every finite admitted depth, independently of
the number and size of traversed source/field records. The source performs no
recursive callback invocation in validation.

At loop exit, freeing count leaves six. Allocating `after=h+1` gives seven.
The exact-depth source seek, current field-code seek and field-end seek execute
sequentially, with at most three scratch indices apiece. The source seek and
field-end seek are at the positive slot `h+1`, so the tail reaches exactly ten.
Freeing after leaves the callback's six persistent indices. Therefore its
exact maximum is ten for `h=0`, fourteen for a positive-depth program without
a half step, and fifteen when a half step occurs. Adding the *simultaneous*
eight caller indices, then taking a maximum with earlier preparation phases,
proves `K=18,22,23`.

The half-step peak is easy to miss: `f` survives after `parent/64`, and the
decoded parent and child as well as current/count/level still coexist with
`divmod(f,2)`. Both parent-size division and this second division include their
own four-Word scratch. Reusing the first division's fourteen-Word bound for the
second division would undercount by one.

For residues, `_prime_power_context` has qword around a first four-Word division,
for five. If `w>1`, it later retains qword, high_cap and test around another
division, for seven. It returns only high_cap. Root decoding adds root_unit;
the inverse can then require ten more, for at most twelve callback residue
Words. All later program and field-code validation allocates only indices,
so high_cap and root_unit are exactly the two additional residue residents
throughout the index peaks.

The source close at `consumer.py:40` frees the six callback indices and those
two residues. Immediately before `packet_engine.run`, the numerical delta is
exactly `(0 residue,8 indices)`. The outer `finally`, when reached after the
engine returns, frees those eight; that does not prove anything about the
engine's own lifetime or cleanup.

## Occupied numerical content, including the two arena templates

Let `r=b_R+1` and `i=b_I+1` be a complete Word's occupied non-LEFT symbols:
binary digits plus RIGHT. Allocation and erasure cannot create more occupied
symbols than a complete Word, and initialization eventually completes every
Word responsible for the stated peaks. The exact maximum for the two numerical
arenas' occupied content over this successful prefix is

\[
 (L_R+1)r+(L_I+1)i + \max\{4096r,\;2r+K(h,H)i\}.
\]

The `+1` in each baseline counts its permanent template. The two candidate
extra peaks occur on every execution in the stated class: the odometer has
`(4096,0)`, and index validation has `(2,K)`. The other possibly relevant
phases have extra pairs bounded by `(0,9)`, `(7,11)` and `(12,13)`.
They are dominated by the displayed maximum. For the last pair, if `i<2r`,
then `12r+13i<38r<4096r`; if `i>=2r`, then
`12r+13i<=2r+18i<=2r+Ki`. The other pairs are smaller.
This proves the joint bound without falsely making the separate category
maxima simultaneous. It is about occupied numerical content, not complete
physical storage or allocator backing capacity.

## Concrete witnesses and independently checked finite domain

The following integer histories satisfy the size portion of the source's
selected program predicates and can be bound to suitable available good or
fallback specification codes. Pair/unit rank is the specification's actual
rank; its value does not affect these child-size recurrences.

| Depth and steps | Root/current extents | Exact extra index peak |
| --- | --- | ---: |
| 0 | root64, current64 | 18 |
| 1, unhalved unit | root4096, current64 | 22 |
| 1, halved unit | root8192, current64 | 23 |

The root index width is always `bit_length(root)+1`. Longer histories of unit
steps result by multiplying the desired child size by64, or by128 at a half
step. This supplies legal extent witnesses at every positive depth, including
a half step at any desired position; matching frozen codes/field prefixes are
still required by the actual implementation. The two-residue validation
baseline plus ten inverse scratch is attained for `q=5,w=1,root_unit=2` in the
arithmetic model. Full selected-vocabulary literal fixtures are a separate
verification responsibility, not inferred from these neutral integer models.

Run from the repository root:

```sh
python3 -I -B research/selected-validation-numerical-lifetime/independent.py
```

`independent.py` imports no vendor code. Native integer arithmetic decides the
branches, while a fresh-handle ownership ledger explicitly checks the source's
allocation/release order. Its replay passed:

* **4229 index histories**: all final widths64 through127; depth0 through8
  unhalved unit and pair chains; one half step at every position at those
  positive depths; and every good rank1 through42 with every factor giving a
  final width in64 through127, with parent remainders0,1,63.
* **1829 residue cases**: `q` in `{2,3,5,7,11}`, `w` in `{1,2,3}`, and every
  unit modulo `q^w`. Residue cases include five unrelated borrowed Words;
  chain cases include three unrelated borrowed index Words. Arithmetic outputs
  are compared with native `divmod` and modular inverse; every modeled return
  checks ownership restoration.

The finite model confirms peaks18/22/23 and the callback residue bound12 with
its sharp fixture. It does not execute source tape parsing, authenticate vendor
bytes, construct the actual selected vocabulary, or test physical payloads.
The directory invoice is checked here by written source analysis, not by this
integer model. The parent package's literal verifier is the independent
implementation-facing complement. Its metadata fixtures likewise prove the
source's grammar checks under a numerical-arena-neutral provider, without
establishing membership in the actual selected catalogue. Its complete-prefix
fixtures use exponent1, while arbitrary finite exponents are covered here by
the directory loop invariant. Its finite weighted-content examples are all
directory-dominated; the other weighted branch follows from the two attained
source cuts and the all-width inequality above. The all-parameter result comes
from the written lifetime invariant, not extension of a finite census; no
proof-kernel validation was performed.
