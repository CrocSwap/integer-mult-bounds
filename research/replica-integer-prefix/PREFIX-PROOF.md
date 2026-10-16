# Integer prefix reserve

The change concerns the integer number of reserved bits, `PAYLOAD`. It does
not change the dyadic outer cutoff `L` or the integer exponentiation used to
represent that cutoff.

For these nine-stage words, the independently recounted required global
prefix is

```
required = actual_local_prefix + 37 + 2*(9*T) + 4.
```

The native local prefix maximum is derived from the exact positive rational
peaks in both orientations of both providers. The complete source manifest,
native cache inventory, word/program hashes, native receipt and freshly
recounted invoice bind those peaks. The native 192-bit caps remain in force.
The invoice and assembly independently require exact equality between their
recounted maximum and the bound in the generated geometry.

The original selector rounded the required bit count up to a power of two.
The derived selector uses `PAYLOAD = required + 1`. This is a positive integer
and satisfies the existing strict requirement `required < PAYLOAD`. The
assembly formerly accepted equality as an intermediate check; the derivative
strengthens that check to strict inequality, matching the invoice and
independent checker. No scalar operation, helper, buffer, stock family,
compiler allowance, or finite work charge is removed.

The finite row is independently recounted as

```
row = 2*physical_stock_bits + 9909 + 252 + 2*PAYLOAD < 20161.
```

With actual local maximum 70, T104 gives required 1983, PAYLOAD 1984 and row 19417.
The named T124 geometry gives required 2343 and PAYLOAD 2344; if its actual
physical stock has 2645 bits, its row is 20139. These are arithmetic statements;
a literal fill and complete release replay are required to admit a candidate.

The source proof `research/bootstrap-depth-audit/sources/pr387/PROOF.md`,
“Finite cutoffs and constants,” permits any integer `ell >= 1` with
`C < 2**ell`. It requires the two inequalities

```
L*delta**2 >= 36
L*delta >= 2*(4+ell).
```

The inherited assembly initializes `ell=PAYLOAD`, chooses a dyadic `L=1<<e`
that satisfies both inequalities, and retains the carried constant update
`ell_next=max(PAYLOAD,ell+ceil(L*delta_a))+1`. All these checks remain unchanged.
The memoized outer witness includes PAYLOAD and both assembly/outer source
hashes in its key, so changing the reserve cannot reuse an old cutoff witness.

This preserves the inherited conditional premise that the selected bit
reserve dominates the relevant unmeasured primitive constants. Neither the
source package nor this derivative measures all such constants or proves an
unconditional all-size compiler theorem. In particular, a finite prefix
calculation alone does not establish that premise. T124's 2344-bit
reserve is larger than the prior 2048-bit reserve; the T104 positive control
tests the changed arithmetic implementation with its 1984-bit reserve.

The ten geometry controls retain all six original mutations and add exact
local-bound changes in both directions, a coherently underfunded global
reserve equal to the required prefix, and a row equal to 20161. The new controls
require rejection at the named strict guards. `evidence/T104-POSITIVE-CONTROL-SUMMARY.json`
records all ten rejections from the complete T104 positive-control release.
The earlier repriced fixture was a separate preflight check.

The source-level derivative is recorded as exact replacements directly from
the pinned original PR2824 files. The final root `DERIVATION.json` additionally pins the complete 541-file source and
full headline claim at PR2833 head
`e9307b48d7d1b690939935ecef0f8e524e6d92f4`. Its comparison uses exact fractions,
checks the complete decimal against `kappa_rational`, and performs no decimal
truncation. PR2833's changed native words require their own fresh native
preparation; the old-word positive control does not validate them.

The first T124 full attempt passed the positive owner audit but a mutation
worker failed. Its inherited runner discarded child stderr. A diagnostic rerun passed the missing worker’s assigned controls; the complete
16-worker rerun then passed all 25 original mutation controls. Source review identified an
independent transport defect: all workers wrote the same temporary pathname
before renaming it to their respective final shard paths. A deterministic
two-worker interleaving reproduces `FileNotFoundError` with those exact source
statements and preserves both correct payloads after using distinct temporary
paths. That witness does not recover or identify the original lost exception.

The final root `admit_integer_prefix.py` derivative adds only the per-shard-and-process
temporary pathname repair to the already reviewed reserve adapter. It keeps
all 25 mutation predicates, control names, atomic final replacement and
exact-once merge assertions. The previous adapter and failed work remain preserved locally; their hashes
and failure/diagnostic evidence are recorded in `evidence/SHARD-TRANSPORT-REPAIR.json`.
The repaired derivative passed a new complete admission in a fresh directory. The reproducible transport witness is
`evidence/SHARD-TEMP-RACE-CONTROL.json` (replay: `check_shard_transport.py`).

Credit: PR2824/PR2827 replica lifting and allocation by Dugongue; PR2833's
changed native words and its credited predecessor chain; the PR2802 native
package and inherited finite/outer proofs. This derivative was prepared with
substantial OpenAI Codex assistance.
