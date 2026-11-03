# Sharp coefficient-bit margins for every odd ADDRESS kernel

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped arithmetic proof with exact finite corroboration.
For every odd kernel q>=3 and every integer j>=0, the named ADDRESS
coefficient-bit tariff has these sharp excesses over its q=1 bill:

```text
                         j=0    j=1    j>=2
word excess                 4      6       8
fused excess               14     20      24
baseline excess            16     24      32
```

At each fixed exponent, each minimum is attained exactly at q=3. The
global fused minimum is 14, and the baseline minimum is 16; each occurs
only at (q,j)=(3,0). The conclusion holds for either sign of the query
powers. [PROOF.md](PROOF.md) proves the unbounded statement.

Wentao Li / VictorLiwentao's [PR3702](https://github.com/CrocSwap/integer-mult-bounds/pull/3702)
supplies the ADDRESS lowering, tariff and finite comparison for five
non-dyadic kernels at j=0,...,32. James Reed's
[PR3704](https://github.com/CrocSwap/integer-mult-bounds/pull/3704) and
[PR3752](https://github.com/CrocSwap/integer-mult-bounds/pull/3752) retain
that finite scope and its margin. The new contribution removes both
parameter cutoffs and identifies the unique minimizing kernel at every
exponent. No predecessor scientific replay is imported or rerun.

The sharp global margins were already observed on the finite grid; their
numeric values are not claimed as new. Their uniform validity, the
exponent-dependent bounds and uniqueness are the new result.

## Exact contract

For a reduced rational coefficient x=u/v, v>0, charge
`c(x)=bit_length(|u|)+bit_length(v)`, including `c(0)=1`. The ten unit
coefficients cost 20. With a=k/4, the other coefficients are
`a, 1+a, -a, -a, -1/a, 1/a-1`. Define

```text
T(k)   = 20 + 4 c(a) + c(1+a) + c(1/a-1),   k != 0,
F(q,j) = 2 T(q 2^j) + T(q 2^(j+1)),
B(q,j) = 4 T(q 2^j).
```

Reducing a to u/v gives
`T(k)=20+5[ell(u)+ell(v)]+ell(u+v)+ell(|u-v|)` for positive k,
where ell is bit length. Four dyadic cases prove the comparison. This
avoids inferring monotonicity from the size of k, which would be invalid:
T(1)=45, T(2)=38 and T(4)=32.

Extending the kernel or exponent search cannot find a cheaper odd kernel
in this tariff. An improvement needs a changed lowering or cost model.
The tariff is a coefficient-table proxy, not a complete physical bill.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/uniform-odd-kernel-margins/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/uniform-odd-kernel-margins/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/uniform-odd-kernel-margins
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/uniform-odd-kernel-margins --check-source-history
```

Another CPython 3.12 path may replace the displayed local installation.
The direct verifier writes no files and prints
`PASS_UNIFORM_ODD_KERNEL_MARGINS` after a generated JSON receipt with
SHA256 hashes of all six package files. This is not a proof-kernel receipt.
Each registered command has a 60-second timeout. Source-history checks
require the committed package and full Git history.

The checker compares direct Fraction charges of the six coefficients
against the new integer formulas. It checks:

- 20,440 kernel/exponent fixtures, q=3,5,...,1023 and j=0,...,39,
  including both signs and the following exponent needed by fusion.
- 640 fixtures near powers of two through 1,024-bit boundaries, at ten
  exponents through 1,023.
- Kernel 3 sharpness and the dyadic reference at each of 1,024 exponents.
- Fourteen invalid-input rejections and seven zero-coefficient or false
  stronger-margin controls.

Fixture families overlap. These counts describe executed cases, not
distinct cases or an exhaustive unbounded census. The written proof
establishes the universal quantifiers. Explicit exceptions preserve every
acceptance check under optimized Python.

## Source and limits

[SOURCES.json](SOURCES.json) pins the predecessor README and tariff file
as historical provenance at canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Neither is an executable or
live mathematical dependency. The selected record and original card are
also provenance. [TASK.json](TASK.json) records the explicit scope change
from the uniform-transfer-audit card to this arithmetic side result,
the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371215)
and the open question.

The source-binding baseline passed at that base, priorities revision 8,
selected conditional kappa .003125804. Main README searches, merged-PR
searches, live open/account PRs, active Discussions, handoffs and local
reservations were checked. Those bounded searches do not cover unpublished
work or arbitrary historical diffs; sparse local-note coverage is partial.

No optimal ADDRESS lowering, different tariff, native implementation,
hosting, routing, restoration, paid supplier, selected-frontier change or
new kappa is claimed. All five selected framework assumptions remain.
The selected cold replay, Lean and Docker were not run. Independent human
and formal proof-kernel review are unclaimed.

Only verify.py is executable. Its loops have fixed fixture bounds and
functions are below sixty lines. The parameter interface bounds q below
2^2048, j through 1024 and literal powers through 4096 bits. These are
verifier resource limits, not restrictions on the written theorem.
Power of Ten rules 3 and 9 have managed-runtime deviations: Python's
Fraction, integer and JSON operations allocate dynamically, and the
fourteen input controls use fixed local callbacks. At most six one-MiB
package files are read for the receipt; scientific fixtures stream their
results. There is no recursion, network call, subprocess or dynamic code
loading. Warning-strict normal and optimized execution supplies the
available runtime diagnostics; no external static analyzer is claimed.

## Open next questions

Does a specific physically justified coefficient encoding change the
cheapest odd kernel? First specify its complete code-length bill for
the same six coefficients. This matters because the present proxy is
only one part of a physical implementation. An alternate tariff and
complete hosting implementation are missing here. No continuation is
reserved.

## Credit

Wentao Li / VictorLiwentao retains PR3702's tariff, lowering and finite
comparison, with PR2687's odd-kernel interface, PR2593's kernel-three
construction, PR840's dyadic query pair, and the retained PR521/677
ADDRESS/DATA lineage. James Reed retains PR3704/3752's finite margin
records. Reduction of rational fractions and binary bit-length
arithmetic are elementary; no general mathematical priority is claimed.
The contribution here is the uniform sharp comparison and its proof.
