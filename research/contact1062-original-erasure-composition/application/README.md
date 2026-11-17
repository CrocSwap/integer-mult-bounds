# Combined application replay

Use CPython 3.12 with assertions and supply the exact `research/chart1062-original-erasures` package from #7644 at `32cfa1d20d3e4587dc601e69ccac1cd24a239e5c`. The complete run is offline. Reserve one local numerical slot separately for each stage under the shared process-tree admission rule. Use a previously absent work directory. The signed stage consumes the native result produced in that directory.

```sh
python3.12 -I -B application/run.py prepare --source "$source7644" --word "$frozen_word" --work "$work"
python3.12 -I -B application/run.py native  --source "$source7644" --work "$work"
python3.12 -I -B application/run.py signed  --source "$source7644" --work "$work"
```

Preparation rebuilds #7644 from #7605, authenticates its complete 138-file source closure, reconstructs #7642 and #7643 on #7605-origin clocks, and translates the #7644 splice onto #7643. The literal reconstruction must equal the frozen candidate and all metadata must match. The paid and target histograms are recomputed from every event and all 17 signed invocations for both predecessors and the candidate. Binary floating point proposes a conservative decimal only. The retained directed 256-bit integer engine checks this decimal and its guard, and rejects the same decimal against both predecessor invoices. Signed replay independently rederives a rational raw crossing, gate and framework claim. Its directed bracket is also checked by the integer engine.

The portable native and signed sources are the published #7643 replay's prepared sources. Their SHA-256 values are `8e70ede63a924e4babe202bd23a56ef6cfaaeffa4dc494fb38315e3aa5e60b85` and `d5e18dce27e9fbd465cb2b8a4456aa03b20983f8b88d8c6e3c1738e05ac06138`. The original #7643 full-run native checker has one additional gzip transport hash assertion, documented in `source/7643-PORTABILITY.json`. Both require the same canonical word and original operations. The final application function is extracted verbatim from the portable #7643 overlay. Every extension or adaptation to these sources matches exactly one source location. `PREPARED.json` records every prepared input and engine's digest. The frozen #7643 source, upstream notices and Apache license are in `source/`.

The native engine checks forward and adjoint action, equality at original ordered private source contacts and all 74 erasures, COPY guards, 1,569 final rows, original lifetimes, grammar and all physical chart columns and absolute phase. It checks the role-46 composed path, the three 134/329 contact identities, and both chart-1062 route contractions. The signed engine consumes the exact signed caller, checks ordinary costs, grids, all catalogue slices and main boundaries, precision, tape bounds, compiler and outer gates. Candidate-specific controls remove required corrections, remove charged MOVE events, corrupt a MOVE source, use the wrong chart, omit ownership cost, underbudget precision, and alter absolute phase.

A prepared receipt alone establishes a literal recount and invoice margin. The candidate requires successful native and signed exit receipts, a final receipt, directed crossing certificates and the separately derived independent check. A timeout leaves any unfinished stage unresolved. The original five framework assumptions remain native all-columns, owned erasure, compiler, precision/tape and analytic recovery.

Credit goes to the authors of #7643 and #7644 and their predecessors, particularly the #7610, #7611, #7612, #7605, #7604, #7480 and #7113 contributions, with the source-specific notices retained. OpenAI Codex materially assisted in producing the combined adaptation.

## Comparison with #7645

After preparation, the following check compares the combined word against Clear1nsight's original-74 role-46 construction at `32abeefff4d5fcc378ab3de1c1a8bf1c37737bdd`.

```sh
python3.12 -I -B application/peer_compare.py --source "$source7644" --work "$work" --out "$work/PEER-7645.json"
```

The checker authenticates the peer's signed and final receipts, cancels common paid and productive terms, and checks the sorted per-invocation prefix sums of the remaining ranks. The integer-power engine separately bounds both signed margins at the peer's public exponent and the signed difference between the two invoices. Clear1nsight's #7645 source notice is retained with those archived receipts.
