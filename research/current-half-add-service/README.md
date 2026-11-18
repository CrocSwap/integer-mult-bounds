# A rounded service at the current half-ADD boundary

This source-bound construction joins an existing literal rounded ADD to
one exposed boundary in [PR 7660](https://github.com/CrocSwap/integer-mult-bounds/pull/7660).
It also proves an exact terminal-error property of the current native word.
No new kappa or complete caller admission is claimed.

At head `d12b854d4825e9edfa3a3466909e1abf3525e929`, the candidate word has
SHA256 `f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669`.
Its zero-based clock 100504 is `ADD 210,457,-1/2` in chart 218, after the
role-457 MOVE from chart 966. Exact same-grid arithmetic requires an even
source numerator. The retained nearest-up service computes
`x - floor(y/2)` on every canonical signed field whose rounded output fits.
No evenness condition is needed on that domain.

The source-specific result is stronger than a norm estimate. Among all
49504 later native events, only clock 100527 touches role 210, with
`ADD 210,292,-1/2`. No later event reads role 210 as a source. Therefore
the difference from this single rounded site reaches native return only
in public role 210, with multiplier one. It affects no owned erasure.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[VENDORED.json](VENDORED.json), and the retained input pins in
[SOURCES.json](SOURCES.json).

## Literal execution and charge

The unchanged compiler and primitive executor from
[PR 6988](https://github.com/CrocSwap/integer-mult-bounds/pull/6988)
produce a 669-row, 210-state table with three reachable carry values.
The table uses only branch, write, unit move, goto, halt and reject.
Runtime tape payloads are not read by a numerical callback.
The exact local source token selects the table in the primitive fixture.

The service uses two distinct private work banks. For R real components,
S=sum(w_i+1), old dirty physical lengths A_0,A_1, and Q_c borrowed contexts,
the retained all-size bound is:

```text
512(S+1) + 64R + 7(A_0+A_1) + 16Q_c
```

The units include physical reads, writes, unit moves and executed control
rows. Private resident backing is
`max(H_0,3S) + max(H_1,3(S+1))`, with prior capacities H_0,H_1.
Source/table setup, public fields, metadata and protected ancestors remain
separate positive charges. No exchange rate to the old supplier tariff is
assumed.

At widths 1 through 5, the literal interpreter checks all 1364 signed
input pairs: 1193 succeed and 171 correctly reject on final range.
Further checks cover both odd signs, late whole-field overflow, reuse of
87 dirty work cells after failure, and a 512-complex-value field.
That field uses 985272 measured physical/control actions including a
64-step wrapper allowance, below the bound 2687504.
These are operation counts, not wall-time performance measurements.

On success, the source and context stay unchanged, all heads return and
both work bodies are erased. On failure, the complete public target stays
unchanged; work and heads can remain dirty. Six controls cover a wrong
clock, wrong coefficient token, wrong-sign table, late overflow, a legal
outbound read of role 210, and a legal SCALE that changes the error gain.

## Error and range

For each real component, the error relative to exact halving is
`Delta*(y mod 2)/2`, where Delta is the grid step. It lies in
`{0, Delta/2}`. For N complex coordinates the field error is at most
`Delta*sqrt(N/2)` in Euclidean norm. The odd-pair fixture attains this
bound. The exact native-return multiplier is one; all other field and
owned-observation differences from this one site are zero.

For a W-bit signed target with endpoints L and U, success holds exactly
when every component satisfies `L <= x-floor(y/2) <= U`.
This is a range contract, not a proof that every full-word trajectory
stays in range. The other half-ADD at 100527 remains a separate scalar
obligation. The comparison holds the other operations fixed and uses
their stated local semantics and nonaliasing.

## Limits

The result reuses CubeJerry's all-size scalar/lifecycle theorem. It does
not claim a new rounding algorithm or an independent replacement proof
of the retained compiler. The new work is the current source binding,
literal consumer fixture, precise charge specialization and terminal
error theorem. The fixture invokes the unchanged primitive method on
its required state. It does not run the complete recursive Controller.

No full native prefix is executed on these local odd fixtures. No complete
17-call rounded caller, all-coefficient installation, common physical
tariff, private backing schedule, native provider or outer recovery is
established. The five inherited assumptions remain: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`.
The source's conditional bound and the selected record are unchanged.

## Reproduce

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/current-half-add-service
```

Both commands must print `PASS_CURRENT_HALF_ADD_SERVICE`. The runner must
print `PASS_REGISTERED_RESEARCH_PACKAGE`. The normal and optimized isolated
commands read only the declared inputs. They write no files and use no Git
or network. The official export includes the retained source closure.

## Open next questions

Check whether the two half-ADDs can share a rounded-domain guarantee or a
joint rounding rule without changing the input epochs. Then bind all
17 occurrences to the signed caller and charge the physical work.
[TASK.json](TASK.json) records these questions and their open obligations.

## Credit

Clear1nsight supplied the exact PR7660 candidate and requested this scalar
review. Its retained NOTICE credits DreamingOfClouds, SYLforge, Ali Romman,
Rohan Arun and the source lineage. CubeJerry supplied the unchanged literal
rounded scalar compiler, lifecycle executor, physical fixtures and all-size
cost proof. [PR 6990](https://github.com/CrocSwap/integer-mult-bounds/pull/6990) and
Nick Petalas's [PR 7268](https://github.com/CrocSwap/integer-mult-bounds/pull/7268)
are related general compiler work; neither is imported here. The scalar source headers and the declared
source closure retain their licenses and attribution.

Ali Romman directed the new source-bound proof and verification with
substantial OpenAI Codex assistance. New work is Apache-2.0. The base is
`e54523517d0f03e58352e647c403a5af3e525a57`.
