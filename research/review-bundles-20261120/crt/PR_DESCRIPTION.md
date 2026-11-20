## Contribution

This PR consolidates the **three sequential literal CRT service packages** into one review, retaining the exact tested source trees and their independent verification records. The progression is: (1) implement ordered Word ownership and retirement, (2) join it to the unchanged arithmetic graph, and (3) close the complete producer/consumer's three remaining record owners. It addresses a concrete piece of `owned_erasure` / `precision_tape`, but **does not remove either foundational assumption**.

### From a live/free Word service to a complete terminal

1. The first package replaces raw Word allocation, copying, erasure and live/free metadata with a literal 130,936-state graph. It uses a physically encoded ordered free stack, protects eight existing owners, manages the other 56, and charges exact COPY and FREE instructions, selectors, head return and high-water history.
2. The second package composes that graph with the existing #7596 CRT arithmetic on one fixed **70-role, 1,435,098-state** inventory. A full pinned producer runs with both old backends disabled. The tests found an essential ordering rule: the original Entry.close still queries live ownership, so the close must occur after lifecycle services finish.
3. The terminal package extends this to **73 roles and 1,438,047 states**, naming the three pre-existing record owners that the 70-role graph cannot reach. It adds *no new physical backing*. On the actual P=7 fixture, the full invocation returns lower 1, product 5 and record (3,5) with 82 adds, 63 comparisons, 14 divisions and six subtractions. All 2,339 literal calls execute 3,120,094 instructions; the remaining 2,050 native actions are separately charged.

The terminal theorem gives an exact local bill of `7(P+n70+n71+n72)+2928` for the active record prefixes, under the explicitly supplied windows, clean historical tails, unique free-stack and entry grants. All 76 actual owner identities and distinct retained capacities survive. No Python fallback is counted as a physical service.

### Reproduce and audit

```sh
python3 -B scripts/research_package.py --package research/literal-crt-word-lifecycle
python3 -B scripts/research_package.py --package research/combined-crt-literal-services
python3 -B scripts/research_package.py --package research/complete-crt-terminal-service
```

The lifecycle checks cover 4,544 primitive packets and a changing free stack; independent review tests 15,872 dispatch paths. The union checks 18,380 public calls and 31,886,648 instructions, with separate raw-cell relocation tests. The terminal passes six registered commands including an independent raw-array interpreter, clean/dirty history controls and complete producer/consumer replays. Negative controls catch wrong owners, aliases, role relocations, premature closure and unreturned carry. The million-state graph is generated in memory, not committed.

### What remains conditional

This is **one supplied eager Entry**, not a general allocated runtime or full multiplication algorithm. Blank grants and windows, higher Word/record/controller lowering, changing-Entry attachment, complete global tape tariffs, the compiler and analytic recovery remain separate obligations. No new κ, unconditional theorem or selected-certificate edit is claimed.

Source and predecessor credit: #7596 and its CRT/Word lineage, JoyboyBrian's producer and the original ownership/entry contributors. Each original package retains its source pins and notices. Prepared for @CubeJerry with substantial OpenAI assistance and independent model-assisted checks; no human peer review or formal-kernel acceptance is claimed.