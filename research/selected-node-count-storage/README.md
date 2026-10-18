# Count-storage component of the first selected BIT node

For the unchanged successful first-range caller from Jose Manuel/jmbarrancoml's
[PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697), at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, participating cardinality tapes occupy at
most

```text
100 * (B + 2) symbols, excluding LEFT markers
B = max(1, bit_length(V), indices.bits)
V = C * A * before * gap * suffix * M^(2n)
```

Here `C` is the old-prefix multiplicity, `A` the fresh-row count, `M=q^w`, and
`n` the incoming bank width. All factors are positive. Counted symbols include
ZERO, ONE and RIGHT, including temporary duplicated or padded encodings.
Canonical borrowed count arguments and `context.highs` are included. This is
a conservative written source proof and finite execution check, not a sharp
constant or a formal proof.

This closes one component of the remaining
[PR2743 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18956879).
It supplies no total reserve constant, supplier admission or new kappa. The
selected record is unchanged. The original selected-stock card was changed to
this concrete first-node implementation obligation after checking newer work.

## Contract

The claim applies to PR2697's fixed `SelectedNode`, `Consumer` and
`IncomingWeights` implementations, with `64 <= n < 128`, their retained source
and completed-leaf contracts, well-formed field/program data, and successful
execution. The same count proof covers its complete dimension-two test caller
and the original-offset peel component. It does not establish those contracts.

The five incoming cardinalities are canonical, unpadded Count encodings. The
fresh-row quotient must be integral and nonzero. The supplied context, incoming
program and index-word extent must satisfy the caller's existing checks.
The caller's optional observer is absent. Tape factories and coefficient
callbacks are the fixed source implementations. An arbitrary callback could
recursively call the node, retain extra tapes or mutate a borrowed count, and
invalidate this envelope. The checker only observes writes and preserves the
runtime's tape contents and arithmetic.

Numerical `Word` tapes, serialized directories, programs, continuation/control
records, payload, route keys, LEFT markers and Python backing capacity are
outside this count. Exception-path cleanup and larger recursive children remain
outside the theorem. Clearing a count erases its content but retains its LEFT
marker; the marker is not silently priced as zero in a total reserve claim.

## Digit bound

The caller requires
`A = families * |GL_d(F_q)| * H * unused`, where
`H=q^((w-1)d^2)` and `unused >= 1`. Its `leading`, `fibre`, family-row counts,
old-prefix counts and selected-packet extents are products of positive factors
of `V`. `Layout.extents` distributes the body atoms and the intervening gap
among positive extents of a single complete fibre. Its intermediate products
also stay below that fibre's final product. `family_rows` is `|GL_d| * H`.

Directory `produce` returns prefix count `C*H`; its emitted counter increases
only to that value. Selection's before/after row counts are at most `|GL_d|*H`.
Route partition counters increase only to `H`. The bitstream digit routines move
factors of `q` between an outer extent and suffix; neither exceeds the original
complete fibre. Their countdowns only decrease.

`Count.product` scans a nonnegative multiplier from its most significant digit.
The partial product never exceeds the final product. Its `add` copy is bounded
by the factor. The code's other cardinality operations are copying, division
and normalization, or monotone multiplication toward one of the bounded final
products. Thus these count values are at most `V`. A zero uses one digit.

Some countdowns copy numerical Words rather than cardinalities, for example
`field_count` and an atom exponent. An index Word contributes at most
`indices.bits` digits even when its numeric value exceeds `V`. Residue Words
have the retained Ring's canonical one-high-zero encoding of `M`; their width
is `bit_length(M)+1 <= bit_length(V)` for `M>=3`, `n>=1` and `V>=M^2`.
This avoids assuming the program depth is bounded by payload volume.

A canonical cardinality needs at most `B` digits. `Natural.marginal` appends
one high zero. `Natural.__init__` and `Counter.__init__` first copy this extra
digit and normalize afterward, so that constructor interval must allow `B+1`
digits. RIGHT adds one symbol. Normalization, carry propagation and decrement
never create more occupied symbols than this `B+2` bound. `Count.literal`'s
temporary raw tape also obeys it. Closed count tapes have no counted symbols.

## Simultaneous inventory

[ROOTS.json](ROOTS.json) records the following deliberately conservative sum.
Each entry counts owned count roots and raw literal temporaries. A returned
factory result can be charged both to its factory and its caller. This
overcount is intentional. Borrowed references inside a routine do not allocate
another tape.

| Source group | Owned root bound |
|---|---:|
| Node | 10 |
| Fresh rows | 6 |
| Driver | 5 |
| Layout | 9 |
| Peel | 1 |
| Packet engine | 2 |
| Cardinal count helpers | 4 |
| Retained count helpers | 3 |
| Natural helpers | 2 |
| Scalar stream | 5 |
| Bitstream | 10 |
| Directory | 4 |
| Legacy packet | 4 |
| Routes | 6 |
| Selection | 5 |
| Legacy episode | 5 |
| Legacy stream runner | 9 |
| Legacy residual | 1 |
| Consumer | 1 |
| Total owned | 92 |
| Five borrowed arguments and context.highs | 6 |

The count-bearing call chain is
`Node -> peel/Driver -> Consumer -> packet_engine -> action -> stream/bitstream`
with the directory, route, selection and arithmetic helpers. It has no
count-bearing recursive cycle under the stated callback boundary. A suspended
trace generator does not allocate count tapes. Sequential loops close their
temporary counters before the next iteration; they do not retain one tape per
payload bit, high header, literal event or recursive child.

The largest fixed multiplicities deserve explicit attention. Node's initial
generator expression retains five Count copies. Its other roots are stock,
unused, leading, fibre and following. `Layout.extents` can retain three original
extents, three marginal results and a product temporary. A route partition has
two bucket counts and two countdowns. `Count.product` has three working Counts;
`Count.add` has another copy. `Count.literal` has both its raw tape and the
returned Count during construction. These are all included in ROOTS.json.
The table includes legacy paths that the selected caller does not enter, so
their simultaneous inclusion only enlarges the bound.

Hence no more than 98 participating tapes have count content. Rounding up to
100 and multiplying by the per-tape bound proves the stated envelope. The
executable inventory checks names and this sum against the authenticated
syntax. It does not mechanically prove the lifetime reasoning above.

## Reproduction and evidence

```sh
python3.12 scripts/research_package.py --package research/selected-node-count-storage
python3.12 -Werror -B -m unittest discover -s research/selected-node-count-storage -p 'test_*.py'
```

The replay imports unchanged sources from the bounded source archive into a
temporary directory. Its three observation points are the Tape bindings in
`cardinality`, `counts` and `stream`. These cover Natural construction,
Count.literal's raw temporary and Counter construction. Every write updates
the live content count. Periodic independent scans of the actual cell arrays
of known live observed tapes check the incremental census. The mutation
control changes a populated live tape. This is not a monitor for arbitrary
direct mutation of an empty tape outside the frozen runtime's write paths.
A separate modular address calculation checks
the literal returned payload, source preservation and head returns.

The full fixture executes the complete four-family GL2 node, including both
local sweeps, native idles, bridges, exchange and 5,712 completed child entries
and returns. A separate literal width-three peel executes the original-offset
remainder path. Padding fixtures cover 1, 2, 8, 64, 257 and 1,025 digits. Failure
controls reject an insufficient constructor budget and an observer-bypassing
cell mutation. Exact results are in [RESULT.json](RESULT.json).

| Literal fixture | V | Peak count symbols | Peak count tapes | Largest single tape |
|---|---:|---:|---:|---:|
| Complete GL2 node | 15,552 | 119 | 27 | 15 |
| Original-offset peel | 729 | 66 | 18 | 11 |

The complete node observes 119,351,262 count writes and returns to its six
borrowed count tapes, occupying 19 symbols. The count work is then fully erased
by fixture cleanup. The peel observes 86,315 count writes. Eleven focused tests
also exercise product/countdown behavior, finite inventory exhaustion, import
isolation, corrupted source pins, archive path rejection, recompression and
typed receipt rejection under optimized Python.

These finite fixtures support the source argument. They do not execute a full
selected GL64 payload, establish Boolean-column equality for every input, or
prove that 100 is optimal. Predecessor endpoint evidence is inherited.

## Open next questions

1. Bound live numerical Words and serialized program/control records at the
   peel sign and final merge. This would add the next missing reserve category.
   Start with the two actual Arena inventories and callback continuation
   lifetimes. The payload and count categories alone do not admit total stock.
2. Join that result with the directory component and price LEFT markers and
   physical tape placement. Start from the same PR2697 source head and PR2743's
   attained peel lifetime. Interpreter capacity and a fixed-tape realization
   remain distinct obligations.

## Sources and engineering boundary

Credit Jose Manuel/jmbarrancoml's PR2697 caller and retained lineage; Nick
Petalas's PR2708 route and PR2743 caller payload audits; starship-s's PR2731
residual audit; and ywz65's directory/primitive work, including PR2688. PR2473
prices countdown time and PR2590 prices directory setup time. Neither supplies
the count-storage theorem here. The archive preserves PR2697's original
NOTICE.md and proof unchanged. New work is by Nick Petalas, under Apache-2.0.

SNAPSHOT.json binds every decompressed source file to its exact bytes and source
commit. Container recompression is immaterial. No predecessor, upstream archive
or selected frontier is edited. The archived runtime is frozen evidence rather
than a new production implementation.

The new checker uses bounded fixture dimensions, a 500-million count-write cap,
at most 100 observed live tapes and 2,048 occupied symbols per tape, a
45-file/400,000-byte archive limit and registered process timeouts. Python
allocates dynamically; its managed-runtime deviation is limited to this finite
checker, with live tracked tapes bounded by its inventory cap. Import dispatch and
the three temporary Tape substitutions are constrained to authenticated files
and restored on every exit. They are necessary to observe literal execution.
The numerical runtime's existing loops and allocation remain frozen inherited
behavior. A future fixed-tape compiler must prove their physical resource bill;
this checker does not repair or certify it.

No repository-wide Python linter is configured. Registered commands use
`-Werror`; the new files receive AST syntax/function-size inspection and the
focused behavioral tests. New functions stay within 60 physical lines. Frozen
source loops are justified by their existing finite inputs, not rewritten to
fit the checker's engineering constraints.

Engineering choices follow Build the Lever and Prove It Works. The retained
checker replaces an unrepeatable manual census, and the literal node/peel
execution checks its actual values and returned bits. The bounded archive and
write cap implement Power of Ten's finite-resource controls for the new checker.
