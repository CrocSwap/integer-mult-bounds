# Recover the rounded inverse input from eight owner residues

A scoped proof with exact finite corroboration: the fixed 112-owner integer
rounded inverse of zxv's [#5444](https://github.com/CrocSwap/integer-mult-bounds/pull/5444)
is injective when only owners **5, 33, 49, 53, 62, 65, 97 and 108** are
required to be divisible by 32. All other input coordinates remain arbitrary
integers. Indices are zero based. This strictly enlarges the predecessor's
uniform sufficient input lattice `32 Z^112`.

The new row certificate has `2A^-1` integral. A shared output bounds quotient
differences by thirteen, while equality of the eight residues modulo 32 makes
every quotient difference a multiple of sixteen. This proves injectivity on
every fixed residue coset. A direct decoder recovers any input from its output
and forty residue bits using eight scalar interval selections. A literal pair
in `16 Z^112` has the same output, so the common five-bit threshold on these
eight owners is sharp. [PROOF.md](PROOF.md) gives the matrices and full argument.

This answers one bounded part of #5444's unequal coordinate-lattice question.
The new certificate, sparse domain and decoder were produced by Nick Petalas.
The predecessor uniform frontier is cited, not audited. The selected frontier
is unchanged.

## What the improvement measures

The sufficient input-lattice index drops from `2^560` to `2^40`. This is a
larger injective domain, not a measured saving in fractional storage. The
forty-bit local residue channel uses more bits than the predecessor's optimal
thirty-bit packed same-grid tag, but needs observations on only eight owners
and has an explicit interval decoder. No global optimum for local observations
is claimed.

The theorem concerns `K(z)=z-M round_away(M^T z/52)` in its fixed integer
coordinates. Nonuniform input scaling need not commute with its linear part.
No implementation of the original physical inverse on unequal output grids,
paid residue acquisition, reversible cleanup, native realization, complete
invoice, new kappa or multiplication theorem is supplied.

## Reproduce

From the repository root, using CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/eight-owner-rounded-injectivity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/eight-owner-rounded-injectivity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/eight-owner-rounded-injectivity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/eight-owner-rounded-injectivity --check-source-history
```

The registered commands include normal and optimized execution. Each prints
`PASS_EIGHT_OWNER_INJECTIVITY` in a generated JSON receipt bound to the six
package files' hashes. No handwritten expected receipt is used. In a sparse
checkout first materialize this package and `research/precision-state-frontier`.
The three pinned predecessor documents are live inputs; no predecessor program
is executed. [SOURCES.json](SOURCES.json) records exact Git blobs and SHA256.

The verifier checks both integer inverse products, a separate rational inverse
and determinant, integer row-lattice spanning, the literal rounded collision,
strict domain inclusion, exact forward/recovery fixtures and rejection controls.
There are 1,128 literal roundtrips, 5,525 scalar candidates across 417 projected
values and eleven rejection controls. Both registered checks finish locally
in under one second each. These are check durations, not speedup claims.
Its finite probes corroborate the written all-input proof. The interpreter's
4096-bit API limit bounds its operational arithmetic, not the theorem.

The code uses fixed matrix dimensions and bounded test domains, with no
recursion or dynamic code execution. Python integer and collection allocation
is a managed-runtime deviation from fixed-allocation rules; vector lengths,
source sizes and input bit lengths bound the live data. Eleven fixed test
callbacks exercise failures. All proof-relevant checks use explicit errors
and remain enabled with `-O`. Every function has fewer than thirty lines.

## Open next questions

1. Can one actual inverse caller supply this sparse input lattice, or acquire
   the eight residues at a favorable complete cost? Start by deriving its actual
   grid and observations. Physical acquisition, restoration and the invoice are
   missing, so no physical saving is inferred.
2. What is the least total local-residue budget over arbitrary owner subsets and
   unequal bit allocations? Start with congruence kernels and the bounded quotient
   difference box. A global allocation search and attainable-collision lower
   bounds are not supplied here.

Structured questions, scope change and stopping rule are in [TASK.json](TASK.json).

## Credit and verification limits

Credit zxv #5444 for the question, matrix and lattice-fiber formulation;
Ali Romman #5323 for same-grid recovery; David Ganz #4929 and Dillon Amburgey
#4933 for the native matrix/caller; and Brian / JoyboyBrian #5035 for the
rounded kernel. All predecessor notices and files remain unchanged. New work
is Apache-2.0. Independent human and formal proof-kernel review are unclaimed.
Hosted CI is separate from local verification.
