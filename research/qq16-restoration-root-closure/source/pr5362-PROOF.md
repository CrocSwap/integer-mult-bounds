# Source-specific restoration metadata and its transient capacity

## Claim and boundary

This implements the **inventory-metadata effect** of the literal
`Machine.restore_context`, its `count`/`tape` methods, `Unsigned.__init__` and
`macro_binding.view(Program,...)`. It answers a bounded part of PR5330 Open
next question 1 and the released Discussion4744 Context-constructor handoff.
It does not implement `new_context`, `high_count`, numerical parking/restoration,
or all mutations of the QQ16 frontend. In particular it does not represent the
numeric value of `context.q`, `context.dimension` or `program.code_bits` in the
inventory graph. Their source values remain supplied by the fixed codebook.

The exact source is the nested chain
`physical-gaussian-leaf/inputs/pr3087.tar ! inputs/pr3055.tar !
inputs/pr2899.tar ! inputs/pr2809.tar`. Inside the last archive the relevant
files are `macro_machine.py`, `macro_binding.py`,
`inputs/pr2753/predecessor/cardinal_counts.py` and the vendor `words.py`,
`records.py`, `cardinality.py`, `counts.py`, `directory.py`.
The outer archive and the actual `qq16-caller-install/installer.py` inventory
function are immutable live inputs. `RESULT.json` also records every nested
member hash used by the replay.

Assume a fixed borrowed boundary with F distinct handles, numbered 1 through F:
the two arenas, fixed vocabulary, highs/program Tape roles, and all objects
addressed by the supplied arenas' stable word-slot tables. The boundary may
contain sharing and cycles. It has no reference back into a newly allocated
restoration object. Its bodies, field order and references are unchanged during
this operation. Its complete construction and inventory traversal are separate
obligations. Every externally retained restoration object must be rooted in the
current pair or **at most one explicitly held prior Context/Program pair**.
An alias to any subobject of that pair is conservatively covered by retaining
the whole pair. Additional external aliases invalidate this theorem's capacity
premise; they are not silently discarded.

Inputs are five already-decoded finite slot labels in the appropriate tables,
plus five prebound configuration handles (arena, indices, vocabulary, highs
Tape, program Tape). The two tables have lengths M and I, each positive and
at most F. The constructor reads their entries through paid padded-store
accesses. It accepts no runtime adjacency schema, CPython object-id dictionary
or numerical payload decoding. Producing the fixed boundary and decoding a
serialized header into these finite labels are not included in this tariff.

This is a constructor theorem under an explicit interface. We have **not**
proved that every possible QQ16 caller satisfies the external-retention premise.
The literal dispatcher has a local old `context` during a replacement, which
motivates allowing an old pair. Whole-program alias liveness and the initial
boundary compiler remain open. The test vocabulary is a declared fixed fixture,
not execution of the full production `SelectedBinding` constructor.

## Five objects, ordered fields, and the exact aliases

There are precisely five newly allocated graph-bearing objects. The source
uses `object.__new__` for Ring, Context, Count and Program; it actually invokes
the one-field `Unsigned` initializer. The order of attributes is:

| Object | Ordered fields |
| --- | --- |
| Unsigned | arena |
| Ring | arena, raw, modulus, one |
| Count | tape |
| Context | ring, arena, raw, codes, q, dimension, cap, highs |
| Program | index_arena, residue_arena, code_bits, tape |

The restored Ring order differs from the ordinary `Ring.__init__` order. We
retain the restoration order rather than infer a schema from that initializer.
Context.raw and Ring.raw point to the **same** fresh Unsigned object; Count.tape
is the existing highs role; Program.tape is the existing program role. The
restored modulus, one, cap, size and depth point to their exact supplied slots,
including source-permitted alias patterns. Their numerical validity is not
established by this structural operation.

The lowering allocates a new Ring record, then Unsigned, then Context, then
Count, then Program. It installs the same references in the same field order,
and changes only current context/program/size/depth roots. Fresh record
identities prevent overwriting a retained old Context. The source's numeric
leaves q, dimension and code_bits map to the one non-Tape leaf 0. PR5330's
opaque-leaf lemma applies: merging zero-successor non-Tape leaves cannot change
the first encounter of any graph-bearing object or Tape. The skipped `codes`
edge remains stored for liveness but is skipped by inventory, exactly as in
the retained inventory function.

Induct over these source assignments. A fresh source object is related to its
fresh record; each fixed reference is related to its prebound handle; each
existing dynamic reference is preserved. Each field install extends this
relation without changing an older object. At return all five source objects,
both public roots and both numerical-word roots agree with the record graph,
modulo the stated leaf quotient. Thus gluing either graph into the *same*
unchanged fixed boundary gives identical ordered distinct Tape DFS. This
reasoning permits arbitrary fixed-boundary sharing, cycles and physical body
contents; it does not compute or reprice that boundary's own DFS.

Partially initialized records are private to the constructor. Reserved but
unwritten fields contain zero; they are not offered as a source inventory
snapshot between assignments. The refinement compares completed restoration
boundaries while the capacity and tariff include those intermediate records.

The source oracle executes the unchanged selected method/class ASTs, including
the actual Count inheritance chain and the actual inventory function. It does
not import the old whole-repository loader or substitute a synthetic Count
constructor. Uncalled numerical and source-construction methods are outside
the replay. The independent comparison checks exact type, attribute order,
every field, two-way identity correspondence, all retained records and the
ordered Tape outputs after test-only boundary expansion.

## Capacity, retirement and repetition

One completed pair contains five objects and no edge to a previous generation.
With one held prior pair there are at most ten live dynamic records before a
replacement. The next replacement needs five fresh records, so **15 dynamic
records suffice**, independently of the number of successful restorations.
The total address universe is the zero leaf, F boundary handles and those 15
records: L=F+16. This derives the transient constructor capacity; it does not
substitute PR5034's return-cut K for a missing whole-frontend capacity.

After installing the new pair, a finite mark/sweep starts from the two current
and two held roots, follows all stored reference edges, and stops at the fixed
boundary. The boundary cannot point back into the dynamic region by hypothesis.
It erases every unmarked record. Therefore every stored or declared external
alias keeps its object alive, and every reclaimed address is unreachable. The
next constructor can reuse that address without identifying two simultaneously
live source objects. Dropping the held roots permits their records to be
collected. Disposal is forbidden while a held pair exists.

The collector uses 15 marks and a 128-word stack. Even on an arbitrary typed
15-record graph, there are at most 15*8 outgoing edges. Each record is expanded
once, so four roots plus those 120 pushes fit. On admitted pair graphs the
actual bound is smaller. Every source field is a fixed or live handle, hence
no object outside the declared boundary is accessed.

This is a successful-operation invariant. Malformed labels, a second hold,
uncollected foreign records or disposal with borrowed roots are rejected.
It is not an asynchronous rollback or exception-cleanup theorem.

## Complete charge for this metadata operation

Let E=F+M+I+16 and Q=512E. `Store(8E)` supplies Q padded words of width
w=bit_length(Q). The implementation uses 9L record words, five configuration
words, M+I slot words, six root words, 15 marks and 128 stack words:
9F+M+I+298 <= Q. All numerical payloads remain outside this store.

Use the inherited sequential padded-access bound
`A = Q(12w+3)+3w+1` bit transitions per metadata-word access, and `16w+16`
per bounded scalar bookkeeping step. This is the PR4986 macro access model,
not a newly emitted binary transition table. No unit-cost random access is
assumed: host indexing fast-forwards a charged full padded scan.

| Phase | Word accesses, upper bound | Scalar steps, upper bound |
| --- | ---: | ---: |
| Initialization, including supplied configuration/table validation | Q+128E | 512E |
| One restoration before collection | 4096 | 65536 |
| One collection | 4096 | 65536 |
| One hold or release, excluding collection | 64 | 1024 |
| Final disposal of owned padded metadata | Q | 0 |

For initialization, the input and record regions have O(E) words and are
scanned/written a bounded number of times. Each restoration performs five
slot lookups, five allocations scanning at most 15 records, 18 field installs
and four root installs. Each allocation clears nine words. The complete
collector has at most 124 stack pops, at most 120 pushes, 15 mark clears and
135 erasure writes; field/range checks add bounded reads. The displayed loose
bounds cover the address arithmetic, loop control, shape/range checks and
source dispatch, including the explicit `Store.tick` bookkeeping. The scalar
bounds also exceed 16 steps per word access in the restoration/collector rows.
The declared runtime labels are already finite words; their external decoding
is not disguised as a bounded check here.

For N restorations, C collections, H holds and R releases (normally C=N+R),
the whole metadata session, including initialization and disposal, is at most

```
B_access = 2Q + 128E + 4096(N+C) + 64(H+R)
B_scalar = 512E + 65536(N+C) + 1024(H+R)
B_bits   = B_access*A + B_scalar*(16w+16).
```

The counters used to report N,C,H,R and the peak are checker telemetry; the
algorithm does not inspect an unbounded session counter to choose an action.
Only the finite control state and bounded record/table indices affect it.
Test-oracle graph comparisons are excluded from the receipt. They are not
unpaid parts of the constructor. Inventory projection, the unchanged
inventory predicate kernel, original numerical/physical actions, initial
source compilation and other mutators are additional charges. Consequently
this is a partial F_restore, not the full missing F(K) or a QQ16 affordability
decision.

## Evidence and open obligations

Four sessions each execute every one of the 108 five-slot tuples twice, for
864 restorations. Two sessions use plain fixed boundaries; two add shared
roles, a boundary cycle and an omitted codebook Tape. Each pair uses 16-bit
and 4096-bit actual source word buffers and produces identical metadata
receipts. A retained old pair survives 108 later restorations. The observed
dynamic peak is 15, completed retained peak 10, and addresses are reused only
after collection. All borrowed contents, heads, meters and live sets remain
unchanged; final owned metadata is erased. Ten fault controls cover wrong
Tape/word bindings, lost raw sharing, old-object mutation, premature retirement,
excess retention, borrowed disposal, bad labels and uncollected history.

These are finite corroboration and a source-specific written refinement proof,
not independent human or proof-kernel acceptance. The next obligations are
the actual `new_context` numerical constructor and its temporary highs Count,
whole-caller alias/root closure, initial fixed-boundary compilation, and
composition with adoption and the other source mutators. No selected cold
replay, full controller run, numerical restoration, supplier admission or
new multiplication exponent follows.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Retain JoyboyBrian's PR4986/5034/5330, Chris R/Clear1nsight's caller/source,
Jose Manuel's physical machine, Tekalign's finite-role work, ywz65 and the
original notices in the nested source archives.
