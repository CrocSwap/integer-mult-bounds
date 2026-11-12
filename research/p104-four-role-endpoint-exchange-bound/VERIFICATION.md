# Verification and matched workflow trial

The registered and direct replays regenerate eight deterministic stage receipts. All dependencies are keyed by package-relative path in `LOCAL-PINS.json`, including both signed-caller Python files. The parser rejects duplicate keys. The input gzip and its decompressed payload are authenticated independently. No solver uses previous temporary state.

| Stage | Scope | Result |
| --- | --- | --- |
| Directed price | One compatible exchange, fixed paid itinerary | Positive only if realized with zero extra paid ranks |
| Chart and impulse census | 20,455 inherited cuts over 76,466 events, 20 s cap | 3,961 lack a coframe, 16,494 eligible in 15 banks, cap clear |
| Archived exact prefix solve | First eight of 15, 25 s limit and intentional eight-case cap | Eight excluded, seven unvisited in that receipt |
| Continuation exact prefix solve | The seven unvisited case IDs, 25 s limit | Seven excluded, cap clear, zero unresolved |
| Independent archived replay | Eight separators, all 16,016 constituent raw cuts, 25 s limit | Every bank zero, target nonzero |
| Independent continuation replay | Seven separators, all 478 constituent raw cuts, 25 s limit | Every bank zero, target nonzero |
| Shared exact-input trial | Same seven, one fixed direction, 25 s limit | Seven excluded, cap clear, zero unresolved |
| Independent shared replay | Same 478 constituent cuts, 25 s limit | Every bank zero, target nonzero |

The per-case search uses exact rational reverse rows and elimination. The independent checker instead propagates each exact sparse input forward through the literal event word, accounting for charts, owned INIT/CLEAR, and COPY freshness. It observes each state before the event and checks the target difference independently. A nonzero signed target is required, and opposite signs are valid. It also checks the contact-free bank intervals against the literal events. The two trial arms have the same case IDs, stop conditions and independently checked coverage. `lead/PREFIX.json` preserves the original eight-case receipt and unvisited keys. `receipts/CONTINUATION.json` and `receipts/SHARED.json` give the seven exact witness records. Their separate checker receipts preserve the raw-cut counts, key lists, target signs and input hashes.

Controls include the original positive four-role bare-exchange identity, an exact four-row span success, a zero-determinant case, and the coframe/impulse classification fixtures. The wrapper also rejects a leaking three-role witness that separates the target but fails the fourth row, and rejects a repeated dependency key.

## Workflow timing

The experiment used CPython 3.12.14, assertions and the same 25-second runner and independent replay limits for each arm. Measured runner and independent replay wall times are shown separately. The independent check itself uses the same code path and event coverage for both arms.

| Method on the seven resumed cases | Solver | Independent replay | Verified decisions |
| --- | ---: | ---: | ---: |
| Existing exact per-case method | 0.09 s | 0.63 s | 7/7, all 478 cuts |
| One precommitted archived input | 0.09 s | 0.67 s | 7/7, all 478 cuts |

Proof and source inspection for the shared trial took an estimated 42–60 active seconds. Shared-arm and scope implementation took about 35–50 active seconds, and drafting the common verifier about 38–55 active seconds. These are coarse tool-boundary estimates. The historical discovery time of the shared witness and a comparable split of active costs for the existing solver are unavailable. Packaging, relocated replay, and waiting are excluded. Since total effort to the same verified decision cannot be compared on equivalent records, the workflow trial is inconclusive and the existing exact per-case solver remains the default. No replacement word or complete candidate was constructed.
