## Why this change matters

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.

The current CRT producer's raw division calls were already routed through a verified literal core, but comparison, addition and subtraction still entered their source providers. This package closes that remaining raw arithmetic interface at the exact current producer, including aliased doubling and the physical result-owner boundary. Higher source controllers, Word lifecycle, metadata and grant services remain explicit dependencies.

## Exact result

One fixed 1,304,162-location, 68-role R/W/M/J/H graph handles every admitted current comparison, addition, subtraction and division. Its first 336,150 instructions are the unchanged divider from [CubeJerry c4ab5dab](https://github.com/CubeJerry/integer-mult-bounds/commit/c4ab5dab6914a04cb86d1fe54eb763b35cc7eeb1); all old entry and setter addresses remain unchanged. It extends the complete division substitution from [CubeJerry 9700fc89](https://github.com/CubeJerry/integer-mult-bounds/commit/9700fc89e2582a1fb358a4c6d0d0387076192adc).

The new entries classify input aliases from encoded six-bit handles, scan the actual P-bit Words, construct a fresh output directly, preserve borrowed contents, return heads and erase all four selector frames. Finite halt tags deliver comparison, carry and borrow results. The actual binder reserves one output where required and preserves the inherited weak owner relation through the whole source. Exactly eight protected guard Words, 56 owned Word roles and four explicitly granted selector windows are retained.

A complete new simple call including setters costs at most `401P+1073` literal instructions. For one invocation, let m/t count left/right records, v valid right coordinates, E total Euclidean iterations, J divisions and H other raw calls outside the old divider. The exact source gives

```text
J = 3m + 2t + v + 2E <= (P-2)(4P+5)
H <= (6P+3)E + m(10P+7) + t(8P+6)
  <= (P-2)(12P²+22P+10)
```

The complete new raw arithmetic subset is bounded by `89 + J(930P²+1395P+14322) + H(401P+1073) < 2^16(P+2)^4`. Across invocations sum the terms at each actual width and pay acquisition once per descriptor lifetime. Residual source actions, finite metadata/flags, grants and full-history services keep separate charges. No unproved common tariff or runtime improvement is inferred.

## Novelty and predecessors

#5053 already supplies the arithmetic algorithms, numerical admission and constant live-stock bound. #5219 and #5353 supply the physical entry and row interfaces; #7388 supplies the actual current source/payload boundary. The preceding literal packages supply the divider, dispatcher, complete division scope, headers, row controller and key path. Their source and notices remain unchanged. This package adds the combined source-bound comparison/addition/subtraction implementation and proves the alias, finite-return, allocation and complete-cost join; it does not claim new generic binary arithmetic.

## Reproduction and checks

Run these primary commands from the package directory:

```sh
python -I -W error -B source_check.py
python -I -W error -B test_core.py
python -I -W error -B verify_source.py
```

The same three primary commands with `-O` produce byte-identical receipts. The complete eight-entry registered suite (twelve checks) includes both complementary independent reviews; from the repository root run `python3 -B scripts/research_package.py --package research/all-current-crt-arithmetic`.

- Static verification authenticates 85 exact source objects, all 16 raw call sites per producer, 167,232 dispatch paths, every new control relocation, and the entire unchanged divider prefix. Wrong-port and fallback mutations are caught.
- Primitive verification covers 840 packets through P257, all ordered four-bit pairs and aliases, retained histories of 1,025 cells, exact logical/physical counts and domain controls. Returning carry/borrow/comparison corruptions finish cleanup but fail the semantic oracle.
- Complete nonleaf source and padded source/payload roundtrips execute 1,135 comparisons, 1,510 additions, 107 subtractions and 192 divisions, including 1,258 aliased simple calls, in 22,179,316 literal instructions. All old arithmetic providers and the obsolete shift provider are unavailable during positive execution; zero fallback calls occur. Exact source outputs, full roundtrips, physical ownership and meter subtraction pass.

The meter subtraction is outermost-only: nested comparisons/subtractions inside the old division body are not removed twice. Numerical actions charge the arena meter and selector actions their marker ports exactly once. Counterfactual old arithmetic runs after actual legs, never as a runtime provider. Separate independent graph/owner and source/cost review assets identify their own evidence and limitations.

## Limitations and open obligations

Admission and successful termination refer to the original producer; finite-trace induction proves the replacement terminates. Verifier transcripts/counters have an explicit erasure projection and do not contribute hidden unbounded machine storage. The graph theorem excludes the bounded Python replay watchdog.

Word lifecycle and higher controller loops, finite live/free metadata, acquisition and current framing remain retained and charged. Arbitrary previous owner histories retain their per-role maxima and any actual full-history sweep/transport bill. The complete source-only 83-role traversal and 100-role-per-leg payload caller remain distinct. The payload boundary keeps fixed 13-bit codewords with arbitrary 12-bit data. No full CRT, recursive caller, compiler assumption or unconditional multiplication theorem is claimed.

**Kappa status: No new kappa.** The selected frontier is unchanged. All five foundational assumptions remain. The remaining questions are literal Word/controller closure, encoded owner control, and a common fully paid physical caller interface.

## Credit and assistance

Contributed by Jerry Chen / @CubeJerry with substantial OpenAI assistance in research, implementation, proof writing, bounded verification, independent model-assisted review and packaging. Credit JoyboyBrian / Brian, Ali Romman, Nick Petalas and all original authors retained in the nested notices. No independent human or formal-kernel acceptance is claimed.
