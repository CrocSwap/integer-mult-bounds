# A finite source-schema implementation of the adoption metadata transaction

## Scope and representation

This result lowers the graph-bearing effects of the exact retained PR4167 `adopt_return` and PR4790 `ReturnProtocol.__call__`. It does not lower every constructor or runtime mutator reachable in the installed QQ16 controller. It supplies a new partial frontend, not the complete missing `F(K)` of PR4986. The graph-cap theorem, including its 49-validation/36-exchange calibration, is inherited from PR5034 and not replayed or proved here.

Let `L >= 4` bound the occupied schema-record universe, maximum sequence length, physical Tape handle universe, source attribute count per object and transient construction space. Constructor input is a finite ordered source schema. Each occupied record has a live flag, Tape handle (zero for non-Tapes), attribute count, edge count and at most L ordered pairs `(child_address, followed)`. Every physical Tape has exactly one record and a distinct positive handle assigned before input. Graph-bearing objects/containers have identity equal to occupied record address, not equality of their fields. Zero is the unique opaque leaf. Roots include all three owners, engine and external-cache holders, auxiliary and storage sequences. For this scoped transaction require seven such roots and at least six free records before adoption; six covers two adoption tuples, up to two engine sequences, one engine pair and one external sequence. The fixed record stride is `r=4+2L`.

The constructor representation is an explicit input contract. The bounded executable calibration builds it before input with a schema-specific host oracle; that oracle is labelled and is not a paid implementation of the original CPython constructors. The paid initializer reads and validates already-encoded records, roots, Tape uniqueness and child ranges and writes the owned store. This distinction prevents renaming the original host observer as a physical frontend.

## Opaque-leaf quotient

`owned_tapes` visits Tape, dict values, list/tuple members and permitted object attributes; type/module/function/method objects and all other leaf types have no successors. Replace every zero-successor non-Tape object by one common leaf and omit its value. On the traversal stack this only merges subcomputations with no Tape emissions and no successors. Thus every first encounter of every graph-bearing object and Tape occurs in the same relative order: a skipped leaf cannot discover or mark a graph-bearing object. Induction on the traversal steps gives identical ordered distinct Tape output, even with cycles, shared containers and repeated leaves. The original graph's node count/leaf-sharing pattern need not agree; canonical adjacency equality is deliberately not claimed.

In particular `1` and `10**100000` need no numeric-word representation in this inventory graph. This says nothing about other source operations which consume that integer. Attribute count and original field order remain in schema records, including skipped positions. Dict keys and set/frozenset members are absent, as are function globals/closures and generator frames. The exact shared omission alphabet is `binding, catalogue, group, data, source, native_child, at_fence, observe, codes, recipes, template, packet, core, events, word`. Known skipped pointers needed by this transaction, specifically `native_child`, may be retained as non-followed edges for ownership/liveness; `binding.slots` is an explicit finite constructor parameter. No skipped edge is traversed by inventory DFS. The source guard still evaluates numeric predicates and physical markers in its original implementation.

## Literal assignment refinement

The `adopt` implementation follows the following exact source assignment sites in order, after validating finite role/alias conditions. The physical marker checks, `old.clear()` and `erase_marker(old)` execute only in the retained source oracle and are separate physical obligations/costs.

1. `bank.packets = tuple(...)` or `private = tuple(...)`: allocate a fresh tuple record, copy the original ordered pointers and replace the selected position. Update only the owning attribute; never mutate the old tuple in place.
2. `parked = (*roles.values(), *bank.packets, *private)`: allocate a fresh concatenation in this exact order and install it.
3. `parking.roles = parked`: install the same new tuple handle, preserving source identity sharing.
4. `native_child.output = old`: install the old physical Tape handle; no Tape is allocated or retired by the metadata transaction.
5. On the service-caller branch only, rebuild the service engine sequence by the literal one-occurrence substitution; always rebuild the native sequence with the reverse substitution. Allocate a new engine pair and install it through its holder. Rebuild the external sequence as service, native, auxiliary and install it in that order.

Preconditions and aliases are preserved by induction over these assignments. In particular fresh tuple identity is necessary: an additional `caller.alias` pointing to the old tuple still reaches the old Tape after replacement. The new finite graph retains that alias, and both actual source inventory and encoded PR4986 inventory reject its cross-owner overlap. An in-place tuple-edge substitution would incorrectly hide it. This control is a new source mutation failure mode, not a reproduction of the K bound.

Allocation scans the finite free-record table. After the transaction, `collect` marks from all roots, following both visible and non-followed stored reference edges, and zeroes unreachable occupied records. Existing aliases prevent reclamation. It keeps no cumulative identity history; an address is reused only when no stored source reference can reach it. For this scoped transaction the root contract must include every externally retained tuple alias. Unknown references outside this contract invalidate the refinement. Collection does not traverse source payloads. Constructor constants and unrepresented source objects belong to the explicit interface, not to an inferred full-heap bound.

## Charges and physical realization

All bounds below are conservative constructive metadata bounds, not attractive constants or a complete caller bill. Put `Q=512L²`, `w=bit_length(Q)` and `A=Q(12w+3)+3w+1`, exactly the predecessor padded-scan `access_cost`. One metadata-word read/write pays A bit transitions; one scalar bookkeeping step pays `16w+16`. The machine has a fixed number of tapes over binary symbols plus delimiters. A word access scans the fixed padded store and returns its head; counters, comparison and stack operations use bounded w-bit fields. Host list/set/index operations in the macro simulator fast-forward these scans, with explicit bulk charges where no `Store.read/write` is performed.

The record area uses `L(4+2L)` words; mark flags, a DFS stack of at most `L²+1` entries, maps, sequences and output adjacency fit within Q words. Object pointers remain at most L; offsets and source lengths remain at most Q. No numerical leaf payload appears in these words. All scratch regions are disjoint and reuse is sequential.

| Phase | Word-access upper bound | Scalar upper bound | Reason |
| --- | ---: | ---: | --- |
| Encoded-record initialization | `1024L²` | `2048L²` | Q zero fill, record input/write, roots and uniqueness/range validation |
| One adoption and both cache branches | `256L²` | `1024L²` | At most six fresh tuple constructors, finite alias scans, copying, concatenation and field installs |
| One inventory projection plus DFS | `256L³` | `1024L³` | At most L records and L² edges; explicit padded index/visited/stack scans, including ABI output installation |
| One mark/sweep | `64L³` | `256L³` | All retained edges followed for liveness, finite mark/stack scans, at most L complete record erasures |
| Final disposal | `Q` | `0` | Full owned store zeroing, including all scratch and descriptors |

The initializer pays its extra constructor validation explicitly; it does not cover generating the schema from the source constructors. Per transaction bounds assume the declared capacity and schemas, valid source selector and enough temporary free records. A failed capacity check is not successful admitted execution. A session with N completed transactions and V inventory projections therefore has the explicit partial bound

`F_adopt(L,N,V) <= [1024L² + 256NL² + 256VL³ + 64NL³ + Q] A + [2048L² + 1024NL² + 1024VL³ + 256NL³](16w+16)`.

The predecessor inventory predicate kernel charge is additional. Likewise original marker/body actions, schema generation, and non-adoption mutations are additional. `L` is a constructor/transient parameter; the return-cut K alone is not substituted for L. In a closed source schema admitting six spare transient records, a future compiler may derive L from K plus retained omitted-reference slots, but this package does not assume that implication.

## Coverage boundary

| PR5034 source mutator family | This package |
| --- | --- |
| PR4167 bank/private/parked/parking/output adoption; PR4790 engine/external replacement | Implemented source-specific finite-store updates and literal original-function oracle |
| Bank selection dict, scatter/commit/release state | Not lowered; needs explicit key-order and replacement construction |
| Scalar recipe replacement and monomial recipe construction | Not lowered; needs catalogue/recipe handle production and finite schema dispatch |
| Context/Program/Count replacement and geometry retirement | Not lowered; needs actual constructor/free updates, not retained history |
| ScratchPool leases and OuterScope manager/transform | Not lowered; needs transient liveness and opaque-function boundary |
| Ordinary/RootSession final marker erasure and numerical machine containers | Not lowered; final `[{},{}]` cut inherited only; no source replay here |
| General fixed-field scalar updates, capacities, entire initial constructor graph | Not lowered; numeric leaf omission proves their inventory values irrelevant only once leaf typing is established |

The source-only fixture is deliberately reduced: explicit role schema, marker-only Tape oracle, real `owned_tapes`, real PR4167 `adopt_return`, real PR4790 `ReturnProtocol` and the predecessor encoded inventory kernel. It does not execute the original controller or demonstrate all 49 source validations. Normal and optimized Python both retain all new rejection checks through explicit `need`, not assertions.
