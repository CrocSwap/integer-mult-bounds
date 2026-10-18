# Selected compiler ordering and all-low owner separation

This independent audit checks one explicit boundary in PR2809's fixed-role
lowering. It gives a conditional whole-word ordering lemma and independently
checks the selected inventory's same-family owner separation for every
admissible low class, without enumerating GL64. It does not establish the full
physical caller.

The sources are Jose Manuel / jmbarrancoml's PR2809, author head
`e7d93dd0de0bb81308bc3356f65eddeeb22fd712`, and its retained David Arias PR2753
logical caller. Main's installed package is pinned in [SOURCES.json](SOURCES.json).
The selected frontier and all predecessor files remain unchanged.

## Two results and a necessary admission boundary

### 1. Conditional ordering lemma

Consider a finite topology accepted by the retained `Driver` guards. Assume:

- Every gather, route, scatter, XOR, copy and transfer has the declared complete
  packet contract. Borrowed sources survive until their last read. Scatter
  replaces only its low packet in the **latest** family state.
- Every compiled residual returns exactly the source residual's distinct owned
  output for the same identifier, common/native flag and low label. Its
  recursive cuts, internal blocks and costs are separate hypotheses.
- Node split and final merge agree, and canonical result commits preserve data.

Then `compile_node` followed by `Machine.dispatch` has the source
`Driver.global_word`'s family states at every completed global event. It also
has the same residual inputs and outputs and the same ordered local/family XOR
inputs and outputs. This is an implication about completed packet operations,
not a proof of the substituted physical kernels.

Proof by nested induction on global event, replica, common low and local event:

1. A local call gathers every owner before executing its literal word. Both
   implementations use `compile_owner` on the same chart and common low, hence
   stage the same native packet through the same forward route. The source's
   disjoint-owner guard is an entry premise.
2. MOVE applies the same residual to the same staged source. XOR reads the same
   live staged source and destination. COPY first preserves the source in a
   distinct retained packet, applies the same residual and assigns its result
   to the private role. ERASE clears only that private role. `LocalState`'s
   version/frame checks prevent modification of the copied source during this
   interval. The canonical labels replace source buffer references without
   changing packet values.
3. Both route every nonprivate staged role back in owner order. Each scatter
   reads the current family after preceding commits. Two different staged
   packets in one family therefore do not overwrite each other's returns.
   The temporary source bindings may differ, but their last payload read is
   complete before cleanup.
4. IDLE nests replicas, request identifiers and native lows in the same order,
   gathering and committing one complete residual at a time. Bridge emits the
   same two ordered family XORs for each replica and port. Its sign is Boolean
   XOR on either permitted coefficient. Exchange swaps the same two family
   values, implemented by three destructive transfers through an empty role.
5. Empty stage/private/current roles at each completed call permit the next
   iteration. The induction gives the next global-event boundary. Applying the
   assumed node/merge contracts gives the complete boundary endpoint.

The proof inspects the actual source and dispatch templates, not a second
implementation of their loops. The exact symbolic differential replay below
corroborates it in a bounded domain.

### 2. Selected all-low owner separation

In a common low class L, owner chart C has native low `L C^-1` modulo q.
For invertible L,C,D over the field,

`L C^-1 = L D^-1` if and only if `C = D`.

Thus source-owner disjointness within one physical family does not require
iterating GL64. It suffices to distinguish each pair of charts used by that
family in that call.

`owners.py` traverses all 288 selected calls and all 190,368 staged owners,
retaining physical family and replica identities. The 106,528 family groups
contain 181,056 unordered owner-pair occurrences and only 463 distinct chart
pairs. For each distinct pair it constructs a coordinate difference equal to
`1`, `-1`, `1/2` or `-1/2`. The 123 charts in these comparisons contain only
integral or half-integral entries. Every witness is therefore defined and
nonzero modulo **every odd prime**. Substituting the field identity above proves
pairwise native-low separation for every GL64 common low at every source prime
where those charts are invertible. Different physical families are distinct by
construction.

The exact witness histogram is `{-1:32, 1:19, -1/2:260, 1/2:152}`. The replay
reconstructs all matrices and witnesses from pinned sources. It does not infer
this statement from sampled low matrices or from a rank profile.

The separation theorem is not new. Jose Manuel's
[PR2195 support argument](../selected-bit-local-ring-sweeps/PROOF.md#3-complete-owner-packets-and-chronological-sweeps)
and PR2753 retain it. ywz65's
[whole-packet staging audit](../bit-whole-packet-staging/README.md) already
counts the 190,368 owners and 181,056 pairs using source support descriptors.
The added check here reconstructs the **actual compiler chart matrices** and
supplies 463 explicit field-independent coordinate witnesses. Those earlier
counts and support proofs retain their original credit.

Only the rational inventory is taken from `Catalogue(3)`. Its chart construction,
selected owner lists and this separation calculation do not depend on q.
No q=3 GL64 low is enumerated. Chart invertibility and source-prime admission
are retained premises, not consequences of a nonzero difference.

### 3. Compilation alone is not source admission

The compiler omits two runtime guards present in `Driver`:

- Two identical same-family owner charts compile to 1,155 instructions in the
  bounded fixture, but the source rejects `disjoint complete owned low packets`.
- A self-bridge compiles to five instructions, but the source rejects
  `native bridge scalar`.

These are exact boundary counterexamples, **not defects established on the
selected construction**. `SelectedTopology._validate_global` already excludes
self-bridges. Result 2 supplies a separate all-low check for the selected
owner-packet guard. The guarded source and unguarded compiler cannot be treated
as interchangeable admission validators on arbitrary supplied topologies.

## Reproduce and evidence

Use standard-library Python 3.12 from the repository root:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/physical-compiler-correspondence
```

Registered normal and optimized CPython 3.12.15 commands pass eight behavioral
groups each and reconstruct [RESULT.json](RESULT.json). The Linux x86_64 / WSL2
workflow suite passes 158 tests with 16 platform skips. Ruff lint and format
checks pass; registered commands enable `-Werror`. The predecessor loader authenticates its complete
97-file source exports and transitive repository inputs before imports. The
new manifest also pins the consumed compiler, dispatcher and local support
modules. Registered replay uses a fresh bytecode namespace.

Eight complete GL2(F3) abstract-packet words cover all 48 lows, one/two replicas,
forward/reversed global-event order and forward/reversed low order. They execute
67,024 compiled instructions and compare 8,064 residual boundaries. Each family
packet has four independent Boolean coordinates per low, giving exact linear
maps on 768 or 1,536 independent input bits. Comparisons include every global
cut, every residual input/output and every XOR input/output.

The test adapter deliberately substitutes complete symbolic packet kernels,
node/merge and residual bodies. It executes the actual retained source `Driver`
and actual production compiler, dispatch and commit methods. These are not real
Tape payloads or selected GL64 executions. Reversed synthetic schedules test
ordering; they are not proposed admitted selected circuits.

Five compiler-word defects are detected: omitted/reversed bridge, omitted
exchange, omitted COPY, and deletion of a cancelling private-XOR pair. The last
preserves the final endpoint, every global cut and every residual boundary;
its complete private XOR trace still differs. Final-output checks alone would
miss it. Missing/zero chart witnesses and both admission counterexamples are
separate controls. Behavioral tests also check literal dispatch payloads,
latest-family scatter and source-hash rejection.

No full selected cold replay, full predecessor replay, formal-kernel proof,
hosted-CI pass or independent human review is claimed. Physical heads, markers,
scratch inventories, parking/CALL invariants, all-size residual refinement,
precision, movement and costs remain unproved here. There is no supplier
admission or new kappa.

## Open next questions

1. Check the residual block implication independently at the same exact head.
   Compare its good/fallback and omitted-half contracts to the source trace,
   including the recursive CALL/RETURN substitution. This is the next omitted
   premise of Result 1; packet-ordering evidence cannot discharge it.
2. Decide whether a successor compiler should enforce the source's admission
   guards at compile time. Start with the duplicate-owner and self-bridge
   counterexamples, preserving frozen sources. This is useful for any future
   caller accepting independently supplied topologies; the selected guard is
   already covered by Result 2 and the existing global validation.

## Scope, provenance and engineering limits

Task `supplier-boundary-audit`, refined to the current physical-contract map's
independent opcode/source-correspondence handoff. Picker nonce
`1ab643d575b1d286d218d0375017dcfb`, priority revision 5, starting canonical main
`b3f3ee0392b71b118fd086a6eaf6b4cab54ef455`. Coordination is in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18977492).
[TASK.json](TASK.json) records overlap coverage, freshness and remaining scope.

The Python checker uses bounded managed-runtime allocation and scoped monkey
patching because its purpose is to compare two unchanged source entry points
at an explicitly abstract operation boundary. Fixture sizes are fixed: at most
eight families, 48 lows, four coordinates and 11,165 instructions per word.
The selected census has 288 calls, 661 owners per call and 64-by-64 charts.
Patch contexts restore every binding on normal and exceptional exit. This is
a verification adapter, not a proposed allocation-free implementation or a
machine-step bound. These are bounded deviations from Power of Ten rules 3,
8 and 9 for managed allocation and dynamic test substitution. Frozen long
functions and dynamic loaders remain unchanged;
any physical refinement must address their separate resource contracts.

Nick Petalas. Apache-2.0. Substantial automated assistance was used; no
independent human review is claimed. Credit Jose Manuel / jmbarrancoml for
PR2809's implementation, PR2195's support-separation theorem and retained
numerical/parking lineage, David Arias for PR2753's logical caller, ywz65 for
the parking predecessor and whole-packet staging census, and the unchanged
PR589/PR555/source notices. This audit claims neither their implementation nor
the preceding physical, route, scaling or storage results as new work.
