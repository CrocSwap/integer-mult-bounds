# Exact packed execution of the actual P104 tensor collector

This opt-in representation adapter targets the unfinished implementation
comparison in commdata2338's PR3243: the retained PR3131 nested evaluator on
the promoted actual multiplicity-two collector (`n=18`, 262,144 Gaussian
coordinates, rank 14). PR3243 already checked that mathematical boundary using
two direct evaluators; its two retained-program attempts stopped at 600 seconds.
This package keeps the nested program and its cleanup checks executable.

The evaluator batches exact signed arithmetic into isolated lanes of Python
integers. Encoded words retain their width while storing repeated sign bits
implicitly. This preserves the original 160-bit backend contract, scalar
rounding order, both native calls, all four wrappers and protected oracles.
Every arithmetic overflow, exact downshift, signed-word boundary and private
return remains checked. No floating point or result cache is used.
[PROOF.md](PROOF.md) gives the componentwise representation argument and
source substitutions. `adapter.py` authenticates the original program before
applying count-checked substitutions; frozen predecessors are unchanged.

## Measured result

The promoted actual tensor comparison **passes**: all 262,144 coordinates,
original macro counts, source preservation and literal cleanup agree. Its
packed execution took **285.604 s**, followed by **4.939 s** of independent
checks. The same-input original tuple run was still unfinished at its
600-second process cap; that is an incomplete run, not an arithmetic failure.
The unmodified original full-size executable is not claimed to have finished.

Three alternating fresh-process pairs at N=512 give these medians on
CPython 3.12.14 / Linux x86_64:

| Measured interval | Original | Packed | Speedup |
| --- | ---: | ---: | ---: |
| Complete collector execution, including packing/unpacking | 2.565 s | 0.304 s | 8.44x |
| Whole process, including binding and independent checks | 2.724 s | 0.472 s | 5.77x |

`BENCHMARK.json` contains raw observations and the exact environment. The
larger case has one completed packed measurement and a capped baseline, so no
completed large-case speedup ratio is claimed. These are measurements of the
Python reference, not of the conditional fast physical algorithm.

## Evidence and scope

`RESULT.json` records deterministic endpoint, source, grid and complete macro
receipts. The full replay compares **every coordinate** of entrance, sent,
returned and updated query arrays with PR3243's separate column/parity oracle
before hashing, preserves all five sources and the entrance query, and checks
literal private zero. It also checks PR3243's previously published fixture and
output hashes. Small full collectors compare the original and packed programs
on promoted, rounding, cancellation and zero fixtures.

Signed local pairs, arbitrary signed arithmetic, cross-lane contamination,
inputs through 257 bits, nonconsecutive axes, both orientations and differing
block plans are checked separately. Controls retain the original unguarded
CNOT distinction, omitted phase rejection and omitted cleanup rejection.
Malformed axes, signed overflow, inexact shifts, width-tag mismatch and changed
source bytes fail. Tests also run with Python assertions disabled.

This is **verification tooling and finite implementation evidence**. It does
not execute the fast physical C backend, reduce its recursive rank or cost,
admit a supplier or improve kappa. The physical/compiler and stock-hosting
premises remain inherited. The frozen complete P104 consumer still fails the
599/584 zero-saving screen. A successful local execution does not authorize
further supplier expansion without a changed complete bill.

## Reproduce

From repository root with standard-library Python 3.12:

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-tensor-collector-execution
```

Expected markers include `PASS_P104_PACKED_SMALL`,
`PASS_P104_PACKED_TENSOR` and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
The full tensor comparison is bounded by the registered 600-second command
limit. Timing is not a mathematical acceptance condition.

For a fresh same-input benchmark (three alternating serial pairs at N=512):

```sh
python3.12 -I -B research/p104-tensor-collector-execution/benchmark.py
```

Use `--multiplicity 2 --repeats 1` for the larger pair; each command is capped
at 600 seconds. A timeout is incomplete performance evidence, not an arithmetic
failure. `BENCHMARK.json` retains measured one-host timings; execution includes
packing and unpacking, while process wall time also includes source binding,
fixture construction and the independent oracle. These are Python verifier
measurements, not physical-machine tariffs.

## Sources and coordination

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) binds main inputs and lists the exact predecessor
heads; [INPUTS.json](INPUTS.json) authenticates all executed and documentary
inputs, including five verbatim PR3243 files. CI does not need foreign PR Git
objects. `TASK.json` records seed 28, the three candidates, scope change,
stopping rule and overlap coverage. The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19003929)
takes PR3243's released handoff. PR3134's wrapper contraction is adjacent work;
this comparison retains PR3131's original protected wrapper schedule.

## Open next questions

Bind a reached fast physical C-backend trace to this exact endpoint, including
its owned workspace, heads, copies and cleanup. This is the next implementation
obligation; the reference still uses the original direct mathematical backend.
Separately, identify a changed complete P104 consumer that can pay for the
correction. Start with a complete profile and boundary invoice rather than
attributing supplier savings to faster verification. These questions and their
blockers are recorded in `TASK.json`; no new supplier search is proposed here.

## Credit

Jose Manuel's PR3131/3109 supplies the program and conditional construction;
commdata2338's PR3243 supplies the actual tensor fixture, independent oracle and
released comparison handoff. Credit Tekalign's PR3025/3033, Ross Richardson's
PR3072, Douglas Colkitt, ywz65, Vasek/flyingviper and the full retained native,
compiler and physical lineage. [NOTICE.md](NOTICE.md) gives exact heads and
further attribution; retained source notices are unchanged.

New work by Tekalign (@tekuuu), with substantial OpenAI Codex assistance in
design, proof, implementation, checking, measurement and writing. Apache-2.0.
No independent human or formal-kernel review is claimed.
