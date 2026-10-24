# Protected child returns across the installed QQ16 callers

**A new opt-in D* protocol, compared with frozen #4166 D.** The package composes
#4167's existing protected-return exchange with the actual QQ16 producer,
decoder service and Installation inventories. It preserves the original guards
and controlled cleanup. For a successful complete installed root, the resulting
read/write/unit-move saving is

```
T_D - T_D* = 511014 Γ (5v+2, 2v, 4v+2).
```

Here v is one complete returned child packet, including prefixes, unused rows,
physical component width, coefficient count and all address spectators. This
is an exact tape-action difference of matched executions under the inherited
successful caller contracts. Additional finite validation/rebinding/compilation
control is **not zero** and is charged separately below. This does not decide
D* versus the fair baseline B*, execute production O73 payloads, establish
supplier admission or improve κ.

## The new composition obligation

#4167 already proves the return-site exchange and its `(5n+2,2n,4n+2)` saving;
those are credited prior results. #4166 already supplies the actual installed
producer/service connection, all root-call counts and whole-bank publication
adoption. #4177's exclusion concerns frozen D, and #4753 locates the first
nonterminal C8 band. None of those credits is counted again as a new gain.

The missing connection is concrete. `Installation.__init__` caches
`engine_roles=(owned_tapes(service),owned_tapes(native_child))`, and
`CallerStorage.external_roles` includes those same physical identities.
`adopt_return` changes the dedicated child's output identity. Merely installing
that transaction in `ProducerMachine.enter_child` leaves these caches stale.
The unmodified integrated fixture executes four producer child returns and then
rejects at the original Installation guard:

```
active producer and original/service engines have distinct fixed inventories
```

The nominal native output is now a producer packet, but the old cached native
inventory still includes it. Removing the guard would conceal the ownership
problem and would leave controlled disposal using the wrong role partition.

[adapter.py](adapter.py) changes only the two original return expressions
`transfer(result,self.packet(target)); erase_marker(result)` in each caller's
`enter_child`, after the original connection factory succeeds. All prepared
header, PC, target/rank, primitive-boundary, original-C invocation, capsule and
header disposal, PC increment and observation statements remain the original
AST. The protected-return transaction itself is the unchanged authenticated
#4167 method inside #4177's nested source archive.

## Ownership invariant and continuation proof

Write P for producer roles, S for service roles and N for the dedicated original
C roles. Initially these finite physical inventories are disjoint. Let o be the
caller's dead target and r the completed protected N output. The existing
transaction physically clears/erases o, installs r at the same target slot,
updates `parked` and `parking.roles`, and makes o the new N output.

The new adapter performs the corresponding finite cache update:

- Producer return: `N'=(N−{r})∪{o}`; S is unchanged.
- Service return: `S'=(S−{o})∪{r}` and `N'=(N−{r})∪{o}`.
- In both cases `storage.external_roles` is rebuilt from the two current engine
  tuples followed by the unchanged auxiliary tuple.

Before and after each valid transaction, the adapter checks complete current
engine membership, uniqueness, mutual disjointness, producer separation, exact
external-role bindings and the original storage exclusivity guard. Each tuple
replacement requires exactly one old identity and no new identity already in
that tuple. These checks inspect finite role tables; they never decode a
payload length or select a role using numerical data. Fixed and deliberately
stale variants are comparison/rejection controls; the default is the adopted
protocol.

The union of all physical roles is unchanged. Public root input/output, parent
output and the service's public result are not exchanged. Bank selection and
encoded continuation headers use finite slot numbers, not escaped Tape aliases;
`packet(target)` resolves the updated role. The complete current bank, descriptors,
source groups, numerical arenas and allocator order are unchanged. No pointer
to a protected return may escape this fixed closed composition; arbitrary
external clients are outside the contract.

After an exchange, the state is the original fixed-copy state under this finite
role permutation: the target contains the same completed value, the backend
output is empty with its marker erased, and every authoritative ownership table
has the corresponding permutation. All other source instructions are equivariant
under that permutation. The next producer instruction, suspended-parent service
entry, subsequent original-C run, service extraction, whole-bank publication,
remaining root suffix and next generation therefore preserve this relation.
The arithmetic uses exactly the same native objects, calls, payloads and
allocator histories; none of the separate-engine history cancellations needed
for D versus B* is asserted here.

`Installation.discard` follows the refreshed engine tuples. On a controlled
failure after an adopted service return, the actual source cleanup closes the
service/compiler/storage lifetimes and erases the current owned inventory while
preserving borrowed payload/descriptors and heads. The fixture checks this
**before** its own final cleanup. There is no claim about asynchronous
interruption, arbitrary invalid Tape heads or exception cleanup outside the
source's controlled contract. No frozen source or guard is edited.

## Complete matched bill

For returned length n and old target length m, #4167's literal source tariff is

```
fixed transfer: (5n+2m+7, 2n+m, 4n+2m+10),
old-target clear: (2m+3, m, 2m+4),
adoption origin checks: (2,0,4).
```

Each arm erases one marker. Thus the return saving is `(5n+2,2n,4n+2)`,
independent of m. The new cache checks/updates create no Tape and perform no Tape
read/write/move. Their control cost remains separately charged. All other
complete source intervals match under the invariant above, including setup,
acquisition/compiler/service work, already-adopted whole-bank publication,
original-C bodies with all their descendants and final cleanup. No generic
outer parking or internal C8 parking credit is added here.

For arbitrary returned lengths the complete tape saving is the sum of this
vector over **every** installed producer and service invocation. The inherited
full source census gives 510678Γ producer calls and 336Γ service calls, including
493097Γ later producer calls. The checker binds the original/changed histograms,
entry-plus-later partition and decoder count to the authenticated #4166 receipt;
#4753's independently reconstructed original histogram agrees. This census is
inherited evidence, not a newly rerun full production compiler.

For the fixed actual root descriptor, all returned packets have

```
v = P U · 2H_b c · 2^b,
b = 3 compact_bits + front + before + width·spacing + after + back.
```

`Machine.prepare_child` uses rows U and moves the removed active axes into
`after`, preserving b. The successful exact C contract preserves complete packet
length, even when the child is nonterminal. `service_descriptors` copies all
other root descriptors and sets service rows to `U·families·Γ`. Its unchanged
node quotient therefore recovers exactly U. Its 336Γ child returns have the
same v. No Γ is inserted inside v a second time. This yields the leading formula
without assuming a terminal child or discarding later calls.

Let Δ_control be the new total finite compilation, validation and rebinding
control charge minus the old return-control charge, under a chosen step model.
The complete **unweighted tape-action plus that control** comparison is

```
T_D* - T_D = -511014 Γ (11v+4) + Δ_control.
```

A step improvement requires `Δ_control < 511014Γ(11v+4)`; no unspecified control
tariff or practical wall-time advantage is claimed. The new algorithm adds no
physical Tape inventory, but historical backing follows physical tapes and is
not reclaimed by erasure or role exchange. No memory reduction is asserted.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/qq16-protected-return-caller
```

[RESULT.json](RESULT.json) records fixed/adopted executions of the original
nonconstant reduced integrated fixture: two producer/service generations, 24
real original-C calls, both source bridge legs, all endpoint bytes, preserved
borrowed inputs/descriptors, dirty scratch retirement and all original factory
and root-attachment checks. Per generation the actual chronology is four
producer calls, six service calls, then two later producer calls. Each returned
packet has 512 bits. The two arms create the same 8,046 record Tapes including
all fixture/constructor activity. Their complete record-Tape action difference
is exactly

```
(reads, writes, moves) = (61488, 24576, 49200)
                      = 24 · (5·512+2, 2·512, 4·512+2).
```

This whole-fixture metering is separate from the source proof: it is reduced
geometry, and its record-Tape census is not called a production all-engine
measurement. It agrees with every individually metered return interval.
Controls reproduce the original stale-engine failure, reject a stale external
inventory and a real output alias, and interrupt after the first adopted
service return to check controlled disposal before fixture recovery.

All 136 live inputs authenticate before inherited execution. A disposable
projection restores only the exact historical selected record required by
#4166 (`bb2eaa...129`, Git blob `b1fea0c...81`), reusing its unchanged retained
bytes on current main. Other original caller/source files remain byte-identical.
The original source manifests and authentication still run; the current selected
record is not changed. Child processes use separate fresh cache namespaces.
Git-free exports need no Git executable or historical object database. Ordinary
and optimized registered checks are read-only; only explicit `--write`
regenerates RESULT.json.

Base: `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7. Canonical
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19131467).
Entry overlap covered 299 open PRs, 3,695 Discussion records and all 6,319
base local notes; scoped searches found no match. Closed arbitrary code and
unpublished work were not exhaustive. No Lean, Docker, full historical suite,
production O73/RootLayer execution, hosted CI or human/formal review is claimed.

## Credit

Chris R / Clear1nsight's #4166/#4167/#4172/#4177 provide the caller, exact return
exchange, tariff and native-history/cost lineage. Tekalign's #3380 provides the
finite-role exchange idea; Jose Manuel supplies the physical controller and
original C/Ordinary/Compact operations. Sagar Thakrar, ywz65, Ali Romman, Arham
Tahir and all retained source notices keep their predecessor attribution.
New inventory composition, controlled failure test, complete D* versus D bill
and writing: JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

- Price the finite control difference for a specified compiled step model; the
  tape-action theorem alone does not make that work free.
- Compare this implemented D* with B* at the first nonterminal C8 band. The new
  return credit does not price the complete unmatched nonchild/native work.
- Any all-node use needs a new ownership/installation invariant and supplier
  bootstrap proof; this contribution modifies only the two outer callers.
