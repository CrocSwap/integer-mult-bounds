# Packed states for the historical cyclic routing audit

This tooling change reduces the cost of `routing_state_search` without changing
its search domain, pruning rules, receipts, or mathematical conclusions. It
preserves all 529,066 nonsaturated four-role states through depth seven, every
frontier SHA-256, saturation count, terminal count, and the complete eight cyclic
seed controls. There is **no new kappa, construction, or negative result**.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The original checker was preserved in commit
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0` by Douglas R. Colkitt.
`SOURCE.json` pins the original checker/certificate and the unchanged imported
dependencies. Only the historical certificate's checker-source hash changes;
`upstream/` and selected-frontier records remain unchanged. The selected
frontier at this original base was #626/#543.

## Object, method, and exactness argument

The original search stores `(A, R)`, where `A` consists of the `W` scalar rows
over F2 and `R` is a bit set of routable permutations in the original
lexicographic permutation order. Here `W` is 2, 3, or 4 and the depth cap is at
most seven. Starting with the identity, a gate performs `A[t] ^= A[s]` and
extends the routing set by the same physical transposition as before.

Let `b = W!`, `q = 2^W`, and let `A_i` be the integer encoding of row `i`.
The new state is the exact Python integer

    P = (sum(A_i * q^(W-1-i), i=0,...,W-1) << b) | R.

Every `A_i` lies in `[0,q)` and `R` lies in `[0,2^b)`. The fields therefore do
not overlap: this is a bijective encoding of the complete joint state, not a
hash or a scalar-only merge. In particular, different routing sets remain
different states even when their scalar matrices agree. Numeric ordering of
`P` is exactly the old lexicographic ordering of `(tuple(A_i), R)`.

An XOR update changes only the target's `W`-bit lane. No carries, modular
approximation, or narrowing integer conversion occur. Routing extension and
its per-call cache are unchanged. Consequently, induction on the BFS depth
preserves each frontier, the visited set, saturation counts, and stopping
conditions. Decoding sorted states back into the original representation
preserves the literal bytes sent to the original SHA-256 accumulator.

The terminal lookup enumerates all permutation matrices. This agrees with the
old one-hot-row predicate on every reachable matrix: distinct-row XOR updates
preserve invertibility, so a reachable matrix with one-hot rows cannot have a
repeated row. The optimization relies on this reachable-state invariant; it
does not offer a classifier for arbitrary singular matrices.

## Reproduce

Use standard-library Python 3.11+ and Git in a full repository clone containing
the base commit. No external Python packages are required.

```sh
python3 -B research/cyclic-routing-performance/benchmark.py --pairs 7 --out routing-benchmark.json
python3 -B -m unittest discover -s tests -p test_cyclic_routing_packed.py -v
python3 -B -m unittest discover -s tests -p test_finite_bit_contract.py -v
```

Use a fresh benchmark output path. Expected: the benchmark ends with
`PASS_IDENTICAL_COMPLETE_ROUTING_RECEIPTS`; the two test commands pass five and
nine tests respectively. The benchmark loads the original implementation from
the exact Git object, admits pinned dependency bytes, and runs the complete
certificate in both modes. Every field must match the frozen original after
restoring only the changed checker-source binding. It records all samples and
rejects source drift, changed receipts, and reused output files.

To regenerate the historical certificate, run
`python3 scripts/audit_cyclic_topology.py`. Its numerical and frontier payloads
remain unchanged. The new source binding is committed with this change.

## Measurements and validation

`RESULT.json` records seven sequential, alternating fresh-process pairs on
Windows 10 / CPython 3.12.14, x86-64, with the interpreter, Git version,
processor identifier, source hashes, and all raw samples. OS caches were not
flushed. Both modes perform the same source-admission and receipt checks.

| Measurement | Original | Packed |
|---|---:|---:|
| Complete-process wall median | 3.788324 s | 2.680431 s |
| Certificate execution wall median | 3.528838 s | 2.417635 s |
| Certificate execution CPU median | 3.515625 s | 2.421875 s |
| Python allocation peak, separate traced run | 131,099,209 bytes | 80,510,849 bytes |

The complete-process median is 1.413 times faster (29.24% less elapsed time).
The separately measured Python allocation peak falls by 38.59%. It is **not
process RSS**; `tracemalloc` is disabled in all timing samples. One memory run
per mode measures the complete certificate, not just a synthetic key array.
No timing threshold is imposed, and other environments may differ.

The additional same-host Windows matrix targets the Python versions used by
upstream CI. Each row has its own seven alternating before/after process pairs
and separately traced memory runs; it is not a comparison between versions.

| CPython | Original process median | Packed process median | Speedup | Allocation peak reduction |
|---|---:|---:|---:|---:|
| 3.11.16 | 3.436026 s | 2.553110 s | 1.346x | 38.59% |
| 3.13.15 | 3.628811 s | 2.902232 s | 1.250x | 38.61% |
| 3.14.7 | 3.842965 s | 3.198651 s | 1.201x | 42.42% |

`RESULT-python311.json`, `RESULT-python313.json`, and `RESULT-python314.json`
retain every sample. The Python 3.14 timings vary more; none were discarded.
Together with the two original 3.12 series, all 80 complete certificate receipts
agree. The measured benefit depends on the interpreter and environment; the
original 1.413x result is not a universal speedup guarantee.

`VALIDATION-MATRIX.json` retains source hashes and complete command output for
all 14 tests under 3.11.16, 3.13.15 and 3.14.7, plus all 14 under 3.14.7 `-O`.
These runs use the full depth-seven independent oracle. Reproduce with the two
test commands above under each interpreter, adding `-O` before `-m` for the
optimized-mode check; run the benchmark under each interpreter with a distinct
output filename. The matrix uses the standard library only, and does not alter
project dependencies or CI settings.

The new independent oracle uses dense F2 rows and literal sets of permutation
tuples, rather than either implementation's packed state or routing masks.
It compares every receipt field at every cap 0–7 for all three widths, including
an independent replay of all 529,066 four-role states. Full depth-seven receipts
are also compared with the original committed certificate. A deliberately
incorrect scalar-only merge still finds no survivor, but loses states and
changes frontier digests; the negative
control detects this loss. Other tests distinguish a depth cutoff from closure
and retain width/depth input rejections. The original finite-contract tests
independently enumerate short raw XOR words and exercise malformed circuits,
terminal obligations, routing failures, and budget exhaustion.
The oracle independently implements the state representation and transitions;
it shares the documented joint-state reduction and saturation rule, and does
not independently prove those reductions or the routing theorem.

Preliminary measurements are retained in `EXPLORATION.json`; profiled timings
are not used to claim the speedup. `INITIAL-RESULT.json` retains the first
seven-pair run (3.652717 s to 2.670171 s, 1.368 times faster). The final run
followed a source-admission review that added an
explicit upstream-manifest pin and removed two unused input pins; the numerical
kernel did not change. `VALIDATION.txt` records executed checks, including a
minimal offline replay in a path containing spaces and source-drift/output
reuse rejection controls.

## Scope, prior work, and attribution

Upstream advanced to `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261` during the
follow-up and selected #741. The compatibility record in
`VALIDATION-MATRIX.json` compares actual file bytes at that immutable main
commit: all 14 pinned dependencies, the original checker/certificate, the
finite-contract tests, the isolated test runner and general CI workflow are
unchanged (19 files). This preserves the original experiment's input basis;
it is not a replay or endorsement of the new selected construction. No frontier
record is edited or rebased into this contribution.

The [original routing note](../../docs/research/cyclic-topology-audit.md) supplies
the finite-state reduction and the edge-disjoint-routing rank argument. The
two/three-role frontier closes; the four-role frontier does not. The latter
still excludes only words through seven primitive gates. This work neither
extends that domain nor formalizes those arguments in Lean. The inherited
all-size, compiler, physical realization, precision/tape, and analytic transfer
obligations are unaffected.

Assignment seed **87** came from the Windows operating system cryptographic
random source via `RandomNumberGenerator.GetInt32(0,100)`. `SELECTION.json`
records the three candidates, profiling, overlap check, and local scope claim.
No pinned sprint coordination issue was available.

Douglas R. Colkitt authored the original checker, routing obstruction, and
historical certificate. Pending [PR154](https://github.com/CrocSwap/integer-mult-bounds/pull/154)
by eumemic reports other verifier hotspots; pending
[PR756](https://github.com/CrocSwap/integer-mult-bounds/pull/756) by Victor Li
optimizes the distinct balanced-Fano meet-in-the-middle search. Neither is a
code dependency or an independently reviewed result here. The frozen upstream
and all predecessor notices retain their attribution.

Contributor: **4RchYMing**, authenticated GitHub account ID 275918740; commit
email `275918740+4RchYMing@users.noreply.github.com`, as specified by the user.
Prepared with **substantial OpenAI Codex assistance**, including implementation,
proof reasoning, experiments, and tests. There is no claim of independent
human peer review. Apache-2.0, as in the parent project.

Full `make verify`, the selected supplier cold replay, Lean, and remote Linux
CI have not been run for this isolated historical-verifier change. The local
environment lacks `make` and a C++ compiler. At the follow-up check, upstream
Actions returned `action_required`, awaiting maintainer approval. The Windows
version matrix does not establish Linux CI success or a full theorem audit.
