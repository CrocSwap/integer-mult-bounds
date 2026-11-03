# Exact unit-price optimum with one reusable clean checkpoint

One reusable clean array never reduces the unit-price signed-leaf count
beyond a clean root in the ordered binary, reserved-connector class.
For `s >= 1` scratch arrays and `n <= 2^s` factors, the exact minimum is

```
F(1)=1, F(2)=3,
F(n)=6q(n-2q),    3q <= n < 6q, q a power of two, n >= 3.
```

Above `2^s` factors the class is infeasible. The value is independent of
the admitting scratch cap. A clean root and balanced dirty children
attain it using the least possible cap `ceil(log2(n))` for `n >= 2`.

Claim type: scoped written proof with exact finite corroboration. No new
kappa, physical supplier or complete multiplication theorem is claimed.
This contribution was produced by Nick Petalas. Independent human and
formal proof-kernel review are unclaimed.

Stephen Shore / nightangelflowerwin-ops's [PR788](https://github.com/CrocSwap/integer-mult-bounds/pull/788)
gives the reusable-array grammar, a strict unequal-price improvement and
the equality at 54 unit-price factors. FanPUYen's
[PR714](https://github.com/CrocSwap/integer-mult-bounds/pull/714) gives the
displayed clean-root formula. The new result is its optimality under
arbitrary clean-array reuse for every factor count and cap. Neither the
formula nor the numerical value `F(54)=2112` is claimed as new.

[PROOF.md](PROOF.md) proves the root inequalities and the all-tree lower
bound. [verify.py](verify.py) evaluates the full clean/dirty recurrence
without importing or running predecessor code. The receipt emitted to
stdout binds all six package source files by SHA256. It is generated on
each replay; there is no handwritten receipt.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/one-clean-unit-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/one-clean-unit-optimum --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/one-clean-unit-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/one-clean-unit-optimum/verify.py
```

Each direct run prints a generated JSON receipt and
`PASS_ONE_CLEAN_UNIT_OPTIMUM`. The registered hook runs both direct modes
under separate 60-second limits. Direct replay needs only this package;
Git, network, numerical libraries and predecessor scripts are unnecessary.
Source metadata uses the exact Git provenance in [SOURCES.json](SOURCES.json).
Those four predecessor documents are proof provenance, not executable
inputs. Their original attribution remains unchanged.

The finite checks cover all factor counts through 256 and caps `1..10`,
every root split through 256, and large integer identities near dyadic
breakpoints. An iterative emitter checks attaining words at factors
`2..32,54,63,128`. Dense coefficient execution tracks every arbitrary
source, target and dirty-input column under noncommuting integer factors,
including literal inverse restoration. Ten controls cover omitted cleanup,
a dirty purported clean entry, reversed factor order, a wrong sign,
aliasing and invalid factor counts. The receipt enumerates the actual
coverage; finite tests support the written all-n proof.

## Scope and engineering limits

The `p104-side-correction` card changes scope to a recursive helper's clean
storage assumption. This is a side result about schedule count, not a
profitable P104 split. The current source-binding first example passed on
canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19380579)
records the question and overlap limits. The selected frontier is unchanged.

Unequal prices, two clean arrays, higher arity and nonreserved lifetimes
are excluded. Dispatch, provisioning, admission scans, routing, precision,
native implementation, hosting, compiler and outer costs remain payable.
The PR628 rounded leaves, selected scientific cold replay, Lean and Docker
were not run. No complete multiplication assumption is discharged.

The new verifier has no recursion. Its tables are bounded by 11 by 257
entries, its integer input helpers reject values with more than 1024 bits,
and emitted words are bounded by the 256-factor formula. Python allocates
managed objects during execution; fixed-allocation compliance is not
claimed. The control helper's indirect call has only the two explicit
targets `optimum` and `execute`. All acceptance checks use exceptions and
remain active under `-O`. Package replay is the available recurring
diagnostic; warning-as-error execution is registered. No additional Python
static analyzer was available on PATH.

## Open next questions

- Which unequal-price sequences still have a clean-root optimum? The
  theorem settles equal prices, while PR788 shows that arbitrary unequal
  prices can benefit from reuse. Start with monotone price sequences and
  the predecessor's weighted recurrence. A useful criterion must retain
  ordered factors and the scratch cap; no such criterion is supplied here.
- Can a source-bound caller supply the one clean array at a cost that
  survives its complete signed invoice? Start with one actual lifetime,
  including initialization, admission and cleanup. No physical occurrence
  or positive complete supplier margin is established here.

The structured versions are in [TASK.json](TASK.json). Following the first
proved result, neither question was pursued in this contribution.

## Credit

The new all-n reuse lower bound and its checker were produced by Nick Petalas.
Credit Stephen Shore / nightangelflowerwin-ops for PR788's grammar and
weighted construction, FanPUYen for PR714's clean-root formula, Chafik
Boukhalfa / chafreaky for PR628, 0xkilgore for PR663, androolloyd for PR673,
and the retained reversible-echo lineage. Better-Call-Paul's PR829 studies
the separate two-clean resource. Convexity and binary-tree induction are
classical. No predecessor file or credit line is changed. Apache-2.0.
