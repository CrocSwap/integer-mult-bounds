# Targeted review: permanent-home dispatcher

Reviewed only:

- worker-b/research/compiler-permanent-home-dispatch/PROOF.md
- worker-b/research/compiler-permanent-home-dispatch/emit.py
- worker-b/research/compiler-permanent-home-dispatch/tape_graph.py

SHA-256 pins:

- PROOF.md: 308e74fdfd59901bcff784c4c299d892ae2637043544271c9e46fbed4516abea
- emit.py: 762c6c3e094e300bbe67de80597c3557413d4047c040ee5feaa4b925873c9a58
- tape_graph.py: 7d3cee3e79ba5fe410e1a6b5f4cf6a2fbe5e274f838b798cd8860344ff258b54

## Decision and scope

**Conditional pass** for the stated permanent-home dispatcher bound under the explicit supplied-primitive, common-format, typed-lifetime, reservation, and history premises. No selected native semantic result is established here.

The parent supplied one ABI fact for comparison: native A uses a guard at operand-origin minus one. The checked literal tape model has no cell there. The general theorem must therefore restrict supplied services to the compiler ABI or include a charged representation/entry adapter. This is a real admission condition for applying the dispatcher to native A, not a contradiction to the conditional theorem.

## Requested claims

**Services are supplied primitives.** PROOF §2 items 3–5 require the complete native word and finite catalogue of uniform all-format primitive graphs, with complete service tariffs T_mu(F,theta). Every scalar, phase, route, INIT/CLEAR, conversion, adapter and caller action must occur in a service segment and in R; no rank-based inference supplies an unimplemented operation. emit.py accepts service names/callback results as finite compiler data. It does not prove their semantics or charge an arbitrary callback, so the uniformity and charged-descriptor restrictions in §2 are necessary premises.

**Rank-N source expansion is finite.** Emitter.visit recursively calls child/visit for positive complement and exit calls, and the base case emits n sequential leaves for 1<=n<ambient. Induction proves termination if each supplied child rank satisfies 1<=n'<n. The proof identifies the #7423 complement/individual-exit recurrences as the source of that decrease and rules out rank zero. emit.py does not independently guard against malformed nondecreasing rank data; those recurrences must be authenticated compiler input.

**K counts all homes.** Emitter starts with B source rows, appends a home at each first owned-tag allocation, rejects tag reuse, and retains released tags in homes/home_index. Thus K=B+O includes every historical owned tag, not only live banks. compile_graph checks unique home identities before lowering.

**No runtime call stack is hidden in markers.** emit.py emits call/return events around recursively expanded children, but compile_graph skips every event with an empty service string. The child's entire finite event sequence is already between those receipts. No call/return transition survives in the physical graph; the Python recursion is the offline finite expansion. The tiny check below confirms empty receipts do not change the generated state count or run tariff in the fixture.

**Time ledger.** Each nonempty service event receives a complete home gather, a supplied service graph, a return/scatter, operand erasure, and head restoration. The reservation prelude is generated once. For the synthetic R=4, B=2, O=1, K=3, b=2, F=3 fixture, the literal run used 371 transitions against the asserted nonprimitive allowance 2400, before adding the service tariffs. This is corroboration only; the all-size count follows from two K-home scans and bounded b-operand/marker work per service, plus one K-home reservation, with all variable field loops terminated by supplied delimiters. All format-dependent primitive work remains in T_mu.

**Prior history.** The full K-home packet is K(F+1)+2 cells including origin, separators and terminal marker. The b operand buffers contribute at most b(F+2), and H is the sum of per-work-tape maximum visited extents, including the reservation guide. Tape.peak is monotone and is not shortened by erasure; opaque pre-entry storage remains in Hist_entry. The fixture had initial peaks (10,1,1,1), retained peaks (14,5,5,5), and the same peaks after same-packet reuse. This matches the no-history-reset accounting. Reuse remains conditional on the same reservation, owner/home bijection, root format and machine.

## Issues to preserve at application

1. **Typed zero is a premise, not supplied by zero-fill.** PROOF §2 explicitly distinguishes raw 0^F from a valid semantic field and requires a charged INIT before typed use unless the field ABI defines raw zero as semantic zero. PROOF §4 restricts the fixture to that binary-zero contract. The code itself tracks ownership/liveness only: allocate invokes ZERO, reserve writes raw zeros, and there is no semantic type-state checker. The correction is present in the theorem’s hypotheses, but any native application must prove the per-tag initializer-before-use sequence and include its service in R and sum T_mu.
2. **Operand ABI mismatch for origin-minus-one guards.** tape_graph.py fixes alphabet _01^|$, initializes each packet as ^field|...|$, places the head/origin at relative cell 0 and body at positive offsets, and Tape.move rejects a move below 0. It therefore cannot directly execute a primitive that must inspect or move onto a guard at relative origin-1. Add an explicit compatibility premise or a paid adapter with reserved left-guard space and a revised common format/tariff before applying this to native A.
3. **Keep general existence separate from tested arity.** PROOF §2 states a constructive extension for arbitrary fixed b, but the supplied literal code rejects arity above 2 and implements a four-tape fixture with one private tape. Only that b<=2 fixture was exercised here; the larger-arity extension is not part of the code replay.
4. The theorem’s history and time bounds require a shared fixed set of m primitive work tapes/origins and uniform graphs for all F,theta. Each primitive must preserve its ABI and complete format on arbitrary valid operands. The synthetic primitive suite does not establish any selected scientific provider contract.

## Tiny exact fixture check

check_fixture.py imports only the pinned tape_graph.py and checks the allocated-home lifecycle, NOT/XOR service results, same-packet reuse, retained peaks, call/return omission, and the origin-minus-one boundary:

    PASS_COMPILER_DISPATCH_FIXTURE [{'first_steps': 371, 'second_steps': 321, 'initial_peaks': (10, 1, 1, 1), 'retained_peaks': (14, 5, 5, 5), 'nonprimitive_allowance': 2400, 'states': 83}, {'first_steps': 371, 'second_steps': 321, 'initial_peaks': (10, 1, 1, 1), 'retained_peaks': (14, 5, 5, 5), 'nonprimitive_allowance': 2400, 'states': 83}]
    ABI_PACKET=^010|$; origin_minus_one=rejected

The script refuses optimized Python because it relies on assertions. This check does not replay the source-codec expansion, check #7423 recurrences, validate arbitrary-b compilation, or prove the external service contracts.
