# Selected PR1094: a 112-bit conditional prefix estimate

**Scoped precision audit; no new κ and no production reserve change.**
Following the actual data dependencies reduces the selected controller's
sufficient global-prefix estimate from **397 to 112 bits**, using its existing
positive scalar/Horner envelopes. The literal 16-replica controller has maximum
boundary norm majorant **14**. Every actual call's data and borrowed-helper
inputs have majorant at most **8**. The production payload remains **512 bits**.

This refines Brody Arbon's [PR821](https://github.com/CrocSwap/integer-mult-bounds/pull/821)
replica-counter argument: track each pair and side, then inspect the actual
owners at each call. It is not a transplantation of PR821's historical 160-bit
estimate. Gareth Davidson's [PR1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282)
tightens the **local** signed envelope; that improvement and its code are not
used here. Both approaches build on eumemic's PR496 maximum-stream norm argument.
Concurrent [PR1093](https://github.com/CrocSwap/integer-mult-bounds/pull/1093)
by @woklerx also uses componentwise majorants, for a different 12-stage
cyclic-inverse word. Its 112-bit working precision is a separate result with
different interfaces and inputs; this package imports neither its code nor its
precision budget.
Gareth Davidson's [PR1309](https://github.com/CrocSwap/integer-mult-bounds/pull/1309)
formalizes a conditional stream-prefix norm implication; it does not bind this
controller's concrete call-input budgets. No Lean code is used or replayed here.

## Reproduce and evidence

From the repository root, using the standard library:

```sh
python3 -I -O -B research/selected1094-wire-prefix-audit/verify.py
python3 -I -O -B research/selected1094-wire-prefix-audit/test_verify.py
python3.12 scripts/research_package.py --package research/selected1094-wire-prefix-audit
```

The verifier prints `PASS_SELECTED1094_WIRE_PREFIX_AUDIT` and
`conditional_bits=397->112 retained_payload=512 no_new_kappa`.
It writes only into a temporary directory. An intentional receipt regeneration
uses `--write /new/path.json`; existing output paths are refused.

[EXPECTED.json](EXPECTED.json) records all 144 call input bounds, the 30 source
boundary vectors, exact envelopes, controls and source hashes. Fresh verification:

- Binds the actual selected replay archive, provider programs and prefix receipt.
- Replays the unchanged local checker on both **704-column** arbitrary-input
  maps and all **25** original rejection controls. Its entire parsed receipt
  equals the archived receipt, including the positive coefficient-work bounds.
- Checks all **482** controller events, **144** calls and **69,120** helper
  roles, including **57,480** cross-replica helper occurrences. A separate dense
  8×8 transfer calculation agrees at all **480** replica event boundaries.
- Rejects **12** mutations: altered bridges, local direction, physical aliases,
  a data-port permutation, program mismatch, missing/reordered/unknown events,
  a bound of seven, and a post-terminal helper borrow.

These are finite source/interface checks. They are not a cold supplier replay
or a complete physical/operator verification.

Verified on Linux x86_64 with CPython **3.12.13**, using the registered package
command above; all eight test groups passed. The verifier and exact receipt also
agree under CPython **3.11.15**. Tests include 9,600 exact squared-norm comparisons
in nonidentity, noncommuting two-dimensional unitary contract models, an
independent evaluation of the borrowed-input witness, strict bit-boundary cases,
source-corruption controls, and an optimized read-only export without Git.
`make selected-record-check` and the package metadata/source checks pass.

## Conditional norm proposition and proof

Use the inherited norm convention: for physical family `f`, let `N_f` be the
maximum, over its cover classes, of the stream's Hilbert norm on `2^73` entries.
Do **not** concatenate every physical family or every cover class into one
Euclidean norm. Let the initial maximum be `B`. Assume the retained interfaces:

1. A completed forward call has the data endpoints `Y_i += U_i X_i`, and a
   backward call `X_i -= U_i* Y_i`, where each `U_i` is unitary. Their physical
   family/port pairing is exactly the emitted one. Cover-class permutations
   preserve the maximum defining `N_f`.
2. Each borrowed helper's completed residual is unitary **within its own
   family**. Its initial dirt does not leak into any other endpoint. Private
   work is cleared. Whole calls, including their complete cover sweeps and
   wrappers, finish before the next call.
3. Bridges update corresponding sides of two pairs of the same replica, with
   their literal signed coefficient. Idle children, phases and translations
   preserve individual family norms. A terminal signed exchange is within
   its own final pair, after all that replica's local calls and bridges.
4. The inherited complete-cover realization transports the local positive
   scalar/Horner envelope to physical streams: each stream is visited once
   per call sweep. The original 37-bit input conversion, four-bit arithmetic
   margin and recursive primitive-prefix interfaces remain available.

These are the normalized interfaces behind the pinned invoice and the
[T16 proof](../complex-double-replica-owners/PROOF.md). The fresh local replay
checks their scalar/frame/wrapper premises; it does not prove the all-size or
physical realization statements.

Index a family by `(replica, pair, side, port)`. Maintain one integer `b` per
replica/pair/side, uniformly over its 112 ports, initially one. At a forward
call set `b_Y := b_Y+b_X`; at a backward call set `b_X := b_X+b_Y`.
For a bridge set `b_dst,side := b_dst,side+|c| b_src,side` on both sides.
All familywise unitary events leave the bounds alone. At a terminal exchange,
replace both bounds in each pair by their maximum, which covers either signed
exchange convention conservatively.

Induction gives `N_f <= b_f B`: the shear step is the triangle inequality and
unitarity; a helper endpoint leaves its owner's bound unchanged even when that
owner belongs to another replica. No calls are commuted, no helper is assumed
clean, and no signed cancellation between different calls is used.

The source's eight bounds immediately before its terminal exchange are

```text
(X0,Y0, X1,Y1, X2,Y2, X3,Y3) = (5,8, 9,14, 8,12, 6,9).
```

They increase monotonically up to a maximum of 14. The terminal update gives
`(8,8,14,14,12,12,9,9)`. Every replica has the same source projection; arbitrary
interleaving of those projections therefore preserves the boundary bound 14.
The source transfer matrices give a second exact computation of this table.

Before each selected call, inspect **every** one of its 704 actual owner
families. Their current majorants are at most eight for both orientations.
This eightfold statement uses the pinned schedule and owner map; it is not
claimed for arbitrary maps or interleavings. Helpers dominate the active
pair's majorant in **126** of the 144 calls.

The independently replayed **original** positive local envelopes are

```text
K_forward  = 2765345294379392599 / 1024  < 2^52
K_backward = 14824960514781440791821 / 64 < 2^68.
```

Thus every local scalar/Horner prefix is bounded by `8 max(K_forward,K_backward) B`.
This also dominates the completed-boundary bound `14 B`. Exactly,

```text
max(14, 8 K_forward, 8 K_backward)
  = 14824960514781440791821 / 8 < 2^71.
```

Keeping the inherited conversion and margin gives **71+37+4 = 112** sufficient
bits. The original invoice charged `68+37+144+144+4 = 397`.
This improves a sufficient bound, not the actual attained physical maximum or
the minimal safe payload. Partial primitive execution and recursive internals
remain covered only to the extent of the inherited arithmetic/compiler contract.

## Adversarial boundary and limits

Counting only the active data pair is insufficient. At emitted event 25,
stage 0 of replica 11 borrows helper 0 from physical family 223 in replica 0.
In the exact scalar contract model with identity familywise unitaries, its row
is `initial_X0 + initial_X1` of replica 0. Set those two inputs to one and all
others to zero. This helper is two while the new replica's active inputs are
zero (their unit-input operator bound is one). The receipt supplies the exact
row and input. This instantiates PR821's borrowed-input warning on the selected
map; it is **not** a new physical counterexample to the selected construction.

The post-terminal control preserves counts, owner ranges and within-call
uniqueness but points a later helper at family 336 after its bound has reached
14. The checker rejects the claimed eightfold input cap. Such a borrow also
violates the production hosting windows; no production acceptance bug is
alleged. Mutations enter the semantic checks after loading the pinned positive
fixture, so their rejection does not rely on a stale checksum.

Not established here: fresh complete controller/hosting admission; all native
Clifford and phase identities; optimality of 112; roundoff or lattice transport;
the all-size/common-label/mutable-source and tape/analytic interfaces; Lean or
human peer review. The helper chart geometry, window legality and existing
physical implementation remain inherited. A smaller local prefix estimate
alone does not change the paid rank profile, recursive moment or κ.

## Scope, provenance and coordination

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6` (current main at entry).
Rebased for submission onto `c5108f0f68d482e5712a8e26a5978d47762dfc16`;
the applicable guidance, selected record and all consumed source bytes are
unchanged between those commits.
Selected PR1094: `0fc329d0bec93ca7cd288eaea1295172e8789810`; parent PR1087:
`589d1cedf5ef5f231182f4ec86408616311a8af0`.
[SOURCES.json](SOURCES.json) pins source bytes and Git blobs. Historical selected
record and catalogue pins do not track later moving selections.

The chooser's nonce was `2ebb0ab34af6cc7e7d70f4ddf504ef89`, adversarial-audit,
priority revision 2. The `supplier-boundary-audit` card is **refined** to the
global-prefix obligation; [TASK.json](TASK.json) records the claim and stop rule.
The historical owner audit and current baseline-binding orientation commands
passed. Initial overlap covered all 759 public open PR titles/bodies, including
drafts. A complete public REST refresh at **2026-10-14 02:30:51 UTC** covered
781 open PRs. Public Discussion pages and searches were checked, but comments
were not exhaustively enumerated. The overlap helper's 02:31:44 UTC refresh
covered 327 local records and reported unavailable authenticated remote caches;
the public REST check supplies separate open-PR coverage. No novelty claim
follows from these searches. PR1112 independently checks the historical PR1042
397-bit invoice arithmetic; it does not propagate these current owner bounds.

The authenticated board refresh at 02:48–02:50 UTC covered 80 Discussion
titles/bodies, all 27 top-level handoff comments, and the empty comment thread
on Discussion1260. Other comment/reply trees remain only partially covered.
The initial claim was retained locally while API access was located. The
subsequent Discussion1260 post was explicitly rejected by GitHub's organization
OAuth-app restriction. The finding and submission material are retained with
this public branch. No original source, selected record, frozen evidence or
production verifier is changed.

## Open next questions

1. **Can this bound support a 128-bit production reserve?** It could reduce
   physical row overhead, although it need not improve κ. First add this
   dependency-bound check to an opt-in successor invoice and replay the complete
   local/native/hosting/precision chain with a 128-bit charge. Adoption is blocked
   by the inherited recursive/roundoff interfaces and the required complete cold
   replay; this note does not authorize changing a frozen invoice.
2. **Can the bound be composed with PR1282's signed local envelopes?** This
   could tighten the sufficient norm bound further. First independently replay
   and bind that package, then check the partial-component and wrapper interfaces
   against the same cover norm and owner inputs. Its estimates are pending
   independent adoption and are deliberately not numerical inputs here.

## Credit

Credit eumemic's PR496 for the maximum-stream norm and unitary-helper argument;
Brody Arbon's PR821 for historical replica counters and the cross-replica input
caution; Gareth Davidson's PR1282 for the complementary signed-local audit;
@woklerx's PR1093 for the concurrent componentwise-majorant precision work;
Rohan Arun's PR1094, Jeremy Kothe's k8/T16 lineage, Hao Yan's PR858 controller,
Douglas Colkitt's integration and source archives, and icekylinx's credited
PR514/PR433 local checker with the retained HPE/compiler/Clifford contributors.
Their implementations and notices remain unchanged. Triangle-inequality
majorants and transfer matrices are standard methods, with no priority claim.

Prepared with substantial OpenAI Codex (GPT-6 Astra) assistance in mathematics,
implementation, testing and prose. No subagents or independent human review.
New material is Apache-2.0.
