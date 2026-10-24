# Validation record

The portable package replay passed on 22 October 2026. It used Python
3.14.7 and SymPy 1.14.0, with isolation and optimization enabled. All
17 exact checks ran in sequence. The run took 63.873 seconds on this host;
that time is not a performance claim.

```text
PASS_ACTUAL_QUERY_INFORMATION_BOUNDS_PACKAGE
```

[validation/REPLAY.json](validation/REPLAY.json) records each status,
duration, output hash, and the exact source-manifest and replay-script
hashes. The [logs](validation/logs) retain the literal command outputs.
The replay checks the full typed JSON receipts, with the declared portable
source-hash updates. The optional cover sixth-moment fields are omitted
because that extension is outside this package's claims.

The run checked the reverse source reconstruction, fourth and fifth
moments, independent moment arithmetic, all 712 snapshot input columns,
all 16,687 availability intervals, the cone support law and exact minors,
support distance 53, the global cut bound 42, the twelve rank-five cut
certificates, the two rank-eight certificates with their FULL extensions,
the cover traces, and the residual factorization. Separate implementations
checked the moment arithmetic, support, global cut, rank-five and rank-eight
cuts, cover traces, and residual algebra.

The inherited controls ran as part of these checks. They include wrong
route order, changed snapshot coefficient/frame/interval, invalid quartet
data, an overstated quartet bound, wrong flag order, an understated edge
charge, a missing controller bridge, a wrong triangular sign, and the
constant-cover representation that does not satisfy the full-cover trace
premise. Exact receipts state the coverage of each control. No new search
was run.

The package proof review corrected one summary sentence: the kernel with
dimension d is `ker(V*)`, not `ker(V)`. The full historical residual proof
already used the correct adjoint. No numerical result changed.

The local native-lift receipt and global endpoint normal-form proof are
retained application dependencies. Their native checks were not rerun.
No new physical word, full supplier replay, recursive price, Lean proof,
or application to the selected PR4470 construction was checked.
