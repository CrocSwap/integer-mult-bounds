# Validation record

Environment: macOS, Python 3.14.7, one CPU thread. No solver, external Python
package, predecessor import or network call is used by the checker. The
package copies its required source files. All Python checks use explicit
exceptions, so Python optimization does not remove the checks.

## Test value and scope

The test-audit authoring gate was applied before this checker was added.
Each check has an independent mathematical or package contract:

| Check owner | Contract | Failure detected |
|---|---|---|
| Full six-field census | Native orbits and ordinary endpoint on all addresses | Wrong push direction, lost short orbit, wrong fixed-address count |
| Separate reduced census | Closed orbit formula over prime powers | A prime-only formula used for a composite power |
| Rational lowering | Seven literal events equal the pinned native matrix | Wrong coefficient, event order or ADDRESS child |
| Complete symbolic VALUE execution | Actual DATA and all arbitrary dirty helper outputs | A correct rank comparison with an incorrect word or encoder |
| Literal inverse execution | Exact restoration through reverse execution | An incorrect affine inverse or decode order |
| Two-fiber execution | Every child retains every spectator address | Correct first fiber but an omitted second fiber |
| Complementary small blocks | Algebraic factors have full required rank, zero product and correct sum | A one-dimensional or singular core |
| Package command | Copied, isolated, optimized replay uses the complete exact receipt | Hidden imports, changed source bytes or identity, wrong child volume, Boolean/integer coercion |

The full VALUE execution checks each input bit as an independent binary
column. It covers all VALUE assignments by linearity. It does not enumerate
those assignments. The two-fiber execution adds a real spectator dimension;
it is not a multiplication of a scalar count. The package command adds a
separate distribution and receipt contract. No production API or test-only
injection hook was added to support these tests.

The primary endpoint owner rejects four modified literal words: omit an
ordinary child, omit a full-row XOR, omit a final decoder transfer, and corrupt
a dirty helper. The spectator check rejects a child restricted to its first
fiber. Separate scope controls use an actual two-cycle, a nonunit power at
m=9, and the wrong full-order-only orbit count. These checks do not establish
statements outside the written theorem's hypotheses.

## Commands

Run the standalone exact replay from the repository root:

```sh
python3 -I -O -B research/native-query-boundary/verify.py
```

Run the relocation and certificate rejection checks:

```sh
python3 -I -O -B research/native-query-boundary/check_package.py
```

The package check creates one temporary directory, copies this package, and
runs from outside the copied directory. It first requires a valid optimized
replay. It then requires the correct rejection guard for each mutation. It
restores copied inputs between cases and removes only its own temporary files.
The source checkout is not changed.

Expected markers:

```text
PASS_NATIVE_QUERY_BOUNDARY full_addresses=665444 prime_power_cases=13 dirty_columns=2187 escape_children=6 no_new_kappa
PASS_NATIVE_QUERY_PACKAGE relocated_optimized_replay changed_pinned_source_rejected changed_source_identity_rejected child_volume_rejected boolean_count_rejected
```

The certificate was emitted from a normal isolated Python run. The committed
certificate is then checked without emission by optimized Python. All source
copies have exact byte hashes and Git blob pins in SOURCES.json. The receipt
binds the complete source manifest by SHA-256. Thus a changed source identity
is rejected even when the copied bytes stay unchanged.

## Evidence limits

The written proof covers all odd prime powers, all spectator volumes, the
stated conjugacy class, and the constructive two-block theorem. Finite
execution covers only the listed domains. Large three-genuine-row encoders
are not instantiated. The small direct-sum templates check their exact
algebra and dimensions; they are not a large-domain tape replay.

The literal program is an exact binary VALUE execution. Its complete-scan
bit-transfer implementation is described and priced in the proof. It is not
a benchmark of a Turing machine, a fast encoder, or an admitted recursive
supplier. No practical multiplication performance was measured.

The selected-record gate checks the selected frozen files at the base. It is
not the selected construction's cold replay. No selected artifact or existing
code is changed, so this contribution does not regenerate that construction.
The full repository `make verify` and selected cold replay were not run for
this isolated package. Their scope includes unrelated large regenerations.

## Recorded results

On 2026-10-13, the normal isolated receipt emission passed. The first frozen
optimized comparison then rejected the receipt. The cause was JSON key
normalization: internal integer orbit lengths became string keys on loading,
and the two key types had different sort orders. The two receipt histogram
fields now use JSON string keys at their output boundary. The optimized
relocated replay and all rejection controls then passed. The final rerun
also binds the complete source identity manifest.

`make selected-record-check` passed at the exact base in the complete lane01
checkout. Its marker was:

```text
PASS selected record, exact kappa, original source inventory and proof supplement: 1661960547713947/1000000000000000000
```

No mathematical check was bypassed after a failure. No failed receipt was
changed to record success. The final certificate was generated from the
checker and then checked through the normal command.
