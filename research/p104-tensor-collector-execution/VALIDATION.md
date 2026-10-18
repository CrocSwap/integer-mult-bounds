# Verification receipt

Base `463113d675af7410ac91d53a4fed51ec6494eb9a`.
Executable replay commit `b9a2c1efdfd862aab7cd4cfd53529a81e0c76f00`.
CPython 3.12.14, standard library, Linux x86_64.

The complete registered replay passed on the frozen checkout:

```
Ran 8 tests ... OK
PASS_P104_PACKED_SMALL exact_arrays_and_retained_cleanup no_new_kappa
PASS_P104_PACKED_TENSOR
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-tensor-collector-execution outcome=completed
```

The tensor expected receipt was fixed before its full execution: retained
PR3243 outputs, direct scalar gather/promotion and a static call-count derivation.
All returned arrays are compared in full to the independent oracle, then
checked against the typed receipt. The 52/104/432/1664/2 macro counts agree.
The eight optimized groups include 2,401 exhaustive signed pairs, wide and
sparse-axis comparisons, 257-bit complete macros, wrong-phase/guard/cleanup,
implicit sign extension through 4096-bit encoded words, width-tag and overflow
controls. Three corrupted source paths fail before vendor import.

The n=18 original tuple evaluator was capped at 600 s without a completed result.
This is not a failed arithmetic assertion. The adapted evaluator completes the
same promoted fixture: 285.6036819 s execution, 4.9389859 s independent checks,
855160 KiB peak process RSS. The original complete endpoint remains unexecuted
at this size. A written component refinement and smaller exact differential
cases bind the representation to the unchanged source schedule.

Six final fresh serial benchmark workers on the same N=512 input give 8.44x
execution and 5.77x whole-process median improvements. Raw observations are in
BENCHMARK.json; startup, source checks and the oracle are included only in the
whole-process interval. Measurements apply to this host and Python reference,
not the physical C backend or a supplier tariff.

The final publication amendment changes only documentation and timing evidence;
all executable files and deterministic expected receipts remain identical to the
tested commit. The checks below validate the committed export and final metadata. No selected cold replay, physical-machine run, supplier-admission
review, independent human review or proof-kernel verification is claimed.

## Publication checks

The read-only Git-free export at documentation head
`956c88a465` passes all eight test groups and all four complete original/packed
small comparisons using CPython 3.14.7 with `-I -O -B`. No full n=18 cross-version
replay was run. Exported executable, input and deterministic receipt bytes are
unchanged in the final publication; the final amendment adds this receipt and
refreshes prose/overlap metadata only. Metadata/source pins, whitespace and
all committed package/input byte comparisons pass. Hosted CI is a separate
check, reported on the PR rather than inferred from local success.
