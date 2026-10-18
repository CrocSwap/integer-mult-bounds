# Exact retired-slot eligibility masks

**Tooling improvement, no new κ.** This optional adapter accelerates the
historical joint-dual compiler by using coordinate-membership bitsets to
exclude ineligible retired slots before iterating in the unchanged priority
order. All compiler operations, paid frame changes, helper choices, dirty
restoration checks and emitted word bytes must remain identical.

Chafik Boukhalfa's [PR175](https://github.com/CrocSwap/integer-mult-bounds/pull/175)
already removes repeated sorting using ordered rank buckets. The new step is
geometry filtering before iteration. The comparison includes PR175's exact
archived compiler, as well as the slower compiler still used by the root
historical verifier. This does not claim PR175's ordering improvement as new.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
OS-random track assignment: **85**, verification engineering. `CLAIM.json`
records the shortlist, scope refinement, overlap checks and stopping rule.
There was no sprint coordination issue, so the claim is local.

## Measured result

Three cyclic-order rounds per axis on CPython 3.14.6 / macOS 26.5.2 arm64,
18 fresh processes in total. All generated words and all receipt fields agree.
Medians in seconds:

| Workload | Base sorting | PR175 buckets | Coordinate masks |
|---|---:|---:|---:|
| h=23 compilation | 54.310 | 19.668 | 4.346 |
| h=25 compilation | 93.476 | 31.894 | 6.548 |
| h=23 complete measured process | 57.422 | 22.499 | 7.443 |
| h=25 complete measured process | 97.542 | 35.837 | 10.875 |

Compilation is **4.53–4.87× faster than PR175**, and **12.50–14.28× faster
than the base compiler**. The complete measured process includes imports,
source checks, compilation, serialization, exact comparison, independent
word replay and transition reconstruction. Its improvement relative to PR175
is 3.02–3.30×. These are local measurements under ordinary machine load, not
a cross-platform guarantee. CPU timings and every raw sample are retained in
[`evidence/BENCHMARK.json`](evidence/BENCHMARK.json), together with exact hashes
of all executed adapter/runtime files. No timing result is an admission check.

The full public command was then run once separately and passed, including
six more matched timing processes. Its complete log and raw timings are in
`evidence/PUBLIC-REPRODUCTION*`. The two independent sequence audits cover
30,770 and 40,749 requests (71,519 total); `AUDIT-23.json` and `AUDIT-25.json`
record their coverage. Their `unfiltered_candidates` counts sum whole retired
set sizes, **not** actual predecessor visits before early return.

All **12 focused tests** and **16 unchanged historical control tests** pass.
The latter include omitted XORs, nonnested frames, missing/aliased outputs,
unpaid cancelling scatter, omitted transitions and understated width. Local
temporary fixtures were retained for inspection; the assertions were unchanged.
Reproduce those existing controls separately with
`python3 -B -m unittest discover -s tests -p 'test_joint_reclaim.py' -v`.
The selected-record/source-inventory check and staged whitespace check pass.
This is local evidence; remote CI is not asserted to have run.

## Reproduce

From a full checkout, using Python 3.11+ and only its standard library:

```sh
python3 -B research/reclamation-priority-performance/verify.py --out /tmp/reclamation-review
```

Use a fresh output directory. Expected final marker:
`PASS_RECLAMATION_PRIORITY`. The command runs focused tests, audits every
eligible candidate sequence on both shipped axes, then runs a sequential
three-engine timing comparison. Every generated word and receipt is retained
under the output directory, including failed-run files for inspection. It
never regenerates a repository certificate.

For the recorded three-round benchmark alone:

```sh
python3 -B research/reclamation-priority-performance/benchmark.py --rounds 3 --out /tmp/reclamation-timings
```

Expected: `PASS_RECLAMATION_BENCHMARK`. There is no timing threshold. Runtime
depends on machine load; the comparison runs sequential fresh processes and
rotates engine order. OS caches are not flushed.

## Evidence and implementation

`priority.py` maintains rank and coordinate-membership bitsets. `adapter.py`
checks the frozen source closure, then applies exactly three checked
in-memory substitutions: create the index, update it before a frame change,
and use its eligible ordered iterator. The original containment test and
elimination remain in place. Default commands and all existing sources,
manifests, certificates and `upstream/` are unchanged.

`SOURCE.json` pins the base manifest, compiler, consumer verifiers and the
exact PR175 compiler bytes. The original manifest checks and `check_sources()`
also run. Each measured process rebuilds one complete `h=23` or `h=25` axis,
compares the **entire decompressed physical word** to the frozen input, and
compares every compiler-receipt field. The independent serialized-word checker
then replays the fresh word's complete input/dirty basis in both orientations;
the transition consumer independently reconstructs paid events from its XORs.

The untimed `audit_index.py` compares the full eligible sequence at **every**
acquisition to an ordinary sorted-set oracle using the original current
frames. It checks candidates after the first successful one too. Unit controls
exhaust three-coordinate frame pairs and exercise 2,400 seed-85 set/frame
changes with sparse IDs up to 40,337. Five deliberately stale or incorrect
index mutations are detected. Source tampering, duplicated substitution sites,
disabled assertions and reused outputs are rejected.

The exact invariant and control-flow argument is in [PROOF.md](PROOF.md).
[NOTICE.md](NOTICE.md) credits eumemic, Chafik Boukhalfa, Rohan Gupta, rfu08
and inherited contributors, and discloses substantial OpenAI Codex assistance.

## Limits

This measures historical axis compilation and its replay/transition process.
It is not a speedup measurement of integer multiplication, the selected
frontier's cold replay, or the full joint-dual verifier with C++ CRT profiles
and assembly. The selected #626/#543 certificate remains
κ = `51110230636731/31250000000000000`.

The source-pinned adapter is opt-in and sequential. Future compiler versions
require a new source review; mutation during a partially consumed iterator is
only supported under the pinned acquire-and-return control flow. No global
optimality or formal multiplication theorem is asserted. Inherited all-size
compiler, physical realization, hosting, residual, precision, tape, recovery
and analytic obligations remain. The repository-wide `make verify`, supplier
cold rebuild, C++ profile computation and Lean are outside this isolated run.
